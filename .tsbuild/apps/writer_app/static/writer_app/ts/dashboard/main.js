"use strict";
/**
 * Index main page functionality
 * Corresponds to: templates/writer_app/index/main.html
 */
class IndexPage {
    constructor() {
        this.btnNewManuscript = document.getElementById('btn-new-manuscript');
        this.init();
    }
    init() {
        console.log('[Index] Initializing index page');
        this.setupEventListeners();
    }
    setupEventListeners() {
        if (this.btnNewManuscript) {
            this.btnNewManuscript.addEventListener('click', () => {
                this.createNewManuscript();
            });
        }
    }
    createNewManuscript() {
        console.log('[Index] Creating new manuscript');
        window.location.href = '/writer/editor/';
    }
}
document.addEventListener('DOMContentLoaded', () => {
    new IndexPage();
});
//# sourceMappingURL=main.js.map