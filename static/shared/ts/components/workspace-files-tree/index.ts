/**
 * Workspace Files Tree - Main Export
 * Unified file tree component for all workspace modules
 *
 * Usage:
 * ```typescript
 * import { WorkspaceFilesTree } from '@shared/components/workspace-files-tree';
 *
 * const tree = new WorkspaceFilesTree({
 *   mode: 'code',
 *   containerId: 'file-tree',
 *   username: 'test-user',
 *   slug: 'my-project',
 *   onFileSelect: (path, item) => {
 *     console.log('Selected:', path);
 *   },
 * });
 *
 * await tree.initialize();
 * ```
 */

export { WorkspaceFilesTree } from './WorkspaceFilesTree.js';
export { TreeStateManager } from './TreeState.js';
export { TreeFilter } from './TreeFilter.js';
export { TreeRenderer } from './TreeRenderer.js';
export type {
  TreeItem,
  TreeConfig,
  TreeState,
  FilterConfig,
  WorkspaceMode,
} from './types.js';
export { MODE_FILTERS } from './types.js';
