// =============================================================================
// User Profile Functions
// =============================================================================
(function () {
  "use strict";
  // =============================================================================
  // Helper Functions
  // =============================================================================
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
  // =============================================================================
  // Repository Search
  // =============================================================================
  const repoSearchInput = document.getElementById("repo-search");
  if (repoSearchInput) {
    repoSearchInput.addEventListener("input", function (e) {
      const target = e.target;
      const searchTerm = target.value.toLowerCase();
      const repoItems = document.querySelectorAll(".repo-item");
      repoItems.forEach((item) => {
        const htmlItem = item;
        const repoNameElement = item.querySelector(".repo-name");
        const repoDescElement = item.querySelector(".repo-description");
        if (!repoNameElement) return;
        const repoName = (repoNameElement.textContent || "").toLowerCase();
        const repoDesc = (repoDescElement?.textContent || "").toLowerCase();
        if (repoName.includes(searchTerm) || repoDesc.includes(searchTerm)) {
          htmlItem.style.display = "";
        } else {
          htmlItem.style.display = "none";
        }
      });
    });
  }
  // =============================================================================
  // Follow/Unfollow Functionality
  // =============================================================================
  async function toggleFollow() {
    const btn = document.getElementById("follow-btn");
    if (!btn) {
      console.error("Follow button not found");
      return;
    }
    const isFollowing = btn.innerHTML.includes("Following");
    const profileData = window.SCITEX_PROFILE_DATA;
    if (!profileData || !profileData.username) {
      console.error("Profile data not available");
      return;
    }
    const username = profileData.username;
    const endpoint = isFollowing
      ? `/social/api/unfollow/${username}/`
      : `/social/api/follow/${username}/`;
    try {
      const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
      const csrfToken = csrfInput?.value || getCookie("csrftoken");
      if (!csrfToken) {
        console.error("CSRF token not found");
        return;
      }
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/json",
        },
      });
      const data = await response.json();
      if (data.success) {
        // Toggle button state
        if (isFollowing) {
          btn.innerHTML = '<i class="fas fa-user-plus"></i> Follow';
        } else {
          btn.innerHTML = '<i class="fas fa-user-check"></i> Following';
        }
        // Update follower count
        const followerCountElement = document.querySelector(
          ".profile-stat strong",
        );
        if (followerCountElement && data.followers_count !== undefined) {
          followerCountElement.textContent = String(data.followers_count);
        }
      } else {
        alert(data.error || "Failed to update follow status");
      }
    } catch (err) {
      console.error("Follow error:", err);
      alert("Failed to update follow status");
    }
  }
  // =============================================================================
  // Star/Unstar Repository Functionality
  // =============================================================================
  async function toggleStar(btn) {
    if (!btn) {
      console.error("Star button not provided");
      return;
    }
    const isStarred = btn.innerHTML.includes("Unstar");
    const username = btn.dataset.username;
    const slug = btn.dataset.slug;
    if (!username || !slug) {
      console.error("Username or slug not found in button dataset");
      return;
    }
    const endpoint = isStarred
      ? `/social/api/unstar/${username}/${slug}/`
      : `/social/api/star/${username}/${slug}/`;
    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = "⏳ ...";
    try {
      const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
      const csrfToken = csrfInput?.value || getCookie("csrftoken");
      if (!csrfToken) {
        console.error("CSRF token not found");
        btn.innerHTML = originalHTML;
        btn.disabled = false;
        return;
      }
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/json",
        },
      });
      const data = await response.json();
      if (data.success) {
        // Get the static URL for star icon
        const starIconUrl =
          btn.dataset.starIcon || "/static/project_app/icons/star.svg";
        // Toggle button state
        if (isStarred) {
          btn.innerHTML = `<img src="${starIconUrl}" alt="" style="width: 14px; height: 14px; vertical-align: text-bottom; margin-right: 4px;">Star`;
        } else {
          btn.innerHTML = `<img src="${starIconUrl}" alt="" style="width: 14px; height: 14px; vertical-align: text-bottom; margin-right: 4px;">Unstar`;
        }
      } else {
        alert(data.error || "Failed to update star status");
        btn.innerHTML = originalHTML;
      }
    } catch (err) {
      console.error("Star error:", err);
      alert("Failed to update star status");
      btn.innerHTML = originalHTML;
    } finally {
      btn.disabled = false;
    }
  }
  // Expose functions to global scope for use in HTML onclick attributes
  window.toggleFollow = toggleFollow;
  window.toggleStar = toggleStar;
})();
//# sourceMappingURL=profile.js.map
