/**
 * Pull request form page functionality
 * Corresponds to: templates/project_app/pull_requests/form.html
 */
console.log(
  "[DEBUG] apps/project_app/static/project_app/ts/pull_requests/form.ts loaded",
);
class PullRequestFormPage {
  constructor() {
    this.form = document.querySelector("form.pr-form");
    this.init();
  }
  init() {
    console.log("[PRForm] Initializing pull request form");
    if (this.form) {
      this.setupFormHandling();
    }
  }
  setupFormHandling() {
    this.form?.addEventListener("submit", (e) => {
      console.log("[PRForm] Form submitted");
    });
  }
}
document.addEventListener("DOMContentLoaded", () => {
  new PullRequestFormPage();
});
//# sourceMappingURL=form.js.map
