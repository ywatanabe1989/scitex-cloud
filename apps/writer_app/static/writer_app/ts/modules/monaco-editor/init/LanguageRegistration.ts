/**
 * Language Registration Module
 * Handles LaTeX language registration with Monaco Editor
 */

console.log("[DEBUG] LanguageRegistration.ts loaded");

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
