/**
 * Workspace Files Tree - HTML Renderer
 * Renders tree items as HTML with icons, status indicators, and actions
 */

import type { TreeItem, TreeConfig } from './types.js';
import type { TreeStateManager } from './TreeState.js';
import type { TreeFilter } from './TreeFilter.js';
import { getFileIcon, getFolderIcon } from '../../utils/file-icons.js';

export class TreeRenderer {
  private config: TreeConfig;
  private stateManager: TreeStateManager;
  private filter: TreeFilter;

  constructor(config: TreeConfig, stateManager: TreeStateManager, filter: TreeFilter) {
    this.config = config;
    this.stateManager = stateManager;
    this.filter = filter;
  }

  /** Render the entire tree */
  render(items: TreeItem[]): string {
    const filteredItems = this.filter.filterTree(items);
    return `<div class="wft-tree">${this.renderItems(filteredItems, 0)}</div>`;
  }

  /** Render tree items recursively */
  private renderItems(items: TreeItem[], level: number): string {
    let html = '';
    // Base padding for all items (CSS handles indentation via margin-left on wft-children)
    const basePadding = 8;

    for (const item of items) {
      if (item.type === 'directory') {
        html += this.renderFolder(item, basePadding, level);
      } else {
        html += this.renderFile(item, basePadding);
      }
    }

    return html;
  }

  /** Render a folder item */
  private renderFolder(item: TreeItem, indent: number, level: number): string {
    const itemId = this.getItemId(item.path);
    const isExpanded = this.stateManager.isExpanded(item.path);
    const hasChildren = item.children && item.children.length > 0;
    const icon = getFolderIcon();

    let html = `<div class="wft-item wft-folder${isExpanded ? ' expanded' : ''}"
                     data-path="${this.escapeAttr(item.path)}"
                     draggable="true"
                     style="padding-left: ${indent}px;">`;

    // Git gutter (left-side indicator)
    html += this.renderGitGutter(item.git_status);

    // Folder toggle button
    html += `<button type="button" class="wft-folder-toggle" data-action="toggle" data-path="${this.escapeAttr(item.path)}">`;
    if (hasChildren) {
      html += `<span class="wft-chevron${isExpanded ? ' expanded' : ''}"></span>`;
    } else {
      html += `<span class="wft-spacer"></span>`;
    }
    html += `<span class="wft-icon">${icon}</span>`;
    html += `</button>`;

    // Folder name
    html += `<span class="wft-name">${this.escapeHtml(item.name)}`;
    if (item.is_symlink && item.symlink_target) {
      html += `<span class="wft-symlink"> → ${this.escapeHtml(item.symlink_target)}</span>`;
    }
    html += `</span>`;

    // Git status badge
    if (this.config.showGitStatus && item.git_status) {
      html += this.renderGitStatus(item.git_status);
    }

    // Folder actions (new file/folder buttons)
    if (this.config.showFolderActions) {
      html += this.renderFolderActions(item.path);
    }

    html += `</div>`;

    // Children container
    if (hasChildren) {
      const childrenStyle = isExpanded ? '' : 'display: none;';
      html += `<div id="${itemId}" class="wft-children${isExpanded ? ' expanded' : ''}" style="${childrenStyle}">`;
      html += this.renderItems(item.children!, level + 1);
      html += `</div>`;
    }

    return html;
  }

  /** Render a file item */
  private renderFile(item: TreeItem, indent: number): string {
    const isDisabled = this.filter.isDisabled(item);
    const isSelected = this.stateManager.getSelected() === item.path;
    const isTarget = this.stateManager.isTarget(item.path);
    const icon = getFileIcon(item.name);

    const classes = ['wft-item', 'wft-file'];
    if (isDisabled) classes.push('disabled');
    if (isSelected) classes.push('selected');
    if (isTarget) classes.push('target');

    let html = `<div class="${classes.join(' ')}"
                     data-path="${this.escapeAttr(item.path)}"
                     data-action="select"
                     draggable="true"
                     style="padding-left: ${indent}px;">`;

    // Git gutter (left-side indicator)
    html += this.renderGitGutter(item.git_status);

    html += `<span class="wft-spacer"></span>`;
    html += `<span class="wft-icon">${icon}</span>`;
    html += `<span class="wft-name">${this.escapeHtml(item.name)}`;

    if (item.is_symlink && item.symlink_target) {
      html += `<span class="wft-symlink"> → ${this.escapeHtml(item.symlink_target)}</span>`;
    }
    html += `</span>`;

    // Target file indicator (appears before git status)
    if (isTarget) {
      html += `<span class="wft-target-badge" title="Active in editor">●</span>`;
    }

    // Git status badge
    if (this.config.showGitStatus && item.git_status) {
      html += this.renderGitStatus(item.git_status);
    }

    // File actions (delete button)
    if (this.config.showFolderActions) {
      html += this.renderFileActions(item.path);
    }

    html += `</div>`;

    return html;
  }

  /** Render file action buttons */
  private renderFileActions(path: string): string {
    return `<span class="wft-file-actions">
      <button class="wft-action-btn wft-action-rename" data-action="rename" data-path="${this.escapeAttr(path)}" title="Rename">
        <i class="fas fa-pen"></i>
      </button>
      <button class="wft-action-btn wft-action-copy" data-action="copy" data-path="${this.escapeAttr(path)}" title="Duplicate">
        <i class="fas fa-copy"></i>
      </button>
      <button class="wft-action-btn wft-action-delete" data-action="delete" data-path="${this.escapeAttr(path)}" title="Delete">
        <i class="fas fa-trash"></i>
      </button>
    </span>`;
  }

  /** Render git gutter mark (left-side indicator like editor gutters) */
  private renderGitGutter(status: { status: string; staged: boolean } | undefined): string {
    if (!status || !this.config.showGitStatus) {
      return '';
    }

    // Map git status to gutter class and symbol
    const gutterConfig: Record<string, { class: string; symbol: string; title: string }> = {
      'M': { class: 'git-modified', symbol: '~', title: 'Modified' },
      'A': { class: 'git-added', symbol: '+', title: 'Added' },
      'D': { class: 'git-deleted', symbol: '-', title: 'Deleted' },
      '??': { class: 'git-untracked', symbol: '?', title: 'Untracked' },
      'R': { class: 'git-added', symbol: '+', title: 'Renamed' },
      'C': { class: 'git-added', symbol: '+', title: 'Copied' },
    };

    const config = gutterConfig[status.status];
    if (!config) {
      return '';
    }

    return `<span class="wft-git-gutter ${config.class}" title="${config.title}">${config.symbol}</span>`;
  }

  /** Render git status badge */
  private renderGitStatus(status: { status: string; staged: boolean }): string {
    const colors: Record<string, string> = {
      'M': '#e2c08d',   // Modified - orange/yellow
      'A': '#73c991',   // Added - green
      'D': '#f14c4c',   // Deleted - red
      '??': '#73c991',  // Untracked - green
      'R': '#73c991',   // Renamed - green
      'C': '#89d185',   // Copied - green
    };

    const labels: Record<string, string> = {
      'M': 'M',
      'A': 'A',
      'D': 'D',
      '??': 'U',
      'R': 'R',
      'C': 'C',
    };

    const color = colors[status.status] || '#858585';
    const label = labels[status.status] || status.status;
    const title = status.staged ? 'Staged' : 'Modified';

    return `<span class="wft-git-status" style="color: ${color};" title="${title}">${label}</span>`;
  }

  /** Render folder action buttons */
  private renderFolderActions(path: string): string {
    return `<span class="wft-folder-actions">
      <button class="wft-action-btn" data-action="new-file" data-path="${this.escapeAttr(path)}" title="New file">
        <i class="fas fa-file"></i><i class="fas fa-plus"></i>
      </button>
      <button class="wft-action-btn" data-action="new-folder" data-path="${this.escapeAttr(path)}" title="New folder">
        <i class="fas fa-folder"></i><i class="fas fa-plus"></i>
      </button>
      <button class="wft-action-btn wft-action-rename" data-action="rename" data-path="${this.escapeAttr(path)}" title="Rename">
        <i class="fas fa-pen"></i>
      </button>
      <button class="wft-action-btn wft-action-copy" data-action="copy" data-path="${this.escapeAttr(path)}" title="Duplicate">
        <i class="fas fa-copy"></i>
      </button>
      <button class="wft-action-btn wft-action-delete" data-action="delete" data-path="${this.escapeAttr(path)}" title="Delete">
        <i class="fas fa-trash"></i>
      </button>
    </span>`;
  }

  /** Generate unique ID for tree item */
  private getItemId(path: string): string {
    return `wft-${path.replace(/[\/\.]/g, '-')}`;
  }

  /** Escape HTML entities */
  private escapeHtml(str: string): string {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  /** Escape attribute value */
  private escapeAttr(str: string): string {
    return str.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  /** Update selection state in DOM */
  updateSelection(oldPath: string | null, newPath: string | null): void {
    if (oldPath) {
      const oldEl = document.querySelector(`.wft-file[data-path="${oldPath}"]`);
      oldEl?.classList.remove('selected');
    }
    if (newPath) {
      const newEl = document.querySelector(`.wft-file[data-path="${newPath}"]`);
      newEl?.classList.add('selected');
    }
  }

  /** Update folder expansion state in DOM */
  updateFolderExpansion(path: string, expanded: boolean): void {
    const itemId = this.getItemId(path);
    const childrenEl = document.getElementById(itemId);
    const folderEl = document.querySelector(`.wft-folder[data-path="${path}"]`);
    const chevron = folderEl?.querySelector('.wft-chevron');

    if (childrenEl) {
      childrenEl.style.display = expanded ? '' : 'none';
      childrenEl.classList.toggle('expanded', expanded);
    }
    if (folderEl) {
      folderEl.classList.toggle('expanded', expanded);
    }
    if (chevron) {
      chevron.classList.toggle('expanded', expanded);
    }
  }
}
