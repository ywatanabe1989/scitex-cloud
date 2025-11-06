/**
 * Writer File Tree Module
 * Handles file tree browsing and navigation
 */

import { ApiClient } from '@/utils/api';

console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/editor/modules/file_tree.ts loaded");
export interface FileTreeNode {
    name: string;
    path: string;
    type: 'file' | 'directory';
    children?: FileTreeNode[];
}

export interface FileTreeOptions {
    projectId: number;
    container: HTMLElement;
    onFileSelect?: (filePath: string, fileName: string) => void;
    texFileDropdownId?: string;
}

export class FileTreeManager {
    private apiClient: ApiClient;
    private projectId: number;
    private container: HTMLElement;
    private onFileSelectCallback?: (filePath: string, fileName: string) => void;
    private expandedDirs: Set<string> = new Set();
    private texFileDropdownId?: string;

    constructor(options: FileTreeOptions) {
        this.apiClient = new ApiClient();
        this.projectId = options.projectId;
        this.container = options.container;
        this.onFileSelectCallback = options.onFileSelect;
        this.texFileDropdownId = options.texFileDropdownId;

        console.log('[FileTree] Initialized for project', this.projectId);
    }

    /**
     * Load and render file tree
     */
    async load(): Promise<void> {
        try {
            console.log('[FileTree] Loading file tree...');

            const response = await this.apiClient.get<{ tree: FileTreeNode[] }>(
                `/writer/api/project/${this.projectId}/file-tree/`
            );

            if (!response.success || !response.data) {
                throw new Error(response.error || 'Failed to load file tree');
            }

            const tree = response.data.tree;
            console.log('[FileTree] Loaded', tree.length, 'root items');

            // Populate section dropdown for manuscript type (default)
            this.populateTexFileDropdown('manuscript');

            this.render(tree);
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to load file tree';
            console.error('[FileTree] Error:', message);
            this.renderError(message);
        }
    }

    /**
     * Render file tree in the container
     */
    private render(nodes: FileTreeNode[]): void {
        if (nodes.length === 0) {
            this.container.innerHTML = `
                <div class="text-muted text-center py-3" style="font-size: 0.85rem;">
                    <i class="fas fa-folder-open me-2"></i>
                    <div style="margin-top: 0.5rem;">No .tex files found</div>
                </div>
            `;
            return;
        }

        this.container.innerHTML = '';
        const treeElement = this.createTreeElement(nodes);
        this.container.appendChild(treeElement);
    }

    /**
     * Create tree element from nodes
     */
    private createTreeElement(nodes: FileTreeNode[]): HTMLElement {
        const ul = document.createElement('ul');
        ul.className = 'file-tree-list';
        ul.style.cssText = 'list-style: none; padding-left: 0; margin: 0;';

        nodes.forEach(node => {
            const li = this.createNodeElement(node);
            ul.appendChild(li);
        });

        return ul;
    }

    /**
     * Create a single node element
     */
    private createNodeElement(node: FileTreeNode, level: number = 0): HTMLElement {
        const li = document.createElement('li');
        li.className = 'file-tree-item';
        li.style.cssText = `padding: 0.35rem 0.5rem 0.35rem ${level * 1.2 + 0.5}rem; cursor: pointer; border-radius: 4px; transition: background 0.15s;`;

        if (node.type === 'directory') {
            const isExpanded = this.expandedDirs.has(node.path);

            li.innerHTML = `
                <div class="d-flex align-items-center file-tree-node-content" data-path="${node.path}">
                    <i class="fas fa-chevron-${isExpanded ? 'down' : 'right'} me-2" style="font-size: 0.75rem; width: 12px;"></i>
                    <i class="fas fa-folder${isExpanded ? '-open' : ''} me-2 text-warning" style="font-size: 0.9rem;"></i>
                    <span style="font-size: 0.9rem;">${node.name}</span>
                </div>
            `;

            // Add click handler for directory toggle
            const contentDiv = li.querySelector('.file-tree-node-content');
            contentDiv?.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleDirectory(node.path);
            });

            // Add children container
            if (node.children && node.children.length > 0) {
                const childrenContainer = document.createElement('div');
                childrenContainer.className = 'file-tree-children';
                childrenContainer.style.display = isExpanded ? 'block' : 'none';

                const childrenUl = document.createElement('ul');
                childrenUl.style.cssText = 'list-style: none; padding-left: 0; margin: 0.25rem 0 0 0;';

                node.children.forEach(child => {
                    const childLi = this.createNodeElement(child, level + 1);
                    childrenUl.appendChild(childLi);
                });

                childrenContainer.appendChild(childrenUl);
                li.appendChild(childrenContainer);
            }
        } else {
            // File node
            li.innerHTML = `
                <div class="d-flex align-items-center file-tree-node-content" data-path="${node.path}">
                    <i class="fas fa-file-alt me-2 text-primary" style="font-size: 0.85rem; margin-left: 1.5rem;"></i>
                    <span style="font-size: 0.9rem;">${node.name}</span>
                </div>
            `;

            // Add click handler for file selection
            const contentDiv = li.querySelector('.file-tree-node-content');
            contentDiv?.addEventListener('click', (e) => {
                e.stopPropagation();
                this.selectFile(node.path, node.name);
            });

            // Hover effect
            li.addEventListener('mouseenter', () => {
                li.style.background = 'rgba(0, 123, 255, 0.1)';
            });
            li.addEventListener('mouseleave', () => {
                li.style.background = 'transparent';
            });
        }

        return li;
    }

    /**
     * Toggle directory expansion
     */
    private toggleDirectory(path: string): void {
        if (this.expandedDirs.has(path)) {
            this.expandedDirs.delete(path);
        } else {
            this.expandedDirs.add(path);
        }

        // Reload the tree to update UI
        this.load();
    }

    /**
     * Select a file
     */
    private selectFile(filePath: string, fileName: string): void {
        console.log('[FileTree] File selected:', filePath);

        // Highlight selected file
        this.container.querySelectorAll('.file-tree-node-content').forEach(el => {
            el.classList.remove('selected');
        });

        const selectedNode = this.container.querySelector(`[data-path="${filePath}"]`);
        if (selectedNode) {
            selectedNode.classList.add('selected');
            selectedNode.setAttribute('style', selectedNode.getAttribute('style') + '; background: rgba(0, 123, 255, 0.2);');
        }

        // Trigger callback
        if (this.onFileSelectCallback) {
            this.onFileSelectCallback(filePath, fileName);
        }
    }

    /**
     * Render error message
     */
    private renderError(message: string): void {
        this.container.innerHTML = `
            <div class="alert alert-warning" style="font-size: 0.85rem; padding: 0.75rem; margin: 0;">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </div>
        `;
    }

    /**
     * Refresh file tree
     */
    async refresh(): Promise<void> {
        console.log('[FileTree] Refreshing...');
        await this.load();
    }

    /**
     * Set file selection callback
     */
    onFileSelect(callback: (filePath: string, fileName: string) => void): void {
        this.onFileSelectCallback = callback;
    }

    /**
     * Update sections dropdown for a new document type
     */
    updateForDocType(docType: string): void {
        console.log('[FileTree] Updating sections for document type:', docType);
        this.populateTexFileDropdown(docType);
    }

    /**
     * Extract all .tex files from the tree recursively
     */
    private extractTexFiles(nodes: FileTreeNode[], files: Array<{ path: string; name: string }> = []): Array<{ path: string; name: string }> {
        nodes.forEach(node => {
            if (node.type === 'file' && node.name.endsWith('.tex')) {
                files.push({ path: node.path, name: node.name });
            } else if (node.type === 'directory' && node.children) {
                this.extractTexFiles(node.children, files);
            }
        });
        return files;
    }

    /**
     * Map of section IDs to readable names (IMRAD structure)
     */
    private sectionNames: { [key: string]: string } = {
        'title': 'Title',
        'abstract': 'Abstract',
        'introduction': 'Introduction',
        'methods': 'Methods',
        'results': 'Results',
        'discussion': 'Discussion',
        'conclusion': 'Conclusion',
        'references': 'References',
        'keywords': 'Keywords',
        'authors': 'Authors',
        'highlights': 'Highlights',
        'graphical_abstract': 'Graphical Abstract',
    };

    /**
     * Sections available for each document type
     */
    private sectionsByDocType: { [key: string]: string[] } = {
        'manuscript': ['abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion', 'references'],
        'supplementary': ['content', 'methods', 'results'],
        'revision': ['response', 'changes'],
        'shared': [],
    };

    /**
     * Populate the section dropdown selector with hierarchical structure
     */
    public async populateTexFileDropdown(docType: string = 'manuscript'): Promise<void> {
        if (!this.texFileDropdownId) return;

        const dropdown = document.getElementById(this.texFileDropdownId) as HTMLSelectElement;
        if (!dropdown) {
            console.warn('[FileTree] Dropdown element not found:', this.texFileDropdownId);
            return;
        }

        // Clear existing options
        dropdown.innerHTML = '';

        try {
            // Fetch hierarchical sections configuration
            const response = await fetch('/writer/api/sections-config/');
            const data = await response.json();

            if (!data.success || !data.hierarchy) {
                console.error('[FileTree] Failed to load sections hierarchy');
                this.populateTexFileDropdownFallback(dropdown, docType);
                return;
            }

            const hierarchy = data.hierarchy;

            // Populate dropdown based on docType
            if (docType === 'shared' && hierarchy.shared) {
                this.addSectionsToDropdown(dropdown, 'Shared', hierarchy.shared.sections);
            } else if (docType === 'manuscript' && hierarchy.manuscript) {
                this.addSectionsToDropdown(dropdown, 'Manuscript', hierarchy.manuscript.sections);
            } else if (docType === 'supplementary' && hierarchy.supplementary) {
                this.addSectionsToDropdown(dropdown, 'Supplementary', hierarchy.supplementary.sections);
            } else if (docType === 'revision' && hierarchy.revision) {
                this.addSectionsToDropdown(dropdown, 'Revision', hierarchy.revision.sections);
            } else {
                console.warn('[FileTree] Unknown document type:', docType);
                this.populateTexFileDropdownFallback(dropdown, docType);
                return;
            }

            console.log('[FileTree] Populated dropdown with hierarchical sections for', docType);

            // Select the first option (Compiled PDF) by default if nothing is selected
            if (dropdown.options.length > 0 && !dropdown.value) {
                dropdown.selectedIndex = 0;
                const firstOption = dropdown.options[0];
                console.log('[FileTree] Auto-selected first section:', firstOption.value);
                // Trigger the selection to load the content
                this.selectFile(firstOption.value, firstOption.textContent || '');
            }

            // Add change event listener if not already attached
            if (!dropdown.dataset.listenerAttached) {
                dropdown.addEventListener('change', (e) => {
                    const target = e.target as HTMLSelectElement;
                    if (target.value) {
                        const sectionId = target.value;
                        const selectedOption = target.options[target.selectedIndex];
                        const sectionName = selectedOption.textContent || sectionId;

                        // Trigger callback with section info
                        this.selectFile(sectionId, sectionName);
                    }
                });
                dropdown.dataset.listenerAttached = 'true';
            }
        } catch (error) {
            console.error('[FileTree] Error loading sections:', error);
            this.populateTexFileDropdownFallback(dropdown, docType);
        }
    }

    /**
     * Add sections to dropdown with optgroup
     */
    private addSectionsToDropdown(dropdown: HTMLSelectElement, groupLabel: string, sections: any[]): void {
        if (sections.length === 0) return;

        const optgroup = document.createElement('optgroup');
        optgroup.label = groupLabel;

        sections.forEach(section => {
            const option = document.createElement('option');
            option.value = section.id;
            option.textContent = section.label;

            if (section.optional) {
                option.textContent += ' (Optional)';
            }
            if (section.view_only) {
                option.disabled = true;
                option.textContent += ' (View Only)';
            }

            optgroup.appendChild(option);
        });

        dropdown.appendChild(optgroup);
    }

    /**
     * Fallback population method using legacy structure
     */
    private populateTexFileDropdownFallback(dropdown: HTMLSelectElement, docType: string): void {
        const sections = this.sectionsByDocType[docType] || [];

        if (sections.length === 0) {
            console.warn('[FileTree] No sections available for document type:', docType);
            return;
        }

        sections.forEach(sectionId => {
            const option = document.createElement('option');
            option.value = sectionId;
            option.textContent = this.sectionNames[sectionId] || sectionId.charAt(0).toUpperCase() + sectionId.slice(1);
            dropdown.appendChild(option);
        });

        console.log('[FileTree] Used fallback to populate dropdown with', sections.length, 'sections');
    }
}
