/**
 * User overview page functionality
 * Corresponds to: templates/project_app/users/overview.html
 */


console.log("[DEBUG] apps/project_app/static/project_app/ts/users/overview.ts loaded");

class UserOverviewPage {
    constructor() {
        this.init();
    }

    private init(): void {
        console.log('[UserOverview] Initializing user overview');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new UserOverviewPage();
});
