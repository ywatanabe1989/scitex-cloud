/**
 * Panel Resizer Module
 * Handles draggable divider between editor and preview panels
 */
export declare class PanelResizer {
    private resizer;
    private leftPanel;
    private rightPanel;
    private container;
    private isResizing;
    private startX;
    private startLeftWidth;
    constructor(containerId?: string);
    /**
     * Initialize resizer event listeners
     */
    private init;
    /**
     * Handle mouse down on resizer
     */
    private handleMouseDown;
    /**
     * Handle mouse move during resize
     */
    private handleMouseMove;
    /**
     * Handle mouse up
     */
    private handleMouseUp;
    /**
     * Restore saved panel width from localStorage
     */
    restoreSavedWidth(): void;
    /**
     * Reset to default 50:50 split
     */
    resetToDefault(): void;
    /**
     * Check if the resizer is properly initialized
     */
    isInitialized(): boolean;
}
//# sourceMappingURL=panel-resizer.d.ts.map