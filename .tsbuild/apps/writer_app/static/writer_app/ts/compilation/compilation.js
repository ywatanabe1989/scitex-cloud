/**
 * Compilation Module - LaTeX compilation and PDF preview
 *
 * Handles compilation job submission, status tracking, and PDF preview.
 */
/**
 * Interface for compilation job response
 */
console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/compilation/compilation.ts loaded");
/**
 * Compilation handler for LaTeX documents
 */
export class CompilationHandler {
    jobId = null;
    pollInterval = null;
    /**
     * Submit a compilation job
     */
    async submitCompilation(compilationType = 'full') {
        try {
            const response = await fetch('/api/writer/compilation/submit/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({ compilation_type: compilationType }),
            });
            if (!response.ok) {
                throw new Error('Compilation submission failed');
            }
            const data = await response.json();
            this.jobId = data.job_id;
            this.startPolling();
            return data.job_id;
        }
        catch (error) {
            console.error('Compilation error:', error);
            throw error;
        }
    }
    /**
     * Check compilation status
     */
    async checkStatus(jobId) {
        try {
            const response = await fetch(`/api/writer/compilation/status/${jobId}/`);
            if (!response.ok) {
                throw new Error('Failed to fetch compilation status');
            }
            return await response.json();
        }
        catch (error) {
            console.error('Status check error:', error);
            throw error;
        }
    }
    /**
     * Start polling for job status
     */
    startPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }
        this.pollInterval = setInterval(async () => {
            if (!this.jobId)
                return;
            try {
                const status = await this.checkStatus(this.jobId);
                this.handleStatusUpdate(status);
                if (status.status === 'completed' || status.status === 'failed') {
                    this.stopPolling();
                }
            }
            catch (error) {
                console.error('Polling error:', error);
                this.stopPolling();
            }
        }, 1000); // Poll every second
    }
    /**
     * Stop polling
     */
    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }
    /**
     * Handle status updates
     */
    handleStatusUpdate(status) {
        console.log('Compilation status:', status);
        // TODO: Update UI with status
    }
    /**
     * Get CSRF token from DOM
     */
    getCSRFToken() {
        const token = document.querySelector('input[name="csrfmiddlewaretoken"]');
        return token ? token.value : '';
    }
    /**
     * Cancel ongoing polling
     */
    cancel() {
        this.stopPolling();
        this.jobId = null;
    }
}
// Initialize on document load
document.addEventListener('DOMContentLoaded', () => {
    const handler = new CompilationHandler();
    const submitButton = document.getElementById('compile-button');
    if (submitButton) {
        submitButton.addEventListener('click', async () => {
            try {
                await handler.submitCompilation('full');
            }
            catch (error) {
                console.error('Compilation failed:', error);
            }
        });
    }
});
//# sourceMappingURL=compilation.js.map