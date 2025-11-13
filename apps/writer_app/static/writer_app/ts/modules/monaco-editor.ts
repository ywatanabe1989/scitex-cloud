/**
 * Monaco Editor Module
 * Enhanced editor with Monaco Editor capabilities
 * Falls back to CodeMirror if Monaco is not available
 */

import { StorageManager } from "@/utils/storage";
import { HistoryEntry } from "@/types";
import { SpellChecker, injectSpellCheckStyles } from "./spell-checker.js";

console.log(
  "[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/modules/monaco-editor.ts loaded",
);
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
  private editorType: "monaco" | "codemirror" = "codemirror";
  private storage: StorageManager;
  private history: HistoryEntry[] = [];
  private historyIndex: number = -1;
  private maxHistorySize: number = 50;
  private onChangeCallback?: (content: string, wordCount: number) => void;
  private monacoEditor?: any;
  private currentSectionId: string = "";
  private spellChecker?: SpellChecker;

  constructor(config: MonacoEditorConfig) {
    this.storage = new StorageManager("writer_editor_");

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
      console.warn("[Editor] Element not found, falling back to CodeMirror");
      this.initializeCodeMirror(config);
      return;
    }

    // Wait for Monaco to be available
    const waitForMonaco = (): void => {
      if (!(window as any).monaco) {
        console.log("[Editor] Waiting for Monaco to load...");
        setTimeout(() => waitForMonaco(), 100);
        return;
      }

      try {
        const monaco = (window as any).monaco;

        // Register LaTeX language if not already registered
        console.log(
          "[Monaco] Available languages:",
          monaco.languages.getLanguages().map((l: any) => l.id),
        );
        const latexExists = monaco.languages
          .getLanguages()
          .find((l: any) => l.id === "latex");
        console.log("[Monaco] LaTeX language exists:", !!latexExists);

        if (!latexExists) {
          console.log("[Monaco] Registering LaTeX language...");
          monaco.languages.register({ id: "latex" });

          // Define LaTeX language configuration
          monaco.languages.setLanguageConfiguration("latex", {
            comments: {
              lineComment: "%",
            },
            brackets: [
              ["{", "}"],
              ["[", "]"],
              ["(", ")"],
              ["\\begin{", "\\end{"], // Treat LaTeX environments as bracket pairs!
            ],
            autoClosingPairs: [
              { open: "{", close: "}" },
              { open: "[", close: "]" },
              { open: "(", close: ")" },
              { open: "$", close: "$" },
              { open: "`", close: "'" },
              { open: "\\begin{", close: "}", notIn: ["string", "comment"] },
            ],
            surroundingPairs: [
              { open: "{", close: "}" },
              { open: "[", close: "]" },
              { open: "(", close: ")" },
              { open: "$", close: "$" },
            ],
          });

          // Define LaTeX syntax highlighting
          monaco.languages.setMonarchTokensProvider("latex", {
            tokenizer: {
              root: [
                [/%.*$/, "comment"],
                [/\\[a-zA-Z@]+/, "keyword"],
                [/\{/, "delimiter.curly"],
                [/\}/, "delimiter.curly"],
                [/\[/, "delimiter.square"],
                [/\]/, "delimiter.square"],
                [/\$\$/, "string"],
                [/\$/, "string"],
              ],
            },
          });

          // Register completion provider for LaTeX commands
          console.log("[Monaco] Registering LaTeX completion provider...");
          monaco.languages.registerCompletionItemProvider("latex", {
            triggerCharacters: ["\\"],
            provideCompletionItems: (model: any, position: any) => {
              console.log(
                "[Monaco] Completion requested at position:",
                position,
              );
              const word = model.getWordUntilPosition(position);
              console.log("[Monaco] Word at position:", word);
              const range = {
                startLineNumber: position.lineNumber,
                endLineNumber: position.lineNumber,
                startColumn: word.startColumn,
                endColumn: word.endColumn,
              };

              const suggestions = [
                // Document structure
                {
                  label: "\\documentclass",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText: "\\documentclass{article}",
                  documentation: "Document class",
                },
                {
                  label: "\\begin",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText:
                    "\\begin{${1:environment}}\n\t$0\n\\end{${1:environment}}",
                  insertTextRules:
                    monaco.languages.CompletionItemInsertTextRule
                      .InsertAsSnippet,
                  documentation: "Begin environment",
                },
                {
                  label: "\\end",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText: "\\end{${1:environment}}",
                  insertTextRules:
                    monaco.languages.CompletionItemInsertTextRule
                      .InsertAsSnippet,
                  documentation: "End environment",
                },
                {
                  label: "\\section",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText: "\\section{$0}",
                  insertTextRules:
                    monaco.languages.CompletionItemInsertTextRule
                      .InsertAsSnippet,
                  documentation: "Section",
                },
                {
                  label: "\\subsection",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText: "\\subsection{$0}",
                  insertTextRules:
                    monaco.languages.CompletionItemInsertTextRule
                      .InsertAsSnippet,
                  documentation: "Subsection",
                },
                {
                  label: "\\subsubsection",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText: "\\subsubsection{$0}",
                  insertTextRules:
                    monaco.languages.CompletionItemInsertTextRule
                      .InsertAsSnippet,
                  documentation: "Subsubsection",
                },

                // Text formatting
                {
                  label: "\\textbf",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText: "\\textbf{$0}",
                  insertTextRules:
                    monaco.languages.CompletionItemInsertTextRule
                      .InsertAsSnippet,
                  documentation: "Bold text",
                },
                {
                  label: "\\textit",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText: "\\textit{$0}",
                  insertTextRules:
                    monaco.languages.CompletionItemInsertTextRule
                      .InsertAsSnippet,
                  documentation: "Italic text",
                },
                {
                  label: "\\emph",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText: "\\emph{$0}",
                  insertTextRules:
                    monaco.languages.CompletionItemInsertTextRule
                      .InsertAsSnippet,
                  documentation: "Emphasized text",
                },
                {
                  label: "\\texttt",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText: "\\texttt{$0}",
                  insertTextRules:
                    monaco.languages.CompletionItemInsertTextRule
                      .InsertAsSnippet,
                  documentation: "Typewriter text",
                },

                // Math mode
                {
                  label: "\\[",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText: "\\[\n\t$0\n\\]",
                  insertTextRules:
                    monaco.languages.CompletionItemInsertTextRule
                      .InsertAsSnippet,
                  documentation: "Display math",
                },
                {
                  label: "\\(",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText: "\\($0\\)",
                  insertTextRules:
                    monaco.languages.CompletionItemInsertTextRule
                      .InsertAsSnippet,
                  documentation: "Inline math",
                },
                {
                  label: "\\equation",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText: "\\begin{equation}\n\t$0\n\\end{equation}",
                  insertTextRules:
                    monaco.languages.CompletionItemInsertTextRule
                      .InsertAsSnippet,
                  documentation: "Equation environment",
                },

                // Figures and tables
                {
                  label: "\\figure",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText:
                    "\\begin{figure}[htbp]\n\t\\centering\n\t\\includegraphics[width=0.8\\textwidth]{$1}\n\t\\caption{$2}\n\t\\label{fig:$3}\n\\end{figure}",
                  insertTextRules:
                    monaco.languages.CompletionItemInsertTextRule
                      .InsertAsSnippet,
                  documentation: "Figure environment",
                },
                {
                  label: "\\table",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText:
                    "\\begin{table}[htbp]\n\t\\centering\n\t\\caption{$1}\n\t\\label{tab:$2}\n\t\\begin{tabular}{$3}\n\t\t$0\n\t\\end{tabular}\n\\end{table}",
                  insertTextRules:
                    monaco.languages.CompletionItemInsertTextRule
                      .InsertAsSnippet,
                  documentation: "Table environment",
                },

                // Citations and references
                {
                  label: "\\cite",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText: "\\cite{$0}",
                  insertTextRules:
                    monaco.languages.CompletionItemInsertTextRule
                      .InsertAsSnippet,
                  documentation: "Citation",
                },
                {
                  label: "\\ref",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText: "\\ref{$0}",
                  insertTextRules:
                    monaco.languages.CompletionItemInsertTextRule
                      .InsertAsSnippet,
                  documentation: "Reference",
                },
                {
                  label: "\\label",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText: "\\label{$0}",
                  insertTextRules:
                    monaco.languages.CompletionItemInsertTextRule
                      .InsertAsSnippet,
                  documentation: "Label",
                },

                // Lists
                {
                  label: "\\itemize",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText: "\\begin{itemize}\n\t\\item $0\n\\end{itemize}",
                  insertTextRules:
                    monaco.languages.CompletionItemInsertTextRule
                      .InsertAsSnippet,
                  documentation: "Itemize list",
                },
                {
                  label: "\\enumerate",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText:
                    "\\begin{enumerate}\n\t\\item $0\n\\end{enumerate}",
                  insertTextRules:
                    monaco.languages.CompletionItemInsertTextRule
                      .InsertAsSnippet,
                  documentation: "Enumerate list",
                },
                {
                  label: "\\item",
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText: "\\item $0",
                  insertTextRules:
                    monaco.languages.CompletionItemInsertTextRule
                      .InsertAsSnippet,
                  documentation: "List item",
                },
              ];

              const completions = suggestions.map((s: any) => ({
                ...s,
                range,
              }));
              console.log(
                "[Monaco] Returning",
                completions.length,
                "completions",
              );
              return { suggestions: completions };
            },
          });
          console.log(
            "[Monaco] LaTeX completion provider registered successfully",
          );

          // ============================================================
          // CITATION AUTOCOMPLETE: Register completion provider for \cite{} commands
          // ============================================================
          console.log("[Citations] ========================================");
          console.log("[Citations] STARTING CITATION COMPLETION REGISTRATION");
          console.log("[Citations] ========================================");

          // Get project ID from URL or global variable
          const getProjectId = (): string | null => {
            // Try WRITER_CONFIG first (most reliable)
            const writerConfig = (window as any).WRITER_CONFIG;
            if (writerConfig?.projectId) {
              console.log(
                "[Citations] Found project ID from WRITER_CONFIG:",
                writerConfig.projectId,
              );
              return String(writerConfig.projectId);
            }

            // Try URL pattern: /writer/project/{id}/
            const match = window.location.pathname.match(
              /\/writer\/project\/(\d+)\//,
            );
            if (match) {
              console.log("[Citations] Found project ID from URL:", match[1]);
              return match[1];
            }

            // Try global variable
            if ((window as any).SCITEX_PROJECT_ID) {
              console.log(
                "[Citations] Found project ID from global:",
                (window as any).SCITEX_PROJECT_ID,
              );
              return String((window as any).SCITEX_PROJECT_ID);
            }

            console.warn(
              "[Citations] No project ID found - checked WRITER_CONFIG, URL, and global",
            );
            return null;
          };

          // Cache for citations
          let citationsCache: any[] | null = null;
          let lastFetchTime = 0;
          const CACHE_DURATION = 60000; // 1 minute

          // Fetch citations from API
          const fetchCitations = async (): Promise<any[]> => {
            const projectId = getProjectId();
            if (!projectId) {
              console.warn(
                "[Citations] No project ID - cannot fetch citations",
              );
              return [];
            }

            const now = Date.now();
            if (citationsCache && now - lastFetchTime < CACHE_DURATION) {
              console.log(
                `[Citations] Using cached citations (${citationsCache.length} entries)`,
              );
              return citationsCache;
            }

            try {
              const apiUrl = `/writer/api/project/${projectId}/citations/`;
              console.log("[Citations] Fetching from API:", apiUrl);
              const response = await fetch(apiUrl);
              console.log("[Citations] API response status:", response.status);

              if (!response.ok) {
                console.error(
                  "[Citations] API error:",
                  response.status,
                  response.statusText,
                );
                return [];
              }

              const data = await response.json();
              console.log("[Citations] API response:", data);

              if (data.success && data.citations) {
                citationsCache = data.citations;
                lastFetchTime = now;
                console.log(
                  `[Citations] ✓ Loaded ${data.citations.length} citations`,
                );
                return data.citations;
              }
              console.warn(
                "[Citations] No citations in response:",
                data.message,
              );
              return [];
            } catch (error) {
              console.error("[Citations] Error fetching:", error);
              return [];
            }
          };

          // Register citation completion provider
          monaco.languages.registerCompletionItemProvider("latex", {
            triggerCharacters: ["{", "\\"], // Trigger on { or \ for better UX
            provideCompletionItems: async (model: any, position: any) => {
              const lineContent = model.getLineContent(position.lineNumber);
              const beforeCursor = lineContent.substring(
                0,
                position.column - 1,
              );

              console.log("[Citations] Triggered at:", beforeCursor.slice(-20));

              // Check for \cite or \cite{ context (with or without {)
              // Matches: \cite, \citep, \citet, \cite{, \citep{, \citet{
              const citeMatch = beforeCursor.match(/\\cite([tp])?\{?([^}]*)$/);
              if (!citeMatch) {
                return { suggestions: [] };
              }

              console.log("[Citations] In \\cite context!");

              const citations = await fetchCitations();
              if (citations.length === 0) {
                console.warn(
                  "[Citations] No citations available - showing guideline",
                );
                // Show helpful guideline when no citations found
                return {
                  suggestions: [
                    {
                      label: "📚 No citations available yet",
                      kind: monaco.languages.CompletionItemKind.Text,
                      detail:
                        "Upload BibTeX files to enable citation autocomplete",
                      documentation: {
                        value:
                          "To add citations:\n\n" +
                          "1. Go to Scholar app (/scholar/bibtex/)\n" +
                          "2. Upload your .bib file\n" +
                          "3. Save to this project\n" +
                          "4. Citations will appear here automatically\n\n" +
                          "Or manually add .bib files to:\n" +
                          "• scitex/scholar/bib_files/\n" +
                          "• scitex/writer/bib_files/",
                        isTrusted: true,
                        supportHtml: false,
                      },
                      insertText: "",
                      range: {
                        startLineNumber: position.lineNumber,
                        startColumn: position.column,
                        endLineNumber: position.lineNumber,
                        endColumn: position.column,
                      },
                    },
                  ],
                };
              }

              const currentWord = citeMatch[2] || ""; // Changed from citeMatch[1] to citeMatch[2] due to new regex groups

              // Fuzzy search across multiple fields
              const suggestions = citations
                .filter((cite: any) => {
                  if (!currentWord) return true;
                  const searchTerm = currentWord.toLowerCase();

                  // Search in citation key
                  if (cite.key.toLowerCase().includes(searchTerm)) return true;

                  // Search in title
                  if (
                    cite.title &&
                    cite.title.toLowerCase().includes(searchTerm)
                  )
                    return true;

                  // Search in authors
                  if (cite.authors && Array.isArray(cite.authors)) {
                    if (
                      cite.authors.some((author: string) =>
                        author.toLowerCase().includes(searchTerm),
                      )
                    )
                      return true;
                  }

                  // Search in journal
                  if (
                    cite.journal &&
                    cite.journal.toLowerCase().includes(searchTerm)
                  )
                    return true;

                  // Search in abstract
                  if (
                    cite.abstract &&
                    cite.abstract.toLowerCase().includes(searchTerm)
                  )
                    return true;

                  return false;
                })
                .map((cite: any) => {
                  // Create MULTI-LINE detail showing all metadata on separate lines
                  let detailLines = [];

                  // Line 1: Author and Year
                  if (cite.detail) {
                    detailLines.push(cite.detail);
                  }

                  // Line 2: Title (truncated to 100 chars)
                  if (cite.title) {
                    const titlePreview =
                      cite.title.length > 100
                        ? cite.title.substring(0, 100) + "..."
                        : cite.title;
                    detailLines.push(`📄 ${titlePreview}`);
                  }

                  // Line 3: Journal with IF and Citation Count
                  let metricsLine = [];
                  if (cite.journal) {
                    let journalPart = cite.journal;
                    if (cite.impact_factor) {
                      journalPart += ` (IF: ${cite.impact_factor})`;
                    }
                    metricsLine.push(`📖 ${journalPart}`);
                  }
                  if (cite.citation_count && cite.citation_count > 0) {
                    metricsLine.push(`📊 ${cite.citation_count} citations`);
                  }
                  if (metricsLine.length > 0) {
                    detailLines.push(metricsLine.join("  •  "));
                  }

                  // Combine all lines with newlines for multi-line display
                  const detailLine = detailLines.join("\n");

                  // Sort by citation count (higher first), then alphabetically
                  const sortPrefix = String(
                    1000000 - (cite.citation_count || 0),
                  ).padStart(7, "0");

                  // Build completion item with rich inline metadata
                  const completionItem: any = {
                    label: cite.key,
                    kind: monaco.languages.CompletionItemKind.Reference,
                    detail: detailLine, // All metadata visible inline
                    documentation: {
                      value: cite.documentation || "",
                      isTrusted: false,
                      supportHtml: false,
                    },
                    insertText: beforeCursor.endsWith("{")
                      ? cite.key + "}"
                      : `{${cite.key}}`, // Smart brace handling
                    sortText: sortPrefix + cite.key,
                    filterText: `${cite.key} ${cite.title || ""} ${cite.journal || ""} ${(cite.authors || []).join(" ")}`,
                    range: {
                      startLineNumber: position.lineNumber,
                      startColumn: position.column - currentWord.length,
                      endLineNumber: position.lineNumber,
                      endColumn: position.column,
                    },
                  };

                  // Add command to show additional info on hover
                  completionItem.additionalTextEdits = [];

                  return completionItem;
                });

              console.log(
                `[Citations] Returning ${suggestions.length} suggestions`,
              );
              return { suggestions };
            },
          });

          console.log("[Citations] Citation completion provider registered");

          // ============================================================
          // FORCE DETAILS PANEL TO RIGHT SIDE WITH JAVASCRIPT
          // ============================================================
          // Override Monaco's suggest controller to always show details to the right
          setTimeout(() => {
            const suggestController = (this.monacoEditor as any)._contentWidget
              ?._widget;
            if (suggestController && suggestController.widget) {
              // Force detail panel to always show
              suggestController.widget._setDetailsVisible(true);
            }
          }, 1000);

          // Watch for suggestion widget creation and force positioning + auto-expand
          const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
              mutation.addedNodes.forEach((node: any) => {
                if (
                  node.classList &&
                  node.classList.contains("suggest-widget")
                ) {
                  console.log(
                    "[Citations] Suggestion widget detected, forcing right-side layout and auto-expanding details",
                  );

                  // Force horizontal layout
                  node.style.flexDirection = "row";
                  node.style.alignItems = "flex-start";

                  // Find and reposition details panel
                  const details = node.querySelector(".suggest-details");
                  if (details) {
                    (details as HTMLElement).style.position = "relative";
                    (details as HTMLElement).style.order = "2";
                    (details as HTMLElement).style.marginLeft = "4px";
                    (details as HTMLElement).style.display = "block";
                    (details as HTMLElement).style.visibility = "visible";
                  }

                  // Programmatically trigger "show more" mode
                  // Simulate Ctrl+Space to expand details automatically
                  setTimeout(() => {
                    try {
                      // Try to access Monaco's suggest controller
                      const editor = this.monacoEditor;
                      if (editor) {
                        // Trigger suggest widget to show details
                        editor.trigger(
                          "keyboard",
                          "toggleSuggestionDetails",
                          {},
                        );
                      }
                    } catch (e) {
                      console.log(
                        "[Citations] Could not auto-trigger details:",
                        e,
                      );
                    }
                  }, 50);
                }
              });
            });
          });

          observer.observe(document.body, {
            childList: true,
            subtree: true,
          });

          // ============================================================
          // HOVER PROVIDER: Show rich citation info when hovering over \cite{key}
          // ============================================================
          console.log("[Citations] Registering hover provider...");

          monaco.languages.registerHoverProvider("latex", {
            provideHover: async (model: any, position: any) => {
              const lineContent = model.getLineContent(position.lineNumber);
              const word = model.getWordAtPosition(position);

              if (!word) return null;

              // Check if we're hovering over a citation key inside \cite{}
              const beforeWord = lineContent.substring(0, position.column - 1);
              const afterWord = lineContent.substring(position.column - 1);

              // Match: \cite{WORD} or \citep{WORD} or \citet{WORD}
              const beforeMatch = beforeWord.match(/\\cite[tp]?\{([^}]*)$/);
              const afterMatch = afterWord.match(/^([^}]*)\}/);

              if (!beforeMatch && !afterMatch) return null;

              // Get the citation key under cursor
              const citationKey = word.word;
              console.log(
                "[Citations] Hovering over citation key:",
                citationKey,
              );

              // Fetch citations and find matching key
              const citations = await fetchCitations();
              const citation = citations.find(
                (c: any) => c.key === citationKey,
              );

              if (!citation) {
                console.log(
                  "[Citations] Key not found in bibliography:",
                  citationKey,
                );
                return null;
              }

              console.log(
                "[Citations] Found citation for hover:",
                citation.key,
              );

              // Return rich hover content
              return {
                contents: [
                  { value: `**${citation.key}**` },
                  { value: citation.documentation || "" },
                ],
              };
            },
          });

          console.log("[Citations] Hover provider registered");
        } else {
          console.log("[Monaco] LaTeX language already registered, skipping");
        }

        // Define custom SciTeX dark theme with consistent background
        monaco.editor.defineTheme("scitex-dark", {
          base: "vs-dark",
          inherit: true,
          rules: [],
          colors: {
            "editor.background": "#1a2332",
            "editor.lineHighlightBackground": "#1a2332",
            "editorLineNumber.foreground": "#6c8ba0",
            "editorLineNumber.activeForeground": "#b5c7d1",
            "editor.selectionBackground": "#34495e",
            "editor.inactiveSelectionBackground": "#2a3a4a",
          },
        });

        // Get initial value before replacing element
        const textareaElement = element as HTMLTextAreaElement;
        const initialValue = textareaElement.value || "";

        // Create editor container
        const editorContainer = document.createElement("div");
        editorContainer.id = `${config.elementId}-monaco`;
        editorContainer.style.cssText =
          "width: 100%; height: 100%; border: none;";
        element.parentElement?.replaceChild(editorContainer, element);

        // Detect current theme
        const isDarkMode =
          document.documentElement.getAttribute("data-theme") === "dark";
        const initialTheme = isDarkMode ? "vs-dark" : "vs";

        this.monacoEditor = monaco.editor.create(editorContainer, {
          value: initialValue,
          language: "latex",
          theme: initialTheme,
          lineNumbers: config.lineNumbers !== false ? "on" : "off",
          wordWrap: config.lineWrapping !== false ? "on" : "off",
          wrappingIndent: "indent", // Wrap with proper indentation
          tabSize: 2, // LaTeX standard: 2 spaces
          insertSpaces: true,

          // ============================================================
          // RAINBOW BRACKETS & BRACKET FEATURES (Emacs-style!)
          // ============================================================
          "bracketPairColorization.enabled": true,
          "bracketPairColorization.independentColorPoolPerBracketType": true,
          matchBrackets: "always", // Highlight matching brackets
          autoClosingBrackets: "always",
          autoClosingQuotes: "always",
          autoSurround: "languageDefined", // Auto-surround selected text

          // ============================================================
          // VISUAL GUIDES (Python/Elisp-style structure visualization)
          // ============================================================
          "guides.bracketPairs": true, // Vertical lines for bracket pairs
          "guides.highlightActiveBracketPair": true, // Highlight active pair
          "guides.indentation": true, // Show indentation guides

          // ============================================================
          // SMART EDITING FEATURES
          // ============================================================
          formatOnPaste: true, // Auto-format on paste
          formatOnType: true, // Auto-format while typing

          // ============================================================
          // UI & NAVIGATION
          // ============================================================
          automaticLayout: true,
          minimap: { enabled: false }, // Disable minimap
          folding: true, // Enable code folding
          foldingStrategy: "indentation", // Fold based on indentation
          scrollBeyondLastLine: false,
          fontSize: 14,
          lineHeight: 21, // Fixed: was 19, now 21 (1.5x fontSize for proper cursor alignment)
          fontFamily: 'Consolas, Monaco, "Courier New", monospace', // Fixed: use web-safe monospace fonts
          renderLineHighlight: "none",

          // ============================================================
          // AUTOCOMPLETE & SUGGESTIONS
          // ============================================================
          suggestOnTriggerCharacters: true,
          quickSuggestions: true,
          wordBasedSuggestions: false,
          fixedOverflowWidgets: true, // CRITICAL: Render widgets in body to prevent clipping
          suggest: {
            showIcons: true,
            showStatusBar: true, // Keep "show more" text visible
            maxVisibleSuggestions: 20, // Show up to 20 suggestions at once
            snippetsPreventQuickSuggestions: false,
            preselect: "first", // Preselect first item
          },

          // ============================================================
          // SCROLLBAR
          // ============================================================
          scrollbar: {
            vertical: "visible",
            horizontal: "visible",
            verticalScrollbarSize: 10,
            horizontalScrollbarSize: 10,
            alwaysConsumeMouseWheel: true,
          },
          mouseWheelScrollSensitivity: 1,
          fastScrollSensitivity: 5,
        });

        this.editor = this.monacoEditor;
        this.editorType = "monaco";
        this.setupMonacoEditor();

        // Initialize spell checker
        injectSpellCheckStyles();
        this.spellChecker = new SpellChecker(monaco, this.monacoEditor, {
          enabled: true,
          language: 'en-US',
          skipLaTeXCommands: true,
          skipMathMode: true,
          skipCodeBlocks: true,
        });
        this.spellChecker.loadCustomDictionary();
        this.spellChecker.enable();
        console.log("[Editor] Spell checker initialized and enabled");

        // Listen for global theme changes and update editor theme
        const themeObserver = new MutationObserver(() => {
          const isDarkMode =
            document.documentElement.getAttribute("data-theme") === "dark";
          const newTheme = isDarkMode ? "vs-dark" : "vs";
          monaco.editor.setTheme(newTheme);
          console.log("[Editor] Monaco theme auto-switched to:", newTheme);
        });
        themeObserver.observe(document.documentElement, {
          attributes: true,
          attributeFilter: ["data-theme"],
        });

        console.log("[Editor] Monaco Editor initialized with LaTeX support");
      } catch (error) {
        console.warn(
          "[Editor] Monaco initialization failed, falling back to CodeMirror",
          error,
        );
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

    const monaco = (window as any).monaco;

    // Track changes
    this.monacoEditor.onDidChangeModelContent(() => {
      const content = this.monacoEditor.getValue();
      const wordCount = this.countWords(content);

      if (this.onChangeCallback) {
        this.onChangeCallback(content, wordCount);
      }
    });

    // Save cursor position on cursor changes (debounced)
    let cursorSaveTimeout: number | undefined;
    this.monacoEditor.onDidChangeCursorPosition(() => {
      if (cursorSaveTimeout) {
        clearTimeout(cursorSaveTimeout);
      }
      cursorSaveTimeout = window.setTimeout(() => {
        if (this.currentSectionId) {
          this.saveCursorPosition(this.currentSectionId);
        }
      }, 500); // Debounce by 500ms
    });

    // Add custom comment toggle action (Ctrl+/ or Cmd+/)
    this.monacoEditor.addAction({
      id: "toggle-line-comment",
      label: "Toggle Line Comment",
      keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.Slash],
      contextMenuGroupId: "modification",
      contextMenuOrder: 1.5,
      run: (editor: any) => {
        // Use Monaco's built-in toggle line comment action
        editor.trigger("keyboard", "editor.action.commentLine", {});
      },
    });

    // Add Ctrl+; (C-;) as alternative comment toggle shortcut
    this.monacoEditor.addAction({
      id: "toggle-line-comment-alt",
      label: "Toggle Line Comment (Alt)",
      keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.Semicolon],
      run: (editor: any) => {
        // Use Monaco's built-in toggle line comment action
        editor.trigger("keyboard", "editor.action.commentLine", {});
      },
    });

    // Setup drag-and-drop for citation insertion
    this.setupCitationDropZone();

    // Setup citation protection (atomic delete)
    this.setupCitationProtection();

    console.log("[Editor] Monaco Editor listeners and actions configured");
  }

  /**
   * Setup drag-and-drop zone for citation insertion
   */
  private setupCitationDropZone(): void {
    if (!this.monacoEditor) return;

    const editorDomNode = this.monacoEditor.getDomNode();
    if (!editorDomNode) return;

    // Dragover: Allow drop
    editorDomNode.addEventListener("dragover", (e: DragEvent) => {
      e.preventDefault();
      if (e.dataTransfer) {
        e.dataTransfer.dropEffect = "copy";
      }
      // Add visual feedback
      editorDomNode.parentElement?.classList.add("drag-over");
    });

    // Dragleave: Remove visual feedback
    editorDomNode.addEventListener("dragleave", () => {
      editorDomNode.parentElement?.classList.remove("drag-over");
    });

    // Drop: Insert citation
    editorDomNode.addEventListener("drop", (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation(); // Prevent Monaco's default drop handling
      editorDomNode.parentElement?.classList.remove("drag-over");

      if (!e.dataTransfer) return;

      const citationKey = e.dataTransfer.getData("text/plain");
      if (!citationKey) return;

      // Get drop position from Monaco
      const position = this.monacoEditor.getTargetAtClientPoint(
        e.clientX,
        e.clientY,
      );
      if (!position) return;

      // Insert \cite{key} at drop position
      const citationText = `\\cite{${citationKey}}`;
      const range = {
        startLineNumber: position.position.lineNumber,
        startColumn: position.position.column,
        endLineNumber: position.position.lineNumber,
        endColumn: position.position.column,
      };

      // Use pushEditOperations to prevent default text insertion
      this.monacoEditor.pushUndoStop();
      this.monacoEditor.executeEdits("citation-drop", [
        {
          range: range,
          text: citationText,
          forceMoveMarkers: true,
        },
      ]);
      this.monacoEditor.pushUndoStop();

      // Focus editor and move cursor after citation
      this.monacoEditor.setPosition({
        lineNumber: position.position.lineNumber,
        column: position.position.column + citationText.length,
      });
      this.monacoEditor.focus();

      console.log(
        `[Editor] Inserted citation at drop position: ${citationKey}`,
      );

      // Show toast notification
      const showToast = (window as any).showToast;
      if (showToast) {
        showToast(`Citation added: ${citationKey}`, "success");
      }
    });

    console.log("[Editor] Citation drop zone configured");
  }


  /**
   * Setup citation protection - treat \cite{key} as atomic unit
   */
  private setupCitationProtection(): void {
    if (!this.monacoEditor) return;

    const monaco = (window as any).monaco;

    // Register link provider to detect citations
    monaco.languages.registerLinkProvider("latex", {
      provideLinks: (model: any) => {
        const links: any[] = [];
        const lineCount = model.getLineCount();

        for (let lineNumber = 1; lineNumber <= lineCount; lineNumber++) {
          const lineContent = model.getLineContent(lineNumber);

          // Find all \cite{...} patterns
          const regex = /\\cite[tp]?\{([^}]+)\}/g;
          let match;

          while ((match = regex.exec(lineContent)) !== null) {
            const startColumn = match.index + 1;
            const endColumn = match.index + match[0].length + 1;

            links.push({
              range: new monaco.Range(
                lineNumber,
                startColumn,
                lineNumber,
                endColumn,
              ),
              url: `#citation:${match[1]}`,
              tooltip: `Citation: ${match[1]} (Click to select whole citation)`,
            });
          }
        }

        return { links };
      },
    });

  }

  /**
   * Initialize CodeMirror fallback
   */
  private initializeCodeMirror(config: MonacoEditorConfig): void {
    if ((window as any).CodeMirror) {
      const element = document.getElementById(config.elementId);
      if (!element) {
        throw new Error(
          `Editor element with id "${config.elementId}" not found`,
        );
      }

      this.editor = (window as any).CodeMirror.fromTextArea(element, {
        mode: config.mode || "text/x-latex",
        theme: config.theme || "default",
        lineNumbers: config.lineNumbers !== false,
        lineWrapping: config.lineWrapping !== false,
        indentUnit: config.indentUnit || 4,
        tabSize: 4,
        indentWithTabs: false,
        autoCloseBrackets: true,
        matchBrackets: true,
      });

      this.editorType = "codemirror";
      this.setupCodeMirrorEditor();
    } else {
      console.warn(
        "[Editor] Neither Monaco nor CodeMirror available. Editor will not be initialized.",
      );
    }
  }

  /**
   * Setup CodeMirror event listeners
   */
  private setupCodeMirrorEditor(): void {
    if (!this.editor || this.editorType !== "codemirror") return;

    // Track changes
    this.editor.on("change", (editor: any) => {
      const content = editor.getValue();
      const wordCount = this.countWords(content);

      if (this.onChangeCallback) {
        this.onChangeCallback(content, wordCount);
      }
    });

    console.log("[Editor] CodeMirror initialized");
  }

  /**
   * Get editor content
   */
  getContent(): string {
    if (!this.editor) return "";
    return this.editorType === "monaco"
      ? this.monacoEditor.getValue()
      : this.editor.getValue();
  }

  /**
   * Set editor content
   */
  setContent(content: string, emitChange: boolean = false): void {
    if (!this.editor) return;

    if (this.editorType === "monaco") {
      this.monacoEditor.setValue(content);

      // Trigger spell check on existing content after a short delay
      // to ensure dictionary is loaded
      if (this.spellChecker && content.length > 0) {
        setTimeout(() => {
          if (this.spellChecker) {
            this.spellChecker.recheckAll();
          }
        }, 1500); // Wait 1.5s for dictionary to load
      }
    } else {
      const doc = this.editor.getDoc();
      const lastLine = doc.lastLine();

      this.editor.replaceRange(
        content,
        { line: 0, ch: 0 },
        { line: lastLine, ch: doc.getLine(lastLine).length },
      );

      if (emitChange) {
        this.editor.execCommand("goDocEnd");
      }
    }
  }

  /**
   * Append content to editor
   */
  appendContent(content: string): void {
    if (!this.editor) return;

    if (this.editorType === "monaco") {
      const currentContent = this.monacoEditor.getValue();
      this.monacoEditor.setValue(currentContent + content);
    } else {
      const doc = this.editor.getDoc();
      const lastLine = doc.lastLine();
      doc.replaceRange(content, {
        line: lastLine,
        ch: doc.getLine(lastLine).length,
      });
    }
  }

  /**
   * Clear editor content
   */
  clear(): void {
    this.setContent("");
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
      author: "editor",
    });

    if (this.history.length > this.maxHistorySize) {
      this.history.shift();
    } else {
      this.historyIndex++;
    }

    this.storage.save("history", this.history);
  }

  /**
   * Undo last change
   */
  undo(): boolean {
    if (this.editorType === "monaco" && this.monacoEditor) {
      this.monacoEditor.trigger("keyboard", "undo", null);
      return true;
    } else if (this.editor) {
      this.editor.execCommand("undo");
      return true;
    }
    return false;
  }

  /**
   * Redo change
   */
  redo(): boolean {
    if (this.editorType === "monaco" && this.monacoEditor) {
      this.monacoEditor.trigger("keyboard", "redo", null);
      return true;
    } else if (this.editor) {
      this.editor.execCommand("redo");
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
    if (this.editorType === "monaco" && this.monacoEditor) {
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
    if (this.editorType === "monaco" && this.monacoEditor) {
      console.log("[Editor] Setting Monaco theme to:", theme);
      // Map common CodeMirror theme names to Monaco themes
      const monacoThemeMap: Record<string, string> = {
        zenburn: "vs-dark",
        monokai: "vs-dark",
        dracula: "vs-dark",
        eclipse: "vs",
        neat: "vs",
        "solarized light": "vs",
        "scitex-dark": "scitex-dark",
        default: "vs",
      };
      const monacoTheme = monacoThemeMap[theme.toLowerCase()] || "scitex-dark";
      (window as any).monaco.editor.setTheme(monacoTheme);
    } else {
      // CodeMirror theme change
      console.log("[Editor] Setting CodeMirror theme to:", theme);
      const cmEditor = (document.querySelector(".CodeMirror") as any)
        ?.CodeMirror;
      if (cmEditor) {
        cmEditor.setOption("theme", theme);
      }
    }
  }

  /**
   * Set editor read-only state
   */
  setReadOnly(readOnly: boolean): void {
    if (this.editorType === "monaco" && this.monacoEditor) {
      console.log("[Editor] Setting Monaco readOnly to:", readOnly);
      this.monacoEditor.updateOptions({ readOnly: readOnly });
    } else {
      // CodeMirror read-only mode
      console.log("[Editor] Setting CodeMirror readOnly to:", readOnly);
      const cmEditor = (document.querySelector(".CodeMirror") as any)
        ?.CodeMirror;
      if (cmEditor) {
        cmEditor.setOption("readOnly", readOnly);
      }
    }
  }

  /**
   * Set editor keybinding mode
   */
  setKeyBinding(mode: string): void {
    if (this.editorType === "monaco" && this.monacoEditor) {
      console.log("[Editor] Monaco keybinding change requested:", mode);
      // Monaco doesn't directly support Vim/Emacs keybindings without extensions
      // For now, just log - would need monaco-vim or monaco-emacs packages
      console.warn(
        "[Editor] Monaco Vim/Emacs keybindings require additional packages",
      );
    } else {
      // CodeMirror keymap
      console.log("[Editor] Setting CodeMirror keymap to:", mode);
      const cmEditor = (document.querySelector(".CodeMirror") as any)
        ?.CodeMirror;
      if (cmEditor) {
        cmEditor.setOption("keyMap", mode);
      }
    }
  }

  /**
   * Save cursor position for a section (like Emacs save-place)
   */
  private saveCursorPosition(sectionId: string): void {
    if (!this.monacoEditor || !sectionId) return;

    const position = this.monacoEditor.getPosition();
    const content = this.monacoEditor.getValue();
    const contentHash = this.generateHash(content);

    const cursorData = {
      lineNumber: position.lineNumber,
      column: position.column,
      contentHash: contentHash,
      timestamp: Date.now(),
    };

    this.storage.save(`cursor_${sectionId}`, cursorData);
    console.log(
      `[Editor] Saved cursor position for ${sectionId}:`,
      cursorData.lineNumber,
      ":",
      cursorData.column,
    );
  }

  /**
   * Restore cursor position for a section if content hash matches
   */
  private restoreCursorPosition(sectionId: string, content: string): void {
    if (!this.monacoEditor || !sectionId) return;

    const savedData = this.storage.load<any>(`cursor_${sectionId}`);
    if (!savedData) {
      console.log(`[Editor] No saved cursor position for ${sectionId}`);
      return;
    }

    const currentHash = this.generateHash(content);
    if (savedData.contentHash !== currentHash) {
      console.log(
        `[Editor] Content changed for ${sectionId}, not restoring cursor (hash mismatch)`,
      );
      return;
    }

    // Restore cursor position
    const position = {
      lineNumber: savedData.lineNumber,
      column: savedData.column,
    };

    // Use setTimeout to ensure editor is fully rendered
    setTimeout(() => {
      this.monacoEditor.setPosition(position);
      this.monacoEditor.revealPositionInCenter(position);
      this.monacoEditor.focus(); // Activate cursor automatically
      console.log(
        `[Editor] Restored cursor position for ${sectionId}:`,
        position.lineNumber,
        ":",
        position.column,
      );
    }, 50);
  }

  /**
   * Set content with optional section ID for cursor position management
   */
  setContentForSection(sectionId: string, content: string): void {
    // Save cursor position for current section before switching
    if (this.currentSectionId && this.currentSectionId !== sectionId) {
      this.saveCursorPosition(this.currentSectionId);
    }

    // Update current section
    this.currentSectionId = sectionId;

    // Set content
    this.setContent(content);

    // Restore cursor position for new section
    const savedData = this.storage.load<any>(`cursor_${sectionId}`);
    if (savedData) {
      this.restoreCursorPosition(sectionId, content);
    } else {
      // No saved cursor position, just focus the editor
      setTimeout(() => {
        if (this.monacoEditor) {
          this.monacoEditor.focus();
          console.log(
            `[Editor] No saved cursor for ${sectionId}, focused editor at start`,
          );
        }
      }, 50);
    }
  }

  /**
   * Enable spell checking
   */
  enableSpellCheck(): void {
    if (this.spellChecker) {
      this.spellChecker.enable();
      console.log("[Editor] Spell check enabled");
    }
  }

  /**
   * Disable spell checking
   */
  disableSpellCheck(): void {
    if (this.spellChecker) {
      this.spellChecker.disable();
      console.log("[Editor] Spell check disabled");
    }
  }

  /**
   * Re-check all content for spelling errors
   */
  recheckSpelling(): void {
    if (this.spellChecker) {
      this.spellChecker.recheckAll();
      console.log("[Editor] Re-checking all content");
    }
  }

  /**
   * Add word to custom dictionary
   */
  addToSpellCheckDictionary(word: string): void {
    if (this.spellChecker) {
      this.spellChecker.addToCustomDictionary(word);
    }
  }

  /**
   * Clear custom spell check dictionary
   */
  clearSpellCheckDictionary(): void {
    if (this.spellChecker) {
      this.spellChecker.clearCustomDictionary();
    }
  }
}
