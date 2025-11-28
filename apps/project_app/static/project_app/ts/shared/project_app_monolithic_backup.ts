/**
 * project_app.ts - Consolidated TypeScript for project_app
 *
 * This file contains all TypeScript functionality previously scattered across
 * inline <script> blocks in various templates.
 *
 * Organization:
 * 1. Sidebar Management (from project_detail.html)
 * 2. File Tree Management (from project_detail.html, project_directory.html)
 * 3. Project Actions (Watch/Star/Fork from project_detail.html)
 * 4. Project Forms (from project_create.html, project_settings.html, project_delete.html)
 * 5. File Management (from project_files.html, project_file_view.html, project_file_edit.html)
 * 6. Directory Operations (from project_directory.html)
 * 7. User Profile (from user_project_list.html)
 * 8. Utility Functions
 */

import { getCsrfToken } from "../utils/csrf.js";
import {
  loadFileTree as loadFileTreeShared,
  toggleFolder as toggleFolderShared,
} from "./file-tree.js";

console.log(
  "[DEBUG] apps/project_app/static/project_app/ts/shared/project_app.ts loaded",
);

(function () {
  "use strict";

  // =============================================================================
  // 1. SIDEBAR MANAGEMENT
  // =============================================================================

  // const SIDEBAR_STATE_KEY = 'scitex-sidebar-state';
  const SIDEBAR_SECTIONS_KEY = "scitex-sidebar-sections";

  /**
   * Initialize sidebar (no toggle functionality - always visible)
   */
  function initializeSidebar() {
    const sidebar = document.getElementById("repo-sidebar");

    if (!sidebar) {
      console.log("Sidebar element not found on this page");
      return;
    }

    console.log("Sidebar initialized (always visible)");
  }

  /**
   * Toggle individual sidebar section
   */
  function toggleSidebarSection(sectionId: string) {
    const sidebar = document.getElementById("repo-sidebar");

    if (!sidebar) return;

    // Don't toggle sections when sidebar is collapsed
    if (sidebar.classList.contains("collapsed")) {
      return;
    }

    const section = document.getElementById(sectionId);
    if (!section) return;

    section.classList.toggle("section-collapsed");
    saveSectionStates();
  }

  /**
   * Save all section states to localStorage
   */
  function saveSectionStates() {
    const fileTreeSection = document.getElementById("file-tree-section");
    const aboutSection = document.getElementById("about-section");

    if (!fileTreeSection && !aboutSection) return;

    const sections: Record<string, string> = {};
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
  // 2. FILE TREE MANAGEMENT
  // =============================================================================

  /**
   * Load file tree from API and render it in sidebar - uses shared module
   */
  async function loadFileTree() {
    console.log("[loadFileTree] START - Loading file tree from sidebar");

    // Extract project info from page URL
    const pathParts = window.location.pathname.split("/").filter((x) => x);
    if (pathParts.length < 2) {
      console.log("[loadFileTree] Not enough path parts");
      return;
    }

    const username = pathParts[0];
    const slug = pathParts[1];
    console.log("[loadFileTree] Fetching tree for:", username + "/" + slug);

    // Use shared loadFileTree function
    await loadFileTreeShared(username, slug, "file-tree");
  }

  /**
   * Toggle folder expansion in file tree - uses shared module
   */
  function toggleFolder(folderId: string, event?: Event): boolean {
    console.log("[toggleFolder] Toggling folder:", folderId);
    toggleFolderShared(folderId, event);
    return false;
  }

  // =============================================================================
  // 3. PROJECT ACTIONS (Watch/Star/Fork)
  // =============================================================================

  /**
   * Load project statistics (watch/star/fork counts)
   */
  async function loadProjectStats() {
    const watchCount = document.getElementById("watch-count");
    const starCount = document.getElementById("star-count");
    const forkCount = document.getElementById("fork-count");
    const sidebarStarCount = document.getElementById("sidebar-star-count");
    const sidebarForkCount = document.getElementById("sidebar-fork-count");

    if (!watchCount && !starCount && !forkCount) return;

    // Extract project info from page URL
    const pathParts = window.location.pathname.split("/").filter((x) => x);
    if (pathParts.length < 2) return;

    const username = pathParts[0];
    const slug = pathParts[1];

    try {
      const response = await fetch(`/${username}/${slug}/api/stats/`);
      const data = await response.json();

      if (data.success) {
        // Update counts
        if (watchCount) watchCount.textContent = data.stats.watch_count;
        if (starCount) starCount.textContent = data.stats.star_count;
        if (forkCount) forkCount.textContent = data.stats.fork_count;

        // Update sidebar counts
        if (sidebarStarCount) {
          sidebarStarCount.textContent = `${data.stats.star_count} ${data.stats.star_count === 1 ? "star" : "stars"}`;
        }
        if (sidebarForkCount) {
          sidebarForkCount.textContent = `${data.stats.fork_count} ${data.stats.fork_count === 1 ? "fork" : "forks"}`;
        }

        // Update button states
        const watchBtn = document.getElementById("watch-btn");
        const starBtn = document.getElementById("star-btn");

        if (watchBtn && data.user_status.is_watching) {
          watchBtn.classList.add("active");
        }
        if (starBtn && data.user_status.is_starred) {
          starBtn.classList.add("active");
        }
      }
    } catch (error) {
      console.error("Failed to load project stats:", error);
    }
  }

  /**
   * Handle watch button click
   */
  async function handleWatch(event: Event) {
    const btn = event.currentTarget as HTMLElement;
    const pathParts = window.location.pathname
      .split("/")
      .filter((x: string) => x);
    if (pathParts.length < 2) return;

    const username = pathParts[0];
    const slug = pathParts[1];

    try {
      const response = await fetch(`/${username}/${slug}/api/watch/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
      });

      const data = await response.json();

      if (data.success) {
        if (data.is_watching) {
          btn.classList.add("active");
        } else {
          btn.classList.remove("active");
        }

        const watchCount = document.getElementById("watch-count");
        if (watchCount) {
          watchCount.textContent = data.watch_count;
        }

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

  /**
   * Handle star button click
   */
  async function handleStar(event: Event) {
    const btn = event.currentTarget as HTMLElement;
    const pathParts = window.location.pathname
      .split("/")
      .filter((x: string) => x);
    if (pathParts.length < 2) return;

    const username = pathParts[0];
    const slug = pathParts[1];

    try {
      const response = await fetch(`/${username}/${slug}/api/star/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
      });

      const data = await response.json();

      if (data.success) {
        if (data.is_starred) {
          btn.classList.add("active");
        } else {
          btn.classList.remove("active");
        }

        const starCount = document.getElementById("star-count");
        if (starCount) {
          starCount.textContent = data.star_count;
        }

        showNotification(data.message, "success");
      } else {
        showNotification(data.error || "Failed to update star status", "error");
      }
    } catch (error) {
      console.error("Error toggling star:", error);
      showNotification("Failed to update star status", "error");
    }
  }

  /**
   * Handle fork button click
   */
  async function handleFork(event: Event) {
    if (
      !confirm(
        "Fork this repository? This will create a copy under your account.",
      )
    ) {
      return;
    }

    const btn = event.currentTarget as HTMLButtonElement;
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = "<span>Forking...</span>";

    const pathParts = window.location.pathname
      .split("/")
      .filter((x: string) => x);
    if (pathParts.length < 2) return;

    const username = pathParts[0];
    const slug = pathParts[1];

    try {
      const response = await fetch(`/${username}/${slug}/api/fork/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
      });

      const data = await response.json();

      if (data.success) {
        const forkCount = document.getElementById("fork-count");
        if (forkCount) {
          forkCount.textContent = data.fork_count;
        }

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

  // =============================================================================
  // 4. PROJECT FORMS (Create/Settings/Delete)
  // =============================================================================

  /**
   * Initialize project create form
   */
  function initProjectCreateForm() {
    const nameInput = document.getElementById("name");
    const form = document.querySelector("form");
    const submitButton = document.querySelector(".btn-primary");
    const initTypeRadios = document.querySelectorAll('input[name="init_type"]');
    const githubUrlInput = document.getElementById("github_url_input");
    const githubUrlField = document.getElementById("github_url");

    if (!nameInput) return;

    let nameCheckTimeout: number | undefined;
    let isNameAvailable = false;

    // Real-time name availability checking
    nameInput.addEventListener("input", function (this: HTMLInputElement) {
      const name = this.value.trim();
      const availabilityDiv = document.getElementById(
        "name-availability",
      ) as HTMLElement | null;
      const availabilityIcon = document.getElementById(
        "availability-icon",
      ) as HTMLElement | null;
      const availabilityMessage = document.getElementById(
        "availability-message",
      ) as HTMLElement | null;

      clearTimeout(nameCheckTimeout);

      if (!name) {
        if (availabilityDiv) availabilityDiv.style.display = "none";
        isNameAvailable = false;
        if (submitButton) {
          (submitButton as HTMLButtonElement).disabled = true;
          (submitButton as HTMLElement).style.opacity = "0.5";
          (submitButton as HTMLElement).style.cursor = "not-allowed";
        }
        return;
      }

      isNameAvailable = false;
      if (submitButton) {
        (submitButton as HTMLButtonElement).disabled = true;
        (submitButton as HTMLElement).style.opacity = "0.5";
        (submitButton as HTMLElement).style.cursor = "not-allowed";
      }

      if (availabilityDiv) {
        availabilityDiv.style.display = "block";
        if (availabilityIcon) availabilityIcon.textContent = "⏳";
        if (availabilityMessage) {
          availabilityMessage.textContent = " Checking availability...";
          availabilityMessage.style.color = "#666";
        }
      }

      nameCheckTimeout = window.setTimeout(async () => {
        try {
          const response = await fetch(
            `/project/api/check-name/?name=${encodeURIComponent(name)}`,
          );
          const data = await response.json();

          if (data.available) {
            isNameAvailable = true;
            if (availabilityIcon) availabilityIcon.textContent = "✓";
            if (availabilityMessage) {
              availabilityMessage.textContent = " " + data.message;
              availabilityMessage.style.color = "#28a745";
            }
            if (submitButton) {
              (submitButton as HTMLButtonElement).disabled = false;
              (submitButton as HTMLElement).style.opacity = "1";
              (submitButton as HTMLElement).style.cursor = "pointer";
            }
          } else {
            isNameAvailable = false;
            if (availabilityIcon) availabilityIcon.textContent = "✗";
            if (availabilityMessage) {
              availabilityMessage.textContent = " " + data.message;
              availabilityMessage.style.color = "#dc3545";
            }
            if (submitButton) {
              (submitButton as HTMLButtonElement).disabled = true;
              (submitButton as HTMLElement).style.opacity = "0.5";
              (submitButton as HTMLElement).style.cursor = "not-allowed";
            }
          }
        } catch (error) {
          console.error("Error checking name availability:", error);
          if (availabilityDiv) availabilityDiv.style.display = "none";
        }
      }, 500);
    });

    // Prevent form submission if name is not available
    if (form) {
      form.addEventListener("submit", function (e) {
        const name = (nameInput as HTMLInputElement).value.trim();
        if (!name) {
          e.preventDefault();
          alert("Please enter a project name");
          return;
        }
        if (!isNameAvailable) {
          e.preventDefault();
          alert(
            "Please choose an available project name. The current name is already taken or invalid.",
          );
          return;
        }
      });
    }

    // Handle initialization type selection
    initTypeRadios.forEach((radio) => {
      radio.addEventListener("change", function (this: HTMLInputElement) {
        if (githubUrlInput)
          (githubUrlInput as HTMLElement).style.display = "none";

        if (this.value === "github") {
          if (githubUrlInput && githubUrlField) {
            (githubUrlInput as HTMLElement).style.display = "block";
            githubUrlField.setAttribute("required", "required");
          }
        } else {
          if (githubUrlField) githubUrlField.removeAttribute("required");
        }
      });
    });

    // Auto-fill name from Git URL
    if (githubUrlField) {
      githubUrlField.addEventListener(
        "blur",
        function (this: HTMLInputElement) {
          const url = this.value.trim();
          if (url && !(nameInput as HTMLInputElement).value.trim()) {
            const repoName = extractRepoNameFromUrl(url);
            if (repoName) {
              (nameInput as HTMLInputElement).value = repoName;
              nameInput.dispatchEvent(new Event("input"));
            }
          }
        },
      );
    }

    // Aggressive autofill prevention
    nameInput.setAttribute("readonly", "readonly");

    const clearAutofill = function () {
      if (
        (nameInput as HTMLInputElement).value &&
        nameInput.matches(":-webkit-autofill")
      ) {
        (nameInput as HTMLInputElement).value = "";
      }
    };

    setTimeout(clearAutofill, 50);
    setTimeout(clearAutofill, 100);
    setTimeout(clearAutofill, 200);

    nameInput.addEventListener(
      "focus",
      function () {
        nameInput.removeAttribute("readonly");
      },
      { once: true },
    );

    nameInput.addEventListener(
      "click",
      function () {
        nameInput.removeAttribute("readonly");
      },
      { once: true },
    );

    setTimeout(function () {
      nameInput.removeAttribute("readonly");
    }, 500);
  }

  /**
   * Extract repository name from URL
   */
  function extractRepoNameFromUrl(url: string): string {
    if (!url) return "";
    url = url.trim();
    if (url.endsWith(".git")) {
      url = url.slice(0, -4);
    }
    const parts = url.replace(/\/$/, "").split("/");
    return parts[parts.length - 1] || "";
  }

  /**
   * Initialize project settings form
   */
  function initProjectSettingsForm() {
    // Radio button selection visual feedback
    document
      .querySelectorAll('.radio-option input[type="radio"]')
      .forEach((radio) => {
        radio.addEventListener("change", function (this: HTMLInputElement) {
          document
            .querySelectorAll(".radio-option")
            .forEach((opt) => opt.classList.remove("selected"));
          const closestOption = this.closest(".radio-option");
          if (closestOption) closestOption.classList.add("selected");
        });
      });

    // Delete modal functions
    const deleteModal = document.getElementById("deleteModal");
    const deleteConfirmInput = document.getElementById("deleteConfirmInput");
    const deleteConfirmButton = document.getElementById("deleteConfirmButton");

    if (deleteModal && deleteConfirmInput && deleteConfirmButton) {
      // Check delete input
      deleteConfirmInput.addEventListener(
        "input",
        function (this: HTMLInputElement) {
          const expectedValue = this.getAttribute("data-expected-value") || "";
          if (this.value === expectedValue) {
            (deleteConfirmButton as HTMLButtonElement).disabled = false;
            (deleteConfirmButton as HTMLElement).style.opacity = "1";
          } else {
            (deleteConfirmButton as HTMLButtonElement).disabled = true;
            (deleteConfirmButton as HTMLElement).style.opacity = "0.5";
          }
        },
      );
    }

    // Close modal on ESC key
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && deleteModal) {
        hideDeleteModal();
      }
    });

    // Add collaborator button feedback
    const addCollaboratorBtn = document.getElementById("addCollaboratorBtn");
    const collaboratorUsername = document.getElementById(
      "collaboratorUsername",
    );
    const addBtnText = document.getElementById("addBtnText");

    if (addCollaboratorBtn && collaboratorUsername && addBtnText) {
      addCollaboratorBtn.addEventListener("click", function (e) {
        const username = (
          collaboratorUsername as HTMLInputElement
        ).value.trim();
        if (username) {
          addBtnText.textContent = "Adding...";
          (addCollaboratorBtn as HTMLButtonElement).disabled = true;
          (addCollaboratorBtn as HTMLElement).style.opacity = "0.7";
          console.log("Adding collaborator:", username);
        } else {
          e.preventDefault();
          alert("Please enter a username");
        }
      });

      collaboratorUsername.addEventListener("input", function () {
        if ((addCollaboratorBtn as HTMLButtonElement).disabled) {
          addBtnText.textContent = "Add collaborator";
          (addCollaboratorBtn as HTMLButtonElement).disabled = false;
          (addCollaboratorBtn as HTMLElement).style.opacity = "1";
        }
      });
    }
  }

  /**
   * Show delete modal
   */
  function showDeleteModal() {
    const modal = document.getElementById("deleteModal");
    if (modal) {
      (modal as HTMLElement).style.display = "flex";
      const deleteConfirmInput = document.getElementById("deleteConfirmInput");
      const deleteConfirmButton = document.getElementById(
        "deleteConfirmButton",
      );
      if (deleteConfirmInput)
        (deleteConfirmInput as HTMLInputElement).value = "";
      if (deleteConfirmButton)
        (deleteConfirmButton as HTMLButtonElement).disabled = true;
    }
  }

  /**
   * Hide delete modal
   */
  function hideDeleteModal() {
    const modal = document.getElementById("deleteModal");
    if (modal) {
      (modal as HTMLElement).style.display = "none";
    }
  }

  /**
   * Submit delete form
   */
  function submitDelete() {
    const form = document.createElement("form");
    form.method = "POST";
    form.action = window.location.href;

    const csrfInput = document.createElement("input");
    csrfInput.type = "hidden";
    csrfInput.name = "csrfmiddlewaretoken";
    const csrfToken = document.querySelector(
      "[name=csrfmiddlewaretoken]",
    ) as HTMLInputElement;
    csrfInput.value = csrfToken ? csrfToken.value : "";

    const actionInput = document.createElement("input");
    actionInput.type = "hidden";
    actionInput.name = "action";
    actionInput.value = "delete_repository";

    form.appendChild(csrfInput);
    form.appendChild(actionInput);
    document.body.appendChild(form);
    form.submit();
  }

  /**
   * Initialize project delete form
   */
  function initProjectDeleteForm() {
    const confirmText = document.getElementById("confirmText");
    const deleteBtn = document.getElementById("deleteBtn");

    if (!confirmText || !deleteBtn) return;

    const expectedText = deleteBtn.getAttribute("data-expected-text") || "";

    confirmText.addEventListener("input", function (this: HTMLInputElement) {
      if (this.value === expectedText) {
        (deleteBtn as HTMLButtonElement).disabled = false;
        (deleteBtn as HTMLElement).style.opacity = "1";
        (deleteBtn as HTMLElement).style.cursor = "pointer";
      } else {
        (deleteBtn as HTMLButtonElement).disabled = true;
        (deleteBtn as HTMLElement).style.opacity = "0.5";
        (deleteBtn as HTMLElement).style.cursor = "not-allowed";
      }
    });
  }

  // =============================================================================
  // 5. FILE MANAGEMENT
  // =============================================================================

  /**
   * Handle file upload
   */
  function handleFileUpload(event: Event) {
    const target = event.target as HTMLInputElement;
    const files = target.files;
    if (files && files.length > 0) {
      alert(
        `Selected ${files.length} file(s) for upload. Upload functionality to be implemented.`,
      );
    }
  }

  /**
   * Create new folder
   */
  function createFolder(): void {
    const folderName = prompt("Enter folder name:");
    if (folderName && folderName.trim()) {
      alert(`Creating folder: ${folderName}`);
    }
  }

  /**
   * Refresh files list
   */
  function refreshFiles(): void {
    location.reload();
  }

  /**
   * Open file or folder
   */
  function openFile(fileName: string) {
    alert(`Opening: ${fileName}`);
  }

  /**
   * Copy file content to clipboard
   */
  function copyToClipboard() {
    const content =
      (document.querySelector(".file-content") as HTMLElement)?.innerText ||
      (document.querySelector(".markdown-body") as HTMLElement)?.innerText ||
      "";

    navigator.clipboard
      .writeText(content)
      .then(() => {
        const btn = (event as Event).target as HTMLElement;
        const originalText = btn.innerHTML;
        btn.innerHTML = "✓ Copied!";
        setTimeout(() => {
          btn.innerHTML = originalText;
        }, 2000);
      })
      .catch((err: Error) => {
        alert("Failed to copy: " + err);
      });
  }

  /**
   * Show markdown code view
   */
  function showCode(): void {
    const preview = document.getElementById("markdownPreview");
    const code = document.getElementById("markdownCode");
    const codeBtn = document.getElementById("codeBtn");
    const previewBtn = document.getElementById("previewBtn");

    if (preview && code && codeBtn && previewBtn) {
      (preview as HTMLElement).style.display = "none";
      (code as HTMLElement).style.display = "block";
      codeBtn.classList.add("active");
      previewBtn.classList.remove("active");
    }
  }

  /**
   * Show markdown preview
   */
  function showPreview(): void {
    const preview = document.getElementById("markdownPreview");
    const code = document.getElementById("markdownCode");
    const codeBtn = document.getElementById("codeBtn");
    const previewBtn = document.getElementById("previewBtn");

    if (preview && code && codeBtn && previewBtn) {
      (preview as HTMLElement).style.display = "block";
      (code as HTMLElement).style.display = "none";
      codeBtn.classList.remove("active");
      previewBtn.classList.add("active");
    }
  }

  /**
   * Show markdown edit view (for file editor)
   */
  function showEdit(): void {
    const textarea = document.getElementById("editorTextarea");
    const previewContainer = document.getElementById("previewContainer");
    const editBtn = document.getElementById("editBtn");
    const previewBtn = document.getElementById("previewBtn");

    if (textarea && previewContainer && editBtn && previewBtn) {
      (textarea as HTMLElement).style.display = "block";
      (previewContainer as HTMLElement).style.display = "none";
      editBtn.classList.add("active");
      previewBtn.classList.remove("active");
    }
  }

  // =============================================================================
  // 6. DIRECTORY OPERATIONS
  // =============================================================================

  /**
   * Copy entire project/directory content to clipboard
   */
  async function copyProjectToClipboard() {
    console.log("copyProjectToClipboard() called");
    const btn = document.getElementById("copy-project-btn");
    if (!btn) return;

    const originalText = btn.innerHTML;
    btn.innerHTML = "⏳ Loading...";
    (btn as HTMLButtonElement).disabled = true;

    const pathParts = window.location.pathname.split("/").filter((x) => x);
    if (pathParts.length < 2) return;

    const username = pathParts[0];
    const slug = pathParts[1];
    const subpath = pathParts.slice(2).join("/");

    try {
      console.log("Fetching concatenated content...");
      const response = await fetch(
        `/${username}/${slug}/api/concatenate/${subpath}`,
      );
      const data = await response.json();
      console.log("API response:", data);

      if (data.success) {
        await navigator.clipboard.writeText(data.content);
        btn.innerHTML = `✓ Copied ${data.file_count} files!`;
        setTimeout(() => {
          btn.innerHTML = originalText;
          (btn as HTMLButtonElement).disabled = false;
        }, 3000);
      } else {
        alert("Error: " + data.error);
        btn.innerHTML = originalText;
        (btn as HTMLButtonElement).disabled = false;
      }
    } catch (err) {
      alert("Failed to copy: " + err);
      btn.innerHTML = originalText;
      (btn as HTMLButtonElement).disabled = false;
    }
  }

  /**
   * Download project/directory content as file
   */
  async function downloadProjectAsFile() {
    const btn = (event as Event).target as HTMLElement;
    const originalText = btn.innerHTML;
    btn.innerHTML = "⏳ Preparing download...";

    const pathParts = window.location.pathname
      .split("/")
      .filter((x: string) => x);
    if (pathParts.length < 2) return;

    const username = pathParts[0];
    const slug = pathParts[1];
    const subpath = pathParts.slice(2).join("/");

    try {
      const response = await fetch(
        `/${username}/${slug}/api/concatenate/${subpath}`,
      );
      const data = await response.json();

      if (data.success) {
        const blob = new Blob([data.content], { type: "text/plain" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;

        const dirName =
          subpath
            .split("/")
            .filter((x) => x)
            .pop() || slug;
        a.download = `${dirName}_all_files.txt`;

        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        btn.innerHTML = `✓ Downloaded ${data.file_count} files!`;
        setTimeout(() => {
          btn.innerHTML = originalText;
        }, 3000);
      } else {
        alert("Error: " + data.error);
        btn.innerHTML = originalText;
      }
    } catch (err) {
      alert("Failed to download: " + err);
      btn.innerHTML = originalText;
    }
  }

  /**
   * Toggle branch dropdown
   */
  function toggleBranchDropdown(event?: Event) {
    if (event) event.stopPropagation();
    const dropdown = document.getElementById("branchDropdown");
    if (dropdown) {
      dropdown.classList.toggle("show");
    }
  }

  /**
   * Switch to different Git branch
   */
  async function switchBranch(branch: string) {
    console.log("Switching to branch:", branch);

    const pathParts = window.location.pathname
      .split("/")
      .filter((x: string) => x);
    if (pathParts.length < 2) return;

    const username = pathParts[0];
    const slug = pathParts[1];

    try {
      const response = await fetch(`/${username}/${slug}/api/switch-branch/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({ branch: branch }),
      });

      const data = await response.json();

      if (data.success) {
        window.location.reload();
      } else {
        alert("Failed to switch branch: " + data.error);
      }
    } catch (error) {
      console.error("Error switching branch:", error);
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
      alert("Failed to switch branch: " + errorMessage);
    }
  }

  /**
   * Toggle dropdown menus
   */
  function toggleAddFileDropdown(): void {
    const dropdown = document.getElementById("add-file-dropdown");
    if (dropdown) {
      const isVisible = (dropdown as HTMLElement).style.display === "block";
      closeAllDropdowns();
      (dropdown as HTMLElement).style.display = isVisible ? "none" : "block";
    }
  }

  function toggleCopyDropdown(): void {
    const dropdown = document.getElementById("copy-dropdown");
    if (dropdown) {
      const isVisible = (dropdown as HTMLElement).style.display === "block";
      closeAllDropdowns();
      (dropdown as HTMLElement).style.display = isVisible ? "none" : "block";
    }
  }

  function toggleCodeDropdown(): void {
    const dropdown = document.getElementById("code-dropdown");
    if (dropdown) {
      const isVisible = (dropdown as HTMLElement).style.display === "block";
      closeAllDropdowns();
      (dropdown as HTMLElement).style.display = isVisible ? "none" : "block";
    }
  }

  function toggleMoreDropdown(): void {
    const dropdown = document.getElementById("more-dropdown");
    if (dropdown) {
      const isVisible = (dropdown as HTMLElement).style.display === "block";
      closeAllDropdowns();
      (dropdown as HTMLElement).style.display = isVisible ? "none" : "block";
    }
  }

  function closeAllDropdowns(): void {
    document
      .querySelectorAll(".dropdown-menu, .file-browser-toolbar .dropdown-menu")
      .forEach((dropdown) => {
        (dropdown as HTMLElement).style.display = "none";
      });
  }

  // =============================================================================
  // 7. USER PROFILE
  // =============================================================================

  /**
   * Repository search in user profile
   */
  function initRepoSearch() {
    const searchInput = document.getElementById("repo-search");
    if (!searchInput) return;

    searchInput.addEventListener("input", function (e) {
      const target = e.target as HTMLInputElement;
      const searchTerm = target.value.toLowerCase();
      const repoItems = document.querySelectorAll(".repo-item");

      repoItems.forEach((item) => {
        const repoName =
          item.querySelector(".repo-name")?.textContent?.toLowerCase() || "";
        const repoDesc =
          item.querySelector(".repo-description")?.textContent?.toLowerCase() ||
          "";

        if (repoName.includes(searchTerm) || repoDesc.includes(searchTerm)) {
          (item as HTMLElement).style.display = "";
        } else {
          (item as HTMLElement).style.display = "none";
        }
      });
    });
  }

  /**
   * Toggle follow/unfollow for user
   */
  async function toggleFollow() {
    const btn = document.getElementById("follow-btn");
    if (!btn) return;

    const isFollowing = btn.innerHTML.includes("Following");
    const username = btn.getAttribute("data-username");
    if (!username) return;

    const endpoint = isFollowing
      ? `/social/api/unfollow/${username}/`
      : `/social/api/follow/${username}/`;

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCsrfToken(),
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      if (data.success) {
        if (isFollowing) {
          btn.innerHTML = '<i class="fas fa-user-plus"></i> Follow';
        } else {
          btn.innerHTML = '<i class="fas fa-user-check"></i> Following';
        }

        const followerCount = document.querySelector(".profile-stat strong");
        if (followerCount) {
          followerCount.textContent = data.followers_count;
        }
      } else {
        alert(data.error || "Failed to update follow status");
      }
    } catch (err) {
      console.error("Follow error:", err);
      alert("Failed to update follow status");
    }
  }

  /**
   * Toggle star/unstar for repository
   */
  async function toggleStar(btn: HTMLButtonElement) {
    const isStarred = btn.innerHTML.includes("Unstar");
    const username = btn.dataset.username;
    const slug = btn.dataset.slug;

    if (!username || !slug) return;

    const endpoint = isStarred
      ? `/social/api/unstar/${username}/${slug}/`
      : `/social/api/star/${username}/${slug}/`;

    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = "⏳ ...";

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCsrfToken(),
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      if (data.success) {
        if (isStarred) {
          btn.innerHTML = "⭐ Star";
        } else {
          btn.innerHTML = "⭐ Unstar";
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

  // =============================================================================
  // 8. UTILITY FUNCTIONS
  // =============================================================================

  /**
   * Show notification message
   */
  function showNotification(message: string, type: string = "info"): void {
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

    setTimeout(() => {
      notification.style.animation = "slideOut 0.3s ease";
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }

  /**
   * Make table rows clickable
   * Supports both .clickable-row (legacy) and .file-browser-row (new standard) classes
   */
  function initClickableRows() {
    const clickableRows = document.querySelectorAll(
      ".clickable-row, .file-browser-row",
    );
    clickableRows.forEach((row) => {
      row.addEventListener("click", function (this: HTMLElement, e: Event) {
        const target = e.target as HTMLElement;
        if (target.tagName === "A" || target.closest("a")) {
          return;
        }
        const href = this.getAttribute("data-href");
        if (href) {
          window.location.href = href;
        }
      });
    });
  }

  /**
   * Initialize drag and drop for file upload
   */
  function initDragAndDrop() {
    const uploadZone = document.getElementById("upload-zone");
    if (!uploadZone) return;

    uploadZone.addEventListener("dragover", (e: DragEvent) => {
      e.preventDefault();
      uploadZone.classList.add("dragover");
    });

    uploadZone.addEventListener("dragleave", (e: DragEvent) => {
      e.preventDefault();
      uploadZone.classList.remove("dragover");
    });

    uploadZone.addEventListener("drop", (e: DragEvent) => {
      e.preventDefault();
      uploadZone.classList.remove("dragover");

      const files = e.dataTransfer?.files;
      if (files && files.length > 0) {
        alert(
          `Dropped ${files.length} file(s). Upload functionality to be implemented.`,
        );
      }
    });

    uploadZone.addEventListener("click", () => {
      const fileInput = document.getElementById(
        "file-upload",
      ) as HTMLInputElement;
      if (fileInput) fileInput.click();
    });
  }

  // =============================================================================
  // INITIALIZATION ON PAGE LOAD
  // =============================================================================

  document.addEventListener("DOMContentLoaded", function () {
    console.log("project_app.js: Initializing...");

    // Initialize sidebar if present
    if (document.getElementById("repo-sidebar")) {
      initializeSidebar();
      loadFileTree();
    }

    // Load project stats if on project detail page
    if (
      document.getElementById("watch-count") ||
      document.getElementById("star-count")
    ) {
      loadProjectStats();
    }

    // Initialize forms based on page context
    if (
      document.getElementById("name") &&
      document.getElementById("name-availability")
    ) {
      initProjectCreateForm();
    }

    if (document.querySelector('.radio-option input[type="radio"]')) {
      initProjectSettingsForm();
    }

    if (
      document.getElementById("confirmText") &&
      document.getElementById("deleteBtn")
    ) {
      initProjectDeleteForm();
    }

    // Initialize clickable rows
    initClickableRows();

    // Initialize drag and drop
    initDragAndDrop();

    // Initialize repository search
    initRepoSearch();

    // Close dropdowns when clicking outside
    document.addEventListener("click", function (e) {
      const target = e.target as HTMLElement;
      if (
        !target.closest(".btn-group") &&
        !target.closest(".file-browser-toolbar .btn-group")
      ) {
        closeAllDropdowns();
      }

      // Close branch dropdown
      const branchDropdown = document.getElementById("branchDropdown");
      const branchSelector = document.querySelector(".branch-selector");
      if (
        branchDropdown &&
        branchSelector &&
        !branchSelector.contains(target)
      ) {
        branchDropdown.classList.remove("show");
      }
    });

    console.log("project_app.ts: Initialization complete");
  });

  // =============================================================================
  // EXPOSE FUNCTIONS TO GLOBAL SCOPE (for onclick handlers in templates)
  // =============================================================================

  // Make key functions available globally for inline onclick handlers
  (window as any).toggleSidebarSection = toggleSidebarSection;
  (window as any).toggleFolder = toggleFolder;
  (window as any).handleWatch = handleWatch;
  (window as any).handleStar = handleStar;
  (window as any).handleFork = handleFork;
  (window as any).showDeleteModal = showDeleteModal;
  (window as any).hideDeleteModal = hideDeleteModal;
  (window as any).submitDelete = submitDelete;
  (window as any).copyToClipboard = copyToClipboard;
  (window as any).showCode = showCode;
  (window as any).showPreview = showPreview;
  (window as any).showEdit = showEdit;
  (window as any).copyProjectToClipboard = copyProjectToClipboard;
  (window as any).downloadProjectAsFile = downloadProjectAsFile;
  (window as any).toggleBranchDropdown = toggleBranchDropdown;
  (window as any).switchBranch = switchBranch;
  (window as any).toggleAddFileDropdown = toggleAddFileDropdown;
  (window as any).toggleCopyDropdown = toggleCopyDropdown;
  (window as any).toggleCodeDropdown = toggleCodeDropdown;
  (window as any).toggleMoreDropdown = toggleMoreDropdown;
  (window as any).toggleFollow = toggleFollow;
  (window as any).toggleStar = toggleStar;
  (window as any).handleFileUpload = handleFileUpload;
  (window as any).createFolder = createFolder;
  (window as any).refreshFiles = refreshFiles;
  (window as any).openFile = openFile;
})(); // End of IIFE
