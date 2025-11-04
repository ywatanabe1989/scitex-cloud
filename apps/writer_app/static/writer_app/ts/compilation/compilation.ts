/**
 * Compilation Management
 * Handles PDF compilation operations and status tracking
 */

export class CompilationManager {
    private projectId: number | null;

    constructor(projectId: number | null) {
        this.projectId = projectId;
    }

    /**
     * Start a new compilation job
     */
    async compile(docType: string = 'manuscript'): Promise<void> {
        if (!this.projectId) {
            throw new Error('Project ID required for compilation');
        }

        try {
            const response = await fetch('/writer/api/compile/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    project_id: this.projectId,
                    doc_type: docType,
                }),
            });

            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.error || 'Compilation failed');
            }

            console.log('Compilation started:', result);
        } catch (error) {
            console.error('Compilation error:', error);
            throw error;
        }
    }

    /**
     * Check compilation job status
     */
    async checkStatus(jobId: string): Promise<any> {
        try {
            const response = await fetch(`/writer/api/compilation/status/?job_id=${jobId}`);
            const result = await response.json();
            
            return result.status;
        } catch (error) {
            console.error('Status check error:', error);
            throw error;
        }
    }
}
