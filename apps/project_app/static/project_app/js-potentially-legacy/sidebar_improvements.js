/* =============================================================================
   SIDEBAR IMPROVEMENTS - TypeScript Updates
   Apply these changes to the <script> section in project_detail.html
   ============================================================================= */
(function () {
  "use strict";
  // localStorage keys - define them properly
  const SIDEBAR_STATE_KEY = "projectSidebarState";
  const SIDEBAR_SECTIONS_KEY = "projectSidebarSections";
  // ===========================================================================
  // 1. UPDATE: initializeSidebar() function
  // Replace the existing function with this enhanced version
  // ===========================================================================
  function initializeSidebar() {
    const sidebar = document.getElementById("repo-sidebar");
    const repoLayout = document.getElementById("repo-layout");
    const toggleBtn = document.getElementById("sidebar-toggle");
    const savedState = localStorage.getItem(SIDEBAR_STATE_KEY);
    console.log("Initializing sidebar. Saved state:", savedState);
    if (!sidebar || !repoLayout || !toggleBtn) {
      console.error("Required sidebar elements not found");
      return;
    }
    // Always start collapsed by default (per GitHub style)
    sidebar.classList.add("collapsed");
    repoLayout.classList.add("sidebar-collapsed");
    toggleBtn.setAttribute("title", "Expand sidebar"); // ADDED
    console.log("Sidebar initialized as collapsed (default)");
    // Restore section states
    const savedSections = localStorage.getItem(SIDEBAR_SECTIONS_KEY);
    if (savedSections) {
      try {
        const sections = JSON.parse(savedSections);
        Object.keys(sections).forEach((sectionId) => {
          const section = document.getElementById(sectionId);
          if (section && sections[sectionId] === "collapsed") {
            section.classList.add("section-collapsed");
          }
        });
      } catch (e) {
        console.error("Error restoring section states:", e);
      }
    }
  }
  // ===========================================================================
  // 2. UPDATE: toggleSidebar() function
  // Replace the existing function with this enhanced version
  // ===========================================================================
  function toggleSidebar() {
    const sidebar = document.getElementById("repo-sidebar");
    const repoLayout = document.getElementById("repo-layout");
    const toggleBtn = document.getElementById("sidebar-toggle");
    if (!sidebar || !repoLayout || !toggleBtn) {
      console.error("Required sidebar elements not found");
      return;
    }
    if (sidebar.classList.contains("collapsed")) {
      // Expand sidebar
      sidebar.classList.remove("collapsed");
      sidebar.classList.add("expanded");
      repoLayout.classList.remove("sidebar-collapsed");
      repoLayout.classList.add("sidebar-expanded");
      localStorage.setItem(SIDEBAR_STATE_KEY, "expanded");
      toggleBtn.setAttribute("title", "Collapse sidebar"); // ADDED
      console.log("Sidebar expanded");
    } else {
      // Collapse sidebar
      sidebar.classList.remove("expanded");
      sidebar.classList.add("collapsed");
      repoLayout.classList.remove("sidebar-expanded");
      repoLayout.classList.add("sidebar-collapsed");
      localStorage.setItem(SIDEBAR_STATE_KEY, "collapsed");
      toggleBtn.setAttribute("title", "Expand sidebar"); // ADDED
      console.log("Sidebar collapsed");
    }
  }
  async function loadProjectStats() {
    try {
      const response = await fetch(
        "/{{ project.owner.username }}/{{ project.slug }}/api/stats/",
      );
      const data = await response.json();
      if (data.success) {
        // Update counts
        const watchCount = document.getElementById("watch-count");
        const starCount = document.getElementById("star-count");
        const forkCount = document.getElementById("fork-count");
        if (watchCount) watchCount.textContent = String(data.stats.watch_count);
        if (starCount) starCount.textContent = String(data.stats.star_count);
        if (forkCount) forkCount.textContent = String(data.stats.fork_count);
        // UPDATE SIDEBAR COUNTS (ADDED SECTION)
        const sidebarStarCount = document.getElementById("sidebar-star-count");
        const sidebarForkCount = document.getElementById("sidebar-fork-count");
        if (sidebarStarCount) {
          sidebarStarCount.textContent = `${data.stats.star_count} ${data.stats.star_count === 1 ? "star" : "stars"}`;
        }
        if (sidebarForkCount) {
          sidebarForkCount.textContent = `${data.stats.fork_count} ${data.stats.fork_count === 1 ? "fork" : "forks"}`;
        }
        // Update button states
        const watchBtn = document.getElementById("watch-btn");
        const starBtn = document.getElementById("star-btn");
        if (data.user_status.is_watching && watchBtn) {
          watchBtn.classList.add("active");
        }
        if (data.user_status.is_starred && starBtn) {
          starBtn.classList.add("active");
        }
      }
    } catch (error) {
      console.error("Failed to load project stats:", error);
    }
  }
  // Expose functions to global scope for HTML onclick handlers
  window.initializeSidebar = initializeSidebar;
  window.toggleSidebar = toggleSidebar;
  window.loadProjectStats = loadProjectStats;
})();
/* =============================================================================
   END OF TYPESCRIPT IMPROVEMENTS
   ============================================================================= */
//# sourceMappingURL=sidebar.js.map
