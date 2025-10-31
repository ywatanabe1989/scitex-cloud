/**
 * Monaco Editor Module
 * Enhanced editor with Monaco Editor capabilities
 * Falls back to CodeMirror if Monaco is not available
 */

import { StorageManager } from '@/utils/storage';
import { HistoryEntry } from '@/types';

export interface MonacoEditorConfig {
    elementId: string;
    mode?: string;
    theme?: string;
    lineNumbers?: boolean;
    lineWrapping?: boolean;
    indentUnit?: number;
    useMonaco?: boolean;
}

export class EnhancedEditor {
    private editor: any; // Monaco or CodeMirror instance
    private editorType: 'monaco' | 'codemirror' = 'codemirror';
    private storage: StorageManager;
    private history: HistoryEntry[] = [];
    private historyIndex: number = -1;
    private maxHistorySize: number = 50;
    private onChangeCallback?: (content: string, wordCount: number) => void;
    private monacoEditor?: any;

    constructor(config: MonacoEditorConfig) {
        this.storage = new StorageManager('writer_editor_');

        // Try to use Monaco if requested and available
        if (config.useMonaco !== false && (window as any).monaco) {
            this.initializeMonaco(config);
        } else {
            this.initializeCodeMirror(config);
        }
    }

    /**
     * Initialize Monaco Editor
     */
    private initializeMonaco(config: MonacoEditorConfig): void {
        const element = document.getElementById(config.elementId);
        if (!element) {
            console.warn('[Editor] Element not found, falling back to CodeMirror');
            this.initializeCodeMirror(config);
            return;
        }

        // Wait for Monaco to be available
        const waitForMonaco = (): void => {
            if (!(window as any).monaco) {
                console.log('[Editor] Waiting for Monaco to load...');
                setTimeout(() => waitForMonaco(), 100);
                return;
            }

            try {
                const monaco = (window as any).monaco;

                // Register LaTeX language if not already registered
                console.log('[Monaco] Available languages:', monaco.languages.getLanguages().map((l: any) => l.id));
                const latexExists = monaco.languages.getLanguages().find((l: any) => l.id === 'latex');
                console.log('[Monaco] LaTeX language exists:', !!latexExists);

                if (!latexExists) {
                    console.log('[Monaco] Registering LaTeX language...');
                    monaco.languages.register({ id: 'latex' });

                    // Define LaTeX language configuration
                    monaco.languages.setLanguageConfiguration('latex', {
                        comments: {
                            lineComment: '%'
                        },
                        brackets: [
                            ['{', '}'],
                            ['[', ']'],
                            ['(', ')']
                        ],
                        autoClosingPairs: [
                            { open: '{', close: '}' },
                            { open: '[', close: ']' },
                            { open: '(', close: ')' },
                            { open: '$', close: '$' },
                            { open: '`', close: "'" }
                        ],
                        surroundingPairs: [
                            { open: '{', close: '}' },
                            { open: '[', close: ']' },
                            { open: '(', close: ')' },
                            { open: '$', close: '$' }
                        ]
                    });

                    // Define LaTeX syntax highlighting
                    monaco.languages.setMonarchTokensProvider('latex', {
                        tokenizer: {
                            root: [
                                [/%.*$/, 'comment'],
                                [/\\[a-zA-Z@]+/, 'keyword'],
                                [/\{/, 'delimiter.curly'],
                                [/\}/, 'delimiter.curly'],
                                [/\[/, 'delimiter.square'],
                                [/\]/, 'delimiter.square'],
                                [/\$\$/, 'string'],
                                [/\$/, 'string']
                            ]
                        }
                    });

                    // Register completion provider for LaTeX commands
                    console.log('[Monaco] Registering LaTeX completion provider...');
                    monaco.languages.registerCompletionItemProvider('latex', {
                        triggerCharacters: ['\\'],
                        provideCompletionItems: (model: any, position: any) => {
                            console.log('[Monaco] Completion requested at position:', position);
                            const word = model.getWordUntilPosition(position);
                            console.log('[Monaco] Word at position:', word);
                            const range = {
                                startLineNumber: position.lineNumber,
                                endLineNumber: position.lineNumber,
                                startColumn: word.startColumn,
                                endColumn: word.endColumn
                            };

                            const suggestions = [
                                // Document structure
                                { label: '\\documentclass', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\documentclass{article}', documentation: 'Document class' },
                                { label: '\\begin', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\begin{${1:environment}}\n\t$0\n\\end{${1:environment}}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Begin environment' },
                                { label: '\\end', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\end{${1:environment}}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'End environment' },
                                { label: '\\section', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\section{$0}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Section' },
                                { label: '\\subsection', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\subsection{$0}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Subsection' },
                                { label: '\\subsubsection', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\subsubsection{$0}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Subsubsection' },

                                // Text formatting
                                { label: '\\textbf', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\textbf{$0}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Bold text' },
                                { label: '\\textit', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\textit{$0}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Italic text' },
                                { label: '\\emph', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\emph{$0}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Emphasized text' },
                                { label: '\\texttt', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\texttt{$0}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Typewriter text' },

                                // Math mode
                                { label: '\\[', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\[\n\t$0\n\\]', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Display math' },
                                { label: '\\(', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\($0\\)', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Inline math' },
                                { label: '\\equation', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\begin{equation}\n\t$0\n\\end{equation}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Equation environment' },

                                // Figures and tables
                                { label: '\\figure', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\begin{figure}[htbp]\n\t\\centering\n\t\\includegraphics[width=0.8\\textwidth]{$1}\n\t\\caption{$2}\n\t\\label{fig:$3}\n\\end{figure}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Figure environment' },
                                { label: '\\table', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\begin{table}[htbp]\n\t\\centering\n\t\\caption{$1}\n\t\\label{tab:$2}\n\t\\begin{tabular}{$3}\n\t\t$0\n\t\\end{tabular}\n\\end{table}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Table environment' },

                                // Citations and references
                                { label: '\\cite', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\cite{$0}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Citation' },
                                { label: '\\ref', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\ref{$0}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Reference' },
                                { label: '\\label', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\label{$0}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Label' },

                                // Lists
                                { label: '\\itemize', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\begin{itemize}\n\t\\item $0\n\\end{itemize}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Itemize list' },
                                { label: '\\enumerate', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\begin{enumerate}\n\t\\item $0\n\\end{enumerate}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Enumerate list' },
                                { label: '\\item', kind: monaco.languages.CompletionItemKind.Keyword, insertText: '\\item $0', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'List item' }
                            ];

                            const completions = suggestions.map((s: any) => ({ ...s, range }));
                            console.log('[Monaco] Returning', completions.length, 'completions');
                            return { suggestions: completions };
                        }
                    });
                    console.log('[Monaco] LaTeX completion provider registered successfully');
                } else {
                    console.log('[Monaco] LaTeX language already registered, skipping');
                }

                // Define custom SciTeX dark theme with consistent background
                monaco.editor.defineTheme('scitex-dark', {
                    base: 'vs-dark',
                    inherit: true,
                    rules: [],
                    colors: {
                        'editor.background': '#1a2332',
                        'editor.lineHighlightBackground': '#1a2332',
                        'editorLineNumber.foreground': '#6c8ba0',
                        'editorLineNumber.activeForeground': '#b5c7d1',
                        'editor.selectionBackground': '#34495e',
                        'editor.inactiveSelectionBackground': '#2a3a4a'
                    }
                });

                // Get initial value before replacing element
                const textareaElement = element as HTMLTextAreaElement;
                const initialValue = textareaElement.value || '';

                // Create editor container
                const editorContainer = document.createElement('div');
                editorContainer.id = `${config.elementId}-monaco`;
                editorContainer.style.cssText = 'width: 100%; height: 100%; border: none;';
                element.parentElement?.replaceChild(editorContainer, element);

                this.monacoEditor = monaco.editor.create(editorContainer, {
                    value: initialValue,
                    language: 'latex',
                    theme: 'scitex-dark',
                    lineNumbers: config.lineNumbers !== false ? 'on' : 'off',
                    wordWrap: config.lineWrapping !== false ? 'on' : 'off',
                    tabSize: 4,
                    insertSpaces: true,
                    autoClosingBrackets: 'always',
                    automaticLayout: true,
                    minimap: { enabled: false },
                    scrollBeyondLastLine: false,
                    fontSize: 14,
                    lineHeight: 21,  // Fixed: was 19, now 21 (1.5x fontSize for proper cursor alignment)
                    fontFamily: 'Consolas, "Courier New", monospace',  // Fixed: use web-safe monospace fonts
                    renderLineHighlight: 'none',
                    suggestOnTriggerCharacters: true,
                    quickSuggestions: true,
                    wordBasedSuggestions: false,
                    scrollbar: {
                        vertical: 'visible',
                        horizontal: 'visible',
                        verticalScrollbarSize: 10,
                        horizontalScrollbarSize: 10,
                        alwaysConsumeMouseWheel: true
                    },
                    mouseWheelScrollSensitivity: 1,
                    fastScrollSensitivity: 5
                });

                this.editor = this.monacoEditor;
                this.editorType = 'monaco';
                this.setupMonacoEditor();
                console.log('[Editor] Monaco Editor initialized with LaTeX support');
            } catch (error) {
                console.warn('[Editor] Monaco initialization failed, falling back to CodeMirror', error);
                this.initializeCodeMirror(config);
            }
        };

        // Start waiting for Monaco
        waitForMonaco();
    }

    /**
     * Setup Monaco Editor event listeners
     */
    private setupMonacoEditor(): void {
        if (!this.monacoEditor) return;

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
    private initializeCodeMirror(config: MonacoEditorConfig): void {
        if ((window as any).CodeMirror) {
            const element = document.getElementById(config.elementId);
            if (!element) {
                throw new Error(`Editor element with id "${config.elementId}" not found`);
            }

            this.editor = (window as any).CodeMirror.fromTextArea(element, {
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
        } else {
            console.warn('[Editor] Neither Monaco nor CodeMirror available. Editor will not be initialized.');
        }
    }

    /**
     * Setup CodeMirror event listeners
     */
    private setupCodeMirrorEditor(): void {
        if (!this.editor || this.editorType !== 'codemirror') return;

        // Track changes
        this.editor.on('change', (editor: any) => {
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
    getContent(): string {
        if (!this.editor) return '';
        return this.editorType === 'monaco'
            ? this.monacoEditor.getValue()
            : this.editor.getValue();
    }

    /**
     * Set editor content
     */
    setContent(content: string, emitChange: boolean = false): void {
        if (!this.editor) return;

        if (this.editorType === 'monaco') {
            this.monacoEditor.setValue(content);
        } else {
            const doc = this.editor.getDoc();
            const lastLine = doc.lastLine();

            this.editor.replaceRange(
                content,
                { line: 0, ch: 0 },
                { line: lastLine, ch: doc.getLine(lastLine).length }
            );

            if (emitChange) {
                this.editor.execCommand('goDocEnd');
            }
        }
    }

    /**
     * Append content to editor
     */
    appendContent(content: string): void {
        if (!this.editor) return;

        if (this.editorType === 'monaco') {
            const currentContent = this.monacoEditor.getValue();
            this.monacoEditor.setValue(currentContent + content);
        } else {
            const doc = this.editor.getDoc();
            const lastLine = doc.lastLine();
            doc.replaceRange(content, { line: lastLine, ch: doc.getLine(lastLine).length });
        }
    }

    /**
     * Clear editor content
     */
    clear(): void {
        this.setContent('');
    }

    /**
     * Add entry to history
     */
    addToHistory(content: string, wordCount: number): void {
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
        } else {
            this.historyIndex++;
        }

        this.storage.save('history', this.history);
    }

    /**
     * Undo last change
     */
    undo(): boolean {
        if (this.editorType === 'monaco' && this.monacoEditor) {
            this.monacoEditor.trigger('keyboard', 'undo', null);
            return true;
        } else if (this.editor) {
            this.editor.execCommand('undo');
            return true;
        }
        return false;
    }

    /**
     * Redo change
     */
    redo(): boolean {
        if (this.editorType === 'monaco' && this.monacoEditor) {
            this.monacoEditor.trigger('keyboard', 'redo', null);
            return true;
        } else if (this.editor) {
            this.editor.execCommand('redo');
            return true;
        }
        return false;
    }

    /**
     * Count words in text
     */
    private countWords(text: string): number {
        const trimmed = text.trim();
        if (!trimmed) return 0;
        return trimmed.split(/\s+/).length;
    }

    /**
     * Generate simple hash for content
     */
    private generateHash(content: string): string {
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
    getWordCount(): number {
        return this.countWords(this.getContent());
    }

    /**
     * Set change callback
     */
    onChange(callback: (content: string, wordCount: number) => void): void {
        this.onChangeCallback = callback;
    }

    /**
     * Focus editor
     */
    focus(): void {
        if (this.editorType === 'monaco' && this.monacoEditor) {
            this.monacoEditor.focus();
        } else if (this.editor) {
            this.editor.focus();
        }
    }

    /**
     * Check if editor has unsaved changes
     */
    hasUnsavedChanges(lastSavedContent: string): boolean {
        return this.getContent() !== lastSavedContent;
    }

    /**
     * Get editor instance (for advanced usage)
     */
    getInstance(): any {
        return this.editor;
    }

    /**
     * Get editor type
     */
    getEditorType(): string {
        return this.editorType;
    }

    /**
     * Set editor theme
     */
    setTheme(theme: string): void {
        if (this.editorType === 'monaco' && this.monacoEditor) {
            console.log('[Editor] Setting Monaco theme to:', theme);
            // Map common CodeMirror theme names to Monaco themes
            const monacoThemeMap: Record<string, string> = {
                'zenburn': 'vs-dark',
                'monokai': 'vs-dark',
                'dracula': 'vs-dark',
                'eclipse': 'vs',
                'neat': 'vs',
                'solarized light': 'vs',
                'scitex-dark': 'scitex-dark',
                'default': 'vs'
            };
            const monacoTheme = monacoThemeMap[theme.toLowerCase()] || 'scitex-dark';
            (window as any).monaco.editor.setTheme(monacoTheme);
        } else {
            // CodeMirror theme change
            console.log('[Editor] Setting CodeMirror theme to:', theme);
            const cmEditor = (document.querySelector('.CodeMirror') as any)?.CodeMirror;
            if (cmEditor) {
                cmEditor.setOption('theme', theme);
            }
        }
    }

    /**
     * Set editor read-only state
     */
    setReadOnly(readOnly: boolean): void {
        if (this.editorType === 'monaco' && this.monacoEditor) {
            console.log('[Editor] Setting Monaco readOnly to:', readOnly);
            this.monacoEditor.updateOptions({ readOnly: readOnly });
        } else {
            // CodeMirror read-only mode
            console.log('[Editor] Setting CodeMirror readOnly to:', readOnly);
            const cmEditor = (document.querySelector('.CodeMirror') as any)?.CodeMirror;
            if (cmEditor) {
                cmEditor.setOption('readOnly', readOnly);
            }
        }
    }
}
