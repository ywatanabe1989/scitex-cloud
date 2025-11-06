/**
 * Shared File Tree Module
 * Provides reusable file tree building and interaction functionality
 * Corresponds to: Used across multiple pages with file tree sidebars
 */
export interface TreeItem {
    name: string;
    path: string;
    type: 'file' | 'directory';
    children?: TreeItem[];
    is_symlink?: boolean;
    symlink_target?: string;
}
/**
 * Builds HTML for file tree recursively
 * @param items - Array of tree items to render
 * @param username - Project owner username
 * @param slug - Project slug
 * @param level - Current nesting level (0 = root)
 * @returns HTML string for the tree
 */
export declare function buildTreeHTML(items: TreeItem[], username: string, slug: string, level?: number): string;
/**
 * Toggles folder expand/collapse state
 * @param folderId - ID of the folder container to toggle
 * @param event - Optional event to prevent propagation
 */
export declare function toggleFolder(folderId: string, event?: Event): void;
/**
 * Loads file tree from API and renders it
 * @param username - Project owner username
 * @param slug - Project slug
 * @param containerId - ID of container element to render tree into
 */
export declare function loadFileTree(username: string, slug: string, containerId?: string): Promise<void>;
//# sourceMappingURL=file-tree.d.ts.map