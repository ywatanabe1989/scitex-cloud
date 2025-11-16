/**
 * Code Workspace TypeScript
 * Corresponds to: templates/code_app/workspace.html
 * Provides IDE-like functionality with Monaco editor and interactive terminal
 */

import { buildCodeTreeHTML, toggleCodeFolder } from "./file-tree-builder.js";
import { ansiToHtml } from "./ansi-colors.js";
import { renderWithPathLinks, detectPaths } from "./path-linker.js";
import { PTYTerminal } from "./pty-terminal.js";

console.log("[DEBUG] apps/code_app/static/code_app/ts/workspace.ts loaded");

interface Project {
  id: number;
  name: string;
  owner: string;
  slug: string;
}

interface EditorConfig {
  currentProject: Project | null;
  csrfToken: string;
}

// Make toggleCodeFolder available globally for HTML onclick handlers
(window as any).toggleCodeFolder = toggleCodeFolder;

interface OpenFile {
  path: string;
  content: string;
  language: string;
}

class CodeWorkspace {
  private editor: any = null;
  private currentFile: string | null = null;
  private config: EditorConfig;
  private fileList: string[] = []; // For tab completion
  private openFiles: Map<string, OpenFile> = new Map(); // Track open files
  private ptyTerminal: PTYTerminal | null = null; // Real PTY terminal (exclusive mode)
  private gitStatusCache: Map<string, { status: string; staged: boolean }> = new Map(); // Git status cache
  private currentDecorations: string[] = []; // Monaco decorations for git gutter
  private languageMap: { [key: string]: string } = {
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
    ".bib": "bibtex", // BibTeX files
    ".txt": "plaintext",
  };

  constructor(config: EditorConfig) {
    this.config = config;
    this.init();
  }

  private init(): void {
    console.log("[CodeWorkspace] Initializing...");

    if (!this.config.currentProject) {
      this.showNoProjectMessage();
      return;
    }

    this.loadFileTree();
    this.attachEventListeners();
    this.initMonaco();
    this.initPTYTerminal(); // PTY only - removed simple terminal
    this.initContextMenu();

    // Show scratch buffer by default (like Emacs)
    this.initScratchBuffer();
  }

  private initPTYTerminal(): void {
    const ptyTerminalEl = document.getElementById("pty-terminal");
    if (!ptyTerminalEl || !this.config.currentProject) return;

    // Create PTY terminal immediately
    this.ptyTerminal = new PTYTerminal(
      ptyTerminalEl,
      this.config.currentProject.id,
    );
    console.log("[CodeWorkspace] PTY terminal initialized");
  }

  private showNoProjectMessage(): void {
    const fileTreeContainer = document.getElementById("file-tree");
    if (fileTreeContainer) {
      fileTreeContainer.innerHTML = `
        <div class="tree-loading" style="padding: 16px; text-align: center; color: var(--color-fg-muted);">
          Please select a project from the dropdown above
        </div>
      `;
    }
  }

  private async loadFileTree(): Promise<void> {
    if (!this.config.currentProject) return;

    const { owner, slug } = this.config.currentProject;

    try {
      const response = await fetch(`/${owner}/${slug}/api/file-tree/`);
      const data = await response.json();

      const treeContainer = document.getElementById("file-tree");
      if (!treeContainer) {
        console.error("File tree container not found");
        return;
      }

      if (data.success) {
        treeContainer.innerHTML = buildCodeTreeHTML(data.tree, owner, slug);
        this.attachFileClickHandlers();
        // Build file list for tab completion
        this.buildFileList(data.tree);
      } else {
        treeContainer.innerHTML =
          '<div class="tree-loading">Error loading file tree</div>';
      }
    } catch (err) {
      console.error("Failed to load file tree:", err);
      const treeContainer = document.getElementById("file-tree");
      if (treeContainer) {
        treeContainer.innerHTML =
          '<div class="tree-loading">Error loading file tree</div>';
      }
    }
  }

  private attachFileClickHandlers(): void {
    document.querySelectorAll(".file-tree-file").forEach((fileElement) => {
      fileElement.addEventListener("click", async (e) => {
        e.preventDefault();
        const filePath = fileElement.getAttribute("data-file-path");
        if (!filePath) return;

        await this.loadFile(filePath);
      });
    });
  }

  private attachEventListeners(): void {
    // Keybinding mode selector
    const keybindingMode = document.getElementById(
      "keybinding-mode",
    ) as HTMLSelectElement;
    const btnEditorShortcuts = document.getElementById(
      "btn-editor-shortcuts",
    ) as HTMLButtonElement;

    if (keybindingMode) {
      // Function to update tooltip based on mode
      const updateShortcutsTooltip = () => {
        if (btnEditorShortcuts) {
          const mode = keybindingMode.value;
          const tooltips: { [key: string]: string } = {
            vscode: "VS Code Shortcuts (not confirmed)",
            vim: "Vim Shortcuts (not confirmed)",
            emacs: "Emacs Shortcuts (confirmed ✓)",
          };
          btnEditorShortcuts.title = tooltips[mode] || "Keyboard Shortcuts";
        }
      };

      keybindingMode.addEventListener("change", (e) => {
        const mode = (e.target as HTMLSelectElement).value;
        this.setKeybindingMode(mode);
        localStorage.setItem("code-keybinding-mode", mode);
        updateShortcutsTooltip();
      });

      // Load saved preference or default to Emacs
      const savedMode = localStorage.getItem("code-keybinding-mode");
      if (savedMode) {
        keybindingMode.value = savedMode;
      } else {
        // Default to Emacs if no saved preference
        keybindingMode.value = "emacs";
        localStorage.setItem("code-keybinding-mode", "emacs");
      }

      // Set initial tooltip
      updateShortcutsTooltip();
    }

    // Editor shortcuts button (keyboard icon)
    if (btnEditorShortcuts) {
      btnEditorShortcuts.addEventListener("click", () => {
        this.showShortcutsModal();
      });
    }

    // Save button
    const btnSave = document.getElementById("btn-save");
    if (btnSave) {
      btnSave.addEventListener("click", () => this.saveFile());
    }

    // Run button
    const btnRun = document.getElementById("btn-run");
    if (btnRun) {
      btnRun.addEventListener("click", () => this.runFile());
    }

    // Delete button
    const btnDelete = document.getElementById("btn-delete");
    if (btnDelete) {
      btnDelete.addEventListener("click", () => this.deleteCurrentFile());
    }

    // Commit button
    const btnCommit = document.getElementById("btn-commit");
    if (btnCommit) {
      btnCommit.addEventListener("click", () => this.showCommitModal());
    }

    // Terminal shortcuts button
    const btnTerminalShortcuts = document.getElementById(
      "btn-terminal-shortcuts",
    );
    if (btnTerminalShortcuts) {
      btnTerminalShortcuts.addEventListener("click", () => {
        const modal = document.getElementById("terminal-shortcuts-modal");
        if (modal) {
          modal.classList.add("active");
        }
      });
    }

    // New file button (in tab bar)
    const btnNewFileTab = document.getElementById("btn-new-file-tab");
    if (btnNewFileTab) {
      btnNewFileTab.addEventListener("click", () => this.createNewFile());
    }

    // Global keyboard shortcuts (using Alt/Meta to avoid conflicts)
    document.addEventListener("keydown", (e) => {
      // Alt+T to focus editor
      if (e.altKey && e.key === "t") {
        e.preventDefault();
        if (this.editor) {
          this.editor.focus();
        }
      }

      // Ctrl+S to save (if file is open)
      if (e.ctrlKey && e.key === "s") {
        e.preventDefault();
        if (this.currentFile && this.editor) {
          this.saveFile();
        }
      }

      // Ctrl+Enter to run Python file (standard shortcut)
      if (e.ctrlKey && e.key === "Enter") {
        e.preventDefault();
        if (this.currentFile && this.currentFile.endsWith(".py")) {
          this.runFile();
        }
      }

      // Ctrl+Tab: Next tab
      if (e.ctrlKey && e.key === "Tab" && !e.shiftKey) {
        e.preventDefault();
        this.switchToNextTab();
        console.log("[Tabs] Ctrl+Tab: next tab");
      }

      // Ctrl+Shift+Tab: Previous tab
      if (e.ctrlKey && e.shiftKey && e.key === "Tab") {
        e.preventDefault();
        this.switchToPreviousTab();
        console.log("[Tabs] Ctrl+Shift+Tab: previous tab");
      }

      // Ctrl+1 through Ctrl+9: Switch to specific tab
      if (e.ctrlKey && !e.shiftKey && !e.altKey) {
        const num = parseInt(e.key);
        if (num >= 1 && num <= 9) {
          e.preventDefault();
          this.switchToTabByIndex(num - 1);
          console.log("[Tabs] Ctrl+" + num + ": switch to tab " + num);
        }
      }

      // Ctrl+Shift+R: Reset scratch buffer to default
      if (e.ctrlKey && e.shiftKey && e.key === "R") {
        e.preventDefault();
        this.resetScratchBuffer();
        console.log("[Scratch] Buffer reset to default");
      }

      // Note: Ctrl+M is Enter in terminals, so we don't override it
    });
  }

  private showShortcutsModal(): void {
    const modal = document.getElementById("shortcuts-modal-overlay");
    const modalTitle = document.getElementById("shortcuts-modal-title");
    const modalBody = document.getElementById("shortcuts-modal-body");
    const keybindingMode = document.getElementById(
      "keybinding-mode",
    ) as HTMLSelectElement;

    if (!modal || !modalBody || !keybindingMode) return;

    const mode = keybindingMode.value;
    let title = "Confirmed Shortcuts";
    let content = "";

    if (mode === "emacs") {
      title = "Emacs Shortcuts";
      content = this.getEmacsShortcutsHTML();
    } else if (mode === "vim") {
      title = "Vim Shortcuts";
      content = this.getVimShortcutsHTML();
    } else {
      title = "VS Code Shortcuts";
      content = this.getVSCodeShortcutsHTML();
    }

    if (modalTitle) {
      modalTitle.innerHTML = `<i class="fas fa-keyboard"></i> ${title}`;
    }
    modalBody.innerHTML = content;
    modal.classList.add("active");
  }

  private getEmacsShortcutsHTML(): string {
    return `
      <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
        <thead>
          <tr style="background: var(--color-canvas-subtle); border-bottom: 2px solid var(--color-border-default);">
            <th style="padding: 8px; text-align: left; font-weight: 600;">Shortcut</th>
            <th style="padding: 8px; text-align: left; font-weight: 600;">Description</th>
          </tr>
        </thead>
        <tbody>
          <tr style="background: var(--color-canvas-subtle);"><td colspan="2" style="padding: 6px 8px; font-weight: bold;">Motion</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>C-f</kbd> / <kbd>C-b</kbd></td><td style="padding: 6px 8px;">Forward/Backward character</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>M-f</kbd> / <kbd>M-b</kbd></td><td style="padding: 6px 8px;">Forward/Backward word</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Alt+N</kbd> / <kbd>Alt+P</kbd></td><td style="padding: 6px 8px;">Next/Previous line</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>C-a</kbd> / <kbd>C-e</kbd></td><td style="padding: 6px 8px;">Line beginning/end</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>M-&lt;</kbd> / <kbd>M-&gt;</kbd></td><td style="padding: 6px 8px;">Buffer beginning/end</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>C-v</kbd> / <kbd>M-v</kbd></td><td style="padding: 6px 8px;">Scroll page down/up</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>M-g</kbd></td><td style="padding: 6px 8px;">Goto line</td></tr>
          <tr style="background: var(--color-canvas-subtle);"><td colspan="2" style="padding: 6px 8px; font-weight: bold;">Editing</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>C-k</kbd></td><td style="padding: 6px 8px;">Kill line (copies to clipboard)</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>M-d</kbd> / <kbd>M-DEL</kbd></td><td style="padding: 6px 8px;">Kill word forward/backward</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>C-d</kbd> / <kbd>C-h</kbd></td><td style="padding: 6px 8px;">Delete char forward/backward</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>M-x</kbd></td><td style="padding: 6px 8px;">Kill region (cut)</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>M-w</kbd></td><td style="padding: 6px 8px;">Copy region</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>C-y</kbd></td><td style="padding: 6px 8px;">Yank (paste)</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>C-SPC</kbd></td><td style="padding: 6px 8px;">Set mark (extends selection)</td></tr>
          <tr style="background: var(--color-canvas-subtle);"><td colspan="2" style="padding: 6px 8px; font-weight: bold;">Tabs</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Ctrl+Tab</kbd> / <kbd>Ctrl+Shift+Tab</kbd></td><td style="padding: 6px 8px;">Next/Previous tab</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Ctrl+1</kbd> ~ <kbd>Ctrl+9</kbd></td><td style="padding: 6px 8px;">Switch to tab 1-9</td></tr>
          <tr style="background: var(--color-canvas-subtle);"><td colspan="2" style="padding: 6px 8px; font-weight: bold;">Commands (C-x prefix)</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>C-x</kbd> <kbd>C-s</kbd></td><td style="padding: 6px 8px;">Save file</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>C-x</kbd> <kbd>C-f</kbd></td><td style="padding: 6px 8px;">Find file</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>C-x</kbd> <kbd>C-u</kbd>/<kbd>C-l</kbd></td><td style="padding: 6px 8px;">Uppercase/Lowercase region</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>C-x</kbd> <kbd>u</kbd> or <kbd>C-/</kbd></td><td style="padding: 6px 8px;">Undo</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>M-%</kbd></td><td style="padding: 6px 8px;">Query replace</td></tr>
        </tbody>
      </table>
    `;
  }

  private getVSCodeShortcutsHTML(): string {
    return `
      <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
        <thead>
          <tr style="background: var(--color-canvas-subtle); border-bottom: 2px solid var(--color-border-default);">
            <th style="padding: 8px; text-align: left; font-weight: 600;">Shortcut</th>
            <th style="padding: 8px; text-align: left; font-weight: 600;">Description</th>
          </tr>
        </thead>
        <tbody>
          <tr style="background: var(--color-canvas-subtle);"><td colspan="2" style="padding: 6px 8px; font-weight: bold;">Editing</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Ctrl+X</kbd> / <kbd>C</kbd> / <kbd>V</kbd></td><td style="padding: 6px 8px;">Cut / Copy / Paste</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Ctrl+Z</kbd> / <kbd>Y</kbd></td><td style="padding: 6px 8px;">Undo / Redo</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Ctrl+A</kbd></td><td style="padding: 6px 8px;">Select all</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Ctrl+D</kbd></td><td style="padding: 6px 8px;">Add selection to next find match</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Ctrl+/</kbd></td><td style="padding: 6px 8px;">Toggle line comment</td></tr>
          <tr style="background: var(--color-canvas-subtle);"><td colspan="2" style="padding: 6px 8px; font-weight: bold;">Navigation</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Ctrl+G</kbd></td><td style="padding: 6px 8px;">Go to line</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Ctrl+P</kbd></td><td style="padding: 6px 8px;">Quick file open</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Ctrl+F</kbd></td><td style="padding: 6px 8px;">Find</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Ctrl+H</kbd></td><td style="padding: 6px 8px;">Replace</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Home</kbd> / <kbd>End</kbd></td><td style="padding: 6px 8px;">Go to line start/end</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Ctrl+Home</kbd> / <kbd>End</kbd></td><td style="padding: 6px 8px;">Go to file start/end</td></tr>
          <tr style="background: var(--color-canvas-subtle);"><td colspan="2" style="padding: 6px 8px; font-weight: bold;">Selection</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Alt+Shift+Drag</kbd></td><td style="padding: 6px 8px;">Column (rectangle) selection</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Ctrl+Alt+Up/Down</kbd></td><td style="padding: 6px 8px;">Add cursor above/below</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Alt+Click</kbd></td><td style="padding: 6px 8px;">Insert cursor</td></tr>
          <tr style="background: var(--color-canvas-subtle);"><td colspan="2" style="padding: 6px 8px; font-weight: bold;">Code Actions</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Ctrl+Space</kbd></td><td style="padding: 6px 8px;">Trigger suggestions</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Ctrl+Shift+K</kbd></td><td style="padding: 6px 8px;">Delete line</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Ctrl+]</kbd> / <kbd>[</kbd></td><td style="padding: 6px 8px;">Indent / Outdent line</td></tr>
        </tbody>
      </table>
    `;
  }

  private getVimShortcutsHTML(): string {
    return `
      <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
        <thead>
          <tr style="background: var(--color-canvas-subtle); border-bottom: 2px solid var(--color-border-default);">
            <th style="padding: 8px; text-align: left; font-weight: 600;">Shortcut</th>
            <th style="padding: 8px; text-align: left; font-weight: 600;">Description</th>
          </tr>
        </thead>
        <tbody>
          <tr style="background: var(--color-attention-subtle);"><td colspan="2" style="padding: 6px 8px;">
            <strong>⚠️ Note:</strong> Vim mode requires monaco-vim extension. Basic Vim keybindings may not work.
          </td></tr>
          <tr style="background: var(--color-canvas-subtle);"><td colspan="2" style="padding: 6px 8px; font-weight: bold;">Normal Mode</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>h</kbd> <kbd>j</kbd> <kbd>k</kbd> <kbd>l</kbd></td><td style="padding: 6px 8px;">Left / Down / Up / Right</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>w</kbd> / <kbd>b</kbd></td><td style="padding: 6px 8px;">Word forward / backward</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>0</kbd> / <kbd>$</kbd></td><td style="padding: 6px 8px;">Line start / end</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>gg</kbd> / <kbd>G</kbd></td><td style="padding: 6px 8px;">File start / end</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>:</kbd><i>num</i></td><td style="padding: 6px 8px;">Go to line number</td></tr>
          <tr style="background: var(--color-canvas-subtle);"><td colspan="2" style="padding: 6px 8px; font-weight: bold;">Insert Mode</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>i</kbd> / <kbd>a</kbd></td><td style="padding: 6px 8px;">Insert before/after cursor</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>I</kbd> / <kbd>A</kbd></td><td style="padding: 6px 8px;">Insert at line start/end</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>o</kbd> / <kbd>O</kbd></td><td style="padding: 6px 8px;">Open line below/above</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Esc</kbd></td><td style="padding: 6px 8px;">Return to normal mode</td></tr>
          <tr style="background: var(--color-canvas-subtle);"><td colspan="2" style="padding: 6px 8px; font-weight: bold;">Editing</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>x</kbd> / <kbd>X</kbd></td><td style="padding: 6px 8px;">Delete char after/before</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>dd</kbd></td><td style="padding: 6px 8px;">Delete line</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>yy</kbd></td><td style="padding: 6px 8px;">Yank (copy) line</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>p</kbd> / <kbd>P</kbd></td><td style="padding: 6px 8px;">Paste after/before</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>u</kbd> / <kbd>Ctrl+R</kbd></td><td style="padding: 6px 8px;">Undo / Redo</td></tr>
          <tr style="background: var(--color-canvas-subtle);"><td colspan="2" style="padding: 6px 8px; font-weight: bold;">Visual Mode</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>v</kbd></td><td style="padding: 6px 8px;">Visual character mode</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>V</kbd></td><td style="padding: 6px 8px;">Visual line mode</td></tr>
          <tr><td style="padding: 6px 8px;"><kbd>Ctrl+V</kbd></td><td style="padding: 6px 8px;">Visual block mode</td></tr>
        </tbody>
      </table>
    `;
  }

  private initMonaco(): void {
    // Monaco will be loaded by the template's require() call
    // We just need to wait for it to be available
    console.log("[CodeWorkspace] Waiting for Monaco...");
  }

  private async createMonacoEditor(language: string = "python"): Promise<void> {
    // Wait for Monaco to be available with better error handling
    await new Promise<void>((resolve) => {
      // Check if already loaded
      if ((window as any).monaco) {
        console.log("[CodeWorkspace] Monaco already available");
        resolve();
        return;
      }

      // Check if monacoReady flag is set
      if ((window as any).monacoReady) {
        console.log("[CodeWorkspace] Monaco ready flag set, waiting for object...");
        // Give it a moment to populate
        setTimeout(() => resolve(), 100);
        return;
      }

      let attempts = 0;
      const maxAttempts = 100; // 10 seconds total
      const checkInterval = 100;

      const checkMonaco = () => {
        attempts++;

        if ((window as any).monaco) {
          console.log(`[CodeWorkspace] Monaco loaded after ${attempts * checkInterval}ms`);
          resolve();
        } else if ((window as any).monacoReady && attempts > 5) {
          // If monacoReady is set but window.monaco is still not available after 500ms, something is wrong
          console.error("[CodeWorkspace] monacoReady flag set but window.monaco is undefined");
          resolve(); // Resolve anyway to prevent indefinite waiting
        } else if (attempts < maxAttempts) {
          setTimeout(checkMonaco, checkInterval);
        } else {
          console.error(`[CodeWorkspace] Monaco timeout after ${attempts * checkInterval}ms`);
          console.error("[CodeWorkspace] window.monaco:", (window as any).monaco);
          console.error("[CodeWorkspace] window.monacoReady:", (window as any).monacoReady);
          console.error("[CodeWorkspace] window.require:", typeof (window as any).require);
          resolve();
        }
      };

      // Listen for the monaco-ready event
      const eventHandler = () => {
        console.log("[CodeWorkspace] monaco-ready event received");
        // Give Monaco a moment to fully initialize
        setTimeout(() => resolve(), 50);
      };
      window.addEventListener("monaco-ready", eventHandler, { once: true });

      // Start polling
      checkMonaco();
    });

    const monaco = (window as any).monaco;
    if (!monaco) {
      console.warn(
        "[CodeWorkspace] Monaco not available - keeping welcome screen",
      );
      console.warn(
        "[CodeWorkspace] Check browser console for Monaco loading errors",
      );
      return; // Silently keep welcome screen, don't show error in terminal
    }

    const container = document.getElementById("monaco-editor");
    if (!container) {
      console.error("[CodeWorkspace] Monaco container not found");
      return;
    }

    // Hide welcome screen
    const welcomeScreen = document.getElementById("welcome-screen");
    if (welcomeScreen) {
      welcomeScreen.style.display = "none";
    }

    // Create Monaco editor with syntax highlighting
    this.editor = monaco.editor.create(container, {
      value: "",
      language: language,
      theme:
        document.documentElement.getAttribute("data-theme") === "dark"
          ? "vs-dark"
          : "vs",
      automaticLayout: true,
      fontSize: 14,
      fontFamily: "'JetBrains Mono', 'Monaco', 'Menlo', monospace",
      minimap: { enabled: true },
      lineNumbers: "on",
      renderWhitespace: "selection",
      scrollBeyondLastLine: false,
      wordWrap: "on",
      tabSize: 4,
      insertSpaces: true,
      // Enable git gutter
      glyphMargin: true,
      // Enable additional features like in writer app
      suggest: {
        showKeywords: true,
        showSnippets: true,
      },
      quickSuggestions: true,
      parameterHints: { enabled: true },
      formatOnPaste: true,
      formatOnType: true,
    });

    console.log("[CodeWorkspace] Monaco editor created successfully");

    // Apply saved keybinding mode or default to Emacs (tooltips updated in setKeybindingMode)
    const savedMode = localStorage.getItem("code-keybinding-mode") || "emacs";
    this.setKeybindingMode(savedMode);
  }

  private setKeybindingMode(mode: string): void {
    if (!this.editor) return;

    const monaco = (window as any).monaco;
    if (!monaco) return;

    // Remove previous Emacs event listener if exists
    if ((this.editor as any)._emacsPreventDefaultHandler) {
      document.removeEventListener(
        "keydown",
        (this.editor as any)._emacsPreventDefaultHandler,
        true,
      );
      (this.editor as any)._emacsPreventDefaultHandler = null;
    }

    // Remove all custom keybindings first
    if ((this.editor as any)._standaloneKeybindingService) {
      (this.editor as any)._standaloneKeybindingService._dynamicKeybindings =
        [];
    }

    if (mode === "vim") {
      // Note: Vim mode requires monaco-vim extension
      console.log(
        "[Keybindings] Vim mode selected (requires monaco-vim extension)",
      );
    } else if (mode === "emacs") {
      // Emacs mode - Add custom keybindings
      console.log("[Keybindings] Emacs mode selected");
      this.addEmacsKeybindings(monaco);
    } else {
      // Default VS Code mode
      console.log("[Keybindings] VS Code mode selected");
    }

    // Update button tooltips to reflect keybinding mode
    this.updateTooltipsForMode(mode);
  }

  private updateTooltipsForMode(mode: string): void {
    const btnSave = document.getElementById("btn-save") as HTMLButtonElement;
    const btnNewFileTab = document.getElementById(
      "btn-new-file-tab",
    ) as HTMLButtonElement;
    const btnDelete = document.getElementById(
      "btn-delete",
    ) as HTMLButtonElement;
    const btnRun = document.getElementById("btn-run") as HTMLButtonElement;

    if (mode === "emacs") {
      // Emacs mode tooltips
      if (btnSave) btnSave.title = "Save (C-x C-s or C-s)";
      if (btnNewFileTab) btnNewFileTab.title = "New file (C-x C-f)";
      if (btnDelete) btnDelete.title = "Delete file";
      if (btnRun) btnRun.title = "Run Python script (Ctrl+Enter)";
    } else if (mode === "vim") {
      // Vim mode tooltips
      if (btnSave) btnSave.title = "Save (:w or Ctrl+S)";
      if (btnNewFileTab) btnNewFileTab.title = "New file (:e filename)";
      if (btnDelete) btnDelete.title = "Delete file (:bd)";
      if (btnRun) btnRun.title = "Run Python script (Ctrl+Enter)";
    } else {
      // VS Code mode tooltips
      if (btnSave) btnSave.title = "Save (Ctrl+S)";
      if (btnNewFileTab) btnNewFileTab.title = "New file (Ctrl+N)";
      if (btnDelete) btnDelete.title = "Delete file";
      if (btnRun) btnRun.title = "Run Python script (Ctrl+Enter)";
    }

    console.log("[Tooltips] Updated for", mode, "mode");
  }

  private addEmacsKeybindings(monaco: any): void {
    if (!this.editor) return;

    // Add global event listener to prevent Chrome shortcuts when editor has focus
    const preventDefaultForEmacs = (e: KeyboardEvent) => {
      // Only prevent if editor has focus or is active
      const activeElement = document.activeElement;
      const isInEditor =
        activeElement?.classList?.contains("inputarea") ||
        activeElement?.closest(".monaco-editor") !== null;

      console.log(
        "[Emacs] Key pressed:",
        e.key,
        "Ctrl:",
        e.ctrlKey,
        "In editor:",
        isInEditor,
      );

      if (!isInEditor) return;

      // List of Ctrl combinations that conflict with Chrome
      if (e.ctrlKey && !e.shiftKey && !e.altKey && !e.metaKey) {
        const key = e.key.toLowerCase();
        // Prevent Chrome shortcuts that conflict with Emacs
        if (["n", "p", "w", "t", "y"].includes(key)) {
          console.log(
            "[Emacs] Preventing default for Ctrl+" + key.toUpperCase(),
          );
          e.preventDefault();
          // Don't use stopPropagation - we need Monaco to receive the event!
        }
      }
    };

    // Add listener at capture phase to intercept before Chrome
    document.addEventListener("keydown", preventDefaultForEmacs, true);

    // Store reference to remove later if needed
    (this.editor as any)._emacsPreventDefaultHandler = preventDefaultForEmacs;

    // Navigation - Character
    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyF, () => {
      console.log("[Emacs] C-f: cursor right");
      this.editor.trigger("keyboard", "cursorRight", {});
    });
    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyB, () => {
      console.log("[Emacs] C-b: cursor left");
      this.editor.trigger("keyboard", "cursorLeft", {});
    });
    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyN, () => {
      console.log("[Emacs] C-n: cursor down");
      this.editor.trigger("keyboard", "cursorDown", {});
    });
    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyP, () => {
      console.log("[Emacs] C-p: cursor up");
      this.editor.trigger("keyboard", "cursorUp", {});
    });

    // Alternative bindings for Chrome-blocked shortcuts (Alt+N, Alt+P as fallback)
    this.editor.addCommand(monaco.KeyMod.Alt | monaco.KeyCode.KeyN, () => {
      console.log("[Emacs] Alt+N (fallback): cursor down");
      this.editor.trigger("keyboard", "cursorDown", {});
    });
    this.editor.addCommand(monaco.KeyMod.Alt | monaco.KeyCode.KeyP, () => {
      console.log("[Emacs] Alt+P (fallback): cursor up");
      this.editor.trigger("keyboard", "cursorUp", {});
    });

    // Navigation - Word
    this.editor.addCommand(monaco.KeyMod.Alt | monaco.KeyCode.KeyF, () => {
      console.log("[Emacs] M-f: forward word");
      this.editor.trigger("keyboard", "cursorWordRight", {});
    });
    this.editor.addCommand(monaco.KeyMod.Alt | monaco.KeyCode.KeyB, () => {
      console.log("[Emacs] M-b: backward word");
      this.editor.trigger("keyboard", "cursorWordLeft", {});
    });

    // Beginning/End of line
    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyA, () => {
      console.log("[Emacs] C-a: line beginning");
      this.editor.trigger("keyboard", "cursorHome", {});
    });
    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyE, () => {
      console.log("[Emacs] C-e: line end");
      this.editor.trigger("keyboard", "cursorEnd", {});
    });

    // Beginning/End of buffer
    this.editor.addCommand(
      monaco.KeyMod.Alt | monaco.KeyMod.Shift | monaco.KeyCode.Comma,
      () => {
        console.log("[Emacs] M-<: buffer beginning");
        this.editor.trigger("keyboard", "cursorTop", {});
      },
    );
    this.editor.addCommand(
      monaco.KeyMod.Alt | monaco.KeyMod.Shift | monaco.KeyCode.Period,
      () => {
        console.log("[Emacs] M->: buffer end");
        this.editor.trigger("keyboard", "cursorBottom", {});
      },
    );

    // Scroll screen
    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyV, () => {
      console.log("[Emacs] C-v: scroll down (page down)");
      this.editor.trigger("keyboard", "cursorPageDown", {});
    });
    this.editor.addCommand(monaco.KeyMod.Alt | monaco.KeyCode.KeyV, () => {
      console.log("[Emacs] M-v: scroll up (page up)");
      this.editor.trigger("keyboard", "cursorPageUp", {});
    });

    // Goto line/char
    this.editor.addCommand(monaco.KeyMod.Alt | monaco.KeyCode.KeyG, () => {
      console.log("[Emacs] M-g: goto prefix");
      // Next key determines action
      // For simplicity, open goto line dialog
      this.editor.trigger("keyboard", "editor.action.gotoLine", {});
    });

    // Delete character
    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyD, () => {
      console.log("[Emacs] C-d: delete forward");
      this.editor.trigger("keyboard", "deleteRight", {});
    });
    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyH, () => {
      console.log("[Emacs] C-h: delete backward");
      this.editor.trigger("keyboard", "deleteLeft", {});
    });

    // Kill word (M-d forward, M-DEL backward)
    this.editor.addCommand(monaco.KeyMod.Alt | monaco.KeyCode.KeyD, () => {
      console.log("[Emacs] M-d: kill word forward");
      this.editor.trigger("keyboard", "deleteWordRight", {});
    });
    this.editor.addCommand(monaco.KeyMod.Alt | monaco.KeyCode.Backspace, () => {
      console.log("[Emacs] M-DEL: kill word backward");
      this.editor.trigger("keyboard", "deleteWordLeft", {});
    });

    // Kill line (delete to end of line and copy to clipboard)
    this.editor.addCommand(
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyK,
      async () => {
        console.log("[Emacs] C-k: kill line");
        const selection = this.editor.getSelection();
        const model = this.editor.getModel();
        if (!model) return;

        const lineNumber = selection.startLineNumber;
        const lineContent = model.getLineContent(lineNumber);
        const startColumn = selection.startColumn;
        const endColumn = lineContent.length + 1;

        // Get text from cursor to end of line
        const killedText = lineContent.substring(startColumn - 1);
        console.log("[Emacs] Killed text:", killedText);

        // Copy to clipboard
        try {
          await navigator.clipboard.writeText(killedText);
          console.log("[Emacs] Copied to clipboard");
        } catch (err) {
          console.error("[Emacs] Failed to copy to clipboard:", err);
        }

        // Delete the text
        const range = new monaco.Range(
          lineNumber,
          startColumn,
          lineNumber,
          endColumn,
        );
        const id = { major: 1, minor: 1 };
        const op = {
          identifier: id,
          range: range,
          text: "",
          forceMoveMarkers: true,
        };
        this.editor.executeEdits("emacs-kill", [op]);
      },
    );

    // Undo/Redo
    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Slash, () => {
      console.log("[Emacs] C-/: undo");
      this.editor.trigger("keyboard", "undo", {});
    });
    this.editor.addCommand(
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.Underline,
      () => {
        console.log("[Emacs] C-_: undo");
        this.editor.trigger("keyboard", "undo", {});
      },
    );
    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyX, () => {
      const nextHandler = async (e: KeyboardEvent) => {
        if (e.key === "u") {
          console.log("[Emacs] C-x u: undo");
          this.editor.trigger("keyboard", "undo", {});
        }
        document.removeEventListener("keydown", nextHandler, true);
      };
      document.addEventListener("keydown", nextHandler, true);
    });

    // Search
    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      // First Ctrl+S - save file (already handled globally)
      // Could be extended to incremental search
      this.saveFile();
    });

    // Mark/Selection (using Ctrl+Space or Ctrl+@)
    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Space, () => {
      console.log("[Emacs] C-SPC: set mark");
      const position = this.editor.getPosition();

      if ((this.editor as any)._emacsMarkActive) {
        // Deactivate mark
        (this.editor as any)._emacsMarkActive = false;
        (this.editor as any)._emacsMarkPosition = null;
      } else {
        // Activate mark and start tracking cursor movements
        (this.editor as any)._emacsMarkPosition = position;
        (this.editor as any)._emacsMarkActive = true;

        // Set up cursor position change listener
        if (!(this.editor as any)._emacsCursorListener) {
          (this.editor as any)._emacsCursorListener =
            this.editor.onDidChangeCursorPosition((e: any) => {
              if (
                (this.editor as any)._emacsMarkActive &&
                (this.editor as any)._emacsMarkPosition
              ) {
                const markPos = (this.editor as any)._emacsMarkPosition;
                const curPos = e.position;

                // Update selection to span from mark to current position
                const selection = new monaco.Selection(
                  markPos.lineNumber,
                  markPos.column,
                  curPos.lineNumber,
                  curPos.column,
                );

                this.editor.setSelection(selection);
                console.log("[Emacs] Selection updated:", markPos, "→", curPos);
              }
            });
        }
      }
    });

    // Query Replace (M-%)
    this.editor.addCommand(
      monaco.KeyMod.Alt | monaco.KeyMod.Shift | monaco.KeyCode.Digit5,
      () => {
        console.log("[Emacs] M-%: query replace (find and replace)");
        this.editor.trigger(
          "keyboard",
          "editor.action.startFindReplaceAction",
          {},
        );
      },
    );

    // Go to line (Ctrl+G in Emacs, but Monaco uses it for other things)
    this.editor.addCommand(
      monaco.KeyMod.CtrlCmd | monaco.KeyMod.Alt | monaco.KeyCode.KeyG,
      () => {
        this.editor.trigger("keyboard", "editor.action.gotoLine", {});
      },
    );

    // Center cursor (Ctrl+L in Emacs)
    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyL, () => {
      this.editor.revealPositionInCenter(this.editor.getPosition());
    });

    // Kill/Copy region (Ctrl+W) - Chrome blocks this, so use M-x instead
    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyW, () => {
      console.log("[Emacs] C-w: kill region (cut) - blocked by Chrome");
      this.editor.trigger("keyboard", "editor.action.clipboardCutAction", {});
    });

    // Kill region (M-x) - Emacs-style cut using Meta/Alt
    this.editor.addCommand(monaco.KeyMod.Alt | monaco.KeyCode.KeyX, () => {
      console.log("[Emacs] M-x: kill region (cut)");
      this.editor.trigger("keyboard", "editor.action.clipboardCutAction", {});
    });

    // Copy region (M-w) - Emacs-style
    this.editor.addCommand(monaco.KeyMod.Alt | monaco.KeyCode.KeyW, () => {
      console.log("[Emacs] M-w: copy region");
      this.editor.trigger("keyboard", "editor.action.clipboardCopyAction", {});
    });

    // Copy region (M-c) - Alternative copy
    this.editor.addCommand(monaco.KeyMod.Alt | monaco.KeyCode.KeyC, () => {
      console.log("[Emacs] M-c: copy region");
      this.editor.trigger("keyboard", "editor.action.clipboardCopyAction", {});
    });

    // M-v is already used for scroll up (page up), removed paste binding

    // Yank/Paste (Ctrl+Y) - Use direct paste action
    this.editor.addCommand(
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyY,
      async () => {
        console.log("[Emacs] C-y: yank (paste) - executing");
        try {
          // Read from clipboard and insert
          const text = await navigator.clipboard.readText();
          console.log("[Emacs] Pasting text:", text.substring(0, 50));
          const selection = this.editor.getSelection();
          const id = { major: 1, minor: 1 };
          const op = {
            identifier: id,
            range: selection,
            text: text,
            forceMoveMarkers: true,
          };
          this.editor.executeEdits("emacs-yank", [op]);
          console.log("[Emacs] Paste completed");
        } catch (err) {
          console.error("[Emacs] Paste failed:", err);
          // Fallback to trigger
          this.editor.trigger("keyboard", "paste", {});
        }
      },
    );

    // C-x prefix - Open command palette or handle C-x sequences
    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyX, () => {
      console.log("[Emacs] C-x: prefix key");

      // Listen for next key
      const nextHandler = async (e: KeyboardEvent) => {
        const key = e.key.toLowerCase();
        console.log("[Emacs] C-x followed by:", key);

        if (e.ctrlKey) {
          // C-x C-... sequences
          if (key === "s") {
            console.log("[Emacs] C-x C-s: save file");
            e.preventDefault();
            if (this.currentFile && this.editor) {
              this.saveFile();
            }
          } else if (key === "f") {
            console.log("[Emacs] C-x C-f: find file");
            e.preventDefault();
            this.createNewFile();
          } else if (key === "u") {
            console.log("[Emacs] C-x C-u: uppercase region");
            e.preventDefault();
            this.editor.trigger(
              "keyboard",
              "editor.action.transformToUppercase",
              {},
            );
          } else if (key === "l") {
            console.log("[Emacs] C-x C-l: lowercase region");
            e.preventDefault();
            this.editor.trigger(
              "keyboard",
              "editor.action.transformToLowercase",
              {},
            );
          } else if (key === "c") {
            console.log("[Emacs] C-x C-c: exit (command palette)");
            e.preventDefault();
            this.editor.trigger("keyboard", "editor.action.quickCommand", {});
          }
        } else {
          // C-x ... sequences
          if (key === "u") {
            console.log("[Emacs] C-x u: undo");
            e.preventDefault();
            this.editor.trigger("keyboard", "undo", {});
          } else if (key === "(") {
            console.log("[Emacs] C-x (: start macro recording");
            e.preventDefault();
            // Monaco doesn't have native macro support
          } else if (key === ")") {
            console.log("[Emacs] C-x ): end macro recording");
            e.preventDefault();
          } else if (key === "e") {
            console.log("[Emacs] C-x e: execute macro");
            e.preventDefault();
          }
        }

        document.removeEventListener("keydown", nextHandler, true);
      };

      document.addEventListener("keydown", nextHandler, true);

      // Clear handler after 2 seconds if no key pressed
      setTimeout(() => {
        document.removeEventListener("keydown", nextHandler, true);
      }, 2000);
    });

    // Open line (Ctrl+O)
    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyO, () => {
      this.editor.trigger("keyboard", "lineBreakInsert", {});
      this.editor.trigger("keyboard", "cursorUp", {});
    });

    // Transpose characters (Ctrl+T)
    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyT, () => {
      const position = this.editor.getPosition();
      const model = this.editor.getModel();
      if (!model) return;

      const lineContent = model.getLineContent(position.lineNumber);
      if (position.column <= 1 || position.column > lineContent.length) return;

      const char1 = lineContent[position.column - 2];
      const char2 = lineContent[position.column - 1];

      const range = new monaco.Range(
        position.lineNumber,
        position.column - 1,
        position.lineNumber,
        position.column + 1,
      );

      this.editor.executeEdits("transpose", [
        {
          range: range,
          text: char2 + char1,
        },
      ]);
    });

    console.log("[Emacs] Keybindings installed");
  }

  private detectLanguage(filePath: string, content?: string): string {
    // First try to detect from shebang if content is provided
    if (content) {
      const firstLine = content.split("\n")[0];
      if (firstLine.startsWith("#!")) {
        const shebang = firstLine.toLowerCase();
        if (shebang.includes("python")) return "python";
        if (shebang.includes("bash") || shebang.includes("/sh")) return "shell";
        if (shebang.includes("node")) return "javascript";
        if (shebang.includes("ruby")) return "ruby";
        if (shebang.includes("perl")) return "perl";
      }
    }

    // Fallback to extension detection
    const ext = filePath.substring(filePath.lastIndexOf("."));
    return this.languageMap[ext] || "plaintext";
  }

  private async loadFile(filePath: string): Promise<void> {
    if (!this.config.currentProject) return;

    // Check if it's a media file (image or PDF)
    const ext = filePath.substring(filePath.lastIndexOf(".")).toLowerCase();
    const isImage = [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"].includes(
      ext,
    );
    const isPDF = ext === ".pdf";

    if (isImage || isPDF) {
      this.showMediaFile(filePath, isImage ? "image" : "pdf");
      return;
    }

    // Show monaco editor and hide media preview when loading code files
    const monacoEditor = document.getElementById("monaco-editor");
    const mediaPreview = document.getElementById("media-preview");
    if (monacoEditor) monacoEditor.style.display = "block";
    if (mediaPreview) mediaPreview.style.display = "none";

    try {
      const response = await fetch(
        `/code/api/file-content/${filePath}?project_id=${this.config.currentProject.id}`,
      );
      const data = await response.json();

      if (!data.success) {
        console.error(`Error loading file: ${data.error}`);
        return;
      }

      // Create Monaco editor if it doesn't exist
      if (!this.editor) {
        const language = this.detectLanguage(filePath);
        await this.createMonacoEditor(language);
      }

      // Detect language from content (shebang) or extension
      const detectedLanguage = this.detectLanguage(filePath, data.content);

      // Store file content
      this.openFiles.set(filePath, {
        path: filePath,
        content: data.content,
        language: detectedLanguage,
      });

      // Update editor content and language
      if (this.editor) {
        const monaco = (window as any).monaco;
        const model = this.editor.getModel();

        if (model) {
          monaco.editor.setModelLanguage(model, detectedLanguage);
          this.editor.setValue(data.content);
        }
      }

      this.currentFile = filePath;
      this.updateTabs();

      // Update toolbar
      const toolbarFilePath = document.getElementById("toolbar-file-path");
      if (toolbarFilePath) {
        toolbarFilePath.textContent = filePath;
      }

      // Enable/disable buttons and update tooltips
      const btnSave = document.getElementById("btn-save") as HTMLButtonElement;
      const btnRun = document.getElementById("btn-run") as HTMLButtonElement;
      const btnDelete = document.getElementById(
        "btn-delete",
      ) as HTMLButtonElement;

      if (btnSave) btnSave.disabled = false;

      // Enable Run button for Python files and update tooltip
      if (btnRun) {
        const isPython =
          filePath.endsWith(".py") ||
          this.detectLanguage(filePath, data.content) === "python";
        btnRun.disabled = !isPython;
        if (isPython) {
          btnRun.title = `Run: python ${filePath} (Ctrl+Enter)`;
        }
      }

      if (btnDelete) btnDelete.disabled = false;

      console.log(`Opened: ${filePath}`);
    } catch (err) {
      console.error("Error loading file:", err);
    }
  }

  private async saveFile(): Promise<void> {
    if (!this.currentFile || !this.config.currentProject || !this.editor)
      return;

    // Don't save *scratch* buffer to server (session-only)
    if (this.currentFile === "*scratch*") {
      console.log("[Scratch] Cannot save - this is a session-only buffer");
      console.warn("[Scratch] Create a new file (+ button) to save your code");
      alert("⚠️ Scratch buffer cannot be saved\n\nThis is a temporary buffer for quick experiments.\nTo save your code:\n1. Click the '+' button to create a new file\n2. Copy your code to the new file\n3. Save it with Ctrl+S");
      return;
    }

    try {
      const content = this.editor.getValue();

      const response = await fetch(`/code/api/save/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.config.csrfToken,
        },
        body: JSON.stringify({
          project_id: this.config.currentProject.id,
          path: this.currentFile,
          content: content,
        }),
      });

      const data = await response.json();
      if (data.success) {
        console.log(`✓ Saved: ${this.currentFile}`);

        // Fetch git status and update UI
        await this.updateGitStatus();

        // Update git decorations for current file
        if (this.currentFile) {
          await this.updateGitDecorations(this.currentFile);
        }
      } else {
        console.error(`✗ Error: ${data.error}`);
      }
    } catch (err) {
      console.error(`✗ Failed to save file`);
    }
  }

  private async updateGitStatus(): Promise<void> {
    if (!this.config.currentProject) return;

    try {
      const response = await fetch(
        `/code/api/git-status/?project_id=${this.config.currentProject.id}`
      );
      const data = await response.json();

      if (data.success) {
        // Update cache
        this.gitStatusCache.clear();
        for (const [path, status] of Object.entries(data.statuses)) {
          this.gitStatusCache.set(path, status as { status: string; staged: boolean });
        }

        // Reload file tree with git status
        await this.loadFileTree();
      }
    } catch (err) {
      console.error("Failed to fetch git status:", err);
    }
  }

  private async updateGitDecorations(filePath: string): Promise<void> {
    if (!this.config.currentProject || !this.editor) return;

    try {
      const response = await fetch(
        `/code/api/file-diff/${filePath}?project_id=${this.config.currentProject.id}`
      );
      const data = await response.json();

      if (data.success) {
        this.applyGitDecorations(data.diffs);
      }
    } catch (err) {
      console.error("Failed to fetch file diff:", err);
    }
  }

  private applyGitDecorations(diffs: Array<{ line: number; status: string }>): void {
    if (!this.editor) return;

    const monaco = (window as any).monaco;
    if (!monaco) return;

    // Clear previous decorations
    this.currentDecorations = this.editor.deltaDecorations(
      this.currentDecorations,
      []
    );

    // Create new decorations
    const newDecorations: any[] = [];

    for (const diff of diffs) {
      let className = 'git-gutter-modified';
      let glyphMarginClassName = 'git-glyph-modified';

      if (diff.status === 'added') {
        className = 'git-gutter-added';
        glyphMarginClassName = 'git-glyph-added';
      } else if (diff.status === 'deleted') {
        className = 'git-gutter-deleted';
        glyphMarginClassName = 'git-glyph-deleted';
      }

      newDecorations.push({
        range: new monaco.Range(diff.line, 1, diff.line, 1),
        options: {
          isWholeLine: true,
          linesDecorationsClassName: className,
          glyphMarginClassName: glyphMarginClassName,
        }
      });
    }

    // Apply new decorations
    this.currentDecorations = this.editor.deltaDecorations(
      [],
      newDecorations
    );

    console.log(`[Git] Applied ${newDecorations.length} decorations`);
  }

  private async showCommitModal(): Promise<void> {
    if (!this.config.currentProject) return;

    const modal = document.getElementById("commit-modal-overlay");
    const filesPreview = document.getElementById("commit-files-preview");
    const messageInput = document.getElementById("commit-message") as HTMLTextAreaElement;
    const submitBtn = document.getElementById("commit-modal-submit");

    if (!modal || !filesPreview || !messageInput || !submitBtn) return;

    // Clear previous state
    messageInput.value = "";

    // Fetch git status to show changed files
    try {
      const response = await fetch(
        `/code/api/git-status/?project_id=${this.config.currentProject.id}`
      );
      const data = await response.json();

      if (data.success) {
        const statuses = data.statuses as { [key: string]: { status: string; staged: boolean } };
        const fileCount = Object.keys(statuses).length;

        if (fileCount === 0) {
          filesPreview.innerHTML = '<div style="color: var(--color-fg-muted); padding: 8px;">No changes to commit</div>';
        } else {
          let html = '<div style="color: var(--color-fg-muted); margin-bottom: 8px;">';
          html += `${fileCount} file${fileCount > 1 ? 's' : ''} changed:</div>`;

          for (const [path, status] of Object.entries(statuses)) {
            const statusColor = {
              'M': '#e2c08d',
              'A': '#73c991',
              'D': '#f14c4c',
              '??': '#73c991'
            }[status.status] || '#858585';

            const statusLabel = {
              'M': 'M',
              'A': 'A',
              'D': 'D',
              '??': 'U'
            }[status.status] || status.status;

            html += `<div style="padding: 4px 0; display: flex; align-items: center; gap: 8px;">`;
            html += `<span style="color: ${statusColor}; font-weight: 600; width: 16px;">${statusLabel}</span>`;
            html += `<span>${path}</span>`;
            html += `</div>`;
          }

          filesPreview.innerHTML = html;
        }
      }
    } catch (err) {
      filesPreview.innerHTML = '<div style="color: var(--color-danger-fg);">Failed to load changes</div>';
    }

    // Show modal
    modal.classList.add("active");

    // Focus message input
    setTimeout(() => messageInput.focus(), 100);

    // Handle submit
    const handleSubmit = async () => {
      const message = messageInput.value.trim();
      const push = (document.getElementById("commit-and-push") as HTMLInputElement).checked;

      if (!message) {
        alert("Please enter a commit message");
        return;
      }

      await this.performCommit(message, push);
      modal.classList.remove("active");
    };

    // Remove previous listeners
    const newSubmitBtn = submitBtn.cloneNode(true) as HTMLElement;
    submitBtn.parentNode?.replaceChild(newSubmitBtn, submitBtn);

    // Add new listener
    newSubmitBtn.addEventListener("click", handleSubmit);

    // Handle Enter in textarea (Ctrl+Enter to submit)
    const handleKeydown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === "Enter") {
        e.preventDefault();
        handleSubmit();
        messageInput.removeEventListener("keydown", handleKeydown);
      }
    };
    messageInput.addEventListener("keydown", handleKeydown);
  }

  private async performCommit(message: string, push: boolean = true): Promise<void> {
    if (!this.config.currentProject) return;

    try {
      console.log(`[Git] Committing with message: ${message}`);
      console.log(`[Git] Push to remote: ${push}`);

      const response = await fetch(`/code/api/git-commit/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.config.csrfToken,
        },
        body: JSON.stringify({
          project_id: this.config.currentProject.id,
          message: message,
          push: push,
        }),
      });

      const data = await response.json();

      if (data.success) {
        console.log(`✓ ${data.message}`);

        // Refresh git status
        await this.updateGitStatus();

        // Clear git decorations (everything is committed)
        this.applyGitDecorations([]);
      } else {
        console.error(`✗ Commit failed: ${data.error}`);
        alert(`Commit failed: ${data.error}`);
      }
    } catch (err) {
      console.error(`✗ Failed to commit:`, err);
      alert(`Failed to commit: ${err}`);
    }
  }

  private async runFile(): Promise<void> {
    if (!this.config.currentProject || !this.editor) return;

    // Check if it's a Python file (by extension or shebang)
    const fileData = this.openFiles.get(this.currentFile || "");
    const isPython =
      this.currentFile?.endsWith(".py") ||
      fileData?.language === "python" ||
      fileData?.content.startsWith("#!/usr/bin/env python") ||
      fileData?.content.startsWith("#!/bin/python");

    if (!isPython) {
      console.warn("Can only run Python files or scripts with Python shebang");
      return;
    }

    const content = this.editor.getValue();
    const fileName = this.currentFile || "*scratch*";

    // If it's a saved file, save it first
    if (this.currentFile && this.currentFile !== "*scratch*") {
      await this.saveFile();
      await new Promise((resolve) => setTimeout(resolve, 300));
    }

    try {
      // Create temp file and run it
      const tempFileName =
        fileName === "*scratch*" ? ".scratch_temp.py" : fileName;

      // Write command to terminal
      if (this.ptyTerminal) {
        this.ptyTerminal.writeln(`\x1b[36m$ python ${tempFileName}\x1b[0m`); // Cyan
      } else {
        console.log(`$ python ${tempFileName}`);
      }

      // First save content to temp file
      if (fileName === "*scratch*") {
        const saveResponse = await fetch(`/code/api/create-file/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": this.config.csrfToken,
          },
          body: JSON.stringify({
            project_id: this.config.currentProject.id,
            path: ".scratch_temp.py",
            content: content,
          }),
        });

        if (!saveResponse.ok) {
          // File might exist, try updating
          await fetch(`/code/api/save/`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": this.config.csrfToken,
            },
            body: JSON.stringify({
              project_id: this.config.currentProject.id,
              path: ".scratch_temp.py",
              content: content,
            }),
          });
        }
      }

      // Execute the file (use temp file for scratch)
      const response = await fetch(`/code/api/execute/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.config.csrfToken,
        },
        body: JSON.stringify({
          project_id: this.config.currentProject.id,
          path: tempFileName,
          args: [],
        }),
      });

      const data = await response.json();

      // Write output to terminal
      if (this.ptyTerminal) {
        if (data.stdout) {
          // Convert \n to \r\n for proper terminal line breaks
          const terminalOutput = data.stdout.replace(/\n/g, '\r\n');
          this.ptyTerminal.write(terminalOutput);
        }

        if (data.stderr) {
          // Convert \n to \r\n for proper terminal line breaks
          const terminalError = data.stderr.replace(/\n/g, '\r\n');
          this.ptyTerminal.write(`\x1b[31m${terminalError}\x1b[0m`); // Red for stderr
        }

        if (data.success) {
          this.ptyTerminal.writeln(`\x1b[32m✓ Exit code: ${data.returncode}\x1b[0m`); // Green
        } else {
          this.ptyTerminal.writeln(`\x1b[31m✗ Exit code: ${data.returncode}\x1b[0m`); // Red
        }
      } else {
        // Fallback to console if terminal not available
        if (data.stdout) {
          console.log(data.stdout);
        }

        if (data.stderr) {
          console.error(data.stderr);
        }

        if (data.success) {
          console.log(`✓ Exit code: ${data.returncode}`);
        } else {
          console.error(`✗ Exit code: ${data.returncode}`);
        }
      }
    } catch (err) {
      if (this.ptyTerminal) {
        this.ptyTerminal.writeln(`\x1b[31m✗ Failed to execute: ${err}\x1b[0m`);
      } else {
        console.error(`✗ Failed to execute: ${err}`);
      }
    }
  }

  private async createNewFile(): Promise<void> {
    if (!this.config.currentProject) return;

    const fileName = await this.showFileModal(
      "New File",
      "File name:",
      "example.py",
    );
    if (!fileName) return;

    const filePath = fileName.trim();

    try {
      const response = await fetch(`/code/api/create-file/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.config.csrfToken,
        },
        body: JSON.stringify({
          project_id: this.config.currentProject.id,
          path: filePath,
          content: "",
        }),
      });

      const data = await response.json();
      if (data.success) {
        console.log(`✓ Created: ${filePath}`);
        // Reload file tree
        await this.loadFileTree();
        // Open the new file
        await this.loadFile(filePath);
      } else {
        console.error(`✗ Error: ${data.error}`);
      }
    } catch (err) {
      console.error(`✗ Failed to create file`);
    }
  }

  private async deleteCurrentFile(): Promise<void> {
    if (!this.currentFile || !this.config.currentProject) return;

    const confirmDelete = confirm(`Delete ${this.currentFile}?`);
    if (!confirmDelete) return;

    try {
      const response = await fetch(`/code/api/delete/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.config.csrfToken,
        },
        body: JSON.stringify({
          project_id: this.config.currentProject.id,
          path: this.currentFile,
        }),
      });

      const data = await response.json();
      if (data.success) {
        console.log(`✓ Deleted: ${this.currentFile}`);

        // Clear editor
        if (this.editor) {
          this.editor.setValue("");
        }

        this.currentFile = null;

        const toolbarFilePath = document.getElementById("toolbar-file-path");
        if (toolbarFilePath) toolbarFilePath.textContent = "No file selected";

        const btnSave = document.getElementById(
          "btn-save",
        ) as HTMLButtonElement;
        const btnRun = document.getElementById("btn-run") as HTMLButtonElement;
        const btnDelete = document.getElementById(
          "btn-delete",
        ) as HTMLButtonElement;

        if (btnSave) btnSave.disabled = true;
        if (btnRun) btnRun.disabled = true;
        if (btnDelete) btnDelete.disabled = true;

        // Reload file tree
        await this.loadFileTree();
      } else {
        console.error(`✗ Error: ${data.error}`);
      }
    } catch (err) {
      console.error(`✗ Failed to delete`);
    }
  }

  private buildFileList(tree: any[], prefix: string = ""): void {
    this.fileList = [];
    const traverse = (items: any[], path: string = "") => {
      items.forEach((item) => {
        const fullPath = path ? `${path}/${item.name}` : item.name;
        this.fileList.push(fullPath);
        if (item.children && item.children.length > 0) {
          traverse(item.children, fullPath);
        }
      });
    };
    traverse(tree);
  }

  private updateTabs(): void {
    const tabsContainer = document.getElementById("file-tabs");
    if (!tabsContainer) return;

    // Clear tabs but keep the + button
    const plusBtn = tabsContainer.querySelector("#btn-new-file-tab");
    tabsContainer.innerHTML = "";

    this.openFiles.forEach((file, path) => {
      const tab = document.createElement("div");
      tab.className = `file-tab ${path === this.currentFile ? "active" : ""}`;
      tab.setAttribute("data-file-path", path);

      // File name
      const fileName = path.split("/").pop() || path;
      tab.innerHTML = `
        <span class="file-tab-name">${fileName}</span>
        <span class="file-tab-close">×</span>
      `;

      // Click tab to switch file
      tab.addEventListener("click", (e) => {
        if (!(e.target as HTMLElement).classList.contains("file-tab-close")) {
          this.switchToFile(path);
        }
      });

      // Close button
      const closeBtn = tab.querySelector(".file-tab-close");
      closeBtn?.addEventListener("click", (e) => {
        e.stopPropagation();
        this.closeTab(path);
      });

      tabsContainer.appendChild(tab);
    });

    // Re-add the + button at the end
    if (plusBtn) {
      tabsContainer.appendChild(plusBtn);
    }
  }

  private showFileModal(
    title: string,
    label: string,
    placeholder: string,
  ): Promise<string | null> {
    return new Promise((resolve) => {
      const overlay = document.getElementById("file-modal-overlay");
      const modalTitle = document.getElementById("file-modal-title");
      const modalLabel = document.getElementById("file-modal-label");
      const input = document.getElementById(
        "file-modal-input",
      ) as HTMLInputElement;
      const submitBtn = document.getElementById("file-modal-submit");

      if (!overlay || !modalTitle || !modalLabel || !input || !submitBtn) {
        console.error("[Modal] Elements not found");
        resolve(null);
        return;
      }

      // Setup modal
      modalTitle.textContent = title;
      modalLabel.textContent = label;
      input.placeholder = placeholder;
      input.value = "";

      // Show modal
      overlay.classList.add("active");

      // Focus with longer delay to ensure modal is rendered
      setTimeout(() => {
        input.focus();
        console.log("[Modal] Input focused");
      }, 200);

      // Handle submit
      const handleSubmit = () => {
        const value = input.value.trim();
        overlay.classList.remove("active");
        resolve(value || null);
      };

      // Enter key
      const handleKeydown = (e: KeyboardEvent) => {
        if (e.key === "Enter") {
          e.preventDefault();
          handleSubmit();
          input.removeEventListener("keydown", handleKeydown);
        } else if (e.key === "Escape") {
          overlay.classList.remove("active");
          resolve(null);
          input.removeEventListener("keydown", handleKeydown);
        }
      };

      input.addEventListener("keydown", handleKeydown);

      // Submit button
      const handleClick = () => {
        handleSubmit();
        submitBtn.removeEventListener("click", handleClick);
      };
      submitBtn.addEventListener("click", handleClick);

      // Close on overlay click
      overlay.addEventListener("click", (e) => {
        if (e.target === overlay) {
          overlay.classList.remove("active");
          resolve(null);
        }
      });
    });
  }

  private async switchToFile(filePath: string): Promise<void> {
    const fileData = this.openFiles.get(filePath);
    if (!fileData || !this.editor) return;

    // Show monaco editor and hide media preview when switching to code files
    const monacoEditor = document.getElementById("monaco-editor");
    const mediaPreview = document.getElementById("media-preview");
    if (monacoEditor) monacoEditor.style.display = "block";
    if (mediaPreview) mediaPreview.style.display = "none";

    // Save current file content before switching
    if (this.currentFile && this.editor) {
      const currentData = this.openFiles.get(this.currentFile);
      if (currentData) {
        currentData.content = this.editor.getValue();
      }
    }

    // For scratch buffer, always regenerate content to reflect current project
    let contentToDisplay = fileData.content;
    if (filePath === "*scratch*") {
      contentToDisplay = this.getDefaultScratchContent();
      fileData.content = contentToDisplay;
      console.log("[Scratch] Regenerated content for current project");
    }

    // Switch to new file
    const monaco = (window as any).monaco;
    const model = this.editor.getModel();

    if (model && monaco) {
      monaco.editor.setModelLanguage(model, fileData.language);
      this.editor.setValue(contentToDisplay);
    }

    this.currentFile = filePath;

    // Update toolbar
    const toolbarFilePath = document.getElementById("toolbar-file-path");
    if (toolbarFilePath) {
      toolbarFilePath.textContent = filePath;
    }

    // Update buttons
    const btnSave = document.getElementById("btn-save") as HTMLButtonElement;
    const btnRun = document.getElementById("btn-run") as HTMLButtonElement;
    const btnDelete = document.getElementById(
      "btn-delete",
    ) as HTMLButtonElement;

    if (btnSave) btnSave.disabled = false;
    if (btnRun) btnRun.disabled = !filePath.endsWith(".py");
    if (btnDelete) btnDelete.disabled = false;

    this.updateTabs();
  }

  private switchToNextTab(): void {
    const tabPaths = Array.from(this.openFiles.keys());
    if (tabPaths.length === 0) return;

    const currentIndex = tabPaths.indexOf(this.currentFile || "");
    const nextIndex = (currentIndex + 1) % tabPaths.length;
    this.switchToFile(tabPaths[nextIndex]);
  }

  private switchToPreviousTab(): void {
    const tabPaths = Array.from(this.openFiles.keys());
    if (tabPaths.length === 0) return;

    const currentIndex = tabPaths.indexOf(this.currentFile || "");
    const prevIndex =
      currentIndex <= 0 ? tabPaths.length - 1 : currentIndex - 1;
    this.switchToFile(tabPaths[prevIndex]);
  }

  private switchToTabByIndex(index: number): void {
    const tabPaths = Array.from(this.openFiles.keys());
    if (index >= 0 && index < tabPaths.length) {
      this.switchToFile(tabPaths[index]);
    }
  }

  private closeTab(filePath: string): void {
    // Don't allow closing the *scratch* buffer (silently ignore)
    if (filePath === "*scratch*") {
      return; // Silently prevent closing
    }

    this.openFiles.delete(filePath);

    // If closing current file, switch to another tab
    if (filePath === this.currentFile) {
      const remainingFiles = Array.from(this.openFiles.keys());
      if (remainingFiles.length > 0) {
        this.switchToFile(remainingFiles[remainingFiles.length - 1]);
      } else {
        // No more files, clear editor
        if (this.editor) {
          this.editor.setValue("");
        }
        this.currentFile = null;

        const toolbarFilePath = document.getElementById("toolbar-file-path");
        if (toolbarFilePath) toolbarFilePath.textContent = "No file selected";

        const btnSave = document.getElementById(
          "btn-save",
        ) as HTMLButtonElement;
        const btnRun = document.getElementById("btn-run") as HTMLButtonElement;
        const btnDelete = document.getElementById(
          "btn-delete",
        ) as HTMLButtonElement;

        if (btnSave) btnSave.disabled = true;
        if (btnRun) btnRun.disabled = true;
        if (btnDelete) btnDelete.disabled = true;
      }
    }

    this.updateTabs();
  }

  private getDefaultScratchContent(): string {
    const username = this.config.currentProject?.owner || "username";
    const projectName = this.config.currentProject?.name || "your-project";
    const projectSlug = this.config.currentProject?.slug || "your-project";

    // Get current host and protocol
    const host = window.location.host; // e.g., "127.0.0.1:8000" or "scitex.cloud"
    const protocol = window.location.protocol; // "http:" or "https:"
    const workspaceUrl = `${protocol}//${host}/code/`;
    const projectUrl = `${protocol}//${host}/${username}/${projectSlug}/`;
    const sshKeysUrl = `${protocol}//${host}/accounts/settings/ssh-keys/`;

    // SSH info - adjust based on environment
    const isDev = host.includes("127.0.0.1") || host.includes("localhost");
    const sshHost = isDev ? "127.0.0.1" : "scitex.cloud";
    const sshPort = isDev ? "2222" : "2222"; // Adjust production port if different

    return `#!/usr/bin/env python3
# SciTeX Code Workspace
#
# Project: ${projectName}
# User:    ${username}
#
# URLs:
#   Workspace:  ${workspaceUrl}
#   Project:    ${projectUrl}
#   SSH Keys:   ${sshKeysUrl}
#
# SSH Access:
#   1. Add SSH key: ${sshKeysUrl}
#   2. Connect:     ssh -p ${sshPort} ${username}@${sshHost}
#
# Keyboard Shortcuts:
#   Ctrl+S         Save file
#   Ctrl+Enter     Run Python file
#   ⌨ button       Show all shortcuts
#   Ctrl+Shift+R   Reset this buffer
#
# Paths:
#   Your config:   /home/${username}/
#   Your project:  /home/${username}/proj/${projectSlug}/
#
# Editor Mode: Emacs | Vim | VS Code (toolbar dropdown)

def hello():
    """Example function"""
    print("Hello from SciTeX!")
    print(f"Project: ${projectName}")
    print(f"User: ${username}")
    print(f"SSH: ssh -p ${sshPort} ${username}@${sshHost}")

if __name__ == "__main__":
    hello()
      `;
  }

  private resetScratchBuffer(): void {
    if (this.currentFile !== "*scratch*" || !this.editor) return;

    const scratchContent = this.getDefaultScratchContent();
    this.editor.setValue(scratchContent);

    // Update in-memory content
    const scratchData = this.openFiles.get("*scratch*");
    if (scratchData) {
      scratchData.content = scratchContent;
    }

    console.log("[Scratch] Buffer reset to default (Ctrl+Shift+R)");
  }

  private async initScratchBuffer(): Promise<void> {
    // Create Monaco editor with scratch buffer content
    await this.createMonacoEditor("python");

    if (!this.editor) return;

    // Ensure monaco editor is visible and media preview is hidden
    const monacoEditor = document.getElementById("monaco-editor");
    const mediaPreview = document.getElementById("media-preview");
    if (monacoEditor) monacoEditor.style.display = "block";
    if (mediaPreview) mediaPreview.style.display = "none";

    // Get default scratch content (session-based, not persistent)
    const scratchContent = this.getDefaultScratchContent();

    this.editor.setValue(scratchContent);

    // Add scratch buffer to open files
    this.currentFile = "*scratch*";
    this.openFiles.set("*scratch*", {
      path: "*scratch*",
      content: scratchContent,
      language: "python",
    });

    const toolbarFilePath = document.getElementById("toolbar-file-path");
    if (toolbarFilePath) {
      toolbarFilePath.textContent = "*scratch*";
    }

    // Enable Run button for scratch (it's Python) with command hint
    const btnRun = document.getElementById("btn-run") as HTMLButtonElement;
    if (btnRun) {
      btnRun.disabled = false;
      btnRun.title = "Run: python .scratch_temp.py (Ctrl+Enter)";
    }

    // Update tabs to show the scratch tab
    this.updateTabs();
  }

  private initContextMenu(): void {
    const fileTree = document.getElementById("file-tree");
    const contextMenu = document.getElementById("context-menu");

    if (!fileTree || !contextMenu) return;

    let contextTarget: string | null = null;

    // Right-click on file tree items
    fileTree.addEventListener("contextmenu", (e) => {
      e.preventDefault();

      const target = (e.target as HTMLElement).closest(
        ".file-tree-item, .file-tree-file",
      );
      if (!target) return;

      // Get file path
      const fileElement = target.querySelector(".file-tree-file");
      contextTarget = fileElement?.getAttribute("data-file-path") || null;

      // Show context menu at cursor position
      contextMenu.style.display = "block";
      contextMenu.style.left = `${e.pageX}px`;
      contextMenu.style.top = `${e.pageY}px`;
    });

    // Handle context menu actions
    contextMenu.addEventListener("click", async (e) => {
      const item = (e.target as HTMLElement).closest(".context-menu-item");
      if (!item) return;

      const action = item.getAttribute("data-action");
      contextMenu.style.display = "none";

      switch (action) {
        case "new-file":
          await this.createNewFile();
          break;
        case "new-folder":
          await this.createNewFolder();
          break;
        case "rename":
          if (contextTarget) await this.renameFile(contextTarget);
          break;
        case "delete":
          if (contextTarget) await this.deleteFile(contextTarget);
          break;
      }
    });

    // Close context menu on click outside
    document.addEventListener("click", () => {
      contextMenu.style.display = "none";
    });

    // Close on Escape
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        contextMenu.style.display = "none";
      }
    });
  }

  private async createNewFolder(): Promise<void> {
    const folderName = await this.showFileModal(
      "New Folder",
      "Folder name:",
      "my-folder",
    );
    if (!folderName) return;

    // Create folder via terminal command
    console.log(`$ mkdir -p ${folderName}`);

    try {
      const response = await fetch(`/code/api/command/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.config.csrfToken,
        },
        body: JSON.stringify({
          project_id: this.config.currentProject?.id,
          command: `mkdir -p ${folderName}`,
        }),
      });

      const data = await response.json();
      if (data.success) {
        console.log(`✓ Created folder: ${folderName}`);
        await this.loadFileTree();
      } else {
        console.error(`✗ Error: ${data.error}`);
      }
    } catch (err) {
      console.error(`✗ Failed to create folder`);
    }
  }

  // Create file within a specific folder
  private async createFileInFolder(folderPath: string): Promise<void> {
    if (!this.config.currentProject) return;

    const fileName = await this.showFileModal(
      "New File",
      "File name:",
      "example.py",
    );
    if (!fileName) return;

    // Combine folder path with file name
    const filePath = folderPath
      ? `${folderPath}/${fileName.trim()}`
      : fileName.trim();

    try {
      const response = await fetch(`/code/api/create-file/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.config.csrfToken,
        },
        body: JSON.stringify({
          project_id: this.config.currentProject.id,
          path: filePath,
          content: "",
        }),
      });

      const data = await response.json();
      if (data.success) {
        console.log(`✓ Created: ${filePath}`);
        await this.loadFileTree();
        await this.loadFile(filePath);
      } else {
        console.error(`✗ Error: ${data.error}`);
      }
    } catch (err) {
      console.error(`✗ Failed to create file`);
    }
  }

  // Create folder within a specific folder
  private async createFolderInFolder(folderPath: string): Promise<void> {
    const folderName = await this.showFileModal(
      "New Folder",
      "Folder name:",
      "my-folder",
    );
    if (!folderName) return;

    // Combine parent folder path with new folder name
    const fullPath = folderPath
      ? `${folderPath}/${folderName.trim()}`
      : folderName.trim();

    console.log(`$ mkdir -p ${fullPath}`);

    try {
      const response = await fetch(`/code/api/command/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.config.csrfToken,
        },
        body: JSON.stringify({
          project_id: this.config.currentProject?.id,
          command: `mkdir -p "${fullPath}"`,
        }),
      });

      const data = await response.json();
      if (data.success) {
        console.log(`✓ Created folder: ${fullPath}`);
        await this.loadFileTree();
      } else {
        console.error(`✗ Error: ${data.error}`);
      }
    } catch (err) {
      console.error(`✗ Failed to create folder`);
    }
  }

  private async renameFile(oldPath: string): Promise<void> {
    const newName = await this.showFileModal("Rename", "New name:", oldPath);
    if (!newName || newName === oldPath) return;

    console.log(`$ mv ${oldPath} ${newName}`);

    try {
      const response = await fetch(`/code/api/command/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.config.csrfToken,
        },
        body: JSON.stringify({
          project_id: this.config.currentProject?.id,
          command: `mv "${oldPath}" "${newName}"`,
        }),
      });

      const data = await response.json();
      if (data.success) {
        console.log(`✓ Renamed: ${oldPath} → ${newName}`);
        await this.loadFileTree();
      } else {
        console.error(`✗ Error: ${data.error}`);
      }
    } catch (err) {
      console.error(`✗ Failed to rename`);
    }
  }

  private async deleteFile(filePath: string): Promise<void> {
    const confirmDelete = confirm(`Delete ${filePath}?`);
    if (!confirmDelete) return;

    try {
      const response = await fetch(`/code/api/delete/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.config.csrfToken,
        },
        body: JSON.stringify({
          project_id: this.config.currentProject?.id,
          path: filePath,
        }),
      });

      const data = await response.json();
      if (data.success) {
        console.log(`✓ Deleted: ${filePath}`);

        // Close tab if open
        if (this.openFiles.has(filePath)) {
          this.closeTab(filePath);
        }

        await this.loadFileTree();
      } else {
        console.error(`✗ Error: ${data.error}`);
      }
    } catch (err) {
      console.error(`✗ Failed to delete`);
    }
  }

  private showMediaFile(filePath: string, type: "image" | "pdf"): void {
    const editorContainer = document.getElementById("editor-container");
    const welcomeScreen = document.getElementById("welcome-screen");
    const monacoEditor = document.getElementById("monaco-editor");

    if (!editorContainer) return;

    // Hide Monaco and welcome screen
    if (welcomeScreen) welcomeScreen.style.display = "none";
    if (monacoEditor) monacoEditor.style.display = "none";

    // Create or update media preview
    let mediaPreview = document.getElementById("media-preview");
    if (!mediaPreview) {
      mediaPreview = document.createElement("div");
      mediaPreview.id = "media-preview";
      mediaPreview.style.cssText = `
        width: 100%;
        height: 100%;
        overflow: auto;
        padding: 20px;
        background: var(--color-canvas-default);
        display: flex;
        align-items: center;
        justify-content: center;
      `;
      editorContainer.appendChild(mediaPreview);
    }

    mediaPreview.style.display = "flex";

    const fileUrl = `/${this.config.currentProject?.owner}/${this.config.currentProject?.slug}/raw/${filePath}`;

    if (type === "image") {
      mediaPreview.innerHTML = `
        <img src="${fileUrl}"
             alt="${filePath}"
             style="max-width: 100%; max-height: 100%; object-fit: contain;" />
      `;
    } else if (type === "pdf") {
      mediaPreview.innerHTML = `
        <iframe src="${fileUrl}"
                style="width: 100%; height: 100%; border: none;"></iframe>
      `;
    }

    this.currentFile = filePath;
    console.log(`Opened media file: ${filePath}`);

    // Update toolbar
    const toolbarFilePath = document.getElementById("toolbar-file-path");
    if (toolbarFilePath) {
      toolbarFilePath.textContent = filePath;
    }
  }
}

// Store workspace instance globally
let workspaceInstance: CodeWorkspace | null = null;

// Initialize workspace
function initWorkspace() {
  // Get config from template
  const configElement = document.getElementById("workspace-config");
  if (!configElement) {
    console.error("[CodeWorkspace] Config element not found");
    return;
  }

  const config: EditorConfig = JSON.parse(configElement.textContent || "{}");
  workspaceInstance = new CodeWorkspace(config);
}

// Initialize when DOM is ready (or immediately if already loaded)
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initWorkspace);
} else {
  // DOM already loaded (module script loaded dynamically)
  initWorkspace();
}

// Global functions for folder actions (called from HTML)
(window as any).createFileInFolder = async (folderPath: string) => {
  if (!workspaceInstance) {
    console.error("[CodeWorkspace] Instance not initialized");
    return;
  }
  await (workspaceInstance as any).createFileInFolder(folderPath);
};

(window as any).createFolderInFolder = async (folderPath: string) => {
  if (!workspaceInstance) {
    console.error("[CodeWorkspace] Instance not initialized");
    return;
  }
  await (workspaceInstance as any).createFolderInFolder(folderPath);
};
