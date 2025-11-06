/**
 * PDF Scroll and Zoom Handler
 * Provides native PDF viewer-like interaction:
 * - Mouse wheel scrolling within PDF (doesn't scroll page)
 * - Ctrl+drag for zoom with cursor centering
 * - Zoom level indicator and controls
 */
console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/editor/modules/pdf-scroll-zoom.ts loaded");
const PDF_COLOR_THEMES = {
    light: {
        name: 'light',
        label: 'Light',
        filter: 'none',
        backgroundColor: '#ffffff'
    },
    dark: {
        name: 'dark',
        label: 'Dark',
        filter: 'none', // No filter - colors handled by LaTeX compilation
        backgroundColor: '#1a1a1a'
    }
};
export class PDFScrollZoomHandler {
    container;
    pdfViewer = null;
    currentZoom = 100;
    minZoom = 50;
    maxZoom = 300;
    zoomStep = 10;
    isCtrlPressed = false;
    isDraggingZoom = false;
    dragStartX = 0;
    dragStartY = 0;
    dragStartZoom = 100;
    originalOverflow = '';
    colorMode = 'light';
    onColorModeChangeCallback;
    constructor(options) {
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
                this.pdfViewer = existingViewer;
                console.log('[PDFScrollZoom] Set pdfViewer reference on construction');
            }
            this.setupEventListeners();
        }
        else {
            console.warn('[PDFScrollZoom] Container not found!');
        }
    }
    /**
     * Setup all event listeners for scroll and zoom
     */
    setupEventListeners() {
        if (!this.container)
            return;
        // Track Ctrl key state
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        document.addEventListener('keyup', (e) => this.handleKeyUp(e));
        // Mouse wheel scrolling within PDF (use capture phase)
        this.container.addEventListener('wheel', (e) => this.handleWheel(e), true);
        // Also handle editor scrolling - find editor container and prioritize it
        const editorContainer = document.querySelector('.latex-panel');
        if (editorContainer) {
            editorContainer.addEventListener('wheel', (e) => this.handleEditorWheel(e), true);
        }
        // Ctrl+drag for zoom
        document.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        document.addEventListener('mousemove', (e) => this.handleMouseMove(e));
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
    handleEditorWheel(e) {
        const editorContainer = e.currentTarget;
        if (!editorContainer)
            return;
        // Check if target is actually inside the editor
        if (!editorContainer.contains(e.target))
            return;
        // DON'T prevent default - let browser handle native scrolling
        // The CSS will make the editor scrollable
    }
    /**
     * Setup mutation observer to track PDF viewer changes
     */
    setupMutationObserver() {
        if (!this.container)
            return;
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
                this.pdfViewer = currentViewer;
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
    handleKeyDown(e) {
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
    handleKeyUp(e) {
        if (e.key === 'Control' || e.key === 'Meta') {
            this.isCtrlPressed = false;
        }
    }
    /**
     * Handle mouse wheel - ALWAYS prioritize PDF scroll
     * Don't prevent default - let CSS handle scrolling, just check if we're over PDF
     */
    handleWheel(e) {
        if (!this.container)
            return;
        if (!this.pdfViewer)
            return;
        const isOverPDF = this.container.contains(e.target);
        if (!isOverPDF)
            return;
        // DON'T prevent default - let browser handle native scrolling
        // The CSS will make the PDF viewer scrollable with overflow-y: scroll
        // This allows native smooth scrolling
    }
    /**
     * Handle mouse down - start zoom drag
     */
    handleMouseDown(e) {
        if (!this.container || !this.isCtrlPressed)
            return;
        const isOverPDF = this.container.contains(e.target);
        if (!isOverPDF)
            return;
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
    handleMouseMove(e) {
        if (!this.isDraggingZoom || !this.pdfViewer)
            return;
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
    handleMouseUp() {
        if (!this.isDraggingZoom)
            return;
        this.isDraggingZoom = false;
        if (this.pdfViewer) {
            this.pdfViewer.style.cursor = this.originalOverflow || 'auto';
        }
    }
    /**
     * Handle touch start - start pinch zoom
     */
    handleTouchStart(e) {
        if (e.touches.length !== 2)
            return;
        e.preventDefault();
        const touch1 = e.touches[0];
        const touch2 = e.touches[1];
        const distance = Math.hypot(touch2.clientX - touch1.clientX, touch2.clientY - touch1.clientY);
        e.pinchStartDistance = distance;
        e.pinchStartZoom = this.currentZoom;
    }
    /**
     * Handle touch move - pinch zoom
     */
    handleTouchMove(e) {
        if (e.touches.length !== 2 || !e.pinchStartDistance)
            return;
        e.preventDefault();
        const touch1 = e.touches[0];
        const touch2 = e.touches[1];
        const distance = Math.hypot(touch2.clientX - touch1.clientX, touch2.clientY - touch1.clientY);
        const zoomRatio = distance / e.pinchStartDistance;
        const centerX = (touch1.clientX + touch2.clientX) / 2;
        const centerY = (touch1.clientY + touch2.clientY) / 2;
        const newZoom = Math.max(this.minZoom, Math.min(this.maxZoom, e.pinchStartZoom * zoomRatio));
        this.setZoom(newZoom, centerX, centerY);
    }
    /**
     * Handle touch end
     */
    handleTouchEnd(e) {
        e.pinchStartDistance = null;
        e.pinchStartZoom = null;
    }
    /**
     * Set zoom level with cursor/center point preservation
     */
    setZoom(zoomLevel, cursorX, cursorY) {
        if (!this.pdfViewer)
            return;
        const oldZoom = this.currentZoom;
        this.currentZoom = Math.max(this.minZoom, Math.min(this.maxZoom, zoomLevel));
        // Update embed scale via transform
        const embed = this.pdfViewer.querySelector('embed');
        if (embed) {
            const scaleRatio = this.currentZoom / 100;
            embed.style.transform = `scale(${scaleRatio})`;
            embed.style.transformOrigin = 'top center';
            embed.style.transition = 'none';
            // If cursor position provided, center zoom on cursor
            if (cursorX !== undefined && cursorY !== undefined) {
                this.centerZoomOnPoint(cursorX, cursorY, oldZoom);
            }
        }
        this.updateZoomIndicator();
        console.log(`[PDFScrollZoom] Zoom: ${this.currentZoom.toFixed(0)}%`);
    }
    /**
     * Center zoom on a specific point (cursor/touch point)
     */
    centerZoomOnPoint(pointX, pointY, oldZoom) {
        if (!this.pdfViewer)
            return;
        const rect = this.pdfViewer.getBoundingClientRect();
        const relX = pointX - rect.left;
        const relY = pointY - rect.top;
        // Calculate scroll adjustment to keep point centered
        const zoomRatio = this.currentZoom / oldZoom;
        const scrollLeftAdjust = (relX * (zoomRatio - 1)) / zoomRatio;
        const scrollTopAdjust = (relY * (zoomRatio - 1)) / zoomRatio;
        requestAnimationFrame(() => {
            this.pdfViewer.scrollLeft += scrollLeftAdjust;
            this.pdfViewer.scrollTop += scrollTopAdjust;
        });
    }
    /**
     * Zoom in
     */
    zoomIn() {
        const newZoom = this.currentZoom + this.zoomStep;
        this.setZoom(newZoom);
    }
    /**
     * Zoom out
     */
    zoomOut() {
        const newZoom = this.currentZoom - this.zoomStep;
        this.setZoom(newZoom);
    }
    /**
     * Reset zoom to 100%
     */
    resetZoom() {
        this.setZoom(100);
    }
    /**
     * Set zoom to fit page width
     */
    fitToWidth() {
        if (!this.pdfViewer || !this.pdfViewer.querySelector('embed'))
            return;
        const embed = this.pdfViewer.querySelector('embed');
        const embedWidth = embed.scrollWidth;
        const containerWidth = this.pdfViewer.clientWidth;
        const zoomLevel = (containerWidth / embedWidth) * 100;
        this.setZoom(zoomLevel);
    }
    /**
     * Set zoom to fit page height
     */
    fitToHeight() {
        if (!this.pdfViewer || !this.pdfViewer.querySelector('embed'))
            return;
        const embed = this.pdfViewer.querySelector('embed');
        const embedHeight = embed.scrollHeight;
        const containerHeight = this.pdfViewer.clientHeight;
        const zoomLevel = (containerHeight / embedHeight) * 100;
        this.setZoom(zoomLevel);
    }
    /**
     * Update zoom indicator in UI
     */
    updateZoomIndicator() {
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
    getCurrentZoom() {
        return this.currentZoom;
    }
    /**
     * Cycle through available PDF color modes
     */
    cycleColorMode() {
        const modes = ['light', 'dark'];
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
    toggleColorMode() {
        this.cycleColorMode();
    }
    /**
     * Set PDF color mode explicitly
     */
    setColorMode(mode) {
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
    getColorMode() {
        return this.colorMode;
    }
    /**
     * Apply color mode/theme filters to PDF embed
     * Uses CSS filters to apply different visual themes
     */
    applyColorMode() {
        const embed = this.pdfViewer?.querySelector('embed');
        if (!embed)
            return;
        const theme = PDF_COLOR_THEMES[this.colorMode];
        if (!theme) {
            console.warn('[PDFScrollZoom] Unknown color mode:', this.colorMode);
            return;
        }
        embed.style.filter = theme.filter;
        if (this.pdfViewer) {
            this.pdfViewer.style.backgroundColor = theme.backgroundColor;
        }
        console.log('[PDFScrollZoom] Applied theme:', theme.label);
    }
    /**
     * Load saved color mode preference from localStorage
     */
    loadColorModePreference() {
        const savedMode = localStorage.getItem('pdf-color-mode');
        if (savedMode === 'dark' || savedMode === 'light') {
            this.colorMode = savedMode;
        }
    }
    /**
     * Save color mode preference to localStorage
     */
    saveColorModePreference() {
        localStorage.setItem('pdf-color-mode', this.colorMode);
    }
    /**
     * Update color mode button state
     */
    updateColorModeButton() {
        const btn = document.getElementById('pdf-color-mode-btn');
        if (!btn)
            return;
        const theme = PDF_COLOR_THEMES[this.colorMode];
        const iconEl = btn.querySelector('i');
        const textEl = btn.querySelector('.theme-label');
        // Map color modes to icons
        const iconMap = {
            light: 'fas fa-sun',
            dark: 'fas fa-moon'
        };
        if (iconEl) {
            iconEl.className = iconMap[this.colorMode];
        }
        if (textEl) {
            textEl.textContent = theme.label;
        }
        btn.setAttribute('title', `PDF Theme: ${theme.label} (Click to cycle)`);
    }
    /**
     * Get available color modes
     */
    getAvailableColorModes() {
        return [
            { name: 'light', label: 'Light' },
            { name: 'dark', label: 'Dark' }
        ];
    }
    /**
     * Register callback for color mode changes
     */
    onColorModeChange(callback) {
        this.onColorModeChangeCallback = callback;
    }
    /**
     * Notify color mode change
     */
    notifyColorModeChange() {
        if (this.onColorModeChangeCallback) {
            this.onColorModeChangeCallback(this.colorMode);
        }
    }
    /**
     * Observe PDF viewer changes and reinitialize
     * (Already handled by setupMutationObserver in setupEventListeners)
     */
    observePDFViewer() {
        if (!this.container) {
            console.warn('[PDFScrollZoom] No container found for observing');
            return;
        }
        // First, check if PDF viewer already exists
        const existingViewer = this.container.querySelector('.pdf-preview-viewer');
        if (existingViewer) {
            this.pdfViewer = existingViewer;
            this.currentZoom = 100;
            this.updateZoomIndicator();
            this.loadColorModePreference();
            this.applyColorMode();
            this.updateColorModeButton();
            console.log('[PDFScrollZoom] Found existing PDF viewer');
        }
        // Load preference on first initialization
        this.loadColorModePreference();
    }
}
//# sourceMappingURL=pdf-scroll-zoom.js.map