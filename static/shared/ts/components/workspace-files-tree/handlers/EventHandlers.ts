/**
 * Event Handlers for WorkspaceFilesTree
 * Handles file/folder click events
 */

import type { TreeItem, TreeConfig } from '../types.js';
import type { TreeStateManager } from '../TreeState.js';

export class EventHandlers {
  constructor(
    private config: TreeConfig,
    private stateManager: TreeStateManager,
    private onToggleFolder: (path: string) => void,
    private onSelectFile: (path: string) => void,
    private onRename: (path: string, el: HTMLElement) => void
  ) {}

  attachEventListeners(container: HTMLElement): void {
    const treeEl = container.querySelector('.wft-tree');
    if (!treeEl) return;

    // File/folder click
    treeEl.addEventListener('click', (e) => {
      const target = e.target as HTMLElement;
      
      // Folder toggle (chevron icon)
      const chevron = target.closest('.wft-folder-chevron');
      if (chevron) {
        e.preventDefault();
        const folderItem = chevron.closest('[data-path]');
        if (folderItem) {
          const path = folderItem.getAttribute('data-path')!;
          this.onToggleFolder(path);
        }
        return;
      }

      // File selection
      const fileItem = target.closest('.wft-file[data-path]');
      if (fileItem && !fileItem.classList.contains('disabled')) {
        e.preventDefault();
        const path = fileItem.getAttribute('data-path')!;
        this.onSelectFile(path);
        return;
      }

      // Folder selection (click on folder name, not chevron)
      const folderItem = target.closest('.wft-folder[data-path]');
      if (folderItem && !folderItem.classList.contains('disabled')) {
        const clickedEl = target.closest('.wft-folder-name');
        if (clickedEl) {
          e.preventDefault();
          const path = folderItem.getAttribute('data-path')!;
          this.onToggleFolder(path);
        }
      }
    });

    // Double-click to rename
    treeEl.addEventListener('dblclick', (e) => {
      const target = e.target as HTMLElement;
      const item = target.closest('[data-path]');
      if (item) {
        e.preventDefault();
        const path = item.getAttribute('data-path')!;
        this.onRename(path, item as HTMLElement);
      }
    });

    // Context menu
    treeEl.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      // Context menu can be implemented here
    });
  }
}
