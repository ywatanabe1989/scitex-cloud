/**
 * Writer Compilation Module
 * Handles LaTeX compilation and PDF generation
 */

import { ApiClient } from "@/utils/api";
import { getCsrfToken } from "@/utils/csrf";
import { CompilationJob } from "@/types";
import { statusLamp } from "./status-lamp.js";

console.log(
  "[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/modules/compilation.ts loaded",
);
export interface CompilationOptions {
  projectId: number;
  docType: string;
  content?: string; // Optional: only for preview
  format?: "pdf" | "dvi";
  colorMode?: "light" | "dark";
  sectionName?: string; // For section-specific preview files
  // Full compilation options
  noFigs?: boolean;
  ppt2tif?: boolean;
  cropTif?: boolean;
  quiet?: boolean;
  verbose?: boolean;
  force?: boolean;
}

export class CompilationManager {
  private apiClient: ApiClient;
  private currentJob: CompilationJob | null = null;
  private isCompiling: boolean = false;
  private onProgressCallback?: (progress: number, status: string) => void;
  private onCompleteCallback?: (jobId: string, pdfUrl: string) => void;
  private onErrorCallback?: (error: string) => void;

  constructor(apiBaseUrl: string = "") {
    this.apiClient = new ApiClient(apiBaseUrl);
  }

  /**
   * Compile preview (live editing with content)
   */
  async compilePreview(
    options: CompilationOptions,
  ): Promise<CompilationJob | null> {
    if (!options.content) {
      console.error(
        "[CompilationPreview] Content is required for preview compilation",
      );
      return null;
    }

    if (this.isCompiling) {
      console.warn("[CompilationPreview] Compilation already in progress");
      return null;
    }

    this.isCompiling = true;
    statusLamp.startPreviewCompilation();
    this.notifyProgress(0, "Preparing preview...");

    // Initialize preview log with starting message
    let logHtml = "<div>Starting preview compilation...</div>";

    // Save initial state to global storage
    const compilationLogs = (window as any).compilationLogs;
    if (compilationLogs) {
      compilationLogs.preview = logHtml;
    }

    // Update log div if currently showing preview logs
    const logDiv = document.getElementById("compilation-log-inline");
    const output = document.getElementById("compilation-output");
    if (logDiv && output?.getAttribute("data-log-type") === "preview") {
      logDiv.innerHTML = logHtml;
    }

    try {
      const timeoutMs = 60000; // 60 seconds for preview
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

      // Ensure color mode is set (get from global if not specified)
      let effectiveColorMode = options.colorMode || "light";
      if (!options.colorMode) {
        // Check if there's a saved PDF theme preference
        const savedPdfTheme = localStorage.getItem("pdf-color-mode");
        if (savedPdfTheme === "light" || savedPdfTheme === "dark") {
          effectiveColorMode = savedPdfTheme;
        } else {
          // Default to global page theme
          const globalTheme =
            document.documentElement.getAttribute("data-theme") || "light";
          effectiveColorMode = globalTheme === "dark" ? "dark" : "light";
        }
        console.log(
          "[CompilationPreview] Using effective color mode:",
          effectiveColorMode,
        );
      }

      const response = await fetch(
        `/writer/api/project/${options.projectId}/compile_preview/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
          },
          body: JSON.stringify({
            content: options.content,
            timeout: 60,
            color_mode: effectiveColorMode,
            section_name: options.sectionName || "preview",
          }),
          signal: controller.signal,
        },
      );

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = (await response.json()) as any;

      console.log("[CompilationPreview] Result:", result.success);
      console.log(
        "[CompilationPreview] PDF URL from server:",
        result.output_pdf || result.pdf_path,
      );
      this.notifyProgress(50, "Compiling preview...");

      // Build log HTML
      let logHtml = "";
      if (result.log) {
        if (result.log_html) {
          // If server provides HTML-formatted log (with ANSI colors converted)
          logHtml = result.log_html;
        } else {
          // Plain text log - convert to HTML
          const logLines = result.log.split("\n");
          logLines.forEach((line: string) => {
            logHtml += `<div>${line || " "}</div>`;
          });
        }
      }

      if (result?.success === true) {
        this.notifyProgress(100, "Preview ready");
        this.currentJob = { id: "preview", status: "completed", progress: 100 };
        statusLamp.previewCompilationSuccess();

        const pdfPath = result.output_pdf || result.pdf_path;
        console.log("[CompilationPreview] Using PDF path:", pdfPath);

        // Append success message to log
        logHtml += `<div style="color: var(--color-success-fg); margin-top: 0.5rem;">✓ Preview compilation completed successfully</div>`;

        // Save preview log to global storage
        const compilationLogs = (window as any).compilationLogs;
        if (compilationLogs) {
          compilationLogs.preview = logHtml;
        }

        // Update log div if currently showing preview logs
        const logDiv = document.getElementById("compilation-log-inline");
        const output = document.getElementById("compilation-output");
        if (logDiv && output?.getAttribute("data-log-type") === "preview") {
          logDiv.innerHTML = logHtml;
          logDiv.scrollTop = logDiv.scrollHeight;
        }

        if (this.onCompleteCallback && pdfPath) {
          this.onCompleteCallback("preview", pdfPath);
        }

        return this.currentJob;
      } else {
        throw new Error(result?.error || "Preview compilation failed");
      }
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Preview compilation failed";
      this.notifyError(message);
      statusLamp.previewCompilationError();

      // Build error log HTML
      const errorLogHtml = `<div style="color: var(--color-danger-fg); margin-top: 0.5rem; font-weight: bold;">✗ Preview compilation failed: ${message}</div>`;

      // Save error to global storage
      const compilationLogs = (window as any).compilationLogs;
      if (compilationLogs) {
        const currentLog = compilationLogs.preview || "";
        compilationLogs.preview = currentLog + errorLogHtml;
      }

      // Update log div if currently showing preview logs
      const logDiv = document.getElementById("compilation-log-inline");
      const output = document.getElementById("compilation-output");
      if (logDiv && output?.getAttribute("data-log-type") === "preview") {
        logDiv.innerHTML += errorLogHtml;
        logDiv.scrollTop = logDiv.scrollHeight;
      }

      this.currentJob = null;
      return null;
    } finally {
      this.isCompiling = false;
    }
  }

  /**
   * Compile full manuscript from workspace (no content)
   */
  async compileFull(
    options: CompilationOptions,
  ): Promise<CompilationJob | null> {
    if (this.isCompiling) {
      console.warn("[CompilationFull] Compilation already in progress");
      return null;
    }

    this.isCompiling = true;
    statusLamp.startFullCompilation();

    // Don't show progress modal automatically - only show when status indicator is clicked
    // const showProgress = (window as any).showCompilationProgress;
    // if (showProgress) {
    //   showProgress(
    //     "Compiling Full Manuscript",
    //     "Building complete manuscript PDF...",
    //   );
    // }

    this.notifyProgress(0, "Preparing full compilation...");

    try {
      const timeoutMs = 300000; // 5 minutes for full compilation
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

      console.log("[CompilationFull] Starting:", options.docType);

      // Don't prompt log at start - just keep showing "Executing LaTeX compilation..." button
      const appendLog = (window as any).appendCompilationLog;
      const updateLog = (window as any).updateCompilationLog;
      // if (appendLog) {
      //   appendLog(
      //     `[${new Date().toLocaleTimeString()}] Starting ${options.docType} compilation`,
      //     "processing",
      //     { spinner: true, dots: true, id: "compilation-start-line" },
      //   );
      // }

      const response = await fetch(
        `/writer/api/project/${options.projectId}/compile_full/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
          },
          body: JSON.stringify({
            doc_type: options.docType,
            timeout: 300,
            no_figs: options.noFigs || false,
            ppt2tif: options.ppt2tif || false,
            crop_tif: options.cropTif || false,
            quiet: options.quiet || false,
            verbose: options.verbose || false,
            force: options.force || false,
          }),
          signal: controller.signal,
        },
      );

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = (await response.json()) as any;

      console.log("[CompilationFull] API Response:", result);

      if (result?.job_id) {
        // Job started, begin polling for status
        console.log(
          "[CompilationFull] Job started, polling status:",
          result.job_id,
        );
        this.pollCompilationStatus(result.job_id, options.projectId);
        return { id: result.job_id, status: "processing", progress: 0 };
      } else if (result?.success === true) {
        // Old-style immediate response (backward compat)
        this.currentJob = { id: "full", status: "completed", progress: 100 };
        statusLamp.fullCompilationSuccess();

        const pdfPath = result.output_pdf || result.pdf_path;
        console.log("[CompilationFull] PDF path:", pdfPath);

        // Show success
        const showSuccess = (window as any).showCompilationSuccess;
        if (showSuccess && pdfPath) {
          showSuccess(pdfPath);
        }

        if (updateLog) {
          updateLog(
            "compilation-start-line",
            `[${new Date().toLocaleTimeString()}] ✓ Compilation successful!`,
            "success",
          );
        }
        if (appendLog) {
          appendLog(`PDF generated: ${pdfPath}`, "info");
        }

        if (this.onCompleteCallback && pdfPath) {
          this.onCompleteCallback("full", pdfPath);
        }

        return this.currentJob;
      } else {
        const errorMsg =
          result?.error || result?.log || "Full compilation failed";
        console.error("[CompilationFull] Error:", errorMsg);
        statusLamp.fullCompilationError();

        // Show error
        const showError = (window as any).showCompilationError;
        if (showError) {
          showError("Compilation failed", result?.log || errorMsg);
        }

        if (updateLog) {
          updateLog(
            "compilation-start-line",
            `[${new Date().toLocaleTimeString()}] ✗ Compilation failed`,
            "error",
          );
        }
        if (appendLog) {
          appendLog(`Error: ${errorMsg}`, "error");
        }

        throw new Error(errorMsg);
      }
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Full compilation failed";
      statusLamp.fullCompilationError();

      // Show error modal
      const showError = (window as any).showCompilationError;
      if (showError) {
        showError(message, error instanceof Error ? error.stack || "" : "");
      }

      const appendLog = (window as any).appendCompilationLog;
      const updateLog = (window as any).updateCompilationLog;
      if (updateLog) {
        updateLog(
          "compilation-start-line",
          `[${new Date().toLocaleTimeString()}] ✗ Error: ${message}`,
          "error",
        );
      } else if (appendLog) {
        appendLog(
          `[${new Date().toLocaleTimeString()}] ✗ Error: ${message}`,
          "error",
        );
      }

      this.notifyError(message);
      this.currentJob = null;
      return null;
    } finally {
      this.isCompiling = false;
    }
  }

  /**
   * @deprecated Use compilePreview() or compileFull() instead
   */
  async compile(options: CompilationOptions): Promise<CompilationJob | null> {
    console.warn(
      "[Compilation] DEPRECATED: Use compilePreview() or compileFull() instead",
    );
    if (options.content) {
      return this.compilePreview(options);
    } else {
      return this.compileFull(options);
    }
  }

  /**
   * Poll compilation status for real-time updates
   */
  private pollCompilationStatus(
    jobId: string,
    projectId: number,
    attempts: number = 0,
  ): void {
    const maxAttempts = 300; // 5 minutes max (1 poll per second)

    if (attempts > maxAttempts) {
      console.error(
        "[CompilationFull] Polling timeout after",
        attempts,
        "attempts",
      );
      const showError = (window as any).showCompilationError;
      if (showError) {
        showError(
          "Compilation timeout",
          "Compilation took longer than expected",
        );
      }
      return;
    }

    fetch(`/writer/api/project/${projectId}/compilation/status/${jobId}/`)
      .then((response) => response.json())
      .then((data) => {
        console.log(
          `[CompilationFull] Poll #${attempts + 1}:`,
          data.status,
          data.progress + "%",
        );

        // Update progress
        const updateProgress = (window as any).updateCompilationProgress;
        if (updateProgress && data.progress !== undefined) {
          updateProgress(data.progress, data.step || "Processing...");
        }

        // Append new logs (use HTML version if available for color support)
        const logDiv = document.getElementById("compilation-log-inline");
        if (logDiv && data.log_html) {
          // Use innerHTML to render ANSI colors as HTML
          const existingLogLength = (this as any).lastLogLength || 0;
          const newLogsHtml = data.log_html.substring(existingLogLength);

          if (newLogsHtml.trim()) {
            // Append HTML directly (ANSI codes converted to colored spans)
            const newContent = document.createElement("span");
            newContent.innerHTML = newLogsHtml;
            logDiv.appendChild(newContent);
            logDiv.appendChild(document.createTextNode("\n"));

            // Auto-scroll
            logDiv.scrollTop = logDiv.scrollHeight;
          }

          (this as any).lastLogLength = data.log_html.length;
        } else if (data.log) {
          // Fallback to plain text
          const appendLog = (window as any).appendCompilationLog;
          if (appendLog) {
            const existingLogLength = (this as any).lastLogLength || 0;
            const newLogs = data.log.substring(existingLogLength);

            if (newLogs.trim()) {
              newLogs
                .trim()
                .split("\n")
                .forEach((line) => {
                  appendLog(line);
                });
            }

            (this as any).lastLogLength = data.log.length;
          }
        }

        // Check status
        if (data.status === "completed") {
          this.isCompiling = false;
          console.log("[CompilationFull] Completed!");
          statusLamp.fullCompilationSuccess();

          const result = data.result || {};
          const pdfPath = result.output_pdf || result.pdf_path;

          // Update spinner line to success
          const updateLog = (window as any).updateCompilationLog;
          if (updateLog) {
            updateLog(
              "compilation-start-line",
              `[${new Date().toLocaleTimeString()}] ✓ Compilation completed successfully!`,
              "success",
            );
          }

          if (pdfPath) {
            const showSuccess = (window as any).showCompilationSuccess;
            if (showSuccess) {
              showSuccess(pdfPath);
            }

            if (this.onCompleteCallback) {
              this.onCompleteCallback("full", pdfPath);
            }
          }
        } else if (data.status === "failed") {
          this.isCompiling = false;
          console.error("[CompilationFull] Failed");
          statusLamp.fullCompilationError();

          // Update spinner line to error
          const updateLog = (window as any).updateCompilationLog;
          if (updateLog) {
            updateLog(
              "compilation-start-line",
              `[${new Date().toLocaleTimeString()}] ✗ Compilation failed`,
              "error",
            );
          }

          const showError = (window as any).showCompilationError;
          if (showError) {
            const errorMsg = data.result?.error || "Compilation failed";
            const errorLog = data.log || "";
            showError(errorMsg, errorLog);
          }
        } else if (
          data.status === "processing" ||
          data.status === "pending"
        ) {
          // Continue polling
          setTimeout(
            () => this.pollCompilationStatus(jobId, projectId, attempts + 1),
            1000,
          );
        }
      })
      .catch((error) => {
        console.error("[CompilationFull] Polling error:", error);
        // Retry on error
        setTimeout(
          () => this.pollCompilationStatus(jobId, projectId, attempts + 1),
          2000,
        );
      });
  }

  /**
   * Get current job status
   */
  async getStatus(jobId: string): Promise<CompilationJob | null> {
    try {
      if (jobId === "local") {
        // Local synchronous job
        return this.currentJob;
      }

      // This would be for async job polling (not currently used)
      return null;
    } catch (error) {
      console.error("[Compilation] Failed to get status:", error);
      return null;
    }
  }

  /**
   * Cancel compilation
   */
  async cancel(jobId: string): Promise<boolean> {
    try {
      const response = await this.apiClient.post<any>(
        `/writer/api/cancel-compilation/${jobId}/`,
        {},
      );

      return response.success;
    } catch (error) {
      console.error("[Compilation] Failed to cancel:", error);
      return false;
    }
  }

  /**
   * Check if currently compiling
   */
  getIsCompiling(): boolean {
    return this.isCompiling;
  }

  /**
   * Set progress callback
   */
  onProgress(callback: (progress: number, status: string) => void): void {
    this.onProgressCallback = callback;
  }

  /**
   * Set completion callback
   */
  onComplete(callback: (jobId: string, pdfUrl: string) => void): void {
    this.onCompleteCallback = callback;
  }

  /**
   * Set error callback
   */
  onError(callback: (error: string) => void): void {
    this.onErrorCallback = callback;
  }

  /**
   * Notify progress
   */
  private notifyProgress(progress: number, status: string): void {
    console.log(`[Compilation] ${progress}% - ${status}`);
    if (this.onProgressCallback) {
      this.onProgressCallback(progress, status);
    }
  }

  /**
   * Notify error
   */
  private notifyError(error: string): void {
    console.error("[Compilation] Error:", error);
    if (this.onErrorCallback) {
      this.onErrorCallback(error);
    }
  }

  /**
   * Check for existing PDF
   */
  async checkExistingPDF(
    projectSlug: string,
    docType: string = "manuscript",
  ): Promise<string | null> {
    try {
      const response = await this.apiClient.get<any>(
        `/writer/api/pdf/${projectSlug}/${docType}/`,
      );

      if (response.success && response.data?.url) {
        return response.data.url;
      }

      return null;
    } catch (error) {
      console.error("[Compilation] Failed to check existing PDF:", error);
      return null;
    }
  }
}
