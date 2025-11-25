/**
 * File Tree Manager
 * Handles loading and displaying the project file tree
 */

import { buildCodeTreeHTML } from "../../file-tree-builder.js";
import type { EditorConfig } from "../core/types.js";

export class FileTreeManager {
  private config: EditorConfig;
  private fileList: string[] = [];
  private onFileClick: (filePath: string) => void;

  constructor(config: EditorConfig, onFileClick: (filePath: string) => void) {
    this.config = config;
    this.onFileClick = onFileClick;
  }

  async loadFileTree(): Promise<void> {
    if (!this.config.currentProject) {
      console.warn("[FileTreeManager] No current project, skipping file tree load");
      return;
    }

    const { owner, slug } = this.config.currentProject;
    const url = `/${owner}/${slug}/api/file-tree/`;

    console.log(`[FileTreeManager] Loading file tree from: ${url}`);

    try {
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log("[FileTreeManager] File tree data received:", data);

      const treeContainer = document.getElementById("file-tree");
      if (!treeContainer) {
        console.error("[FileTreeManager] File tree container not found");
        return;
      }

      if (data.success) {
        console.log("[FileTreeManager] Building tree HTML...");
        treeContainer.innerHTML = buildCodeTreeHTML(data.tree, owner, slug);
        this.attachFileClickHandlers();
        this.buildFileList(data.tree);
        console.log("[FileTreeManager] File tree loaded successfully");
      } else {
        console.error("[FileTreeManager] API returned success=false:", data);
        treeContainer.innerHTML = '<div class="tree-loading">Error loading file tree</div>';
      }
    } catch (err) {
      console.error("[FileTreeManager] Failed to load file tree:", err);
      const treeContainer = document.getElementById("file-tree");
      if (treeContainer) {
        treeContainer.innerHTML = `<div class="tree-loading">Error: ${err instanceof Error ? err.message : 'Unknown error'}</div>`;
      }
    }
  }

  private attachFileClickHandlers(): void {
    document.querySelectorAll(".file-tree-file").forEach((fileElement) => {
      fileElement.addEventListener("click", async (e) => {
        e.preventDefault();
        const filePath = fileElement.getAttribute("data-file-path");
        if (filePath) {
          this.onFileClick(filePath);
        }
      });
    });
  }

  private buildFileList(tree: any[], prefix: string = ""): void {
    this.fileList = [];
    const traverse = (items: any[], path: string = "") => {
      items.forEach((item) => {
        const fullPath = path ? `${path}/${item.name}` : item.name;
        this.fileList.push(fullPath);
        if (item.children && item.children.length > 0) {
          traverse(item.children, fullPath);
        }
      });
    };
    traverse(tree);
  }

  getFileList(): string[] {
    return this.fileList;
  }
}
