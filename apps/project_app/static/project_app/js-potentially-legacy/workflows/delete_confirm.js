/**
 * Workflow delete confirmation page functionality
 * Corresponds to: templates/project_app/workflows/delete_confirm.html
 */
console.log("[DEBUG] apps/project_app/static/project_app/ts/workflows/delete_confirm.ts loaded");
class WorkflowDeleteConfirmPage {
    constructor() {
        this.form = document.querySelector('form.workflow-delete-form');
        this.init();
    }
    init() {
        console.log('[WorkflowDeleteConfirm] Initializing delete confirmation');
        if (this.form) {
            this.setupConfirmation();
        }
    }
    setupConfirmation() {
        this.form?.addEventListener('submit', (e) => {
            const confirmed = confirm('Are you sure you want to delete this workflow?');
            if (!confirmed) {
                e.preventDefault();
            }
        });
    }
}
document.addEventListener('DOMContentLoaded', () => {
    new WorkflowDeleteConfirmPage();
});
//# sourceMappingURL=delete_confirm.js.map