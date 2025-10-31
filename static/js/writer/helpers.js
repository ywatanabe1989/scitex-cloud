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
export function createDefaultEditorState() {
    return {
        content: '',
        currentSection: 'manuscript/compiled_pdf',
        unsavedSections: new Set(),
        currentDocType: 'manuscript',
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