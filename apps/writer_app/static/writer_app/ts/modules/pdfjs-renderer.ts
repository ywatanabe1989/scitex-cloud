/**
 * PDF.js Renderer Module
 * Handles PDF rendering with PDF.js library for better control and theme-aware scrollbars
 */

console.log("[DEBUG] pdfjs-renderer.ts loaded");

// Declare PDF.js types
declare global {
    interface Window {
        pdfjsLib: any;
    }
}

export class PDFJSRenderer {
    private container: HTMLElement;
    private pdfDoc: any = null;
    private currentScale: number = 2.0; // Default to 2x for better quality
    private renderTasks: any[] = [];
    private colorMode: 'light' | 'dark' = 'light';

    constructor(containerId: string, initialColorMode?: 'light' | 'dark') {
        const container = document.getElementById(containerId);
        if (!container) {
            throw new Error(`Container ${containerId} not found`);
        }
        this.container = container;

        // Use provided color mode, or detect from data attribute, or default to light
        if (initialColorMode) {
            this.colorMode = initialColorMode;
        } else {
            const textPreview = document.getElementById('text-preview');
            const mode = textPreview?.getAttribute('data-pdf-theme');
            this.colorMode = (mode === 'dark' || mode === 'light') ? mode : 'light';
        }

        console.log('[PDFJSRenderer] Initialized with color mode:', this.colorMode);
    }

    /**
     * Load PDF.js library if not already loaded
     */
    private async loadPDFJS(): Promise<void> {
        if (window.pdfjsLib) {
            return Promise.resolve();
        }

        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js';
            script.onload = () => {
                if (window.pdfjsLib) {
                    window.pdfjsLib.GlobalWorkerOptions.workerSrc =
                        'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
                    resolve();
                } else {
                    reject(new Error('PDF.js failed to load'));
                }
            };
            script.onerror = () => reject(new Error('Failed to load PDF.js script'));
            document.head.appendChild(script);
        });
    }

    /**
     * Render PDF from URL
     */
    async renderPDF(pdfUrl: string, scale: number = 1.0): Promise<void> {
        this.currentScale = scale;

        try {
            // Use the colorMode that was set in constructor or via setColorMode()
            // Don't override it - it's already correct from saved preferences
            console.log('[PDFJSRenderer] Rendering PDF with color mode:', this.colorMode, 'URL:', pdfUrl);

            // Load PDF.js library
            await this.loadPDFJS();

            // Cancel any pending render tasks
            this.renderTasks.forEach(task => {
                if (task.cancel) task.cancel();
            });
            this.renderTasks = [];

            // Show loading state
            this.container.innerHTML = `
                <div class="pdf-loading" style="padding: 2rem; text-align: center; color: var(--color-fg-muted);">
                    <i class="fas fa-spinner fa-spin"></i> Loading PDF...
                </div>
            `;

            // Load PDF document
            const loadingTask = window.pdfjsLib.getDocument(pdfUrl);
            this.pdfDoc = await loadingTask.promise;

            // Create container for all pages
            const pagesContainer = document.createElement('div');
            pagesContainer.className = 'pdfjs-pages-container';
            pagesContainer.setAttribute('data-pdf-theme', this.colorMode);

            this.container.innerHTML = '';
            this.container.appendChild(pagesContainer);

            console.log('[PDFJSRenderer] Created pagesContainer with data-pdf-theme:', this.colorMode);

            // Render all pages
            const numPages = this.pdfDoc.numPages;
            for (let pageNum = 1; pageNum <= numPages; pageNum++) {
                await this.renderPage(pageNum, pagesContainer);
            }

            console.log('[PDFJSRenderer] Rendered', numPages, 'pages at scale', scale);
        } catch (error) {
            console.error('[PDFJSRenderer] Error rendering PDF:', error);
            this.container.innerHTML = `
                <div class="pdf-error" style="padding: 2rem; text-align: center; color: var(--color-danger-fg);">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Error loading PDF</p>
                    <small>${error}</small>
                </div>
            `;
        }
    }

    /**
     * Render a single page
     */
    private async renderPage(pageNum: number, container: HTMLElement): Promise<void> {
        const page = await this.pdfDoc.getPage(pageNum);
        const viewport = page.getViewport({ scale: this.currentScale });

        // Create page container - NO inline styles, use CSS only
        const pageContainer = document.createElement('div');
        pageContainer.className = 'pdfjs-page-container';
        pageContainer.setAttribute('data-page-number', pageNum.toString());
        pageContainer.setAttribute('data-width', viewport.width.toString());
        pageContainer.setAttribute('data-height', viewport.height.toString());

        // Create canvas - NO inline styles
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        if (!context) {
            console.error('[PDFJSRenderer] Could not get canvas context');
            return;
        }

        canvas.height = viewport.height;
        canvas.width = viewport.width;

        pageContainer.appendChild(canvas);
        container.appendChild(pageContainer);

        console.log('[PDFJSRenderer] Page', pageNum, 'rendered with theme:', this.colorMode, 'size:', viewport.width, 'x', viewport.height);

        // Render page
        const renderContext = {
            canvasContext: context,
            viewport: viewport
        };

        const renderTask = page.render(renderContext);
        this.renderTasks.push(renderTask);

        try {
            await renderTask.promise;
        } catch (error: any) {
            if (error?.name !== 'RenderingCancelledException') {
                console.error('[PDFJSRenderer] Error rendering page', pageNum, error);
            }
        }
    }

    /**
     * Update zoom level
     */
    async setScale(scale: number): Promise<void> {
        if (!this.pdfDoc) return;

        this.currentScale = scale;

        // Get the current scroll position ratio
        const pagesContainer = this.container.querySelector('.pdfjs-pages-container') as HTMLElement;
        if (!pagesContainer) return;

        const scrollRatio = pagesContainer.scrollTop / pagesContainer.scrollHeight;

        // Re-render all pages
        const numPages = this.pdfDoc.numPages;
        pagesContainer.innerHTML = '';

        for (let pageNum = 1; pageNum <= numPages; pageNum++) {
            await this.renderPage(pageNum, pagesContainer);
        }

        // Restore scroll position
        pagesContainer.scrollTop = scrollRatio * pagesContainer.scrollHeight;
    }

    /**
     * Set color mode and re-render
     */
    async setColorMode(mode: 'light' | 'dark'): Promise<void> {
        this.colorMode = mode;
        console.log('[PDFJSRenderer] Color mode set to:', mode);

        // Re-render all pages with new theme
        const pagesContainer = this.container.querySelector('.pdfjs-pages-container') as HTMLElement;
        if (pagesContainer && this.pdfDoc) {
            pagesContainer.setAttribute('data-pdf-theme', mode);
            pagesContainer.innerHTML = '';

            const numPages = this.pdfDoc.numPages;
            for (let pageNum = 1; pageNum <= numPages; pageNum++) {
                await this.renderPage(pageNum, pagesContainer);
            }
        }
    }

    /**
     * Get current color mode
     */
    getColorMode(): 'light' | 'dark' {
        return this.colorMode;
    }

    /**
     * Destroy renderer and cleanup
     */
    destroy(): void {
        // Cancel pending render tasks
        this.renderTasks.forEach(task => {
            if (task.cancel) task.cancel();
        });
        this.renderTasks = [];

        // Destroy PDF document
        if (this.pdfDoc) {
            this.pdfDoc.destroy();
            this.pdfDoc = null;
        }
    }
}
