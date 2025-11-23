/**
 * File Tab Manager
 * Handles tab display, switching, and closing for open files
 */

import type { OpenFile } from "../core/types.js";

export class FileTabManager {
  private openFiles: Map<string, OpenFile>;
  private currentFile: string | null = null;
  private onTabSwitch: (filePath: string) => void;
  private onTabClose: (filePath: string) => void;

  constructor(
    openFiles: Map<string, OpenFile>,
    onTabSwitch: (filePath: string) => void,
    onTabClose: (filePath: string) => void
  ) {
    this.openFiles = openFiles;
    this.onTabSwitch = onTabSwitch;
    this.onTabClose = onTabClose;
  }

  setCurrentFile(filePath: string | null): void {
    this.currentFile = filePath;
    this.updateTabs();
  }

  getCurrentFile(): string | null {
    return this.currentFile;
  }

  updateTabs(): void {
    const tabsContainer = document.getElementById("file-tabs");
    if (!tabsContainer) return;

    // Clear tabs but keep the + button
    const plusBtn = tabsContainer.querySelector("#btn-new-file-tab");
    tabsContainer.innerHTML = "";

    this.openFiles.forEach((file, path) => {
      const tab = document.createElement("div");
      tab.className = `file-tab ${path === this.currentFile ? "active" : ""}`;
      tab.setAttribute("data-file-path", path);

      // File name
      const fileName = path.split("/").pop() || path;
      tab.innerHTML = `
        <span class="file-tab-name">${fileName}</span>
        <span class="file-tab-close">×</span>
      `;

      // Click tab to switch file
      tab.addEventListener("click", (e) => {
        if (!(e.target as HTMLElement).classList.contains("file-tab-close")) {
          this.onTabSwitch(path);
        }
      });

      // Close button
      const closeBtn = tab.querySelector(".file-tab-close");
      closeBtn?.addEventListener("click", (e) => {
        e.stopPropagation();
        this.onTabClose(path);
      });

      tabsContainer.appendChild(tab);
    });

    // Re-add the + button at the end
    if (plusBtn) {
      tabsContainer.appendChild(plusBtn);
    }
  }

  switchToNextTab(): void {
    const tabs = Array.from(this.openFiles.keys());
    if (tabs.length === 0) return;

    const currentIndex = tabs.indexOf(this.currentFile || "");
    const nextIndex = (currentIndex + 1) % tabs.length;
    this.onTabSwitch(tabs[nextIndex]);
  }

  switchToPreviousTab(): void {
    const tabs = Array.from(this.openFiles.keys());
    if (tabs.length === 0) return;

    const currentIndex = tabs.indexOf(this.currentFile || "");
    const prevIndex = (currentIndex - 1 + tabs.length) % tabs.length;
    this.onTabSwitch(tabs[prevIndex]);
  }

  switchToTabByIndex(index: number): void {
    const tabs = Array.from(this.openFiles.keys());
    if (index >= 0 && index < tabs.length) {
      this.onTabSwitch(tabs[index]);
    }
  }

  closeTab(filePath: string): void {
    if (!this.openFiles.has(filePath)) return;

    this.openFiles.delete(filePath);

    // If closing the current file, switch to another tab or scratch
    if (filePath === this.currentFile) {
      const remainingTabs = Array.from(this.openFiles.keys());
      if (remainingTabs.length > 0) {
        // Switch to the first tab
        this.onTabSwitch(remainingTabs[0]);
      } else {
        // No tabs left, switch to scratch
        this.onTabSwitch("*scratch*");
      }
    }

    this.updateTabs();
  }

  hasOpenFiles(): boolean {
    return this.openFiles.size > 0;
  }

  getOpenFilePaths(): string[] {
    return Array.from(this.openFiles.keys());
  }
}
