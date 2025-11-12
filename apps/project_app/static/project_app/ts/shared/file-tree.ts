/**
 * Shared File Tree Module
 * Provides reusable file tree building and interaction functionality
 * Corresponds to: Used across multiple pages with file tree sidebars
 */

console.log("[DEBUG] apps/project_app/static/project_app/ts/shared/file-tree.ts loaded");

export interface TreeItem {
    name: string;
    path: string;
    type: 'file' | 'directory';
    children?: TreeItem[];
    is_symlink?: boolean;
    symlink_target?: string;
}

/**
 * Checks if a tree item path is in the current URL path
 * @param itemPath - The path of the tree item
 * @param currentPath - The current URL path
 * @returns True if the item is in the current path
 */
function isInCurrentPath(itemPath: string, currentPath: string): boolean {
    // Normalize paths by removing trailing slashes and decoding URI components
    const normalizedItemPath = decodeURIComponent(itemPath.replace(/\/$/, ''));
    const normalizedCurrentPath = decodeURIComponent(currentPath.replace(/\/$/, ''));

    // Check if current path starts with item path (for directories)
    return normalizedCurrentPath.includes(normalizedItemPath);
}

/**
 * Builds HTML for file tree recursively
 * @param items - Array of tree items to render
 * @param username - Project owner username
 * @param slug - Project slug
 * @param level - Current nesting level (0 = root)
 * @returns HTML string for the tree
 */
export function buildTreeHTML(items: TreeItem[], username: string, slug: string, level: number = 0): string {
    let html = '';
    const indent = level * 8;  // Reduced from 16 to 8 for compact indentation
    const currentPath = window.location.pathname;

    items.forEach((item: TreeItem) => {
        const itemPath = `/${username}/${slug}/${item.path}${item.type === 'directory' ? '/' : ''}`;
        const isActive = currentPath.includes(item.path);

        // Determine if this folder should be auto-expanded (if it's in the current path)
        const shouldExpand = isInCurrentPath(item.path, currentPath);

        // Debug logging
        if (item.type === 'directory' && level < 3) {
            console.log(`[FileTree] ${item.name}: path="${item.path}", currentPath="${currentPath}", shouldExpand=${shouldExpand}`);
        }

        // Symlink icon
        const symlinkIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" style="fill: var(--color-accent-fg);"><path d="M7.775 3.275a.75.75 0 001.06 1.06l1.25-1.25a2 2 0 112.83 2.83l-2.5 2.5a2 2 0 01-2.83 0 .75.75 0 00-1.06 1.06 3.5 3.5 0 004.95 0l2.5-2.5a3.5 3.5 0 00-4.95-4.95l-1.25 1.25zm-4.69 9.64a2 2 0 010-2.83l2.5-2.5a2 2 0 012.83 0 .75.75 0 001.06-1.06 3.5 3.5 0 00-4.95 0l-2.5 2.5a3.5 3.5 0 004.95 4.95l1.25-1.25a.75.75 0 00-1.06-1.06l-1.25 1.25a2 2 0 01-2.83 0z"></path></svg>';

        const icon = item.type === 'directory'
            ? (item.is_symlink ? symlinkIcon : '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" class="icon-folder"><path fill="currentColor" d="M1.75 1A1.75 1.75 0 0 0 0 2.75v10.5C0 14.216.784 15 1.75 15h12.5A1.75 1.75 0 0 0 16 13.25v-8.5A1.75 1.75 0 0 0 14.25 3H7.5a.25.25 0 0 1-.2-.1l-.9-1.2C6.07 1.26 5.55 1 5 1H1.75Z"></path></svg>')
            : (item.is_symlink ? symlinkIcon : '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" class="icon-file"><path fill="currentColor" d="M2 1.75C2 .784 2.784 0 3.75 0h6.586c.464 0 .909.184 1.237.513l2.914 2.914c.329.328.513.773.513 1.237v9.586A1.75 1.75 0 0 1 13.25 16h-9.5A1.75 1.75 0 0 1 2 14.25Zm1.75-.25a.25.25 0 0 0-.25.25v12.5c0 .138.112.25.25.25h9.5a.25.25 0 0 0 .25-.25V6h-2.75A1.75 1.75 0 0 1 9 4.25V1.5Zm6.75.062V4.25c0 .138.112.25.25.25h2.688l-.011-.013-2.914-2.914-.013-.011Z"></path></svg>');

        const hasChildren = item.children && item.children.length > 0;
        const itemId = `tree-${item.path.replace(/\//g, '-')}`;

        if (item.type === 'directory') {
            // FOLDER ROW - entire div is clickable to expand/collapse (except the folder name)
            html += `<div class="file-tree-item file-tree-item--folder ${isActive ? 'active' : ''}" style="padding-left: ${indent}px;" onclick="toggleFolder('${itemId}', event)">`;

            // FOLDER ICON BUTTON - visual grouping of chevron and icon
            html += `<button type="button" class="folder-icon-button">`;

            // Chevron - part of the icon button
            if (hasChildren) {
                html += `<span class="file-tree-chevron ${shouldExpand ? 'expanded' : ''}">▸</span>`;
            } else {
                html += `<span class="file-tree-spacer"></span>`;
            }

            // Folder ICON
            html += `<span class="file-tree-icon">${icon}</span>`;
            html += `</button>`;

            // Folder NAME - link that navigates (stops propagation to prevent toggle)
            html += `<a href="${itemPath}" class="file-tree-folder-link" onclick="event.stopPropagation()">${item.name}`;

            // Add symlink indicator if it's a symlink
            if (item.is_symlink && item.symlink_target) {
                html += `<span style="color: var(--color-fg-muted); margin-left: 4px; font-size: 12px;"> → ${item.symlink_target}</span>`;
            }

            html += `</a>`;

            html += `</div>`;

            // Children container
            if (hasChildren) {
                html += `<div id="${itemId}" class="file-tree-children ${shouldExpand ? 'expanded' : ''}">`;
                html += buildTreeHTML(item.children || [], username, slug, level + 1);
                html += `</div>`;
            }
        } else {
            // FILE - just a link
            html += `<div class="file-tree-item file-tree-item--file ${isActive ? 'active' : ''}" style="padding-left: ${indent}px;">`;
            html += `<a href="/${username}/${slug}/blob/${item.path}" class="file-tree-file">`;
            html += `<span class="file-tree-spacer"></span>`;
            html += `<span class="file-tree-icon">${icon}</span><span class="file-tree-file-name">${item.name}`;

            // Add symlink indicator for files if it's a symlink
            if (item.is_symlink && item.symlink_target) {
                html += `<span style="color: var(--color-fg-muted); margin-left: 4px; font-size: 11px;"> → ${item.symlink_target}</span>`;
            }

            html += `</span>`;
            html += `</a>`;
            html += `</div>`;
        }
    });

    return html;
}

/**
 * Toggles folder expand/collapse state
 * @param folderId - ID of the folder container to toggle
 * @param event - Optional event to prevent propagation
 */
export function toggleFolder(folderId: string, event?: Event): void {
    const folder = document.getElementById(folderId);
    if (!folder) return;

    // Find the chevron - it's in the previous sibling (the folder card div)
    const folderCard = folder.previousElementSibling;
    const chevron = folderCard?.querySelector('.file-tree-chevron') as HTMLElement;

    if (folder.classList.contains('expanded')) {
        folder.classList.remove('expanded');
        if (chevron) chevron.classList.remove('expanded');
    } else {
        folder.classList.add('expanded');
        if (chevron) chevron.classList.add('expanded');
    }

    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }
}

/**
 * Loads file tree from API and renders it
 * @param username - Project owner username
 * @param slug - Project slug
 * @param containerId - ID of container element to render tree into
 */
export async function loadFileTree(username: string, slug: string, containerId: string = 'file-tree'): Promise<void> {
    try {
        const response = await fetch(`/${username}/${slug}/api/file-tree/`);
        const data = await response.json();

        const treeContainer = document.getElementById(containerId);
        if (!treeContainer) {
            console.error(`File tree container #${containerId} not found`);
            return;
        }

        if (data.success) {
            treeContainer.innerHTML = buildTreeHTML(data.tree, username, slug);
        } else {
            treeContainer.innerHTML = '<div style="color: var(--color-fg-muted); padding: 0.5rem;">Error loading file tree</div>';
        }
    } catch (err) {
        console.error('Failed to load file tree:', err);
        const treeContainer = document.getElementById(containerId);
        if (treeContainer) {
            treeContainer.innerHTML = '<div style="color: var(--color-fg-muted); padding: 0.5rem;">Error loading file tree</div>';
        }
    }
}
