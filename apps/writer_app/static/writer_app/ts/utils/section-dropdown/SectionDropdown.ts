/**
 * Section Dropdown Main Class
 * Core interface for the custom section dropdown
 */

import { showToast } from "../ui.js";
import { getWriterConfig } from "../../helpers.js";
import { setupDragAndDrop } from "../../modules/index.js";
import { statePersistence } from "../../modules/state-persistence.js";
import type { CompilationManager } from "../../modules/index.js";
import { renderSectionDropdown } from "./rendering.js";
import { setupSectionEvents } from "./events.js";

console.log(
  "[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/utils/section-dropdown/SectionDropdown.ts loaded",
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

    // Render the dropdown HTML
    const html = renderSectionDropdown(sections, docType);
    dropdownContainer.innerHTML = html;
    console.log(
      "[Writer] Custom dropdown populated with",
      sections.length,
      "sections",
    );

    // Setup all event listeners
    setupSectionEvents(
      dropdownContainer,
      sections,
      onFileSelectCallback,
      compilationManager,
      state,
      selectorText,
    );

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
