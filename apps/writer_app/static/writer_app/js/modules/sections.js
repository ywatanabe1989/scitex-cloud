/**
 * Writer Sections Manager Module
 * Handles document sections (abstract, introduction, methods, results, discussion)
 */
import { StorageManager } from '@/utils/storage';
export class SectionsManager {
    constructor() {
        this.sections = new Map();
        this.currentSection = 'abstract';
        this.defaultSections = [
            { id: 'abstract', name: 'abstract', label: 'Abstract', order: 0, visible: true, content: '' },
            { id: 'introduction', name: 'introduction', label: 'Introduction', order: 1, visible: true, content: '' },
            { id: 'methods', name: 'methods', label: 'Methods', order: 2, visible: true, content: '' },
            { id: 'results', name: 'results', label: 'Results', order: 3, visible: true, content: '' },
            { id: 'discussion', name: 'discussion', label: 'Discussion', order: 4, visible: true, content: '' }
        ];
        this.storage = new StorageManager('writer_sections_');
        this.initializeSections();
    }
    /**
     * Initialize sections
     */
    initializeSections() {
        const stored = this.storage.load('list');
        const sectionsToUse = stored || this.defaultSections;
        sectionsToUse.forEach(section => {
            this.sections.set(section.id, section);
        });
        // Load content from WRITER_CONFIG if available (from Django backend)
        const writerConfig = window.WRITER_CONFIG;
        if (writerConfig?.sections) {
            Object.entries(writerConfig.sections).forEach(([sectionId, content]) => {
                if (content && this.sections.has(sectionId)) {
                    const section = this.sections.get(sectionId);
                    if (section) {
                        section.content = content;
                        // Also save to storage for offline access
                        this.storage.save(`content_${sectionId}`, content);
                    }
                }
            });
            console.log('[Sections] Loaded content from WRITER_CONFIG for', Object.keys(writerConfig.sections).length, 'sections');
        }
        console.log('[Sections] Initialized with', this.sections.size, 'sections');
    }
    /**
     * Get all sections
     */
    getAll() {
        return Array.from(this.sections.values()).sort((a, b) => a.order - b.order);
    }
    /**
     * Get visible sections
     */
    getVisible() {
        return this.getAll().filter(s => s.visible);
    }
    /**
     * Get section by id
     */
    get(id) {
        return this.sections.get(id);
    }
    /**
     * Add a new section
     */
    add(section) {
        this.sections.set(section.id, section);
        this.save();
        this.notifyUpdate();
        console.log('[Sections] Added section:', section.id);
    }
    /**
     * Update section
     */
    update(id, changes) {
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
    remove(id) {
        if (this.sections.delete(id)) {
            this.save();
            this.notifyUpdate();
            console.log('[Sections] Removed section:', id);
        }
    }
    /**
     * Set section content
     */
    setContent(id, content) {
        const section = this.sections.get(id);
        if (section) {
            section.content = content;
            this.storage.save(`content_${id}`, content);
        }
    }
    /**
     * Get section content
     */
    getContent(id) {
        const section = this.sections.get(id);
        if (section) {
            return section.content;
        }
        // Try to load from storage
        const stored = this.storage.load(`content_${id}`);
        if (stored) {
            return stored;
        }
        return '';
    }
    /**
     * Switch to section
     */
    switchTo(id) {
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
    getCurrent() {
        return this.currentSection;
    }
    /**
     * Reorder sections
     */
    reorder(orderMap) {
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
    toggleVisibility(id) {
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
    onSectionChange(callback) {
        this.onSectionChangeCallback = callback;
    }
    /**
     * Set callback for sections update
     */
    onUpdate(callback) {
        this.onSectionsUpdateCallback = callback;
    }
    /**
     * Notify listeners of update
     */
    notifyUpdate() {
        if (this.onSectionsUpdateCallback) {
            this.onSectionsUpdateCallback(this.getAll());
        }
    }
    /**
     * Save sections to storage
     */
    save() {
        this.storage.save('list', this.getAll());
    }
    /**
     * Export all sections as combined content
     */
    exportCombined() {
        return this.getVisible()
            .map(s => `% ${s.label}\n${s.content}`)
            .join('\n\n');
    }
    /**
     * Get total word count across all sections
     */
    getTotalWordCount() {
        return this.getAll().reduce((total, section) => {
            const words = section.content.trim().split(/\s+/).length;
            return total + (section.content ? words : 0);
        }, 0);
    }
}
//# sourceMappingURL=sections.js.map