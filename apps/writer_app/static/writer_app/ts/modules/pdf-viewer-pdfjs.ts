/**
 * PDF.js Viewer for Writer App
 * Replaces iframe-based PDF viewing with canvas-based rendering
 * Provides full control over scrollbars, themes, and rendering
 */

console.log("[DEBUG] pdf-viewer-pdfjs.ts loaded");

export interface PDFViewerOptions {
    containerId: string;
    colorMode?: 'light' | 'dark';
    fitToWidth?: boolean;
    onPageChange?: (pageNum: number) => void;
}

export class PDFJSViewer {
    private container: HTMLElement | null;
    private pdfDoc: any = null;
    private currentScale: number = 1.5;
    private currentPage: number = 1;
    private colorMode: 'light' | 'dark' = 'light';
    private fitToWidth: boolean = true;
    private onPageChangeCallback?: (pageNum: number) => void;
    private pdfjsLib: any = null;
    private isLoading: boolean = false;

    constructor(options: PDFViewerOptions) {
        this.container = document.getElementById(options.containerId);
        this.colorMode = options.colorMode || 'light';
        this.fitToWidth = options.fitToWidth ?? true;
        this.onPageChangeCallback = options.onPageChange;

        console.log('[PDFJSViewer] Initialized with container:', options.containerId, 'theme:', this.colorMode);

        // Load PDF.js library
        this.loadPDFJS();
    }

    /**
     * Load PDF.js from CDN
     */
    private loadPDFJS(): void {
        // Check if already loaded
        if ((window as any).pdfjsLib) {
            this.pdfjsLib = (window as any).pdfjsLib;
            console.log('[PDFJSViewer] PDF.js already loaded');
            return;
        }

        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js';
        script.onload = () => {
            this.pdfjsLib = (window as any).pdfjsLib;
            if (this.pdfjsLib) {
                this.pdfjsLib.GlobalWorkerOptions.workerSrc =
                    'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
                console.log('[PDFJSViewer] PDF.js loaded successfully');
            }
        };
        script.onerror = () => {
            console.error('[PDFJSViewer] Failed to load PDF.js');
        };
        document.head.appendChild(script);
    }

    /**
     * Load and render a PDF
     */
    async loadPDF(pdfUrl: string): Promise<void> {
        if (!this.container) {
            console.error('[PDFJSViewer] No container found');
            return;
        }

        if (!this.pdfjsLib) {
            console.warn('[PDFJSViewer] PDF.js not loaded yet, waiting...');
            // Wait for library to load
            await new Promise(resolve => setTimeout(resolve, 500));
            if (!this.pdfjsLib) {
                console.error('[PDFJSViewer] PDF.js still not available');
                return;
            }
        }

        if (this.isLoading) {
            console.warn('[PDFJSViewer] Already loading a PDF');
            return;
        }

        this.isLoading = true;

        // Show loading indicator
        this.container.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: var(--color-fg-muted);">
                <div style="text-align: center;">
                    <i class="fas fa-spinner fa-spin fa-2x mb-2"></i>
                    <p>Loading PDF...</p>
                </div>
            </div>
        `;

        try {
            console.log('[PDFJSViewer] Loading PDF:', pdfUrl, 'theme:', this.colorMode);

            const loadingTask = this.pdfjsLib.getDocument(pdfUrl);
            this.pdfDoc = await loadingTask.promise;

            console.log('[PDFJSViewer] PDF loaded:', this.pdfDoc.numPages, 'pages');

            // Render all pages
            await this.renderAllPages();

            this.isLoading = false;
        } catch (error) {
            console.error('[PDFJSViewer] Error loading PDF:', error);
            this.isLoading = false;

            if (this.container) {
                this.container.innerHTML = `
                    <div style="display: flex; align-items: center; justify-content: center; height: 100%; padding: 2rem; text-align: center; color: var(--color-danger-fg);">
                        <div>
                            <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                            <h5>Error Loading PDF</h5>
                            <p>${error instanceof Error ? error.message : 'Unknown error'}</p>
                        </div>
                    </div>
                `;
            }
        }
    }

    /**
     * Render all pages to canvas elements
     */
    private async renderAllPages(): Promise<void> {
        if (!this.pdfDoc || !this.container) return;

        // Create scrollable container with theme-responsive styling
        const viewerHtml = `
            <div class="pdfjs-viewer" id="pdfjs-viewer" data-theme="${this.colorMode}">
                <!-- Pages will be rendered here -->
            </div>
        `;

        this.container.innerHTML = viewerHtml;

        const viewer = document.getElementById('pdfjs-viewer');
        if (!viewer) return;

        // Calculate scale for fit-to-width
        if (this.fitToWidth) {
            const containerWidth = this.container.clientWidth;
            // Standard PDF page width is 612 points
            this.currentScale = (containerWidth - 40) / 612;
            console.log('[PDFJSViewer] Fit to width scale:', this.currentScale);
        }

        // Render each page
        for (let pageNum = 1; pageNum <= this.pdfDoc.numPages; pageNum++) {
            await this.renderPage(pageNum, viewer);
        }

        // Setup scroll listener
        this.setupScrollListener();
    }

    /**
     * Render a single page
     */
    private async renderPage(pageNum: number, container: HTMLElement): Promise<void> {
        try {
            const page = await this.pdfDoc.getPage(pageNum);
            const viewport = page.getViewport({ scale: this.currentScale });

            // Create page container
            const pageContainer = document.createElement('div');
            pageContainer.className = 'pdfjs-page-container';
            pageContainer.id = `pdfjs-page-${pageNum}`;
            pageContainer.dataset.pageNum = String(pageNum);
            pageContainer.style.cssText = `
                margin: 1rem auto;
                background: ${this.colorMode === 'dark' ? '#1a1a1a' : 'white'};
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                position: relative;
                width: ${viewport.width}px;
                height: ${viewport.height}px;
            `;

            // Create canvas
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            if (!context) return;

            canvas.height = viewport.height;
            canvas.width = viewport.width;
            canvas.style.display = 'block';

            pageContainer.appendChild(canvas);
            container.appendChild(pageContainer);

            // Render PDF page to canvas
            const renderContext = {
                canvasContext: context,
                viewport: viewport
            };

            await page.render(renderContext).promise;

            console.log('[PDFJSViewer] Rendered page', pageNum);
        } catch (error) {
            console.error(`[PDFJSViewer] Error rendering page ${pageNum}:`, error);
        }
    }

    /**
     * Setup scroll listener for page tracking
     */
    private setupScrollListener(): void {
        const viewer = document.getElementById('pdfjs-viewer');
        if (!viewer) return;

        let scrollTimeout: number;

        viewer.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = window.setTimeout(() => {
                this.updateCurrentPageFromScroll();
            }, 100);
        });
    }

    /**
     * Update current page based on scroll position
     */
    private updateCurrentPageFromScroll(): void {
        const viewer = document.getElementById('pdfjs-viewer');
        if (!viewer) return;

        const pages = Array.from(viewer.querySelectorAll('.pdfjs-page-container'));
        const scrollTop = viewer.scrollTop;
        const viewportMiddle = scrollTop + viewer.clientHeight / 3;

        for (const page of pages) {
            const pageElement = page as HTMLElement;
            const pageTop = pageElement.offsetTop;
            const pageBottom = pageTop + pageElement.offsetHeight;

            if (viewportMiddle >= pageTop && viewportMiddle < pageBottom) {
                const pageNumStr = pageElement.dataset.pageNum;
                if (pageNumStr) {
                    const pageNum = parseInt(pageNumStr);
                    if (pageNum !== this.currentPage) {
                        this.currentPage = pageNum;
                        if (this.onPageChangeCallback) {
                            this.onPageChangeCallback(pageNum);
                        }
                        console.log('[PDFJSViewer] Current page:', pageNum);
                    }
                }
                break;
            }
        }
    }

    /**
     * Set color mode and re-render
     */
    setColorMode(colorMode: 'light' | 'dark'): void {
        if (this.colorMode === colorMode) return;

        this.colorMode = colorMode;
        console.log('[PDFJSViewer] Color mode changed to:', colorMode);

        // Re-render pages with new theme
        if (this.pdfDoc) {
            this.renderAllPages();
        }
    }

    /**
     * Set zoom level and re-render
     */
    setScale(scale: number): void {
        if (scale < 0.5 || scale > 3.0) return;

        this.currentScale = scale;
        console.log('[PDFJSViewer] Scale changed to:', scale);

        if (this.pdfDoc) {
            this.renderAllPages();
        }
    }

    /**
     * Zoom in
     */
    zoomIn(): void {
        this.setScale(this.currentScale + 0.25);
    }

    /**
     * Zoom out
     */
    zoomOut(): void {
        this.setScale(this.currentScale - 0.25);
    }

    /**
     * Fit to width
     */
    fitWidth(): void {
        if (!this.container) return;
        const containerWidth = this.container.clientWidth;
        const newScale = (containerWidth - 40) / 612; // Standard PDF width
        this.setScale(newScale);
    }

    /**
     * Go to page
     */
    gotoPage(pageNum: number): void {
        if (pageNum < 1 || (this.pdfDoc && pageNum > this.pdfDoc.numPages)) return;

        this.currentPage = pageNum;
        const pageElement = document.getElementById(`pdfjs-page-${pageNum}`);
        if (pageElement) {
            pageElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    /**
     * Get total pages
     */
    getPageCount(): number {
        return this.pdfDoc ? this.pdfDoc.numPages : 0;
    }

    /**
     * Get current page
     */
    getCurrentPage(): number {
        return this.currentPage;
    }
}

// EOF
