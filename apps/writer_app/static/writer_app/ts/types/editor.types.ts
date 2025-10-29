/**
 * Editor-related type definitions
 */

export interface EditorState {
  content: string;
  cursorPosition: CodeMirror.Position;
  scrollPosition: number;
}

export interface EditorOptions {
  mode: string;
  theme: string;
  lineNumbers: boolean;
  indentUnit: number;
  indentWithTabs: boolean;
  lineWrapping: boolean;
  matchBrackets: boolean;
  autoCloseBrackets: boolean;
  highlightSelectionMatches: boolean;
  styleActiveLine: boolean;
  readOnly: boolean;
  extraKeys: Record<string, string | ((cm: CodeMirror.Editor) => void)>;
}

export interface PreviewState {
  mode: 'latex' | 'preview' | 'split';
  content: string;
  wordCount: number;
}

export interface EditorTheme {
  name: string;
  label: string;
  isDark: boolean;
}

export interface ThemeConfig {
  dark: EditorTheme;
  light: EditorTheme;
}
