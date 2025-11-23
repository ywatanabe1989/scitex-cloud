/**
 * Section Management Functions
 * Handles section loading, switching, and CRUD operations
 */

import { WriterEditor, SectionsManager, PDFPreviewManager, setLoadingContent, getLoadingContent } from "../modules/index.js";
import { statePersistence } from "../modules/state-persistence.js";
import { getCsrfToken } from "@/utils/csrf.js";
import { getWriterConfig } from "../helpers.js";
import { validateSectionReadResponse } from "../types/api-responses.js";
import {
  showToast,
  getUserContext,
  updateWordCountDisplay,
  updateSectionTitleLabel,
  updatePDFPreviewTitle,
  updateCommitButtonVisibility,
} from "./ui.js";
import {
  syncDropdownToSection,
  populateSectionDropdownDirect,
  handleDocTypeSwitch,
} from "./section-dropdown.js";

// Module-level variables
let compileTimeout: ReturnType<typeof setTimeout> | null = null;

/**
 * Clear compile timeout
 */
export function clearCompileTimeout(): void {
  if (compileTimeout) {
    clearTimeout(compileTimeout);
    compileTimeout = null;
  }
}

/**
 * Setup section listeners
 */
export function setupSectionListeners(
  sectionsManager: SectionsManager,
  editor: WriterEditor,
  state: any,
  _storage: any,
): void {
  const sectionItems = document.querySelectorAll(".section-tab");
  sectionItems.forEach((item) => {
    item.addEventListener("click", (e: Event) => {
      const target = e.target as HTMLElement;
      const sectionId = target.dataset.section;
      if (sectionId) {
        switchSection(editor, sectionsManager, state, sectionId);
      }
    });
  });

  // NO CALLBACKS - direct error handling only
}

/**
 * Load section content from API
 */
export async function loadSectionContent(
  editor: WriterEditor,
  sectionsManager: SectionsManager,
  _state: any,
  sectionId: string,
  pdfPreviewManager?: PDFPreviewManager,
): Promise<void> {
  const config = getWriterConfig();
  if (!config.projectId) {
    console.warn("[Writer] Cannot load section content: no project ID");
    return;
  }

  try {
    // Extract section name and doc type from sectionId (e.g., "manuscript/abstract" -> doc_type="manuscript", section_name="abstract")
    const parts = sectionId.split("/");
    if (parts.length !== 2) {
      console.warn("[Writer] Invalid section ID format:", sectionId);
      return;
    }

    const docType = parts[0];
    const sectionName = parts[1];

    const userContext = getUserContext();
    console.log(
      `${userContext} [Writer] Loading section content:`,
      sectionId,
      "docType:",
      docType,
      "sectionName:",
      sectionName,
    );

    const response = await fetch(
      `/writer/api/project/${config.projectId}/section/${sectionName}/?doc_type=${docType}`,
    );

    if (!response.ok) {
      const error = await response.text();
      console.error("[Writer] Failed to load section:", response.status, error);
      return;
    }

    const data = await response.json();
    console.log("[Writer] API Response for", sectionId, ":", data);

    if (data.success && data.content !== undefined) {
      console.log(
        "[Writer] ✓ Content loaded for:",
        sectionId,
        "length:",
        data.content.length,
      );
      console.log("[Writer] First 100 chars:", data.content.substring(0, 100));

      // Set flag to prevent multiple auto-compiles during onChange events
      setLoadingContent(true);
      sectionsManager.setContent(sectionId, data.content);

      // Use setContentForSection to restore cursor position
      if (typeof (editor as any).setContentForSection === "function") {
        (editor as any).setContentForSection(sectionId, data.content);
      } else {
        editor.setContent(data.content);
      }

      // Reset flag and trigger ONE initial preview
      setTimeout(() => {
        setLoadingContent(false);
        // Trigger initial preview for the loaded section (skip for compiled sections)
        const isCompiledSection =
          sectionId.endsWith("/compiled_pdf") ||
          sectionId.endsWith("/compiled_tex");
        if (pdfPreviewManager && !isCompiledSection) {
          console.log("[Writer] Triggering initial preview for:", sectionId);
          pdfPreviewManager.compileQuick(data.content, sectionId);
        }
      }, 100);
    } else {
      const errorMsg = data.error || "Unknown error loading section";
      console.error("[Writer] ✗ API Error:", errorMsg);
      throw new Error(errorMsg);
    }
  } catch (error) {
    console.error("[Writer] Error loading section content:", error);
    setLoadingContent(false); // Reset flag on error
    throw error; // Re-throw to let caller handle it
  }
}

/**
 * Switch to a section
 */
export async function switchSection(
  editor: WriterEditor,
  sectionsManager: SectionsManager,
  state: any,
  sectionId: string,
  pdfPreviewManager?: PDFPreviewManager,
): Promise<void> {
  // Save current section
  const currentContent = editor.getContent();
  sectionsManager.setContent(state.currentSection, currentContent);

  // Update current section
  state.currentSection = sectionId;
  console.log("[Writer] Switching to section:", sectionId);

  updateSectionUI(sectionId);
  syncDropdownToSection(sectionId);

  // For compiled_pdf sections, load the compiled TeX in editor (read-only)
  if (sectionId.endsWith("/compiled_pdf")) {
    console.log("[Writer] Compiled PDF section - loading compiled TeX");

    // Set editor to read-only
    if (typeof (editor as any).setReadOnly === "function") {
      (editor as any).setReadOnly(true);
    }

    // Load compiled_tex content
    const compiledTexId = sectionId.replace("/compiled_pdf", "/compiled_tex");
    try {
      await loadSectionContent(editor, sectionsManager, state, compiledTexId, pdfPreviewManager);
    } catch (error) {
      const errorMsg = `Failed to load compiled TeX: ${error}`;
      console.error("[Writer]", errorMsg);
      editor.setContent(
        `% ERROR: ${errorMsg}\n% Please check browser console for details`,
      );
    }
    return;
  }

  // For regular editable sections
  if (typeof (editor as any).setReadOnly === "function") {
    (editor as any).setReadOnly(false);
  }

  // Load fresh content from API
  try {
    await loadSectionContent(editor, sectionsManager, state, sectionId, pdfPreviewManager);
  } catch (error) {
    const errorMsg = `Failed to load section ${sectionId}: ${error}`;
    console.error("[Writer]", errorMsg);
    editor.setContent(
      `% ERROR: ${errorMsg}\n% Please check browser console for details`,
    );
  }
}

/**
 * Update section UI
 */
export function updateSectionUI(sectionId: string): void {
  document.querySelectorAll(".section-tab").forEach((tab) => {
    tab.classList.toggle(
      "active",
      (tab as HTMLElement).dataset.section === sectionId,
    );
  });

  // Update the section title label in the editor header
  updateSectionTitleLabel(sectionId);

  // Update PDF preview title as well
  updatePDFPreviewTitle(sectionId);

  // Show/hide commit button based on section type (hide for read-only sections)
  updateCommitButtonVisibility(sectionId);

  // Load compiled PDF if this is the compiled_pdf section
  if (sectionId.endsWith("/compiled_pdf")) {
    // Cancel any pending auto-compile from previous section
    clearCompileTimeout();
    loadCompiledPDF(sectionId);
  }
}

/**
 * Load compiled PDF for display (not quick preview)
 */
export function loadCompiledPDF(sectionId: string): void {
  const config = getWriterConfig();
  if (!config.projectId) return;

  // Extract doc type from sectionId (e.g., "manuscript/compiled_pdf" -> "manuscript")
  const parts = sectionId.split("/");
  const docType = parts[0];

  // Use API endpoint for PDF with doc_type query parameter
  const pdfUrl = `/writer/api/project/${config.projectId}/pdf/?doc_type=${docType}`;

  console.log(
    "[Writer] Loading compiled PDF for section:",
    sectionId,
    "URL:",
    pdfUrl,
  );

  const textPreview = document.getElementById("text-preview");
  if (!textPreview) return;

  // Check if PDF exists first
  fetch(pdfUrl, { method: "HEAD" })
    .then((response) => {
      if (!response.ok) {
        // PDF doesn't exist - show helpful message
        textPreview.innerHTML = `
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 2rem; text-align: center; color: var(--color-fg-muted);">
                        <i class="fas fa-file-pdf fa-3x mb-3" style="opacity: 0.3;"></i>
                        <h5 style="color: var(--color-fg-default);">Full Manuscript Not Compiled Yet</h5>
                        <p style="margin: 1rem 0;">Click the 📄 <strong>Compile</strong> button in the dropdown to generate the full manuscript PDF.</p>
                        <small style="opacity: 0.7;">This combines all enabled sections into a single document.</small>
                    </div>
                `;
        return;
      }

      // PDF exists - display it with cache-busting
      const cacheBustUrl = `${pdfUrl}?t=${Date.now()}`;
      textPreview.innerHTML = `
                <div class="pdf-preview-container">
                    <div class="pdf-preview-viewer" id="pdf-viewer-pane">
                        <iframe
                            src="${cacheBustUrl}#toolbar=0&navpanes=0&scrollbar=1&view=FitW&zoom=page-width"
                            type="application/pdf"
                            width="100%"
                            height="100%"
                            title="Compiled PDF"
                            frameborder="0"
                            style="display: block;">
                        </iframe>
                    </div>
                </div>
            `;

      // Reset scroll position to top
      textPreview.scrollTop = 0;
    })
    .catch((error) => {
      console.error("[Writer] Error checking compiled PDF:", error);
      textPreview.innerHTML = `
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 2rem; text-align: center; color: var(--color-fg-muted);">
                    <i class="fas fa-exclamation-triangle fa-3x mb-3 text-warning"></i>
                    <h5 style="color: var(--color-fg-default);">Error Loading PDF</h5>
                    <p>Could not check if PDF exists. Please try again.</p>
                </div>
            `;
    });
}

/**
 * Setup section management button listeners
 */
export function setupSectionManagementButtons(
  config: any,
  state: any,
  sectionsManager: SectionsManager,
  editor: WriterEditor | null,
): void {
  console.log("[Writer] Setting up section management buttons");

  // Get references to buttons
  const addSectionBtn = document.getElementById("add-section-btn");
  const deleteSectionBtn = document.getElementById("delete-section-btn");
  const toggleIncludeBtn = document.getElementById(
    "toggle-section-include-btn",
  );
  const moveUpBtn = document.getElementById("move-section-up-btn");
  const moveDownBtn = document.getElementById("move-section-down-btn");

  // Add Section Button
  if (addSectionBtn) {
    addSectionBtn.addEventListener("click", () => {
      const modal = new (window as any).bootstrap.Modal(
        document.getElementById("add-section-modal"),
      );
      modal.show();
    });
  }

  // Confirm Add Section
  const confirmAddBtn = document.getElementById("confirm-add-section-btn");
  if (confirmAddBtn) {
    confirmAddBtn.addEventListener("click", async () => {
      const nameInput = document.getElementById(
        "new-section-name",
      ) as HTMLInputElement;
      const labelInput = document.getElementById(
        "new-section-label",
      ) as HTMLInputElement;

      const sectionName = nameInput.value
        .trim()
        .toLowerCase()
        .replace(/\s+/g, "_");
      const sectionLabel =
        labelInput.value.trim() ||
        sectionName
          .split("_")
          .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
          .join(" ");

      if (!sectionName) {
        showToast("Please enter a section name", "error");
        return;
      }

      // Validate section name format
      if (!/^[a-z0-9_]+$/.test(sectionName)) {
        showToast(
          "Section name must contain only lowercase letters, numbers, and underscores",
          "error",
        );
        return;
      }

      try {
        const docType = state.currentDocType || "manuscript";
        const response = await fetch(
          `/writer/api/project/${config.projectId}/section/create/`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCsrfToken(),
            },
            body: JSON.stringify({
              doc_type: docType,
              section_name: sectionName,
              section_label: sectionLabel,
            }),
          },
        );

        const data = await response.json();

        if (response.ok && data.success) {
          showToast(
            `Section "${sectionLabel}" created successfully`,
            "success",
          );

          // Close modal
          const modalEl = document.getElementById("add-section-modal");
          if (modalEl) {
            const modal = (window as any).bootstrap.Modal.getInstance(modalEl);
            modal?.hide();
          }

          // Clear inputs
          nameInput.value = "";
          labelInput.value = "";

          // Refresh section dropdown
          await populateSectionDropdownDirect(
            docType,
            null,
            undefined, // compilationManager not accessible in nested closure
            state,
          );

          // Switch to the new section
          const newSectionId = `${docType}/${sectionName}`;
          if (editor) {
            switchSection(editor, sectionsManager, state, newSectionId);
          }
        } else {
          showToast(
            `Failed to create section: ${data.error || "Unknown error"}`,
            "error",
          );
        }
      } catch (error) {
        console.error("[Writer] Error creating section:", error);
        showToast("Failed to create section", "error");
      }
    });
  }

  // Delete Section Button
  if (deleteSectionBtn) {
    deleteSectionBtn.addEventListener("click", () => {
      const currentSection = state.currentSection;
      if (!currentSection) {
        showToast("No section selected", "error");
        return;
      }

      // Extract section name from ID
      const parts = currentSection.split("/");
      const sectionName = parts[parts.length - 1];

      // Prevent deletion of core sections
      const coreSections = [
        "abstract",
        "introduction",
        "methods",
        "results",
        "discussion",
        "title",
        "authors",
        "keywords",
        "compiled_pdf",
        "compiled_tex",
      ];
      if (coreSections.includes(sectionName)) {
        showToast("Cannot delete core sections", "error");
        return;
      }

      // Show confirmation modal
      const displayElem = document.getElementById(
        "delete-section-name-display",
      );
      if (displayElem) {
        displayElem.textContent = sectionName;
      }

      const modal = new (window as any).bootstrap.Modal(
        document.getElementById("delete-section-modal"),
      );
      modal.show();
    });
  }

  // Confirm Delete Section
  const confirmDeleteBtn = document.getElementById(
    "confirm-delete-section-btn",
  );
  if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener("click", async () => {
      const currentSection = state.currentSection;
      if (!currentSection) return;

      try {
        const response = await fetch(
          `/writer/api/project/${config.projectId}/section/${encodeURIComponent(currentSection)}/delete/`,
          {
            method: "DELETE",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCsrfToken(),
            },
          },
        );

        const data = await response.json();

        if (response.ok && data.success) {
          showToast("Section deleted successfully", "success");

          // Close modal
          const modalEl = document.getElementById("delete-section-modal");
          if (modalEl) {
            const modal = (window as any).bootstrap.Modal.getInstance(modalEl);
            modal?.hide();
          }

          // Refresh section dropdown
          const docType = state.currentDocType || "manuscript";
          await populateSectionDropdownDirect(
            docType,
            null,
            undefined, // compilationManager not accessible in nested closure
            state,
          );

          // Switch to first available section
          if (editor) {
            handleDocTypeSwitch(editor, sectionsManager, state, docType);
          }
        } else {
          showToast(
            `Failed to delete section: ${data.error || "Unknown error"}`,
            "error",
          );
        }
      } catch (error) {
        console.error("[Writer] Error deleting section:", error);
        showToast("Failed to delete section", "error");
      }
    });
  }

  // Toggle Include/Exclude Button
  if (toggleIncludeBtn) {
    toggleIncludeBtn.addEventListener("click", async () => {
      const currentSection = state.currentSection;
      if (!currentSection) {
        showToast("No section selected", "error");
        return;
      }

      const isExcluded = toggleIncludeBtn.classList.contains("excluded");
      const newState = !isExcluded;

      try {
        const response = await fetch(
          `/writer/api/project/${config.projectId}/section/${encodeURIComponent(currentSection)}/toggle-exclude/`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCsrfToken(),
            },
            body: JSON.stringify({ excluded: newState }),
          },
        );

        const data = await response.json();

        if (response.ok && data.success) {
          // Update button state
          if (newState) {
            toggleIncludeBtn.classList.add("excluded");
            toggleIncludeBtn
              .querySelector("i")
              ?.classList.replace("fa-eye", "fa-eye-slash");
            toggleIncludeBtn.title = "Include Section in Compilation";
            showToast("Section excluded from compilation", "info");
          } else {
            toggleIncludeBtn.classList.remove("excluded");
            toggleIncludeBtn
              .querySelector("i")
              ?.classList.replace("fa-eye-slash", "fa-eye");
            toggleIncludeBtn.title = "Exclude Section from Compilation";
            showToast("Section included in compilation", "info");
          }
        } else {
          showToast(
            `Failed to toggle section: ${data.error || "Unknown error"}`,
            "error",
          );
        }
      } catch (error) {
        console.error("[Writer] Error toggling section:", error);
        showToast("Failed to toggle section state", "error");
      }
    });
  }

  // Move Section Up Button
  if (moveUpBtn) {
    moveUpBtn.addEventListener("click", async () => {
      const currentSection = state.currentSection;
      if (!currentSection) {
        showToast("No section selected", "error");
        return;
      }

      try {
        const response = await fetch(
          `/writer/api/project/${config.projectId}/section/${encodeURIComponent(currentSection)}/move-up/`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCsrfToken(),
            },
          },
        );

        const data = await response.json();

        if (response.ok && data.success) {
          showToast("Section moved up", "success");

          // Refresh section dropdown to show new order
          const docType = state.currentDocType || "manuscript";
          await populateSectionDropdownDirect(
            docType,
            null,
            undefined, // compilationManager not accessible in nested closure
            state,
          );
        } else {
          showToast(
            `Failed to move section: ${data.error || "Cannot move section up"}`,
            "info",
          );
        }
      } catch (error) {
        console.error("[Writer] Error moving section up:", error);
        showToast("Failed to move section", "error");
      }
    });
  }

  // Move Section Down Button
  if (moveDownBtn) {
    moveDownBtn.addEventListener("click", async () => {
      const currentSection = state.currentSection;
      if (!currentSection) {
        showToast("No section selected", "error");
        return;
      }

      try {
        const response = await fetch(
          `/writer/api/project/${config.projectId}/section/${encodeURIComponent(currentSection)}/move-down/`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCsrfToken(),
            },
          },
        );

        const data = await response.json();

        if (response.ok && data.success) {
          showToast("Section moved down", "success");

          // Refresh section dropdown to show new order
          const docType = state.currentDocType || "manuscript";
          await populateSectionDropdownDirect(
            docType,
            null,
            undefined, // compilationManager not accessible in nested closure
            state,
          );
        } else {
          showToast(
            `Failed to move section: ${data.error || "Cannot move section down"}`,
            "info",
          );
        }
      } catch (error) {
        console.error("[Writer] Error moving section down:", error);
        showToast("Failed to move section", "error");
      }
    });
  }

  console.log("[Writer] Section management buttons initialized");
}
