/**
 * Writer Editor Module
 * Handles CodeMirror editor initialization and management
 */
export interface EditorConfig {
    elementId: string;
    mode?: string;
    theme?: string;
    lineNumbers?: boolean;
    lineWrapping?: boolean;
    indentUnit?: number;
}
export declare class WriterEditor {
    private editor;
    private storage;
    private history;
    private historyIndex;
    private maxHistorySize;
    private onChangeCallback?;
    constructor(config: EditorConfig);
    /**
     * Setup editor event listeners
     */
    private setupEditor;
    /**
     * Get editor content
     */
    getContent(): string;
    /**
     * Set editor content
     */
    setContent(content: string, emitChange?: boolean): void;
    /**
     * Add content to editor
     */
    appendContent(content: string): void;
    /**
     * Clear editor content
     */
    clear(): void;
    /**
     * Add entry to history
     */
    addToHistory(content: string, wordCount: number): void;
    /**
     * Undo last change
     */
    undo(): boolean;
    /**
     * Redo change
     */
    redo(): boolean;
    /**
     * Check if can undo
     */
    canUndo(): boolean;
    /**
     * Check if can redo
     */
    canRedo(): boolean;
    /**
     * Load history from storage
     */
    loadHistory(): void;
    /**
     * Count words in text
     */
    private countWords;
    /**
     * Generate simple hash for content
     */
    private generateHash;
    /**
     * Get word count of current content
     */
    getWordCount(): number;
    /**
     * Set change callback
     */
    onChange(callback: (content: string, wordCount: number) => void): void;
    /**
     * Focus editor
     */
    focus(): void;
    /**
     * Check if editor has unsaved changes
     */
    hasUnsavedChanges(lastSavedContent: string): boolean;
    /**
     * Get editor instance (for advanced usage)
     */
    getInstance(): any;
}
//# sourceMappingURL=editor.d.ts.map