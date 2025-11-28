/**
 * Drag and Drop Handlers for WorkspaceFilesTree
 * Handles file/folder drag and drop operations
 */

import type { TreeConfig } from '../types.js';

export class DragDropHandlers {
  constructor(
    private config: TreeConfig,
    private getCsrfToken: () => string,
    private refresh: () => Promise<void>
  ) {}

  attachDragDropListeners(container: HTMLElement): void {
    const treeEl = container.querySelector('.wft-tree');
    if (!treeEl) return;

    // Make items draggable
    treeEl.addEventListener('dragstart', (e) => {
      const target = e.target as HTMLElement;
      const item = target.closest('[data-path]');
      if (item && e.dataTransfer) {
        const path = item.getAttribute('data-path')!;
        e.dataTransfer.setData('text/plain', path);
        e.dataTransfer.effectAllowed = 'move';
        item.classList.add('wft-dragging');
      }
    });

    // Drag over folder
    treeEl.addEventListener('dragover', (e) => {
      e.preventDefault();
      const target = e.target as HTMLElement;
      const folderItem = target.closest('.wft-folder[data-path]');
      if (folderItem && e.dataTransfer) {
        e.dataTransfer.dropEffect = 'move';
        folderItem.classList.add('wft-drop-target');
      }
    });

    // Drag leave
    treeEl.addEventListener('dragleave', (e) => {
      const target = e.target as HTMLElement;
      const folderItem = target.closest('.wft-folder[data-path]');
      if (folderItem) {
        folderItem.classList.remove('wft-drop-target');
      }
    });

    // Drop
    treeEl.addEventListener('drop', async (e) => {
      e.preventDefault();
      const target = e.target as HTMLElement;
      const folderItem = target.closest('.wft-folder[data-path]');
      
      if (folderItem && e.dataTransfer) {
        const sourcePath = e.dataTransfer.getData('text/plain');
        const targetPath = folderItem.getAttribute('data-path')!;
        
        if (sourcePath && targetPath && sourcePath !== targetPath) {
          await this.createSymlink(sourcePath, targetPath);
        }
      }

      // Clean up
      document.querySelectorAll('.wft-dragging, .wft-drop-target').forEach(el => {
        el.classList.remove('wft-dragging');
        el.classList.remove('wft-drop-target');
      });
    });

    // Drag end
    treeEl.addEventListener('dragend', (e) => {
      document.querySelectorAll('.wft-dragging, .wft-drop-target').forEach(el => {
        el.classList.remove('wft-dragging');
        el.classList.remove('wft-drop-target');
      });
    });
  }

  private async createSymlink(sourcePath: string, targetPath: string): Promise<void> {
    try {
      const response = await fetch(`/${this.config.username}/${this.config.slug}/api/files/symlink/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCsrfToken(),
        },
        body: JSON.stringify({ source: sourcePath, target: targetPath }),
      });

      const data = await response.json();
      if (data.success) {
        console.log('[DragDrop] Symlink created successfully');
        await this.refresh();
      } else {
        console.error('[DragDrop] Failed to create symlink:', data.error);
      }
    } catch (error) {
      console.error('[DragDrop] Error creating symlink:', error);
    }
  }
}
