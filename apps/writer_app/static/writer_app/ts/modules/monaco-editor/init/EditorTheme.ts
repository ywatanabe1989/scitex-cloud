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
