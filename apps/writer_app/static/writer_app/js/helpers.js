/**
 * Writer Helper Functions
 * Utility functions for writer initialization and configuration
 */
import { writerStorage } from '@/utils/storage';
/**
 * Get writer configuration from global scope
 */
console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/helpers.ts loaded");
export function getWriterConfig() {
    const config = window.WRITER_CONFIG;
    if (!config) {
        console.warn('[Writer] WRITER_CONFIG not found in window');
        return {
            projectId: null,
            writerInitialized: false,
            isDemo: false,
            username: null,
            projectSlug: null,
            isAnonymous: true,
        };
    }
    return config;
}
/**
 * Create default editor state
 */
export function createDefaultEditorState(config) {
    return {
        content: '',
        currentSection: 'manuscript/compiled_pdf',
        unsavedSections: new Set(),
        currentDocType: 'manuscript',
        projectId: config?.projectId ? Number(config.projectId) : null,
    };
}
/**
 * Load editor state from storage or create default
 */
export function loadEditorState() {
    const saved = writerStorage.load('editorState');
    if (saved) {
        return {
            ...saved,
            unsavedSections: new Set(saved.unsavedSections),
        };
    }
    return createDefaultEditorState();
}
/**
 * Save editor state to storage
 */
export function saveEditorState(state) {
    writerStorage.save('editorState', {
        ...state,
        unsavedSections: state.unsavedSections ? Array.from(state.unsavedSections) : [],
    });
}
/**
 * Load section hierarchy from API
 */
export async function loadSectionHierarchy() {
    try {
        const response = await fetch('/writer/api/sections-config/');
        const data = await response.json();
        if (data.success && data.hierarchy) {
            console.log('[Writer] Loaded section hierarchy:', data.hierarchy);
            return data.hierarchy;
        }
        else {
            console.error('[Writer] Failed to load section hierarchy:', data);
            return null;
        }
    }
    catch (error) {
        console.error('[Writer] Error loading section hierarchy:', error);
        return null;
    }
}
/**
 * Populate section dropdown with hierarchical structure
 */
export function populateSectionDropdown(dropdown, hierarchy, currentSectionId) {
    // Clear existing options
    dropdown.innerHTML = '';
    // Add categories with optgroups
    const categories = ['shared', 'manuscript', 'supplementary', 'revision'];
    for (const categoryKey of categories) {
        const category = hierarchy[categoryKey];
        if (!category || category.sections.length === 0)
            continue;
        // Create optgroup
        const optgroup = document.createElement('optgroup');
        optgroup.label = category.label;
        // Add sections to optgroup
        for (const section of category.sections) {
            const option = document.createElement('option');
            option.value = section.id; // e.g., "shared/title", "manuscript/abstract"
            option.textContent = section.label;
            if (section.optional) {
                option.textContent += ' (optional)';
            }
            if (currentSectionId && section.id === currentSectionId) {
                option.selected = true;
            }
            optgroup.appendChild(option);
        }
        dropdown.appendChild(optgroup);
    }
}
//# sourceMappingURL=helpers.js.map