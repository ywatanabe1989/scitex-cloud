/**
 * File Tree Setup Module
 * Handles file tree and section dropdown initialization
 *
 * Uses the shared WorkspaceFilesTree component with writer-specific configuration
 * for consistency with other modules (vis, scholar, code).
 */

import {
  switchSection,
  handleDocTypeSwitch,
  populateSectionDropdownDirect,
  syncDropdownsFromPath,
} from "../../utils/index.js";
import { loadTexFile } from "../files/FileLoader.js";
import { initializeWriterFilter } from "../../modules/writer-file-filter.js";
import { PanelSwitcher } from "../ui/PanelSwitcher.js";

// Type for WorkspaceFilesTree (loaded dynamically)
interface WorkspaceFilesTreeType {
  new (config: any): any;
}

export class FileTreeSetup {
  private config: any;
  private editor: any;
  private sectionsManager: any;
  private compilationManager: any;
  private state: any;
  private pdfPreviewManager: any;
  private statePersistence: any;
  private panelSwitcher: PanelSwitcher;

  constructor(
    config: any,
    editor: any,
    sectionsManager: any,
    compilationManager: any,
    state: any,
    pdfPreviewManager: any,
    statePersistence: any,
  ) {
    this.config = config;
    this.editor = editor;
    this.sectionsManager = sectionsManager;
    this.compilationManager = compilationManager;
    this.state = state;
    this.pdfPreviewManager = pdfPreviewManager;
    this.statePersistence = statePersistence;
    this.panelSwitcher = new PanelSwitcher();
  }

  /**
   * Initialize file tree or section dropdown
   */
  setup(): void {
    // Define shared section/file selection callback
    const onFileSelectHandler = async (
      sectionId: string,
      sectionName: string,
    ): Promise<void> => {
      console.log(
        "[FileTreeSetup] File/section selected:",
        sectionName,
        "ID:",
        sectionId,
      );

      // Check if this is a section ID pattern (doctype/section format) or a file path
      // Section IDs follow: {docType}/{sectionName} where doctype is manuscript|supplementary|revision
      // File paths have .tex extension or are in shared/* directories
      const sectionPattern =
        /^(manuscript|supplementary|revision)\/([a-z_]+)$/;
      const sectionMatch = sectionId.match(sectionPattern);

      if (sectionMatch) {
        // It's a section ID - switch section and load corresponding .tex file
        const docType = sectionMatch[1];
        const sectionNameParsed = sectionMatch[2];

        console.log(
          "[FileTreeSetup] Detected section ID, switching section:",
          sectionId,
          "docType:",
          docType,
          "section:",
          sectionNameParsed,
        );

        // Skip loading .tex file for compiled sections (they show PDF directly)
        const isCompiledSection =
          sectionNameParsed === "compiled_pdf" || sectionNameParsed === "compiled_tex";

        let texFilePath: string | null = null;

        if (!isCompiledSection && this.config.projectId) {
          // Get the expected .tex file path
          const { getWriterFilter } = await import("../../modules/writer-file-filter.js");
          const filter = getWriterFilter();
          texFilePath = filter.getExpectedFilePath(docType, sectionNameParsed);
          console.log(
            "[FileTreeSetup] Loading .tex file for section:",
            texFilePath,
          );

          // Load the .tex file content
          loadTexFile(texFilePath, this.editor);

          // Expand file tree to show the corresponding file
          const filesTree = (window as any).writerFileTree;
          if (filesTree && filesTree.expandPath) {
            console.log("[FileTreeSetup] Expanding file tree to:", texFilePath);
            filesTree.expandPath(texFilePath);
          }
        }

        // Also switch section for state management
        switchSection(
          this.editor,
          this.sectionsManager,
          this.state,
          sectionId,
          this.pdfPreviewManager,
        );
      } else if (sectionId.endsWith(".tex")) {
        // It's a file path - load from disk
        console.log(
          "[FileTreeSetup] Detected .tex file, loading from disk:",
          sectionId,
        );
        loadTexFile(sectionId, this.editor);

        // Expand file tree to show the file
        const filesTree = (window as any).writerFileTree;
        if (filesTree && filesTree.expandPath) {
          console.log("[FileTreeSetup] Expanding file tree to:", sectionId);
          filesTree.expandPath(sectionId);
        }
      } else {
        // Fallback: try as section first, then as file
        console.log(
          "[FileTreeSetup] Unknown ID format, trying as section:",
          sectionId,
        );
        switchSection(
          this.editor,
          this.sectionsManager,
          this.state,
          sectionId,
          this.pdfPreviewManager,
        );
      }
    };

    // Initialize file tree (including demo mode with projectId 0)
    if (
      this.config.projectId !== null &&
      this.config.projectId !== undefined
    ) {
      const fileTreeContainer = document.getElementById("writer-file-tree");
      if (fileTreeContainer) {
        // setupWithFileTree is async but we don't need to await here
        this.setupWithFileTree(fileTreeContainer, onFileSelectHandler).catch((error) => {
          console.error("[FileTreeSetup] Failed to setup file tree:", error);
        });
      } else {
        this.setupWithoutFileTree(onFileSelectHandler);
      }
    } else {
      // No projectId - still need to populate dropdown
      console.log(
        "[FileTreeSetup] No project, populating dropdown for demo mode",
      );
      populateSectionDropdownDirect(
        "manuscript",
        onFileSelectHandler,
        this.compilationManager,
        this.state,
      );
    }
  }

  /**
   * Setup with file tree container using shared WorkspaceFilesTree component
   */
  private async setupWithFileTree(
    fileTreeContainer: HTMLElement,
    onFileSelectHandler: (sectionId: string, sectionName: string) => void,
  ): Promise<void> {
    // Restore saved doctype
    const savedDoctype = this.statePersistence.getSavedDoctype();
    const docTypeSelector = document.getElementById(
      "doctype-selector",
    ) as HTMLSelectElement;
    if (docTypeSelector && savedDoctype) {
      docTypeSelector.value = savedDoctype;
      console.log("[FileTreeSetup] Restored saved doctype:", savedDoctype);
    }

    // Initialize writer filter with current doctype
    const currentDoctype = savedDoctype || "manuscript";
    const writerFilter = initializeWriterFilter(currentDoctype, null);
    console.log("[FileTreeSetup] Initialized writer filter with doctype:", currentDoctype);

    // Get project owner and slug from config
    const projectOwner = this.config.projectOwner || this.config.visitorUsername || this.config.username;
    const projectSlug = this.config.projectSlug;

    if (!projectOwner || !projectSlug) {
      console.warn("[FileTreeSetup] Missing project owner or slug, skipping file tree");
      return;
    }

    // Enhanced file select handler that updates section filter and switches panel
    const enhancedFileSelectHandler = (path: string, item: any): void => {
      const fileName = path.split('/').pop() || '';
      console.log("[FileTreeSetup] File selected from tree:", path, fileName);

      // If it's a .tex file, sync dropdowns and update filter
      if (path.endsWith(".tex")) {
        // Sync dropdowns first (updates doctype and section dropdowns visually)
        syncDropdownsFromPath(path);

        const section = writerFilter.extractSectionFromPath(path);
        if (section) {
          console.log("[FileTreeSetup] Extracted section from file path:", section);
          writerFilter.setSection(section);

          // Auto-switch panel based on section
          const currentDoctype = writerFilter.getState().doctype;
          this.panelSwitcher.autoSwitchForSection(section, currentDoctype);
        }
      }

      // Call original handler with path and filename
      onFileSelectHandler(path, fileName);
    };

    try {
      // Check if WorkspaceFilesTree is already initialized by inline script
      // If so, we just need to set up the additional event handlers
      const existingTree = (window as any).writerFileTree;
      if (existingTree) {
        console.log("[FileTreeSetup] WorkspaceFilesTree already initialized by inline script, skipping duplicate initialization");
        // Just set up the refresh button and doctype handlers
        const filesTree = existingTree;
        this.setupTreeEventHandlers(filesTree, writerFilter, docTypeSelector);

        // Focus on the doctype directory (expand it, collapse siblings)
        const initialDoctypeFolder = this.getDoctypeFolder(currentDoctype);
        if (filesTree.focusDirectory) {
          console.log("[FileTreeSetup] Focusing on doctype folder:", initialDoctypeFolder);
          filesTree.focusDirectory(initialDoctypeFolder);
        }

        // Still need to populate section dropdown
        await populateSectionDropdownDirect(
          currentDoctype,
          onFileSelectHandler,
          this.compilationManager,
          this.state,
        );
        return;
      }

      // Dynamically import the shared WorkspaceFilesTree component
      const module = await import("/static/shared/js/components/workspace-files-tree/WorkspaceFilesTree.js") as any;
      const WorkspaceFilesTree: WorkspaceFilesTreeType = module.WorkspaceFilesTree;

      // Create the tree with writer-specific configuration
      const filesTree = new WorkspaceFilesTree({
        mode: 'writer',
        containerId: 'writer-file-tree',
        username: projectOwner,
        slug: projectSlug,
        showFolderActions: true,
        showGitStatus: true,
        allowedExtensions: ['.tex', '.bib', '.cls', '.sty', '.pdf', '.csv', '.xlsx', '.xls', '.png', '.jpg', '.jpeg', '.svg', '.eps', '.bbl', '.bst'],
        onFileSelect: enhancedFileSelectHandler,
      });

      // Initialize the tree
      await filesTree.initialize();

      // Store reference globally for other components
      (window as any).writerFileTree = filesTree;

      // Focus on the doctype directory (expand it, collapse siblings)
      const initialDoctypeFolder = this.getDoctypeFolder(currentDoctype);
      if (filesTree.focusDirectory) {
        console.log("[FileTreeSetup] Focusing on doctype folder:", initialDoctypeFolder);
        filesTree.focusDirectory(initialDoctypeFolder);
      }

      console.log("[FileTreeSetup] WorkspaceFilesTree initialized successfully");

      // Populate section dropdown (must be done even when file tree is present)
      await populateSectionDropdownDirect(
        currentDoctype,
        onFileSelectHandler,
        this.compilationManager,
        this.state,
      );

      // Setup refresh button
      const refreshBtn = document.getElementById("refresh-files-btn");
      if (refreshBtn) {
        refreshBtn.addEventListener("click", () => {
          filesTree.refresh();
        });
      }

      // Listen to document type changes (with file tree)
      if (docTypeSelector) {
        docTypeSelector.addEventListener("change", (e) => {
          const newDocType = (e.target as HTMLSelectElement).value;
          console.log(
            "[FileTreeSetup] Document type changed to:",
            newDocType,
          );
          if (this.editor && this.state.currentSection) {
            // Save current section before switching
            const currentContent = this.editor.getContent();
            this.sectionsManager.setContent(
              this.state.currentSection,
              currentContent,
            );
            // Update state with new document type
            this.state.currentDocType = newDocType;
            // Save doctype to persistence
            this.statePersistence.saveDoctype(newDocType);
            console.log(
              "[FileTreeSetup] Saved doctype to persistence:",
              newDocType,
            );
            // Update filter with new doctype
            writerFilter.setDoctype(newDocType);
            // Update PDF preview manager to use the new document type
            this.pdfPreviewManager.setDocType(newDocType);
            // Switch to first section of the new document type
            handleDocTypeSwitch(
              this.editor,
              this.sectionsManager,
              this.state,
              newDocType,
            );

            // Focus on the selected doctype directory (expand it, collapse siblings)
            const doctypeFolder = this.getDoctypeFolder(newDocType);
            if (doctypeFolder && filesTree.focusDirectory) {
              console.log("[FileTreeSetup] Focusing on doctype folder:", doctypeFolder);
              filesTree.focusDirectory(doctypeFolder);
            }
          }
        });
      }

    } catch (error) {
      console.error("[FileTreeSetup] Failed to initialize WorkspaceFilesTree:", error);
    }
  }

  /**
   * Setup event handlers for an existing tree instance
   */
  private setupTreeEventHandlers(
    filesTree: any,
    writerFilter: any,
    docTypeSelector: HTMLSelectElement | null
  ): void {
    // Setup refresh button
    const refreshBtn = document.getElementById("refresh-files-btn");
    if (refreshBtn) {
      refreshBtn.addEventListener("click", () => {
        filesTree.refresh();
      });
    }

    // Listen to document type changes
    if (docTypeSelector) {
      docTypeSelector.addEventListener("change", (e) => {
        const newDocType = (e.target as HTMLSelectElement).value;
        console.log("[FileTreeSetup] Document type changed to:", newDocType);

        if (this.editor && this.state.currentSection) {
          const currentContent = this.editor.getContent();
          this.sectionsManager.setContent(this.state.currentSection, currentContent);
          this.state.currentDocType = newDocType;
          this.statePersistence.saveDoctype(newDocType);
          writerFilter.setDoctype(newDocType);
          this.pdfPreviewManager.setDocType(newDocType);
          handleDocTypeSwitch(this.editor, this.sectionsManager, this.state, newDocType);

          // Focus on the selected doctype directory (expand it, collapse siblings)
          const doctypeFolder = this.getDoctypeFolder(newDocType);
          if (doctypeFolder && filesTree.focusDirectory) {
            console.log("[FileTreeSetup] Focusing on doctype folder:", doctypeFolder);
            filesTree.focusDirectory(doctypeFolder);
          }
        }
      });
    }
  }

  /**
   * Setup without file tree container (dropdown only)
   */
  private setupWithoutFileTree(
    onFileSelectHandler: (sectionId: string, sectionName: string) => void,
  ): void {
    console.log(
      "[FileTreeSetup] No file tree container, populating dropdown directly",
    );

    // Restore saved doctype
    const savedDoctype = this.statePersistence.getSavedDoctype();
    const initialDoctype = savedDoctype || "manuscript";

    // Set doctype selector to saved value
    const docTypeSelector = document.getElementById(
      "doctype-selector",
    ) as HTMLSelectElement;
    if (docTypeSelector && savedDoctype) {
      docTypeSelector.value = savedDoctype;
      console.log("[FileTreeSetup] Restored saved doctype:", savedDoctype);
    }

    populateSectionDropdownDirect(
      initialDoctype,
      onFileSelectHandler,
      this.compilationManager,
      this.state,
    );

    // Listen to document type changes (without file tree)
    if (docTypeSelector) {
      docTypeSelector.addEventListener("change", async (e) => {
        const newDocType = (e.target as HTMLSelectElement).value;
        console.log(
          "[FileTreeSetup] Document type changed to:",
          newDocType,
          "- updating section dropdown",
        );

        // Save current section content before switching
        if (this.editor && this.state.currentSection) {
          const currentContent = this.editor.getContent();
          this.sectionsManager.setContent(
            this.state.currentSection,
            currentContent,
          );
        }

        // Update state
        this.state.currentDocType = newDocType;

        // Save doctype to persistence
        this.statePersistence.saveDoctype(newDocType);
        console.log(
          "[FileTreeSetup] Saved doctype to persistence:",
          newDocType,
        );

        // Update PDF preview manager doc type
        if (this.pdfPreviewManager) {
          this.pdfPreviewManager.setDocType(newDocType);
        }

        // Repopulate section dropdown for new doc_type
        await populateSectionDropdownDirect(
          newDocType,
          onFileSelectHandler,
          this.compilationManager,
          this.state,
        );
      });
      console.log("[FileTreeSetup] Doc type change handler attached");
    }
  }

  /**
   * Map doctype to folder path (writer-specific logic)
   * @param doctype - manuscript, supplementary, revision, or shared
   * @returns Folder path like 'scitex/writer/01_manuscript'
   */
  private getDoctypeFolder(doctype: string): string {
    const doctypeFolderMap: Record<string, string> = {
      'manuscript': 'scitex/writer/01_manuscript',
      'supplementary': 'scitex/writer/02_supplementary',
      'revision': 'scitex/writer/03_revision',
      'shared': 'scitex/writer/00_shared',
    };
    return doctypeFolderMap[doctype] || 'scitex/writer/01_manuscript';
  }
}
