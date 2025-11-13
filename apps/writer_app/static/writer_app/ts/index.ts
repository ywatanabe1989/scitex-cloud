/**
 * SciTeX Writer Application
 * Main entry point for the writer interface
 *
 * This module coordinates all writer modules:
 * - WriterEditor: CodeMirror editor management
 * - SectionsManager: Section and document structure management
 * - CompilationManager: LaTeX compilation and PDF management
 */

import {
  WriterEditor,
  EnhancedEditor,
  SectionsManager,
  CompilationManager,
  FileTreeManager,
  PDFPreviewManager,
  PanelResizer,
  EditorControls,
  CitationsPanel,
  statusLamp,
  compilationSettings,
} from "./modules/index.js";
import { PDFScrollZoomHandler } from "./modules/pdf-scroll-zoom.js";
import { statePersistence } from "./modules/state-persistence.js";
import { getCsrfToken } from "@/utils/csrf.js";
import { writerStorage } from "@/utils/storage.js";
import { getWriterConfig, createDefaultEditorState } from "./helpers.js";
import {
  SaveSectionsResponse,
  SectionReadResponse,
  validateSaveSectionsResponse,
  validateSectionReadResponse,
  isSaveSectionsResponse,
  isSectionReadResponse,
} from "./types/api-responses.js";

/**
 * Show toast notification
 */

console.log(
  "[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/index.ts loaded",
);
function showToast(message: string, _type: string = "info"): void {
  const fn = (window as any).showToast || ((msg: string) => console.log(msg));
  fn(message);
}

/**
 * Get user context string for logging
 */
function getUserContext(): string {
  const config = getWriterConfig();
  if (config.visitorUsername) {
    return `[${config.visitorUsername}]`;
  } else if (config.username) {
    return `[${config.username}]`;
  }
  return "[anonymous]";
}

// Initialize application
document.addEventListener("DOMContentLoaded", async () => {
  console.log("[Writer] Initializing application");

  const config = getWriterConfig();
  console.log("[Writer] Config:", config);

  // Check if workspace is initialized
  if (!config.writerInitialized && !config.isDemo) {
    console.log("[Writer] Workspace not initialized - skipping editor setup");
    setupWorkspaceInitialization(config);
    return;
  }

  // Initialize editor components (async to wait for Monaco)
  await initializeEditor(config);
});

/**
 * Setup workspace initialization button
 */
function setupWorkspaceInitialization(config: any): void {
  const initBtn = document.getElementById("init-writer-btn");
  if (!initBtn) return;

  // Setup project selector
  const repoSelector = document.getElementById(
    "repository-selector",
  ) as HTMLSelectElement;
  if (repoSelector) {
    repoSelector.addEventListener("change", (e) => {
      const target = e.target as HTMLSelectElement;
      const projectId = target.value;

      if (projectId) {
        // Redirect to the selected project's writer page
        window.location.href = `/writer/project/${projectId}/`;
      }
    });
  }

  initBtn.addEventListener("click", async (e) => {
    e.preventDefault();

    // Validate project exists
    if (!config.projectId) {
      showToast(
        "Error: No project selected. Please select or create a project first.",
        "error",
      );
      initBtn.removeAttribute("disabled");
      return;
    }

    initBtn.setAttribute("disabled", "true");
    initBtn.innerHTML =
      '<i class="fas fa-spinner fa-spin me-2"></i>Creating workspace...';

    try {
      const response = await fetch("/writer/api/initialize-workspace/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({
          project_id: config.projectId,
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        showToast("Workspace initialized successfully", "success");
        // Small delay before reload to let user see success message
        setTimeout(() => {
          window.location.reload();
        }, 1000);
      } else {
        showToast(
          "Failed to initialize workspace: " + (data.error || "Unknown error"),
          "error",
        );
        initBtn.removeAttribute("disabled");
        initBtn.innerHTML =
          '<i class="fas fa-rocket me-2"></i>Create Workspace';
      }
    } catch (error) {
      showToast(
        "Error: " + (error instanceof Error ? error.message : "Unknown error"),
        "error",
      );
      initBtn.removeAttribute("disabled");
      initBtn.innerHTML = '<i class="fas fa-rocket me-2"></i>Create Workspace';
    }
  });
}

/**
 * Wait for Monaco to load asynchronously
 */
async function waitForMonaco(maxWaitMs: number = 10000): Promise<boolean> {
  const startTime = Date.now();
  console.log("[Writer] Waiting for Monaco to load...");

  while (Date.now() - startTime < maxWaitMs) {
    if ((window as any).monacoLoaded && (window as any).monaco) {
      console.log("[Writer] Monaco loaded successfully");
      return true;
    }
    // Wait 100ms before checking again
    await new Promise((resolve) => setTimeout(resolve, 100));
  }

  console.warn(
    "[Writer] Monaco failed to load within timeout, will fallback to CodeMirror",
  );
  return false;
}

/**
 * Load .tex file content from server
 */
async function loadTexFile(filePath: string, editor: any): Promise<void> {
  console.log("[Writer] Loading .tex file:", filePath);

  const config = getWriterConfig();
  if (!config.projectId) {
    console.error("[Writer] Cannot load file: no project ID");
    showToast("Cannot load file: no project selected", "error");
    return;
  }

  try {
    const response = await fetch(
      `/writer/api/project/${config.projectId}/read-tex-file/?path=${encodeURIComponent(filePath)}`,
    );

    console.log("[Writer] File API response status:", response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(
        "[Writer] Failed to load file:",
        response.status,
        errorText,
      );
      showToast(`Failed to load file: ${response.statusText}`, "error");
      return;
    }

    const data = await response.json();
    console.log(
      "[Writer] File loaded successfully, length:",
      data.content?.length || 0,
    );

    if (data.success && data.content !== undefined) {
      editor.setContent(data.content);
      console.log("[Writer] File content set in editor");
      showToast(`Loaded: ${filePath}`, "success");
    } else {
      console.error("[Writer] Invalid response format:", data);
      showToast("Failed to load file: invalid response", "error");
    }
  } catch (error) {
    console.error("[Writer] Error loading file:", error);
    showToast(
      "Error loading file: " +
        (error instanceof Error ? error.message : "Unknown error"),
      "error",
    );
  }
}

/**
 * Populate section dropdown directly (fallback when FileTreeManager not available)
 */
async function populateSectionDropdownDirect(
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
        downloadBtn.addEventListener("click", (e) => {
          e.stopPropagation();
          const sectionId = sectionItem.dataset.sectionId;
          const sectionLabel =
            sectionItem.querySelector(".section-item-name")?.textContent ||
            "section";
          if (sectionId) {
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
 * Setup drag and drop for section reordering
 */
function setupDragAndDrop(container: HTMLElement, sections: any[]): void {
  let draggedItem: HTMLElement | null = null;
  let placeholder: HTMLElement | null = null;

  container.querySelectorAll(".section-item").forEach((item) => {
    const htmlItem = item as HTMLElement;

    // Drag start
    htmlItem.addEventListener("dragstart", (e) => {
      draggedItem = htmlItem;
      htmlItem.classList.add("dragging");
      e.dataTransfer!.effectAllowed = "move";
    });

    // Drag end
    htmlItem.addEventListener("dragend", () => {
      if (draggedItem) {
        draggedItem.classList.remove("dragging");
        draggedItem = null;
      }
      if (placeholder && placeholder.parentNode) {
        placeholder.parentNode.removeChild(placeholder);
        placeholder = null;
      }
    });

    // Drag over
    htmlItem.addEventListener("dragover", (e) => {
      e.preventDefault();
      if (!draggedItem || draggedItem === htmlItem) return;

      const rect = htmlItem.getBoundingClientRect();
      const midpoint = rect.top + rect.height / 2;
      const isAfter = e.clientY > midpoint;

      // Insert dragged item
      if (isAfter) {
        container.insertBefore(draggedItem, htmlItem.nextSibling);
      } else {
        container.insertBefore(draggedItem, htmlItem);
      }
    });

    // Drop
    htmlItem.addEventListener("drop", (e) => {
      e.preventDefault();
      if (draggedItem) {
        // Update order
        const newOrder: string[] = [];
        container.querySelectorAll(".section-item").forEach((si, idx) => {
          const sectionId = (si as HTMLElement).dataset.sectionId;
          if (sectionId) {
            newOrder.push(sectionId);
            (si as HTMLElement).dataset.index = idx.toString();
          }
        });

        console.log("[Writer] New section order:", newOrder);
        // Note: Order is saved automatically when sections are saved
      }
    });
  });
}

/**
 * Setup PDF scroll - prevent page scroll when hovering over PDF
 */
function setupPDFScrollPriority(): void {
  const textPreview = document.getElementById("text-preview");
  if (!textPreview) {
    console.warn("[PDFScroll] text-preview element not found");
    return;
  }

  console.log(
    "[PDFScroll] Setting up smart scroll: PDF priority when hovering",
  );

  // Prevent page scroll when mouse is over PDF area
  textPreview.addEventListener(
    "wheel",
    (e: WheelEvent) => {
      // Check if PDF is loaded (iframe or embed)
      const pdfElement = textPreview.querySelector(
        'iframe[type="application/pdf"], embed[type="application/pdf"]',
      );
      if (pdfElement) {
        // PDF is loaded - prevent page scroll, let PDF viewer handle it
        e.stopPropagation();
        console.log(
          "[PDFScroll] Scroll over PDF - preventing page scroll (PDF handles internally)",
        );
      }
    },
    { passive: true, capture: true },
  );

  // Reset scroll position to top when PDF content is loaded
  const observer = new MutationObserver(() => {
    const pdfContainer = textPreview.querySelector(".pdf-preview-container");
    if (pdfContainer) {
      console.log("[PDFScroll] PDF container detected");
      textPreview.scrollTop = 0;

      const pdfViewer = textPreview.querySelector(
        ".pdf-preview-viewer",
      ) as HTMLElement;
      if (pdfViewer) {
        pdfViewer.scrollTop = 0;
      }

      const pdfElement = pdfContainer.querySelector(
        'iframe[type="application/pdf"], embed[type="application/pdf"]',
      );
      if (pdfElement) {
        console.log("[PDFScroll] PDF loaded - smart scrolling enabled");
      }
    }
  });

  observer.observe(textPreview, { childList: true, subtree: true });

  console.log("[PDFScroll] Smart scroll setup complete");
}

/**
 * Initialize editor and its components
 */
async function initializeEditor(config: any): Promise<void> {
  console.log("[Writer] Setting up editor components");

  // Wait for Monaco to load if attempting to use it
  const monacoReady = await waitForMonaco();

  // Initialize editor (try Monaco first if ready, fallback to CodeMirror)
  let editor: any = null;
  try {
    editor = new EnhancedEditor({
      elementId: "latex-editor-textarea",
      mode: "text/x-latex",
      theme: "default",
      useMonaco: monacoReady,
    });
  } catch (error) {
    console.error(
      "[Writer] Failed to initialize enhanced editor, trying basic editor:",
      error,
    );
    try {
      editor = new WriterEditor({
        elementId: "latex-editor-textarea",
        mode: "text/x-latex",
        theme: "default",
      });
    } catch (fallbackError) {
      console.error("[Writer] Failed to initialize any editor:", fallbackError);
      showToast("Failed to initialize editor", "error");
      return;
    }
  }

  // Initialize sections manager
  const sectionsManager = new SectionsManager();

  // Initialize compilation manager
  const compilationManager = new CompilationManager("");

  // Initialize AI2 prompt generator (disabled until generate_ai2_prompt.py is implemented)
  // const { initializeAI2Prompt } = await import('./modules/ai2-prompt.js');
  // initializeAI2Prompt(config.projectId);

  // Setup state management
  const state = createDefaultEditorState(config);

  // Initialize PDF preview manager
  const pdfPreviewManager = new PDFPreviewManager({
    containerId: "text-preview",
    projectId: config.projectId || 0,
    manuscriptTitle: config.manuscriptTitle || "Untitled",
    author: config.username || "",
    autoCompile: false, // Disabled - preview shows full manuscript PDF only
    compileDelay: 2000, // 2 seconds delay for live preview
    apiBaseUrl: "",
    docType: state.currentDocType || "manuscript",
  });

  // Set module-level reference for access from other functions
  modulePdfPreviewManager = pdfPreviewManager;

  // Initialize PDF scroll and zoom handler
  const pdfScrollZoomHandler = new PDFScrollZoomHandler({
    containerId: "text-preview",
    minZoom: 50,
    maxZoom: 300,
    zoomStep: 10,
  });

  // Observe for PDF viewer changes and reinitialize zoom handler
  pdfScrollZoomHandler.observePDFViewer();

  // Setup PDF color mode toggle button - SIMPLE direct approach with debounce
  const colorModeBtn = document.getElementById("pdf-color-mode-btn");
  let isTogglingTheme = false;

  if (colorModeBtn) {
    colorModeBtn.addEventListener("click", () => {
      // Prevent rapid clicking
      if (isTogglingTheme) {
        console.log("[Writer] Theme toggle in progress, ignoring click");
        return;
      }

      isTogglingTheme = true;

      // Toggle color mode
      const newMode =
        pdfScrollZoomHandler.getColorMode() === "dark" ? "light" : "dark";
      console.log("[Writer] PDF color mode switching to:", newMode);

      // Update handler state and button
      pdfScrollZoomHandler.setColorMode(newMode);

      // Immediately switch PDF display (pass content for compilation if needed)
      const currentContent = editor?.getContent();
      const currentSection = state?.currentSection;
      pdfPreviewManager.setColorMode(newMode, currentContent, currentSection);

      // Allow next toggle after short delay
      setTimeout(() => {
        isTogglingTheme = false;
      }, 500);
    });
  }

  // Initialize panel resizer for draggable split view
  const panelResizer = new PanelResizer();
  if (!panelResizer.isInitialized()) {
    console.warn("[Writer] Panel resizer could not be initialized");
  }

  // Initialize citations panel
  const citationsPanel = new CitationsPanel();
  (window as any).citationsPanel = citationsPanel; // Make available globally
  console.log("[Writer] Citations panel initialized");

  // Initialize editor controls (font size, auto-preview, preview button)
  // @ts-ignore - editorControls is initialized and manages its own event listeners
  const editorControls = new EditorControls({
    pdfPreviewManager: pdfPreviewManager,
    compilationManager: compilationManager,
    editor: editor,
  });

  // Expose preview functionality globally
  (window as any).handlePreviewClick = function(): void {
    // Check current status
    const currentStatus = statusLamp.getPreviewStatus();

    if (currentStatus === "compiling") {
      // Stop compilation
      console.log("[Writer] Stopping preview compilation");
      if (pdfPreviewManager) {
        // Set status to idle/ready
        statusLamp.setPreviewStatus("idle");
      }
    } else {
      // Start compilation
      if (pdfPreviewManager) {
        const latexEditor = document.getElementById("latex-editor-textarea") as HTMLTextAreaElement;
        if (latexEditor && latexEditor.value.trim()) {
          console.log("[Writer] Triggering PDF preview compilation");
          pdfPreviewManager.compileQuick(latexEditor.value);
        }
      }
    }
  };

  // Expose full compile functionality globally
  (window as any).handleFullCompileClick = function(): void {
    // Check current status
    const currentStatus = statusLamp.getFullCompileStatus();

    if (currentStatus === "compiling") {
      // Stop compilation
      console.log("[Writer] Stopping full compilation");
      // Set status to idle/ready
      statusLamp.setFullCompileStatus("idle");
    } else {
      // Start compilation
      console.log("[Writer] Full compilation button clicked");
      handleCompileFull(compilationManager, state, "manuscript", true);
    }
  };

  // Setup auto-full-compilation feature (opt-in, debounced 15s)
  let autoFullCompileTimeout: ReturnType<typeof setTimeout> | null = null;
  const autoFullCompileCheckbox = document.getElementById(
    "auto-fullcompile-checkbox",
  ) as HTMLInputElement;

  if (autoFullCompileCheckbox) {
    // Load saved preference
    const savedAutoFull = localStorage.getItem("scitex-auto-fullcompile");
    autoFullCompileCheckbox.checked = savedAutoFull === "true"; // Default off

    // Save preference on change
    autoFullCompileCheckbox.addEventListener("change", () => {
      localStorage.setItem(
        "scitex-auto-fullcompile",
        autoFullCompileCheckbox.checked.toString(),
      );
      console.log(
        "[Writer] Auto-full-compile:",
        autoFullCompileCheckbox.checked,
      );
    });

    // Setup debounced auto-full-compilation on editor changes
    if (editor && editor.editor) {
      editor.editor.onDidChangeModelContent(() => {
        if (!autoFullCompileCheckbox.checked) return;

        // Clear existing timeout
        if (autoFullCompileTimeout) {
          clearTimeout(autoFullCompileTimeout);
        }

        // Schedule full compilation after 15 seconds of inactivity
        autoFullCompileTimeout = setTimeout(() => {
          console.log("[Writer] Auto-full-compile triggered");
          handleCompileFull(compilationManager, state, "manuscript", false); // false = no modal for auto-compile
        }, 15000); // 15 seconds
      });
    }
  }

  // Define shared section/file selection callback
  const onFileSelectHandler = (
    sectionId: string,
    sectionName: string,
  ): void => {
    console.log(
      "[Writer] File/section selected:",
      sectionName,
      "ID:",
      sectionId,
    );

    // Check if this is a known section ID pattern or a file path
    // Section IDs follow: {docType}/{sectionName}
    // File paths have .tex extension or are in shared/* directories
    const sectionPattern =
      /^(manuscript|supplementary|revision)\/(abstract|introduction|methods|results|discussion|content|figures|tables|response|changes|compiled_pdf|compiled_tex)$/;
    const isKnownSection = sectionPattern.test(sectionId);

    if (isKnownSection) {
      // It's a section ID - switch section
      console.log(
        "[Writer] Detected section ID, switching section:",
        sectionId,
      );
      switchSection(editor, sectionsManager, state, sectionId);
    } else if (sectionId.endsWith(".tex")) {
      // It's a file path - load from disk
      console.log("[Writer] Detected .tex file, loading from disk:", sectionId);
      loadTexFile(sectionId, editor);
    } else {
      // Fallback: try as section first, then as file
      console.log("[Writer] Unknown ID format, trying as section:", sectionId);
      switchSection(editor, sectionsManager, state, sectionId);
    }
  };

  // Initialize file tree (including demo mode with projectId 0)
  if (config.projectId !== null && config.projectId !== undefined) {
    const fileTreeContainer = document.getElementById("tex-files-list");
    if (fileTreeContainer) {
      const fileTreeManager = new FileTreeManager({
        projectId: config.projectId,
        container: fileTreeContainer,
        texFileDropdownId: "texfile-selector",
        onFileSelect: onFileSelectHandler,
      });

      // Restore saved doctype
      const savedDoctype = statePersistence.getSavedDoctype();
      const docTypeSelector = document.getElementById(
        "doctype-selector",
      ) as HTMLSelectElement;
      if (docTypeSelector && savedDoctype) {
        docTypeSelector.value = savedDoctype;
        console.log("[Writer] Restored saved doctype:", savedDoctype);
      }

      // Load file tree
      fileTreeManager.load().catch((error) => {
        console.warn("[Writer] Failed to load file tree:", error);
      });

      // Setup refresh button
      const refreshBtn = document.getElementById("refresh-files-btn");
      if (refreshBtn) {
        refreshBtn.addEventListener("click", () => {
          fileTreeManager.refresh();
        });
      }

      // Listen to document type changes (with file tree)
      if (docTypeSelector) {
        docTypeSelector.addEventListener("change", (e) => {
          const newDocType = (e.target as HTMLSelectElement).value;
          console.log("[Writer] Document type changed to:", newDocType);
          if (editor && state.currentSection) {
            // Save current section before switching
            const currentContent = editor.getContent();
            sectionsManager.setContent(state.currentSection, currentContent);
            // Update state with new document type
            state.currentDocType = newDocType;
            // Save doctype to persistence
            statePersistence.saveDoctype(newDocType);
            console.log("[Writer] Saved doctype to persistence:", newDocType);
            // Update section dropdown for the new document type
            fileTreeManager.updateForDocType(newDocType);
            // Update PDF preview manager to use the new document type
            pdfPreviewManager.setDocType(newDocType);
            // Switch to first section of the new document type
            handleDocTypeSwitch(editor, sectionsManager, state, newDocType);
          }
        });
      }
    } else {
      // No file tree container found - populate dropdown directly
      console.log(
        "[Writer] No file tree container, populating dropdown directly",
      );

      // Restore saved doctype
      const savedDoctype = statePersistence.getSavedDoctype();
      const initialDoctype = savedDoctype || "manuscript";

      // Set doctype selector to saved value
      const docTypeSelector = document.getElementById(
        "doctype-selector",
      ) as HTMLSelectElement;
      if (docTypeSelector && savedDoctype) {
        docTypeSelector.value = savedDoctype;
        console.log("[Writer] Restored saved doctype:", savedDoctype);
      }

      populateSectionDropdownDirect(
        initialDoctype,
        onFileSelectHandler,
        compilationManager,
        state,
      );

      // Listen to document type changes (without file tree)
      if (docTypeSelector) {
        docTypeSelector.addEventListener("change", async (e) => {
          const newDocType = (e.target as HTMLSelectElement).value;
          console.log(
            "[Writer] Document type changed to:",
            newDocType,
            "- updating section dropdown",
          );

          // Save current section content before switching
          if (editor && state.currentSection) {
            const currentContent = editor.getContent();
            sectionsManager.setContent(state.currentSection, currentContent);
          }

          // Update state
          state.currentDocType = newDocType;

          // Save doctype to persistence
          statePersistence.saveDoctype(newDocType);
          console.log("[Writer] Saved doctype to persistence:", newDocType);

          // Update PDF preview manager doc type
          if (pdfPreviewManager) {
            pdfPreviewManager.setDocType(newDocType);
          }

          // Repopulate section dropdown for new doc_type
          await populateSectionDropdownDirect(
            newDocType,
            onFileSelectHandler,
            compilationManager,
            state,
          );
        });
        console.log("[Writer] Doc type change handler attached");
      }
    }
  } else {
    // No projectId - still need to populate dropdown
    console.log("[Writer] No project, populating dropdown for demo mode");
    populateSectionDropdownDirect(
      "manuscript",
      onFileSelectHandler,
      compilationManager,
      state,
    );
  }

  // Setup event listeners with error handling
  try {
    if (editor) {
      setupEditorListeners(
        editor,
        sectionsManager,
        compilationManager,
        state,
        pdfPreviewManager,
      );
      setupSectionListeners(sectionsManager, editor, state, writerStorage);
    }
    setupCompilationListeners(compilationManager, config);
    setupThemeListener(editor);
    setupKeybindingListener(editor);
    setupSidebarButtons(config);
    setupSectionManagementButtons(config, state, sectionsManager, editor);
  } catch (error) {
    console.error("[Writer] Error setting up event listeners:", error);
    // Continue initialization despite errors
  }

  // Setup scroll priority: PDF scrolling takes priority over page scrolling
  setupPDFScrollPriority();

  // Display PDF preview placeholder
  pdfPreviewManager.displayPlaceholder();

  // Load initial content
  const currentSection = state.currentSection || "manuscript/compiled_pdf";
  const content = sectionsManager.getContent(currentSection);
  if (editor && content) {
    // Use setContentForSection to restore cursor position and auto-focus
    if (typeof (editor as any).setContentForSection === "function") {
      (editor as any).setContentForSection(currentSection, content);
    } else {
      editor.setContent(content);
    }
  }

  // Show only split view - all views are split by default in HTML
  document.querySelectorAll(".editor-view").forEach((view) => {
    view.classList.add("active");
  });

  console.log("[Writer] Editor initialized successfully");
  console.log(
    "[Writer] Using editor type:",
    editor?.getEditorType?.() || "CodeMirror",
  );

  // Restore saved pane state with increased delay to ensure all DOM elements are ready
  setTimeout(() => {
    try {
      const savedPane = statePersistence.getSavedActivePane();
      console.log("[Writer] === PANE RESTORATION START ===");
      console.log("[Writer] Saved pane value:", savedPane);
      console.log("[Writer] Saved pane type:", typeof savedPane);

      if (savedPane === "citations") {
        console.log("[Writer] Switching to citations pane...");
        switchRightPanel("citations");
        console.log("[Writer] ✓ Restored citations pane from saved state");
      } else if (savedPane === "pdf") {
        console.log("[Writer] Switching to PDF pane...");
        switchRightPanel("pdf");
        console.log("[Writer] ✓ Restored PDF pane from saved state");
      } else {
        console.log("[Writer] No saved pane state found, using default (PDF)");
      }
      console.log("[Writer] === PANE RESTORATION END ===");
    } catch (error) {
      console.error("[Writer] Error during pane restoration:", error);
    }
  }, 300); // Increased delay to ensure all initialization is complete
}

/**
 * Sync dropdown selection with current section
 */
function syncDropdownToSection(sectionId: string): void {
  const dropdown = document.getElementById(
    "texfile-selector",
  ) as HTMLSelectElement;
  if (dropdown) {
    dropdown.value = sectionId;
  }
}

/**
 * Handle document type switch
 */
function handleDocTypeSwitch(
  editor: WriterEditor,
  sectionsManager: SectionsManager,
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
  switchSection(editor, sectionsManager, state, firstSection);
}

/**
 * Setup editor event listeners
 */
function setupEditorListeners(
  editor: WriterEditor | null,
  sectionsManager: SectionsManager,
  compilationManager: CompilationManager,
  state: any,
  pdfPreviewManager?: PDFPreviewManager,
): void {
  if (!editor) return;
  // Track changes
  editor.onChange((content: string, wordCount: number) => {
    const currentSection = state.currentSection;

    // Skip tracking changes for compiled sections (read-only)
    const isCompiledSection =
      currentSection &&
      (currentSection.endsWith("/compiled_pdf") ||
        currentSection.endsWith("/compiled_tex"));

    if (isCompiledSection) {
      console.log(
        "[Writer] Skipping change tracking for compiled section:",
        currentSection,
      );
      return;
    }

    sectionsManager.setContent(currentSection, content);
    state.unsavedSections.add(currentSection);

    // Update word count display
    updateWordCountDisplay(currentSection, wordCount);

    // Schedule auto-save
    scheduleSave(editor, sectionsManager, state);

    // Schedule auto-compile for live PDF preview (skip for compiled sections)
    const isCompiledForPreview =
      currentSection.endsWith("/compiled_pdf") ||
      currentSection.endsWith("/compiled_tex");
    if (pdfPreviewManager && !isCompiledForPreview) {
      scheduleAutoCompile(pdfPreviewManager, content, currentSection);
    }
  });

  // Keyboard shortcuts
  document.addEventListener("keydown", (e) => {
    // Ctrl/Cmd + S to save
    if ((e.ctrlKey || e.metaKey) && e.key === "s") {
      e.preventDefault();
      saveSections(sectionsManager, state);
    }

    // Alt + Enter to compile preview (quick)
    if (e.altKey && !e.shiftKey && e.key === "Enter") {
      e.preventDefault();
      const handlePreviewClick = (window as any).handlePreviewClick;
      if (handlePreviewClick) {
        handlePreviewClick();
        console.log("[Writer] Preview compilation triggered via Alt+Enter");
      }
    }

    // Alt + Shift + Enter to compile full manuscript
    if (e.altKey && e.shiftKey && e.key === "Enter") {
      e.preventDefault();
      handleCompileFull(compilationManager, state, "manuscript", true);
      console.log("[Writer] Full compilation triggered via Alt+Shift+Enter");
    }

    // Ctrl/Cmd + Shift + X to compile (legacy)
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === "X") {
      e.preventDefault();
      handleCompile(
        editor,
        sectionsManager,
        compilationManager,
        state,
        pdfPreviewManager,
      );
    }

    // Ctrl+K to focus citation search (only when citations pane visible)
    if (e.ctrlKey && e.key === "k") {
      const citationsView = document.getElementById("citations-view");
      const searchInput = document.getElementById(
        "citations-search-toolbar",
      ) as HTMLInputElement;

      if (
        citationsView &&
        citationsView.style.display !== "none" &&
        searchInput
      ) {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
        console.log("[Writer] Citation search focused via Ctrl+K");
      }
    }

    // Escape to unfocus citation search
    if (e.key === "Escape") {
      const searchInput = document.getElementById(
        "citations-search-toolbar",
      ) as HTMLInputElement;
      if (searchInput && document.activeElement === searchInput) {
        e.preventDefault();
        searchInput.blur();
        console.log("[Writer] Citation search unfocused via Escape");
      }
    }
  });

  // Setup save button (Ctrl+S keyboard shortcut is handled below)
  // Note: No explicit save button in toolbar - use keyboard shortcut

  // Setup undo/redo buttons
  const undoBtn = document.getElementById("undo-btn");
  if (undoBtn && editor) {
    undoBtn.addEventListener("click", () => {
      editor.undo();
    });
  }

  const redoBtn = document.getElementById("redo-btn");
  if (redoBtn && editor) {
    redoBtn.addEventListener("click", () => {
      editor.redo();
    });
  }

  // Setup compile button (full manuscript compilation)
  const compileBtn = document.getElementById("compile-btn-toolbar");
  if (compileBtn) {
    compileBtn.addEventListener("click", () => {
      handleCompileFull(compilationManager, state);
    });
  }

  // Setup git commit button
  const commitBtn = document.getElementById("git-commit-btn");
  if (commitBtn) {
    commitBtn.addEventListener("click", () => {
      showCommitModal(state);
    });
  }

  // Setup confirm commit button (in modal)
  const confirmCommitBtn = document.getElementById("confirm-commit-btn");
  if (confirmCommitBtn) {
    confirmCommitBtn.addEventListener("click", async () => {
      await handleGitCommit(state);
    });
  }

  // Setup minimize compilation output button
  const minimizeBtn = document.getElementById("minimize-compilation-output");
  if (minimizeBtn) {
    minimizeBtn.addEventListener("click", () => {
      minimizeCompilationOutput();
    });
  }

  // Setup close compilation output button
  const closeBtn = document.getElementById("close-compilation-output");
  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      hideCompilationProgress();
      // Also hide minimized status
      const minimizedStatus = document.getElementById(
        "minimized-compilation-status",
      );
      if (minimizedStatus) {
        minimizedStatus.style.display = "none";
      }
    });
  }

  // Setup minimized compilation status button (click to restore)
  const minimizedStatus = document.getElementById(
    "minimized-compilation-status",
  );
  if (minimizedStatus) {
    minimizedStatus.addEventListener("click", () => {
      restoreCompilationOutput();
    });
  }

  // Initialize status lamps with default state
  // Preview lamp: idle by default
  statusLamp.setPreviewStatus("idle");
  // Full compile lamp: idle by default
  statusLamp.setFullCompileStatus("idle");
  // Note: setSaveStatus removed as it's not implemented in StatusLampManager

  // Restore last compilation status from localStorage
  restoreCompilationStatus();
}

/**
 * Setup section listeners
 */
function setupSectionListeners(
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
 * Setup compilation listeners
 */
function setupCompilationListeners(
  compilationManager: CompilationManager,
  _config: any,
): void {
  compilationManager.onProgress((progress: number, status: string) => {
    const progressBar = document.getElementById("compilation-progress");
    if (progressBar) {
      (progressBar as HTMLInputElement).value = String(progress);
    }

    const statusText = document.getElementById("compilation-status");
    if (statusText) {
      statusText.textContent = status;
    }
  });

  compilationManager.onComplete((_jobId: string, pdfUrl: string) => {
    const showToast =
      (window as any).showToast || ((msg: string) => console.log(msg));
    showToast("Compilation completed successfully");
    if (pdfUrl) {
      openPDF(pdfUrl);
    }
  });

  compilationManager.onError((error: string) => {
    const showToast =
      (window as any).showToast || ((msg: string) => console.error(msg));
    showToast("Compilation error: " + error);
  });
}

/**
 * Get current global page theme (light or dark)
 */
function getPageTheme(): "light" | "dark" {
  const theme = document.documentElement.getAttribute("data-theme");
  return theme === "light" ? "light" : "dark";
}

/**
 * Filter theme dropdown options based on page theme
 */
function filterThemeOptions(): void {
  const themeSelector = document.getElementById(
    "theme-selector",
  ) as HTMLSelectElement;
  if (!themeSelector) return;

  const pageTheme = getPageTheme();
  const optgroups = themeSelector.querySelectorAll("optgroup");

  optgroups.forEach((optgroup) => {
    const label = optgroup.label.toLowerCase();
    const isLightGroup = label.includes("light");
    const isDarkGroup = label.includes("dark");

    // Show only matching theme group
    if (pageTheme === "light" && isLightGroup) {
      optgroup.style.display = "";
    } else if (pageTheme === "dark" && isDarkGroup) {
      optgroup.style.display = "";
    } else {
      optgroup.style.display = "none";
    }
  });

  // If current selected option is hidden, select first visible option
  const currentOption = themeSelector.options[themeSelector.selectedIndex];
  if (
    currentOption &&
    currentOption.parentElement instanceof HTMLOptGroupElement
  ) {
    if (currentOption.parentElement.style.display === "none") {
      // Find first visible option
      for (let i = 0; i < themeSelector.options.length; i++) {
        const option = themeSelector.options[i];
        if (
          option.parentElement instanceof HTMLOptGroupElement &&
          option.parentElement.style.display !== "none"
        ) {
          themeSelector.selectedIndex = i;
          // Trigger change to apply the new theme
          themeSelector.dispatchEvent(new Event("change"));
          break;
        }
      }
    }
  }
}

/**
 * Apply code editor theme to Monaco or CodeMirror
 */
function applyCodeEditorTheme(theme: string, editor: any): void {
  if (!editor) return;

  const editorType = editor.getEditorType
    ? editor.getEditorType()
    : "codemirror";

  if (editorType === "monaco" && editor.setTheme) {
    console.log("[Writer] Applying Monaco theme:", theme);
    editor.setTheme(theme);
  } else {
    // CodeMirror
    const cmEditor = (document.querySelector(".CodeMirror") as any)?.CodeMirror;
    if (cmEditor) {
      console.log("[Writer] Applying CodeMirror theme:", theme);
      cmEditor.setOption("theme", theme);
    }
  }
}

/**
 * Setup theme listener
 */
function setupThemeListener(editor: any): void {
  const themeSelector = document.getElementById(
    "theme-selector",
  ) as HTMLSelectElement;
  if (!themeSelector) return;

  // Initial filter based on page theme
  filterThemeOptions();

  // Load saved theme or use default
  const savedTheme = writerStorage.load("editor_theme") as string | null;
  if (savedTheme && typeof savedTheme === "string") {
    themeSelector.value = savedTheme;
    if (editor) {
      applyCodeEditorTheme(savedTheme, editor);
    }
  }

  // Listen for code editor theme changes
  themeSelector.addEventListener("change", () => {
    const theme = themeSelector.value;
    writerStorage.save("editor_theme", theme);

    console.log("[Writer] Code editor theme changed to:", theme);
    if (editor) {
      applyCodeEditorTheme(theme, editor);
    }
  });

  // Listen for global page theme changes
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (
        mutation.type === "attributes" &&
        mutation.attributeName === "data-theme"
      ) {
        console.log(
          "[Writer] Page theme changed, filtering code editor themes",
        );
        filterThemeOptions();
      }
    });
  });

  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-theme"],
  });
}

/**
 * Setup keybinding listener
 */
function setupKeybindingListener(editor: any): void {
  const keybindingSelector = document.getElementById(
    "keybinding-selector",
  ) as HTMLSelectElement;
  if (!keybindingSelector) return;

  // Load saved keybinding
  const savedKeybinding = writerStorage.load("editor_keybinding") as
    | string
    | null;
  if (savedKeybinding && typeof savedKeybinding === "string") {
    keybindingSelector.value = savedKeybinding;
    if (editor && editor.setKeyBinding) {
      editor.setKeyBinding(savedKeybinding);
    }
  }

  // Listen for keybinding changes
  keybindingSelector.addEventListener("change", () => {
    const keybinding = keybindingSelector.value;
    writerStorage.save("editor_keybinding", keybinding);

    console.log("[Writer] Keybinding changed to:", keybinding);
    if (editor && editor.setKeyBinding) {
      editor.setKeyBinding(keybinding);
    }
  });
}

/**
 * Module-level PDF preview manager (initialized in main)
 */
let modulePdfPreviewManager: PDFPreviewManager | null = null;

/**
 * Load section content from API
 */
let isLoadingContent: boolean = false; // Flag to prevent repeated auto-compile during content loading
async function loadSectionContent(
  editor: WriterEditor,
  sectionsManager: SectionsManager,
  _state: any,
  sectionId: string,
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
      isLoadingContent = true;
      sectionsManager.setContent(sectionId, data.content);

      // Use setContentForSection to restore cursor position
      if (typeof (editor as any).setContentForSection === "function") {
        (editor as any).setContentForSection(sectionId, data.content);
      } else {
        editor.setContent(data.content);
      }

      // Reset flag and trigger ONE initial preview
      setTimeout(() => {
        isLoadingContent = false;
        // Trigger initial preview for the loaded section (skip for compiled sections)
        const isCompiledSection =
          sectionId.endsWith("/compiled_pdf") ||
          sectionId.endsWith("/compiled_tex");
        if (modulePdfPreviewManager && !isCompiledSection) {
          console.log("[Writer] Triggering initial preview for:", sectionId);
          modulePdfPreviewManager.compileQuick(data.content, sectionId);
        }
      }, 100);
    } else {
      const errorMsg = data.error || "Unknown error loading section";
      console.error("[Writer] ✗ API Error:", errorMsg);
      throw new Error(errorMsg);
    }
  } catch (error) {
    console.error("[Writer] Error loading section content:", error);
    isLoadingContent = false; // Reset flag on error
    throw error; // Re-throw to let caller handle it
  }
}

/**
 * Switch to a section
 */
async function switchSection(
  editor: WriterEditor,
  sectionsManager: SectionsManager,
  state: any,
  sectionId: string,
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
      await loadSectionContent(editor, sectionsManager, state, compiledTexId);
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
    await loadSectionContent(editor, sectionsManager, state, sectionId);
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
function updateSectionUI(sectionId: string): void {
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
    clearTimeout(compileTimeout);
    loadCompiledPDF(sectionId);
  }
}

/**
 * Load compiled PDF for display (not quick preview)
 */
function loadCompiledPDF(sectionId: string): void {
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
 * Update the section title label to show current section name with file link
 */
function updateSectionTitleLabel(sectionId: string): void {
  const titleElement = document.getElementById("editor-section-title");
  if (!titleElement) return;

  const config = getWriterConfig();

  // Extract section info from sectionId (e.g., "manuscript/abstract")
  const parts = sectionId.split("/");
  const docType = parts[0];
  const sectionName = parts[parts.length - 1];

  // Capitalize and format the section name
  const formattedName = sectionName
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");

  // Build file path for link
  const docDirMap: Record<string, string> = {
    manuscript: "01_manuscript",
    supplementary: "02_supplementary",
    revision: "03_revision",
    shared: "shared",
  };

  let filePath = "";
  if (sectionName === "compiled_pdf" || sectionName === "compiled_tex") {
    // For compiled_pdf, link to the TEX file (since that's what shows in editor)
    // Compiled files are in the root of doc directory
    filePath = `scitex/writer/${docDirMap[docType]}/${docType}.tex`;
  } else {
    // Regular sections are in contents/
    const ext =
      sectionName === "bibliography" || sectionName === "references"
        ? "bib"
        : "tex";
    if (docType === "shared") {
      filePath = `scitex/writer/00_shared/${sectionName}.${ext}`;
    } else {
      filePath = `scitex/writer/${docDirMap[docType]}/contents/${sectionName}.${ext}`;
    }
  }

  // Create link to project browser
  const fileLink =
    config.username && config.projectSlug
      ? `/${config.username}/${config.projectSlug}/blob/${filePath}`
      : "";

  if (fileLink) {
    titleElement.innerHTML = `${formattedName} Source <a href="${fileLink}" target="_blank" style="font-size: 0.8em; opacity: 0.7;">📁</a>`;
  } else {
    titleElement.textContent = `${formattedName} Source`;
  }
}

/**
 * Update the PDF preview panel title to show current section with link
 */
function updatePDFPreviewTitle(sectionId: string): void {
  const titleElement = document.getElementById("preview-title");
  if (!titleElement) return;

  const config = getWriterConfig();

  // Extract section name from sectionId
  const parts = sectionId.split("/");
  const docType = parts[0];
  const sectionName = parts[parts.length - 1];

  // Capitalize and format
  const docTypeLabel = docType.charAt(0).toUpperCase() + docType.slice(1);
  const formattedName = sectionName
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");

  // Build PDF file link
  let pdfLink = "";
  if (sectionName === "compiled_pdf" && config.username && config.projectSlug) {
    // Link to compiled PDF
    const docDirMap: Record<string, string> = {
      manuscript: "01_manuscript",
      supplementary: "02_supplementary",
      revision: "03_revision",
    };
    pdfLink = `/${config.username}/${config.projectSlug}/blob/scitex/writer/${docDirMap[docType]}/${docType}.pdf`;
  } else if (config.username && config.projectSlug) {
    // Link to preview PDF
    pdfLink = `/${config.username}/${config.projectSlug}/blob/scitex/writer/preview_output/preview-${sectionName}.pdf`;
  }

  // Special case for compiled_pdf - don't add "PDF" twice
  let titleText = "";
  if (sectionName === "compiled_pdf") {
    titleText = `${docTypeLabel} PDF`;
  } else {
    titleText = `${docTypeLabel} ${formattedName} PDF`;
  }

  // Add link if available
  if (pdfLink) {
    titleElement.innerHTML = `${titleText} <a href="${pdfLink}" target="_blank" style="font-size: 0.8em; opacity: 0.7;">📁</a>`;
  } else {
    titleElement.textContent = titleText;
  }
}

/**
 * Update commit button state based on section type and user authentication
 * - Hides button for guest users (Visitor Mode)
 * - Disables button for read-only sections (keeps it visible to reduce surprise)
 */
function updateCommitButtonVisibility(sectionId: string): void {
  const commitBtn = document.getElementById(
    "git-commit-btn",
  ) as HTMLButtonElement;
  if (!commitBtn) return;

  const config = (window as any).WRITER_CONFIG;

  // Hide for guest users (projectId === 0 means demo/guest project)
  if (!config || config.projectId === 0) {
    commitBtn.style.display = "none";
    return;
  }

  // Always show button for authenticated users
  commitBtn.style.display = "";

  // Extract section name from sectionId (e.g., "manuscript/compiled_pdf" -> "compiled_pdf")
  const parts = sectionId.split("/");
  const sectionName = parts[parts.length - 1];

  // Disable button for read-only sections (but keep it visible)
  // compiled_pdf is the merged/compiled document
  // figures, tables, references are directories or view-only sections
  const readOnlySections = ["compiled_pdf", "figures", "tables", "references"];
  const isReadOnly = readOnlySections.includes(sectionName);

  if (isReadOnly) {
    commitBtn.disabled = true;
    commitBtn.title = "Cannot commit read-only sections";
  } else {
    commitBtn.disabled = false;
    commitBtn.title = "Create git commit for current changes";
  }
}

/**
 * Update word count display
 */
function updateWordCountDisplay(_section: string, count: number): void {
  const display = document.getElementById("current-word-count");
  if (display) {
    display.textContent = String(count);
  }
}

/**
 * Schedule auto-save
 */
let saveTimeout: ReturnType<typeof setTimeout>;
function scheduleSave(
  _editor: WriterEditor | null,
  sectionsManager: SectionsManager,
  state: any,
): void {
  clearTimeout(saveTimeout);
  saveTimeout = setTimeout(() => {
    saveSections(sectionsManager, state);
  }, 5000); // Auto-save after 5 seconds of inactivity
}

/**
 * Schedule auto-compile for live PDF preview
 */
let compileTimeout: ReturnType<typeof setTimeout>;
function scheduleAutoCompile(
  pdfPreviewManager: PDFPreviewManager | null,
  content: string,
  sectionId?: string,
): void {
  if (!pdfPreviewManager) return;

  // Skip auto-compile if we're just loading content (not user editing)
  if (isLoadingContent) {
    console.log("[Writer] Skipping auto-compile during content load");
    return;
  }

  // Clear existing timeout
  clearTimeout(compileTimeout);

  // Schedule compilation after user stops typing
  compileTimeout = setTimeout(() => {
    console.log(
      "[Writer] Auto-compiling for live preview, section:",
      sectionId,
    );
    // Pass section ID for section-specific preview
    pdfPreviewManager.compileQuick(content, sectionId);
  }, 2000); // Wait 2 seconds after user stops typing
}

/**
 * Save sections
 */
async function saveSections(
  sectionsManager: SectionsManager,
  state: any,
): Promise<void> {
  try {
    // Get project ID from page config
    const config = getWriterConfig();
    if (!config.projectId) {
      console.warn("[Writer] Cannot save sections: no project ID");
      return;
    }

    const allSections = sectionsManager.getAll(); // Returns Section[]

    // Build sections object with section IDs as keys
    const sections: Record<string, string> = {};
    for (const section of allSections) {
      const content = section.content || "";
      // Skip compiled sections (read-only, virtual sections)
      if (section.id && section.id.endsWith("/compiled_pdf")) {
        continue;
      }
      if (content.trim().length > 0 && section.id) {
        sections[section.id] = content; // Use section.id, not array index!
      }
    }

    if (Object.keys(sections).length === 0) {
      console.log("[Writer] No non-empty sections to save");
      return;
    }

    const userContext = getUserContext();
    console.log(
      `${userContext} [Writer] Saving ${Object.keys(sections).length} sections for ${state.currentDocType || "manuscript"}`,
    );

    const response = await fetch(
      `/writer/api/project/${config.projectId}/save-sections/`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({
          sections,
          doc_type: state.currentDocType || "manuscript",
        }),
      },
    );

    const data = await response.json();

    // Validate response structure
    if (!isSaveSectionsResponse(data)) {
      throw new Error("Invalid response format from server");
    }

    // Validate response data
    try {
      validateSaveSectionsResponse(data);
    } catch (validationError) {
      console.error("[Writer] Response validation failed:", validationError);
      throw new Error(
        `Invalid server response: ${validationError instanceof Error ? validationError.message : String(validationError)}`,
      );
    }

    if (data.success) {
      state.unsavedSections.clear();

      if (data.sections_saved === 0) {
        console.warn("[Writer] No sections were saved!");
        showToast("Warning: No sections were saved", "warning");
      } else {
        console.log(
          `[Writer] Sections saved: ${data.sections_saved} saved, ${data.sections_skipped} skipped`,
        );
        showToast(
          `Saved ${data.sections_saved} section${data.sections_saved > 1 ? "s" : ""}`,
          "success",
        );
      }
    } else {
      console.error("[Writer] Save failed:", data.message);
      if (data.errors && data.errors.length > 0) {
        console.error("[Writer] Errors:", data.errors);
      }
      if (data.error_details && Object.keys(data.error_details).length > 0) {
        console.error("[Writer] Detailed errors:", data.error_details);
      }
      showToast(`Failed to save sections: ${data.message}`, "error");
    }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    console.error("[Writer] Error saving sections:", error);
    showToast(`Error saving sections: ${errorMsg}`, "error");
    // Don't silently fail - show alert for critical errors
    if (error instanceof TypeError || error instanceof SyntaxError) {
      alert(
        `Critical error saving sections: ${errorMsg}\n\nPlease check the console for details.`,
      );
    }
  }
}

/**
 * Handle compilation
 */
/**
 * Show compilation options modal and return a promise with user's choices
 * Now using the merged compilation-settings-modal
 */
function showCompilationOptionsModal(
  docType: string = "manuscript",
): Promise<any> {
  return new Promise((resolve, reject) => {
    const modalElement = document.getElementById("compilation-settings-modal");
    if (!modalElement) {
      reject(new Error("Modal not found"));
      return;
    }

    // Update modal description for full compilation options
    const optionsDescription = modalElement.querySelector(".text-muted.small.mb-3");
    if (descriptionText) {
      const docTypeLabels: Record<string, string> = {
        manuscript: "manuscript",
        supplementary: "supplementary materials",
        revision: "revision",
      };
      const docLabel = docTypeLabels[docType] || docType;
      descriptionText.textContent = `Select compilation options for ${docLabel}:`;
    }

    // Show/hide option groups based on doc type and script capabilities
    const contentOptions = modalBody?.querySelectorAll(
      ".compilation-option-group",
    )[0] as HTMLElement;
    const figureProcessingOptions = modalBody?.querySelectorAll(
      ".compilation-option-group",
    )[1] as HTMLElement;
    const performanceOptions = modalBody?.querySelectorAll(
      ".compilation-option-group",
    )[2] as HTMLElement;
    const appearanceOptions = modalBody?.querySelectorAll(
      ".compilation-option-group",
    )[3] as HTMLElement;
    const advancedOptions = modalBody?.querySelectorAll(
      ".compilation-option-group",
    )[4] as HTMLElement;

    // Show/hide specific options within groups
    const diffOption = document.querySelector('[for="option-add-diff"]')
      ?.parentElement as HTMLElement;
    const ppt2tifOption = document.querySelector('[for="option-ppt2tif"]')
      ?.parentElement as HTMLElement;
    const cropTifOption = document.querySelector('[for="option-crop-tif"]')
      ?.parentElement as HTMLElement;
    const forceOption = document.querySelector('[for="option-force"]')
      ?.parentElement as HTMLElement;

    if (docType === "manuscript" || docType === "supplementary") {
      // Manuscript & Supplementary: All options available (v2.0.0-rc1)
      if (contentOptions) contentOptions.style.display = "block";
      if (figureProcessingOptions)
        figureProcessingOptions.style.display = "block";
      if (performanceOptions) performanceOptions.style.display = "block";
      if (appearanceOptions) appearanceOptions.style.display = "block";
      if (advancedOptions) advancedOptions.style.display = "block";
      if (diffOption) diffOption.style.display = "block";
      if (ppt2tifOption) ppt2tifOption.style.display = "block";
      if (cropTifOption) cropTifOption.style.display = "block";
      if (forceOption) forceOption.style.display = "block";
    } else if (docType === "revision") {
      // Revision: Content (without diff), Performance, Appearance only
      if (contentOptions) contentOptions.style.display = "block";
      if (figureProcessingOptions)
        figureProcessingOptions.style.display = "none";
      if (performanceOptions) performanceOptions.style.display = "block";
      if (appearanceOptions) appearanceOptions.style.display = "block";
      if (advancedOptions) advancedOptions.style.display = "none";
      if (diffOption) diffOption.style.display = "none"; // Revision skips diff by default
      if (ppt2tifOption) ppt2tifOption.style.display = "none";
      if (cropTifOption) cropTifOption.style.display = "none";
      if (forceOption) forceOption.style.display = "none";
    }

    // Show modal
    modal.style.display = "flex";
    setTimeout(() => {
      modal.classList.add("scitex-modal-visible");
    }, 10);

    // Handle confirm
    const confirmBtn = document.getElementById("confirm-compile-btn");
    const handleConfirm = () => {
      // Read options based on doc type (v2.0.0-rc1)
      const options: any = {};

      // Content options (inverted logic: checkbox = include, backend expects no_*)
      const includeFigs =
        (document.getElementById("option-add-figs") as HTMLInputElement)
          ?.checked || false;
      const includeTables =
        (document.getElementById("option-add-tables") as HTMLInputElement)
          ?.checked || false;
      const includeDiff =
        (document.getElementById("option-add-diff") as HTMLInputElement)
          ?.checked || false;

      options.noFigs = !includeFigs; // Default: exclude figures (fast)
      options.noTables = !includeTables; // Default: exclude tables (fast)
      options.noDiff = !includeDiff; // Default: no diff (fast)

      // Figure processing options (manuscript & supplementary only)
      if (docType === "manuscript" || docType === "supplementary") {
        options.ppt2tif =
          (document.getElementById("option-ppt2tif") as HTMLInputElement)
            ?.checked || false;
        options.cropTif =
          (document.getElementById("option-crop-tif") as HTMLInputElement)
            ?.checked || false;
      }

      // Performance options (all doc types)
      options.draft =
        (document.getElementById("option-draft") as HTMLInputElement)
          ?.checked || false;
      options.quiet =
        (document.getElementById("option-quiet") as HTMLInputElement)
          ?.checked || false;

      // Appearance options (all doc types)
      options.darkMode =
        (document.getElementById("option-dark-mode") as HTMLInputElement)
          ?.checked || false;

      // Advanced options (manuscript & supplementary only)
      if (docType === "manuscript" || docType === "supplementary") {
        options.force =
          (document.getElementById("option-force") as HTMLInputElement)
            ?.checked || false;
      }

      // Close modal
      modal.classList.remove("scitex-modal-visible");
      modal.classList.add("scitex-modal-closing");
      setTimeout(() => {
        modal.style.display = "none";
        modal.classList.remove("scitex-modal-closing");
      }, 300);

      // Cleanup listeners
      confirmBtn?.removeEventListener("click", handleConfirm);
      modal.removeEventListener("click", handleCancel);

      resolve(options);
    };

    // Handle cancel
    const handleCancel = (e: Event) => {
      if (
        e.target === modal ||
        (e.target as HTMLElement).classList.contains("scitex-modal-close")
      ) {
        modal.classList.remove("scitex-modal-visible");
        modal.classList.add("scitex-modal-closing");
        setTimeout(() => {
          modal.style.display = "none";
          modal.classList.remove("scitex-modal-closing");
        }, 300);

        // Cleanup listeners
        confirmBtn?.removeEventListener("click", handleConfirm);
        modal.removeEventListener("click", handleCancel);

        reject(new Error("User cancelled"));
      }
    };

    confirmBtn?.addEventListener("click", handleConfirm);
    modal.addEventListener("click", handleCancel);
  });
}

/**
 * Handle full manuscript compilation (no content sent - uses workspace)
 * @param showOptionsModal - Whether to show the compilation options modal (default: true for manual, false for auto)
 */
async function handleCompileFull(
  compilationManager: CompilationManager,
  state: any,
  docType: string = "manuscript",
  showOptionsModal: boolean = true,
): Promise<void> {
  if (compilationManager.getIsCompiling()) {
    showToast("Compilation already in progress", "warning");
    return;
  }

  try {
    const projectId = state.projectId;
    if (!projectId) {
      showToast("No project ID found", "error");
      return;
    }

    // Show modal and get user options (only for manual compilation)
    let compOptions;
    if (showOptionsModal) {
      try {
        compOptions = await showCompilationOptionsModal(docType);
      } catch (error) {
        // User cancelled
        return;
      }
    } else {
      // Auto-compilation: use default options (no modal)
      compOptions = {
        noFigs: false,
        ppt2tif: false,
        cropTif: false,
        quiet: false,
        verbose: false,
        force: false,
      };
    }

    // Display appropriate message based on doc type
    const docTypeLabels: Record<string, string> = {
      manuscript: "manuscript",
      supplementary: "supplementary materials",
      revision: "revision",
    };
    const docLabel = docTypeLabels[docType] || docType;

    showToast(`Compiling full ${docLabel} from workspace...`, "info");
    console.log(
      "[Writer] Starting full compilation for project:",
      projectId,
      "docType:",
      docType,
    );
    console.log("[Writer] Compilation options:", compOptions);

    const result = await compilationManager.compileFull({
      projectId: projectId,
      docType: docType,
      ...compOptions,
    });

    if (result && result.status === "completed") {
      showToast(
        `${docLabel.charAt(0).toUpperCase() + docLabel.slice(1)} compiled successfully`,
        "success",
      );
    } else {
      showToast("Compilation failed", "error");
    }
  } catch (error) {
    showToast(
      "Compilation error: " +
        (error instanceof Error ? error.message : "Unknown error"),
      "error",
    );
  }
}

/**
 * @deprecated Use handleCompileFull instead for compile button
 * Handle preview compilation (sends content - for auto-preview)
 */
async function handleCompile(
  _editor: WriterEditor | null,
  sectionsManager: SectionsManager,
  _compilationManager: CompilationManager,
  _state: any,
  pdfPreviewManager?: PDFPreviewManager,
): Promise<void> {
  if (!pdfPreviewManager) {
    showToast("PDF preview not initialized", "error");
    return;
  }

  if (pdfPreviewManager.isCompiling()) {
    showToast("Compilation already in progress", "warning");
    return;
  }

  try {
    const sections = sectionsManager.getAll();
    const sectionArray = Object.entries(sections).map(([name, content]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      content: content as unknown as string,
    }));

    showToast("Starting preview compilation...", "info");
    await pdfPreviewManager.compile(sectionArray);
  } catch (error) {
    showToast(
      "Compilation error: " +
        (error instanceof Error ? error.message : "Unknown error"),
      "error",
    );
  }
}

/**
 * Show git commit modal
 */
function showCommitModal(state: any): void {
  const currentSection = state.currentSection;
  if (!currentSection) {
    showToast("No section selected", "warning");
    return;
  }

  // Generate default commit message
  const parts = currentSection.split("/");
  const sectionName = parts[parts.length - 1];
  const formattedName = sectionName
    .split("_")
    .map((word: string) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
  const defaultMessage = `Update ${formattedName}`;

  // Set default commit message
  const messageInput = document.getElementById(
    "commit-message-input",
  ) as HTMLInputElement;
  if (messageInput) {
    messageInput.value = defaultMessage;
    // Select all text so user can easily replace it if needed
    setTimeout(() => {
      messageInput.focus();
      messageInput.select();
    }, 100);
  }

  // Show modal using scitex-modal pattern
  const modalEl = document.getElementById("git-commit-modal");
  if (modalEl) {
    modalEl.style.display = "flex";
    setTimeout(() => {
      modalEl.classList.add("scitex-modal-visible");
    }, 10);

    // Handle close buttons
    const handleCancel = (e: Event) => {
      if (
        e.target === modalEl ||
        (e.target as HTMLElement).classList.contains("scitex-modal-close")
      ) {
        closeCommitModal();
        modalEl.removeEventListener("click", handleCancel);
      }
    };
    modalEl.addEventListener("click", handleCancel);

    // Handle Enter key to submit
    const handleEnter = (e: KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleGitCommit(state);
        messageInput?.removeEventListener("keydown", handleEnter);
      }
    };
    messageInput?.addEventListener("keydown", handleEnter);
  }
}

/**
 * Close git commit modal
 */
function closeCommitModal(): void {
  const modalEl = document.getElementById("git-commit-modal");
  if (modalEl) {
    modalEl.classList.remove("scitex-modal-visible");
    modalEl.classList.add("scitex-modal-closing");
    setTimeout(() => {
      modalEl.style.display = "none";
      modalEl.classList.remove("scitex-modal-closing");
    }, 300);
  }
}

/**
 * Handle git commit
 */
async function handleGitCommit(state: any): Promise<void> {
  const currentSection = state.currentSection;
  if (!currentSection) {
    showToast("No section selected", "warning");
    return;
  }

  const messageInput = document.getElementById(
    "commit-message-input",
  ) as HTMLInputElement;
  const commitMessage = messageInput?.value.trim();

  if (!commitMessage) {
    showToast("Please enter a commit message", "warning");
    messageInput?.focus();
    return;
  }

  try {
    // Extract doc type and section name
    const [docType, sectionName] = currentSection.split("/");

    if (!docType || !sectionName) {
      showToast("Invalid section format", "error");
      return;
    }

    const config = (window as any).WRITER_CONFIG;

    // First, ensure changes are saved to file (auto-save might not have triggered yet)
    console.log("[Writer] Ensuring section is saved before commit...");
    // We need to get the current editor content and save it
    // This will be handled by calling the section write API
    // For now, we'll proceed with commit assuming auto-save has run

    // Call API endpoint to commit
    const response = await fetch(
      `/writer/api/project/${config.projectId}/section/${sectionName}/commit/`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": config.csrfToken,
        },
        body: JSON.stringify({
          doc_type: docType,
          message: commitMessage,
        }),
      },
    );

    if (!response.ok) {
      const errorText = await response.text();
      console.error("[Writer] Commit HTTP error:", response.status, errorText);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    console.log("[Writer] Commit response:", data);

    if (data.success) {
      showToast("Changes committed successfully", "success");

      // Close modal
      closeCommitModal();
    } else {
      console.error("[Writer] Commit failed:", data);
      throw new Error(data.error || "Commit failed");
    }
  } catch (error) {
    console.error("[Writer] Git commit error:", error);
    showToast(
      "Failed to commit: " +
        (error instanceof Error ? error.message : "Unknown error"),
      "error",
    );
  }
}

/**
 * Setup section management button listeners
 */
function setupSectionManagementButtons(
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
            compilationManager,
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
            compilationManager,
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
            compilationManager,
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
            compilationManager,
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

/**
 * Setup sidebar button listeners
 */
function setupSidebarButtons(_config: any): void {
  // Button listeners are set up in their respective initialization functions
  // No additional setup needed here
}

/**
 * Setup PDF zoom control buttons
 */
function setupPDFZoomControls(pdfScrollZoomHandler: any): void {
  const zoomInBtn = document.getElementById("pdf-zoom-in-btn");
  const zoomOutBtn = document.getElementById("pdf-zoom-out-btn");
  const fitWidthBtn = document.getElementById("pdf-fit-width-btn");
  const resetZoomBtn = document.getElementById("pdf-reset-zoom-btn");
  const colorModeBtn = document.getElementById("pdf-color-mode-btn");
  const zoomControls = document.querySelector(
    ".pdf-zoom-controls",
  ) as HTMLElement | null;

  if (zoomInBtn) {
    zoomInBtn.addEventListener("click", () => {
      pdfScrollZoomHandler.zoomIn();
    });
  }

  if (zoomOutBtn) {
    zoomOutBtn.addEventListener("click", () => {
      pdfScrollZoomHandler.zoomOut();
    });
  }

  if (fitWidthBtn) {
    fitWidthBtn.addEventListener("click", () => {
      pdfScrollZoomHandler.fitToWidth();
    });
  }

  if (resetZoomBtn) {
    resetZoomBtn.addEventListener("click", () => {
      pdfScrollZoomHandler.resetZoom();
    });
  }

  // Note: colorModeBtn listener already attached earlier in initialization

  // Show/hide zoom controls based on PDF presence
  const observer = new MutationObserver(() => {
    const hasPDF = document.querySelector(".pdf-preview-container") !== null;
    if (zoomControls) {
      zoomControls.style.display = hasPDF ? "flex" : "none";
    }
  });

  const previewPanel = document.querySelector(".preview-panel");
  if (previewPanel) {
    observer.observe(previewPanel, { childList: true, subtree: true });
  }

  console.log("[Writer] PDF zoom controls initialized");
}

/**
 * Open PDF
 */
function openPDF(url: string): void {
  const pdfWindow = window.open(url, "_blank");
  if (!pdfWindow) {
    const showToast =
      (window as any).showToast || ((msg: string) => console.warn(msg));
    showToast("Failed to open PDF. Please check popup blocker settings.");
  }
}

/**
 * Switch right panel between PDF and Citations views
 */
function switchRightPanel(view: "pdf" | "citations"): void {
  const pdfView = document.getElementById("pdf-view");
  const citationsView = document.getElementById("citations-view");
  // Get all view switch buttons in both panel headers
  const allPdfBtns = document.querySelectorAll(
    '#show-pdf-btn, .view-switch-btn[onclick*="pdf"]',
  );
  const allCitationsBtns = document.querySelectorAll(
    '#show-citations-btn, .view-switch-btn[onclick*="citations"]',
  );
  // const pdfZoomControls = document.querySelector('.pdf-zoom-controls') as HTMLElement; // REMOVED
  const previewPanel = document.querySelector(".preview-panel") as HTMLElement;

  if (!pdfView || !citationsView) {
    console.error("[Writer] Panel toggle elements not found");
    return;
  }

  if (view === "citations") {
    // Show citations, hide PDF
    pdfView.style.display = "none";
    citationsView.style.display = "flex";

    // Add class to preview-panel for CSS targeting
    if (previewPanel) {
      previewPanel.classList.add("showing-citations");
      previewPanel.classList.remove("showing-pdf");
    }

    // Update button states - all buttons in both headers
    allPdfBtns.forEach((btn) => btn.classList.remove("active"));
    allCitationsBtns.forEach((btn) => btn.classList.add("active"));

    // Hide PDF zoom controls (REMOVED - no longer in UI)
    // if (pdfZoomControls) {
    //     pdfZoomControls.style.display = 'none';
    // }

    // Save pane state
    statePersistence.saveActivePane("citations");
    console.log("[Writer] Switched to Citations view, saved pane state: citations");

    // Load citations if not already loaded
    const citationsPanel = (window as any).citationsPanel;
    if (citationsPanel && typeof citationsPanel.loadCitations === "function") {
      citationsPanel.loadCitations();
    }
  } else {
    // Show PDF, hide citations
    citationsView.style.display = "none";
    pdfView.style.display = "flex";

    // Add class to preview-panel for CSS targeting
    if (previewPanel) {
      previewPanel.classList.remove("showing-citations");
      previewPanel.classList.add("showing-pdf");
    }

    // Save pane state
    statePersistence.saveActivePane("pdf");

    // Update button states - all buttons in both headers
    allCitationsBtns.forEach((btn) => btn.classList.remove("active"));
    allPdfBtns.forEach((btn) => btn.classList.add("active"));

    // Show PDF zoom controls if PDF is loaded (REMOVED - no longer in UI)
    // const hasPDF = document.querySelector('.pdf-preview-container') !== null;
    // if (pdfZoomControls && hasPDF) {
    //     pdfZoomControls.style.display = 'flex';
    // }

    console.log("[Writer] Switched to PDF view, saved pane state: pdf");
  }

  // Legacy save (keeping for backward compatibility)
  localStorage.setItem("writer_right_panel_view", view);
}

/**
 * Show compilation progress in inline output area
 */
function showCompilationProgress(title: string = "Compiling Manuscript"): void {
  const output = document.getElementById("compilation-output");
  const icon = document.getElementById("compilation-icon");
  const headerTitle = document.getElementById("compilation-header-title");
  const progressContainer = document.getElementById(
    "compilation-progress-container",
  );
  const resultDiv = document.getElementById("compilation-result-inline");

  if (!output) return;

  // Update header
  if (icon) {
    icon.className = "fas fa-spinner fa-spin";
  }
  if (headerTitle) {
    headerTitle.textContent = title;
  }

  // Show progress bar
  if (progressContainer) {
    progressContainer.style.display = "block";
  }

  // Hide result
  if (resultDiv) {
    resultDiv.style.display = "none";
    resultDiv.innerHTML = "";
  }

  // Reset progress
  updateCompilationProgress(0, "Initializing...");

  // Clear log
  const log = document.getElementById("compilation-log-inline");
  if (log) {
    log.textContent = "Starting compilation...\n";
  }

  // Ensure log details are closed (minimized) by default
  const logDetails = document.getElementById("compilation-log-details") as HTMLDetailsElement;
  if (logDetails) {
    logDetails.open = false;
  }

  // Show compilation output
  output.style.display = "block";

  // Update status lamp and slim progress
  updateStatusLamp("compiling", "Compiling...");
  updateSlimProgress(0, "Initializing...");
}

/**
 * Hide compilation output
 */
function hideCompilationProgress(): void {
  const output = document.getElementById("compilation-output");
  if (output) {
    output.style.display = "none";
  }
}

/**
 * Update compilation progress
 */
function updateCompilationProgress(percent: number, status: string): void {
  const progressBar = document.getElementById("compilation-progress-bar");
  const progressPercent = document.getElementById(
    "compilation-progress-percent",
  );
  const progressStatus = document.getElementById("compilation-progress-status");

  if (progressBar) progressBar.style.width = `${percent}%`;
  if (progressPercent) progressPercent.textContent = `${percent}%`;
  if (progressStatus) progressStatus.textContent = status;

  // Also update minimized status if it's visible
  updateMinimizedStatus(percent, status);

  // Update slim progress bar
  updateSlimProgress(percent, status);
}

/**
 * Append to compilation log with semantic color coding and visual cues
 */
function appendCompilationLog(
  message: string,
  type: "info" | "success" | "error" | "warning" | "processing" = "info",
  options?: { spinner?: boolean; dots?: boolean; id?: string },
): void {
  const log = document.getElementById("compilation-log-inline");
  if (!log) return;

  // Create line container
  const lineDiv = document.createElement("div");
  if (options?.id) {
    lineDiv.id = options.id;
  }

  // Add spinner if requested
  if (options?.spinner) {
    const spinner = document.createElement("span");
    spinner.className = "terminal-log__spinner";
    lineDiv.appendChild(spinner);
  }

  // Create colored span for the message
  const span = document.createElement("span");

  // Apply semantic color class based on message content or type
  if (
    message.includes("✓") ||
    message.includes("Success") ||
    type === "success"
  ) {
    span.className = "terminal-log__success";
  } else if (
    message.includes("✗") ||
    message.includes("Error") ||
    message.includes("Failed") ||
    type === "error"
  ) {
    span.className = "terminal-log__error";
  } else if (
    message.includes("⚠") ||
    message.includes("Warning") ||
    type === "warning"
  ) {
    span.className = "terminal-log__warning";
  } else if (type === "processing") {
    span.className = "terminal-log__processing";
  } else {
    span.className = "terminal-log__info";
  }

  span.textContent = message;
  lineDiv.appendChild(span);

  // Add animated dots if requested
  if (options?.dots) {
    const dots = document.createElement("span");
    dots.className = "terminal-log__loading-dots";
    lineDiv.appendChild(dots);
  }

  // Add newline
  lineDiv.appendChild(document.createTextNode("\n"));

  log.appendChild(lineDiv);

  // Auto-scroll to bottom
  log.scrollTop = log.scrollHeight;
}

/**
 * Update a processing log line (remove spinner/dots, update message)
 */
function updateCompilationLog(
  lineId: string,
  message: string,
  type: "success" | "error" | "warning" | "info" = "info",
): void {
  const line = document.getElementById(lineId);
  if (!line) return;

  // Remove spinner and dots
  const spinner = line.querySelector(".terminal-log__spinner");
  const dots = line.querySelector(".terminal-log__loading-dots");
  if (spinner) spinner.remove();
  if (dots) dots.remove();

  // Update message
  const span = line.querySelector(
    "span:not(.terminal-log__spinner):not(.terminal-log__loading-dots)",
  );
  if (span) {
    span.textContent = message;

    // Update color class
    span.className = "";
    if (
      message.includes("✓") ||
      message.includes("Success") ||
      type === "success"
    ) {
      span.className = "terminal-log__success";
    } else if (
      message.includes("✗") ||
      message.includes("Error") ||
      message.includes("Failed") ||
      type === "error"
    ) {
      span.className = "terminal-log__error";
    } else if (
      message.includes("⚠") ||
      message.includes("Warning") ||
      type === "warning"
    ) {
      span.className = "terminal-log__warning";
    } else {
      span.className = "terminal-log__info";
    }
  }
}

/**
 * Show compilation success
 */
function showCompilationSuccess(pdfUrl: string): void {
  const icon = document.getElementById("compilation-icon");
  const progressContainer = document.getElementById(
    "compilation-progress-container",
  );
  const alertBanner = document.getElementById("compilation-alert-banner");
  const resultDiv = document.getElementById("compilation-result-inline");
  const minimizedStatus = document.getElementById(
    "minimized-compilation-status",
  );

  // Update icon to success
  if (icon) {
    icon.className = "fas fa-check-circle text-success";
  }

  // Hide progress bar
  if (progressContainer) {
    progressContainer.style.display = "none";
  }

  // Show success alert banner
  if (alertBanner) {
    alertBanner.style.display = "block";
    alertBanner.className = "alert-banner alert-banner-success";
    alertBanner.innerHTML = `
            <div class="warning-banner-content">
                <i class="fas fa-check-circle warning-banner-icon"></i>
                <div class="warning-banner-text">
                    <div class="warning-banner-title">Compilation Successful!</div>
                    <div class="warning-banner-description">
                        Your manuscript PDF has been generated.
                        <a href="${pdfUrl}" target="_blank" style="color: white; text-decoration: underline; margin-left: 0.5rem;">
                            <i class="fas fa-file-pdf me-1"></i>View PDF
                        </a>
                    </div>
                </div>
            </div>
        `;
  }

  // Keep old result div for backward compatibility (hide it)
  if (resultDiv) {
    resultDiv.style.display = "none";
  }

  updateCompilationProgress(100, "Complete!");

  // Update status lamp to success
  updateStatusLamp("success", "Success");

  // Update minimized status icon to success
  if (minimizedStatus) {
    const icon = minimizedStatus.querySelector("i");
    if (icon) {
      icon.className = "fas fa-check-circle";
      icon.style.color = "var(--color-success-emphasis)";
    }
  }

  // Auto-hide minimized status after 3 seconds if compilation was successful
  setTimeout(() => {
    if (minimizedStatus && minimizedStatus.style.display !== "none") {
      minimizedStatus.style.display = "none";
    }
  }, 3000);
}

/**
 * Show compilation error
 */
function showCompilationError(
  errorMessage: string,
  errorDetails: string = "",
): void {
  const icon = document.getElementById("compilation-icon");
  const progressContainer = document.getElementById(
    "compilation-progress-container",
  );
  const alertBanner = document.getElementById("compilation-alert-banner");
  const resultDiv = document.getElementById("compilation-result-inline");
  const minimizedStatus = document.getElementById(
    "minimized-compilation-status",
  );

  // Update icon to error
  if (icon) {
    icon.className = "fas fa-exclamation-circle text-danger";
  }

  // Hide progress bar
  if (progressContainer) {
    progressContainer.style.display = "none";
  }

  // Show error alert banner
  if (alertBanner) {
    alertBanner.style.display = "block";
    alertBanner.className = "alert-banner alert-banner-danger";
    alertBanner.innerHTML = `
            <div class="warning-banner-content">
                <i class="fas fa-exclamation-circle warning-banner-icon"></i>
                <div class="warning-banner-text">
                    <div class="warning-banner-title">Compilation Failed</div>
                    <div class="warning-banner-description">
                        ${errorMessage}
                        ${errorDetails ? "<br><small>Check the compilation log below for details.</small>" : ""}
                    </div>
                </div>
            </div>
        `;
  }

  // Keep old result div for backward compatibility (hide it)
  if (resultDiv) {
    resultDiv.style.display = "none";
  }

  // Update status lamp to error
  updateStatusLamp("error", "Failed");

  // Update minimized status icon to error and make it clickable to see details
  if (minimizedStatus) {
    const icon = minimizedStatus.querySelector("i");
    const text = minimizedStatus.querySelector("#minimized-compilation-text");
    if (icon) {
      icon.className = "fas fa-exclamation-circle";
      icon.style.color = "var(--color-danger-emphasis)";
    }
    if (text) {
      text.textContent = "Failed";
    }
    // Keep minimized status visible so user can click to see error details
    minimizedStatus.title = "Click to view error details";
  }
}

/**
 * Minimize compilation output to background status
 */
function minimizeCompilationOutput(): void {
  const output = document.getElementById("compilation-output");
  const minimizedStatus = document.getElementById(
    "minimized-compilation-status",
  );
  const minimizeBtn = document.getElementById("minimize-compilation-output");

  if (!output) return;

  // Hide the full compilation output
  output.style.display = "none";

  // Show minimized status indicator
  if (minimizedStatus) {
    minimizedStatus.style.display = "flex";
  }

  // Update minimize button icon to restore icon
  if (minimizeBtn) {
    minimizeBtn.innerHTML = '<i class="fas fa-window-restore"></i>';
    minimizeBtn.title = "Restore compilation panel";
  }
}

/**
 * Restore compilation output from minimized state
 */
function restoreCompilationOutput(): void {
  const output = document.getElementById("compilation-output");
  const minimizedStatus = document.getElementById(
    "minimized-compilation-status",
  );
  const minimizeBtn = document.getElementById("minimize-compilation-output");

  if (!output) return;

  // Show the full compilation output
  output.style.display = "block";

  // Hide minimized status indicator
  if (minimizedStatus) {
    minimizedStatus.style.display = "none";
  }

  // Update minimize button icon back to minimize icon
  if (minimizeBtn) {
    minimizeBtn.innerHTML = '<i class="fas fa-window-minimize"></i>';
    minimizeBtn.title = "Minimize to background";
  }
}

// Store separate logs for preview and full compilation
const compilationLogs = {
  preview: "",
  full: "",
};

/**
 * Toggle compilation panel visibility
 * Called when clicking on status indicators
 */
function toggleCompilationPanel(type: "preview" | "full" = "full"): void {
  const output = document.getElementById("compilation-output");
  const logDiv = document.getElementById("compilation-log-inline");
  if (!output || !logDiv) return;

  // Check if we're switching log types
  const currentType = output.getAttribute("data-log-type");
  const isSwitchingType = currentType && currentType !== type;

  // Store current log content before switching
  if (currentType && logDiv.innerHTML) {
    compilationLogs[currentType as "preview" | "full"] = logDiv.innerHTML;
  }

  // Set the log type
  output.setAttribute("data-log-type", type);

  // Load the appropriate log content
  if (isSwitchingType || !logDiv.innerHTML) {
    const savedLog = compilationLogs[type];
    if (savedLog) {
      logDiv.innerHTML = savedLog;
    } else {
      logDiv.innerHTML =
        type === "preview"
          ? "No preview compilation logs yet. Click the preview play button to compile."
          : "No full compilation logs yet. Click the full play button to compile.";
    }
  }

  // Toggle visibility
  if (output.style.display === "none" || !output.style.display) {
    output.style.display = "block";
    console.log(`[Writer] ${type} compilation panel shown`);
  } else {
    output.style.display = "none";
    console.log("[Writer] Compilation panel hidden");
  }
}

/**
 * Toggle preview compilation log
 */
function togglePreviewLog(): void {
  toggleCompilationPanel("preview");
}

/**
 * Toggle full compilation log
 */
function toggleFullLog(): void {
  toggleCompilationPanel("full");
}

/**
 * Update minimized compilation status
 */
function updateMinimizedStatus(progress: number, status: string): void {
  const minimizedText = document.getElementById("minimized-compilation-text");
  const minimizedProgress = document.getElementById(
    "minimized-compilation-progress",
  );

  if (minimizedText) {
    minimizedText.textContent = status;
  }
  if (minimizedProgress) {
    minimizedProgress.textContent = `${progress}%`;
  }
}

/**
 * Update status lamp (LED indicator)
 */
function updateStatusLamp(
  status: "idle" | "compiling" | "success" | "error",
  text: string,
): void {
  const lamp = document.querySelector(".status-lamp-indicator") as HTMLElement;
  const lampText = document.querySelector(".status-lamp-text") as HTMLElement;

  if (lamp) {
    lamp.setAttribute("data-status", status);
  }
  if (lampText) {
    lampText.textContent = text;
  }

  // Persist status to localStorage
  localStorage.setItem(
    "scitex-compilation-status",
    JSON.stringify({ status, text, timestamp: Date.now() }),
  );
}

/**
 * Update slim progress bar (tqdm-style)
 */
function updateSlimProgress(
  progress: number,
  status: string,
  eta?: string,
): void {
  const slimProgress = document.getElementById("compilation-slim-progress");
  const slimFill = document.getElementById("slim-progress-fill");
  const slimPercent = document.getElementById("slim-progress-percent");
  const slimStatus = document.getElementById("slim-progress-status");
  const slimEta = document.getElementById("slim-progress-eta");

  if (!slimProgress) return;

  // Show slim progress during compilation
  if (progress > 0 && progress < 100) {
    slimProgress.style.display = "block";
  }

  if (slimFill) {
    slimFill.style.width = `${progress}%`;
  }
  if (slimPercent) {
    slimPercent.textContent = `${progress}%`;
  }
  if (slimStatus) {
    slimStatus.textContent = status;
  }
  if (slimEta && eta) {
    slimEta.textContent = eta;
  }

  // Hide after completion (with delay)
  if (progress === 100) {
    setTimeout(() => {
      if (slimProgress) {
        slimProgress.style.display = "none";
      }
    }, 2000);
  }
}

/**
 * Toggle compilation details panel
 */
function toggleCompilationDetails(): void {
  const output = document.getElementById("compilation-output");
  const slimProgress = document.getElementById("compilation-slim-progress");

  if (!output) return;

  const isVisible = output.style.display === "block";

  if (isVisible) {
    // Hide details, show only slim progress
    output.style.display = "none";
    if (slimProgress) {
      slimProgress.style.display = "block";
    }
  } else {
    // Show full details
    output.style.display = "block";
    if (slimProgress) {
      slimProgress.style.display = "none";
    }
  }
}

/**
 * Restore last compilation status from localStorage
 */
function restoreCompilationStatus(): void {
  const saved = localStorage.getItem("scitex-compilation-status");
  if (!saved) {
    updateStatusLamp("idle", "Ready");
    return;
  }

  try {
    const { status, text, timestamp } = JSON.parse(saved);
    const ageMs = Date.now() - timestamp;
    const ageMinutes = Math.floor(ageMs / 60000);

    // If status is recent (< 5 minutes), show it
    if (ageMinutes < 5) {
      updateStatusLamp(status, text);
    } else if (status === "success") {
      // Show successful compilation even if old
      updateStatusLamp("success", `Done (${ageMinutes}m ago)`);
    } else {
      // Reset to idle
      updateStatusLamp("idle", "Ready");
    }
  } catch (e) {
    console.warn("[Compilation] Failed to restore status:", e);
    updateStatusLamp("idle", "Ready");
  }
}

/**
 * Toggle section visibility (include/exclude from compilation)
 */
async function toggleSectionVisibility(
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

// Export functions to global scope for ES6 module compatibility
(window as any).populateSectionDropdownDirect = populateSectionDropdownDirect;

/**
 * Handle download full PDF (called from dropdown buttons - deprecated, use handleDownloadSectionPDF)
 */
(window as any).handleDownloadFullPDF = function (event: Event): void {
  event.preventDefault();
  // Redirect to section-specific handler
  handleDownloadSectionPDF("manuscript/compiled_pdf", "Full Manuscript");
};

/**
 * Handle download current PDF (downloads whatever is shown in viewer)
 */
(window as any).handleDownloadCurrentPDF = function (event: Event): void {
  event.preventDefault();

  const config = getWriterConfig();
  if (!config.projectId) {
    showToast("No project selected", "error");
    return;
  }

  // Get currently displayed PDF from iframe src
  const iframe = document.querySelector(
    "#text-preview iframe",
  ) as HTMLIFrameElement;
  if (!iframe || !iframe.src) {
    showToast("No PDF currently displayed", "warning");
    return;
  }

  // Extract PDF URL (remove query parameters and hash)
  let pdfUrl = iframe.src.split("?")[0].split("#")[0];

  // Determine filename based on URL
  let filename = "preview.pdf";
  if (pdfUrl.includes("manuscript.pdf")) {
    filename = `${config.projectName || "manuscript"}_full.pdf`;
  } else if (pdfUrl.includes("preview-")) {
    // Extract section name from preview filename (handles both theme-specific and legacy)
    // Matches: preview-abstract-light.pdf or preview-abstract.pdf
    const match = pdfUrl.match(/preview-([^-\.]+)(?:-(?:light|dark))?\.pdf/);
    const sectionName = match ? match[1] : "preview";
    filename = `${config.projectName || "manuscript"}_${sectionName}.pdf`;
  }

  // Create temporary link and trigger download
  const link = document.createElement("a");
  link.href = pdfUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  showToast(`Downloading ${filename}...`, "success");
};

/**
 * Handle download citations as BibTeX
 */
(window as any).handleDownloadCitationsBibTeX = function (
  event: Event,
): void {
  event.preventDefault();

  const config = getWriterConfig();
  if (!config.projectId) {
    showToast("No project selected", "error");
    return;
  }

  // Get citations from the citations panel
  const citationsPanel = (window as any).citationsPanel;
  if (!citationsPanel || !citationsPanel.citations) {
    showToast("No citations available", "warning");
    return;
  }

  const citations = citationsPanel.citations;
  if (citations.length === 0) {
    showToast("No citations to download", "info");
    return;
  }

  // Convert citations to BibTeX format
  let bibtexContent = "";
  citations.forEach((citation: any) => {
    const entryType = citation.entry_type || "article";
    const key = citation.key;

    bibtexContent += `@${entryType}{${key},\n`;

    // Add fields
    if (citation.title) bibtexContent += `  title = {${citation.title}},\n`;
    if (citation.authors && citation.authors.length > 0) {
      bibtexContent += `  author = {${citation.authors.join(" and ")}},\n`;
    }
    if (citation.journal) bibtexContent += `  journal = {${citation.journal}},\n`;
    if (citation.year) bibtexContent += `  year = {${citation.year}},\n`;
    if (citation.volume) bibtexContent += `  volume = {${citation.volume}},\n`;
    if (citation.number) bibtexContent += `  number = {${citation.number}},\n`;
    if (citation.pages) bibtexContent += `  pages = {${citation.pages}},\n`;
    if (citation.doi) bibtexContent += `  doi = {${citation.doi}},\n`;
    if (citation.url) bibtexContent += `  url = {${citation.url}},\n`;
    if (citation.publisher)
      bibtexContent += `  publisher = {${citation.publisher}},\n`;
    if (citation.abstract)
      bibtexContent += `  abstract = {${citation.abstract}},\n`;

    bibtexContent += "}\n\n";
  });

  // Create blob and download
  const blob = new Blob([bibtexContent], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${config.projectName || "citations"}.bib`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);

  showToast(
    `Downloaded ${citations.length} citation${citations.length > 1 ? "s" : ""} as BibTeX`,
    "success",
  );
};

/**
 * Handle download section PDF (for dropdown buttons)
 */
function handleDownloadSectionPDF(
  sectionId: string,
  sectionLabel: string,
): void {
  const config = getWriterConfig();
  if (!config.projectId) {
    showToast("No project selected", "error");
    return;
  }

  // Parse section ID to get section name
  const parts = sectionId.split("/");
  const sectionName = parts[parts.length - 1];

  // Determine PDF URL based on section type
  let pdfUrl: string;
  let filename: string;

  if (sectionName === "compiled_pdf") {
    // Full manuscript PDF - use doc_type query parameter
    const docType = parts[0]; // manuscript, supplementary, or revision
    pdfUrl = `/writer/api/project/${config.projectId}/pdf/?doc_type=${docType}`;
    filename = `${config.projectName || "manuscript"}_${docType}.pdf`;

    // Check if PDF exists before downloading
    fetch(pdfUrl, { method: "HEAD" })
      .then((response) => {
        if (!response.ok) {
          console.warn("[Download] Full manuscript PDF not found at:", pdfUrl);
          showToast(
            `Full ${docType} PDF not compiled yet. Click 📄 Compile button in dropdown first.`,
            "warning",
          );
          return;
        }

        // PDF exists, download it
        console.log("[Download] Downloading full manuscript PDF from:", pdfUrl);
        const link = document.createElement("a");
        link.href = pdfUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        showToast(`Downloading ${filename}...`, "success");
      })
      .catch((error) => {
        console.error("[Download] Error checking PDF:", error);
        showToast(
          `Full ${docType} PDF not compiled yet. Click 📄 Compile button in dropdown first.`,
          "warning",
        );
      });
  } else {
    // Section preview PDF - try to find themed version first, fall back to any available
    const currentTheme =
      (window as any).pdfScrollZoomHandler?.getColorMode() || "light";
    const themedPdfUrl = `/writer/api/project/${config.projectId}/pdf/preview-${sectionName}-${currentTheme}.pdf`;
    const fallbackPdfUrl = `/writer/api/project/${config.projectId}/pdf/preview-${sectionName}-light.pdf`;
    filename = `${config.projectName || "manuscript"}_${sectionName}.pdf`;

    // Try themed PDF first
    fetch(themedPdfUrl, { method: "HEAD" })
      .then((response) => {
        if (response.ok) {
          // Themed PDF exists, download it
          pdfUrl = themedPdfUrl;
        } else {
          // Try fallback light theme
          return fetch(fallbackPdfUrl, { method: "HEAD" });
        }
        return response;
      })
      .then((response) => {
        if (response.ok) {
          // PDF found, download it
          const link = document.createElement("a");
          link.href = pdfUrl || fallbackPdfUrl;
          link.download = filename;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);

          showToast(`Downloading ${filename}...`, "success");
        } else {
          showToast(
            `${sectionLabel} PDF not generated yet. Wait for auto-preview or click section.`,
            "warning",
          );
        }
      })
      .catch(() => {
        showToast(
          `${sectionLabel} PDF not generated yet. Wait for auto-preview or click section.`,
          "warning",
        );
      });
  }
}
(window as any).handleDownloadSectionPDF = handleDownloadSectionPDF;
(window as any).switchRightPanel = switchRightPanel;
(window as any).showCompilationProgress = showCompilationProgress;
(window as any).hideCompilationProgress = hideCompilationProgress;
(window as any).updateCompilationProgress = updateCompilationProgress;
(window as any).appendCompilationLog = appendCompilationLog;
(window as any).updateCompilationLog = updateCompilationLog;
(window as any).showCompilationSuccess = showCompilationSuccess;
(window as any).showCompilationError = showCompilationError;
(window as any).minimizeCompilationOutput = minimizeCompilationOutput;
(window as any).restoreCompilationOutput = restoreCompilationOutput;
(window as any).toggleCompilationPanel = toggleCompilationPanel;
(window as any).togglePreviewLog = togglePreviewLog;
(window as any).toggleFullLog = toggleFullLog;
(window as any).compilationLogs = compilationLogs;
(window as any).updateMinimizedStatus = updateMinimizedStatus;
(window as any).updateStatusLamp = updateStatusLamp;
(window as any).updateSlimProgress = updateSlimProgress;
(window as any).toggleCompilationDetails = toggleCompilationDetails;
(window as any).restoreCompilationStatus = restoreCompilationStatus;
// (window as any).toggleCompilationLog = toggleCompilationLog; // Function not defined
