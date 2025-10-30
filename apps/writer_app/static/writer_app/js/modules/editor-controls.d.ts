/**
 * Editor Controls Module
 * Handles font size adjustment and auto-preview functionality
 */
export interface EditorControlsOptions {
    pdfPreviewManager?: any;
    compilationManager?: any;
    editor?: any;
}
export declare class EditorControls {
    private fontSizeSlider;
    private fontSizeDisplay;
    private autoPreviewCheckbox;
    private previewButton;
    private latexEditor;
    private pdfPreviewManager;
    private editor;
    private _compilationManager;
    private autoPreviewTimeout;
    private defaultFontSize;
    private storageFontSizeKey;
    private storageAutoPreviewKey;
    constructor(options?: EditorControlsOptions);
    /**
     * Initialize editor controls with event listeners
     */
    private initialize;
    /**
     * Handle font size slider change
     */
    private handleFontSizeChange;
    /**
     * Load font size from localStorage
     */
    private loadFontSize;
    /**
     * Handle auto preview checkbox toggle
     */
    private handleAutoPreviewToggle;
    /**
     * Load auto-preview preference from localStorage
     */
    private loadAutoPreviewPreference;
    /**
     * Setup auto-preview trigger on editor changes
     */
    private setupAutoPreviewTrigger;
    /**
     * Clear auto-preview timeout
     */
    private clearAutoPreviewTimeout;
    /**
     * Handle preview button click
     */
    private handlePreviewClick;
    /**
     * Trigger PDF preview compilation
     */
    private triggerPreview;
    /**
     * Set PDF preview manager reference (for dynamic initialization)
     */
    setPDFPreviewManager(pdfPreviewManager: any): void;
    /**
     * Set compilation manager reference (for dynamic initialization)
     */
    setCompilationManager(compilationManager: any): void;
    /**
     * Get current font size
     */
    getFontSize(): number;
    /**
     * Set font size programmatically
     */
    setFontSize(fontSize: number): void;
    /**
     * Check if auto-preview is enabled
     */
    isAutoPreviewEnabled(): boolean;
    /**
     * Set auto-preview enabled state
     */
    setAutoPreviewEnabled(enabled: boolean): void;
}
//# sourceMappingURL=editor-controls.d.ts.map