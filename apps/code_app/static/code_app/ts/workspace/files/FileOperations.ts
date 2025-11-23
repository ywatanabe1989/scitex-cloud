/**
 * File Operations Manager
 * Handles file CRUD operations (Create, Read, Update, Delete)
 */

import type { EditorConfig, OpenFile } from "../core/types.js";

export class FileOperations {
  private config: EditorConfig;

  constructor(config: EditorConfig) {
    this.config = config;
  }

  async loadFile(filePath: string): Promise<{ content: string; success: boolean }> {
    if (!this.config.currentProject) {
      return { content: "", success: false };
    }

    const { owner, slug } = this.config.currentProject;

    try {
      const response = await fetch(`/${owner}/${slug}/api/file-content/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.config.csrfToken,
        },
        body: JSON.stringify({ file_path: filePath }),
      });

      const data = await response.json();

      if (data.success) {
        return { content: data.content, success: true };
      } else {
        console.error("[FileOperations] Failed to load file:", data.message);
        return { content: "", success: false };
      }
    } catch (err) {
      console.error("[FileOperations] Error loading file:", err);
      return { content: "", success: false };
    }
  }

  async saveFile(filePath: string, content: string): Promise<boolean> {
    if (!this.config.currentProject) return false;

    const { owner, slug } = this.config.currentProject;

    try {
      const response = await fetch(`/${owner}/${slug}/api/save-file/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.config.csrfToken,
        },
        body: JSON.stringify({
          file_path: filePath,
          content: content,
        }),
      });

      const data = await response.json();

      if (data.success) {
        console.log("[FileOperations] File saved:", filePath);
        return true;
      } else {
        console.error("[FileOperations] Save failed:", data.message);
        return false;
      }
    } catch (err) {
      console.error("[FileOperations] Error saving file:", err);
      return false;
    }
  }

  async deleteFile(filePath: string): Promise<boolean> {
    if (!this.config.currentProject) return false;

    const { owner, slug } = this.config.currentProject;

    try {
      const response = await fetch(`/${owner}/${slug}/api/delete-file/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.config.csrfToken,
        },
        body: JSON.stringify({ file_path: filePath }),
      });

      const data = await response.json();

      if (data.success) {
        console.log("[FileOperations] File deleted:", filePath);
        return true;
      } else {
        console.error("[FileOperations] Delete failed:", data.message);
        return false;
      }
    } catch (err) {
      console.error("[FileOperations] Error deleting file:", err);
      return false;
    }
  }

  async createFile(filePath: string, content: string = ""): Promise<boolean> {
    // Create is basically save with default empty content
    return this.saveFile(filePath, content);
  }

  async createFolder(folderPath: string): Promise<boolean> {
    if (!this.config.currentProject) return false;

    const { owner, slug } = this.config.currentProject;

    try {
      const response = await fetch(`/${owner}/${slug}/api/create-folder/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.config.csrfToken,
        },
        body: JSON.stringify({ folder_path: folderPath }),
      });

      const data = await response.json();

      if (data.success) {
        console.log("[FileOperations] Folder created:", folderPath);
        return true;
      } else {
        console.error("[FileOperations] Create folder failed:", data.message);
        return false;
      }
    } catch (err) {
      console.error("[FileOperations] Error creating folder:", err);
      return false;
    }
  }

  async renameFile(oldPath: string, newPath: string): Promise<boolean> {
    if (!this.config.currentProject) return false;

    const { owner, slug } = this.config.currentProject;

    try {
      const response = await fetch(`/${owner}/${slug}/api/rename-file/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.config.csrfToken,
        },
        body: JSON.stringify({
          old_path: oldPath,
          new_path: newPath,
        }),
      });

      const data = await response.json();

      if (data.success) {
        console.log("[FileOperations] File renamed:", oldPath, "->", newPath);
        return true;
      } else {
        console.error("[FileOperations] Rename failed:", data.message);
        return false;
      }
    } catch (err) {
      console.error("[FileOperations] Error renaming file:", err);
      return false;
    }
  }
}
