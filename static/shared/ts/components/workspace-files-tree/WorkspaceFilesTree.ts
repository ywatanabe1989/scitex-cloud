/**
 * Workspace Files Tree - Main Component
 * Unified file tree component for all workspace modules (/code/, /vis/, /writer/, /scholar/)
 *
 * Features:
 * - Mode-specific filtering (show/hide files by extension)
 * - Persistent state (expanded folders, selection) via localStorage
 * - Cross-tab sync of tree state
 * - Git status indicators
 * - Folder action buttons (new file/folder)
 * - Keyboard navigation
 */

import type { TreeItem, TreeConfig, WorkspaceMode } from './types.js';
import { TreeStateManager } from './TreeState.js';
import { TreeFilter } from './TreeFilter.js';
import { TreeRenderer } from './TreeRenderer.js';
import { TreeNavigation } from './TreeNavigation.js';

console.log('[DEBUG] WorkspaceFilesTree component loaded');

export class WorkspaceFilesTree {
  private config: TreeConfig;
  private container: HTMLElement | null = null;
  private stateManager: TreeStateManager;
  private filter: TreeFilter;
  private renderer: TreeRenderer;
  private navigation: TreeNavigation | null = null;
  private treeData: TreeItem[] = [];
  private isLoading = false;

  constructor(config: TreeConfig) {
    this.config = {
      showFolderActions: true,
      showGitStatus: true,
      ...config,
    };

    // Initialize managers
    this.stateManager = new TreeStateManager(config.username, config.slug);
    this.filter = new TreeFilter(config.mode, {
      allowedExtensions: config.allowedExtensions,
      disabledExtensions: config.disabledExtensions,
      hiddenPatterns: config.hiddenPatterns,
    });
    this.renderer = new TreeRenderer(this.config, this.stateManager, this.filter);

    // Subscribe to state changes for cross-tab sync
    this.stateManager.subscribe(() => {
      this.rerender();
    });

    console.log(`[WorkspaceFilesTree] Initialized for mode: ${config.mode}`);
  }

  /** Initialize the tree (load data and render) */
  async initialize(): Promise<void> {
    this.container = document.getElementById(this.config.containerId);
    if (!this.container) {
      console.error(`[WorkspaceFilesTree] Container #${this.config.containerId} not found`);
      return;
    }

    // Add custom class if provided
    if (this.config.className) {
      this.container.classList.add(this.config.className);
    }

    // Add base class
    this.container.classList.add('workspace-files-tree');

    // Initialize navigation manager with mode for focus persistence
    this.navigation = new TreeNavigation(this.container, this.stateManager, this.config.mode);

    // Attach event listeners
    this.attachEventListeners();

    // Load and render tree data
    await this.loadTree();

    // Auto-expand to focus path
    await this.autoExpandFocusPath();

    // Restore scroll position
    const scrollTop = this.stateManager.getScrollTop();
    if (scrollTop > 0) {
      this.container.scrollTop = scrollTop;
    }
  }

  /** Load tree data from API */
  async loadTree(): Promise<void> {
    if (this.isLoading) return;
    this.isLoading = true;

    try {
      const endpoint = this.config.apiEndpoint ||
        `/${this.config.username}/${this.config.slug}/api/file-tree/`;

      console.log(`[WorkspaceFilesTree] Loading tree from: ${endpoint}`);

      const response = await fetch(endpoint);
      const data = await response.json();

      if (data.success && data.tree) {
        this.treeData = data.tree;
        this.render();
        console.log(`[WorkspaceFilesTree] Tree loaded: ${this.treeData.length} root items`);
      } else {
        this.showError('Failed to load file tree');
      }
    } catch (err) {
      console.error('[WorkspaceFilesTree] Failed to load tree:', err);
      this.showError('Error loading file tree');
    } finally {
      this.isLoading = false;
    }
  }

  /** Render the tree */
  private render(): void {
    if (!this.container) return;
    this.container.innerHTML = this.renderer.render(this.treeData);
  }

  /** Re-render the tree (for state sync) */
  private rerender(): void {
    this.render();
  }

  /** Show error message in container */
  private showError(message: string): void {
    if (!this.container) return;
    this.container.innerHTML = `
      <div class="wft-error">
        <i class="fas fa-exclamation-triangle"></i>
        <span>${message}</span>
      </div>
    `;
  }

  /** Auto-expand to focus path (either saved or default for mode) */
  private async autoExpandFocusPath(): Promise<void> {
    // Import DEFAULT_FOCUS_PATHS from centralized filtering criteria
    const { DEFAULT_FOCUS_PATHS } = await import('./FilteringCriteria.js');

    // Get saved focus path for this mode, or use default
    const savedFocus = this.stateManager.getFocusPath(this.config.mode);
    const focusPath = savedFocus || DEFAULT_FOCUS_PATHS[this.config.mode];

    if (focusPath && focusPath !== '.') {
      // Expand all parent folders leading to focus path
      this.stateManager.expandToPath(focusPath);

      // Also expand the focus path itself (unfold the directory)
      this.stateManager.expand(focusPath);

      // Save this as the focus path for this mode
      if (!savedFocus) {
        this.stateManager.setFocusPath(this.config.mode, focusPath);
      }

      // Re-render to show expanded state
      this.render();

      console.log(`[WorkspaceFilesTree] Auto-expanded and unfolded focus: ${focusPath}`);
    }
  }

  /** Attach event listeners */
  private attachEventListeners(): void {
    if (!this.container) return;

    // Click handler for tree items
    this.container.addEventListener('click', (e) => {
      const target = e.target as HTMLElement;

      // Handle new file action (check first to prevent folder toggle)
      const newFileBtn = target.closest('[data-action="new-file"]') as HTMLElement;
      if (newFileBtn) {
        e.stopPropagation();
        const path = newFileBtn.dataset.path;
        if (path) {
          this.emitEvent('new-file', { folderPath: path });
        }
        return;
      }

      // Handle new folder action (check first to prevent folder toggle)
      const newFolderBtn = target.closest('[data-action="new-folder"]') as HTMLElement;
      if (newFolderBtn) {
        e.stopPropagation();
        const path = newFolderBtn.dataset.path;
        if (path) {
          this.emitEvent('new-folder', { folderPath: path });
        }
        return;
      }

      // Handle folder click - toggle on any click on the folder row
      const folderItem = target.closest('.wft-folder') as HTMLElement;
      if (folderItem) {
        const path = folderItem.dataset.path;
        if (path) {
          this.toggleFolder(path);
        }
        return;
      }

      // Handle file selection
      const fileItem = target.closest('.wft-file[data-action="select"]') as HTMLElement;
      if (fileItem && !fileItem.classList.contains('disabled')) {
        const path = fileItem.dataset.path;
        if (path) {
          this.selectFile(path);
        }
        return;
      }
    });

    // Double-click handler for file rename
    this.container.addEventListener('dblclick', (e) => {
      const target = e.target as HTMLElement;

      // Handle file double-click for rename
      const fileItem = target.closest('.wft-file') as HTMLElement;
      if (fileItem && !fileItem.classList.contains('disabled')) {
        const path = fileItem.dataset.path;
        if (path) {
          e.preventDefault();
          this.startRename(path, fileItem);
        }
        return;
      }
    });

    // Track scroll position
    this.container.addEventListener('scroll', () => {
      if (this.container) {
        this.stateManager.setScrollTop(this.container.scrollTop);
      }
    });

    // Keyboard navigation
    this.container.addEventListener('keydown', (e) => {
      this.handleKeyboard(e);
    });
  }

  /** Toggle folder expansion */
  private toggleFolder(path: string): void {
    const expanded = this.stateManager.toggle(path);
    this.renderer.updateFolderExpansion(path, expanded);

    // Update focus path when user manually expands a folder
    if (expanded) {
      this.stateManager.setFocusPath(this.config.mode, path);
      console.log(`[WorkspaceFilesTree] Updated focus to: ${path}`);
    }

    if (this.config.onFolderToggle) {
      this.config.onFolderToggle(path, expanded);
    }
  }

  /** Select a file */
  private selectFile(path: string): void {
    const oldPath = this.stateManager.getSelected();
    this.stateManager.setSelected(path);
    this.renderer.updateSelection(oldPath, path);

    // Find the tree item for callback
    const item = this.findItem(path);
    if (item && this.config.onFileSelect) {
      this.config.onFileSelect(path, item);
    }
  }

  /** Find item by path in tree data */
  private findItem(path: string): TreeItem | null {
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

  /** Handle keyboard navigation */
  private handleKeyboard(e: KeyboardEvent): void {
    const selected = this.stateManager.getSelected();
    if (!selected) return;

    switch (e.key) {
      case 'Enter':
        // Re-trigger selection callback
        const item = this.findItem(selected);
        if (item && this.config.onFileSelect) {
          this.config.onFileSelect(selected, item);
        }
        break;

      case 'ArrowUp':
      case 'ArrowDown':
        e.preventDefault();
        this.navigateTree(e.key === 'ArrowUp' ? -1 : 1);
        break;

      case 'ArrowLeft':
        // Collapse parent folder
        e.preventDefault();
        this.collapseParent(selected);
        break;

      case 'ArrowRight':
        // Expand folder if selected item is a folder
        e.preventDefault();
        const folderItem = this.findItem(selected);
        if (folderItem?.type === 'directory') {
          this.stateManager.expand(selected);
          this.renderer.updateFolderExpansion(selected, true);
        }
        break;
    }
  }

  /** Navigate up/down in tree */
  private navigateTree(direction: number): void {
    const items = this.container?.querySelectorAll('.wft-file:not(.disabled)');
    if (!items || items.length === 0) return;

    const selected = this.stateManager.getSelected();
    let currentIndex = -1;

    items.forEach((item, index) => {
      if ((item as HTMLElement).dataset.path === selected) {
        currentIndex = index;
      }
    });

    const newIndex = Math.max(0, Math.min(items.length - 1, currentIndex + direction));
    const newItem = items[newIndex] as HTMLElement;
    const newPath = newItem.dataset.path;

    if (newPath && newPath !== selected) {
      this.selectFile(newPath);
      newItem.scrollIntoView({ block: 'nearest' });
    }
  }

  /** Collapse parent folder of selected item */
  private collapseParent(path: string): void {
    const lastSlash = path.lastIndexOf('/');
    if (lastSlash > 0) {
      const parentPath = path.substring(0, lastSlash);
      this.stateManager.collapse(parentPath);
      this.renderer.updateFolderExpansion(parentPath, false);
    }
  }

  /** Start inline rename for a file */
  private startRename(path: string, itemEl: HTMLElement): void {
    const nameEl = itemEl.querySelector('.wft-name') as HTMLElement;
    if (!nameEl) return;

    // Get current name (without symlink text)
    const item = this.findItem(path);
    if (!item) return;

    const currentName = item.name;

    // Create input element
    const input = document.createElement('input');
    input.type = 'text';
    input.value = currentName;
    input.className = 'wft-rename-input';
    input.style.cssText = `
      flex: 1;
      background: var(--color-canvas-default, #0d1117);
      border: 1px solid var(--color-accent-fg, #2f81f7);
      border-radius: 3px;
      color: var(--color-fg-default, #f0f3f6);
      font-family: inherit;
      font-size: inherit;
      padding: 1px 4px;
      outline: none;
      min-width: 0;
    `;

    // Store original content for restoration
    const originalHTML = nameEl.innerHTML;

    // Replace name with input
    nameEl.innerHTML = '';
    nameEl.appendChild(input);
    input.focus();
    input.select();

    // Handle completion
    const completeRename = () => {
      const newName = input.value.trim();
      if (newName && newName !== currentName) {
        // Emit rename event with old and new paths
        const dirPath = path.substring(0, path.lastIndexOf('/'));
        const newPath = dirPath ? `${dirPath}/${newName}` : newName;
        this.emitEvent('rename', { oldPath: path, newPath, oldName: currentName, newName });
      }
      // Restore original (actual rename is handled by event listener)
      nameEl.innerHTML = originalHTML;
    };

    // Handle cancel
    const cancelRename = () => {
      nameEl.innerHTML = originalHTML;
    };

    // Event handlers
    input.addEventListener('blur', completeRename);
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        input.blur();
      } else if (e.key === 'Escape') {
        e.preventDefault();
        input.removeEventListener('blur', completeRename);
        cancelRename();
      }
    });
  }

  /** Emit custom event */
  private emitEvent(type: string, detail: any): void {
    const event = new CustomEvent(`workspace-tree:${type}`, { detail });
    this.container?.dispatchEvent(event);
  }

  // ========== Public API ==========

  /** Refresh tree data from API */
  async refresh(): Promise<void> {
    await this.loadTree();
  }

  /** Expand to a specific file path */
  expandToFile(filePath: string): void {
    this.stateManager.expandToPath(filePath);
    this.render();
  }

  /** Select a file programmatically */
  select(path: string): void {
    this.selectFile(path);
  }

  /** Get currently selected path */
  getSelected(): string | null {
    return this.stateManager.getSelected();
  }

  /** Get tree data */
  getTreeData(): TreeItem[] {
    return this.treeData;
  }

  /** Update filter configuration */
  updateFilter(config: { allowedExtensions?: string[]; disabledExtensions?: string[]; hiddenPatterns?: string[] }): void {
    if (config.allowedExtensions) {
      this.filter.setAllowedExtensions(config.allowedExtensions);
    }
    if (config.disabledExtensions) {
      this.filter.setDisabledExtensions(config.disabledExtensions);
    }
    if (config.hiddenPatterns) {
      this.filter.setHiddenPatterns(config.hiddenPatterns);
    }
    this.render();
  }

  /** Change workspace mode */
  setMode(mode: WorkspaceMode): void {
    this.config.mode = mode;
    this.filter = new TreeFilter(mode);
    this.render();
  }

  // ===== Target File API =====

  /** Mark a file as target/active (currently loaded in editor) */
  setTargetFile(path: string): void {
    this.stateManager.setTargets([path]);
    this.render();
    console.log(`[WorkspaceFilesTree] Target file set: ${path}`);
  }

  /** Mark multiple files as targets/active */
  setTargetFiles(paths: string[]): void {
    this.stateManager.setTargets(paths);
    this.render();
    console.log(`[WorkspaceFilesTree] Target files set: ${paths.join(', ')}`);
  }

  /** Add a file to the list of target/active files */
  addTargetFile(path: string): void {
    this.stateManager.addTarget(path);
    this.render();
    console.log(`[WorkspaceFilesTree] Target file added: ${path}`);
  }

  /** Remove a file from the list of target/active files */
  removeTargetFile(path: string): void {
    this.stateManager.removeTarget(path);
    this.render();
    console.log(`[WorkspaceFilesTree] Target file removed: ${path}`);
  }

  /** Clear all target/active files */
  clearTargetFiles(): void {
    this.stateManager.clearTargets();
    this.render();
    console.log('[WorkspaceFilesTree] All target files cleared');
  }

  /** Get all current target/active file paths */
  getTargetFiles(): string[] {
    return Array.from(this.stateManager.getTargets());
  }

  // ===== Tree Manipulation API =====

  /**
   * Scroll to a target file/folder in the tree
   * @param path Path to scroll to
   * @param behavior Scroll behavior ('auto' | 'smooth')
   */
  scrollToTarget(path: string, behavior: ScrollBehavior = 'smooth'): void {
    if (!this.container) return;

    const element = this.container.querySelector(`[data-path="${path}"]`) as HTMLElement;
    if (element) {
      const itemElement = element.closest('.wft-item') as HTMLElement;
      if (itemElement) {
        itemElement.scrollIntoView({ behavior, block: 'center' });
        console.log(`[WorkspaceFilesTree] Scrolled to: ${path}`);
      }
    } else {
      console.warn(`[WorkspaceFilesTree] Target not found for scrolling: ${path}`);
    }
  }

  /**
   * Fold (collapse) a target directory
   * @param path Path to the directory to fold
   */
  foldTarget(path: string): void {
    this.stateManager.collapse(path);
    this.renderer.updateFolderExpansion(path, false);
    console.log(`[WorkspaceFilesTree] Folded: ${path}`);
  }

  /**
   * Unfold (expand) a target directory
   * @param path Path to the directory to unfold
   */
  unfoldTarget(path: string): void {
    this.stateManager.expand(path);
    this.renderer.updateFolderExpansion(path, true);
    console.log(`[WorkspaceFilesTree] Unfolded: ${path}`);
  }

  /**
   * Fold all directories except those in the path to target
   * Useful for focusing on a specific file/folder
   * @param targetPath Path to keep expanded
   */
  foldExceptTarget(targetPath: string): void {
    // Get all expanded paths
    const expandedPaths = this.stateManager.getExpanded();

    // Get parent paths that should remain expanded
    const targetParents = this.getParentPaths(targetPath);

    // Collapse all except target parents
    expandedPaths.forEach(path => {
      if (!targetParents.includes(path) && path !== targetPath) {
        this.stateManager.collapse(path);
      }
    });

    // Ensure target parents are expanded
    targetParents.forEach(path => {
      this.stateManager.expand(path);
    });

    // Re-render to show changes
    this.render();
    console.log(`[WorkspaceFilesTree] Folded all except target: ${targetPath}`);
  }

  /**
   * Focus on a target file/folder
   * This is a combined operation that:
   * 1. Expands all parent directories
   * 2. Scrolls to the target
   * 3. Highlights the target briefly
   * @param path Path to focus on
   * @param highlight Whether to add a brief highlight effect
   */
  focusOnTarget(path: string, highlight: boolean = true): void {
    // Expand to the target
    this.expandToFile(path);

    // Wait for render to complete
    setTimeout(() => {
      // Scroll to target
      this.scrollToTarget(path, 'smooth');

      // Add highlight effect if requested
      if (highlight) {
        setTimeout(() => {
          if (!this.container) return;

          const element = this.container.querySelector(`[data-path="${path}"]`) as HTMLElement;
          if (element) {
            const itemElement = element.closest('.wft-item') as HTMLElement;
            if (itemElement) {
              // Add highlight class
              itemElement.style.transition = 'background-color 0.3s ease';
              itemElement.style.backgroundColor = 'var(--color-accent-subtle, rgba(47, 129, 247, 0.3))';

              // Remove after animation
              setTimeout(() => {
                itemElement.style.backgroundColor = '';
              }, 1000);
            }
          }
        }, 100);
      }
    }, 50);

    console.log(`[WorkspaceFilesTree] Focused on target: ${path}`);
  }

  /**
   * Get all parent directory paths for a given path
   * @param path File or directory path
   * @returns Array of parent paths from root to direct parent
   */
  private getParentPaths(path: string): string[] {
    const parts = path.split('/');
    const parents: string[] = [];

    for (let i = 1; i < parts.length; i++) {
      parents.push(parts.slice(0, i).join('/'));
    }

    return parents;
  }

  // ==========================================================================
  // PUBLIC NAVIGATION API
  // ==========================================================================

  /**
   * Scroll to a specific file/directory
   * @param path - Path to scroll to
   * @param smooth - Whether to use smooth scrolling (default: true)
   */
  scrollTo(path: string, smooth: boolean = true): boolean {
    if (!this.navigation) {
      console.warn('[WorkspaceFilesTree] Navigation not initialized');
      return false;
    }
    return this.navigation.scrollToTarget(path, {
      behavior: smooth ? 'smooth' : 'auto',
    });
  }

  /**
   * Expand a directory
   * @param path - Directory path to expand
   */
  unfold(path: string): boolean {
    if (!this.navigation) return false;
    return this.navigation.unfoldTarget(path);
  }

  /**
   * Collapse a directory
   * @param path - Directory path to collapse
   */
  fold(path: string): boolean {
    if (!this.navigation) return false;
    return this.navigation.foldTarget(path);
  }

  /**
   * Toggle directory expansion
   * @param path - Directory path to toggle
   */
  toggle(path: string): boolean {
    if (!this.navigation) return false;
    return this.navigation.toggleFold(path);
  }

  /**
   * Collapse all directories except those in the path to target
   * @param path - Path to keep expanded
   */
  foldExcept(path: string): void {
    if (!this.navigation) return;
    this.navigation.foldExceptTarget(path);
  }

  /**
   * Focus on a specific file/directory
   * Comprehensive action: expand path, scroll, optionally fold others, highlight
   * @param path - Path to focus on
   * @param options - Focus options
   */
  focus(
    path: string,
    options: {
      foldOthers?: boolean;
      highlight?: boolean;
      smooth?: boolean;
    } = {}
  ): boolean {
    if (!this.navigation) return false;

    return this.navigation.focusOnTarget(path, {
      foldOthers: options.foldOthers ?? false,
      scrollBehavior: options.smooth !== false ? 'smooth' : 'auto',
      highlight: options.highlight !== false,
      highlightDuration: 2000,
      saveFocus: true,
    });
  }

  /**
   * Collapse all directories
   */
  foldAll(): void {
    if (!this.navigation) return;
    this.navigation.foldAll();
  }

  /** Destroy the component */
  destroy(): void {
    if (this.container) {
      this.container.innerHTML = '';
      this.container.classList.remove('workspace-files-tree');
    }
  }
}
