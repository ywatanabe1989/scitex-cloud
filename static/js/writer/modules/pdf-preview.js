/**
 * PDF Preview Module
 * Handles live PDF preview with auto-compilation
 */
import { CompilationManager } from './compilation.js';
import { LatexWrapper } from './latex-wrapper.js';
export class PDFPreviewManager {
    constructor(options) {
        this.compileTimeout = null;
        this.currentPdfUrl = null;
        this.container = document.getElementById(options.containerId);
        this.projectId = options.projectId;
        this.autoCompile = options.autoCompile ?? false;
        this.compileDelay = options.compileDelay ?? 3000; // 3 seconds
        this.docType = options.docType || 'manuscript';
        this.compilationManager = new CompilationManager(options.apiBaseUrl || '');
        this.latexWrapper = new LatexWrapper({
            title: options.manuscriptTitle,
            author: options.author
        });
        this.setupEventListeners();
    }
    /**
     * Setup event listeners for compilation
     */
    setupEventListeners() {
        this.compilationManager.onProgress((progress, status) => {
            this.updateProgress(progress, status);
        });
        this.compilationManager.onComplete((_jobId, pdfUrl) => {
            this.displayPdf(pdfUrl);
            this.currentPdfUrl = pdfUrl;
        });
        this.compilationManager.onError((error) => {
            this.displayError(error);
        });
    }
    /**
     * Schedule auto-compilation
     */
    scheduleAutoCompile(sections) {
        if (!this.autoCompile)
            return;
        // Clear existing timeout
        if (this.compileTimeout) {
            clearTimeout(this.compileTimeout);
        }
        // Schedule new compilation
        this.compileTimeout = setTimeout(() => {
            this.compile(sections);
        }, this.compileDelay);
    }
    /**
     * Compile document
     */
    async compile(sections) {
        if (!this.container)
            return;
        const latexContent = this.latexWrapper.createDocument(sections);
        const options = {
            projectId: this.projectId,
            docType: 'manuscript',
            content: latexContent,
            format: 'pdf'
        };
        await this.compilationManager.compile(options);
    }
    /**
     * Set the document type for compilation
     */
    setDocType(docType) {
        this.docType = docType;
        console.log('[PDFPreview] Document type changed to:', this.docType);
    }
    /**
     * Compile minimal document for quick preview
     */
    async compileQuick(content) {
        if (!this.container)
            return;
        const latexContent = this.latexWrapper.createMinimalDocument(content);
        const options = {
            projectId: this.projectId,
            docType: this.docType,
            content: latexContent,
            format: 'pdf'
        };
        console.log('[PDFPreview] Quick compile with docType:', this.docType);
        await this.compilationManager.compile(options);
    }
    /**
     * Display PDF in container
     */
    displayPdf(pdfUrl) {
        if (!this.container)
            return;
        this.container.innerHTML = `
            <div class="pdf-preview-container">
                <div class="pdf-preview-viewer">
                    <embed
                        src="${pdfUrl}#toolbar=0&navpanes=0&scrollbar=1"
                        type="application/pdf"
                        title="PDF Preview">
                    </embed>
                </div>
            </div>
        `;
        // Update download button in toolbar
        const downloadBtn = document.getElementById('download-pdf-toolbar');
        if (downloadBtn) {
            downloadBtn.href = pdfUrl;
            downloadBtn.style.display = 'inline-block';
        }
        console.log('[PDFPreview] PDF displayed:', pdfUrl);
    }
    /**
     * Display error message
     */
    displayError(error) {
        if (!this.container)
            return;
        this.container.innerHTML = `
            <div style="padding: 2rem; text-align: center; color: var(--color-danger-fg);">
                <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                <h5>Compilation Error</h5>
                <p style="font-size: 0.9rem;">${error}</p>
                <small style="color: var(--color-fg-muted);">Check the error output for details</small>
            </div>
        `;
        console.error('[PDFPreview] Compilation error:', error);
    }
    /**
     * Update progress display
     */
    updateProgress(progress, status) {
        if (!this.container)
            return;
        this.container.innerHTML = `
            <div style="padding: 2rem; text-align: center;">
                <div class="progress" style="height: 4px; margin-bottom: 1rem;">
                    <div class="progress-bar" role="progressbar" style="width: ${progress}%; background: var(--color-accent-emphasis);" aria-valuenow="${progress}" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                <p style="color: var(--color-fg-muted);">${status}</p>
                <small>${progress}%</small>
            </div>
        `;
    }
    /**
     * Display placeholder
     */
    displayPlaceholder() {
        if (!this.container)
            return;
        this.container.innerHTML = `
            <div style="padding: 2rem; text-align: center; color: var(--color-fg-muted);">
                <i class="fas fa-file-pdf fa-3x mb-3" style="opacity: 0.3;"></i>
                <h5>PDF Preview</h5>
                <p style="font-size: 0.9rem;">Click "Compile" to generate PDF preview</p>
            </div>
        `;
    }
    /**
     * Get current PDF URL
     */
    getCurrentPdfUrl() {
        return this.currentPdfUrl;
    }
    /**
     * Check if currently compiling
     */
    isCompiling() {
        return this.compilationManager.getIsCompiling();
    }
    /**
     * Cancel compilation
     */
    async cancel(jobId) {
        return this.compilationManager.cancel(jobId);
    }
    /**
     * Set auto-compile flag
     */
    setAutoCompile(enabled) {
        this.autoCompile = enabled;
    }
    /**
     * Set compile delay
     */
    setCompileDelay(delayMs) {
        this.compileDelay = delayMs;
    }
    /**
     * Set manuscript title
     */
    setTitle(title) {
        this.latexWrapper.setTitle(title);
    }
    /**
     * Set manuscript author
     */
    setAuthor(author) {
        this.latexWrapper.setAuthor(author);
    }
}
//# sourceMappingURL=pdf-preview.js.map