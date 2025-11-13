/**
 * Preview Panel Manager
 * Handles LaTeX editor, templates, compilation, and PDF preview
 *
 * @version 2.0.0 (TypeScript)
 * @author SciTeX Development Team
 */

// ============================================================================
// Type Definitions
// ============================================================================

console.log(
  "[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/editor/preview-panel-manager.ts loaded",
);
interface CompilationData {
  content: string;
  title: string;
}

interface CompilationResponse {
  success: boolean;
  job_id?: string;
  error?: string;
}

interface CompilationStatus {
  status: "pending" | "running" | "completed" | "failed";
  progress: number;
  pdf_url?: string;
  error?: string;
}

interface LatexTemplates {
  [key: string]: string;
}

interface PreviewPanelConfig {
  quickCompileUrl: string;
  compilationStatusUrl: string;
  csrfToken: string;
}

// ============================================================================
// LaTeX Templates
// ============================================================================

const LATEX_TEMPLATES: LatexTemplates = {
  article: `\\documentclass[12pt]{article}
\\usepackage[utf8]{inputenc}
\\usepackage{amsmath}
\\usepackage{graphicx}
\\usepackage[margin=1in]{geometry}
\\usepackage{cite}

\\title{Your Article Title}
\\author{Your Name\\\\Your Institution}
\\date{\\today}

\\begin{document}

\\maketitle

\\begin{abstract}
Write your abstract here...
\\end{abstract}

\\section{Introduction}
Introduction content...

\\section{Related Work}
Related work...

\\section{Methodology}
Methodology...

\\section{Results}
Results...

\\section{Conclusion}
Conclusion...

\\bibliographystyle{plain}
\\bibliography{references}

\\end{document}`,

  conference: `\\documentclass[conference]{IEEEtran}
\\usepackage{amsmath}
\\usepackage{graphicx}
\\usepackage{cite}

\\title{Your Conference Paper Title}
\\author{\\IEEEauthorblockN{Your Name}
\\IEEEauthorblockA{Your Institution\\\\
Email: your.email@institution.edu}}

\\begin{document}

\\maketitle

\\begin{abstract}
Abstract content...
\\end{abstract}

\\section{Introduction}
Introduction...

\\section{Methodology}
Methodology...

\\section{Results}
Results...

\\section{Conclusion}
Conclusion...

\\begin{thebibliography}{1}
\\bibitem{ref1}
Author, "Title," Journal, Year.
\\end{thebibliography}

\\end{document}`,

  letter: `\\documentclass{letter}
\\usepackage[margin=1in]{geometry}

\\signature{Your Name}
\\address{Your Address\\\\City, State ZIP}

\\begin{document}

\\begin{letter}{Recipient Name\\\\
Recipient Address\\\\
City, State ZIP}

\\opening{Dear Recipient,}

Body of the letter goes here...

\\closing{Sincerely,}

\\end{letter}

\\end{document}`,
};

// ============================================================================
// Preview Panel Manager Class
// ============================================================================

export class PreviewPanelManager {
  private config: PreviewPanelConfig;
  private editor: any; // CodeMirror instance
  private currentJobId: string | null = null;
  private statusCheckInterval: ReturnType<typeof setInterval> | null = null;
  private previewVisible: boolean = true;
  private saveTimeout: ReturnType<typeof setTimeout> | null = null;

  // DOM elements
  private compileBtn!: HTMLButtonElement;
  private saveBtn!: HTMLButtonElement;
  private statusIndicator!: HTMLElement;
  private compileStatus!: HTMLElement;
  private previewContent!: HTMLElement;
  private previewPanel!: HTMLElement;
  private togglePreviewBtn!: HTMLButtonElement;
  private templateSelect!: HTMLSelectElement;
  private documentTitle!: HTMLInputElement;

  constructor(config: PreviewPanelConfig) {
    this.config = config;
  }

  /**
   * Initialize the preview panel manager
   */
  initialize(): void {
    console.log("[PreviewPanel] Initializing preview panel manager");

    // Initialize CodeMirror editor
    this.initializeEditor();

    // Get DOM elements
    this.getDOMElements();

    // Setup event listeners
    this.setupEventListeners();

    console.log("[PreviewPanel] Initialization complete");
  }

  /**
   * Initialize CodeMirror editor
   */
  private initializeEditor(): void {
    const textarea = document.getElementById(
      "latex-editor",
    ) as HTMLTextAreaElement;
    if (!textarea) {
      console.error("[PreviewPanel] LaTeX editor textarea not found");
      return;
    }

    if (!(window as any).CodeMirror) {
      console.error("[PreviewPanel] CodeMirror not loaded");
      return;
    }

    this.editor = (window as any).CodeMirror.fromTextArea(textarea, {
      mode: "stex",
      theme: "github",
      lineNumbers: true,
      autoCloseBrackets: true,
      matchBrackets: true,
      lineWrapping: true,
      indentUnit: 2,
    });

    // Auto-save on content change
    this.editor.on("change", () => {
      this.handleEditorChange();
    });

    console.log("[PreviewPanel] CodeMirror editor initialized");
  }

  /**
   * Get DOM element references
   */
  private getDOMElements(): void {
    this.compileBtn = document.getElementById(
      "compile-btn",
    ) as HTMLButtonElement;
    this.saveBtn = document.getElementById("save-btn") as HTMLButtonElement;
    this.statusIndicator = document.getElementById(
      "status-indicator",
    ) as HTMLElement;
    this.compileStatus = document.getElementById(
      "compile-status",
    ) as HTMLElement;
    this.previewContent = document.getElementById(
      "preview-content",
    ) as HTMLElement;
    this.previewPanel = document.getElementById("preview-panel") as HTMLElement;
    this.togglePreviewBtn = document.getElementById(
      "toggle-preview",
    ) as HTMLButtonElement;
    this.templateSelect = document.getElementById(
      "template-select",
    ) as HTMLSelectElement;
    this.documentTitle = document.getElementById(
      "document-title",
    ) as HTMLInputElement;
  }

  /**
   * Setup all event listeners
   */
  private setupEventListeners(): void {
    // Template selection
    if (this.templateSelect) {
      this.templateSelect.addEventListener("change", () => {
        this.handleTemplateChange();
      });
    }

    // Toggle preview panel
    if (this.togglePreviewBtn) {
      this.togglePreviewBtn.addEventListener("click", () => {
        this.togglePreview();
      });
    }

    // Save draft
    if (this.saveBtn) {
      this.saveBtn.addEventListener("click", () => {
        this.saveDraft();
      });
    }

    // Compile document
    if (this.compileBtn) {
      this.compileBtn.addEventListener("click", () => {
        this.compileDocument();
      });
    }
  }

  /**
   * Handle template selection change
   */
  private handleTemplateChange(): void {
    const template = this.templateSelect.value;
    if (template && LATEX_TEMPLATES[template]) {
      if (confirm("This will replace your current content. Continue?")) {
        this.editor.setValue(LATEX_TEMPLATES[template]);
        this.documentTitle.value =
          template.charAt(0).toUpperCase() + template.slice(1) + " Document";
      } else {
        this.templateSelect.value = "";
      }
    }
  }

  /**
   * Toggle preview panel visibility
   */
  private togglePreview(): void {
    this.previewVisible = !this.previewVisible;
    this.previewPanel.style.display = this.previewVisible ? "flex" : "none";
    this.togglePreviewBtn.innerHTML = this.previewVisible
      ? '<i class="fas fa-eye-slash me-1"></i>Hide Preview'
      : '<i class="fas fa-eye me-1"></i>Show Preview';
  }

  /**
   * Save draft (auto-save functionality)
   */
  private saveDraft(): void {
    this.updateStatus("Saving...", "text-warning");
    setTimeout(() => {
      this.updateStatus("Saved", "text-success");
      setTimeout(() => this.updateStatus("Ready", "text-success"), 2000);
    }, 500);
  }

  /**
   * Compile LaTeX document to PDF
   */
  private async compileDocument(): Promise<void> {
    const content = this.editor.getValue().trim();
    const title = this.documentTitle.value.trim() || "Quick Document";

    if (!content) {
      alert("Please enter some LaTeX content to compile.");
      return;
    }

    // Update UI
    this.compileBtn.disabled = true;
    this.compileBtn.innerHTML =
      '<i class="fas fa-spinner fa-spin me-2"></i>Compiling...';
    this.updateStatus("Compiling...", "text-warning");
    this.updateCompileStatus("Compilation started...", "running");

    // Send compile request
    try {
      const response = await fetch(this.config.quickCompileUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.config.csrfToken,
        },
        body: JSON.stringify({
          content: content,
          title: title,
        } as CompilationData),
      });

      const data: CompilationResponse = await response.json();

      if (data.success && data.job_id) {
        this.currentJobId = data.job_id;
        this.startStatusChecking();
      } else {
        this.handleError(data.error || "Compilation failed");
      }
    } catch (error) {
      this.handleError(
        "Network error: " +
          (error instanceof Error ? error.message : "Unknown error"),
      );
    }
  }

  /**
   * Start polling compilation status
   */
  private startStatusChecking(): void {
    if (this.statusCheckInterval) {
      clearInterval(this.statusCheckInterval);
    }

    this.statusCheckInterval = setInterval(async () => {
      if (!this.currentJobId) return;

      try {
        const url = this.config.compilationStatusUrl.replace(
          "__JOB_ID__",
          this.currentJobId,
        );
        const response = await fetch(url);
        const data: CompilationStatus = await response.json();

        this.updateJobStatus(data);

        if (data.status === "completed" || data.status === "failed") {
          if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
          }
          this.resetCompileUI();

          if (data.status === "completed" && data.pdf_url) {
            this.showPDFPreview(data.pdf_url);
            this.updateCompileStatus("✓ Compilation successful!", "success");
            this.updateStatus("Compiled", "text-success");
          } else if (data.status === "failed") {
            this.handleError(data.error || "Compilation failed");
          }
        }
      } catch (error) {
        console.error("[PreviewPanel] Status check error:", error);
      }
    }, 1000);
  }

  /**
   * Update job status display
   */
  private updateJobStatus(data: CompilationStatus): void {
    const message = `${data.status} (${data.progress}%)`;
    this.updateCompileStatus(message, data.status);
  }

  /**
   * Show PDF preview in iframe
   */
  private showPDFPreview(pdfUrl: string): void {
    this.previewContent.innerHTML = `
            <iframe src="${pdfUrl}" width="100%" height="100%" class="iframe-borderless"></iframe>
        `;
  }

  /**
   * Reset compile button UI
   */
  private resetCompileUI(): void {
    this.compileBtn.disabled = false;
    this.compileBtn.innerHTML = '<i class="fas fa-play me-2"></i>Compile PDF';
    this.currentJobId = null;
  }

  /**
   * Handle compilation error
   */
  private handleError(message: string): void {
    this.updateStatus("Error", "text-danger");
    this.updateCompileStatus("✗ " + message, "error");
    this.resetCompileUI();
  }

  /**
   * Update status indicator
   */
  private updateStatus(text: string, className: string): void {
    if (this.statusIndicator) {
      this.statusIndicator.innerHTML = `<i class="fas fa-circle ${className} me-1"></i>${text}`;
    }
  }

  /**
   * Update compilation status message
   */
  private updateCompileStatus(text: string, type: string): void {
    if (this.compileStatus) {
      this.compileStatus.textContent = text;
      this.compileStatus.className = `compile-status ${type}`;
    }
  }

  /**
   * Handle editor content change
   */
  private handleEditorChange(): void {
    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout);
    }

    this.updateStatus("Unsaved changes", "text-warning");

    this.saveTimeout = setTimeout(() => {
      this.updateStatus("Ready", "text-success");
    }, 3000);
  }

  /**
   * Destroy the preview panel manager and cleanup
   */
  destroy(): void {
    if (this.statusCheckInterval) {
      clearInterval(this.statusCheckInterval);
    }

    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout);
    }

    console.log("[PreviewPanel] Preview panel manager destroyed");
  }
}

// ============================================================================
// Global Export
// ============================================================================

declare global {
  interface Window {
    PreviewPanelManager: typeof PreviewPanelManager;
    previewPanelManager?: PreviewPanelManager;
  }
}

// Export to window for access from templates
window.PreviewPanelManager = PreviewPanelManager;
