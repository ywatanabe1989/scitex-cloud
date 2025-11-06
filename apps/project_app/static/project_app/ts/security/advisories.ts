/**
 * Security advisories page functionality
 * Corresponds to: templates/project_app/security/advisories.html
 */


console.log("[DEBUG] apps/project_app/static/project_app/ts/security/advisories.ts loaded");

class SecurityAdvisoriesPage {
    constructor() {
        this.init();
    }

    private init(): void {
        console.log('[SecurityAdvisories] Initializing advisories page');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new SecurityAdvisoriesPage();
});
