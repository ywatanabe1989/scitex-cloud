/**
 * Monaco Editor Initialization Module
 * Handles LaTeX language registration, configuration, themes, and completion providers
 */

console.log(
  "[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/modules/monaco-editor/monaco-init.ts loaded",
);

/**
 * Register LaTeX language with Monaco
 */
export function registerLatexLanguage(monaco: any): void {
  const latexExists = monaco.languages
    .getLanguages()
    .find((l: any) => l.id === "latex");
  console.log("[Monaco] LaTeX language exists:", !!latexExists);

  if (latexExists) {
    console.log("[Monaco] LaTeX language already registered, skipping");
    return;
  }

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
}

/**
 * Register LaTeX completion provider
 */
export function registerLatexCompletionProvider(monaco: any): void {
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
}

/**
 * Get project ID from various sources
 */
function getProjectId(): string | null {
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
}

/**
 * Fetch citations from API with caching
 */
async function fetchCitations(
  citationsCache: any[] | null,
  lastFetchTime: number,
  CACHE_DURATION: number
): Promise<{ citations: any[]; cache: any[]; fetchTime: number }> {
  const projectId = getProjectId();
  if (!projectId) {
    console.warn(
      "[Citations] No project ID - cannot fetch citations",
    );
    return { citations: [], cache: citationsCache || [], fetchTime: lastFetchTime };
  }

  const now = Date.now();
  if (citationsCache && now - lastFetchTime < CACHE_DURATION) {
    console.log(
      `[Citations] Using cached citations (${citationsCache.length} entries)`,
    );
    return { citations: citationsCache, cache: citationsCache, fetchTime: lastFetchTime };
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
      return { citations: [], cache: citationsCache || [], fetchTime: lastFetchTime };
    }

    const data = await response.json();
    console.log("[Citations] API response:", data);

    if (data.success && data.citations) {
      console.log(
        `[Citations] ✓ Loaded ${data.citations.length} citations`,
      );
      return { citations: data.citations, cache: data.citations, fetchTime: now };
    }
    console.warn(
      "[Citations] No citations in response:",
      data.message,
    );
    return { citations: [], cache: citationsCache || [], fetchTime: lastFetchTime };
  } catch (error) {
    console.error("[Citations] Error fetching:", error);
    return { citations: [], cache: citationsCache || [], fetchTime: lastFetchTime };
  }
}

/**
 * Register citation completion provider
 */
export function registerCitationCompletionProvider(monaco: any): void {
  console.log("[Citations] ========================================");
  console.log("[Citations] STARTING CITATION COMPLETION REGISTRATION");
  console.log("[Citations] ========================================");

  // Cache for citations
  let citationsCache: any[] | null = null;
  let lastFetchTime = 0;
  const CACHE_DURATION = 60000; // 1 minute

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

      const result = await fetchCitations(citationsCache, lastFetchTime, CACHE_DURATION);
      citationsCache = result.cache;
      lastFetchTime = result.fetchTime;
      const citations = result.citations;

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

      const currentWord = citeMatch[2] || "";

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
}

/**
 * Register citation hover provider
 */
export function registerCitationHoverProvider(monaco: any): void {
  console.log("[Citations] Registering hover provider...");

  // Cache for citations (shared with completion provider via closure)
  let citationsCache: any[] | null = null;
  let lastFetchTime = 0;
  const CACHE_DURATION = 60000; // 1 minute

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
      const result = await fetchCitations(citationsCache, lastFetchTime, CACHE_DURATION);
      citationsCache = result.cache;
      lastFetchTime = result.fetchTime;
      const citations = result.citations;

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
}

/**
 * Define custom SciTeX dark theme
 */
export function defineScitexTheme(monaco: any): void {
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
}

/**
 * Create Monaco editor instance with proper configuration
 */
export function createMonacoEditor(
  monaco: any,
  container: HTMLElement,
  initialValue: string,
  config: any
): any {
  // Detect current theme
  const isDarkMode =
    document.documentElement.getAttribute("data-theme") === "dark";
  const initialTheme = isDarkMode ? "vs-dark" : "vs";

  return monaco.editor.create(container, {
    value: initialValue,
    language: "latex",
    theme: initialTheme,
    lineNumbers: config.lineNumbers !== false ? "on" : "off",
    wordWrap: config.lineWrapping !== false ? "on" : "off",
    wrappingIndent: "indent", // Wrap with proper indentation
    tabSize: 2, // LaTeX standard: 2 spaces
    insertSpaces: true,

    // RAINBOW BRACKETS & BRACKET FEATURES (Emacs-style!)
    "bracketPairColorization.enabled": true,
    "bracketPairColorization.independentColorPoolPerBracketType": true,
    matchBrackets: "always", // Highlight matching brackets
    autoClosingBrackets: "always",
    autoClosingQuotes: "always",
    autoSurround: "languageDefined", // Auto-surround selected text

    // VISUAL GUIDES (Python/Elisp-style structure visualization)
    "guides.bracketPairs": true, // Vertical lines for bracket pairs
    "guides.highlightActiveBracketPair": true, // Highlight active pair
    "guides.indentation": true, // Show indentation guides

    // SMART EDITING FEATURES
    formatOnPaste: true, // Auto-format on paste
    formatOnType: true, // Auto-format while typing

    // UI & NAVIGATION
    automaticLayout: true,
    minimap: { enabled: false }, // Disable minimap
    folding: true, // Enable code folding
    foldingStrategy: "indentation", // Fold based on indentation
    scrollBeyondLastLine: false,
    fontSize: 14,
    lineHeight: 21, // Fixed: was 19, now 21 (1.5x fontSize for proper cursor alignment)
    fontFamily: 'Consolas, Monaco, "Courier New", monospace', // Fixed: use web-safe monospace fonts
    renderLineHighlight: "none",

    // AUTOCOMPLETE & SUGGESTIONS
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

    // SCROLLBAR
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
}

/**
 * Setup theme observer to auto-switch Monaco theme
 */
export function setupThemeObserver(monaco: any): void {
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
}
