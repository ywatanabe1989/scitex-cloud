/**
 * Preview Panel Manager
 * Handles LaTeX editor, templates, compilation, and PDF preview
 *
 * @version 2.0.0 (TypeScript)
 * @author SciTeX Development Team
 */
interface PreviewPanelConfig {
    quickCompileUrl: string;
    compilationStatusUrl: string;
    csrfToken: string;
}
export declare class PreviewPanelManager {
    private config;
    private editor;
    private currentJobId;
    private statusCheckInterval;
    private previewVisible;
    private saveTimeout;
    private compileBtn;
    private saveBtn;
    private statusIndicator;
    private compileStatus;
    private previewContent;
    private previewPanel;
    private togglePreviewBtn;
    private templateSelect;
    private documentTitle;
    constructor(config: PreviewPanelConfig);
    /**
     * Initialize the preview panel manager
     */
    initialize(): void;
    /**
     * Initialize CodeMirror editor
     */
    private initializeEditor;
    /**
     * Get DOM element references
     */
    private getDOMElements;
    /**
     * Setup all event listeners
     */
    private setupEventListeners;
    /**
     * Handle template selection change
     */
    private handleTemplateChange;
    /**
     * Toggle preview panel visibility
     */
    private togglePreview;
    /**
     * Save draft (auto-save functionality)
     */
    private saveDraft;
    /**
     * Compile LaTeX document to PDF
     */
    private compileDocument;
    /**
     * Start polling compilation status
     */
    private startStatusChecking;
    /**
     * Update job status display
     */
    private updateJobStatus;
    /**
     * Show PDF preview in iframe
     */
    private showPDFPreview;
    /**
     * Reset compile button UI
     */
    private resetCompileUI;
    /**
     * Handle compilation error
     */
    private handleError;
    /**
     * Update status indicator
     */
    private updateStatus;
    /**
     * Update compilation status message
     */
    private updateCompileStatus;
    /**
     * Handle editor content change
     */
    private handleEditorChange;
    /**
     * Destroy the preview panel manager and cleanup
     */
    destroy(): void;
}
declare global {
    interface Window {
        PreviewPanelManager: typeof PreviewPanelManager;
        previewPanelManager?: PreviewPanelManager;
    }
}
export {};
//# sourceMappingURL=preview-panel-manager.d.ts.map