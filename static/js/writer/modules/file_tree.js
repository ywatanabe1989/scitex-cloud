/**
 * Writer File Tree Module
 * Handles file tree browsing and navigation
 */
import { ApiClient } from '@/utils/api';
export class FileTreeManager {
    constructor(options) {
        this.expandedDirs = new Set();
        /**
         * Map of section IDs to readable names (IMRAD structure)
         */
        this.sectionNames = {
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
        this.sectionsByDocType = {
            'manuscript': ['abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion', 'references'],
            'supplementary': ['content', 'methods', 'results'],
            'revision': ['response', 'changes'],
            'shared': [],
        };
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
    async load() {
        try {
            console.log('[FileTree] Loading file tree...');
            const response = await this.apiClient.get(`/writer/api/project/${this.projectId}/file-tree/`);
            if (!response.success || !response.data) {
                throw new Error(response.error || 'Failed to load file tree');
            }
            const tree = response.data.tree;
            console.log('[FileTree] Loaded', tree.length, 'root items');
            // Populate section dropdown for manuscript type (default)
            this.populateTexFileDropdown('manuscript');
            this.render(tree);
        }
        catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to load file tree';
            console.error('[FileTree] Error:', message);
            this.renderError(message);
        }
    }
    /**
     * Render file tree in the container
     */
    render(nodes) {
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
    createTreeElement(nodes) {
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
    createNodeElement(node, level = 0) {
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
        }
        else {
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
    toggleDirectory(path) {
        if (this.expandedDirs.has(path)) {
            this.expandedDirs.delete(path);
        }
        else {
            this.expandedDirs.add(path);
        }
        // Reload the tree to update UI
        this.load();
    }
    /**
     * Select a file
     */
    selectFile(filePath, fileName) {
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
    renderError(message) {
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
    async refresh() {
        console.log('[FileTree] Refreshing...');
        await this.load();
    }
    /**
     * Set file selection callback
     */
    onFileSelect(callback) {
        this.onFileSelectCallback = callback;
    }
    /**
     * Update sections dropdown for a new document type
     */
    updateForDocType(docType) {
        console.log('[FileTree] Updating sections for document type:', docType);
        this.populateTexFileDropdown(docType);
    }
    /**
     * Extract all .tex files from the tree recursively
     */
    extractTexFiles(nodes, files = []) {
        nodes.forEach(node => {
            if (node.type === 'file' && node.name.endsWith('.tex')) {
                files.push({ path: node.path, name: node.name });
            }
            else if (node.type === 'directory' && node.children) {
                this.extractTexFiles(node.children, files);
            }
        });
        return files;
    }
    /**
     * Populate the section dropdown selector based on document type
     */
    populateTexFileDropdown(docType = 'manuscript') {
        if (!this.texFileDropdownId)
            return;
        const dropdown = document.getElementById(this.texFileDropdownId);
        if (!dropdown) {
            console.warn('[FileTree] Dropdown element not found:', this.texFileDropdownId);
            return;
        }
        // Clear existing options except the first placeholder
        while (dropdown.options.length > 1) {
            dropdown.remove(1);
        }
        // Get sections for the selected document type
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
        console.log('[FileTree] Populated dropdown with', sections.length, 'sections for', docType);
        // Add change event listener if not already attached
        if (!dropdown.dataset.listenerAttached) {
            dropdown.addEventListener('change', (e) => {
                const target = e.target;
                if (target.value) {
                    const sectionId = target.value;
                    const sectionName = this.sectionNames[sectionId] || sectionId;
                    // Trigger callback with section info
                    this.selectFile(sectionId, sectionName);
                }
            });
            dropdown.dataset.listenerAttached = 'true';
        }
    }
}
//# sourceMappingURL=file_tree.js.map