/**
 * Writer Compilation Module
 * Handles LaTeX compilation and PDF generation
 */
import { CompilationJob } from '@/types';
export interface CompilationOptions {
    projectId: number;
    docType: string;
    content?: string;
    format?: 'pdf' | 'dvi';
    colorMode?: 'light' | 'dark';
    sectionName?: string;
}
export declare class CompilationManager {
    private apiClient;
    private currentJob;
    private isCompiling;
    private onProgressCallback?;
    private onCompleteCallback?;
    private onErrorCallback?;
    constructor(apiBaseUrl?: string);
    /**
     * Compile preview (live editing with content)
     */
    compilePreview(options: CompilationOptions): Promise<CompilationJob | null>;
    /**
     * Compile full manuscript from workspace (no content)
     */
    compileFull(options: CompilationOptions): Promise<CompilationJob | null>;
    /**
     * @deprecated Use compilePreview() or compileFull() instead
     */
    compile(options: CompilationOptions): Promise<CompilationJob | null>;
    /**
     * Get current job status
     */
    getStatus(jobId: string): Promise<CompilationJob | null>;
    /**
     * Cancel compilation
     */
    cancel(jobId: string): Promise<boolean>;
    /**
     * Check if currently compiling
     */
    getIsCompiling(): boolean;
    /**
     * Set progress callback
     */
    onProgress(callback: (progress: number, status: string) => void): void;
    /**
     * Set completion callback
     */
    onComplete(callback: (jobId: string, pdfUrl: string) => void): void;
    /**
     * Set error callback
     */
    onError(callback: (error: string) => void): void;
    /**
     * Notify progress
     */
    private notifyProgress;
    /**
     * Notify error
     */
    private notifyError;
    /**
     * Check for existing PDF
     */
    checkExistingPDF(projectSlug: string, docType?: string): Promise<string | null>;
}
//# sourceMappingURL=compilation.d.ts.map