/**
 * Writer Helper Functions
 * Utility functions for writer initialization and configuration
 */
import { writerStorage } from '@/utils/storage';
/**
 * Get writer configuration from global scope
 */
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
    // For demo/new projects, start with abstract (editable section)
    // compiled_pdf should only be selected if a PDF exists
    const defaultSection = 'manuscript/abstract';
    return {
        content: '',
        currentSection: defaultSection,
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
//# sourceMappingURL=helpers.js.map
