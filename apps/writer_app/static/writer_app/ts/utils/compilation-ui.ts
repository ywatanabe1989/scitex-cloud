/**
 * Compilation UI Functions
 * Handles all compilation progress UI, logging, and status indicators
 */

import { showToast } from "./ui.js";

/**
 * Show compilation progress UI
 */
export function showCompilationProgress(title: string = "Compiling Manuscript"): void {
  const output = document.getElementById("compilation-output");
  const icon = document.getElementById("compilation-icon");
  const headerTitle = document.getElementById("compilation-header-title");
  const progressContainer = document.getElementById(
    "compilation-progress-container",
  );
  const resultDiv = document.getElementById("compilation-result-inline");

  if (!output) return;

  // Update header
  if (icon) {
    icon.className = "fas fa-spinner fa-spin";
  }
  if (headerTitle) {
    headerTitle.textContent = title;
  }

  // Show progress bar
  if (progressContainer) {
    progressContainer.style.display = "block";
  }

  // Hide result
  if (resultDiv) {
    resultDiv.style.display = "none";
    resultDiv.innerHTML = "";
  }

  // Reset progress
  updateCompilationProgress(0, "Initializing...");

  // Clear log
  const log = document.getElementById("compilation-log-inline");
  if (log) {
    log.textContent = "Starting compilation...\n";
  }

  // Ensure log details are closed (minimized) by default
  const logDetails = document.getElementById("compilation-log-details") as HTMLDetailsElement;
  if (logDetails) {
    logDetails.open = false;
  }

  // Update toolbar buttons: show Stop, hide Start
  const startBtn = document.getElementById("compilation-log-start-btn");
  const stopBtn = document.getElementById("compilation-log-stop-btn");
  if (startBtn) startBtn.style.display = "none";
  if (stopBtn) stopBtn.style.display = "inline-block";

  // Show compilation output
  output.style.display = "block";

  // Update status lamp and slim progress
  updateStatusLamp("compiling", "Compiling...");
  updateSlimProgress(0, "Initializing...");
}

/**
 * Hide compilation output
 */
export function hideCompilationProgress(): void {
  const output = document.getElementById("compilation-output");
  if (output) {
    output.style.display = "none";
  }
}

/**
 * Update compilation progress
 */
export function updateCompilationProgress(percent: number, status: string): void {
  const progressBar = document.getElementById("compilation-progress-bar");
  const progressPercent = document.getElementById(
    "compilation-progress-percent",
  );
  const progressStatus = document.getElementById("compilation-progress-status");

  if (progressBar) progressBar.style.width = `${percent}%`;
  if (progressPercent) progressPercent.textContent = `${percent}%`;
  if (progressStatus) progressStatus.textContent = status;

  // Also update minimized status if it's visible
  updateMinimizedStatus(percent, status);

  // Update slim progress bar
  updateSlimProgress(percent, status);
}

/**
 * Append to compilation log with semantic color coding and visual cues
 */
export function appendCompilationLog(
  message: string,
  type: "info" | "success" | "error" | "warning" | "processing" = "info",
  options?: { spinner?: boolean; dots?: boolean; id?: string },
): void {
  const log = document.getElementById("compilation-log-inline");
  if (!log) return;

  // Create line container
  const lineDiv = document.createElement("div");
  if (options?.id) {
    lineDiv.id = options.id;
  }

  // Add spinner if requested
  if (options?.spinner) {
    const spinner = document.createElement("span");
    spinner.className = "terminal-log__spinner";
    lineDiv.appendChild(spinner);
  }

  // Create colored span for the message
  const span = document.createElement("span");

  // Apply semantic color class based on message content or type
  if (
    message.includes("✓") ||
    message.includes("Success") ||
    type === "success"
  ) {
    span.className = "terminal-log__success";
  } else if (
    message.includes("✗") ||
    message.includes("Error") ||
    message.includes("Failed") ||
    type === "error"
  ) {
    span.className = "terminal-log__error";
  } else if (
    message.includes("⚠") ||
    message.includes("Warning") ||
    type === "warning"
  ) {
    span.className = "terminal-log__warning";
  } else if (type === "processing") {
    span.className = "terminal-log__processing";
  } else {
    span.className = "terminal-log__info";
  }

  span.textContent = message;
  lineDiv.appendChild(span);

  // Add animated dots if requested
  if (options?.dots) {
    const dots = document.createElement("span");
    dots.className = "terminal-log__loading-dots";
    lineDiv.appendChild(dots);
  }

  // Add newline
  lineDiv.appendChild(document.createTextNode("\n"));

  log.appendChild(lineDiv);

  // Auto-scroll to bottom
  log.scrollTop = log.scrollHeight;
}

/**
 * Update a processing log line (remove spinner/dots, update message)
 */
export function updateCompilationLog(
  lineId: string,
  message: string,
  type: "success" | "error" | "warning" | "info" = "info",
): void {
  const line = document.getElementById(lineId);
  if (!line) return;

  // Remove spinner and dots
  const spinner = line.querySelector(".terminal-log__spinner");
  const dots = line.querySelector(".terminal-log__loading-dots");
  if (spinner) spinner.remove();
  if (dots) dots.remove();

  // Update message
  const span = line.querySelector(
    "span:not(.terminal-log__spinner):not(.terminal-log__loading-dots)",
  );
  if (span) {
    span.textContent = message;

    // Update color class
    span.className = "";
    if (
      message.includes("✓") ||
      message.includes("Success") ||
      type === "success"
    ) {
      span.className = "terminal-log__success";
    } else if (
      message.includes("✗") ||
      message.includes("Error") ||
      message.includes("Failed") ||
      type === "error"
    ) {
      span.className = "terminal-log__error";
    } else if (
      message.includes("⚠") ||
      message.includes("Warning") ||
      type === "warning"
    ) {
      span.className = "terminal-log__warning";
    } else {
      span.className = "terminal-log__info";
    }
  }
}

/**
 * Show compilation success
 */
export function showCompilationSuccess(pdfUrl: string): void {
  const icon = document.getElementById("compilation-icon");
  const progressContainer = document.getElementById(
    "compilation-progress-container",
  );
  const alertBanner = document.getElementById("compilation-alert-banner");
  const resultDiv = document.getElementById("compilation-result-inline");
  const minimizedStatus = document.getElementById(
    "minimized-compilation-status",
  );

  // Update icon to success
  if (icon) {
    icon.className = "fas fa-check-circle text-success";
  }

  // Hide progress bar
  if (progressContainer) {
    progressContainer.style.display = "none";
  }

  // Show success alert banner
  if (alertBanner) {
    alertBanner.style.display = "block";
    alertBanner.className = "alert-banner alert-banner-success";
    alertBanner.innerHTML = `
            <div class="warning-banner-content">
                <i class="fas fa-check-circle warning-banner-icon"></i>
                <div class="warning-banner-text">
                    <div class="warning-banner-title">Compilation Successful!</div>
                    <div class="warning-banner-description">
                        Your manuscript PDF has been generated.
                        <a href="${pdfUrl}" target="_blank" style="color: white; text-decoration: underline; margin-left: 0.5rem;">
                            <i class="fas fa-file-pdf me-1"></i>View PDF
                        </a>
                    </div>
                </div>
            </div>
        `;
  }

  // Keep old result div for backward compatibility (hide it)
  if (resultDiv) {
    resultDiv.style.display = "none";
  }

  updateCompilationProgress(100, "Complete!");

  // Update status lamp to success
  updateStatusLamp("success", "Success");

  // Update toolbar buttons: show Start, hide Stop
  const startBtn = document.getElementById("compilation-log-start-btn");
  const stopBtn = document.getElementById("compilation-log-stop-btn");
  if (startBtn) startBtn.style.display = "inline-block";
  if (stopBtn) stopBtn.style.display = "none";

  // Update minimized status icon to success
  if (minimizedStatus) {
    const icon = minimizedStatus.querySelector("i");
    if (icon) {
      icon.className = "fas fa-check-circle";
      icon.style.color = "var(--color-success-emphasis)";
    }
  }

  // Auto-hide minimized status after 3 seconds if compilation was successful
  setTimeout(() => {
    if (minimizedStatus && minimizedStatus.style.display !== "none") {
      minimizedStatus.style.display = "none";
    }
  }, 3000);
}

/**
 * Show compilation error
 */
export function showCompilationError(
  errorMessage: string,
  errorDetails: string = "",
): void {
  const icon = document.getElementById("compilation-icon");
  const progressContainer = document.getElementById(
    "compilation-progress-container",
  );
  const alertBanner = document.getElementById("compilation-alert-banner");
  const resultDiv = document.getElementById("compilation-result-inline");
  const minimizedStatus = document.getElementById(
    "minimized-compilation-status",
  );

  // Update icon to error
  if (icon) {
    icon.className = "fas fa-exclamation-circle text-danger";
  }

  // Hide progress bar
  if (progressContainer) {
    progressContainer.style.display = "none";
  }

  // Show error alert banner
  if (alertBanner) {
    alertBanner.style.display = "block";
    alertBanner.className = "alert-banner alert-banner-danger";
    alertBanner.innerHTML = `
            <div class="warning-banner-content">
                <i class="fas fa-exclamation-circle warning-banner-icon"></i>
                <div class="warning-banner-text">
                    <div class="warning-banner-title">Compilation Failed</div>
                    <div class="warning-banner-description">
                        ${errorMessage}
                        ${errorDetails ? "<br><small>Check the compilation log below for details.</small>" : ""}
                    </div>
                </div>
            </div>
        `;
  }

  // Keep old result div for backward compatibility (hide it)
  if (resultDiv) {
    resultDiv.style.display = "none";
  }

  // Update status lamp to error
  updateStatusLamp("error", "Failed");

  // Update toolbar buttons: show Start, hide Stop
  const startBtn = document.getElementById("compilation-log-start-btn");
  const stopBtn = document.getElementById("compilation-log-stop-btn");
  if (startBtn) startBtn.style.display = "inline-block";
  if (stopBtn) stopBtn.style.display = "none";

  // Update minimized status icon to error and make it clickable to see details
  if (minimizedStatus) {
    const icon = minimizedStatus.querySelector("i");
    const text = minimizedStatus.querySelector("#minimized-compilation-text");
    if (icon) {
      icon.className = "fas fa-exclamation-circle";
      icon.style.color = "var(--color-danger-emphasis)";
    }
    if (text) {
      text.textContent = "Failed";
    }
    // Keep minimized status visible so user can click to see error details
    minimizedStatus.title = "Click to view error details";
  }
}

/**
 * Minimize compilation output to background status
 */
export function minimizeCompilationOutput(): void {
  const output = document.getElementById("compilation-output");
  const minimizedStatus = document.getElementById(
    "minimized-compilation-status",
  );
  const minimizeBtn = document.getElementById("minimize-compilation-output");

  if (!output) return;

  // Hide the full compilation output
  output.style.display = "none";

  // Show minimized status indicator
  if (minimizedStatus) {
    minimizedStatus.style.display = "flex";
  }

  // Update minimize button icon to restore icon
  if (minimizeBtn) {
    minimizeBtn.innerHTML = '<i class="fas fa-window-restore"></i>';
    minimizeBtn.title = "Restore compilation panel";
  }
}

/**
 * Restore compilation output from minimized state
 */
export function restoreCompilationOutput(): void {
  const output = document.getElementById("compilation-output");
  const minimizedStatus = document.getElementById(
    "minimized-compilation-status",
  );
  const minimizeBtn = document.getElementById("minimize-compilation-output");

  if (!output) return;

  // Show the full compilation output
  output.style.display = "block";

  // Hide minimized status indicator
  if (minimizedStatus) {
    minimizedStatus.style.display = "none";
  }

  // Update minimize button icon back to minimize icon
  if (minimizeBtn) {
    minimizeBtn.innerHTML = '<i class="fas fa-window-minimize"></i>';
    minimizeBtn.title = "Minimize to background";
  }
}

// Store separate logs for preview and full compilation
export const compilationLogs = {
  preview: "",
  full: "",
};

/**
 * Toggle compilation panel visibility
 * Called when clicking on status indicators
 */
export function toggleCompilationPanel(type: "preview" | "full" = "full"): void {
  const output = document.getElementById("compilation-output");
  const logDiv = document.getElementById("compilation-log-inline");
  if (!output || !logDiv) return;

  // Check if we're switching log types
  const currentType = output.getAttribute("data-log-type");
  const isSwitchingType = currentType && currentType !== type;

  // Store current log content before switching
  if (currentType && logDiv.innerHTML) {
    compilationLogs[currentType as "preview" | "full"] = logDiv.innerHTML;
  }

  // Set the log type
  output.setAttribute("data-log-type", type);

  // Load the appropriate log content
  if (isSwitchingType || !logDiv.innerHTML) {
    const savedLog = compilationLogs[type];
    if (savedLog) {
      logDiv.innerHTML = savedLog;
    } else {
      logDiv.innerHTML =
        type === "preview"
          ? "No preview compilation logs yet. Click the preview play button to compile."
          : "No full compilation logs yet. Click the full play button to compile.";
    }
  }

  // Toggle visibility
  if (output.style.display === "none" || !output.style.display) {
    output.style.display = "block";
    console.log(`[Writer] ${type} compilation panel shown`);
  } else {
    output.style.display = "none";
    console.log("[Writer] Compilation panel hidden");
  }
}

/**
 * Toggle preview compilation log
 */
export function togglePreviewLog(): void {
  toggleCompilationPanel("preview");
}

/**
 * Toggle full compilation log
 */
export function toggleFullLog(): void {
  toggleCompilationPanel("full");
}

/**
 * Handle compilation log Start button
 * Starts the appropriate compilation based on current log type (preview or full)
 */
export function handleCompilationLogStart(): void {
  const output = document.getElementById("compilation-output");
  if (!output) return;

  const logType = output.getAttribute("data-log-type") as "preview" | "full" | null;

  if (logType === "preview") {
    // Start preview compilation
    console.log("[Writer] Starting preview compilation from log toolbar");
    if ((window as any).handlePreviewClick) {
      (window as any).handlePreviewClick();
    }
  } else if (logType === "full") {
    // Start full compilation
    console.log("[Writer] Starting full compilation from log toolbar");
    if ((window as any).handleFullCompileClick) {
      (window as any).handleFullCompileClick();
    }
  } else {
    showToast("Please click a status LED first to select compilation type", "warning");
  }
}

/**
 * Handle compilation log Stop button
 * Stops the current compilation
 */
export function handleCompilationLogStop(): void {
  const output = document.getElementById("compilation-output");
  if (!output) return;

  const logType = output.getAttribute("data-log-type") as "preview" | "full" | null;

  if (logType === "preview") {
    // Stop preview compilation
    console.log("[Writer] Stopping preview compilation from log toolbar");
    const statusLamp = (window as any).statusLamp;
    if (statusLamp) {
      statusLamp.setPreviewStatus("idle");
    }
  } else if (logType === "full") {
    // Stop full compilation
    console.log("[Writer] Stopping full compilation from log toolbar");
    const statusLamp = (window as any).statusLamp;
    if (statusLamp) {
      statusLamp.setFullCompileStatus("idle");
    }
  }
}

/**
 * Handle compilation log Close button
 * Closes the log panel
 */
export function handleCompilationLogClose(): void {
  const output = document.getElementById("compilation-output");
  if (output) {
    output.style.display = "none";
    console.log("[Writer] Compilation log panel closed");
  }
}

/**
 * Update minimized compilation status
 */
export function updateMinimizedStatus(progress: number, status: string): void {
  const minimizedText = document.getElementById("minimized-compilation-text");
  const minimizedProgress = document.getElementById(
    "minimized-compilation-progress",
  );

  if (minimizedText) {
    minimizedText.textContent = status;
  }
  if (minimizedProgress) {
    minimizedProgress.textContent = `${progress}%`;
  }
}

/**
 * Update status lamp (LED indicator)
 */
export function updateStatusLamp(
  status: "idle" | "compiling" | "success" | "error",
  text: string,
): void {
  const lamp = document.querySelector(".status-lamp-indicator") as HTMLElement;
  const lampText = document.querySelector(".status-lamp-text") as HTMLElement;

  if (lamp) {
    lamp.setAttribute("data-status", status);
  }
  if (lampText) {
    lampText.textContent = text;
  }

  // Persist status to localStorage
  localStorage.setItem(
    "scitex-compilation-status",
    JSON.stringify({ status, text, timestamp: Date.now() }),
  );
}

/**
 * Update slim progress bar (tqdm-style)
 */
export function updateSlimProgress(
  progress: number,
  status: string,
  eta?: string,
): void {
  const slimProgress = document.getElementById("compilation-slim-progress");
  const slimFill = document.getElementById("slim-progress-fill");
  const slimPercent = document.getElementById("slim-progress-percent");
  const slimStatus = document.getElementById("slim-progress-status");
  const slimEta = document.getElementById("slim-progress-eta");

  if (!slimProgress) return;

  // DISABLED: Status lamp provides sufficient feedback, no need for progress bar
  // Show slim progress during compilation
  // if (progress > 0 && progress < 100) {
  //   slimProgress.style.display = "block";
  // }

  if (slimFill) {
    slimFill.style.width = `${progress}%`;
  }
  if (slimPercent) {
    slimPercent.textContent = `${progress}%`;
  }
  if (slimStatus) {
    slimStatus.textContent = status;
  }
  if (slimEta && eta) {
    slimEta.textContent = eta;
  }

  // Hide after completion (with delay)
  if (progress === 100) {
    setTimeout(() => {
      if (slimProgress) {
        slimProgress.style.display = "none";
      }
    }, 2000);
  }
}

/**
 * Toggle compilation details panel
 */
export function toggleCompilationDetails(): void {
  const output = document.getElementById("compilation-output");
  const slimProgress = document.getElementById("compilation-slim-progress");

  if (!output) return;

  const isVisible = output.style.display === "block";

  if (isVisible) {
    // Hide details (slim progress disabled - status lamp provides feedback)
    output.style.display = "none";
    // DISABLED: Status lamp provides sufficient feedback
    // if (slimProgress) {
    //   slimProgress.style.display = "block";
    // }
  } else {
    // Show full details
    output.style.display = "block";
    if (slimProgress) {
      slimProgress.style.display = "none";
    }
  }
}

/**
 * Restore last compilation status from localStorage
 */
export function restoreCompilationStatus(): void {
  const saved = localStorage.getItem("scitex-compilation-status");
  if (!saved) {
    updateStatusLamp("idle", "Ready");
    return;
  }

  try {
    const { status, text, timestamp } = JSON.parse(saved);
    const ageMs = Date.now() - timestamp;
    const ageMinutes = Math.floor(ageMs / 60000);

    // If status is recent (< 5 minutes), show it
    if (ageMinutes < 5) {
      updateStatusLamp(status, text);
    } else if (status === "success") {
      // Show successful compilation even if old
      updateStatusLamp("success", `Done (${ageMinutes}m ago)`);
    } else {
      // Reset to idle
      updateStatusLamp("idle", "Ready");
    }
  } catch (e) {
    console.warn("[Compilation] Failed to restore status:", e);
    updateStatusLamp("idle", "Ready");
  }
}
