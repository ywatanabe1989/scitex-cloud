/**
 * Writer File Tree Module
 * Handles file tree browsing and navigation
 */
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
export declare class FileTreeManager {
    private apiClient;
    private projectId;
    private container;
    private onFileSelectCallback?;
    private expandedDirs;
    private texFileDropdownId?;
    constructor(options: FileTreeOptions);
    /**
     * Load and render file tree
     */
    load(): Promise<void>;
    /**
     * Render file tree in the container
     */
    private render;
    /**
     * Create tree element from nodes
     */
    private createTreeElement;
    /**
     * Create a single node element
     */
    private createNodeElement;
    /**
     * Toggle directory expansion
     */
    private toggleDirectory;
    /**
     * Select a file
     */
    private selectFile;
    /**
     * Render error message
     */
    private renderError;
    /**
     * Refresh file tree
     */
    refresh(): Promise<void>;
    /**
     * Set file selection callback
     */
    onFileSelect(callback: (filePath: string, fileName: string) => void): void;
    /**
     * Update sections dropdown for a new document type
     */
    updateForDocType(docType: string): void;
    /**
     * Extract all .tex files from the tree recursively
     */
    private extractTexFiles;
    /**
     * Map of section IDs to readable names (IMRAD structure)
     */
    private sectionNames;
    /**
     * Sections available for each document type
     */
    private sectionsByDocType;
    /**
     * Populate the section dropdown selector with hierarchical structure
     */
    populateTexFileDropdown(docType?: string): Promise<void>;
    /**
     * Add sections to dropdown with optgroup
     */
    private addSectionsToDropdown;
    /**
     * Fallback population method using legacy structure
     */
    private populateTexFileDropdownFallback;
}
//# sourceMappingURL=file_tree.d.ts.map