/**
 * Compilation Module - LaTeX compilation and PDF preview
 *
 * Handles compilation job submission, status tracking, and PDF preview.
 */
export interface CompilationJob {
    job_id: string;
    status: 'queued' | 'running' | 'completed' | 'failed';
    output_pdf?: string;
    error_message?: string;
    compilation_time?: number;
}
/**
 * Compilation handler for LaTeX documents
 */
export declare class CompilationHandler {
    private jobId;
    private pollInterval;
    /**
     * Submit a compilation job
     */
    submitCompilation(compilationType?: string): Promise<string>;
    /**
     * Check compilation status
     */
    checkStatus(jobId: string): Promise<CompilationJob>;
    /**
     * Start polling for job status
     */
    private startPolling;
    /**
     * Stop polling
     */
    private stopPolling;
    /**
     * Handle status updates
     */
    private handleStatusUpdate;
    /**
     * Get CSRF token from DOM
     */
    private getCSRFToken;
    /**
     * Cancel ongoing polling
     */
    cancel(): void;
}
//# sourceMappingURL=compilation.d.ts.map