/**
 * Writer Compilation Module
 * Handles LaTeX compilation and PDF generation
 */
import { ApiClient } from '@/utils/api';
export class CompilationManager {
    constructor(apiBaseUrl = '') {
        this.currentJob = null;
        this.isCompiling = false;
        this.pollInterval = 1000; // 1 second
        this.maxPollAttempts = 300; // 5 minutes max
        this.apiClient = new ApiClient(apiBaseUrl);
    }
    /**
     * Compile manuscript
     */
    async compile(options) {
        if (this.isCompiling) {
            console.warn('[Compilation] Compilation already in progress');
            return null;
        }
        this.isCompiling = true;
        this.notifyProgress(0, 'Preparing compilation...');
        try {
            const response = await this.apiClient.post('/writer/api/compile/', {
                project_slug: options.projectSlug,
                doc_type: options.docType,
                content: options.content,
                format: options.format || 'pdf'
            });
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
        }
        catch (error) {
            const message = error instanceof Error ? error.message : 'Compilation failed';
            this.notifyError(message);
            this.currentJob = null;
            return null;
        }
        finally {
            this.isCompiling = false;
        }
    }
    /**
     * Poll compilation status
     */
    async pollCompilation(jobId, attempts = 0) {
        if (attempts >= this.maxPollAttempts) {
            throw new Error('Compilation timeout - operation took too long');
        }
        try {
            const response = await this.apiClient.get(`/writer/api/compilation-status/${jobId}/`);
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
        }
        catch (error) {
            const message = error instanceof Error ? error.message : 'Polling error';
            this.notifyError(message);
            throw error;
        }
    }
    /**
     * Get current job status
     */
    async getStatus(jobId) {
        try {
            const response = await this.apiClient.get(`/writer/api/compilation-status/${jobId}/`);
            if (response.success && response.data) {
                return {
                    id: jobId,
                    status: response.data.status,
                    progress: response.data.progress,
                    error: response.data.error
                };
            }
            return null;
        }
        catch (error) {
            console.error('[Compilation] Failed to get status:', error);
            return null;
        }
    }
    /**
     * Cancel compilation
     */
    async cancel(jobId) {
        try {
            const response = await this.apiClient.post(`/writer/api/cancel-compilation/${jobId}/`, {});
            return response.success;
        }
        catch (error) {
            console.error('[Compilation] Failed to cancel:', error);
            return false;
        }
    }
    /**
     * Check if currently compiling
     */
    getIsCompiling() {
        return this.isCompiling;
    }
    /**
     * Set progress callback
     */
    onProgress(callback) {
        this.onProgressCallback = callback;
    }
    /**
     * Set completion callback
     */
    onComplete(callback) {
        this.onCompleteCallback = callback;
    }
    /**
     * Set error callback
     */
    onError(callback) {
        this.onErrorCallback = callback;
    }
    /**
     * Notify progress
     */
    notifyProgress(progress, status) {
        console.log(`[Compilation] ${progress}% - ${status}`);
        if (this.onProgressCallback) {
            this.onProgressCallback(progress, status);
        }
    }
    /**
     * Notify error
     */
    notifyError(error) {
        console.error('[Compilation] Error:', error);
        if (this.onErrorCallback) {
            this.onErrorCallback(error);
        }
    }
    /**
     * Sleep utility
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    /**
     * Check for existing PDF
     */
    async checkExistingPDF(projectSlug, docType = 'manuscript') {
        try {
            const response = await this.apiClient.get(`/writer/api/pdf/${projectSlug}/${docType}/`);
            if (response.success && response.data?.url) {
                return response.data.url;
            }
            return null;
        }
        catch (error) {
            console.error('[Compilation] Failed to check existing PDF:', error);
            return null;
        }
    }
}
//# sourceMappingURL=compilation.js.map