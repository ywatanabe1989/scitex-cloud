/**
 * File Actions for WorkspaceFilesTree
 * Handles file/folder operations (toggle, select, rename, etc.)
 */

import type { TreeItem, TreeConfig } from '../types.js';
import type { TreeStateManager } from '../TreeState.js';

export class FileActions {
  constructor(
    private config: TreeConfig,
    private stateManager: TreeStateManager,
    private treeData: TreeItem[],
    private getCsrfToken: () => string,
    private rerender: () => void,
    private emitEvent: (type: string, detail: any) => void
  ) {}

  toggleFolder(path: string): void {
    const isExpanded = this.stateManager.isExpanded(path);
    this.stateManager.setExpanded(path, !isExpanded);
    
    // Auto-select folder when expanding
    if (!isExpanded) {
      this.stateManager.setSelectedPath(path);
    }
  }

  selectFile(path: string): void {
    this.stateManager.setSelectedPath(path);
    this.emitEvent('file-select', { path });
  }

  findItem(path: string): TreeItem | null {
    const search = (items: TreeItem[]): TreeItem | null => {
      for (const item of items) {
        if (item.path === path) return item;
        if (item.children) {
          const found = search(item.children);
          if (found) return found;
        }
      }
      return null;
    };
    return search(this.treeData);
  }

  async startRename(path: string, itemEl: HTMLElement): Promise<void> {
    const item = this.findItem(path);
    if (!item) return;

    const nameEl = itemEl.querySelector('.wft-file-name, .wft-folder-name') as HTMLElement;
    if (!nameEl) return;

    const originalName = item.name;
    const input = document.createElement('input');
    input.type = 'text';
    input.value = originalName;
    input.className = 'wft-rename-input';

    nameEl.replaceWith(input);
    input.focus();
    input.select();

    const finishRename = async (save: boolean) => {
      const newName = input.value.trim();
      input.replaceWith(nameEl);

      if (save && newName && newName !== originalName) {
        await this.performRename(path, newName);
      }
    };

    input.addEventListener('blur', () => finishRename(true));
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        finishRename(true);
      } else if (e.key === 'Escape') {
        e.preventDefault();
        finishRename(false);
      }
    });
  }

  private async performRename(oldPath: string, newName: string): Promise<void> {
    try {
      const response = await fetch(`/${this.config.username}/${this.config.slug}/api/files/rename/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCsrfToken(),
        },
        body: JSON.stringify({ old_path: oldPath, new_name: newName }),
      });

      const data = await response.json();
      if (data.success) {
        this.emitEvent('file-rename', { oldPath, newPath: data.new_path });
        this.rerender();
      } else {
        console.error('[FileActions] Rename failed:', data.error);
      }
    } catch (error) {
      console.error('[FileActions] Error renaming file:', error);
    }
  }
}
