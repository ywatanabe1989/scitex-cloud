/**
 * Writer Helper Functions
 * Utility functions for writer initialization and configuration
 */
import { WriterConfig, EditorState } from '@/types';
export declare function getWriterConfig(): WriterConfig;
/**
 * Create default editor state
 */
export declare function createDefaultEditorState(config?: WriterConfig): EditorState;
/**
 * Load editor state from storage or create default
 */
export declare function loadEditorState(): EditorState;
/**
 * Save editor state to storage
 */
export declare function saveEditorState(state: EditorState): void;
//# sourceMappingURL=helpers.d.ts.map