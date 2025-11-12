/**
 * PDF Preview Module
 * Handles live PDF preview with auto-compilation
 */

import { CompilationManager, CompilationOptions } from './compilation.js';
import { LatexWrapper } from './latex-wrapper.js';

console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/modules/pdf-preview.ts loaded");
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
    private pdfZoom: number = 125; // PDF zoom level (default 125%)

    constructor(options: PDFPreviewOptions) {
        this.container = document.getElementById(options.containerId);
        this.projectId = options.projectId;
        this.autoCompile = options.autoCompile ?? false;
        this.compileDelay = options.compileDelay ?? 3000; // 3 seconds
        this.docType = options.docType || 'manuscript';

        // Load saved color mode preference from localStorage
        const savedMode = localStorage.getItem('pdf-color-mode') as ('light' | 'dark') | null;
        if (savedMode === 'dark' || savedMode === 'light') {
            this.colorMode = savedMode;
        } else {
            // Default to global theme
            const globalTheme = document.documentElement.getAttribute('data-theme') ||
                               localStorage.getItem('theme') ||
                               'light';
            this.colorMode = (globalTheme === 'dark' ? 'dark' : 'light');
        }
        console.log('[PDFPreview] Initialized with color mode:', this.colorMode);

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

        // Setup PDF zoom controls
        this.setupZoomControls();
    }

    /**
     * Setup PDF zoom controls
     */
    private setupZoomControls(): void {
        // Load saved zoom level from localStorage
        const savedZoom = localStorage.getItem('pdf-zoom-level');
        if (savedZoom) {
            this.pdfZoom = parseInt(savedZoom, 10);
        }

        // Setup zoom selector
        const zoomSelector = document.getElementById('pdf-zoom-selector') as HTMLSelectElement;
        if (zoomSelector) {
            zoomSelector.value = this.pdfZoom.toString();
            zoomSelector.addEventListener('change', () => {
                this.setPdfZoom(parseInt(zoomSelector.value, 10));
            });
        }

        // Setup zoom in button
        const zoomInBtn = document.getElementById('pdf-zoom-in');
        if (zoomInBtn) {
            zoomInBtn.addEventListener('click', () => {
                const zoomLevels = [100, 125, 150, 175, 200];
                const currentIndex = zoomLevels.indexOf(this.pdfZoom);
                if (currentIndex < zoomLevels.length - 1) {
                    this.setPdfZoom(zoomLevels[currentIndex + 1]);
                }
            });
        }

        // Setup zoom out button
        const zoomOutBtn = document.getElementById('pdf-zoom-out');
        if (zoomOutBtn) {
            zoomOutBtn.addEventListener('click', () => {
                const zoomLevels = [100, 125, 150, 175, 200];
                const currentIndex = zoomLevels.indexOf(this.pdfZoom);
                if (currentIndex > 0) {
                    this.setPdfZoom(zoomLevels[currentIndex - 1]);
                }
            });
        }
    }

    /**
     * Set PDF zoom level
     */
    private setPdfZoom(zoom: number): void {
        this.pdfZoom = zoom;
        localStorage.setItem('pdf-zoom-level', zoom.toString());

        // Update zoom selector if it exists
        const zoomSelector = document.getElementById('pdf-zoom-selector') as HTMLSelectElement;
        if (zoomSelector) {
            zoomSelector.value = zoom.toString();
        }

        // Reload current PDF with new zoom if PDF is displayed
        if (this.currentPdfUrl) {
            this.displayPdf(this.currentPdfUrl);
        }

        console.log('[PDFPreview] Zoom changed to:', zoom + '%');
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
     *
     * ALWAYS compiles with current theme (this.colorMode).
     * Shows existing themed PDF immediately if available, then updates when compilation completes.
     */
    async compileQuick(content: string, sectionId?: string): Promise<void> {
        if (!this.container) return;

        // Extract section name from sectionId (e.g., "manuscript/abstract" -> "abstract")
        const sectionName = sectionId ? sectionId.split('/').pop() : 'preview';

        console.log('[PDFPreview] Quick compile requested for section:', sectionName, 'theme:', this.colorMode);

        // Immediately show existing PDF for current theme if available (don't wait for compilation)
        const existingPdfUrl = `/writer/api/project/${this.projectId}/pdf/preview-${sectionName}-${this.colorMode}.pdf?t=${Date.now()}`;

        // Try to load existing PDF immediately
        fetch(existingPdfUrl, { method: 'HEAD' })
            .then(response => {
                if (response.ok) {
                    console.log('[PDFPreview] ✓ Found existing PDF for', this.colorMode, 'theme, showing immediately');
                    this.displayPdf(existingPdfUrl);
                } else {
                    console.log('[PDFPreview] No existing', this.colorMode, 'PDF found, will compile');
                }
            })
            .catch(() => {
                console.log('[PDFPreview] No existing', this.colorMode, 'PDF found, will compile');
            });

        // ALWAYS compile with current theme
        // This ensures:
        // 1. PDF matches button icon
        // 2. Alternate theme compiled in background
        // 3. Future theme switches are instant
        const latexContent = this.latexWrapper.createMinimalDocument(content, this.fontSize);

        const options: CompilationOptions = {
            projectId: this.projectId,
            docType: this.docType,
            content: latexContent,
            format: 'pdf',
            colorMode: this.colorMode,  // CRITICAL: Use current theme
            sectionName: sectionName
        };

        console.log('[PDFPreview] Compiling with theme:', this.colorMode, '(alternate theme will compile in background)');

        // Compile (will also trigger background compilation of alternate theme)
        await this.compilationManager.compilePreview(options);
    }

    /**
     * Set PDF color mode and switch to themed PDF instantly
     * If themed PDF doesn't exist, compile it
     */
    setColorMode(colorMode: 'light' | 'dark', content?: string, sectionId?: string): void {
        const oldMode = this.colorMode;
        this.colorMode = colorMode;
        console.log('[PDFPreview] Color mode changed from', oldMode, 'to', colorMode);

        // Force reload with new theme if we have a PDF displayed
        if (this.currentPdfUrl) {
            // Extract section name from current URL
            const match = this.currentPdfUrl.match(/preview-([^-]+)-(?:light|dark)\.pdf/);
            if (match) {
                const sectionName = match[1];
                const themedPdfUrl = `/writer/api/project/${this.projectId}/pdf/preview-${sectionName}-${colorMode}.pdf`;

                // Check if themed PDF exists
                fetch(themedPdfUrl, { method: 'HEAD' })
                    .then(response => {
                        if (response.ok) {
                            // PDF exists, display it
                            console.log('[PDFPreview] Themed PDF exists, displaying');
                            this.currentPdfUrl = null;
                            this.displayPdf(themedPdfUrl + `?t=${Date.now()}`);
                        } else if (content) {
                            // PDF doesn't exist but we have content, compile it
                            console.log('[PDFPreview] Themed PDF not found, compiling');
                            this.compileQuick(content, sectionId || `manuscript/${sectionName}`);
                        } else {
                            // No content available, show placeholder
                            console.log('[PDFPreview] No themed PDF and no content, showing placeholder');
                            this.displayPlaceholder();
                        }
                    })
                    .catch(() => {
                        if (content) {
                            console.log('[PDFPreview] Compiling themed PDF');
                            this.compileQuick(content, sectionId || `manuscript/${sectionName}`);
                        } else {
                            this.displayPlaceholder();
                        }
                    });
            }
        }
    }

    /**
     * Display PDF in container with optimized rendering
     * Uses requestAnimationFrame to minimize layout thrashing
     */
    private displayPdf(pdfUrl: string): void {
        if (!this.container) return;

        // Extract theme from URL
        const pdfTheme = pdfUrl.includes('-dark.pdf') ? 'dark' : 'light';
        console.log('[PDFPreview] Displaying PDF:', pdfUrl, 'theme:', pdfTheme);

        // Ensure color mode matches PDF being displayed
        if (pdfTheme !== this.colorMode) {
            console.log('[PDFPreview] Updating color mode to match PDF:', pdfTheme);
            this.colorMode = pdfTheme;

            // Update button icon to match
            const pdfScrollZoomHandler = (window as any).pdfScrollZoomHandler;
            if (pdfScrollZoomHandler && typeof pdfScrollZoomHandler.setColorMode === 'function') {
                pdfScrollZoomHandler.setColorMode(pdfTheme);
            }
        }

        // Use requestAnimationFrame to batch DOM updates with browser repaint cycle
        // This prevents layout thrashing and ensures minimal latency
        requestAnimationFrame(() => {
            // Add timestamp to URL for cache-busting (critical for theme switching)
            const cacheBustUrl = pdfUrl.includes('?') ? pdfUrl : `${pdfUrl}?t=${Date.now()}`;

            this.container!.innerHTML = `
                <div class="pdf-preview-container">
                    <div class="pdf-preview-viewer" id="pdf-viewer-pane">
                        <iframe
                            src="${cacheBustUrl}#toolbar=0&navpanes=0&scrollbar=1&zoom=${this.pdfZoom}"
                            type="application/pdf"
                            width="100%"
                            height="100%"
                            title="PDF Preview"
                            frameborder="0"
                            style="display: block; margin: 0 auto;">
                        </iframe>
                    </div>
                </div>
            `;

            // Update current PDF URL
            this.currentPdfUrl = pdfUrl;

            // Update download button
            const downloadBtn = document.getElementById('download-pdf-toolbar') as HTMLAnchorElement;
            if (downloadBtn) {
                downloadBtn.href = pdfUrl;
                downloadBtn.style.display = 'inline-block';
            }

            console.log('[PDFPreview] PDF displayed with iframe:', pdfUrl, '(theme:', this.colorMode, ')');
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
     * Only show progress if we don't already have a PDF displayed
     */
    private updateProgress(progress: number, status: string): void {
        if (!this.container) return;

        // Check if PDF is already displayed (iframe or PDF.js)
        const hasPDF = this.container.querySelector('iframe, .pdfjs-pages-container') !== null;

        if (hasPDF) {
            // PDF already showing, don't show progress overlay
            console.log('[PDFPreview] Background compile progress:', progress, '%', status);
            return;
        }

        // Only show progress UI if no PDF is displayed yet
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
            <div style="
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100%;
                text-align: center;
                color: var(--color-fg-muted);
                gap: 1rem;
            ">
                <i class="fas fa-file-pdf fa-3x" style="opacity: 0.3;"></i>
                <h5 style="margin: 0;">PDF Preview</h5>
                <p style="font-size: 0.9rem; margin: 0;">Start typing to see your document preview</p>
                <p style="font-size: 0.75rem; opacity: 0.7; margin: 0;">Auto-compilation is enabled</p>
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
