/**
 * Issue form page functionality
 * Corresponds to: templates/project_app/issues/form.html
 */


console.log("[DEBUG] apps/project_app/static/project_app/ts/issues/form.ts loaded");

class IssueFormPage {
    private form: HTMLFormElement | null;

    constructor() {
        this.form = document.querySelector('form.issue-form');
        this.init();
    }

    private init(): void {
        console.log('[IssueForm] Initializing issue form page');
        if (this.form) {
            this.setupFormValidation();
        }
    }

    private setupFormValidation(): void {
        this.form?.addEventListener('submit', (_e) => {
            console.log('[IssueForm] Form submitted');
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new IssueFormPage();
});
