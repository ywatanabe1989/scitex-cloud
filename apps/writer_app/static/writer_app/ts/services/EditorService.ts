/**
 * EditorService manages CodeMirror editor operations
 */

import { EditorOptions, EditorTheme, ThemeConfig } from '@/types';
import { querySelector } from '@/writer/utils/dom.utils';
import { writerStorage } from '@/utils/storage';

declare const CodeMirror: any;

export class EditorService {
  private editor: any = null;
  private container: HTMLElement | null = null;
  private themeConfig: ThemeConfig = {
    dark: { name: 'dracula', label: 'Dracula', isDark: true },
    light: { name: 'neat', label: 'Neat', isDark: false },
  };
  private themeObserver: MutationObserver | null = null;

  /**
   * Initialize CodeMirror editor
   */
  initializeEditor(containerId: string, options?: Partial<EditorOptions>): boolean {
    this.container = querySelector<HTMLElement>(containerId);

    if (!this.container || typeof CodeMirror === 'undefined') {
      console.error('CodeMirror not loaded or container not found');
      return false;
    }

    const defaultOptions: EditorOptions = {
      mode: 'stex',
      theme: this.getSavedTheme(),
      lineNumbers: true,
      indentUnit: 2,
      indentWithTabs: false,
      lineWrapping: true,
      matchBrackets: true,
      autoCloseBrackets: true,
      highlightSelectionMatches: { showToken: /\w/, annotateScrollbar: true },
      styleActiveLine: true,
      readOnly: false,
      extraKeys: {
        'Ctrl-/': 'toggleComment',
        'Shift-Ctrl-/': 'toggleComment',
      },
    };

    const finalOptions = { ...defaultOptions, ...options };

    this.editor = CodeMirror(this.container, finalOptions);

    // Setup keyboard shortcuts
    this.setupKeyboardShortcuts();

    // Setup theme observer
    this.setupThemeObserver();

    return true;
  }

  /**
   * Get editor instance
   */
  getEditor(): any {
    return this.editor;
  }

  /**
   * Get editor content
   */
  getContent(): string {
    return this.editor?.getValue() || '';
  }

  /**
   * Set editor content
   */
  setContent(content: string): void {
    if (this.editor) {
      this.editor.setValue(content);
      this.editor.clearHistory();
    }
  }

  /**
   * Clear editor content
   */
  clearContent(): void {
    if (this.editor) {
      this.editor.setValue('');
    }
  }

  /**
   * Focus editor
   */
  focus(): void {
    if (this.editor) {
      this.editor.focus();
    }
  }

  /**
   * Get cursor position
   */
  getCursorPosition(): { line: number; ch: number } {
    if (this.editor) {
      return this.editor.getCursor();
    }
    return { line: 0, ch: 0 };
  }

  /**
   * Set cursor position
   */
  setCursorPosition(line: number, ch: number): void {
    if (this.editor) {
      this.editor.setCursor({ line, ch });
    }
  }

  /**
   * Get selected text
   */
  getSelectedText(): string {
    return this.editor?.getSelection() || '';
  }

  /**
   * Replace selected text
   */
  replaceSelectedText(text: string): void {
    if (this.editor) {
      this.editor.replaceSelection(text);
    }
  }

  /**
   * Get line count
   */
  getLineCount(): number {
    return this.editor?.lineCount() || 0;
  }

  /**
   * Set editor theme
   */
  setTheme(theme: string): void {
    if (this.editor) {
      this.editor.setOption('theme', theme);
      this.saveTheme(theme);
    }
  }

  /**
   * Get current theme
   */
  getCurrentTheme(): string {
    return this.editor?.getOption('theme') || this.themeConfig.light.name;
  }

  /**
   * Get available themes for current site mode
   */
  getAvailableThemes(isDarkMode: boolean): EditorTheme[] {
    // Return theme based on site mode
    return isDarkMode
      ? [
          this.themeConfig.dark,
          { name: 'zenburn', label: 'Zenburn', isDark: true },
          { name: 'eclipse', label: 'Eclipse', isDark: false },
        ]
      : [
          this.themeConfig.light,
          { name: 'eclipse', label: 'Eclipse', isDark: false },
          { name: 'solarized light', label: 'Solarized Light', isDark: false },
        ];
  }

  /**
   * Enable/disable editor
   */
  setReadOnly(readOnly: boolean): void {
    if (this.editor) {
      this.editor.setOption('readOnly', readOnly);
    }
  }

  /**
   * Check if editor is read-only
   */
  isReadOnly(): boolean {
    return this.editor?.getOption('readOnly') ?? false;
  }

  /**
   * Register change listener
   */
  onChange(callback: (editor: any) => void): () => void {
    if (!this.editor) return () => {};

    this.editor.on('change', callback);

    // Return unregister function
    return () => this.editor.off('change', callback);
  }

  /**
   * Get editor options
   */
  getOptions(): EditorOptions {
    if (!this.editor) {
      return this.getDefaultOptions();
    }

    return {
      mode: this.editor.getOption('mode'),
      theme: this.editor.getOption('theme'),
      lineNumbers: this.editor.getOption('lineNumbers'),
      indentUnit: this.editor.getOption('indentUnit'),
      indentWithTabs: this.editor.getOption('indentWithTabs'),
      lineWrapping: this.editor.getOption('lineWrapping'),
      matchBrackets: this.editor.getOption('matchBrackets'),
      autoCloseBrackets: this.editor.getOption('autoCloseBrackets'),
      highlightSelectionMatches: this.editor.getOption('highlightSelectionMatches'),
      styleActiveLine: this.editor.getOption('styleActiveLine'),
      readOnly: this.editor.getOption('readOnly'),
      extraKeys: this.editor.getOption('extraKeys'),
    };
  }

  /**
   * Refresh editor layout
   */
  refresh(): void {
    if (this.editor) {
      this.editor.refresh();
    }
  }

  /**
   * Destroy editor
   */
  destroy(): void {
    if (this.themeObserver) {
      this.themeObserver.disconnect();
    }
    if (this.editor && this.container) {
      this.container.innerHTML = '';
      this.editor = null;
    }
  }

  /**
   * Setup keyboard shortcuts for editor
   */
  private setupKeyboardShortcuts(): void {
    if (!this.editor) return;

    // Additional shortcuts can be added here
    this.editor.setOption('extraKeys', {
      ...this.editor.getOption('extraKeys'),
      'Ctrl-/': () => this.editor.toggleComment({ indent: true }),
    });
  }

  /**
   * Setup theme observer for site theme changes
   */
  private setupThemeObserver(): void {
    const root = document.documentElement;

    this.themeObserver = new MutationObserver(() => {
      const isDarkMode = root.classList.contains('dark-mode');
      const currentTheme = this.getCurrentTheme();
      const shouldBeDark = this.themeConfig.dark.name === currentTheme;

      if ((isDarkMode && !shouldBeDark) || (!isDarkMode && shouldBeDark)) {
        // Theme mismatch, update editor theme
        const newTheme = isDarkMode ? this.themeConfig.dark.name : this.themeConfig.light.name;
        this.setTheme(newTheme);
      }
    });

    this.themeObserver.observe(root, {
      attributes: true,
      attributeFilter: ['class'],
    });
  }

  /**
   * Save theme preference
   */
  private saveTheme(theme: string): void {
    writerStorage.save('editorTheme', theme);
  }

  /**
   * Get saved theme preference
   */
  private getSavedTheme(): string {
    const saved = writerStorage.load<string>('editorTheme');
    if (saved) return saved;

    // Default based on site mode
    const isDarkMode = document.documentElement.classList.contains('dark-mode');
    return isDarkMode ? this.themeConfig.dark.name : this.themeConfig.light.name;
  }

  /**
   * Get default editor options
   */
  private getDefaultOptions(): EditorOptions {
    return {
      mode: 'stex',
      theme: this.getSavedTheme(),
      lineNumbers: true,
      indentUnit: 2,
      indentWithTabs: false,
      lineWrapping: true,
      matchBrackets: true,
      autoCloseBrackets: true,
      highlightSelectionMatches: true,
      styleActiveLine: true,
      readOnly: false,
      extraKeys: {},
    };
  }
}

// Global EditorService instance
export const editorService = new EditorService();
