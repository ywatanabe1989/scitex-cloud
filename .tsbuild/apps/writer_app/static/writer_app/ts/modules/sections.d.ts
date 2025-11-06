/**
 * Writer Sections Manager Module
 * Handles hierarchical document sections (Shared, Manuscript, Supplementary, Revision)
 */
export interface Section {
    id: string;
    name: string;
    label: string;
    path?: string;
    category?: string;
    order?: number;
    visible?: boolean;
    content?: string;
    optional?: boolean;
    view_only?: boolean;
    instruction?: string;
    is_directory?: boolean;
}
export interface SectionCategory {
    label: string;
    description: string;
    sections: Section[];
    supports_crud?: boolean;
}
export interface SectionHierarchy {
    shared: SectionCategory;
    manuscript: SectionCategory;
    supplementary: SectionCategory;
    revision: SectionCategory;
}
export declare class SectionsManager {
    private sections;
    private hierarchy;
    private storage;
    private currentSection;
    private onSectionChangeCallback?;
    private onSectionsUpdateCallback?;
    private onHierarchyLoadCallback?;
    constructor();
    /**
     * Initialize sections - loads hierarchical structure from API
     */
    private initializeSections;
    /**
     * Load hierarchical section structure from API
     */
    loadHierarchy(): Promise<void>;
    /**
     * Create fallback structure if API fails
     */
    private createFallbackStructure;
    /**
     * Get all sections
     */
    getAll(): Section[];
    /**
     * Get visible sections
     */
    getVisible(): Section[];
    /**
     * Get sections by category
     */
    getByCategory(category: string): Section[];
    /**
     * Get hierarchy
     */
    getHierarchy(): SectionHierarchy | null;
    /**
     * Set callback for hierarchy load
     */
    onHierarchyLoad(callback: (hierarchy: SectionHierarchy) => void): void;
    /**
     * Get section by id
     */
    get(id: string): Section | undefined;
    /**
     * Add a new section
     */
    add(section: Section): void;
    /**
     * Update section
     */
    update(id: string, changes: Partial<Section>): void;
    /**
     * Remove section
     */
    remove(id: string): void;
    /**
     * Set section content
     */
    setContent(id: string, content: string): void;
    /**
     * Get section content
     */
    getContent(id: string): string;
    /**
     * Switch to section
     */
    switchTo(id: string): boolean;
    /**
     * Get current section
     */
    getCurrent(): string;
    /**
     * Reorder sections
     */
    reorder(orderMap: Record<string, number>): void;
    /**
     * Toggle section visibility
     */
    toggleVisibility(id: string): void;
    /**
     * Set callback for section changes
     */
    onSectionChange(callback: (section: string) => void): void;
    /**
     * Set callback for sections update
     */
    onUpdate(callback: (sections: Section[]) => void): void;
    /**
     * Notify listeners of update
     */
    private notifyUpdate;
    /**
     * Save sections to storage
     */
    private save;
    /**
     * Export all sections as combined content
     */
    exportCombined(): string;
    /**
     * Get total word count across all sections
     */
    getTotalWordCount(): number;
}
//# sourceMappingURL=sections.d.ts.map