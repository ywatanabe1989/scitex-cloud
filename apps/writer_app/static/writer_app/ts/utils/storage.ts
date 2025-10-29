/**
 * LocalStorage Utility Module
 * Handles persistence of editor state and word counts
 */

import { WordCounts } from './config';

const STORAGE_KEYS = {
    HISTORY: 'writer_history_',
    WORD_COUNTS: 'writer_word_counts_',
    EDITOR_STATE: 'writer_editor_state',
    THEME: 'writer_theme'
};

/**
 * Save history for a section to localStorage
 */
export function saveHistory(section: string, history: any[]): void {
    try {
        const key = STORAGE_KEYS.HISTORY + section;
        localStorage.setItem(key, JSON.stringify(history));
        console.log(`[Storage] History saved for section: ${section}`);
    } catch (error) {
        console.error('[Storage] Failed to save history:', error);
    }
}

/**
 * Load history for a section from localStorage
 */
export function loadHistory(section: string): any[] {
    try {
        const key = STORAGE_KEYS.HISTORY + section;
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : [];
    } catch (error) {
        console.error('[Storage] Failed to load history:', error);
        return [];
    }
}

/**
 * Save word counts to localStorage
 */
export function saveWordCounts(section: string, docType: string, count: number): void {
    try {
        const key = STORAGE_KEYS.WORD_COUNTS + docType;
        const counts = loadWordCounts(docType);
        counts[section] = count;
        localStorage.setItem(key, JSON.stringify(counts));
    } catch (error) {
        console.error('[Storage] Failed to save word counts:', error);
    }
}

/**
 * Load word counts from localStorage
 */
export function loadWordCounts(docType: string): WordCounts {
    try {
        const key = STORAGE_KEYS.WORD_COUNTS + docType;
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : {};
    } catch (error) {
        console.error('[Storage] Failed to load word counts:', error);
        return {};
    }
}

/**
 * Load all word counts from localStorage
 */
export function loadAllWordCounts(): Record<string, WordCounts> {
    try {
        const result: Record<string, WordCounts> = {};
        const docTypes = ['manuscript', 'abstract', 'coverLetter'];
        
        docTypes.forEach(docType => {
            result[docType] = loadWordCounts(docType);
        });
        
        return result;
    } catch (error) {
        console.error('[Storage] Failed to load all word counts:', error);
        return {};
    }
}

/**
 * Save editor state to localStorage
 */
export function saveEditorState(state: any): void {
    try {
        localStorage.setItem(STORAGE_KEYS.EDITOR_STATE, JSON.stringify(state));
    } catch (error) {
        console.error('[Storage] Failed to save editor state:', error);
    }
}

/**
 * Load editor state from localStorage
 */
export function loadEditorState(): any {
    try {
        const data = localStorage.getItem(STORAGE_KEYS.EDITOR_STATE);
        return data ? JSON.parse(data) : null;
    } catch (error) {
        console.error('[Storage] Failed to load editor state:', error);
        return null;
    }
}

/**
 * Clear all storage data
 */
export function clearAll(): void {
    try {
        const keys = Object.keys(localStorage);
        keys.forEach(key => {
            if (key.startsWith('writer_')) {
                localStorage.removeItem(key);
            }
        });
        console.log('[Storage] All storage cleared');
    } catch (error) {
        console.error('[Storage] Failed to clear storage:', error);
    }
}
