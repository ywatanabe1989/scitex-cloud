"use strict";
/**
 * Compilation view page functionality
 * Corresponds to: templates/writer_app/compilation/compilation_view.html
 */
console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/compilation/compilation_view.ts loaded");
class CompilationViewPage {
    logViewer;
    progressBar;
    // @ts-expect-error - Placeholder for future PDF viewer integration
    _pdfViewer;
    constructor() {
        this.logViewer = document.getElementById('log-viewer');
        this.progressBar = document.getElementById('progress-bar');
        this._pdfViewer = document.getElementById('pdf-viewer');
        this.init();
    }
    init() {
        console.log('[CompilationView] Initializing compilation view');
        this.setupLogViewer();
        this.setupProgressMonitoring();
    }
    setupLogViewer() {
        console.log('[CompilationView] Setting up log viewer');
        // Setup log viewing functionality
    }
    setupProgressMonitoring() {
        console.log('[CompilationView] Setting up progress monitoring');
        // Monitor compilation progress
    }
    updateProgress(percentage) {
        if (this.progressBar) {
            this.progressBar.style.width = `${percentage}%`;
        }
    }
    addLogEntry(log) {
        if (this.logViewer) {
            const entry = document.createElement('div');
            entry.className = `log-entry log-${log.level}`;
            entry.textContent = `[${log.timestamp}] ${log.message}`;
            this.logViewer.appendChild(entry);
        }
    }
}
// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new CompilationViewPage();
});
//# sourceMappingURL=compilation_view.js.map