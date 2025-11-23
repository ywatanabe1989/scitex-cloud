/**
 * File Tree Setup Module
 * Handles file tree and section dropdown initialization
 */

import { FileTreeManager } from "../../modules/index.js";
import {
  switchSection,
  handleDocTypeSwitch,
  populateSectionDropdownDirect,
} from "../../utils/index.js";
import { loadTexFile } from "../files/FileLoader.js";

export class FileTreeSetup {
  private config: any;
  private editor: any;
  private sectionsManager: any;
  private compilationManager: any;
  private state: any;
  private pdfPreviewManager: any;
  private statePersistence: any;

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
  }

  /**
   * Initialize file tree or section dropdown
   */
  setup(): void {
    // Define shared section/file selection callback
    const onFileSelectHandler = (
      sectionId: string,
      sectionName: string,
    ): void => {
      console.log(
        "[FileTreeSetup] File/section selected:",
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
          "[FileTreeSetup] Detected section ID, switching section:",
          sectionId,
        );
        switchSection(
          this.editor,
          this.sectionsManager,
          this.state,
          sectionId,
        );
      } else if (sectionId.endsWith(".tex")) {
        // It's a file path - load from disk
        console.log(
          "[FileTreeSetup] Detected .tex file, loading from disk:",
          sectionId,
        );
        loadTexFile(sectionId, this.editor);
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
        );
      }
    };

    // Initialize file tree (including demo mode with projectId 0)
    if (
      this.config.projectId !== null &&
      this.config.projectId !== undefined
    ) {
      const fileTreeContainer = document.getElementById("tex-files-list");
      if (fileTreeContainer) {
        this.setupWithFileTree(fileTreeContainer, onFileSelectHandler);
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
   * Setup with file tree container
   */
  private setupWithFileTree(
    fileTreeContainer: HTMLElement,
    onFileSelectHandler: (sectionId: string, sectionName: string) => void,
  ): void {
    const fileTreeManager = new FileTreeManager({
      projectId: this.config.projectId,
      container: fileTreeContainer,
      texFileDropdownId: "texfile-selector",
      onFileSelect: onFileSelectHandler,
    });

    // Restore saved doctype
    const savedDoctype = this.statePersistence.getSavedDoctype();
    const docTypeSelector = document.getElementById(
      "doctype-selector",
    ) as HTMLSelectElement;
    if (docTypeSelector && savedDoctype) {
      docTypeSelector.value = savedDoctype;
      console.log("[FileTreeSetup] Restored saved doctype:", savedDoctype);
    }

    // Load file tree
    fileTreeManager.load().catch((error) => {
      console.warn("[FileTreeSetup] Failed to load file tree:", error);
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
          // Update section dropdown for the new document type
          fileTreeManager.updateForDocType(newDocType);
          // Update PDF preview manager to use the new document type
          this.pdfPreviewManager.setDocType(newDocType);
          // Switch to first section of the new document type
          handleDocTypeSwitch(
            this.editor,
            this.sectionsManager,
            this.state,
            newDocType,
          );
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
}
