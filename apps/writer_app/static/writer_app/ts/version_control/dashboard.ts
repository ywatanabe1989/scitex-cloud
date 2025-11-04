/**
 * Version Control Dashboard
 * Manages git history and version operations
 */

export class VersionControlManager {
    private projectId: number | null;

    constructor(projectId: number | null) {
        this.projectId = projectId;
    }

    /**
     * Get commit history
     */
    async getHistory(limit: number = 50): Promise<any[]> {
        if (!this.projectId) {
            return [];
        }

        try {
            const response = await fetch(
                `/writer/api/version-control/history/?project_id=${this.projectId}&limit=${limit}`
            );
            const result = await response.json();
            
            return result.history || [];
        } catch (error) {
            console.error('Error loading history:', error);
            return [];
        }
    }

    /**
     * Create a new version/commit
     */
    async createVersion(message: string): Promise<void> {
        if (!this.projectId) {
            throw new Error('Project ID required');
        }

        try {
            const response = await fetch('/writer/api/version-control/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    project_id: this.projectId,
                    message: message,
                }),
            });

            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.error || 'Failed to create version');
            }
        } catch (error) {
            console.error('Error creating version:', error);
            throw error;
        }
    }
}
