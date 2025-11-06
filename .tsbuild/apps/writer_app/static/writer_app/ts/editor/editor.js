"use strict";
/**
 * Editor main page functionality
 * Corresponds to: templates/writer_app/editor/editor.html
 */
console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/editor/editor.ts loaded");
class EditorPage {
    // @ts-expect-error - Placeholder for future editor integration
    _editor;
    // @ts-expect-error - Placeholder for future PDF preview
    _pdfPreview;
    constructor() {
        this._pdfPreview = document.getElementById('pdf-preview');
        this.init();
    }
    init() {
        console.log('[Editor] Initializing editor page');
        this.setupEditor();
    }
    setupEditor() {
        console.log('[Editor] Setting up Monaco editor');
    }
    compile() {
        console.log('[Editor] Starting compilation');
    }
}
document.addEventListener('DOMContentLoaded', () => {
    new EditorPage();
});
//# sourceMappingURL=editor.js.map