/**
 * Security policy page functionality
 * Corresponds to: templates/project_app/security/policy.html
 */

console.log(
  "[DEBUG] apps/project_app/static/project_app/ts/security/policy.ts loaded",
);

class SecurityPolicyPage {
  constructor() {
    this.init();
  }

  private init(): void {
    console.log("[SecurityPolicy] Initializing policy page");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new SecurityPolicyPage();
});
