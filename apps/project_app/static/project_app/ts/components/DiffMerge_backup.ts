/**
 * DiffMerge Component
 *
 * Handles file comparison and merging functionality with:
 * - Drag-and-drop file uploads
 * - Repository file selection
 * - Direct text input
 * - Live diff rendering
 * - Merge operations
 */

interface DiffMergeConfig {
  username: string;
  slug: string;
  apiBaseUrl: string;
}

interface DiffLine {
  content: string;
  type: "header" | "hunk" | "addition" | "deletion" | "context";
}

interface DiffResult {
  success: boolean;
  diff_lines: DiffLine[];
  statistics: {
    additions: number;
    deletions: number;
    total_changes: number;
  };
}

interface MergeResult {
  success: boolean;
  merged_content: string;
  strategy: string;
}

class DiffMerge {
  private config: DiffMergeConfig;
  private leftContent: string = "";
  private rightContent: string = "";
  private leftFilename: string = "left";
  private rightFilename: string = "right";
  private currentSide: "left" | "right" | null = null;

  constructor(config: DiffMergeConfig) {
    this.config = config;
    this.init();
  }

  private init(): void {
    this.setupDragAndDrop();
    this.setupFileInputs();
    this.setupButtons();
    this.setupModal();
  }

  /**
   * Setup drag-and-drop functionality for both sides
   */
  private setupDragAndDrop(): void {
    const setupDropZone = (
      dropZoneId: string,
      side: "left" | "right"
    ): void => {
      const dropZone = document.getElementById(dropZoneId);
      if (!dropZone) return;

      // Prevent default drag behaviors
      ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
        dropZone.addEventListener(eventName, (e) => {
          e.preventDefault();
          e.stopPropagation();
        });
      });

      // Highlight drop zone when item is dragged over it
      ["dragenter", "dragover"].forEach((eventName) => {
        dropZone.addEventListener(eventName, () => {
          dropZone.classList.add("drag-over");
        });
      });

      ["dragleave", "drop"].forEach((eventName) => {
        dropZone.addEventListener(eventName, () => {
          dropZone.classList.remove("drag-over");
        });
      });

      // Handle dropped files
      dropZone.addEventListener("drop", (e: Event) => {
        const dragEvent = e as DragEvent;
        const files = dragEvent.dataTransfer?.files;
        if (files && files.length > 0) {
          this.handleFileUpload(files[0], side);
        }
      });

      // Click to upload
      dropZone.addEventListener("click", () => {
        const fileInput = document.getElementById(
          `${side}-file-input`
        ) as HTMLInputElement;
        if (fileInput) {
          fileInput.click();
        }
      });
    };

    setupDropZone("left-drop-zone", "left");
    setupDropZone("right-drop-zone", "right");
  }

  /**
   * Setup file input change handlers
   */
  private setupFileInputs(): void {
    const setupFileInput = (inputId: string, side: "left" | "right"): void => {
      const fileInput = document.getElementById(inputId) as HTMLInputElement;
      if (!fileInput) return;

      fileInput.addEventListener("change", (e) => {
        const target = e.target as HTMLInputElement;
        const files = target.files;
        if (files && files.length > 0) {
          this.handleFileUpload(files[0], side);
        }
      });
    };

    setupFileInput("left-file-input", "left");
    setupFileInput("right-file-input", "right");
  }

  /**
   * Handle file upload
   */
  private async handleFileUpload(file: File, side: "left" | "right"): Promise<void> {
    try {
      const content = await this.readFileAsText(file);
      this.setContent(content, side, file.name);
      this.showFileInfo(file, side);
    } catch (error) {
      console.error("Error reading file:", error);
      alert(`Error reading file: ${error}`);
    }
  }

  /**
   * Read file as text
   */
  private readFileAsText(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        resolve(e.target?.result as string);
      };
      reader.onerror = (e) => {
        reject(e);
      };
      reader.readAsText(file);
    });
  }

  /**
   * Set content for a side
   */
  private setContent(content: string, side: "left" | "right", filename?: string): void {
    const textarea = document.getElementById(
      `${side}-content`
    ) as HTMLTextAreaElement;
    const dropZone = document.getElementById(`${side}-drop-zone`);

    if (textarea) {
      textarea.value = content;
      if (side === "left") {
        this.leftContent = content;
        if (filename) this.leftFilename = filename;
      } else {
        this.rightContent = content;
        if (filename) this.rightFilename = filename;
      }
    }

    if (dropZone && content) {
      dropZone.classList.add("has-content");
    }
  }

  /**
   * Show file info
   */
  private showFileInfo(file: File, side: "left" | "right"): void {
    const fileInfo = document.getElementById(`${side}-file-info`);
    if (!fileInfo) return;

    const filename = fileInfo.querySelector(".filename");
    const filesize = fileInfo.querySelector(".filesize");

    if (filename) {
      filename.textContent = file.name;
    }

    if (filesize) {
      filesize.textContent = this.formatFileSize(file.size);
    }

    fileInfo.style.display = "flex";
  }

  /**
   * Format file size
   */
  private formatFileSize(bytes: number): string {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i];
  }

  /**
   * Setup button handlers
   */
  private setupButtons(): void {
    // Upload buttons
    document.getElementById("left-upload-file")?.addEventListener("click", (e) => {
      e.stopPropagation();
      const fileInput = document.getElementById("left-file-input") as HTMLInputElement;
      fileInput?.click();
    });

    document.getElementById("right-upload-file")?.addEventListener("click", (e) => {
      e.stopPropagation();
      const fileInput = document.getElementById("right-file-input") as HTMLInputElement;
      fileInput?.click();
    });

    // Clear buttons
    document.getElementById("left-clear")?.addEventListener("click", (e) => {
      e.stopPropagation();
      this.clearSide("left");
    });

    document.getElementById("right-clear")?.addEventListener("click", (e) => {
      e.stopPropagation();
      this.clearSide("right");
    });

    // From repo buttons
    document.getElementById("left-select-from-repo")?.addEventListener("click", (e) => {
      e.stopPropagation();
      this.openFileBrowser("left");
    });

    document.getElementById("right-select-from-repo")?.addEventListener("click", (e) => {
      e.stopPropagation();
      this.openFileBrowser("right");
    });

    // Compute diff button
    document.getElementById("compute-diff")?.addEventListener("click", () => {
      this.computeDiff();
    });

    // Merge buttons
    document.getElementById("merge-left")?.addEventListener("click", () => {
      this.merge("left");
    });

    document.getElementById("merge-right")?.addEventListener("click", () => {
      this.merge("right");
    });

    document.getElementById("merge-manual")?.addEventListener("click", () => {
      this.merge("manual");
    });

    // Download button
    document.getElementById("download-merged")?.addEventListener("click", () => {
      this.downloadMerged();
    });

    // Copy merged button
    document.getElementById("copy-merged")?.addEventListener("click", () => {
      this.copyMerged();
    });

    // Content change handlers
    const leftTextarea = document.getElementById("left-content") as HTMLTextAreaElement;
    const rightTextarea = document.getElementById("right-content") as HTMLTextAreaElement;

    leftTextarea?.addEventListener("input", (e) => {
      const target = e.target as HTMLTextAreaElement;
      this.leftContent = target.value;
      const dropZone = document.getElementById("left-drop-zone");
      if (dropZone) {
        if (target.value) {
          dropZone.classList.add("has-content");
        } else {
          dropZone.classList.remove("has-content");
        }
      }
    });

    rightTextarea?.addEventListener("input", (e) => {
      const target = e.target as HTMLTextAreaElement;
      this.rightContent = target.value;
      const dropZone = document.getElementById("right-drop-zone");
      if (dropZone) {
        if (target.value) {
          dropZone.classList.add("has-content");
        } else {
          dropZone.classList.remove("has-content");
        }
      }
    });
  }

  /**
   * Clear a side
   */
  private clearSide(side: "left" | "right"): void {
    const textarea = document.getElementById(`${side}-content`) as HTMLTextAreaElement;
    const dropZone = document.getElementById(`${side}-drop-zone`);
    const fileInfo = document.getElementById(`${side}-file-info`);

    if (textarea) {
      textarea.value = "";
    }

    if (dropZone) {
      dropZone.classList.remove("has-content");
    }

    if (fileInfo) {
      fileInfo.style.display = "none";
    }

    if (side === "left") {
      this.leftContent = "";
      this.leftFilename = "left";
    } else {
      this.rightContent = "";
      this.rightFilename = "right";
    }
  }

  /**
   * Setup modal for file browser
   */
  private setupModal(): void {
    const modal = document.getElementById("file-browser-modal");
    const closeBtn = modal?.querySelector(".modal-close");

    closeBtn?.addEventListener("click", () => {
      this.closeFileBrowser();
    });

    modal?.addEventListener("click", (e) => {
      if (e.target === modal) {
        this.closeFileBrowser();
      }
    });
  }

  /**
   * Open file browser
   */
  private openFileBrowser(side: "left" | "right"): void {
    this.currentSide = side;
    const modal = document.getElementById("file-browser-modal");
    if (modal) {
      modal.style.display = "flex";
      this.loadFileTree();
    }
  }

  /**
   * Close file browser
   */
  private closeFileBrowser(): void {
    const modal = document.getElementById("file-browser-modal");
    if (modal) {
      modal.style.display = "none";
    }
    this.currentSide = null;
  }

  /**
   * Load file tree
   */
  private async loadFileTree(): Promise<void> {
    const tree = document.getElementById("file-browser-tree");
    if (!tree) return;

    tree.innerHTML = "<p>Loading files...</p>";

    try {
      const response = await fetch(
        `${this.config.apiBaseUrl}api/file-tree/`,
        {
          method: "GET",
          headers: {
            "X-Requested-With": "XMLHttpRequest",
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to load file tree");
      }

      const data = await response.json();
      this.renderFileTree(data, tree);
    } catch (error) {
      console.error("Error loading file tree:", error);
      tree.innerHTML = "<p>Error loading files</p>";
    }
  }

  /**
   * Render file tree
   */
  private renderFileTree(data: any, container: HTMLElement): void {
    container.innerHTML = "";

    const renderNode = (node: any, parent: HTMLElement, path: string = ""): void => {
      const currentPath = path ? `${path}/${node.name}` : node.name;

      if (node.type === "file") {
        const item = document.createElement("div");
        item.className = "file-tree-item";
        item.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M2 1.75C2 .784 2.784 0 3.75 0h6.586c.464 0 .909.184 1.237.513l2.914 2.914c.329.328.513.773.513 1.237v9.586A1.75 1.75 0 0 1 13.25 16h-9.5A1.75 1.75 0 0 1 2 14.25Zm1.75-.25a.25.25 0 0 0-.25.25v12.5c0 .138.112.25.25.25h9.5a.25.25 0 0 0 .25-.25V6h-2.75A1.75 1.75 0 0 1 9 4.25V1.5Zm6.75.062V4.25c0 .138.112.25.25.25h2.688l-.011-.013-2.914-2.914-.013-.011Z"></path>
          </svg>
          <span>${node.name}</span>
        `;
        item.addEventListener("click", () => {
          this.selectFile(currentPath);
        });
        parent.appendChild(item);
      } else if (node.type === "directory" && node.children) {
        const dirContainer = document.createElement("div");
        dirContainer.style.marginLeft = "1rem";

        const dirHeader = document.createElement("div");
        dirHeader.className = "file-tree-item";
        dirHeader.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M.513 1.513A1.75 1.75 0 0 1 1.75 1h3.5c.55 0 1.07.26 1.4.7l.9 1.2a.25.25 0 0 0 .2.1H13a1 1 0 0 1 1 1v.5H2.75a.75.75 0 0 0 0 1.5h11.978a1 1 0 0 1 .994 1.117L15 13.25A1.75 1.75 0 0 1 13.25 15H1.75A1.75 1.75 0 0 1 0 13.25V2.75c0-.464.184-.91.513-1.237Z"></path>
          </svg>
          <strong>${node.name}</strong>
        `;
        parent.appendChild(dirHeader);
        parent.appendChild(dirContainer);

        node.children.forEach((child: any) => {
          renderNode(child, dirContainer, currentPath);
        });
      }
    };

    if (data.children) {
      data.children.forEach((child: any) => {
        renderNode(child, container);
      });
    }
  }

  /**
   * Select file from repository
   */
  private async selectFile(filePath: string): Promise<void> {
    if (!this.currentSide) return;

    try {
      const formData = new FormData();
      formData.append("file_path", filePath);

      const response = await fetch(
        `${this.config.apiBaseUrl}api/load-file-from-repo/`,
        {
          method: "POST",
          headers: {
            "X-CSRFToken": this.getCSRFToken(),
            "X-Requested-With": "XMLHttpRequest",
          },
          body: formData,
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Failed to load file");
      }

      const data = await response.json();
      this.setContent(data.content, this.currentSide, data.filename);
      this.closeFileBrowser();
    } catch (error) {
      console.error("Error loading file:", error);
      alert(`Error loading file: ${error}`);
    }
  }

  /**
   * Compute diff
   */
  private async computeDiff(): Promise<void> {
    const leftTextarea = document.getElementById("left-content") as HTMLTextAreaElement;
    const rightTextarea = document.getElementById("right-content") as HTMLTextAreaElement;

    this.leftContent = leftTextarea?.value || "";
    this.rightContent = rightTextarea?.value || "";

    if (!this.leftContent && !this.rightContent) {
      alert("Please provide content on both sides");
      return;
    }

    try {
      const formData = new FormData();
      formData.append("content_left", this.leftContent);
      formData.append("content_right", this.rightContent);
      formData.append("filename_left", this.leftFilename);
      formData.append("filename_right", this.rightFilename);

      const response = await fetch(
        `${this.config.apiBaseUrl}api/compute-diff/`,
        {
          method: "POST",
          headers: {
            "X-CSRFToken": this.getCSRFToken(),
            "X-Requested-With": "XMLHttpRequest",
          },
          body: formData,
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Failed to compute diff");
      }

      const data: DiffResult = await response.json();
      this.renderDiff(data);
      this.showMergeButtons();
    } catch (error) {
      console.error("Error computing diff:", error);
      alert(`Error computing diff: ${error}`);
    }
  }

  /**
   * Render diff
   */
  private renderDiff(result: DiffResult): void {
    const diffResults = document.getElementById("diff-results");
    const tableBody = document.getElementById("diff-table-body");
    const statsAdditions = document.getElementById("stats-additions");
    const statsDeletions = document.getElementById("stats-deletions");

    if (!diffResults || !tableBody) return;

    // Update statistics
    if (statsAdditions) {
      statsAdditions.textContent = `+${result.statistics.additions} addition${
        result.statistics.additions !== 1 ? "s" : ""
      }`;
    }
    if (statsDeletions) {
      statsDeletions.textContent = `-${result.statistics.deletions} deletion${
        result.statistics.deletions !== 1 ? "s" : ""
      }`;
    }

    // Render diff lines
    tableBody.innerHTML = "";
    result.diff_lines.forEach((line) => {
      if (line.type !== "header") {
        const row = document.createElement("tr");
        row.className = `diff-line ${line.type}`;
        row.innerHTML = `
          <td class="diff-line-num"></td>
          <td class="diff-line-num"></td>
          <td class="diff-line-content">${this.escapeHtml(line.content)}</td>
        `;
        tableBody.appendChild(row);
      }
    });

    diffResults.style.display = "block";
  }

  /**
   * Show merge buttons
   */
  private showMergeButtons(): void {
    document.getElementById("merge-left")!.style.display = "inline-flex";
    document.getElementById("merge-right")!.style.display = "inline-flex";
    document.getElementById("merge-manual")!.style.display = "inline-flex";
  }

  /**
   * Merge
   */
  private async merge(strategy: "left" | "right" | "manual"): Promise<void> {
    try {
      const formData = new FormData();
      formData.append("content_left", this.leftContent);
      formData.append("content_right", this.rightContent);
      formData.append("merge_strategy", strategy);

      const response = await fetch(
        `${this.config.apiBaseUrl}api/merge-contents/`,
        {
          method: "POST",
          headers: {
            "X-CSRFToken": this.getCSRFToken(),
            "X-Requested-With": "XMLHttpRequest",
          },
          body: formData,
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Failed to merge");
      }

      const data: MergeResult = await response.json();
      this.renderMergeResult(data);
    } catch (error) {
      console.error("Error merging:", error);
      alert(`Error merging: ${error}`);
    }
  }

  /**
   * Render merge result
   */
  private renderMergeResult(result: MergeResult): void {
    const mergeResults = document.getElementById("merge-results");
    const mergedContent = document.getElementById("merged-content-display");

    if (!mergeResults || !mergedContent) return;

    mergedContent.textContent = result.merged_content;
    mergeResults.style.display = "block";

    document.getElementById("download-merged")!.style.display = "inline-flex";
  }

  /**
   * Download merged content
   */
  private downloadMerged(): void {
    const mergedContent = document.getElementById("merged-content-display");
    if (!mergedContent) return;

    const content = mergedContent.textContent || "";
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "merged.txt";
    a.click();
    URL.revokeObjectURL(url);
  }

  /**
   * Copy merged content
   */
  private async copyMerged(): Promise<void> {
    const mergedContent = document.getElementById("merged-content-display");
    if (!mergedContent) return;

    const content = mergedContent.textContent || "";
    try {
      await navigator.clipboard.writeText(content);
      alert("Copied to clipboard!");
    } catch (error) {
      console.error("Error copying to clipboard:", error);
      alert("Failed to copy to clipboard");
    }
  }

  /**
   * Get CSRF token
   */
  private getCSRFToken(): string {
    const cookies = document.cookie.split(";");
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split("=");
      if (name === "csrftoken") {
        return value;
      }
    }
    return "";
  }

  /**
   * Escape HTML
   */
  private escapeHtml(text: string): string {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
}

// Make it available globally
(window as any).DiffMerge = DiffMerge;
