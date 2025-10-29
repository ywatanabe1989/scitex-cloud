/**
 * Shared Type Definitions
 * Used across the SciTeX application
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

export interface HistoryEntry {
    content: string;
    wordCount: number;
    timestamp: number;
}

export interface SectionMetadata {
    name: string;
    label: string;
    order: number;
    visible: boolean;
}
