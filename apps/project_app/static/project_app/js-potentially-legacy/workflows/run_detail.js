// Workflow run detail page functionality
console.log(
  "[DEBUG] apps/project_app/static/project_app/ts/workflows/run_detail.ts loaded",
);
(function () {
  "use strict";
  function toggleJob(jobId) {
    console.log("Toggling job:", jobId);
    const stepsDiv = document.getElementById(`job-${jobId}-steps`);
    const chevron = document.getElementById(`job-${jobId}-chevron`);
    if (!stepsDiv || !chevron) {
      console.error("Job elements not found:", jobId);
      return;
    }
    stepsDiv.classList.toggle("show");
    if (stepsDiv.classList.contains("show")) {
      chevron.classList.remove("bi-chevron-down");
      chevron.classList.add("bi-chevron-up");
    } else {
      chevron.classList.remove("bi-chevron-up");
      chevron.classList.add("bi-chevron-down");
    }
  }
  function toggleStep(stepId) {
    console.log("Toggling step:", stepId);
    const outputDiv = document.getElementById(`step-${stepId}-output`);
    const chevron = document.getElementById(`step-${stepId}-chevron`);
    if (!outputDiv || !chevron) {
      console.error("Step elements not found:", stepId);
      return;
    }
    outputDiv.classList.toggle("show");
    if (outputDiv.classList.contains("show")) {
      chevron.classList.remove("bi-chevron-down");
      chevron.classList.add("bi-chevron-up");
    } else {
      chevron.classList.remove("bi-chevron-up");
      chevron.classList.add("bi-chevron-down");
    }
  }
  // Auto-refresh for in-progress runs
  document.addEventListener("DOMContentLoaded", function () {
    const container = document.querySelector(".container-fluid");
    if (container && container.dataset.runStatus === "in_progress") {
      console.log("Run in progress, auto-refresh enabled");
      setTimeout(function () {
        location.reload();
      }, 5000); // Refresh every 5 seconds
    }
  });
  // Expose functions to global scope
  window.toggleJob = toggleJob;
  window.toggleStep = toggleStep;
})();
//# sourceMappingURL=run_detail.js.map
