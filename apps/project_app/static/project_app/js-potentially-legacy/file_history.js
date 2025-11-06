"use strict";
// File history functionality
<<<<<<<< HEAD:.tsbuild/apps/project_app/static/project_app/ts/repository/file_history.js
console.log("[DEBUG] apps/project_app/static/project_app/ts/repository/file_history.ts loaded");
========
>>>>>>>> feat/writer-visitor-access-and-optimizations:apps/project_app/static/project_app/js-potentially-legacy/file_history.js
function filterByAuthor(author) {
    if (author) {
        window.location.href = '?page=1&author=' + encodeURIComponent(author);
    }
    else {
        window.location.href = '?page=1';
    }
}
//# sourceMappingURL=file_history.js.map