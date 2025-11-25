/**
 * File State Manager
 * Manages open files, current file state, and file switching
 */

import type { OpenFile } from "../core/types.js";
import { MonacoManager } from "../editor/MonacoManager.js";
import { FileOperations } from "./FileOperations.js";
import { FileTabManager } from "./FileTabManager.js";
import { GitStatusManager } from "../git/GitStatusManager.js";

export class FileStateManager {
  private openFiles: Map<string, OpenFile> = new Map();
  private currentFile: string | null = null;

  constructor(
    private monacoManager: MonacoManager,
    private fileOperations: FileOperations,
    private fileTabManager: FileTabManager,
    private gitStatusManager: GitStatusManager
  ) {}

  /**
   * Handle file click from file tree
   */
  handleFileClick(filePath: string): void {
    this.loadFile(filePath);
  }

  /**
   * Load a file from the server and open it
   */
  async loadFile(filePath: string): Promise<void> {
    // Check if already open
    if (this.openFiles.has(filePath)) {
      this.switchToFile(filePath);
      return;
    }

    // Load from server
    const result = await this.fileOperations.loadFile(filePath);
    if (!result.success) {
      console.error(`[FileStateManager] Failed to load file: ${filePath}`);
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

  /**
   * Switch to an already-open file
   */
  async switchToFile(filePath: string): Promise<void> {
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

    console.log(`[FileStateManager] Switched to file: ${filePath}`);
  }

  /**
   * Close a file tab
   */
  closeTab(filePath: string): void {
    this.openFiles.delete(filePath);
    this.fileTabManager.closeTab(filePath);

    // If closing current file, clear current file state
    if (this.currentFile === filePath) {
      this.currentFile = null;
    }
  }

  /**
   * Save the currently open file
   */
  async saveCurrentFile(): Promise<void> {
    if (!this.currentFile || this.currentFile === "*scratch*") {
      console.log("[FileStateManager] Cannot save scratch buffer");
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

  /**
   * Get the currently active file path
   */
  getCurrentFile(): string | null {
    return this.currentFile;
  }

  /**
   * Get the open files map
   */
  getOpenFiles(): Map<string, OpenFile> {
    return this.openFiles;
  }

  /**
   * Check if a file is currently open
   */
  isFileOpen(filePath: string): boolean {
    return this.openFiles.has(filePath);
  }

  /**
   * Initialize scratch buffer as the current file
   * Used during workspace initialization
   */
  initializeScratchBuffer(content: string): void {
    this.currentFile = "*scratch*";
    this.openFiles.set("*scratch*", {
      path: "*scratch*",
      content: content,
      language: "python",
    });
    this.fileTabManager.setCurrentFile(this.currentFile);
    this.fileTabManager.updateTabs();
  }

  /**
   * Rename a file in the open files map
   * Used when a file is renamed on the server
   */
  renameOpenFile(oldPath: string, newPath: string): void {
    if (this.openFiles.has(oldPath)) {
      const fileData = this.openFiles.get(oldPath)!;
      this.openFiles.delete(oldPath);
      fileData.path = newPath;
      this.openFiles.set(newPath, fileData);
    }

    // Update current file if it was the renamed file
    if (this.currentFile === oldPath) {
      this.currentFile = newPath;
      this.fileTabManager.setCurrentFile(newPath);
    }
  }
}
