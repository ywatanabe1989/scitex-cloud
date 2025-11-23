/**
 * Section Dropdown UI Management
 * Handles the custom section dropdown interface for navigating and managing sections
 *
 * This module provides:
 * - Section dropdown population and rendering
 * - Section visibility toggling (exclude/include)
 * - Document type switching
 * - Dropdown-to-section synchronization
 */

import { showToast } from "./ui.js";
import { getCsrfToken } from "@/utils/csrf.js";
import { getWriterConfig } from "../helpers.js";
import { setupDragAndDrop } from "../modules/index.js";
import { statePersistence } from "../modules/state-persistence.js";
import type { CompilationManager } from "../modules/index.js";

console.log(
  "[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/utils/section-dropdown.ts loaded",
);

/**
 * Populate the custom section dropdown with sections from the API
 *
 * @param docType - Document type: "manuscript", "supplementary", "revision", or "shared"
 * @param onFileSelectCallback - Callback when a section is selected
 * @param compilationManager - Compilation manager instance for compile actions
 * @param state - Application state
 */
export async function populateSectionDropdownDirect(
  docType: string = "manuscript",
  onFileSelectCallback:
    | ((sectionId: string, sectionName: string) => void)
    | null = null,
  compilationManager?: CompilationManager,
  state?: any,
): Promise<void> {
  console.log("[Writer] Populating custom section dropdown for:", docType);

  const dropdownContainer = document.getElementById(
    "section-selector-dropdown",
  );
  const toggleBtn = document.getElementById("section-selector-toggle");
  const selectorText = document.getElementById("section-selector-text");

  if (!dropdownContainer || !toggleBtn || !selectorText) {
    console.warn("[Writer] Custom section dropdown elements not found");
    console.log("[Writer] dropdownContainer:", dropdownContainer);
    console.log("[Writer] toggleBtn:", toggleBtn);
    console.log("[Writer] selectorText:", selectorText);
    return;
  }

  console.log("[Writer] Custom dropdown elements found, setting up...");

  // Always setup the toggle listener first (even if fetch fails)
  if (!toggleBtn.dataset.listenerAttached) {
    toggleBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const isVisible = dropdownContainer.style.display !== "none";
      dropdownContainer.style.display = isVisible ? "none" : "flex";
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", (e) => {
      if (
        !toggleBtn.contains(e.target as Node) &&
        !dropdownContainer.contains(e.target as Node)
      ) {
        dropdownContainer.style.display = "none";
      }
    });

    toggleBtn.dataset.listenerAttached = "true";
    console.log("[Writer] Section selector toggle listener attached");
  }

  try {
    const response = await fetch("/writer/api/sections-config/");
    const data = await response.json();

    if (!data.success || !data.hierarchy) {
      console.error("[Writer] Failed to load sections hierarchy");
      console.error("[Writer] API response:", data);

      // Fallback: Show error in dropdown
      dropdownContainer.innerHTML = `
                <div style="padding: 16px; text-align: center; color: var(--color-fg-muted);">
                    <i class="fas fa-exclamation-triangle" style="margin-bottom: 8px; font-size: 24px;"></i>
                    <div>Failed to load sections</div>
                    <div style="font-size: 0.75rem; margin-top: 4px;">Check console for details</div>
                </div>
            `;
      selectorText.textContent = "Error loading sections";
      return;
    }

    const hierarchy = data.hierarchy;
    let sections: any[] = [];

    console.log("[Writer] Hierarchy received:", hierarchy);
    console.log("[Writer] Looking for docType:", docType);

    if (docType === "shared" && hierarchy.shared) {
      sections = hierarchy.shared.sections;
    } else if (docType === "manuscript" && hierarchy.manuscript) {
      sections = hierarchy.manuscript.sections;
    } else if (docType === "supplementary" && hierarchy.supplementary) {
      sections = hierarchy.supplementary.sections;
    } else if (docType === "revision" && hierarchy.revision) {
      sections = hierarchy.revision.sections;
    }

    console.log("[Writer] Sections extracted:", sections);
    console.log("[Writer] Sections count:", sections.length);

    if (sections.length === 0) {
      console.warn("[Writer] No sections found for document type:", docType);
      selectorText.textContent = "No sections found";
      return;
    }

    // Separate regular sections from footer items (compiled PDFs, New Section)
    let regularSectionsHtml = "";
    let footerSectionsHtml = "";

    sections.forEach((section: any, index: number) => {
      const isExcluded = section.excluded === true;
      const isOptional = section.optional === true;
      const isViewOnly = section.view_only === true;
      const isCompiledPdf = section.name === "compiled_pdf";
      const sectionLabel = section.label;

      // Don't show toggle for view-only sections (like compiled_pdf)
      const showToggle = !isViewOnly && (isOptional || isExcluded);

      // Generate file path for the section
      const username =
        (window as any).WRITER_CONFIG?.projectOwner || "ywatanabe";
      const projectSlug =
        (window as any).WRITER_CONFIG?.projectSlug || "default-project";
      // Use the path from backend if available, otherwise construct default path
      let filePath = "";
      if (section.path) {
        // Backend provides the correct path like "01_manuscript/contents/abstract.tex"
        filePath = `/${username}/${projectSlug}/blob/scitex/writer/${section.path}`;
      } else {
        // Fallback for sections without explicit path
        const sectionPath = section.id.replace(`${docType}/`, "");
        const docDirMap: Record<string, string> = {
          manuscript: "01_manuscript",
          supplementary: "02_supplementary",
          revision: "03_revision",
        };
        const docDir = docDirMap[docType] || `01_${docType}`;
        filePath = `/${username}/${projectSlug}/blob/scitex/writer/${docDir}/contents/${sectionPath}.tex`;
      }

      const itemHtml = `
                <div class="section-item ${isExcluded ? "excluded" : ""} section-item-with-actions"
                     data-section-id="${section.id}"
                     data-index="${index}"
                     data-optional="${isOptional}"
                     draggable="${!isCompiledPdf}"
                     title="${isCompiledPdf ? "View " + sectionLabel : "Switch to " + sectionLabel}">
                    <span class="section-drag-handle" style="${isCompiledPdf ? "visibility: hidden;" : ""}" title="Drag to reorder">⋮⋮</span>
                    ${!isCompiledPdf ? `<span class="section-page-number" style="color: var(--color-fg-muted); font-size: 0.75rem; min-width: 20px;">${index + 1}</span>` : ""}
                    <span class="section-item-name">${sectionLabel}</span>
                    ${
                      showToggle
                        ? `
                        <label class="ios-toggle" data-action="toggle-visibility" title="${isExcluded ? "Include in compilation" : "Exclude from compilation"}">
                            <input type="checkbox" ${!isExcluded ? "checked" : ""}>
                            <span class="ios-toggle-slider"></span>
                        </label>
                    `
                        : ""
                    }
                    <div class="section-item-actions">
                        ${
                          isCompiledPdf
                            ? `
                            <button class="btn btn-xs btn-outline-secondary" data-action="compile-full" title="Compile ${sectionLabel} PDF" onclick="event.stopPropagation();">
                                <i class="fas fa-file-pdf"></i>
                            </button>
                        `
                            : ""
                        }
                        <a href="${filePath}" class="btn btn-xs btn-outline-secondary" title="Go to ${sectionLabel} file" onclick="event.stopPropagation();" target="_blank">
                            <i class="fas fa-folder-open"></i>
                        </a>
                        <button class="btn btn-xs btn-outline-secondary" data-action="download-section" title="Download ${sectionLabel} PDF" onclick="event.stopPropagation();">
                            <i class="fas fa-download"></i>
                        </button>
                    </div>
                </div>
            `;

      // Separate compiled sections to footer
      if (isCompiledPdf) {
        footerSectionsHtml += itemHtml;
      } else {
        regularSectionsHtml += itemHtml;
      }
    });

    // Build final HTML with scrollable sections + fixed footer
    const html = `
            <div class="section-items-scrollable">
                ${regularSectionsHtml}
            </div>
            <div class="section-items-footer">
                <div class="section-divider"></div>
                ${footerSectionsHtml}
                <div class="section-divider"></div>
                <div class="section-action-item" data-action="new-section">
                    <i class="fas fa-plus"></i>
                    <span>Add New Section</span>
                </div>
            </div>
        `;

    dropdownContainer.innerHTML = html;
    console.log(
      "[Writer] Custom dropdown populated with",
      sections.length,
      "sections",
    );

    // Setup section item clicks
    dropdownContainer.querySelectorAll(".section-item").forEach((item) => {
      const sectionItem = item as HTMLElement;

      // Setup toggle switch change event
      const toggleCheckbox = sectionItem.querySelector(
        '.section-item-toggle input[type="checkbox"]',
      ) as HTMLInputElement;
      if (toggleCheckbox) {
        toggleCheckbox.addEventListener("change", async (e) => {
          e.stopPropagation();
          const sectionId = sectionItem.dataset.sectionId;
          if (sectionId) {
            await toggleSectionVisibility(sectionId, sectionItem);
          }
        });
      }

      // Setup action buttons (compile/download for FULL MANUSCRIPT)
      const compileBtn = sectionItem.querySelector(
        '[data-action="compile-full"]',
      );
      if (compileBtn) {
        compileBtn.addEventListener("click", async (e) => {
          e.stopPropagation();

          // Extract doc type from section ID (e.g., "manuscript/compiled_pdf" -> "manuscript")
          const sectionId = sectionItem.dataset.sectionId;
          let docTypeToCompile = "manuscript"; // default

          if (sectionId && sectionId.includes("/")) {
            const parts = sectionId.split("/");
            docTypeToCompile = parts[0]; // Get category (manuscript, supplementary, revision)
          }

          console.log(
            "[Writer] Compile button clicked for section:",
            sectionId,
            "docType:",
            docTypeToCompile,
          );

          // Call compilation with correct doc type
          if (compilationManager && state) {
            // Import handleCompileFull dynamically to avoid circular dependency
            const { handleCompileFull } = await import("../index.js");
            await handleCompileFull(
              compilationManager,
              state,
              docTypeToCompile,
            );
          } else {
            console.error("[Writer] compilationManager or state not available");
            showToast("Compilation manager not initialized", "error");
          }

          dropdownContainer.style.display = "none";
        });
      }

      const downloadBtn = sectionItem.querySelector(
        '[data-action="download-section"]',
      );
      if (downloadBtn) {
        downloadBtn.addEventListener("click", async (e) => {
          e.stopPropagation();
          const sectionId = sectionItem.dataset.sectionId;
          const sectionLabel =
            sectionItem.querySelector(".section-item-name")?.textContent ||
            "section";
          if (sectionId) {
            // Import handleDownloadSectionPDF dynamically to avoid circular dependency
            const { handleDownloadSectionPDF } = await import("../writer/index.js");
            handleDownloadSectionPDF(sectionId, sectionLabel);
          }
          dropdownContainer.style.display = "none";
        });
      }

      // Setup section selection (on item click, but not on toggle/actions)
      sectionItem.addEventListener("click", (e) => {
        const target = e.target as HTMLElement;

        // Ignore clicks on toggle switch or action buttons
        if (
          target.closest('[data-action="toggle-visibility"]') ||
          target.closest('[data-action="compile-full"]') ||
          target.closest('[data-action="download-section"]')
        ) {
          return;
        }

        // Handle section selection
        const sectionId = sectionItem.dataset.sectionId;
        const sectionName =
          sectionItem.querySelector(".section-item-name")?.textContent || "";
        const sectionIndex = sectionItem.dataset.index;

        if (sectionId && onFileSelectCallback) {
          // Update active state
          dropdownContainer
            .querySelectorAll(".section-item")
            .forEach((si) => si.classList.remove("active"));
          sectionItem.classList.add("active");

          // Update button text with page number
          const pageNum = sectionIndex ? parseInt(sectionIndex) + 1 : "";
          selectorText.textContent = pageNum ? `${pageNum}. ${sectionName}` : sectionName;

          // Close dropdown
          dropdownContainer.style.display = "none";

          // Save selected section
          statePersistence.saveSection(sectionId);
          console.log("[Writer] Saved section to persistence:", sectionId);

          // Trigger callback
          onFileSelectCallback(sectionId, sectionName);
        }
      });
    });

    // Setup "New Section..." click
    const newSectionItem = dropdownContainer.querySelector(
      '[data-action="new-section"]',
    );
    if (newSectionItem) {
      newSectionItem.addEventListener("click", () => {
        // Open the add section modal directly
        const modalEl = document.getElementById("add-section-modal");
        if (modalEl) {
          const modal = new (window as any).bootstrap.Modal(modalEl);
          modal.show();
        }
        dropdownContainer.style.display = "none";
      });
    }

    // Setup drag and drop for section reordering
    setupDragAndDrop(dropdownContainer, sections);

    // Set initial selection - restore saved section or use first section
    if (sections.length > 0) {
      // Try to restore saved section
      const savedSectionId = statePersistence.getSavedSection();
      let selectedSection = sections[0];
      let selectedIndex = 0;

      if (savedSectionId) {
        const savedIndex = sections.findIndex((s: any) => s.id === savedSectionId);
        if (savedIndex >= 0) {
          selectedSection = sections[savedIndex];
          selectedIndex = savedIndex;
          console.log("[Writer] Restored saved section:", savedSectionId);
        }
      }

      const pageNum = selectedIndex + 1;
      selectorText.textContent = `${pageNum}. ${selectedSection.label}`;

      // Mark the correct section as active
      const sectionItems = dropdownContainer.querySelectorAll(".section-item");
      sectionItems.forEach((item, idx) => {
        if (idx === selectedIndex) {
          item.classList.add("active");
        }
      });

      // Auto-load selected section
      if (onFileSelectCallback) {
        console.log("[Writer] Auto-selecting section:", selectedSection.id);
        onFileSelectCallback(selectedSection.id, selectedSection.label);
      }
    }
  } catch (error) {
    console.error("[Writer] Error populating section dropdown:", error);
  }
}

/**
 * Synchronize dropdown selection with current section
 *
 * @param sectionId - Section ID to sync
 */
export function syncDropdownToSection(sectionId: string): void {
  const dropdown = document.getElementById(
    "texfile-selector",
  ) as HTMLSelectElement;
  if (dropdown) {
    dropdown.value = sectionId;
  }
}

/**
 * Handle document type switch - navigates to first section of new doc type
 *
 * @param editor - Writer editor instance
 * @param sectionsManager - Sections manager instance
 * @param state - Application state
 * @param newDocType - New document type to switch to
 */
export function handleDocTypeSwitch(
  editor: any,
  sectionsManager: any,
  state: any,
  newDocType: string,
): void {
  // Map of first section for each document type
  const firstSectionByDocType: { [key: string]: string } = {
    shared: "title", // Shared sections: title, authors, keywords, journal_name
    manuscript: "abstract",
    supplementary: "content",
    revision: "response",
  };

  const firstSection = firstSectionByDocType[newDocType] || "abstract";

  if (!firstSection) {
    console.warn(
      "[Writer] No sections available for document type:",
      newDocType,
    );
    console.log("[Writer] Keeping current section:", state.currentSection);
    // Don't switch sections if document type has no sections
    return;
  }

  // Switch to the first section of the new document type
  console.log("[Writer] Switching to", firstSection, "for", newDocType);
  // Import switchSection dynamically to avoid circular dependency
  import("../writer/index.js").then(({ switchSection }) => {
    switchSection(editor, sectionsManager, state, firstSection);
  });
}

/**
 * Toggle section visibility (exclude/include from compilation)
 *
 * @param sectionId - Section ID to toggle
 * @param sectionItem - DOM element of the section item
 */
export async function toggleSectionVisibility(
  sectionId: string,
  sectionItem: HTMLElement,
): Promise<void> {
  const config = getWriterConfig();
  if (!config.projectId) {
    showToast("No project selected", "error");
    return;
  }

  const isExcluded = sectionItem.classList.contains("excluded");
  const checkbox = sectionItem.querySelector(
    '.section-item-toggle input[type="checkbox"]',
  ) as HTMLInputElement;

  try {
    // Call API to toggle exclusion
    const response = await fetch(
      `/writer/api/project/${config.projectId}/section/${sectionId}/toggle-exclude/`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({
          excluded: !isExcluded, // Toggle the state
        }),
      },
    );

    const data = await response.json();

    if (response.ok && data.success) {
      // Update UI
      sectionItem.classList.toggle("excluded");
      if (checkbox) {
        checkbox.checked = !data.excluded; // Checkbox is checked when NOT excluded
      }

      const action = data.excluded ? "excluded from" : "included in";
      showToast(`Section ${action} compilation`, "success");

      console.log(
        "[Writer] Toggled visibility for section:",
        sectionId,
        "excluded:",
        data.excluded,
      );
    } else {
      showToast(
        `Failed to toggle section: ${data.error || "Unknown error"}`,
        "error",
      );
      // Revert checkbox state
      if (checkbox) {
        checkbox.checked = !checkbox.checked;
      }
    }
  } catch (error) {
    console.error("[Writer] Error toggling section visibility:", error);
    showToast("Failed to toggle section", "error");
    // Revert checkbox state
    if (checkbox) {
      checkbox.checked = !checkbox.checked;
    }
  }
}
