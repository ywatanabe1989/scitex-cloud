/**
 * Type definitions for Code Workspace
 * All interfaces, types, and constants used across workspace modules
 */

export interface Project {
  id: number;
  name: string;
  owner: string;
  slug: string;
}

export interface EditorConfig {
  currentProject: Project | null;
  csrfToken: string;
}

export interface OpenFile {
  path: string;
  content: string;
  language: string;
}

export interface GitFileStatus {
  status: string;
  staged: boolean;
}

export interface GitDiff {
  line: number;
  status: string;
}

export const LANGUAGE_MAP: { [key: string]: string } = {
  ".py": "python",
  ".js": "javascript",
  ".ts": "typescript",
  ".html": "html",
  ".css": "css",
  ".json": "json",
  ".md": "markdown",
  ".yaml": "yaml",
  ".yml": "yaml",
  ".sh": "shell",
  ".bash": "shell",
  ".r": "r",
  ".R": "r",
  ".tex": "latex",
  ".bib": "bibtex",
  ".txt": "plaintext",
};

export const DEFAULT_SCRATCH_CONTENT = `# Welcome to Code Editor
# This is a scratch buffer for quick notes and code experiments
# Your changes here won't be saved unless you explicitly create a file

# Quick Tips:
# - Press Ctrl+O to open a file
# - Press Ctrl+S to save
# - Press Ctrl+N to create a new file
# - Press Ctrl+K to show all keyboard shortcuts
# - Press F5 to run Python files
# - Right-click in the file tree for more options

# Try some Python code:
def hello(name):
    return f"Hello, {name}!"

print(hello("World"))
`;
