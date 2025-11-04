/**
 * Writer Dashboard
 * Manages manuscript list and user activity
 */

export class DashboardManager {
    constructor() {
        this.init();
    }

    private init(): void {
        console.log('Dashboard initialized');
        this.setupEventListeners();
    }

    private setupEventListeners(): void {
        // New manuscript button
        const newManuscriptBtn = document.getElementById('btn-new-manuscript');
        if (newManuscriptBtn) {
            newManuscriptBtn.addEventListener('click', () => {
                this.createNewManuscript();
            });
        }
    }

    private async createNewManuscript(): Promise<void> {
        // TODO: Implement manuscript creation
        console.log('Creating new manuscript...');
    }

    /**
     * Load user's manuscripts
     */
    async loadManuscripts(): Promise<any[]> {
        try {
            const response = await fetch('/writer/api/manuscripts/');
            const result = await response.json();
            
            return result.manuscripts || [];
        } catch (error) {
            console.error('Error loading manuscripts:', error);
            return [];
        }
    }
}

// Initialize dashboard when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new DashboardManager();
    });
} else {
    new DashboardManager();
}
