/**
 * Panel Resizer Module
 * Handles draggable resizing of split panels (LaTeX editor and PDF preview)
 */
export declare class PanelResizer {
    private resizer;
    private leftPanel;
    private rightPanel;
    private container;
    private isResizing;
    private startX;
    private startLeftWidth;
    private minPanelWidth;
    private storageKey;
    constructor();
    /**
     * Initialize the panel resizer with event listeners
     */
    private initialize;
    /**
     * Load previously saved panel widths from localStorage
     */
    private loadPanelWidths;
    /**
     * Save panel widths to localStorage
     */
    private savePanelWidths;
    /**
     * Handle mouse down on resizer
     */
    private handleMouseDown;
    /**
     * Handle mouse move during resize
     */
    private handleMouseMove;
    /**
     * Handle mouse up to end resize
     */
    private handleMouseUp;
    /**
     * Reset panel widths to equal split (50:50)
     */
    resetToEqualSplit(): void;
    /**
     * Set specific panel widths
     */
    setPanelWidths(leftWidth: number, rightWidth: number): void;
    /**
     * Get current panel widths
     */
    getPanelWidths(): {
        leftWidth: number;
        rightWidth: number;
    };
    /**
     * Check if resizer is initialized
     */
    isInitialized(): boolean;
}
//# sourceMappingURL=panel-resizer.d.ts.map