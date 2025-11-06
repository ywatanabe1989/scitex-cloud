/**
 * File directory page functionality
 * Corresponds to: templates/project_app/repository/file_directory.html
 */


console.log("[DEBUG] apps/project_app/static/project_app/ts/repository/file_directory.ts loaded");

class FileDirectoryPage {
    constructor() {
        this.init();
    }

    private init(): void {
        console.log('[FileDirectory] Initializing file directory');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new FileDirectoryPage();
});
