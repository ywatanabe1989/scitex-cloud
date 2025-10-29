/**
 * Writer Sections Manager Module
 * Handles document sections (abstract, introduction, methods, results, discussion)
 */
export interface Section {
    id: string;
    name: string;
    label: string;
    order: number;
    visible: boolean;
    content: string;
}
export declare class SectionsManager {
    private sections;
    private storage;
    private currentSection;
    private onSectionChangeCallback?;
    private onSectionsUpdateCallback?;
    private defaultSections;
    constructor();
    /**
     * Initialize sections
     */
    private initializeSections;
    /**
     * Get all sections
     */
    getAll(): Section[];
    /**
     * Get visible sections
     */
    getVisible(): Section[];
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