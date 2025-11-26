/**
 * Workspace Files Tree - Filtering
 * Mode-specific filtering for different workspace modules
 *
 * Uses centralized configuration from ModeFilters.ts
 */

import type { TreeItem, FilterConfig, WorkspaceMode } from './types.js';
import { MODE_FILTERS } from './types.js';
import { MODE_FILE_EXTENSIONS, HIDDEN_FOLDERS, ALLOWED_DIRECTORIES, ALWAYS_VISIBLE_FOLDERS } from './ModeFilters.js';
import { ALWAYS_VISIBLE_FILENAMES } from './FilteringCriteria.js';

export class TreeFilter {
  private config: FilterConfig;

  constructor(mode: WorkspaceMode, customConfig?: Partial<FilterConfig>) {
    // Use centralized ModeFilters configuration as default
    const centralExtensions = MODE_FILE_EXTENSIONS[mode];
    const defaultAllowedExtensions = centralExtensions === 'all' ? [] : centralExtensions;
    const defaultHiddenPatterns = HIDDEN_FOLDERS[mode] || [];

    // Fall back to old MODE_FILTERS for backward compatibility
    const legacyDefaults = MODE_FILTERS[mode] || MODE_FILTERS.all;

    this.config = {
      mode,
      allowedExtensions: customConfig?.allowedExtensions ?? defaultAllowedExtensions,
      disabledExtensions: customConfig?.disabledExtensions ?? legacyDefaults.disabledExtensions ?? [],
      hiddenPatterns: customConfig?.hiddenPatterns ?? defaultHiddenPatterns,
    };
  }

  /** Check if a file/folder should be hidden completely */
  isHidden(item: TreeItem): boolean {
    const { name, path, type } = item;

    // ============================================
    // FILTERING CRITERIA (Systematic Order)
    // ============================================

    // 0. ALWAYS VISIBLE FILES (highest priority - bypasses all filtering)
    //    Files like .gitkeep should always be shown
    if (type === 'file' && ALWAYS_VISIBLE_FILENAMES.includes(name)) {
      return false;
    }

    // 1. DIRECTORY WHITELIST (allowed directories)
    //    If path is not within allowed directories, hide it
    if (!this.isWithinAllowedDirectories(path)) {
      return true;
    }

    // 2. DIRECTORY BLACKLIST (hidden folders)
    //    Common system folders to hide
    for (const pattern of this.config.hiddenPatterns) {
      if (name === pattern || path.includes(pattern)) {
        return true;
      }
    }

    // Files pass through (extension filtering done separately)
    return false;
  }

  /**
   * Check if a path is within allowed directories
   * This implements the directory whitelist
   */
  private isWithinAllowedDirectories(path: string): boolean {
    const allowedDirs = ALLOWED_DIRECTORIES[this.config.mode];

    // No restrictions = all directories allowed
    if (allowedDirs.length === 0) {
      return true;
    }

    // Normalize path for comparison
    const normalizedPath = path.replace(/^\.\//, '');

    // Check if path is within or equal to any allowed directory
    const isInAllowedDir = allowedDirs.some(allowedDir => {
      const normalizedAllowedDir = allowedDir.replace(/^\.\//, '');
      return normalizedPath.startsWith(normalizedAllowedDir) ||
             normalizedPath === normalizedAllowedDir;
    });

    if (isInAllowedDir) {
      return true;
    }

    // Check if path is a parent directory of any allowed directory
    // (e.g., 'scitex' is parent of 'scitex/vis', so it should be shown)
    const isParentOfAllowedDir = allowedDirs.some(allowedDir => {
      const normalizedAllowedDir = allowedDir.replace(/^\.\//, '');
      return normalizedAllowedDir.startsWith(normalizedPath + '/');
    });

    return isParentOfAllowedDir;
  }

  /** Check if a file is allowed (can be selected/opened) */
  isAllowed(item: TreeItem): boolean {
    // Directories are always allowed for navigation
    if (item.type === 'directory') {
      return true;
    }

    // Always show files in ALWAYS_VISIBLE_FILENAMES (e.g., .gitkeep)
    if (ALWAYS_VISIBLE_FILENAMES.includes(item.name)) {
      return true;
    }

    // ============================================
    // FILTERING CRITERIA (Systematic Order)
    // ============================================

    // 3. EXTENSION WHITELIST (allowed extensions)
    //    If extension whitelist is specified, only those extensions are allowed
    if (this.config.allowedExtensions.length === 0) {
      return true; // No whitelist = all extensions allowed
    }

    const ext = this.getExtension(item.name);
    return this.config.allowedExtensions.includes(ext);
  }

  /** Check if a file should be grayed out (visible but not selectable) */
  isDisabled(item: TreeItem): boolean {
    if (item.type === 'directory') {
      return false;
    }

    // Never disable files in ALWAYS_VISIBLE_FILENAMES (e.g., .gitkeep)
    if (ALWAYS_VISIBLE_FILENAMES.includes(item.name)) {
      return false;
    }

    const ext = this.getExtension(item.name);

    // ============================================
    // FILTERING CRITERIA (Systematic Order)
    // ============================================

    // 4. EXTENSION BLACKLIST (disabled extensions)
    //    Explicitly disabled extensions are grayed out
    if (this.config.disabledExtensions.includes(ext)) {
      return true;
    }

    // 5. EXTENSION WHITELIST (for disabling)
    //    If allowedExtensions is specified, files NOT in the list are disabled
    if (this.config.allowedExtensions.length > 0 && !this.config.allowedExtensions.includes(ext)) {
      return true;
    }

    return false;
  }

  /** Get file extension including the dot */
  private getExtension(fileName: string): string {
    const lastDot = fileName.lastIndexOf('.');
    if (lastDot === -1) return '';
    return fileName.substring(lastDot).toLowerCase();
  }

  /** Filter tree items recursively */
  filterTree(items: TreeItem[]): TreeItem[] {
    return items
      .filter((item) => !this.isHidden(item))
      .filter((item) => {
        // Apply extension filtering for files (not directories)
        if (item.type === 'file') {
          return this.isAllowed(item);
        }
        return true; // Keep all directories for now
      })
      .map((item) => {
        if (item.type === 'directory' && item.children) {
          return {
            ...item,
            children: this.filterTree(item.children),
          };
        }
        return item;
      })
      // Remove empty directories after filtering children
      // UNLESS they are in ALWAYS_VISIBLE_FOLDERS or match ALLOWED_DIRECTORIES
      .filter((item) => {
        if (item.type === 'directory' && item.children) {
          // Always keep if has children
          if (item.children.length > 0) {
            return true;
          }

          // Check if directory is in ALWAYS_VISIBLE_FOLDERS
          const alwaysVisible = ALWAYS_VISIBLE_FOLDERS[this.config.mode];
          const isAlwaysVisible = alwaysVisible.some(pattern =>
            item.name === pattern || item.path.includes(pattern)
          );
          if (isAlwaysVisible) {
            return true;
          }

          // Check if directory matches ALLOWED_DIRECTORIES (keep root allowed dirs even if empty)
          const allowedDirs = ALLOWED_DIRECTORIES[this.config.mode];
          if (allowedDirs.length > 0) {
            const normalizedPath = item.path.replace(/^\.\//, '');
            const isAllowedDir = allowedDirs.some(allowedDir => {
              const normalizedAllowedDir = allowedDir.replace(/^\.\//, '');
              return normalizedPath === normalizedAllowedDir;
            });
            if (isAllowedDir) {
              return true;
            }
          }

          // Otherwise, remove empty directory
          return false;
        }
        return true;
      });
  }

  /** Get the current mode */
  getMode(): WorkspaceMode {
    return this.config.mode;
  }

  /** Get filter configuration */
  getConfig(): FilterConfig {
    return this.config;
  }

  /** Update allowed extensions */
  setAllowedExtensions(extensions: string[]): void {
    this.config.allowedExtensions = extensions;
  }

  /** Update disabled extensions */
  setDisabledExtensions(extensions: string[]): void {
    this.config.disabledExtensions = extensions;
  }

  /** Update hidden patterns */
  setHiddenPatterns(patterns: string[]): void {
    this.config.hiddenPatterns = patterns;
  }
}
