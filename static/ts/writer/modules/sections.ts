/**
 * Writer Sections Manager Module
 * Handles document sections (abstract, introduction, methods, results, discussion)
 */

import { StorageManager } from '@/utils/storage';

export interface Section {
    id: string;
    name: string;
    label: string;
    order: number;
    visible: boolean;
    content: string;
}

export class SectionsManager {
    private sections: Map<string, Section> = new Map();
    private storage: StorageManager;
    private currentSection: string = 'abstract';
    private onSectionChangeCallback?: (section: string) => void;
    private onSectionsUpdateCallback?: (sections: Section[]) => void;

    private defaultSections: Section[] = [
        { id: 'abstract', name: 'abstract', label: 'Abstract', order: 0, visible: true, content: '' },
        { id: 'introduction', name: 'introduction', label: 'Introduction', order: 1, visible: true, content: '' },
        { id: 'methods', name: 'methods', label: 'Methods', order: 2, visible: true, content: '' },
        { id: 'results', name: 'results', label: 'Results', order: 3, visible: true, content: '' },
        { id: 'discussion', name: 'discussion', label: 'Discussion', order: 4, visible: true, content: '' }
    ];

    constructor() {
        this.storage = new StorageManager('writer_sections_');
        this.initializeSections();
    }

    /**
     * Initialize sections
     */
    private initializeSections(): void {
        const stored = this.storage.load<Section[]>('list');
        const sectionsToUse = stored || this.defaultSections;
        
        sectionsToUse.forEach(section => {
            this.sections.set(section.id, section);
        });

        console.log('[Sections] Initialized with', this.sections.size, 'sections');
    }

    /**
     * Get all sections
     */
    getAll(): Section[] {
        return Array.from(this.sections.values()).sort((a, b) => a.order - b.order);
    }

    /**
     * Get visible sections
     */
    getVisible(): Section[] {
        return this.getAll().filter(s => s.visible);
    }

    /**
     * Get section by id
     */
    get(id: string): Section | undefined {
        return this.sections.get(id);
    }

    /**
     * Add a new section
     */
    add(section: Section): void {
        this.sections.set(section.id, section);
        this.save();
        this.notifyUpdate();
        console.log('[Sections] Added section:', section.id);
    }

    /**
     * Update section
     */
    update(id: string, changes: Partial<Section>): void {
        const section = this.sections.get(id);
        if (section) {
            Object.assign(section, changes);
            this.save();
            this.notifyUpdate();
            console.log('[Sections] Updated section:', id);
        }
    }

    /**
     * Remove section
     */
    remove(id: string): void {
        if (this.sections.delete(id)) {
            this.save();
            this.notifyUpdate();
            console.log('[Sections] Removed section:', id);
        }
    }

    /**
     * Set section content
     */
    setContent(id: string, content: string): void {
        const section = this.sections.get(id);
        if (section) {
            section.content = content;
            this.storage.save(`content_${id}`, content);
        }
    }

    /**
     * Get section content
     */
    getContent(id: string): string {
        const section = this.sections.get(id);
        if (section) {
            return section.content;
        }
        
        // Try to load from storage
        const stored = this.storage.load<string>(`content_${id}`);
        if (stored) {
            return stored;
        }
        
        return '';
    }

    /**
     * Switch to section
     */
    switchTo(id: string): boolean {
        if (this.sections.has(id)) {
            this.currentSection = id;
            if (this.onSectionChangeCallback) {
                this.onSectionChangeCallback(id);
            }
            return true;
        }
        return false;
    }

    /**
     * Get current section
     */
    getCurrent(): string {
        return this.currentSection;
    }

    /**
     * Reorder sections
     */
    reorder(orderMap: Record<string, number>): void {
        Object.entries(orderMap).forEach(([id, order]) => {
            const section = this.sections.get(id);
            if (section) {
                section.order = order;
            }
        });
        this.save();
        this.notifyUpdate();
    }

    /**
     * Toggle section visibility
     */
    toggleVisibility(id: string): void {
        const section = this.sections.get(id);
        if (section) {
            section.visible = !section.visible;
            this.save();
            this.notifyUpdate();
        }
    }

    /**
     * Set callback for section changes
     */
    onSectionChange(callback: (section: string) => void): void {
        this.onSectionChangeCallback = callback;
    }

    /**
     * Set callback for sections update
     */
    onUpdate(callback: (sections: Section[]) => void): void {
        this.onSectionsUpdateCallback = callback;
    }

    /**
     * Notify listeners of update
     */
    private notifyUpdate(): void {
        if (this.onSectionsUpdateCallback) {
            this.onSectionsUpdateCallback(this.getAll());
        }
    }

    /**
     * Save sections to storage
     */
    private save(): void {
        this.storage.save('list', this.getAll());
    }

    /**
     * Export all sections as combined content
     */
    exportCombined(): string {
        return this.getVisible()
            .map(s => `% ${s.label}\n${s.content}`)
            .join('\n\n');
    }

    /**
     * Get total word count across all sections
     */
    getTotalWordCount(): number {
        return this.getAll().reduce((total, section) => {
            const words = section.content.trim().split(/\s+/).length;
            return total + (section.content ? words : 0);
        }, 0);
    }
}
