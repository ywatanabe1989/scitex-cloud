/**
 * PDF Scroll and Zoom Handler
 * Provides native PDF viewer-like interaction:
 * - Mouse wheel scrolling within PDF (doesn't scroll page)
 * - Ctrl+drag for zoom with cursor centering
 * - Zoom level indicator and controls
 */
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
export declare class PDFScrollZoomHandler {
    private container;
    private pdfViewer;
    private currentZoom;
    private minZoom;
    private maxZoom;
    private zoomStep;
    private isCtrlPressed;
    private isDraggingZoom;
    private dragStartX;
    private dragStartY;
    private dragStartZoom;
    private originalOverflow;
    private colorMode;
    private onColorModeChangeCallback?;
    constructor(options: PDFScrollZoomOptions);
    /**
     * Setup all event listeners for scroll and zoom
     */
    private setupEventListeners;
    /**
     * Handle mouse wheel for editor - just tracking, let CSS handle scrolling
     */
    private handleEditorWheel;
    /**
     * Setup mutation observer to track PDF viewer changes
     */
    private setupMutationObserver;
    /**
     * Handle keyboard - track Ctrl key
     */
    private handleKeyDown;
    /**
     * Handle keyboard - untrack Ctrl key
     */
    private handleKeyUp;
    /**
     * Handle mouse wheel - ALWAYS prioritize PDF scroll
     * Don't prevent default - let CSS handle scrolling, just check if we're over PDF
     */
    private handleWheel;
    /**
     * Handle mouse down - start zoom drag
     */
    private handleMouseDown;
    /**
     * Handle mouse move - drag zoom
     */
    private handleMouseMove;
    /**
     * Handle mouse up - end zoom drag
     */
    private handleMouseUp;
    /**
     * Handle touch start - start pinch zoom
     */
    private handleTouchStart;
    /**
     * Handle touch move - pinch zoom
     */
    private handleTouchMove;
    /**
     * Handle touch end
     */
    private handleTouchEnd;
    /**
     * Set zoom level with cursor/center point preservation
     */
    private setZoom;
    /**
     * Center zoom on a specific point (cursor/touch point)
     */
    private centerZoomOnPoint;
    /**
     * Zoom in
     */
    zoomIn(): void;
    /**
     * Zoom out
     */
    zoomOut(): void;
    /**
     * Reset zoom to 100%
     */
    resetZoom(): void;
    /**
     * Set zoom to fit page width
     */
    fitToWidth(): void;
    /**
     * Set zoom to fit page height
     */
    fitToHeight(): void;
    /**
     * Update zoom indicator in UI
     */
    private updateZoomIndicator;
    /**
     * Get current zoom level
     */
    getCurrentZoom(): number;
    /**
     * Cycle through available PDF color modes
     */
    cycleColorMode(): void;
    /**
     * Alias for backward compatibility - toggle between light and dark
     */
    toggleColorMode(): void;
    /**
     * Set PDF color mode explicitly
     */
    setColorMode(mode: PDFColorMode): void;
    /**
     * Get current color mode
     */
    getColorMode(): PDFColorMode;
    /**
     * Apply color mode/theme filters to PDF embed
     * Uses CSS filters to apply different visual themes
     */
    private applyColorMode;
    /**
     * Load saved color mode preference from localStorage
     */
    private loadColorModePreference;
    /**
     * Save color mode preference to localStorage
     */
    private saveColorModePreference;
    /**
     * Update color mode button state
     */
    private updateColorModeButton;
    /**
     * Get available color modes
     */
    getAvailableColorModes(): {
        name: PDFColorMode;
        label: string;
    }[];
    /**
     * Register callback for color mode changes
     */
    onColorModeChange(callback: (colorMode: PDFColorMode) => void): void;
    /**
     * Notify color mode change
     */
    private notifyColorModeChange;
    /**
     * Observe PDF viewer changes and reinitialize
     * (Already handled by setupMutationObserver in setupEventListeners)
     */
    observePDFViewer(): void;
}
export {};
//# sourceMappingURL=pdf-scroll-zoom.d.ts.map