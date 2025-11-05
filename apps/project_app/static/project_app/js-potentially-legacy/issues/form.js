/**
 * Issue form page functionality
 * Corresponds to: templates/project_app/issues/form.html
 */
console.log("[DEBUG] apps/project_app/static/project_app/ts/issues/form.ts loaded");
class IssueFormPage {
    constructor() {
        this.form = document.querySelector('form.issue-form');
        this.init();
    }
    init() {
        console.log('[IssueForm] Initializing issue form page');
        if (this.form) {
            this.setupFormValidation();
        }
    }
    setupFormValidation() {
        this.form?.addEventListener('submit', (e) => {
            console.log('[IssueForm] Form submitted');
        });
    }
}
document.addEventListener('DOMContentLoaded', () => {
    new IssueFormPage();
});
//# sourceMappingURL=form.js.map