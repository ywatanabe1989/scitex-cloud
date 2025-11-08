/**
 * PDF Scroll and Zoom Handler
 * Provides native PDF viewer-like interaction:
 * - Mouse wheel scrolling within PDF (doesn't scroll page)
 * - Ctrl+drag for zoom with cursor centering
 * - Zoom level indicator and controls
 */

console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/modules/pdf-scroll-zoom.ts loaded");
export interface PDFScrollZoomOptions {
    containerId: string;
    minZoom?: number;
    maxZoom?: number;
    zoomStep?: number;
}

type PDFColorMode = 'light' | 'dark';

export interface PDFColorTheme {
    name: string;
    label: string;
    filter: string;
    backgroundColor: string;
}

const PDF_COLOR_THEMES: Record<PDFColorMode, PDFColorTheme> = {
    light: {
        name: 'light',
        label: 'Light',
        filter: 'none',
        backgroundColor: '#ffffff'
    },
    dark: {
        name: 'dark',
        label: 'Dark',
        filter: 'none',  // No filter - colors handled by LaTeX compilation
        backgroundColor: '#1a1a1a'
    }
};

export class PDFScrollZoomHandler {
    private container: HTMLElement | null;
    private pdfViewer: HTMLElement | null = null;
    private currentZoom: number = 100;
    private minZoom: number = 50;
    private maxZoom: number = 300;
    private zoomStep: number = 10;
    private isCtrlPressed: boolean = false;
    private isDraggingZoom: boolean = false;
    private dragStartX: number = 0;
    private dragStartY: number = 0;
    private dragStartZoom: number = 100;
    private originalOverflow: string = '';
    private colorMode: PDFColorMode = 'light';
    private onColorModeChangeCallback?: (colorMode: PDFColorMode) => void;

    constructor(options: PDFScrollZoomOptions) {
        this.container = document.getElementById(options.containerId);
        this.minZoom = options.minZoom || 50;
        this.maxZoom = options.maxZoom || 300;
        this.zoomStep = options.zoomStep || 10;

        console.log('[PDFScrollZoom] Constructor called, containerId:', options.containerId);
        console.log('[PDFScrollZoom] Container found:', !!this.container);

        if (this.container) {
            // Try to find existing PDF viewer immediately
            const existingViewer = this.container.querySelector('.pdf-preview-viewer');
            console.log('[PDFScrollZoom] Existing PDF viewer found:', !!existingViewer);
            if (existingViewer) {
                this.pdfViewer = existingViewer as HTMLElement;
                console.log('[PDFScrollZoom] Set pdfViewer reference on construction');
            }

            this.setupEventListeners();
        } else {
            console.warn('[PDFScrollZoom] Container not found!');
        }
    }

    /**
     * Setup all event listeners for scroll and zoom
     */
    private setupEventListeners(): void {
        if (!this.container) return;

        // Track Ctrl key state
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        document.addEventListener('keyup', (e) => this.handleKeyUp(e));

        // Mouse wheel scrolling within PDF (use capture phase)
        this.container.addEventListener('wheel', (e) => this.handleWheel(e), true);

        // Also handle editor scrolling - find editor container and prioritize it
        const editorContainer = document.querySelector('.latex-panel');
        if (editorContainer) {
            editorContainer.addEventListener('wheel', (e: any) => this.handleEditorWheel(e as WheelEvent), true);
        }

        // Ctrl+drag for zoom
        document.addEventListener('mousedown', (e: any) => this.handleMouseDown(e as MouseEvent));
        document.addEventListener('mousemove', (e: any) => this.handleMouseMove(e as MouseEvent));
        document.addEventListener('mouseup', () => this.handleMouseUp());

        // Touch gestures for zoom (pinch)
        this.container.addEventListener('touchstart', (e) => this.handleTouchStart(e), true);
        this.container.addEventListener('touchmove', (e) => this.handleTouchMove(e), true);
        this.container.addEventListener('touchend', (e) => this.handleTouchEnd(e), true);

        // Setup mutation observer to detect PDF viewer changes
        this.setupMutationObserver();

        console.log('[PDFScrollZoom] Event listeners initialized');
    }

    /**
     * Handle mouse wheel for editor - just tracking, let CSS handle scrolling
     */
    private handleEditorWheel(e: WheelEvent): void {
        const editorContainer = e.currentTarget as HTMLElement;
        if (!editorContainer) return;

        // Check if target is actually inside the editor
        if (!editorContainer.contains(e.target as Node)) return;

        // DON'T prevent default - let browser handle native scrolling
        // The CSS will make the editor scrollable
    }

    /**
     * Setup mutation observer to track PDF viewer changes
     */
    private setupMutationObserver(): void {
        if (!this.container) return;

        let observerCallCount = 0;

        const observer = new MutationObserver(() => {
            observerCallCount++;
            const currentViewer = this.container?.querySelector('.pdf-preview-viewer');

            // Log every mutation to debug
            if (observerCallCount % 10 === 0) {
                console.log('[PDFScrollZoom] Observer called', observerCallCount, 'times');
            }

            // If viewer changed, update reference
            if (currentViewer && currentViewer !== this.pdfViewer) {
                console.log('[PDFScrollZoom] PDF viewer CHANGED - updating reference, old:', this.pdfViewer, 'new:', currentViewer);
                this.pdfViewer = currentViewer as HTMLElement;
                this.currentZoom = 100;
                this.updateZoomIndicator();
                this.loadColorModePreference();
                this.applyColorMode();
                this.updateColorModeButton();
                console.log('[PDFScrollZoom] PDF viewer reference updated, scrollHeight:', this.pdfViewer?.scrollHeight, 'clientHeight:', this.pdfViewer?.clientHeight);
            }
        });

        observer.observe(this.container, {
            childList: true,
            subtree: true,
            attributes: false,
            characterData: false
        });

        console.log('[PDFScrollZoom] Mutation observer setup on container:', this.container);
    }

    /**
     * Handle keyboard - track Ctrl key
     */
    private handleKeyDown(e: KeyboardEvent): void {
        if (e.key === 'Control' || e.key === 'Meta') {
            this.isCtrlPressed = true;
        }

        // Ctrl + Plus: zoom in
        if (this.isCtrlPressed && (e.key === '+' || e.key === '=')) {
            e.preventDefault();
            this.zoomIn();
        }

        // Ctrl + Minus: zoom out
        if (this.isCtrlPressed && e.key === '-') {
            e.preventDefault();
            this.zoomOut();
        }

        // Ctrl + 0: reset zoom
        if (this.isCtrlPressed && e.key === '0') {
            e.preventDefault();
            this.resetZoom();
        }
    }

    /**
     * Handle keyboard - untrack Ctrl key
     */
    private handleKeyUp(e: KeyboardEvent): void {
        if (e.key === 'Control' || e.key === 'Meta') {
            this.isCtrlPressed = false;
        }
    }

    /**
     * Handle mouse wheel - ALWAYS prioritize PDF scroll
     * Don't prevent default - let CSS handle scrolling, just check if we're over PDF
     */
    private handleWheel(e: WheelEvent): void {
        if (!this.container) return;
        if (!this.pdfViewer) return;

        const isOverPDF = this.container.contains(e.target as Node);
        if (!isOverPDF) return;

        // DON'T prevent default - let browser handle native scrolling
        // The CSS will make the PDF viewer scrollable with overflow-y: scroll
        // This allows native smooth scrolling
    }

    /**
     * Handle mouse down - start zoom drag
     */
    private handleMouseDown(e: MouseEvent): void {
        if (!this.container || !this.isCtrlPressed) return;

        const isOverPDF = this.container.contains(e.target as Node);
        if (!isOverPDF) return;

        e.preventDefault();
        this.isDraggingZoom = true;
        this.dragStartX = e.clientX;
        this.dragStartY = e.clientY;
        this.dragStartZoom = this.currentZoom;

        // Change cursor to indicate zoom mode
        if (this.pdfViewer) {
            this.originalOverflow = this.pdfViewer.style.cursor;
            this.pdfViewer.style.cursor = 'grab';
        }
    }

    /**
     * Handle mouse move - drag zoom
     */
    private handleMouseMove(e: MouseEvent): void {
        if (!this.isDraggingZoom || !this.pdfViewer) return;

        // Use both X and Y delta for better zoom control (diagonal drag for better UX)
        const deltaY = this.dragStartY - e.clientY;
        const deltaX = e.clientX - this.dragStartX;
        const delta = deltaY + (deltaX * 0.5); // Y movement is primary, X is secondary
        const zoomDelta = (delta / 100) * this.zoomStep;
        const newZoom = Math.max(this.minZoom, Math.min(this.maxZoom, this.dragStartZoom + zoomDelta));

        this.setZoom(newZoom, e.clientX, e.clientY);
    }

    /**
     * Handle mouse up - end zoom drag
     */
    private handleMouseUp(): void {
        if (!this.isDraggingZoom) return;

        this.isDraggingZoom = false;
        if (this.pdfViewer) {
            this.pdfViewer.style.cursor = this.originalOverflow || 'auto';
        }
    }

    /**
     * Handle touch start - start pinch zoom
     */
    private handleTouchStart(e: TouchEvent): void {
        if (e.touches.length !== 2) return;
        e.preventDefault();

        const touch1 = e.touches[0];
        const touch2 = e.touches[1];
        const distance = Math.hypot(touch2.clientX - touch1.clientX, touch2.clientY - touch1.clientY);

        (e as any).pinchStartDistance = distance;
        (e as any).pinchStartZoom = this.currentZoom;
    }

    /**
     * Handle touch move - pinch zoom
     */
    private handleTouchMove(e: TouchEvent): void {
        if (e.touches.length !== 2 || !(e as any).pinchStartDistance) return;
        e.preventDefault();

        const touch1 = e.touches[0];
        const touch2 = e.touches[1];
        const distance = Math.hypot(touch2.clientX - touch1.clientX, touch2.clientY - touch1.clientY);

        const zoomRatio = distance / (e as any).pinchStartDistance;
        const centerX = (touch1.clientX + touch2.clientX) / 2;
        const centerY = (touch1.clientY + touch2.clientY) / 2;

        const newZoom = Math.max(this.minZoom, Math.min(this.maxZoom, (e as any).pinchStartZoom * zoomRatio));
        this.setZoom(newZoom, centerX, centerY);
    }

    /**
     * Handle touch end
     */
    private handleTouchEnd(e: TouchEvent): void {
        (e as any).pinchStartDistance = null;
        (e as any).pinchStartZoom = null;
    }

    /**
     * Set zoom level with cursor/center point preservation
     */
    private async setZoom(zoomLevel: number, cursorX?: number, cursorY?: number): Promise<void> {
        if (!this.pdfViewer) return;

        const oldZoom = this.currentZoom;
        this.currentZoom = Math.max(this.minZoom, Math.min(this.maxZoom, zoomLevel));

        // Check if using PDF.js (canvas) or legacy embed/iframe
        const isPDFJS = this.pdfViewer.querySelector('.pdfjs-pages-container') !== null;

        if (isPDFJS) {
            // PDF.js zoom - call PDFPreviewManager's setZoomScale
            const pdfPreviewManager = (window as any).modulePdfPreviewManager;
            if (pdfPreviewManager && typeof pdfPreviewManager.setZoomScale === 'function') {
                const scale = this.currentZoom / 100;
                await pdfPreviewManager.setZoomScale(scale);
                console.log(`[PDFScrollZoom] PDF.js zoom: ${this.currentZoom.toFixed(0)}%`);
            }
        } else {
            // Legacy embed/iframe zoom via transform
            const embed = this.pdfViewer.querySelector('embed, iframe');
            if (embed) {
                const scaleRatio = this.currentZoom / 100;
                (embed as HTMLElement).style.transform = `scale(${scaleRatio})`;
                (embed as HTMLElement).style.transformOrigin = 'top center';
                (embed as HTMLElement).style.transition = 'none';

                // If cursor position provided, center zoom on cursor
                if (cursorX !== undefined && cursorY !== undefined) {
                    this.centerZoomOnPoint(cursorX, cursorY, oldZoom);
                }
            }
        }

        this.updateZoomIndicator();
        console.log(`[PDFScrollZoom] Zoom: ${this.currentZoom.toFixed(0)}%`);
    }

    /**
     * Center zoom on a specific point (cursor/touch point)
     */
    private centerZoomOnPoint(pointX: number, pointY: number, oldZoom: number): void {
        if (!this.pdfViewer) return;

        const rect = this.pdfViewer.getBoundingClientRect();
        const relX = pointX - rect.left;
        const relY = pointY - rect.top;

        // Calculate scroll adjustment to keep point centered
        const zoomRatio = this.currentZoom / oldZoom;
        const scrollLeftAdjust = (relX * (zoomRatio - 1)) / zoomRatio;
        const scrollTopAdjust = (relY * (zoomRatio - 1)) / zoomRatio;

        requestAnimationFrame(() => {
            this.pdfViewer!.scrollLeft += scrollLeftAdjust;
            this.pdfViewer!.scrollTop += scrollTopAdjust;
        });
    }

    /**
     * Zoom in
     */
    async zoomIn(): Promise<void> {
        const newZoom = this.currentZoom + this.zoomStep;
        await this.setZoom(newZoom);
    }

    /**
     * Zoom out
     */
    async zoomOut(): Promise<void> {
        const newZoom = this.currentZoom - this.zoomStep;
        await this.setZoom(newZoom);
    }

    /**
     * Reset zoom to 100%
     */
    async resetZoom(): Promise<void> {
        await this.setZoom(100);
    }

    /**
     * Set zoom to fit page width
     */
    fitToWidth(): void {
        if (!this.pdfViewer || !this.pdfViewer.querySelector('embed')) return;

        const embed = this.pdfViewer.querySelector('embed') as HTMLEmbedElement;
        const embedWidth = embed.scrollWidth;
        const containerWidth = this.pdfViewer.clientWidth;

        const zoomLevel = (containerWidth / embedWidth) * 100;
        this.setZoom(zoomLevel);
    }

    /**
     * Set zoom to fit page height
     */
    fitToHeight(): void {
        if (!this.pdfViewer || !this.pdfViewer.querySelector('embed')) return;

        const embed = this.pdfViewer.querySelector('embed') as HTMLEmbedElement;
        const embedHeight = embed.scrollHeight;
        const containerHeight = this.pdfViewer.clientHeight;

        const zoomLevel = (containerHeight / embedHeight) * 100;
        this.setZoom(zoomLevel);
    }

    /**
     * Update zoom indicator in UI
     */
    private updateZoomIndicator(): void {
        const indicator = document.getElementById('pdf-zoom-indicator');
        if (indicator) {
            indicator.textContent = `${this.currentZoom.toFixed(0)}%`;
        }

        // Update button states if available
        const zoomInBtn = document.getElementById('pdf-zoom-in-btn');
        const zoomOutBtn = document.getElementById('pdf-zoom-out-btn');

        if (zoomInBtn) {
            zoomInBtn.setAttribute('disabled', this.currentZoom >= this.maxZoom ? 'true' : 'false');
        }
        if (zoomOutBtn) {
            zoomOutBtn.setAttribute('disabled', this.currentZoom <= this.minZoom ? 'true' : 'false');
        }
    }

    /**
     * Get current zoom level
     */
    getCurrentZoom(): number {
        return this.currentZoom;
    }

    /**
     * Cycle through available PDF color modes
     */
    cycleColorMode(): void {
        const modes: PDFColorMode[] = ['light', 'dark'];
        const currentIndex = modes.indexOf(this.colorMode);
        const nextIndex = (currentIndex + 1) % modes.length;
        this.colorMode = modes[nextIndex];
        this.applyColorMode();
        this.saveColorModePreference();
        this.updateColorModeButton();
        console.log('[PDFScrollZoom] Color mode toggled to:', this.colorMode);

        // Trigger recompilation to apply color mode
        this.notifyColorModeChange();
    }

    /**
     * Alias for backward compatibility - toggle between light and dark
     */
    toggleColorMode(): void {
        this.cycleColorMode();
    }

    /**
     * Set PDF color mode explicitly
     */
    setColorMode(mode: PDFColorMode): void {
        if (!(mode in PDF_COLOR_THEMES)) {
            console.warn('[PDFScrollZoom] Unknown color mode:', mode);
            return;
        }
        this.colorMode = mode;
        this.applyColorMode();
        this.saveColorModePreference();
        this.updateColorModeButton();
        console.log('[PDFScrollZoom] Color mode set to:', this.colorMode);
    }

    /**
     * Get current color mode
     */
    getColorMode(): PDFColorMode {
        return this.colorMode;
    }

    /**
     * Apply color mode/theme filters to PDF embed
     * Uses CSS filters to apply different visual themes
     */
    private applyColorMode(): void {
        const embed = this.pdfViewer?.querySelector('embed');
        if (!embed) return;

        const theme = PDF_COLOR_THEMES[this.colorMode];
        if (!theme) {
            console.warn('[PDFScrollZoom] Unknown color mode:', this.colorMode);
            return;
        }

        embed.style.filter = theme.filter;
        if (this.pdfViewer) {
            this.pdfViewer.style.backgroundColor = theme.backgroundColor;
        }

        // Set data attribute on all PDF-related containers for theme-responsive scrollbar
        const textPreview = document.getElementById('text-preview');
        if (textPreview) {
            textPreview.setAttribute('data-pdf-theme', this.colorMode);
        }

        const pdfPreviewContainer = document.querySelector('.pdf-preview-container');
        if (pdfPreviewContainer) {
            pdfPreviewContainer.setAttribute('data-pdf-theme', this.colorMode);
        }

        if (this.pdfViewer) {
            this.pdfViewer.setAttribute('data-pdf-theme', this.colorMode);
        }

        console.log('[PDFScrollZoom] Applied theme:', theme.label);
    }

    /**
     * Load saved color mode preference from localStorage
     * Defaults to global theme if no PDF-specific preference is saved
     */
    private loadColorModePreference(): void {
        const savedMode = localStorage.getItem('pdf-color-mode') as PDFColorMode | null;

        if (savedMode === 'dark' || savedMode === 'light') {
            // Use saved PDF-specific preference
            this.colorMode = savedMode;
        } else {
            // Default to global theme
            const globalTheme = document.documentElement.getAttribute('data-theme') ||
                               localStorage.getItem('theme') ||
                               'light';
            this.colorMode = (globalTheme === 'dark' ? 'dark' : 'light') as PDFColorMode;
            console.log('[PDFScrollZoom] No PDF theme saved, defaulting to global theme:', this.colorMode);
        }
    }

    /**
     * Save color mode preference to localStorage
     */
    private saveColorModePreference(): void {
        localStorage.setItem('pdf-color-mode', this.colorMode);
    }

    /**
     * Update color mode button state
     */
    private updateColorModeButton(): void {
        const btn = document.getElementById('pdf-color-mode-btn');
        if (!btn) return;

        const theme = PDF_COLOR_THEMES[this.colorMode];
        const iconEl = btn.querySelector('.theme-icon');

        // Map color modes to emoji - show what the PDF SHOULD look like
        // Moon = dark mode (black bg, white text), Sun = light mode (white bg, black text)
        const iconMap: Record<PDFColorMode, string> = {
            dark: '🌙',   // Moon emoji = Dark mode (BLACK background, WHITE text)
            light: '☀️'   // Sun emoji = Light mode (WHITE background, BLACK text)
        };

        if (iconEl) {
            iconEl.textContent = iconMap[this.colorMode];
        }

        btn.setAttribute('title', `PDF Theme: ${theme.label} (Click to toggle)`);
    }

    /**
     * Get available color modes
     */
    getAvailableColorModes(): { name: PDFColorMode; label: string }[] {
        return [
            { name: 'light', label: 'Light' },
            { name: 'dark', label: 'Dark' }
        ];
    }

    /**
     * Register callback for color mode changes
     */
    onColorModeChange(callback: (colorMode: PDFColorMode) => void): void {
        this.onColorModeChangeCallback = callback;
    }

    /**
     * Notify color mode change
     */
    private notifyColorModeChange(): void {
        if (this.onColorModeChangeCallback) {
            this.onColorModeChangeCallback(this.colorMode);
        }
    }

    /**
     * Observe PDF viewer changes and reinitialize
     * (Already handled by setupMutationObserver in setupEventListeners)
     */
    observePDFViewer(): void {
        if (!this.container) {
            console.warn('[PDFScrollZoom] No container found for observing');
            return;
        }

        // First, check if PDF viewer already exists
        const existingViewer = this.container.querySelector('.pdf-preview-viewer');
        if (existingViewer) {
            this.pdfViewer = existingViewer as HTMLElement;
            this.currentZoom = 100;
            this.updateZoomIndicator();
            this.loadColorModePreference();
            this.applyColorMode();
            this.updateColorModeButton();
            console.log('[PDFScrollZoom] Found existing PDF viewer');
        }

        // Load preference on first initialization
        // Note: Will default to global theme if no PDF-specific preference saved
        this.loadColorModePreference();

        // Apply the theme and update button icon immediately on page load
        this.applyColorMode();
        this.updateColorModeButton();
    }
}
