// File editor functionality
console.log("[DEBUG] apps/project_app/static/project_app/ts/repository/file_edit.ts loaded");
(function () {
    'use strict';
    function showEdit() {
        const editorTextarea = document.getElementById('editorTextarea');
        const previewContainer = document.getElementById('previewContainer');
        const editBtn = document.getElementById('editBtn');
        const previewBtn = document.getElementById('previewBtn');
        if (editorTextarea && previewContainer && editBtn && previewBtn) {
            editorTextarea.style.display = 'block';
            previewContainer.style.display = 'none';
            editBtn.classList.add('active');
            previewBtn.classList.remove('active');
        }
    }
    function showPreview() {
        const editorTextarea = document.getElementById('editorTextarea');
        const previewContainer = document.getElementById('previewContainer');
        const editBtn = document.getElementById('editBtn');
        const previewBtn = document.getElementById('previewBtn');
        if (editorTextarea && previewContainer && editBtn && previewBtn) {
            const content = editorTextarea.value;
            // Access marked library from window object (defined in global.d.ts)
            if (window.marked && typeof window.marked.parse === 'function') {
                const html = window.marked.parse(content);
                previewContainer.innerHTML = html;
            }
            else {
                console.error('marked library not found');
                previewContainer.innerHTML = '<p>Error: Markdown parser not available</p>';
            }
            editorTextarea.style.display = 'none';
            previewContainer.style.display = 'block';
            editBtn.classList.remove('active');
            previewBtn.classList.add('active');
        }
    }
    // Expose functions to window object for HTML onclick handlers
    window.showEdit = showEdit;
    window.showPreview = showPreview;
})();
//# sourceMappingURL=file_edit.js.map