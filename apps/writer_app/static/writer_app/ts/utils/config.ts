/**
 * Configuration and Types Module
 * Defines types and configuration interfaces
 */

export interface WriterConfig {
    projectId: string | null;
    username: string | null;
    projectSlug: string | null;
    isDemo: boolean;
    isAnonymous: boolean;
    writerInitialized: boolean;
    csrfToken?: string;
    wordCounts?: Record<string, number>;
}

export interface WordCounts {
    [key: string]: number;
}

export interface EditorState {
    currentSection: string;
    currentDocType: string;
    liveCompilationEnabled: boolean;
    currentlyCompiling: boolean;
    unsavedSections: Set<string>;
}

export interface CompilationJob {
    id: string;
    status: 'pending' | 'processing' | 'completed' | 'failed';
    progress?: number;
    error?: string;
}

/**
 * Get WRITER_CONFIG from window object with proper typing
 */
export function getWriterConfig(): WriterConfig {
    return (window as any).WRITER_CONFIG || {};
}

/**
 * Initialize default editor state
 */
export function createDefaultEditorState(): EditorState {
    return {
        currentSection: 'abstract',
        currentDocType: 'manuscript',
        liveCompilationEnabled: true,
        currentlyCompiling: false,
        unsavedSections: new Set()
    };
}
