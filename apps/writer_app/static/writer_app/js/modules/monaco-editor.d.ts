/**
 * Monaco Editor Module
 * Enhanced editor with Monaco Editor capabilities
 * Falls back to CodeMirror if Monaco is not available
 */
export interface MonacoEditorConfig {
    elementId: string;
    mode?: string;
    theme?: string;
    lineNumbers?: boolean;
    lineWrapping?: boolean;
    indentUnit?: number;
    useMonaco?: boolean;
}
export declare class EnhancedEditor {
    private editor;
    private editorType;
    private storage;
    private history;
    private historyIndex;
    private maxHistorySize;
    private onChangeCallback?;
    private monacoEditor?;
    constructor(config: MonacoEditorConfig);
    /**
     * Initialize Monaco Editor
     */
    private initializeMonaco;
    /**
     * Setup Monaco Editor event listeners
     */
    private setupMonacoEditor;
    /**
     * Initialize CodeMirror fallback
     */
    private initializeCodeMirror;
    /**
     * Setup CodeMirror event listeners
     */
    private setupCodeMirrorEditor;
    /**
     * Get editor content
     */
    getContent(): string;
    /**
     * Set editor content
     */
    setContent(content: string, emitChange?: boolean): void;
    /**
     * Append content to editor
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
    /**
     * Get editor type
     */
    getEditorType(): string;
    /**
     * Set editor theme
     */
    setTheme(theme: string): void;
}
//# sourceMappingURL=monaco-editor.d.ts.map