/**
 * Editor Theme Module
 * Handles theme definitions and automatic theme switching
 */

console.log("[DEBUG] EditorTheme.ts loaded");

/**
 * Define custom SciTeX dark theme
 */
export function defineScitexTheme(monaco: any): void {
  monaco.editor.defineTheme("scitex-dark", {
    base: "vs-dark",
    inherit: true,
    rules: [
      // LaTeX syntax highlighting rules
      { token: "comment.latex", foreground: "6A9955", fontStyle: "italic" },
      { token: "keyword.latex", foreground: "569CD6" },           // \commands
      { token: "keyword.control.latex", foreground: "C586C0" },   // \begin, \end
      { token: "keyword.section.latex", foreground: "DCDCAA", fontStyle: "bold" }, // \section, \chapter
      { token: "keyword.math.latex", foreground: "9CDCFE" },      // commands in math mode
      { token: "string.math.latex", foreground: "CE9178" },       // math content
      { token: "type.identifier.latex", foreground: "4EC9B0" },   // environment names
      { token: "delimiter.curly.latex", foreground: "FFD700" },   // { }
      { token: "delimiter.square.latex", foreground: "DA70D6" },  // [ ]
      { token: "number.latex", foreground: "B5CEA8" },
      { token: "operator.latex", foreground: "D4D4D4" },          // & ~ ^ _
    ],
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
 * Define light theme variant for SciTeX
 */
export function defineScitexLightTheme(monaco: any): void {
  monaco.editor.defineTheme("scitex-light", {
    base: "vs",
    inherit: true,
    rules: [
      // LaTeX syntax highlighting rules (light theme)
      { token: "comment.latex", foreground: "008000", fontStyle: "italic" },
      { token: "keyword.latex", foreground: "0000FF" },           // \commands
      { token: "keyword.control.latex", foreground: "AF00DB" },   // \begin, \end
      { token: "keyword.section.latex", foreground: "795E26", fontStyle: "bold" }, // \section, \chapter
      { token: "keyword.math.latex", foreground: "001080" },      // commands in math mode
      { token: "string.math.latex", foreground: "A31515" },       // math content
      { token: "type.identifier.latex", foreground: "267F99" },   // environment names
      { token: "delimiter.curly.latex", foreground: "B8860B" },   // { }
      { token: "delimiter.square.latex", foreground: "800080" },  // [ ]
      { token: "number.latex", foreground: "098658" },
      { token: "operator.latex", foreground: "000000" },          // & ~ ^ _
    ],
    colors: {
      "editor.background": "#FFFFFF",
      "editor.lineHighlightBackground": "#F5F5F5",
      "editorLineNumber.foreground": "#6E7681",
      "editorLineNumber.activeForeground": "#24292F",
      "editor.selectionBackground": "#ADD6FF",
      "editor.inactiveSelectionBackground": "#E5EBF1",
    },
  });
}

/**
 * Setup theme observer to auto-switch Monaco theme
 */
export function setupThemeObserver(monaco: any): void {
  const themeObserver = new MutationObserver(() => {
    const isDarkMode =
      document.documentElement.getAttribute("data-theme") === "dark";
    const newTheme = isDarkMode ? "scitex-dark" : "scitex-light";
    monaco.editor.setTheme(newTheme);
    console.log("[Editor] Monaco theme auto-switched to:", newTheme);
  });
  themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-theme"],
  });
}
