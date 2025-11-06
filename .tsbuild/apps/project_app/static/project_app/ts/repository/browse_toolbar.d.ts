/**
 * Browse Toolbar Handler
 * Manages file browser toolbar interactions: dropdowns, copy, download, branch switching
 * @module repository/browse_toolbar
 */
interface ProjectData {
    owner: string;
    slug: string;
    breadcrumbPath: string;
}
declare class BrowseToolbar {
    private projectData;
    constructor();
    private init;
    private loadProjectData;
    private setupClickableRows;
    private setupDropdowns;
    private toggleDropdown;
    private closeAllDropdowns;
    private setupDropdownHoverEffects;
    private switchBranch;
    private copyProjectToClipboard;
    private copyDirToClipboard;
    private copyToClipboardGeneric;
    private downloadProjectAsFile;
    private downloadDirAsFile;
    private downloadAsFileGeneric;
    private getCookie;
}
//# sourceMappingURL=browse_toolbar.d.ts.map