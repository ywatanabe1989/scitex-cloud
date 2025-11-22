/**
 * Security dependency graph page functionality
 * Corresponds to: templates/project_app/security/dependency_graph.html
 */

console.log(
  "[DEBUG] apps/project_app/static/project_app/ts/security/dependency_graph.ts loaded",
);

class SecurityDependencyGraphPage {
  constructor() {
    this.init();
  }

  private init(): void {
    console.log("[SecurityDependencyGraph] Initializing dependency graph");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new SecurityDependencyGraphPage();
});
