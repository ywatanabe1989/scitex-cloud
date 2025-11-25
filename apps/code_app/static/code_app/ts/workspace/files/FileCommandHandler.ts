/**
 * File Command Handler
 * Handles user-initiated file/folder CRUD operations
 * Orchestrates: visitor checks, UI modals, file operations, tree refresh, state updates
 */

import type { FileOperations } from "./FileOperations.js";
import type { FileTreeManager } from "./FileTreeManager.js";
import type { FileStateManager } from "./FileStateManager.js";
import type { UIComponents } from "../ui/UIComponents.js";
import type { VisitorManager } from "../auth/VisitorManager.js";

export class FileCommandHandler {
  constructor(
    private fileOperations: FileOperations,
    private fileTreeManager: FileTreeManager,
    private fileStateManager: FileStateManager,
    private uiComponents: UIComponents,
    private visitorManager: VisitorManager
  ) {}

  /**
   * Handle context menu actions
   */
  handleContextMenuAction(action: string, target: string | null): void {
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

  /**
   * Create new file in root directory
   */
  async createNewFile(): Promise<void> {
    // Show one-time warning for visitors
    if (this.visitorManager.isVisitor()) {
      this.visitorManager.showVisitorWarningOnce();
    }

    const fileName = await this.uiComponents.showFileModal(
      "New File",
      "File name:",
      "example.py"
    );

    if (!fileName) return;

    const success = await this.fileOperations.createFile(fileName, "");
    if (success) {
      await this.fileTreeManager.loadFileTree();
      await this.fileStateManager.loadFile(fileName);
    }
  }

  /**
   * Create new folder in root directory
   */
  async createNewFolder(): Promise<void> {
    // Show one-time warning for visitors
    if (this.visitorManager.isVisitor()) {
      this.visitorManager.showVisitorWarningOnce();
    }

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

  /**
   * Rename existing file or folder
   */
  async renameFile(oldPath: string): Promise<void> {
    const newPath = await this.uiComponents.showFileModal(
      "Rename File",
      "New name:",
      oldPath
    );

    if (!newPath || newPath === oldPath) return;

    const success = await this.fileOperations.renameFile(oldPath, newPath);
    if (success) {
      // Update file state manager
      this.fileStateManager.renameOpenFile(oldPath, newPath);
      await this.fileTreeManager.loadFileTree();
    }
  }

  /**
   * Delete file or folder
   */
  async deleteFile(filePath: string): Promise<void> {
    if (!confirm(`Delete ${filePath}?`)) return;

    const success = await this.fileOperations.deleteFile(filePath);
    if (success) {
      this.fileStateManager.closeTab(filePath);
      await this.fileTreeManager.loadFileTree();
    }
  }

  /**
   * Create file in a specific folder (exposed for file tree buttons)
   */
  async createFileInFolder(folderPath: string): Promise<void> {
    // Show one-time warning for visitors
    if (this.visitorManager.isVisitor()) {
      this.visitorManager.showVisitorWarningOnce();
    }

    const fileName = await this.uiComponents.showFileModal(
      "New File",
      "File name:",
      "example.py"
    );

    if (!fileName) return;

    const fullPath = folderPath ? `${folderPath}/${fileName}` : fileName;
    const success = await this.fileOperations.createFile(fullPath, "");
    if (success) {
      await this.fileTreeManager.loadFileTree();
      await this.fileStateManager.loadFile(fullPath);
    }
  }

  /**
   * Create folder in a specific folder (exposed for file tree buttons)
   */
  async createFolderInFolder(parentPath: string): Promise<void> {
    // Show one-time warning for visitors
    if (this.visitorManager.isVisitor()) {
      this.visitorManager.showVisitorWarningOnce();
    }

    const folderName = await this.uiComponents.showFileModal(
      "New Folder",
      "Folder name:",
      "my-folder"
    );

    if (!folderName) return;

    const fullPath = parentPath ? `${parentPath}/${folderName}` : folderName;
    const success = await this.fileOperations.createFolder(fullPath);
    if (success) {
      await this.fileTreeManager.loadFileTree();
    }
  }
}
