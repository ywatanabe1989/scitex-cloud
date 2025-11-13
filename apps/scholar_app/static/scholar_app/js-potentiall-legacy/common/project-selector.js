// Project Selector Handler
document.addEventListener("DOMContentLoaded", function () {
  const projectSelector = document.getElementById("project-selector");
  if (projectSelector) {
    // Store selected project in sessionStorage for use by save functions
    projectSelector.addEventListener("change", function () {
      if (this.value) {
        sessionStorage.setItem("scholar_selected_project_id", this.value);
        console.log("[Scholar] Selected project ID:", this.value);
      } else {
        sessionStorage.removeItem("scholar_selected_project_id");
        console.log("[Scholar] Cleared project selection");
      }
    });

    // Initialize from sessionStorage on page load
    const savedProjectId = sessionStorage.getItem(
      "scholar_selected_project_id",
    );
    if (savedProjectId) {
      projectSelector.value = savedProjectId;
    }
  }
});
