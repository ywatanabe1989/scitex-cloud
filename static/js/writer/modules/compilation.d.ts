/**
 * Writer Compilation Module
 * Handles LaTeX compilation and PDF generation
 */
import { CompilationJob } from '@/types';
export interface CompilationOptions {
    projectSlug: string;
    docType: string;
    content: string;
    format?: 'pdf' | 'dvi';
}
export declare class CompilationManager {
    private apiClient;
    private currentJob;
    private isCompiling;
    private pollInterval;
    private maxPollAttempts;
    private onProgressCallback?;
    private onCompleteCallback?;
    private onErrorCallback?;
    constructor(apiBaseUrl?: string);
    /**
     * Compile manuscript
     */
    compile(options: CompilationOptions): Promise<CompilationJob | null>;
    /**
     * Poll compilation status
     */
    private pollCompilation;
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
     * Sleep utility
     */
    private sleep;
    /**
     * Check for existing PDF
     */
    checkExistingPDF(projectSlug: string, docType?: string): Promise<string | null>;
}
//# sourceMappingURL=compilation.d.ts.map