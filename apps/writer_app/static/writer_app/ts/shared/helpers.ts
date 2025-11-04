/**
 * Writer Helper Functions
 * Utility functions for writer initialization and configuration
 */

import { WriterConfig, EditorState } from '@/types';
import { writerStorage } from '@/utils/storage';

/**
 * Get writer configuration from global scope
 */
export function getWriterConfig(): WriterConfig {
    const config = (window as any).WRITER_CONFIG as WriterConfig;
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
export function createDefaultEditorState(config?: WriterConfig): EditorState {
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
export function loadEditorState(): EditorState {
    const saved = writerStorage.load<EditorState>('editorState');
    if (saved) {
        return {
            ...saved,
            unsavedSections: new Set(saved.unsavedSections as any),
        };
    }
    return createDefaultEditorState();
}

/**
 * Save editor state to storage
 */
export function saveEditorState(state: EditorState): void {
    writerStorage.save('editorState', {
        ...state,
        unsavedSections: state.unsavedSections ? Array.from(state.unsavedSections) : [],
    });
}
