/**
 * CompilationProgressUI.ts
 * Manages the compilation progress UI display, including progress bars,
 * status indicators, and visual feedback for compilation state.
 */

/**
 * Show compilation progress modal
 */
export function showCompilationProgress(
  title: string = "Compiling Manuscript",
): void {
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
  const logDetails = document.getElementById(
    "compilation-log-details",
  ) as HTMLDetailsElement;
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
export function updateCompilationProgress(
  percent: number,
  status: string,
): void {
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
  error: string,
  details?: { stdout?: string; stderr?: string },
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
    alertBanner.className = "alert-banner alert-banner-error";
    alertBanner.innerHTML = `
            <div class="warning-banner-content">
                <i class="fas fa-exclamation-triangle warning-banner-icon"></i>
                <div class="warning-banner-text">
                    <div class="warning-banner-title">Compilation Failed</div>
                    <div class="warning-banner-description">
                        ${error}
                    </div>
                </div>
            </div>
        `;
  }

  // Keep old result div for backward compatibility (hide it)
  if (resultDiv) {
    resultDiv.style.display = "none";
  }

  updateCompilationProgress(100, "Failed");

  // Update status lamp to error
  updateStatusLamp("error", "Failed");

  // Update toolbar buttons: show Start, hide Stop
  const startBtn = document.getElementById("compilation-log-start-btn");
  const stopBtn = document.getElementById("compilation-log-stop-btn");
  if (startBtn) startBtn.style.display = "inline-block";
  if (stopBtn) stopBtn.style.display = "none";

  // Update minimized status icon to error
  if (minimizedStatus) {
    const icon = minimizedStatus.querySelector("i");
    if (icon) {
      icon.className = "fas fa-exclamation-circle";
      icon.style.color = "var(--color-danger-emphasis)";
    }
  }
}

/**
 * Update minimized status text and progress
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
 * Restore compilation status from previous session
 */
export function restoreCompilationStatus(): void {
  const stored = localStorage.getItem("scitex-compilation-status");
  if (!stored) {
    updateStatusLamp("idle", "Ready");
    return;
  }

  try {
    const { status, text, timestamp } = JSON.parse(stored);
    const ageMinutes = Math.floor((Date.now() - timestamp) / 1000 / 60);

    // Show status if less than 5 minutes old
    if (ageMinutes < 5) {
      updateStatusLamp(status, text);
    } else if (status === "success") {
      updateStatusLamp("success", `Done (${ageMinutes}m ago)`);
    } else {
      updateStatusLamp("idle", "Ready");
    }
  } catch (e) {
    updateStatusLamp("idle", "Ready");
  }
}
