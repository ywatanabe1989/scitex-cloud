/**
 * PDF Preview Module
 * Handles live PDF preview with auto-compilation
 */
export interface PDFPreviewOptions {
    containerId: string;
    projectId: number;
    manuscriptTitle: string;
    author?: string;
    autoCompile?: boolean;
    compileDelay?: number;
    apiBaseUrl?: string;
    docType?: string;
}
export declare class PDFPreviewManager {
    private container;
    private compilationManager;
    private latexWrapper;
    private projectId;
    private autoCompile;
    private compileDelay;
    private docType;
    private compileTimeout;
    private currentPdfUrl;
    constructor(options: PDFPreviewOptions);
    /**
     * Setup event listeners for compilation
     */
    private setupEventListeners;
    /**
     * Schedule auto-compilation
     */
    scheduleAutoCompile(sections: {
        name: string;
        content: string;
    }[]): void;
    /**
     * Compile document
     */
    compile(sections: {
        name: string;
        content: string;
    }[]): Promise<void>;
    /**
     * Set the document type for compilation
     */
    setDocType(docType: string): void;
    /**
     * Compile minimal document for quick preview
     */
    compileQuick(content: string): Promise<void>;
    /**
     * Display PDF in container
     */
    private displayPdf;
    /**
     * Display error message
     */
    private displayError;
    /**
     * Update progress display
     */
    private updateProgress;
    /**
     * Display placeholder
     */
    displayPlaceholder(): void;
    /**
     * Get current PDF URL
     */
    getCurrentPdfUrl(): string | null;
    /**
     * Check if currently compiling
     */
    isCompiling(): boolean;
    /**
     * Cancel compilation
     */
    cancel(jobId: string): Promise<boolean>;
    /**
     * Set auto-compile flag
     */
    setAutoCompile(enabled: boolean): void;
    /**
     * Set compile delay
     */
    setCompileDelay(delayMs: number): void;
    /**
     * Set manuscript title
     */
    setTitle(title: string): void;
    /**
     * Set manuscript author
     */
    setAuthor(author: string): void;
}
//# sourceMappingURL=pdf-preview.d.ts.map