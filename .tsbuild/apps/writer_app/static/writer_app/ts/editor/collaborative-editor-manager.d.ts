/**
 * Collaborative Editor Manager
 * Handles manuscript editing, collaboration, auto-save, word counts, and version control
 *
 * @version 2.0.0 (TypeScript)
 * @author SciTeX Development Team
 */
interface ManuscriptConfig {
    id: number;
    sections: string[];
}
export declare class CollaborativeEditorManager {
    private manuscriptConfig;
    private isCollaborationEnabled;
    private autoSaveInterval;
    constructor(manuscriptConfig: ManuscriptConfig);
    /**
     * Initialize the editor
     */
    initialize(): void;
    /**
     * Setup event listeners for all section textareas
     */
    private setupEditorListeners;
    /**
     * Setup collaboration toggle button
     */
    setupCollaborationToggle(): void;
    /**
     * Enable collaboration mode
     */
    private enableCollaboration;
    /**
     * Disable collaboration mode
     */
    private disableCollaboration;
    /**
     * Count words in a text string
     */
    private countWords;
    /**
     * Update word count for a specific section
     */
    private updateWordCount;
    /**
     * Update section badge with word count and collaboration status
     */
    private updateSectionBadge;
    /**
     * Update word counts for all sections
     */
    private updateWordCounts;
    /**
     * Update overall progress indicators
     */
    private updateProgress;
    /**
     * Auto-save manuscript to localStorage
     */
    private autoSave;
    /**
     * Setup auto-save interval
     */
    private setupAutoSave;
    /**
     * Export manuscript as JSON
     */
    exportJSON(): void;
    /**
     * Show LaTeX view (placeholder)
     */
    showLatexView(): void;
    /**
     * Compile manuscript to PDF (placeholder)
     */
    compileManuscript(): void;
    /**
     * Open version control dashboard
     */
    openVersionControl(): void;
    /**
     * Create a new version with git commit
     */
    createVersion(): Promise<void>;
    /**
     * Update last save time message
     */
    private updateLastSaveTime;
    /**
     * Mark document as modified (visual indicator)
     */
    private markAsModified;
    /**
     * Load saved content from localStorage
     */
    private loadSavedContent;
    /**
     * Destroy the editor manager and cleanup
     */
    destroy(): void;
}
declare global {
    interface Window {
        CollaborativeEditorManager: typeof CollaborativeEditorManager;
        collaborativeEditorManager?: CollaborativeEditorManager;
    }
}
export {};
//# sourceMappingURL=collaborative-editor-manager.d.ts.map