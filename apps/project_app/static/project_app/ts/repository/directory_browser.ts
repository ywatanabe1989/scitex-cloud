/**
 * Directory browser page functionality
 * Corresponds to: templates/project_app/repository/directory_browser.html
 */

console.log(
  "[DEBUG] apps/project_app/static/project_app/ts/repository/directory_browser.ts loaded",
);

class DirectoryBrowserPage {
  constructor() {
    this.init();
  }

  private init(): void {
    console.log("[DirectoryBrowser] Initializing directory browser");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new DirectoryBrowserPage();
});
