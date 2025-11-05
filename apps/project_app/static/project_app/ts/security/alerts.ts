/**
 * Security alerts page functionality
 * Corresponds to: templates/project_app/security/alerts.html
 */


console.log("[DEBUG] apps/project_app/static/project_app/ts/security/alerts.ts loaded");

class SecurityAlertsPage {
    constructor() {
        this.init();
    }

    private init(): void {
        console.log('[SecurityAlerts] Initializing alerts page');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new SecurityAlertsPage();
});
