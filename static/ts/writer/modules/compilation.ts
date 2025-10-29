/**
 * Writer Compilation Module
 * Handles LaTeX compilation and PDF generation
 */

import { ApiClient } from '@/utils/api';
import { CompilationJob } from '@/types';

export interface CompilationOptions {
    projectSlug: string;
    docType: string;
    content: string;
    format?: 'pdf' | 'dvi';
}

export class CompilationManager {
    private apiClient: ApiClient;
    private currentJob: CompilationJob | null = null;
    private isCompiling: boolean = false;
    private pollInterval: number = 1000; // 1 second
    private maxPollAttempts: number = 300; // 5 minutes max
    private onProgressCallback?: (progress: number, status: string) => void;
    private onCompleteCallback?: (jobId: string, pdfUrl: string) => void;
    private onErrorCallback?: (error: string) => void;

    constructor(apiBaseUrl: string = '') {
        this.apiClient = new ApiClient(apiBaseUrl);
    }

    /**
     * Compile manuscript
     */
    async compile(options: CompilationOptions): Promise<CompilationJob | null> {
        if (this.isCompiling) {
            console.warn('[Compilation] Compilation already in progress');
            return null;
        }

        this.isCompiling = true;
        this.notifyProgress(0, 'Preparing compilation...');

        try {
            const response = await this.apiClient.post<any>(
                '/writer/api/compile/',
                {
                    project_slug: options.projectSlug,
                    doc_type: options.docType,
                    content: options.content,
                    format: options.format || 'pdf'
                }
            );

            if (!response.success || !response.data?.job_id) {
                throw new Error(response.error || 'Failed to start compilation');
            }

            this.currentJob = {
                id: response.data.job_id,
                status: 'pending',
                progress: 0
            };

            this.notifyProgress(10, 'Compilation started...');

            // Poll for completion
            await this.pollCompilation(this.currentJob.id);

            return this.currentJob;
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Compilation failed';
            this.notifyError(message);
            this.currentJob = null;
            return null;
        } finally {
            this.isCompiling = false;
        }
    }

    /**
     * Poll compilation status
     */
    private async pollCompilation(jobId: string, attempts: number = 0): Promise<void> {
        if (attempts >= this.maxPollAttempts) {
            throw new Error('Compilation timeout - operation took too long');
        }

        try {
            const response = await this.apiClient.get<any>(
                `/writer/api/compilation-status/${jobId}/`
            );

            if (!response.success) {
                throw new Error(response.error || 'Failed to check compilation status');
            }

            const data = response.data;
            const status = data.status || 'unknown';
            const progress = data.progress || 0;

            if (this.currentJob) {
                this.currentJob.status = status;
                this.currentJob.progress = progress;
            }

            this.notifyProgress(Math.min(progress, 99), `Compiling... (${status})`);

            if (status === 'completed') {
                this.notifyProgress(100, 'Compilation completed');
                if (this.onCompleteCallback && data.pdf_url) {
                    this.onCompleteCallback(jobId, data.pdf_url);
                }
                return;
            }

            if (status === 'failed') {
                throw new Error(data.error || 'Compilation failed');
            }

            // Continue polling
            await this.sleep(this.pollInterval);
            await this.pollCompilation(jobId, attempts + 1);
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Polling error';
            this.notifyError(message);
            throw error;
        }
    }

    /**
     * Get current job status
     */
    async getStatus(jobId: string): Promise<CompilationJob | null> {
        try {
            const response = await this.apiClient.get<any>(
                `/writer/api/compilation-status/${jobId}/`
            );

            if (response.success && response.data) {
                return {
                    id: jobId,
                    status: response.data.status,
                    progress: response.data.progress,
                    error: response.data.error
                };
            }

            return null;
        } catch (error) {
            console.error('[Compilation] Failed to get status:', error);
            return null;
        }
    }

    /**
     * Cancel compilation
     */
    async cancel(jobId: string): Promise<boolean> {
        try {
            const response = await this.apiClient.post<any>(
                `/writer/api/cancel-compilation/${jobId}/`,
                {}
            );

            return response.success;
        } catch (error) {
            console.error('[Compilation] Failed to cancel:', error);
            return false;
        }
    }

    /**
     * Check if currently compiling
     */
    getIsCompiling(): boolean {
        return this.isCompiling;
    }

    /**
     * Set progress callback
     */
    onProgress(callback: (progress: number, status: string) => void): void {
        this.onProgressCallback = callback;
    }

    /**
     * Set completion callback
     */
    onComplete(callback: (jobId: string, pdfUrl: string) => void): void {
        this.onCompleteCallback = callback;
    }

    /**
     * Set error callback
     */
    onError(callback: (error: string) => void): void {
        this.onErrorCallback = callback;
    }

    /**
     * Notify progress
     */
    private notifyProgress(progress: number, status: string): void {
        console.log(`[Compilation] ${progress}% - ${status}`);
        if (this.onProgressCallback) {
            this.onProgressCallback(progress, status);
        }
    }

    /**
     * Notify error
     */
    private notifyError(error: string): void {
        console.error('[Compilation] Error:', error);
        if (this.onErrorCallback) {
            this.onErrorCallback(error);
        }
    }

    /**
     * Sleep utility
     */
    private sleep(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Check for existing PDF
     */
    async checkExistingPDF(projectSlug: string, docType: string = 'manuscript'): Promise<string | null> {
        try {
            const response = await this.apiClient.get<any>(
                `/writer/api/pdf/${projectSlug}/${docType}/`
            );

            if (response.success && response.data?.url) {
                return response.data.url;
            }

            return null;
        } catch (error) {
            console.error('[Compilation] Failed to check existing PDF:', error);
            return null;
        }
    }
}
