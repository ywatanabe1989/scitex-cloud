/**
 * Workspace Orchestrator
 * Main coordinator for the Code Workspace - wires all managers together
 */

import { MonacoManager } from "./editor/MonacoManager.js";
import { PTYManager } from "./terminal/PTYManager.js";
import { FileTreeManager } from "./files/FileTreeManager.js";
import { FileOperations } from "./files/FileOperations.js";
import { FileTabManager } from "./files/FileTabManager.js";
import { FileStateManager } from "./files/FileStateManager.js";
import { FileCommandHandler } from "./files/FileCommandHandler.js";
import { GitStatusManager } from "./git/GitStatusManager.js";
import { GitOperations } from "./git/GitOperations.js";
import { UIComponents } from "./ui/UIComponents.js";
import { VisitorManager } from "./auth/VisitorManager.js";
import { DEFAULT_SCRATCH_CONTENT, type EditorConfig } from "./core/types.js";

export class WorkspaceOrchestrator {
  private config: EditorConfig;

  // Managers
  private monacoManager: MonacoManager;
  private ptyManager: PTYManager;
  private fileTreeManager: FileTreeManager;
  private fileOperations: FileOperations;
  private fileTabManager: FileTabManager;
  private fileStateManager: FileStateManager;
  private fileCommandHandler: FileCommandHandler;
  private gitStatusManager: GitStatusManager;
  private gitOperations: GitOperations;
  private uiComponents: UIComponents;
  private visitorManager: VisitorManager;

  constructor(config: EditorConfig) {
    this.config = config;

    // Initialize managers
    this.monacoManager = new MonacoManager(config);
    this.ptyManager = new PTYManager(config);
    this.fileOperations = new FileOperations(config);
    this.gitStatusManager = new GitStatusManager(config);
    this.gitOperations = new GitOperations(config);
    this.visitorManager = new VisitorManager(config);

    // Initialize FileTabManager with temporary callbacks (will be updated after FileStateManager)
    this.fileTabManager = new FileTabManager(
      new Map(), // Temporary, will be replaced
      () => {}, // Temporary
      () => {}  // Temporary
    );

    // Initialize FileStateManager (manages file state and switching)
    this.fileStateManager = new FileStateManager(
      this.monacoManager,
      this.fileOperations,
      this.fileTabManager,
      this.gitStatusManager
    );

    // Update FileTabManager with actual callbacks from FileStateManager
    this.fileTabManager = new FileTabManager(
      this.fileStateManager.getOpenFiles(),
      this.fileStateManager.switchToFile.bind(this.fileStateManager),
      this.fileStateManager.closeTab.bind(this.fileStateManager)
    );

    this.fileTreeManager = new FileTreeManager(
      config,
      this.fileStateManager.handleFileClick.bind(this.fileStateManager)
    );

    // Initialize UIComponents with placeholder callback (will delegate to fileCommandHandler)
    this.uiComponents = new UIComponents(
      config,
      this.handleContextMenuAction.bind(this)
    );

    // Initialize FileCommandHandler after all dependencies are ready
    this.fileCommandHandler = new FileCommandHandler(
      this.fileOperations,
      this.fileTreeManager,
      this.fileStateManager,
      this.uiComponents,
      this.visitorManager
    );

    // Start initialization
    this.init().catch(err => {
      console.error("[WorkspaceOrchestrator] Initialization failed:", err);
    });
  }

  private async init(): Promise<void> {
    console.log("[WorkspaceOrchestrator] Initializing...");

    if (!this.config.currentProject) {
      this.uiComponents.showNoProjectMessage();
      return;
    }

    // Synchronous DOM setup
    this.attachEventListeners();
    this.uiComponents.initializeAll();

    // Parallel async initialization
    console.log("[WorkspaceOrchestrator] Starting parallel initialization...");
    const startTime = performance.now();

    try {
      await Promise.all([
        this.fileTreeManager.loadFileTree().catch(err => {
          console.error("[WorkspaceOrchestrator] File tree initialization failed:", err);
        }),
        this.initScratchBuffer().catch(err => {
          console.error("[WorkspaceOrchestrator] Scratch buffer initialization failed:", err);
        }),
        this.ptyManager.initialize().catch(err => {
          console.error("[WorkspaceOrchestrator] PTY initialization failed:", err);
        }),
      ]);

      const endTime = performance.now();
      console.log(`[WorkspaceOrchestrator] All components initialized in ${Math.round(endTime - startTime)}ms`);

      // Set up theme change listeners
      this.setupThemeListeners();
    } catch (err) {
      console.error("[WorkspaceOrchestrator] Critical initialization error:", err);
    }
  }

  /**
   * Setup theme change listeners for Monaco editor and terminal
   */
  private setupThemeListeners(): void {
    document.addEventListener('theme-changed', (event: Event) => {
      const customEvent = event as CustomEvent<{ theme: string }>;
      const theme = customEvent.detail.theme;

      console.log(`[WorkspaceOrchestrator] Theme changed to: ${theme}`);

      // Update Monaco editor theme
      if (this.monacoManager) {
        this.monacoManager.updateTheme(theme);
      }

      // Update terminal theme
      if (this.ptyManager) {
        this.ptyManager.updateTheme();
      }
    });

    console.log('[WorkspaceOrchestrator] Theme change listeners registered');
  }

  private async initScratchBuffer(): Promise<void> {
    console.log("[WorkspaceOrchestrator] Initializing scratch buffer...");

    await this.monacoManager.initialize("python");

    const editor = this.monacoManager.getEditor();
    if (!editor) {
      console.error("[WorkspaceOrchestrator] Editor not available after initialization");
      return;
    }

    // Show monaco editor, hide media preview
    const monacoEditor = document.getElementById("monaco-editor");
    const mediaPreview = document.getElementById("media-preview");
    if (monacoEditor) monacoEditor.style.display = "block";
    if (mediaPreview) mediaPreview.style.display = "none";

    // Get default scratch content
    const scratchContent = this.getScratchContent();
    editor.setValue(scratchContent);

    // Initialize scratch buffer in file state manager
    this.fileStateManager.initializeScratchBuffer(scratchContent);

    const toolbarFilePath = document.getElementById("toolbar-file-path");
    if (toolbarFilePath) {
      toolbarFilePath.textContent = "*scratch*";
    }

    // Enable Run button for scratch
    const btnRun = document.getElementById("btn-run") as HTMLButtonElement;
    if (btnRun) {
      btnRun.disabled = false;
      btnRun.title = "Run: python .scratch_temp.py (Ctrl+Enter)";
    }

    console.log("[WorkspaceOrchestrator] Scratch buffer initialized");
  }

  private getScratchContent(): string {
    const username = this.config.currentProject?.owner || "username";
    const projectName = this.config.currentProject?.name || "your-project";
    const projectSlug = this.config.currentProject?.slug || "your-project";

    const host = window.location.host;
    const protocol = window.location.protocol;
    const workspaceUrl = `${protocol}//${host}/code/`;
    const projectUrl = `${protocol}//${host}/${username}/${projectSlug}/`;
    const sshKeysUrl = `${protocol}//${host}/accounts/settings/ssh-keys/`;

    const isDev = host.includes("127.0.0.1") || host.includes("localhost");
    const sshHost = isDev ? "127.0.0.1" : "scitex.cloud";
    const sshPort = isDev ? "2200" : "2200";

    return `#!/usr/bin/env python3
# SciTeX Code Workspace
#
# Project: ${projectName}
# User:    ${username}
#
# URLs:
#   Workspace:  ${workspaceUrl}
#   Project:    ${projectUrl}
#   SSH Keys:   ${sshKeysUrl}
#
# SSH Access:
#   1. Add SSH key: ${sshKeysUrl}
#   2. Connect:     ssh -p ${sshPort} ${username}@${sshHost}
#
# Keyboard Shortcuts:
#   Ctrl+S         Save file
#   Ctrl+Enter     Run Python file
#   ⌨ button       Show all shortcuts
#   Ctrl+Shift+R   Reset this buffer
#
# Editor Mode: Emacs | Vim | VS Code (toolbar dropdown)

def hello():
    """Example function"""
    print("Hello from SciTeX!")
    print(f"Project: ${projectName}")
    print(f"User: ${username}")
    print(f"SSH: ssh -p ${sshPort} ${username}@${sshHost}")

if __name__ == "__main__":
    hello()
    `;
  }


  /**
   * Delegate context menu actions to FileCommandHandler
   */
  private handleContextMenuAction(action: string, target: string | null): void {
    this.fileCommandHandler.handleContextMenuAction(action, target);
  }


  /**
   * Create file in a specific folder (exposed globally for file tree buttons)
   */
  public async createFileInFolder(folderPath: string): Promise<void> {
    await this.fileCommandHandler.createFileInFolder(folderPath);
  }

  /**
   * Create folder in a specific folder (exposed globally for file tree buttons)
   */
  public async createFolderInFolder(parentPath: string): Promise<void> {
    await this.fileCommandHandler.createFolderInFolder(parentPath);
  }

  private attachEventListeners(): void {
    // Save button
    const btnSave = document.getElementById("btn-save");
    btnSave?.addEventListener("click", () => this.fileStateManager.saveCurrentFile());

    // New file button
    const btnNewFile = document.getElementById("btn-new-file-tab");
    btnNewFile?.addEventListener("click", () => this.fileCommandHandler.createNewFile());

    // Delete button
    const btnDelete = document.getElementById("btn-delete");
    btnDelete?.addEventListener("click", () => {
      const currentFile = this.fileStateManager.getCurrentFile();
      if (currentFile && currentFile !== "*scratch*") {
        this.fileCommandHandler.deleteFile(currentFile);
      }
    });

    // Keyboard shortcuts
    document.addEventListener("keydown", (e) => {
      // Ctrl+S: Save
      if (e.ctrlKey && e.key === "s") {
        e.preventDefault();
        this.fileStateManager.saveCurrentFile();
      }

      // Ctrl+N: New file
      if (e.ctrlKey && e.key === "n") {
        e.preventDefault();
        this.fileCommandHandler.createNewFile();
      }

      // Ctrl+Tab: Next tab
      if (e.ctrlKey && e.key === "Tab") {
        e.preventDefault();
        this.fileTabManager.switchToNextTab();
      }
    });

    // Keybinding mode selector
    const keybindingMode = document.getElementById("keybinding-mode") as HTMLSelectElement;
    keybindingMode?.addEventListener("change", (e) => {
      const mode = (e.target as HTMLSelectElement).value;
      this.monacoManager.setKeybindingMode(mode);
    });

    console.log("[WorkspaceOrchestrator] Event listeners attached");
  }
}

// Note: Initialization is handled by workspace.ts
// This module only exports the WorkspaceOrchestrator class and utilities
