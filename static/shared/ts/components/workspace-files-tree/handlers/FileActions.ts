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
    const wasExpanded = this.stateManager.isExpanded(path);
    this.stateManager.toggle(path);

    // Auto-select folder when expanding
    if (!wasExpanded) {
      this.stateManager.setSelected(path);
    }
  }

  selectFile(path: string): void {
    this.stateManager.setSelected(path);
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

  async deleteFile(path: string): Promise<void> {
    // No confirmation - delete directly (files can be recovered via git)
    try {
      const response = await fetch(`/${this.config.username}/${this.config.slug}/api/files/delete/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCsrfToken(),
        },
        body: JSON.stringify({ path }),
      });

      const data = await response.json();
      if (data.success) {
        console.log('[FileActions] File deleted:', path);
        this.emitEvent('file-delete', { path });
        this.rerender();
      } else {
        console.error('[FileActions] Delete failed:', data.error);
        alert(`Failed to delete file: ${data.error}`);
      }
    } catch (error) {
      console.error('[FileActions] Error deleting file:', error);
      alert('Error deleting file. Please try again.');
    }
  }

  async createNewFile(folderPath: string): Promise<void> {
    const fileName = prompt('Enter new file name:');
    if (!fileName || !fileName.trim()) {
      return;
    }

    const newPath = folderPath ? `${folderPath}/${fileName.trim()}` : fileName.trim();

    try {
      const response = await fetch(`/${this.config.username}/${this.config.slug}/api/files/create/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCsrfToken(),
        },
        body: JSON.stringify({ path: newPath, type: 'file' }),
      });

      const data = await response.json();
      if (data.success) {
        console.log('[FileActions] File created:', newPath);
        this.emitEvent('file-create', { path: newPath, type: 'file' });
        // Expand the parent folder
        this.stateManager.expand(folderPath);
        this.rerender();
      } else {
        console.error('[FileActions] Create file failed:', data.error);
        alert(`Failed to create file: ${data.error}`);
      }
    } catch (error) {
      console.error('[FileActions] Error creating file:', error);
      alert('Error creating file. Please try again.');
    }
  }

  async createNewFolder(folderPath: string): Promise<void> {
    const folderName = prompt('Enter new folder name:');
    if (!folderName || !folderName.trim()) {
      return;
    }

    const newPath = folderPath ? `${folderPath}/${folderName.trim()}` : folderName.trim();

    try {
      const response = await fetch(`/${this.config.username}/${this.config.slug}/api/files/create/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCsrfToken(),
        },
        body: JSON.stringify({ path: newPath, type: 'directory' }),
      });

      const data = await response.json();
      if (data.success) {
        console.log('[FileActions] Folder created:', newPath);
        this.emitEvent('folder-create', { path: newPath, type: 'directory' });
        // Expand the parent folder
        this.stateManager.expand(folderPath);
        this.rerender();
      } else {
        console.error('[FileActions] Create folder failed:', data.error);
        alert(`Failed to create folder: ${data.error}`);
      }
    } catch (error) {
      console.error('[FileActions] Error creating folder:', error);
      alert('Error creating folder. Please try again.');
    }
  }

  async copyFile(path: string): Promise<void> {
    const item = this.findItem(path);
    if (!item) return;

    // Generate copy name: file.txt -> file_copy.txt or folder -> folder_copy
    const parts = item.name.split('.');
    let copyName: string;
    if (parts.length > 1 && item.type === 'file') {
      const ext = parts.pop();
      copyName = `${parts.join('.')}_copy.${ext}`;
    } else {
      copyName = `${item.name}_copy`;
    }

    const newName = prompt('Enter name for copy:', copyName);
    if (!newName || !newName.trim()) {
      return;
    }

    // Get parent directory
    const pathParts = path.split('/');
    pathParts.pop();
    const parentPath = pathParts.join('/');
    const newPath = parentPath ? `${parentPath}/${newName.trim()}` : newName.trim();

    try {
      const response = await fetch(`/${this.config.username}/${this.config.slug}/api/files/copy/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCsrfToken(),
        },
        body: JSON.stringify({ source_path: path, dest_path: newPath }),
      });

      const data = await response.json();
      if (data.success) {
        console.log('[FileActions] File copied:', path, '->', newPath);
        this.emitEvent('file-copy', { sourcePath: path, destPath: newPath });
        this.rerender();
      } else {
        console.error('[FileActions] Copy failed:', data.error);
        alert(`Failed to copy: ${data.error}`);
      }
    } catch (error) {
      console.error('[FileActions] Error copying file:', error);
      alert('Error copying file. Please try again.');
    }
  }
}
