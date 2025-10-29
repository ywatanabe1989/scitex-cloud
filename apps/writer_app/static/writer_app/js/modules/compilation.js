/**
 * Writer Compilation Module
 * Handles LaTeX compilation and PDF generation
 */
import { ApiClient } from '@/utils/api';
import { getCsrfToken } from '@/utils/csrf';
export class CompilationManager {
    constructor(apiBaseUrl = '') {
        this.currentJob = null;
        this.isCompiling = false;
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
            // Add timeout to prevent indefinite waiting (60 seconds for dev)
            const timeoutMs = 60000; // 60 seconds timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
            const response = await fetch(`/writer/api/project/${options.projectId}/compile/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    doc_type: options.docType,
                    content: options.content,
                    format: options.format || 'pdf'
                }),
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const compilationResult = await response.json();
            console.log('[Compilation] Response data:', compilationResult);
            console.log('[Compilation] Response success:', compilationResult?.success);
            console.log('[Compilation] Response output_pdf:', compilationResult?.output_pdf);
            console.log('[Compilation] Response error:', compilationResult?.error);
            this.notifyProgress(50, 'Compiling...');
            if (compilationResult?.success === true) {
                this.notifyProgress(100, 'Compilation completed');
                this.currentJob = {
                    id: 'local',
                    status: 'completed',
                    progress: 100
                };
                // Get PDF path (could be output_pdf or pdf_path)
                const pdfPath = compilationResult.output_pdf || compilationResult.pdf_path;
                console.log('[Compilation] PDF path:', pdfPath);
                // Notify completion
                if (this.onCompleteCallback && pdfPath) {
                    this.onCompleteCallback('local', pdfPath);
                }
                else if (!pdfPath) {
                    console.warn('[Compilation] Compilation successful but no PDF path provided');
                }
                return this.currentJob;
            }
            else {
                // Detailed error message
                const errorMsg = compilationResult?.error || compilationResult?.log || 'Compilation failed';
                console.error('[Compilation] Compilation result:', compilationResult);
                throw new Error(errorMsg);
            }
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
     * Get current job status
     */
    async getStatus(jobId) {
        try {
            if (jobId === 'local') {
                // Local synchronous job
                return this.currentJob;
            }
            // This would be for async job polling (not currently used)
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