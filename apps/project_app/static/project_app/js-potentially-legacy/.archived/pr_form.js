// Pull request form functionality
(function () {
  "use strict";
  function updateComparison() {
    const baseSelect = document.getElementById("baseSelect");
    const headSelect = document.getElementById("headSelect");
    if (!baseSelect || !headSelect) {
      console.error("Base or head select element not found");
      return;
    }
    const base = baseSelect.value;
    const head = headSelect.value;
    if (base && head) {
      window.location.href = `?base=${base}&head=${head}`;
    }
  }
  // Expose function to global scope for use in HTML onchange attributes
  window.updateComparison = updateComparison;
})();
//# sourceMappingURL=pr_form.js.map
