<!-- ---
!-- Timestamp: 2025-11-13 03:07:59
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/MONACO_IMPROVEMENT.md
!-- --- -->

# Monaco Editor Enhancement for SciTeX

## Vision: Visual Structure over Forced Formatting

**"Embrace the Parentheses" (Learn from Elisp/Lisp)**

Instead of imposing aggressive newline rules, let visual features reveal the structure of deeply-nested LaTeX code. Monaco Editor provides 90% of what we need out of the box!

---

## Implementation Checklist

### Core Bracket Features
- [x] Enable rainbow bracket colorization (`bracketPairColorization.enabled: true`)
- [x] Configure independent color pools per bracket type
- [x] Enable bracket matching (`matchBrackets: 'always'`)
- [x] Enable auto-closing for brackets and quotes
- [x] Enable bracket pair visual guides
- [x] Enable auto-surround feature (`autoSurround: 'languageDefined'`)

### LaTeX-Specific Configuration
- [x] Register LaTeX language in Monaco
- [x] Configure LaTeX syntax highlighting with MonarchTokensProvider
  - [x] Commands (`\section`, `\usepackage`, etc.)
  - [x] Comments (`%`)
  - [x] Environments (`\begin{}`, `\end{}`)
  - [x] Math mode delimiters (`$`, `$$`)
- [x] Configure LaTeX bracket pairs (including `\begin{}`/`\end{}` as pairs)
- [x] Configure LaTeX auto-closing pairs (including `$` for math mode)
- [x] Configure surrounding pairs for LaTeX

### Visual Navigation Features
- [x] Enable indentation guides
- [x] Enable code folding with indentation strategy
- [x] Enable minimap for document overview
- [x] Enable active bracket pair highlighting

### Smart Editing Features
- [x] Enable format on paste
- [x] Enable format on type
- [x] Configure word wrap with proper indentation (`wrappingIndent: 'indent'`)
- [x] Set editor preferences (tabSize: 2, insertSpaces: true)
- [x] Configure font family for monospace display

### Structural Editing Features ⭐ NEW!
- [x] Atomic paired token deletion (`\command{` paired with `}`)
- [x] Block editing inside tokens (no character insertion/deletion)
- [x] Protect token integrity (`\section{` cannot become `\sectin{`)
- [x] Atomic undo/redo (paired operations = single undo step)
- [x] Visual feedback when edit blocked inside token

### Testing & Integration
- [ ] Test rainbow brackets with deeply nested LaTeX structures
- [ ] Verify `\begin{}`/`\end{}` bracket pair matching
- [ ] Test auto-close and auto-surround with various bracket types
- [ ] Test structural editing (token protection, atomic deletion)
- [ ] Integrate Monaco LaTeX editor with citation panels (already integrated)
- [ ] Integrate Monaco LaTeX editor with figure panels
- [ ] Test folding with sections and environments

---

## Monaco Editor Configuration Reference

### Basic Setup

```javascript
monaco.editor.create(element, {
  // Rainbow brackets - BUILT IN!
  'bracketPairColorization.enabled': true,
  'bracketPairColorization.independentColorPoolPerBracketType': true
});
```

### Complete Recommended Config for SciTeX

```javascript
const editorConfig = {
  language: 'latex',
  theme: 'vs-dark',
  fontSize: 14,
  fontFamily: 'Consolas, Monaco, Courier New, monospace',

  // Rainbow brackets (like Emacs)
  'bracketPairColorization.enabled': true,
  'bracketPairColorization.independentColorPoolPerBracketType': true,

  // Bracket matching
  'matchBrackets': 'always',
  'autoClosingBrackets': 'always',
  'autoClosingQuotes': 'always',

  // Visual guides
  'guides.bracketPairs': true,
  'guides.highlightActiveBracketPair': true,
  'guides.indentation': true,

  // Smart editing
  'autoSurround': 'languageDefined',
  'formatOnPaste': true,
  'formatOnType': true,

  // LaTeX-specific
  'tabSize': 2,
  'insertSpaces': true,
  'wordWrap': 'on',
  'wrappingIndent': 'indent',

  // UI
  'minimap.enabled': true,
  'lineNumbers': 'on',
  'folding': true,
  'foldingStrategy': 'indentation'
};
```

### LaTeX Language Configuration

```javascript
// Register LaTeX language
monaco.languages.register({ id: 'latex' });

// Define LaTeX tokens
monaco.languages.setMonarchTokensProvider('latex', {
  tokenizer: {
    root: [
      // Commands
      [/\\[a-zA-Z@]+/, 'keyword'],

      // Braces (for colorization)
      [/\{/, '@brackets'],
      [/\}/, '@brackets'],

      // Brackets
      [/\[/, '@brackets'],
      [/\]/, '@brackets'],

      // Environments
      [/\\begin\{[^}]+\}/, 'tag'],
      [/\\end\{[^}]+\}/, 'tag'],

      // Comments
      [/%.*$/, 'comment'],
    ]
  }
});

// Configure bracket pairs for LaTeX
monaco.languages.setLanguageConfiguration('latex', {
  brackets: [
    ['{', '}'],
    ['[', ']'],
    ['\\begin{', '\\end{']  // Treat environments as bracket pairs!
  ],

  autoClosingPairs: [
    { open: '{', close: '}' },
    { open: '[', close: ']' },
    { open: '$', close: '$' },
    { open: '\\begin{', close: '}', notIn: ['string', 'comment'] }
  ],

  surroundingPairs: [
    { open: '{', close: '}' },
    { open: '[', close: ']' }
  ]
});
```

---

## Expected Features

### What You Get Out of the Box
✅ **Rainbow brackets** - different colors for nesting levels
✅ **Bracket matching** - click on `{`, highlights matching `}`
✅ **Auto-close** - type `{`, auto-inserts `}`
✅ **Auto-surround** - select text, type `{`, wraps in `{}`
✅ **Bracket guides** - vertical lines showing bracket pairs
✅ **Active bracket highlight** - current bracket pair highlighted

### Benefits
🌈 **Rainbow brackets** (Emacs-style)
⚛️ **Atomic pairs** (auto-close, auto-surround)
🎨 **Syntax highlighting** (commands, comments, etc.)
📏 **Indentation guides** (Python-style)
🔍 **Bracket matching** (click to see pairs)
✨ **Smart editing** (format on paste/type)

### Visual Features Replace Aggressive Newlines
- Rainbow colors show nesting
- Guides show structure
- Folding collapses sections
- Minimap shows document outline

---

## Example: Elisp-Style LaTeX with Monaco

```latex
\documentclass{article}
\usepackage{graphicx}

\begin{document}

\section{Introduction}
  Scientific manuscript preparation requires careful management.

  \subsection{Background}
    Previous work has shown essential principles.

    \begin{itemize}
      \item{First key point}
      \item{Second key point
        \begin{itemize}
          \item{Nested point A}
          \item{Nested point B}
        \end{itemize}}
    \end{itemize}

\section{Methods}
  \begin{figure}[h]
    \centering
    \includegraphics[width=0.8\textwidth]{architecture.png}
    \caption{System architecture showing main components}
    \label{fig:architecture}
  \end{figure}

  See Figure~\ref{fig:architecture} for details.

\end{document}
```

With Monaco's rainbow brackets, you'll instantly see the nesting structure!

---

## Minimal Monaco Setup for LaTeX

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" data-name="vs/editor/editor.main"
          href="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs/editor/editor.main.min.css">
</head>
<body>
    <div id="container" style="width:800px;height:600px;border:1px solid grey"></div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs/loader.min.js"></script>
    <script>
        require.config({
            paths: {
                vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs'
            }
        });

        require(['vs/editor/editor.main'], function() {
            // Register LaTeX language
            monaco.languages.register({ id: 'latex' });

            // LaTeX syntax highlighting
            monaco.languages.setMonarchTokensProvider('latex', {
                tokenizer: {
                    root: [
                        [/\\[a-zA-Z@]+/, 'keyword'],
                        [/%.*$/, 'comment'],
                        [/\{/, '@brackets'],
                        [/\}/, '@brackets']
                    ]
                }
            });

            // Bracket configuration
            monaco.languages.setLanguageConfiguration('latex', {
                brackets: [
                    ['{', '}'],
                    ['[', ']']
                ],
                autoClosingPairs: [
                    { open: '{', close: '}' },
                    { open: '[', close: ']' },
                    { open: '$', close: '$' }
                ]
            });

            // Create editor
            const editor = monaco.editor.create(document.getElementById('container'), {
                value: `\\documentclass{article}

\\begin{document}

\\section{Introduction}

\\begin{itemize}
  \\item First {nested {deeply {nested}}}
  \\item Second
\\end{itemize}

\\end{document}`,
                language: 'latex',
                theme: 'vs-dark',
                fontSize: 14,

                // RAINBOW BRACKETS! ✨
                'bracketPairColorization.enabled': true,
                'bracketPairColorization.independentColorPoolPerBracketType': true,

                // Bracket matching
                'matchBrackets': 'always',
                'autoClosingBrackets': 'always',

                // Visual guides
                'guides.bracketPairs': true,
                'guides.bracketPairsHorizontal': true,
                'guides.highlightActiveBracketPair': true,

                // Auto-surround
                'autoSurround': 'languageDefined',

                // Other useful features
                'formatOnPaste': true,
                'formatOnType': true,
                'minimap.enabled': true,
                'lineNumbers': 'on'
            });
        });
    </script>
</body>
</html>
```

---

## Next Steps

1. Implement core bracket features in current Monaco editor instance
2. Add LaTeX language configuration
3. Test with complex nested LaTeX documents
4. Integrate with citation and figure management panels
5. Gather user feedback on visual structure approach vs forced formatting

<!-- EOF -->