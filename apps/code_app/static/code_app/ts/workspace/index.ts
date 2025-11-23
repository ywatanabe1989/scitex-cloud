/**
 * Workspace Orchestrator
 * Main coordinator for the Code Workspace - wires all managers together
 */

import { MonacoManager } from "./editor/MonacoManager.js";
import { PTYManager } from "./terminal/PTYManager.js";
import { FileTreeManager } from "./files/FileTreeManager.js";
import { FileOperations } from "./files/FileOperations.js";
import { FileTabManager } from "./files/FileTabManager.js";
import { GitStatusManager } from "./git/GitStatusManager.js";
import { GitOperations } from "./git/GitOperations.js";
import { UIComponents } from "./ui/UIComponents.js";
import { DEFAULT_SCRATCH_CONTENT, type EditorConfig, type OpenFile } from "./core/types.js";

export class WorkspaceOrchestrator {
  private config: EditorConfig;

  // Managers
  private monacoManager: MonacoManager;
  private ptyManager: PTYManager;
  private fileTreeManager: FileTreeManager;
  private fileOperations: FileOperations;
  private fileTabManager: FileTabManager;
  private gitStatusManager: GitStatusManager;
  private gitOperations: GitOperations;
  private uiComponents: UIComponents;

  // State
  private openFiles: Map<string, OpenFile> = new Map();
  private currentFile: string | null = null;

  constructor(config: EditorConfig) {
    this.config = config;

    // Initialize managers
    this.monacoManager = new MonacoManager(config);
    this.ptyManager = new PTYManager(config);
    this.fileOperations = new FileOperations(config);
    this.gitStatusManager = new GitStatusManager(config);
    this.gitOperations = new GitOperations(config);

    this.fileTreeManager = new FileTreeManager(config, this.handleFileClick.bind(this));
    this.fileTabManager = new FileTabManager(
      this.openFiles,
      this.switchToFile.bind(this),
      this.closeTab.bind(this)
    );
    this.uiComponents = new UIComponents(
      config,
      this.handleContextMenuAction.bind(this)
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

    await Promise.all([
      this.fileTreeManager.loadFileTree(),
      this.initScratchBuffer(),
      this.ptyManager.initialize(),
    ]);

    const endTime = performance.now();
    console.log(`[WorkspaceOrchestrator] All components initialized in ${Math.round(endTime - startTime)}ms`);
  }

  private async initScratchBuffer(): Promise<void> {
    await this.monacoManager.initialize("python");

    const editor = this.monacoManager.getEditor();
    if (!editor) return;

    // Show monaco editor, hide media preview
    const monacoEditor = document.getElementById("monaco-editor");
    const mediaPreview = document.getElementById("media-preview");
    if (monacoEditor) monacoEditor.style.display = "block";
    if (mediaPreview) mediaPreview.style.display = "none";

    // Get default scratch content
    const scratchContent = this.getScratchContent();
    editor.setValue(scratchContent);

    // Add scratch buffer to open files
    this.currentFile = "*scratch*";
    this.openFiles.set("*scratch*", {
      path: "*scratch*",
      content: scratchContent,
      language: "python",
    });

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

    this.fileTabManager.setCurrentFile(this.currentFile);
    this.fileTabManager.updateTabs();
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
    const sshPort = isDev ? "2222" : "2222";

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

  private handleFileClick(filePath: string): void {
    this.loadFile(filePath);
  }

  private async loadFile(filePath: string): Promise<void> {
    // Check if already open
    if (this.openFiles.has(filePath)) {
      this.switchToFile(filePath);
      return;
    }

    // Load from server
    const result = await this.fileOperations.loadFile(filePath);
    if (!result.success) {
      console.error(`[WorkspaceOrchestrator] Failed to load file: ${filePath}`);
      return;
    }

    const language = this.monacoManager.detectLanguage(filePath, result.content);

    // Add to open files
    this.openFiles.set(filePath, {
      path: filePath,
      content: result.content,
      language: language,
    });

    // Switch to the file
    await this.switchToFile(filePath);
  }

  private async switchToFile(filePath: string): Promise<void> {
    const fileData = this.openFiles.get(filePath);
    if (!fileData) return;

    const editor = this.monacoManager.getEditor();
    if (!editor) return;

    // Save current file content before switching
    if (this.currentFile && this.currentFile !== filePath) {
      const currentData = this.openFiles.get(this.currentFile);
      if (currentData) {
        currentData.content = editor.getValue();
      }
    }

    // Switch to new file
    this.currentFile = filePath;
    editor.setValue(fileData.content);

    // Update Monaco language
    const monaco = (window as any).monaco;
    if (monaco) {
      const model = editor.getModel();
      if (model) {
        monaco.editor.setModelLanguage(model, fileData.language);
      }
    }

    // Update UI
    const toolbarFilePath = document.getElementById("toolbar-file-path");
    if (toolbarFilePath) {
      toolbarFilePath.textContent = filePath;
    }

    // Update tabs
    this.fileTabManager.setCurrentFile(filePath);

    // Update git decorations
    await this.gitStatusManager.updateGitDecorations(filePath, editor);

    console.log(`[WorkspaceOrchestrator] Switched to file: ${filePath}`);
  }

  private closeTab(filePath: string): void {
    this.fileTabManager.closeTab(filePath);
  }

  private async saveFile(): Promise<void> {
    if (!this.currentFile || this.currentFile === "*scratch*") {
      console.log("[WorkspaceOrchestrator] Cannot save scratch buffer");
      return;
    }

    const editor = this.monacoManager.getEditor();
    if (!editor) return;

    const content = editor.getValue();
    const success = await this.fileOperations.saveFile(this.currentFile, content);

    if (success) {
      // Update in-memory content
      const fileData = this.openFiles.get(this.currentFile);
      if (fileData) {
        fileData.content = content;
      }

      // Update git status and decorations
      await this.gitStatusManager.updateGitStatus();
      await this.gitStatusManager.updateGitDecorations(this.currentFile, editor);
    }
  }

  private handleContextMenuAction(action: string, target: string | null): void {
    // Fire and forget - async operations handled internally
    switch (action) {
      case "new-file":
        this.createNewFile();
        break;
      case "new-folder":
        this.createNewFolder();
        break;
      case "rename":
        if (target) this.renameFile(target);
        break;
      case "delete":
        if (target) this.deleteFile(target);
        break;
    }
  }

  private async createNewFile(): Promise<void> {
    const fileName = await this.uiComponents.showFileModal(
      "New File",
      "File name:",
      "example.py"
    );

    if (!fileName) return;

    const success = await this.fileOperations.createFile(fileName, "");
    if (success) {
      await this.fileTreeManager.loadFileTree();
      await this.loadFile(fileName);
    }
  }

  private async createNewFolder(): Promise<void> {
    const folderName = await this.uiComponents.showFileModal(
      "New Folder",
      "Folder name:",
      "my-folder"
    );

    if (!folderName) return;

    const success = await this.fileOperations.createFolder(folderName);
    if (success) {
      await this.fileTreeManager.loadFileTree();
    }
  }

  private async renameFile(oldPath: string): Promise<void> {
    const newPath = await this.uiComponents.showFileModal(
      "Rename File",
      "New name:",
      oldPath
    );

    if (!newPath || newPath === oldPath) return;

    const success = await this.fileOperations.renameFile(oldPath, newPath);
    if (success) {
      // Update open files map
      if (this.openFiles.has(oldPath)) {
        const fileData = this.openFiles.get(oldPath)!;
        this.openFiles.delete(oldPath);
        fileData.path = newPath;
        this.openFiles.set(newPath, fileData);
      }

      if (this.currentFile === oldPath) {
        this.currentFile = newPath;
      }

      await this.fileTreeManager.loadFileTree();
      this.fileTabManager.setCurrentFile(this.currentFile);
    }
  }

  private async deleteFile(filePath: string): Promise<void> {
    if (!confirm(`Delete ${filePath}?`)) return;

    const success = await this.fileOperations.deleteFile(filePath);
    if (success) {
      this.closeTab(filePath);
      await this.fileTreeManager.loadFileTree();
    }
  }

  private attachEventListeners(): void {
    // Save button
    const btnSave = document.getElementById("btn-save");
    btnSave?.addEventListener("click", () => this.saveFile());

    // New file button
    const btnNewFile = document.getElementById("btn-new-file-tab");
    btnNewFile?.addEventListener("click", () => this.createNewFile());

    // Delete button
    const btnDelete = document.getElementById("btn-delete");
    btnDelete?.addEventListener("click", () => {
      if (this.currentFile && this.currentFile !== "*scratch*") {
        this.deleteFile(this.currentFile);
      }
    });

    // Keyboard shortcuts
    document.addEventListener("keydown", (e) => {
      // Ctrl+S: Save
      if (e.ctrlKey && e.key === "s") {
        e.preventDefault();
        this.saveFile();
      }

      // Ctrl+N: New file
      if (e.ctrlKey && e.key === "n") {
        e.preventDefault();
        this.createNewFile();
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
