/**
 * Issue Detail Page
 * Functions for closing and reopening issues
 */
console.log(
  "[DEBUG] apps/project_app/static/project_app/ts/issues/detail.ts loaded",
);
(function () {
  "use strict";
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  async function closeIssue() {
    if (!confirm("Are you sure you want to close this issue?")) return;
    const closeUrl = document.body.dataset.issueCloseUrl;
    if (!closeUrl) {
      console.error("Issue close URL not found");
      return;
    }
    const csrfToken = getCookie("csrftoken");
    if (!csrfToken) {
      console.error("CSRF token not found");
      return;
    }
    try {
      const response = await fetch(closeUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      });
      const data = await response.json();
      if (data.success) {
        location.reload();
      } else {
        alert(data.error || "Failed to close issue");
      }
    } catch (error) {
      console.error("Error closing issue:", error);
      alert("Failed to close issue");
    }
  }
  async function reopenIssue() {
    const reopenUrl = document.body.dataset.issueReopenUrl;
    if (!reopenUrl) {
      console.error("Issue reopen URL not found");
      return;
    }
    const csrfToken = getCookie("csrftoken");
    if (!csrfToken) {
      console.error("CSRF token not found");
      return;
    }
    try {
      const response = await fetch(reopenUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      });
      const data = await response.json();
      if (data.success) {
        location.reload();
      } else {
        alert(data.error || "Failed to reopen issue");
      }
    } catch (error) {
      console.error("Error reopening issue:", error);
      alert("Failed to reopen issue");
    }
  }
  // Export functions to window
  window.closeIssue = closeIssue;
  window.reopenIssue = reopenIssue;
})();
//# sourceMappingURL=detail.js.map
