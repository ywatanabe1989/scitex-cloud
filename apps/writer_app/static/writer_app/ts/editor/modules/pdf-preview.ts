/**
 * PDF Preview Module
 * Handles live PDF preview with auto-compilation
 */

import { CompilationManager, CompilationOptions } from './compilation.js';
import { LatexWrapper } from './latex-wrapper.js';
<<<<<<<< HEAD:.tsbuild/apps/writer_app/static/writer_app/ts/editor/modules/pdf-preview.js
console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/editor/modules/pdf-preview.ts loaded");
export class PDFPreviewManager {
    container;
    compilationManager;
    latexWrapper;
    projectId;
    autoCompile;
    compileDelay;
    docType;
    compileTimeout = null;
    currentPdfUrl = null;
    fontSize = 14; // Default editor font size
    colorMode = 'light'; // PDF color mode
    constructor(options) {
========

console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/editor/modules/pdf-preview.ts loaded");
export interface PDFPreviewOptions {
    containerId: string;
    projectId: number;
    manuscriptTitle: string;
    author?: string;
    autoCompile?: boolean;
    compileDelay?: number; // ms to wait before auto-compiling
    apiBaseUrl?: string;
    docType?: string; // manuscript, supplementary, revision (default: manuscript)
}

export class PDFPreviewManager {
    private container: HTMLElement | null;
    private compilationManager: CompilationManager;
    private latexWrapper: LatexWrapper;
    private projectId: number;
    private autoCompile: boolean;
    private compileDelay: number;
    private docType: string;
    private compileTimeout: ReturnType<typeof setTimeout> | null = null;
    private currentPdfUrl: string | null = null;
    private fontSize: number = 14; // Default editor font size
    private colorMode: 'light' | 'dark' = 'light'; // PDF color mode

    constructor(options: PDFPreviewOptions) {
>>>>>>>> feat/writer-visitor-access-and-optimizations:apps/writer_app/static/writer_app/ts/editor/modules/pdf-preview.ts
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
    private setupEventListeners(): void {
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
    scheduleAutoCompile(sections: { name: string; content: string }[]): void {
        if (!this.autoCompile) return;

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
     * Compile document preview (for auto-preview during editing)
     */
    async compile(sections: { name: string; content: string }[]): Promise<void> {
        if (!this.container) return;

        const latexContent = this.latexWrapper.createDocument(sections);

        const options: CompilationOptions = {
            projectId: this.projectId,
            docType: 'manuscript',
            content: latexContent,
            format: 'pdf'
        };

        // Use preview compilation for live editing
        await this.compilationManager.compilePreview(options);
    }

    /**
     * Set the document type for compilation
     */
    setDocType(docType: string): void {
        this.docType = docType;
        console.log('[PDFPreview] Document type changed to:', this.docType);
    }

    /**
     * Compile minimal document for quick preview
     */
    async compileQuick(content: string, sectionId?: string): Promise<void> {
        if (!this.container) return;

        const latexContent = this.latexWrapper.createMinimalDocument(content, this.fontSize);

        // Extract section name from sectionId (e.g., "manuscript/abstract" -> "abstract")
        const sectionName = sectionId ? sectionId.split('/').pop() : 'preview';

        const options: CompilationOptions = {
            projectId: this.projectId,
            docType: this.docType,
            content: latexContent,
            format: 'pdf',
            colorMode: this.colorMode,
            sectionName: sectionName  // For section-specific preview files
        };

        console.log('[PDFPreview] Quick compile for section:', sectionName, 'docType:', this.docType, 'fontSize:', this.fontSize, 'colorMode:', this.colorMode);

        // Use preview compilation for live editing
        await this.compilationManager.compilePreview(options);
    }

    /**
     * Set PDF color mode
     */
    setColorMode(colorMode: 'light' | 'dark'): void {
        this.colorMode = colorMode;
        console.log('[PDFPreview] Color mode set to:', colorMode);
    }

    /**
     * Display PDF in container with optimized rendering
     * Uses requestAnimationFrame to minimize layout thrashing
     */
    private displayPdf(pdfUrl: string): void {
        if (!this.container) return;

        // Use requestAnimationFrame to batch DOM updates with browser repaint cycle
        // This prevents layout thrashing and ensures minimal latency
        requestAnimationFrame(() => {
            // Batch all HTML updates in a single operation
            this.container!.innerHTML = `
                <div class="pdf-preview-container">
                    <div class="pdf-preview-viewer" id="pdf-viewer-pane">
                        <iframe
                            src="${pdfUrl}#toolbar=0&navpanes=0&scrollbar=1&view=FitW"
                            type="application/pdf"
                            width="100%"
                            height="100%"
                            title="PDF Preview"
                            frameborder="0">
                        </iframe>
                    </div>
                </div>
            `;

            // Update download button and panel title in a separate animation frame
            // This prevents blocking the initial PDF render
            requestAnimationFrame(() => {
                const downloadBtn = document.getElementById('download-pdf-toolbar') as HTMLAnchorElement;
                if (downloadBtn) {
                    downloadBtn.href = pdfUrl;
                    downloadBtn.style.display = 'inline-block';
                }

                // Update panel title to show which document type is displayed
                // Note: Don't update here - let updatePDFPreviewTitle() handle it with links
                // const previewTitle = document.getElementById('preview-title');
                // if (previewTitle) {
                //     const docTypeLabel = this.docType.charAt(0).toUpperCase() + this.docType.slice(1);
                //     previewTitle.textContent = `${docTypeLabel} PDF`;  // This would remove the link!
                // }
            });

            console.log('[PDFPreview] PDF displayed:', pdfUrl);
        });
    }

    /**
     * Display error message
     */
    private displayError(error: string): void {
        if (!this.container) return;

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
    private updateProgress(progress: number, status: string): void {
        if (!this.container) return;

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
    displayPlaceholder(): void {
        if (!this.container) return;

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
    getCurrentPdfUrl(): string | null {
        return this.currentPdfUrl;
    }

    /**
     * Check if currently compiling
     */
    isCompiling(): boolean {
        return this.compilationManager.getIsCompiling();
    }

    /**
     * Cancel compilation
     */
    async cancel(jobId: string): Promise<boolean> {
        return this.compilationManager.cancel(jobId);
    }

    /**
     * Set auto-compile flag
     */
    setAutoCompile(enabled: boolean): void {
        this.autoCompile = enabled;
    }

    /**
     * Set compile delay
     */
    setCompileDelay(delayMs: number): void {
        this.compileDelay = delayMs;
    }

    /**
     * Set manuscript title
     */
    setTitle(title: string): void {
        this.latexWrapper.setTitle(title);
    }

    /**
     * Set manuscript author
     */
    setAuthor(author: string): void {
        this.latexWrapper.setAuthor(author);
    }

    /**
     * Set font size for PDF compilation
     */
    setFontSize(fontSize: number): void {
        this.fontSize = fontSize;
        console.log('[PDFPreview] Font size set to:', fontSize);
    }
}
