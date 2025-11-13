// =============================================================================
// Sidebar State Management
// =============================================================================
(function () {
  "use strict";
  const SIDEBAR_STATE_KEY = "scitex-sidebar-state";
  const SIDEBAR_SECTIONS_KEY = "scitex-sidebar-sections";
  // Initialize sidebar state from localStorage
  function initializeSidebar() {
    const sidebar = document.getElementById("repo-sidebar");
    const repoLayout = document.getElementById("repo-layout");
    const toggleBtn = document.getElementById("sidebar-toggle");
    const savedState = localStorage.getItem(SIDEBAR_STATE_KEY);
    console.log("Initializing sidebar. Saved state:", savedState);
    // Check if sidebar element exists before trying to manipulate it
    if (!sidebar) {
      console.log(
        "Sidebar element not found on this page, skipping sidebar initialization",
      );
      return;
    }
    // Start collapsed by default, but respect localStorage if user explicitly expanded it
    if (savedState === "expanded") {
      sidebar.classList.remove("collapsed");
      sidebar.classList.add("expanded");
      if (repoLayout) {
        repoLayout.classList.remove("sidebar-collapsed");
        repoLayout.classList.add("sidebar-expanded");
      }
      if (toggleBtn) {
        toggleBtn.setAttribute("title", "Collapse sidebar");
      }
      console.log("Sidebar initialized as expanded (from localStorage)");
    } else {
      sidebar.classList.add("collapsed");
      if (repoLayout) {
        repoLayout.classList.add("sidebar-collapsed");
      }
      if (toggleBtn) {
        toggleBtn.setAttribute("title", "Expand sidebar");
      }
      console.log("Sidebar initialized as collapsed (default)");
    }
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
  // Toggle entire sidebar
  function toggleSidebar() {
    const sidebar = document.getElementById("repo-sidebar");
    const repoLayout = document.getElementById("repo-layout");
    const toggleBtn = document.getElementById("sidebar-toggle");
    if (!sidebar) return;
    if (sidebar.classList.contains("collapsed")) {
      // Expand sidebar
      sidebar.classList.remove("collapsed");
      sidebar.classList.add("expanded");
      if (repoLayout) {
        repoLayout.classList.remove("sidebar-collapsed");
        repoLayout.classList.add("sidebar-expanded");
      }
      localStorage.setItem(SIDEBAR_STATE_KEY, "expanded");
      if (toggleBtn) {
        toggleBtn.setAttribute("title", "Collapse sidebar");
      }
      console.log("Sidebar expanded");
    } else {
      // Collapse sidebar
      sidebar.classList.remove("expanded");
      sidebar.classList.add("collapsed");
      if (repoLayout) {
        repoLayout.classList.remove("sidebar-expanded");
        repoLayout.classList.add("sidebar-collapsed");
      }
      localStorage.setItem(SIDEBAR_STATE_KEY, "collapsed");
      if (toggleBtn) {
        toggleBtn.setAttribute("title", "Expand sidebar");
      }
      console.log("Sidebar collapsed");
    }
  }
  // Toggle individual sidebar section
  function toggleSidebarSection(sectionId) {
    const sidebar = document.getElementById("repo-sidebar");
    // Don't toggle sections when sidebar is collapsed
    if (!sidebar || sidebar.classList.contains("collapsed")) {
      return;
    }
    const section = document.getElementById(sectionId);
    if (!section) return;
    section.classList.toggle("section-collapsed");
    // Save section states
    saveSectionStates();
  }
  // Save all section states to localStorage
  function saveSectionStates() {
    const fileTreeSection = document.getElementById("file-tree-section");
    const aboutSection = document.getElementById("about-section");
    const sections = {};
    if (fileTreeSection) {
      sections["file-tree-section"] = fileTreeSection.classList.contains(
        "section-collapsed",
      )
        ? "collapsed"
        : "expanded";
    }
    if (aboutSection) {
      sections["about-section"] = aboutSection.classList.contains(
        "section-collapsed",
      )
        ? "collapsed"
        : "expanded";
    }
    localStorage.setItem(SIDEBAR_SECTIONS_KEY, JSON.stringify(sections));
  }
  // =============================================================================
  // File Tree
  // =============================================================================
  // Build file tree for sidebar
  async function loadFileTree() {
    const projectData = window.SCITEX_PROJECT_DATA;
    if (!projectData) {
      console.error("Project data not available");
      return;
    }
    try {
      const response = await fetch(
        `/${projectData.owner}/${projectData.slug}/api/file-tree/`,
      );
      const data = await response.json();
      if (data.success) {
        const treeContainer = document.getElementById("file-tree");
        if (treeContainer) {
          treeContainer.innerHTML = buildTreeHTML(
            data.tree,
            projectData.owner,
            projectData.slug,
          );
        }
      } else {
        const treeContainer = document.getElementById("file-tree");
        if (treeContainer) {
          treeContainer.innerHTML =
            '<div style="color: var(--color-fg-muted); padding: 0.5rem;">Error loading file tree</div>';
        }
      }
    } catch (err) {
      console.error("Failed to load file tree:", err);
      const treeContainer = document.getElementById("file-tree");
      if (treeContainer) {
        treeContainer.innerHTML =
          '<div style="color: var(--color-fg-muted); padding: 0.5rem;">Error loading file tree</div>';
      }
    }
  }
  function buildTreeHTML(items, username, slug, level = 0) {
    let html = "";
    const indent = level * 16;
    const currentPath = window.location.pathname;
    items.forEach((item, index) => {
      const itemPath = `/${username}/${slug}/${item.path}${item.type === "directory" ? "/" : ""}`;
      const isActive = currentPath.includes(item.path);
      const icon =
        item.type === "directory"
          ? '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" class="icon-folder"><path fill="currentColor" d="M1.75 1A1.75 1.75 0 0 0 0 2.75v10.5C0 14.216.784 15 1.75 15h12.5A1.75 1.75 0 0 0 16 13.25v-8.5A1.75 1.75 0 0 0 14.25 3H7.5a.25.25 0 0 1-.2-.1l-.9-1.2C6.07 1.26 5.55 1 5 1H1.75Z"></path></svg>'
          : '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" class="icon-file"><path fill="currentColor" d="M2 1.75C2 .784 2.784 0 3.75 0h6.586c.464 0 .909.184 1.237.513l2.914 2.914c.329.328.513.773.513 1.237v9.586A1.75 1.75 0 0 1 13.25 16h-9.5A1.75 1.75 0 0 1 2 14.25Zm1.75-.25a.25.25 0 0 0-.25.25v12.5c0 .138.112.25.25.25h9.5a.25.25 0 0 0 .25-.25V6h-2.75A1.75 1.75 0 0 1 9 4.25V1.5Zm6.75.062V4.25c0 .138.112.25.25.25h2.688l-.011-.013-2.914-2.914-.013-.011Z"></path></svg>';
      const hasChildren = item.children && item.children.length > 0;
      const itemId = `tree-${item.path.replace(/\//g, "-")}`; // Unique ID based on path
      // Item row
      html += `<div class="file-tree-item ${isActive ? "active" : ""}" style="padding-left: ${indent}px;">`;
      if (item.type === "directory") {
        html += `<a href="${itemPath}" class="file-tree-folder" style="text-decoration: none; color: var(--color-fg-default);">`;
        // Chevron for folders with children
        if (hasChildren) {
          html += `<span class="file-tree-chevron ${level === 0 ? "expanded" : ""}" onclick="toggleFolder('${itemId}'); return false;">▸</span>`;
        } else {
          html += `<span style="width: 12px; display: inline-block;"></span>`;
        }
        html += `<span class="file-tree-icon">${icon}</span><span>${item.name}</span>`;
        html += `</a>`;
      } else {
        html += `<a href="/${username}/${slug}/blob/${item.path}" class="file-tree-file" style="text-decoration: none; color: var(--color-fg-muted);">`;
        html += `<span style="width: 12px; display: inline-block;"></span>`;
        html += `<span class="file-tree-icon">${icon}</span><span>${item.name}</span>`;
        html += `</a>`;
      }
      html += `</div>`;
      // Children container - render ALL children
      if (hasChildren) {
        const isExpanded = level === 0; // Auto-expand root level only
        html += `<div id="${itemId}" class="file-tree-children ${isExpanded ? "expanded" : ""}">`;
        html += buildTreeHTML(item.children, username, slug, level + 1); // Recursively build all children
        html += `</div>`;
      }
    });
    return html;
  }
  function toggleFolder(folderId, event) {
    const folder = document.getElementById(folderId);
    if (!folder) return;
    // Find the chevron element - it's the span with class 'file-tree-chevron'
    const chevron = event
      ? event.target
      : document
          .querySelector(`#${folderId}`)
          ?.previousElementSibling?.querySelector(".file-tree-chevron");
    if (folder.classList.contains("expanded")) {
      folder.classList.remove("expanded");
      if (chevron) chevron.classList.remove("expanded");
    } else {
      folder.classList.add("expanded");
      if (chevron) chevron.classList.add("expanded");
    }
    if (event) {
      event.stopPropagation();
      event.preventDefault();
    }
  }
  // =============================================================================
  // Project Concatenation
  // =============================================================================
  async function copyProjectToClipboard(event) {
    const projectData = window.SCITEX_PROJECT_DATA;
    if (!projectData) return;
    const btn = event.currentTarget;
    const originalText = btn.innerHTML;
    btn.innerHTML = "⏳ Loading...";
    btn.disabled = true;
    try {
      const response = await fetch(
        `/${projectData.owner}/${projectData.slug}/api/concatenate/`,
      );
      const data = await response.json();
      if (data.success) {
        await navigator.clipboard.writeText(data.content);
        const checkIcon =
          '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" class="octicon octicon-16" style="vertical-align: text-bottom; margin-right: 4px;"><path fill="currentColor" d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"></path></svg>';
        btn.innerHTML = `${checkIcon} Copied ${data.file_count} files!`;
        setTimeout(() => {
          btn.innerHTML = originalText;
          btn.disabled = false;
        }, 3000);
      } else {
        alert("Error: " + data.error);
        btn.innerHTML = originalText;
        btn.disabled = false;
      }
    } catch (err) {
      alert("Failed to copy: " + err);
      btn.innerHTML = originalText;
      btn.disabled = false;
    }
  }
  async function downloadProjectAsFile(event) {
    const projectData = window.SCITEX_PROJECT_DATA;
    if (!projectData) return;
    const btn = event.currentTarget;
    const originalText = btn.innerHTML;
    btn.innerHTML = "⏳ Preparing download...";
    btn.disabled = true;
    try {
      const response = await fetch(
        `/${projectData.owner}/${projectData.slug}/api/concatenate/`,
      );
      const data = await response.json();
      if (data.success) {
        // Create a blob and download it
        const blob = new Blob([data.content], { type: "text/plain" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${projectData.slug}_all_files.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        const checkIcon =
          '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" class="octicon octicon-16" style="vertical-align: text-bottom; margin-right: 4px;"><path fill="currentColor" d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"></path></svg>';
        btn.innerHTML = `${checkIcon} Downloaded ${data.file_count} files!`;
        setTimeout(() => {
          btn.innerHTML = originalText;
          btn.disabled = false;
        }, 3000);
      } else {
        alert("Error: " + data.error);
        btn.innerHTML = originalText;
        btn.disabled = false;
      }
    } catch (err) {
      alert("Failed to download: " + err);
      btn.innerHTML = originalText;
      btn.disabled = false;
    }
  }
  // =============================================================================
  // Watch/Star/Fork Action Handlers
  // =============================================================================
  async function loadProjectStats() {
    const projectData = window.SCITEX_PROJECT_DATA;
    if (!projectData) return;
    try {
      const response = await fetch(
        `/${projectData.owner}/${projectData.slug}/api/stats/`,
      );
      const data = await response.json();
      if (data.success) {
        // Update counts
        const watchCount = document.getElementById("watch-count");
        const starCount = document.getElementById("star-count");
        const forkCount = document.getElementById("fork-count");
        if (watchCount) watchCount.textContent = data.stats.watch_count;
        if (starCount) starCount.textContent = data.stats.star_count;
        if (forkCount) forkCount.textContent = data.stats.fork_count;
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
  async function handleWatch(event) {
    const projectData = window.SCITEX_PROJECT_DATA;
    if (!projectData) return;
    const btn = event.currentTarget;
    const isWatching = btn.classList.contains("active");
    try {
      const response = await fetch(
        `/${projectData.owner}/${projectData.slug}/api/watch/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
        },
      );
      const data = await response.json();
      if (data.success) {
        // Toggle active state
        if (data.is_watching) {
          btn.classList.add("active");
        } else {
          btn.classList.remove("active");
        }
        // Update count
        const watchCount = document.getElementById("watch-count");
        if (watchCount) watchCount.textContent = data.watch_count;
        // Show notification
        showNotification(data.message, "success");
      } else {
        showNotification(
          data.error || "Failed to update watch status",
          "error",
        );
      }
    } catch (error) {
      console.error("Error toggling watch:", error);
      showNotification("Failed to update watch status", "error");
    }
  }
  async function handleStar(event) {
    const projectData = window.SCITEX_PROJECT_DATA;
    if (!projectData) return;
    const btn = event.currentTarget;
    const isStarred = btn.classList.contains("active");
    try {
      const response = await fetch(
        `/${projectData.owner}/${projectData.slug}/api/star/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
        },
      );
      const data = await response.json();
      if (data.success) {
        // Toggle active state
        if (data.is_starred) {
          btn.classList.add("active");
        } else {
          btn.classList.remove("active");
        }
        // Update count
        const starCount = document.getElementById("star-count");
        if (starCount) starCount.textContent = data.star_count;
        // Show notification
        showNotification(data.message, "success");
      } else {
        showNotification(data.error || "Failed to update star status", "error");
      }
    } catch (error) {
      console.error("Error toggling star:", error);
      showNotification("Failed to update star status", "error");
    }
  }
  async function handleFork(event) {
    if (
      !confirm(
        "Fork this repository? This will create a copy under your account.",
      )
    ) {
      return;
    }
    const projectData = window.SCITEX_PROJECT_DATA;
    if (!projectData) return;
    const btn = event.currentTarget;
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = "<span>Forking...</span>";
    try {
      const response = await fetch(
        `/${projectData.owner}/${projectData.slug}/api/fork/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
        },
      );
      const data = await response.json();
      if (data.success) {
        // Update count
        const forkCount = document.getElementById("fork-count");
        if (forkCount) forkCount.textContent = data.fork_count;
        // Show success message and redirect
        showNotification(data.message, "success");
        setTimeout(() => {
          window.location.href = data.forked_project.url;
        }, 1500);
      } else {
        showNotification(data.error || "Failed to fork repository", "error");
        btn.innerHTML = originalText;
        btn.disabled = false;
      }
    } catch (error) {
      console.error("Error forking project:", error);
      showNotification("Failed to fork repository", "error");
      btn.innerHTML = originalText;
      btn.disabled = false;
    }
  }
  // Helper function to show notifications
  function showNotification(message, type = "info") {
    // Create notification element
    const notification = document.createElement("div");
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 24px;
        background: ${type === "success" ? "var(--color-success-emphasis)" : type === "error" ? "var(--color-danger-emphasis)" : "var(--color-accent-emphasis)"};
        color: white;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(notification);
    // Remove after 3 seconds
    setTimeout(() => {
      notification.style.animation = "slideOut 0.3s ease";
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }
  // Helper function to get CSRF token
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
  // Toolbar Dropdown Functions
  // =============================================================================
  function toggleBranchDropdown() {
    const dropdown = document.getElementById("branch-dropdown");
    const isVisible = dropdown && dropdown.style.display === "block";
    // Close all other dropdowns
    closeAllDropdowns();
    if (dropdown) {
      dropdown.style.display = isVisible ? "none" : "block";
      console.log("Branch dropdown toggled:", dropdown.style.display);
    }
  }
  function switchBranch(branchName) {
    console.log("Switching to branch:", branchName);
    const currentBranch = document.getElementById("current-branch");
    if (currentBranch) currentBranch.textContent = branchName;
    // Update active state in dropdown
    document.querySelectorAll(".branch-item").forEach((item) => {
      const htmlItem = item;
      if (htmlItem.dataset.branch === branchName) {
        htmlItem.classList.add("active");
        const svg = htmlItem.querySelector("svg");
        if (svg) svg.style.opacity = "1";
      } else {
        htmlItem.classList.remove("active");
        const svg = htmlItem.querySelector("svg");
        if (svg) svg.style.opacity = "0";
      }
    });
    // Close dropdown
    const branchDropdown = document.getElementById("branch-dropdown");
    if (branchDropdown) branchDropdown.style.display = "none";
    // TODO: Reload page with selected branch
    // const projectData = window.SCITEX_PROJECT_DATA;
    // window.location.href = `/${projectData.owner}/${projectData.slug}/?branch=${branchName}`;
  }
  // Simple wrapper functions for toolbar buttons
  function toggleWatch() {
    const btn = document.getElementById("watch-btn");
    if (btn) {
      // Create a proper event object
      const event = new MouseEvent("click", {
        bubbles: true,
        cancelable: true,
        view: window,
      });
      // Set currentTarget manually after creation
      Object.defineProperty(event, "currentTarget", {
        writable: false,
        value: btn,
      });
      handleWatch(event);
    }
  }
  function toggleStar() {
    const btn = document.getElementById("star-btn");
    if (btn) {
      // Create a proper event object
      const event = new MouseEvent("click", {
        bubbles: true,
        cancelable: true,
        view: window,
      });
      // Set currentTarget manually after creation
      Object.defineProperty(event, "currentTarget", {
        writable: false,
        value: btn,
      });
      handleStar(event);
    }
  }
  function forkProject() {
    const btn = document.getElementById("fork-btn");
    if (btn) {
      // Create a proper event object
      const event = new MouseEvent("click", {
        bubbles: true,
        cancelable: true,
        view: window,
      });
      // Set currentTarget manually after creation
      Object.defineProperty(event, "currentTarget", {
        writable: false,
        value: btn,
      });
      handleFork(event);
    }
  }
  function toggleAddFileDropdown() {
    const dropdown = document.getElementById("add-file-dropdown");
    if (!dropdown) return;
    const isVisible = dropdown.style.display === "block";
    // Close all other dropdowns
    closeAllDropdowns();
    dropdown.style.display = isVisible ? "none" : "block";
    console.log("Add file dropdown toggled:", dropdown.style.display);
  }
  function toggleCodeDropdown() {
    const dropdown = document.getElementById("code-dropdown");
    if (!dropdown) return;
    const isVisible = dropdown.style.display === "block";
    // Close all other dropdowns
    closeAllDropdowns();
    dropdown.style.display = isVisible ? "none" : "block";
    console.log("Code dropdown toggled:", dropdown.style.display);
  }
  function toggleCopyDropdown() {
    const dropdown = document.getElementById("copy-dropdown");
    if (!dropdown) return;
    const isVisible = dropdown.style.display === "block";
    // Close all other dropdowns
    closeAllDropdowns();
    dropdown.style.display = isVisible ? "none" : "block";
    console.log("Copy dropdown toggled:", dropdown.style.display);
  }
  function closeAllDropdowns() {
    const dropdowns = [
      "branch-dropdown-menu",
      "add-file-dropdown",
      "code-dropdown",
      "copy-dropdown",
    ];
    dropdowns.forEach((id) => {
      const dropdown = document.getElementById(id);
      if (dropdown && dropdown.style.display === "block") {
        dropdown.style.display = "none";
      }
    });
  }
  function copyCloneUrl(event) {
    const input = document.getElementById("clone-url");
    if (!input) return;
    navigator.clipboard
      .writeText(input.value)
      .then(() => {
        const btn = event.target.closest("button");
        if (!btn) return;
        const originalHTML = btn.innerHTML;
        btn.innerHTML =
          '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z"/></svg>';
        setTimeout(() => {
          btn.innerHTML = originalHTML;
        }, 2000);
      })
      .catch((err) => {
        console.error("Failed to copy:", err);
      });
  }
  function downloadProjectZip() {
    // Placeholder for ZIP download functionality
    alert("ZIP download functionality coming soon!");
  }
  // =============================================================================
  // Event Listeners
  // =============================================================================
  // Load file tree on page load
  document.addEventListener("DOMContentLoaded", function () {
    console.log("Page loaded - initializing sidebar, file tree and dropdown");
    // Initialize sidebar state
    initializeSidebar();
    // Load file tree
    loadFileTree();
    // Load initial stats
    loadProjectStats();
    // Make table rows clickable
    const fileBrowserRows = document.querySelectorAll(".file-browser-row");
    fileBrowserRows.forEach((row) => {
      row.addEventListener("click", function (e) {
        // Don't navigate if clicking on a link directly
        const target = e.target;
        if (target.tagName === "A" || target.closest("a")) {
          return;
        }
        const href = this.getAttribute("data-href");
        if (href) {
          window.location.href = href;
        }
      });
    });
    // Manual dropdown toggle for split button
    const dropdownToggle = document.querySelector(".dropdown-toggle-split");
    const dropdownMenu = document.querySelector(".dropdown-menu");
    if (dropdownToggle && dropdownMenu) {
      console.log("Dropdown elements found - setting up manual toggle");
      dropdownToggle.addEventListener("click", function (e) {
        console.log("Dropdown toggle clicked!");
        e.preventDefault();
        e.stopPropagation();
        const isVisible = dropdownMenu.style.display === "block";
        dropdownMenu.style.display = isVisible ? "none" : "block";
        console.log(
          "Dropdown visibility toggled to:",
          dropdownMenu.style.display,
        );
      });
      // Close dropdown when clicking outside
      document.addEventListener("click", function (e) {
        const target = e.target;
        if (
          !dropdownToggle.contains(target) &&
          !dropdownMenu.contains(target)
        ) {
          dropdownMenu.style.display = "none";
        }
      });
    } else {
      console.warn("Dropdown elements not found:", {
        dropdownToggle,
        dropdownMenu,
      });
    }
  });
  // Close dropdowns when clicking outside
  document.addEventListener("click", function (e) {
    // Check if click is on any dropdown button or within dropdown content
    const target = e.target;
    const clickedButton = target.closest("button");
    const isDropdownButton =
      clickedButton &&
      (clickedButton.id === "branch-dropdown-btn-header" ||
        clickedButton.id === "add-file-btn" ||
        clickedButton.classList.contains("dropdown-toggle-split"));
    const isDropdownContent = target.closest(".dropdown-menu");
    if (!isDropdownButton && !isDropdownContent) {
      closeAllDropdowns();
    }
  });
  // Expose functions to global scope for onclick handlers
  window.toggleSidebar = toggleSidebar;
  window.toggleSidebarSection = toggleSidebarSection;
  window.toggleFolder = toggleFolder;
  window.copyProjectToClipboard = copyProjectToClipboard;
  window.downloadProjectAsFile = downloadProjectAsFile;
  window.handleWatch = handleWatch;
  window.handleStar = handleStar;
  window.handleFork = handleFork;
  window.toggleBranchDropdown = toggleBranchDropdown;
  window.switchBranch = switchBranch;
  window.toggleWatch = toggleWatch;
  window.toggleStar = toggleStar;
  window.forkProject = forkProject;
  window.toggleAddFileDropdown = toggleAddFileDropdown;
  window.toggleCodeDropdown = toggleCodeDropdown;
  window.toggleCopyDropdown = toggleCopyDropdown;
  window.copyCloneUrl = copyCloneUrl;
  window.downloadProjectZip = downloadProjectZip;
})(); // End of IIFE
//# sourceMappingURL=project_detail.js.map
