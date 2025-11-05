/**
 * User projects page functionality
 * Corresponds to: templates/project_app/users/projects.html
 */


console.log("[DEBUG] apps/project_app/static/project_app/ts/users/projects.ts loaded");

class UserProjectsPage {
    constructor() {
        this.init();
    }

    private init(): void {
        console.log('[UserProjects] Initializing user projects');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new UserProjectsPage();
});
