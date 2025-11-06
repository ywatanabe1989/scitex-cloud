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
/**
 * Section hierarchy types
 */
export interface SectionConfig {
    id: string;
    name: string;
    label: string;
    path: string;
    optional?: boolean;
}
export interface SectionCategory {
    label: string;
    description: string;
    sections: SectionConfig[];
    supports_crud?: boolean;
}
export interface SectionHierarchy {
    shared: SectionCategory;
    manuscript: SectionCategory;
    supplementary: SectionCategory;
    revision: SectionCategory;
}
/**
 * Load section hierarchy from API
 */
export declare function loadSectionHierarchy(): Promise<SectionHierarchy | null>;
/**
 * Populate section dropdown with hierarchical structure
 */
export declare function populateSectionDropdown(dropdown: HTMLSelectElement, hierarchy: SectionHierarchy, currentSectionId?: string): void;
//# sourceMappingURL=helpers.d.ts.map