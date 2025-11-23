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
  FiguresPanel,
  TablesPanel,
  TablePreviewModal,
  statusLamp,
  compilationSettings,
  setupDragAndDrop,
  setupPDFScrollPriority,
  setupThemeListener,
  setupKeybindingListener,
  scheduleSave,
  scheduleAutoCompile,
  saveSections,
  setLoadingContent,
  getLoadingContent,
  showCommitModal,
  closeCommitModal,
  handleGitCommit,
  showCompilationOptionsModal,
  setupWorkspaceInitialization,
  waitForMonaco,
} from "./modules/index.js";
import {
  SectionManagement,
  setSectionOpsPdfPreviewManager,
  PanelSwitcher,
  EditorListeners,
  loadTexFile,
  handleDownloadFullPDF,
  handleDownloadCurrentPDF,
  handleDownloadCitationsBibTeX,
  handleDownloadSectionPDF,
  setDownloadPdfPreviewManager,
  ComponentInitializer,
  EventHandlerSetup,
} from "./writer/index.js";
import { PDFScrollZoomHandler } from "./modules/pdf-scroll-zoom.js";
import { statePersistence } from "./modules/state-persistence.js";
import { getCsrfToken } from "@/utils/csrf.js";
import { writerStorage } from "@/utils/storage.js";
import { getWriterConfig, createDefaultEditorState } from "./helpers.js";
import { GitHistoryManager } from "./modules/git-history.js";
import { initializeCollaboratorsPanel } from "./collaboration-panel.js";
import {
  SaveSectionsResponse,
  SectionReadResponse,
  validateSaveSectionsResponse,
  validateSectionReadResponse,
  isSaveSectionsResponse,
  isSectionReadResponse,
} from "./types/api-responses.js";
import {
  showToast,
  getUserContext,
  updateWordCountDisplay,
  updateSectionTitleLabel,
  updatePDFPreviewTitle,
  updateCommitButtonVisibility,
  showCompilationProgress,
  hideCompilationProgress,
  updateCompilationProgress,
  appendCompilationLog,
  updateCompilationLog,
  showCompilationSuccess,
  showCompilationError,
  minimizeCompilationOutput,
  restoreCompilationOutput,
  compilationLogs,
  toggleCompilationPanel,
  togglePreviewLog,
  toggleFullLog,
  handleCompilationLogStart,
  handleCompilationLogStop,
  handleCompilationLogClose,
  updateMinimizedStatus,
  updateStatusLamp,
  updateSlimProgress,
  toggleCompilationDetails,
  restoreCompilationStatus,
  populateSectionDropdownDirect,
  syncDropdownToSection,
  handleDocTypeSwitch,
  toggleSectionVisibility,
  setupSectionListeners,
  loadSectionContent,
  switchSection,
  updateSectionUI,
  loadCompiledPDF,
  setupSectionManagementButtons,
  clearCompileTimeout,
  setupCompilationListeners,
  handleCompileFull,
  handleCompile,
  setupSidebarButtons,
  setupPDFZoomControls,
  openPDF,
  loadPanelCSS,
  switchRightPanel,
} from "./utils/index.js";

console.log(
  "[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/index.ts loaded",
);

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
 * Initialize editor and its components
 */
async function initializeEditor(config: any): Promise<void> {
  const totalStart = performance.now();
  console.log("[Writer] Starting parallel initialization...");

  // PHASE 1: Initialize independent UI components in parallel with Monaco loading
  const phase1Start = performance.now();
  const [monacoReady, panelResizer, citationsPanel, figuresPanel, tablesPanel, tablePreviewModal, sectionsManager, compilationManager] = await Promise.all([
    // Wait for Monaco to load
    waitForMonaco(),

    // Initialize independent UI panels
    Promise.resolve(new PanelResizer()),
    Promise.resolve(new CitationsPanel()),
    Promise.resolve(new FiguresPanel()),
    Promise.resolve(new TablesPanel()),
    Promise.resolve(new TablePreviewModal()),

    // Initialize independent core components
    Promise.resolve(new SectionsManager()),
    Promise.resolve(new CompilationManager("")),
  ]);

  // Make panels available globally
  (window as any).citationsPanel = citationsPanel;
  (window as any).figuresPanel = figuresPanel;
  (window as any).tablesPanel = tablesPanel;
  (window as any).tablePreviewModal = tablePreviewModal;

  if (!panelResizer.isInitialized()) {
    console.warn("[Writer] Panel resizer could not be initialized");
  }

  const phase1End = performance.now();
  console.log(`[Writer] Phase 1 complete in ${(phase1End - phase1Start).toFixed(2)}ms (UI panels + core components initialized)`);

  // PHASE 2: Initialize editor and dependent components
  const phase2Start = performance.now();

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

  // Initialize AI2 prompt generator (disabled until generate_ai2_prompt.py is implemented)
  // const { initializeAI2Prompt } = await import('./modules/ai2-prompt.js');
  // initializeAI2Prompt(config.projectId);

  // Setup state management
  const state = createDefaultEditorState(config);

  // Initialize PDF components in parallel
  const [pdfPreviewManager, pdfScrollZoomHandler] = await Promise.all([
    Promise.resolve(new PDFPreviewManager({
      containerId: "text-preview",
      projectId: config.projectId || 0,
      manuscriptTitle: config.manuscriptTitle || "Untitled",
      author: config.username || "",
      autoCompile: false, // Disabled - preview shows full manuscript PDF only
      compileDelay: 2000, // 2 seconds delay for live preview
      apiBaseUrl: "",
      docType: state.currentDocType || "manuscript",
    })),
    Promise.resolve(new PDFScrollZoomHandler({
      containerId: "text-preview",
      minZoom: 50,
      maxZoom: 300,
      zoomStep: 10,
    })),
  ]);

  // Set module-level reference for access from other functions
  modulePdfPreviewManager = pdfPreviewManager;

  // Set PDF preview manager reference for modules
  setSectionOpsPdfPreviewManager(pdfPreviewManager);
  setDownloadPdfPreviewManager(pdfPreviewManager);

  // Observe for PDF viewer changes and reinitialize zoom handler
  pdfScrollZoomHandler.observePDFViewer();

  const phase2End = performance.now();
  console.log(`[Writer] Phase 2 complete in ${(phase2End - phase2Start).toFixed(2)}ms (editor + PDF components initialized)`);

  // PHASE 3: Setup event handlers and connections
  const phase3Start = performance.now();

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

  const phase3End = performance.now();
  console.log(`[Writer] Phase 3 complete in ${(phase3End - phase3Start).toFixed(2)}ms (event handlers setup)`);

  console.log("[Writer] Citations panel initialized");
  console.log("[Writer] Figures panel initialized");
  console.log("[Writer] Tables panel initialized");
  console.log("[Writer] Table preview modal initialized");

  // Initialize Git History Manager lazily (will be created when history panel is first accessed)
  // This is because the history panel DOM elements don't exist until the panel is loaded
  (window as any).initGitHistoryManager = () => {
    if (!(window as any).gitHistoryManager && config.projectId) {
      const gitHistoryManager = new GitHistoryManager(config.projectId);
      (window as any).gitHistoryManager = gitHistoryManager;
      console.log("[Writer] Git History Manager initialized");
      return gitHistoryManager;
    }
    return (window as any).gitHistoryManager;
  };

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
      switchSection(editor, sectionsManager, state, sectionId, pdfPreviewManager);
    } else if (sectionId.endsWith(".tex")) {
      // It's a file path - load from disk
      console.log("[Writer] Detected .tex file, loading from disk:", sectionId);
      loadTexFile(sectionId, editor);
    } else {
      // Fallback: try as section first, then as file
      console.log("[Writer] Unknown ID format, trying as section:", sectionId);
      switchSection(editor, sectionsManager, state, sectionId, pdfPreviewManager);
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
      // Use EditorListeners module
      const editorListeners = new EditorListeners(
        editor,
        sectionsManager,
        compilationManager,
        state,
        pdfPreviewManager,
      );
      editorListeners.setupListeners();

      setupSectionListeners(sectionsManager, editor, state, writerStorage);
    }
    setupCompilationListeners(compilationManager, config);
    setupThemeListener(editor);
    setupKeybindingListener(editor);
    setupSidebarButtons(config);

    // Use SectionManagement module
    const sectionManagement = new SectionManagement(
      config,
      state,
      sectionsManager,
      editor,
    );
    sectionManagement.setupButtons();
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

  const totalEnd = performance.now();

  // TIMING SUMMARY
  console.log('\n═══════════════════════════════════════════════════════');
  console.log('📊 WRITER PAGE LOAD TIMING SUMMARY');
  console.log('═══════════════════════════════════════════════════════');
  console.log(`Phase 1 (parallel UI + core):   ${(phase1End - phase1Start).toFixed(2)}ms`);
  console.log(`Phase 2 (editor + PDF):          ${(phase2End - phase2Start).toFixed(2)}ms`);
  console.log(`Phase 3 (event handlers):        ${(phase3End - phase3Start).toFixed(2)}ms`);
  console.log('───────────────────────────────────────────────────────');
  console.log(`TOTAL:                           ${(totalEnd - totalStart).toFixed(2)}ms`);
  console.log('═══════════════════════════════════════════════════════\n');

  console.log("[Writer] Editor initialized successfully");
  console.log(
    "[Writer] Using editor type:",
    editor?.getEditorType?.() || "CodeMirror",
  );

  // Restore saved pane state with increased delay to ensure all DOM elements are ready
  setTimeout(() => {
    try {
      // Check URL parameters first (highest priority)
      const urlParams = new URLSearchParams(window.location.search);
      let targetPane: string | null = null;

      // Check for panel parameter (?panel=citations, ?panel=pdf, etc.)
      if (urlParams.has('panel')) {
        targetPane = urlParams.get('panel');
        console.log("[Writer] URL parameter 'panel' found:", targetPane);
      }
      // Also support shorthand parameters (?pdf, ?citations, ?figures, ?tables, ?history)
      else if (urlParams.has('pdf')) {
        targetPane = 'pdf';
        console.log("[Writer] URL shorthand parameter 'pdf' found");
      } else if (urlParams.has('citations')) {
        targetPane = 'citations';
        console.log("[Writer] URL shorthand parameter 'citations' found");
      } else if (urlParams.has('figures')) {
        targetPane = 'figures';
        console.log("[Writer] URL shorthand parameter 'figures' found");
      } else if (urlParams.has('tables')) {
        targetPane = 'tables';
        console.log("[Writer] URL shorthand parameter 'tables' found");
      } else if (urlParams.has('history')) {
        targetPane = 'history';
        console.log("[Writer] URL shorthand parameter 'history' found");
      } else if (urlParams.has('collaboration')) {
        targetPane = 'collaboration';
        console.log("[Writer] URL shorthand parameter 'collaboration' found");
      }

      // Fallback to saved state if no URL parameter
      if (!targetPane) {
        targetPane = statePersistence.getSavedActivePane();
        console.log("[Writer] No URL parameter, using saved pane:", targetPane);
      }

      console.log("[Writer] === PANE RESTORATION START ===");
      console.log("[Writer] Target pane value:", targetPane);
      console.log("[Writer] Target pane type:", typeof targetPane);

      if (targetPane === "citations") {
        console.log("[Writer] Switching to citations pane...");
        switchRightPanel("citations");
        console.log("[Writer] ✓ Restored citations pane");
      } else if (targetPane === "figures") {
        console.log("[Writer] Switching to figures pane...");
        switchRightPanel("figures");
        console.log("[Writer] ✓ Restored figures pane");
      } else if (targetPane === "tables") {
        console.log("[Writer] Switching to tables pane...");
        switchRightPanel("tables");
        console.log("[Writer] ✓ Restored tables pane");
      } else if (targetPane === "history") {
        console.log("[Writer] Switching to history pane...");
        switchRightPanel("history");
        console.log("[Writer] ✓ Restored history pane");
      } else if (targetPane === "collaboration") {
        console.log("[Writer] Switching to collaboration pane...");
        switchRightPanel("collaboration");
        console.log("[Writer] ✓ Restored collaboration pane");
      } else if (targetPane === "pdf") {
        console.log("[Writer] Switching to PDF pane...");
        switchRightPanel("pdf");
        console.log("[Writer] ✓ Restored PDF pane");
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
 * Module-level PDF preview manager (initialized in main)
 */
let modulePdfPreviewManager: PDFPreviewManager | null = null;

// Export functions to global scope for ES6 module compatibility
(window as any).populateSectionDropdownDirect = populateSectionDropdownDirect;

// Create global PanelSwitcher instance
const globalPanelSwitcher = new PanelSwitcher();

// Export download handlers from module
(window as any).handleDownloadFullPDF = handleDownloadFullPDF;
(window as any).handleDownloadCurrentPDF = handleDownloadCurrentPDF;
(window as any).handleDownloadCitationsBibTeX = handleDownloadCitationsBibTeX;
(window as any).handleDownloadSectionPDF = handleDownloadSectionPDF;

// Export switchRightPanel using PanelSwitcher module
(window as any).switchRightPanel = (view: "pdf" | "citations" | "figures" | "tables" | "history" | "collaboration") => {
  globalPanelSwitcher.switchPanel(view);
};

// Re-export handleCompileFull for modules that import from index.js
export { handleCompileFull };
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
(window as any).handleCompilationLogStart = handleCompilationLogStart;
(window as any).handleCompilationLogStop = handleCompilationLogStop;
(window as any).handleCompilationLogClose = handleCompilationLogClose;
(window as any).compilationLogs = compilationLogs;
(window as any).updateMinimizedStatus = updateMinimizedStatus;
(window as any).updateStatusLamp = updateStatusLamp;
(window as any).updateSlimProgress = updateSlimProgress;
(window as any).toggleCompilationDetails = toggleCompilationDetails;
(window as any).restoreCompilationStatus = restoreCompilationStatus;
// (window as any).toggleCompilationLog = toggleCompilationLog; // Function not defined
