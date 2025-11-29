/**
 * Workspace Files Tree - Main Component (Refactored)
 * Unified file tree component for all workspace modules
 *
 * Refactored from 940 lines to orchestrator pattern using handler modules.
 * Original: WorkspaceFilesTree_monolithic_backup.ts
 */

import type { TreeItem, TreeConfig, WorkspaceMode } from './types.js';
import { TreeStateManager } from './TreeState.js';
import { TreeFilter } from './TreeFilter.js';
import { TreeRenderer } from './TreeRenderer.js';
import { TreeNavigation } from './TreeNavigation.js';
import { EventHandlers } from './handlers/EventHandlers.js';
import { DragDropHandlers } from './handlers/DragDropHandlers.js';
import { KeyboardHandlers } from './handlers/KeyboardHandlers.js';
import { FileActions } from './handlers/FileActions.js';

console.log('[DEBUG] WorkspaceFilesTree component loaded (orchestrator pattern)');

export class WorkspaceFilesTree {
  private config: TreeConfig;
  private container: HTMLElement | null = null;
  private stateManager: TreeStateManager;
  private filter: TreeFilter;
  private renderer: TreeRenderer;
  private navigation: TreeNavigation | null = null;
  private eventHandlers: EventHandlers;
  private dragDropHandlers: DragDropHandlers;
  private keyboardHandlers: KeyboardHandlers | null = null;
  private fileActions: FileActions;
  private treeData: TreeItem[] = [];
  private isLoading = false;

  constructor(config: TreeConfig) {
    this.config = {
      showFolderActions: true,
      showGitStatus: true,
      ...config,
    };

    // Initialize core managers
    this.stateManager = new TreeStateManager(config.username, config.slug);
    this.filter = new TreeFilter(config.mode, {
      allowedExtensions: config.allowedExtensions,
      disabledExtensions: config.disabledExtensions,
      hiddenPatterns: config.hiddenPatterns,
    });
    this.renderer = new TreeRenderer(this.config, this.stateManager, this.filter);

    // Initialize handlers
    this.fileActions = new FileActions(
      this.config,
      this.stateManager,
      this.treeData,
      () => this.getCsrfToken(),
      () => this.rerender(),
      (type, detail) => this.emitEvent(type, detail)
    );

    this.eventHandlers = new EventHandlers(
      this.config,
      this.stateManager,
      (path) => this.fileActions.toggleFolder(path),
      (path) => this.fileActions.selectFile(path),
      (path, el) => this.fileActions.startRename(path, el)
    );

    this.dragDropHandlers = new DragDropHandlers(
      this.config,
      () => this.getCsrfToken(),
      () => this.refresh()
    );

    // Subscribe to state changes for cross-tab sync
    this.stateManager.subscribe(() => {
      this.rerender();
    });

    console.log(`[WorkspaceFilesTree] Initialized for mode: ${config.mode}`);
  }

  async initialize(): Promise<void> {
    this.container = document.getElementById(this.config.containerId);
    if (!this.container) {
      console.error(`[WorkspaceFilesTree] Container #${this.config.containerId} not found`);
      return;
    }

    if (this.config.className) {
      this.container.classList.add(this.config.className);
    }
    this.container.classList.add('workspace-files-tree');

    await this.loadTree();
  }

  async loadTree(): Promise<void> {
    if (this.isLoading) return;
    this.isLoading = true;

    try {
      const response = await fetch(`/${this.config.username}/${this.config.slug}/api/file-tree/`);
      const data = await response.json();

      if (data.success) {
        this.treeData = data.tree;
        this.render();
        await this.autoExpandFocusPath();
        this.attachEventListeners();
      } else {
        this.showError(data.error || 'Failed to load file tree');
      }
    } catch (error) {
      console.error('[WorkspaceFilesTree] Error loading tree:', error);
      this.showError('Network error loading file tree');
    } finally {
      this.isLoading = false;
    }
  }

  private render(): void {
    if (!this.container) return;
    this.container.innerHTML = this.renderer.render(this.treeData);
  }

  private rerender(): void {
    this.render();
    this.attachEventListeners();
  }

  private showError(message: string): void {
    if (!this.container) return;
    this.container.innerHTML = `
      <div class="wft-error">
        <i class="fas fa-exclamation-triangle"></i>
        <p>${message}</p>
      </div>
    `;
  }

  private async autoExpandFocusPath(): Promise<void> {
    // Get focus path from state manager for this mode
    const focusPath = this.stateManager.getFocusPath(this.config.mode);
    if (!focusPath) return;

    const parentPaths = this.getParentPaths(focusPath);
    parentPaths.forEach(path => {
      this.stateManager.expand(path);
    });

    this.stateManager.setSelected(focusPath);
    this.rerender();

    await new Promise(resolve => setTimeout(resolve, 100));
    const focusEl = this.container?.querySelector(`[data-path="${focusPath}"]`);
    if (focusEl) {
      focusEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  private attachEventListeners(): void {
    if (!this.container) return;

    this.eventHandlers.attachEventListeners(this.container);
    this.dragDropHandlers.attachDragDropListeners(this.container);

    // Keyboard navigation
    this.keyboardHandlers = new KeyboardHandlers(
      this.config,
      this.stateManager,
      this.container,
      (path) => this.fileActions.toggleFolder(path),
      (path) => this.fileActions.selectFile(path)
    );

    this.container.addEventListener('keydown', (e) => {
      this.keyboardHandlers?.handleKeyboard(e);
    });
  }

  private getCsrfToken(): string {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta?.getAttribute('content') || '';
  }

  private emitEvent(type: string, detail: any): void {
    if (!this.container) return;
    this.container.dispatchEvent(new CustomEvent(type, { detail, bubbles: true }));
  }

  async refresh(): Promise<void> {
    await this.loadTree();
  }

  /**
   * Refresh the tree and expand to show a specific path
   * Useful for showing newly added files in a directory
   */
  async refreshAndExpandPath(path: string): Promise<void> {
    await this.loadTree();

    // Expand all parent directories
    const parentPaths = this.getParentPaths(path);
    parentPaths.forEach(parentPath => {
      this.stateManager.expand(parentPath);
    });

    // Also expand the path itself if it's a directory
    this.stateManager.expand(path);

    // Re-render with expanded state
    this.rerender();

    // Scroll to show the expanded directory
    await new Promise(resolve => setTimeout(resolve, 100));
    const element = this.container?.querySelector(`[data-path="${path}"]`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  private getParentPaths(path: string): string[] {
    const parts = path.split('/');
    const parents: string[] = [];
    for (let i = 1; i < parts.length; i++) {
      parents.push(parts.slice(0, i).join('/'));
    }
    return parents;
  }
}
