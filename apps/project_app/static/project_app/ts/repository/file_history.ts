// File history functionality

console.log("[DEBUG] apps/project_app/static/project_app/ts/repository/file_history.ts loaded");

function filterByAuthor(author: string) {
    if (author) {
        window.location.href = '?page=1&author=' + encodeURIComponent(author);
    }
    else {
        window.location.href = '?page=1';
    }
}
