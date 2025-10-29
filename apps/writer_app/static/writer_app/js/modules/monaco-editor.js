/**
 * Monaco Editor Module
 * Enhanced editor with Monaco Editor capabilities
 * Falls back to CodeMirror if Monaco is not available
 */
import { StorageManager } from '@/utils/storage';
export class EnhancedEditor {
    constructor(config) {
        this.editorType = 'codemirror';
        this.history = [];
        this.historyIndex = -1;
        this.maxHistorySize = 50;
        this.storage = new StorageManager('writer_editor_');
        // Try to use Monaco if requested and available
        if (config.useMonaco !== false && window.monaco) {
            this.initializeMonaco(config);
        }
        else {
            this.initializeCodeMirror(config);
        }
    }
    /**
     * Initialize Monaco Editor
     */
    initializeMonaco(config) {
        const element = document.getElementById(config.elementId);
        if (!element) {
            console.warn('[Editor] Element not found, falling back to CodeMirror');
            this.initializeCodeMirror(config);
            return;
        }
        try {
            const monaco = window.monaco;
            // Create editor container if needed
            const editorContainer = document.createElement('div');
            editorContainer.id = `${config.elementId}-monaco`;
            editorContainer.style.cssText = 'width: 100%; height: 100%; border: none;';
            const textareaElement = element;
            element.parentElement?.replaceChild(editorContainer, element);
            this.monacoEditor = monaco.editor.create(editorContainer, {
                value: textareaElement.value || '',
                language: 'latex',
                theme: 'vs-dark',
                lineNumbers: config.lineNumbers !== false ? 'on' : 'off',
                wordWrap: config.lineWrapping !== false ? 'on' : 'off',
                tabSize: 4,
                insertSpaces: true,
                autoClosingBrackets: 'always',
                automaticLayout: true,
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                fontSize: 13,
                fontFamily: 'Monaco, Menlo, Ubuntu Mono, Consolas, monospace'
            });
            this.editor = this.monacoEditor;
            this.editorType = 'monaco';
            this.setupMonacoEditor();
            console.log('[Editor] Monaco Editor initialized');
        }
        catch (error) {
            console.warn('[Editor] Monaco initialization failed, falling back to CodeMirror', error);
            this.initializeCodeMirror(config);
        }
    }
    /**
     * Setup Monaco Editor event listeners
     */
    setupMonacoEditor() {
        if (!this.monacoEditor)
            return;
        // Track changes
        this.monacoEditor.onDidChangeModelContent(() => {
            const content = this.monacoEditor.getValue();
            const wordCount = this.countWords(content);
            if (this.onChangeCallback) {
                this.onChangeCallback(content, wordCount);
            }
        });
        console.log('[Editor] Monaco Editor listeners configured');
    }
    /**
     * Initialize CodeMirror fallback
     */
    initializeCodeMirror(config) {
        if (window.CodeMirror) {
            const element = document.getElementById(config.elementId);
            if (!element) {
                throw new Error(`Editor element with id "${config.elementId}" not found`);
            }
            this.editor = window.CodeMirror.fromTextArea(element, {
                mode: config.mode || 'text/x-latex',
                theme: config.theme || 'default',
                lineNumbers: config.lineNumbers !== false,
                lineWrapping: config.lineWrapping !== false,
                indentUnit: config.indentUnit || 4,
                tabSize: 4,
                indentWithTabs: false,
                autoCloseBrackets: true,
                matchBrackets: true
            });
            this.editorType = 'codemirror';
            this.setupCodeMirrorEditor();
        }
        else {
            console.warn('[Editor] Neither Monaco nor CodeMirror available. Editor will not be initialized.');
        }
    }
    /**
     * Setup CodeMirror event listeners
     */
    setupCodeMirrorEditor() {
        if (!this.editor || this.editorType !== 'codemirror')
            return;
        // Track changes
        this.editor.on('change', (editor) => {
            const content = editor.getValue();
            const wordCount = this.countWords(content);
            if (this.onChangeCallback) {
                this.onChangeCallback(content, wordCount);
            }
        });
        console.log('[Editor] CodeMirror initialized');
    }
    /**
     * Get editor content
     */
    getContent() {
        if (!this.editor)
            return '';
        return this.editorType === 'monaco'
            ? this.monacoEditor.getValue()
            : this.editor.getValue();
    }
    /**
     * Set editor content
     */
    setContent(content, emitChange = false) {
        if (!this.editor)
            return;
        if (this.editorType === 'monaco') {
            this.monacoEditor.setValue(content);
        }
        else {
            const doc = this.editor.getDoc();
            const lastLine = doc.lastLine();
            this.editor.replaceRange(content, { line: 0, ch: 0 }, { line: lastLine, ch: doc.getLine(lastLine).length });
            if (emitChange) {
                this.editor.execCommand('goDocEnd');
            }
        }
    }
    /**
     * Append content to editor
     */
    appendContent(content) {
        if (!this.editor)
            return;
        if (this.editorType === 'monaco') {
            const currentContent = this.monacoEditor.getValue();
            this.monacoEditor.setValue(currentContent + content);
        }
        else {
            const doc = this.editor.getDoc();
            const lastLine = doc.lastLine();
            doc.replaceRange(content, { line: lastLine, ch: doc.getLine(lastLine).length });
        }
    }
    /**
     * Clear editor content
     */
    clear() {
        this.setContent('');
    }
    /**
     * Add entry to history
     */
    addToHistory(content, wordCount) {
        this.history.splice(this.historyIndex + 1);
        this.history.push({
            content,
            timestamp: new Date().toISOString(),
            hash: this.generateHash(content + wordCount),
            message: `${wordCount} words`,
            author: 'editor',
        });
        if (this.history.length > this.maxHistorySize) {
            this.history.shift();
        }
        else {
            this.historyIndex++;
        }
        this.storage.save('history', this.history);
    }
    /**
     * Undo last change
     */
    undo() {
        if (this.editorType === 'monaco' && this.monacoEditor) {
            this.monacoEditor.trigger('keyboard', 'undo', null);
            return true;
        }
        else if (this.editor) {
            this.editor.execCommand('undo');
            return true;
        }
        return false;
    }
    /**
     * Redo change
     */
    redo() {
        if (this.editorType === 'monaco' && this.monacoEditor) {
            this.monacoEditor.trigger('keyboard', 'redo', null);
            return true;
        }
        else if (this.editor) {
            this.editor.execCommand('redo');
            return true;
        }
        return false;
    }
    /**
     * Count words in text
     */
    countWords(text) {
        const trimmed = text.trim();
        if (!trimmed)
            return 0;
        return trimmed.split(/\s+/).length;
    }
    /**
     * Generate simple hash for content
     */
    generateHash(content) {
        let hash = 0;
        for (let i = 0; i < content.length; i++) {
            const char = content.charCodeAt(i);
            hash = (hash << 5) - hash + char;
            hash = hash & hash;
        }
        return hash.toString(36);
    }
    /**
     * Get word count of current content
     */
    getWordCount() {
        return this.countWords(this.getContent());
    }
    /**
     * Set change callback
     */
    onChange(callback) {
        this.onChangeCallback = callback;
    }
    /**
     * Focus editor
     */
    focus() {
        if (this.editorType === 'monaco' && this.monacoEditor) {
            this.monacoEditor.focus();
        }
        else if (this.editor) {
            this.editor.focus();
        }
    }
    /**
     * Check if editor has unsaved changes
     */
    hasUnsavedChanges(lastSavedContent) {
        return this.getContent() !== lastSavedContent;
    }
    /**
     * Get editor instance (for advanced usage)
     */
    getInstance() {
        return this.editor;
    }
    /**
     * Get editor type
     */
    getEditorType() {
        return this.editorType;
    }
}
//# sourceMappingURL=monaco-editor.js.map