"use strict";
/**
 * ArXiv submission page functionality
 * Corresponds to: templates/writer_app/arxiv/submission.html
 */
console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/arxiv/submission.ts loaded");
class ArxivSubmissionPage {
    form;
    constructor() {
        this.form = document.querySelector('form#arxiv-submission-form');
        this.init();
    }
    init() {
        console.log('[ArxivSubmission] Initializing arXiv submission page');
        this.setupFormValidation();
    }
    setupFormValidation() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitToArxiv();
            });
        }
    }
    async submitToArxiv() {
        console.log('[ArxivSubmission] Submitting to arXiv');
    }
}
document.addEventListener('DOMContentLoaded', () => {
    new ArxivSubmissionPage();
});
//# sourceMappingURL=submission.js.map