/**
 * Keyboard Navigation Handlers for WorkspaceFilesTree
 * Handles arrow key navigation and keyboard shortcuts
 */

import type { TreeConfig } from '../types.js';
import type { TreeStateManager } from '../TreeState.js';

export class KeyboardHandlers {
  constructor(
    private config: TreeConfig,
    private stateManager: TreeStateManager,
    private container: HTMLElement,
    private onToggleFolder: (path: string) => void,
    private onSelectFile: (path: string) => void
  ) {}

  handleKeyboard(e: KeyboardEvent): void {
    const selected = this.stateManager.getSelected();
    if (!selected) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        this.navigateTree(1);
        break;
      case 'ArrowUp':
        e.preventDefault();
        this.navigateTree(-1);
        break;
      case 'ArrowRight': {
        e.preventDefault();
        const expanded = this.stateManager.isExpanded(selected);
        if (!expanded) {
          this.onToggleFolder(selected);
        } else {
          this.navigateTree(1); // Move to first child
        }
        break;
      }
      case 'ArrowLeft': {
        e.preventDefault();
        const expanded = this.stateManager.isExpanded(selected);
        if (expanded) {
          this.onToggleFolder(selected);
        } else {
          this.collapseParent(selected);
        }
        break;
      }
      case 'Enter':
        e.preventDefault();
        this.onSelectFile(selected);
        break;
    }
  }

  private navigateTree(direction: number): void {
    const allItems = Array.from(this.container.querySelectorAll('[data-path]:not(.wft-hidden)'));
    const selectedPath = this.stateManager.getSelected();
    const currentIndex = allItems.findIndex(item => item.getAttribute('data-path') === selectedPath);

    if (currentIndex === -1) return;

    const nextIndex = currentIndex + direction;
    if (nextIndex >= 0 && nextIndex < allItems.length) {
      const nextItem = allItems[nextIndex];
      const nextPath = nextItem.getAttribute('data-path')!;

      if (nextItem.classList.contains('wft-file')) {
        this.onSelectFile(nextPath);
      } else {
        this.stateManager.setSelected(nextPath);
      }
    }
  }

  private collapseParent(path: string): void {
    const parts = path.split('/');
    if (parts.length > 1) {
      const parentPath = parts.slice(0, -1).join('/');
      this.onToggleFolder(parentPath);
      this.stateManager.setSelected(parentPath);
    }
  }
}
