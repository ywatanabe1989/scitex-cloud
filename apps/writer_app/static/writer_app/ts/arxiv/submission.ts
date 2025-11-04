/**
 * arXiv Submission Management
 * Handles manuscript submission to arXiv.org
 */

export class ArxivSubmissionManager {
    private projectId: number | null;

    constructor(projectId: number | null) {
        this.projectId = projectId;
    }

    /**
     * Submit manuscript to arXiv
     */
    async submit(data: any): Promise<void> {
        if (!this.projectId) {
            throw new Error('Project ID required for submission');
        }

        try {
            const response = await fetch('/writer/api/arxiv/submit/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    project_id: this.projectId,
                    ...data,
                }),
            });

            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.error || 'Submission failed');
            }

            console.log('Submitted to arXiv:', result);
        } catch (error) {
            console.error('Submission error:', error);
            throw error;
        }
    }

    /**
     * Validate manuscript before submission
     */
    async validate(): Promise<any> {
        if (!this.projectId) {
            throw new Error('Project ID required for validation');
        }

        try {
            const response = await fetch('/writer/api/arxiv/validate/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    project_id: this.projectId,
                }),
            });

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Validation error:', error);
            throw error;
        }
    }
}
