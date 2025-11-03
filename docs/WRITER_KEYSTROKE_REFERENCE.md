# Writer Keystroke Reference

**Investigation Date:** 2025-11-03
**Monaco Version:** 0.45.0
**Purpose:** Document available keystrokes for custom command implementation

## Monaco Editor Default Keybindings

**Total Actions:** 122 built-in commands

**Already Bound (Cannot Override):**
- `Ctrl+/` - Toggle Line Comment
- `Ctrl+Shift+/` - Toggle Block Comment
- `Ctrl+Z` - Undo
- `Ctrl+Y` / `Ctrl+Shift+Z` - Redo
- `Ctrl+X` - Cut
- `Ctrl+C` - Copy
- `Ctrl+V` - Paste
- `Ctrl+A` - Select All
- `Ctrl+F` - Find
- `Ctrl+H` - Replace
- `Ctrl+G` - Go to Line
- `Ctrl+D` - Add Selection to Next Find Match
- `Ctrl+[` - Outdent Line
- `Ctrl+]` - Indent Line
- `Ctrl+/` (or `Ctrl+K Ctrl+C`) - Add Line Comment
- `Alt+Up/Down` - Move Line Up/Down
- `Ctrl+Alt+Up/Down` - Add Cursor Above/Below
- `Ctrl+Shift+L` - Select All Occurrences
- `F2` - Rename Symbol
- `F3` - Find Next
- `Shift+F3` - Find Previous

## Browser Reserved Keys (Cannot Capture)

**Navigation:**
- `Ctrl+T` - New Tab
- `Ctrl+W` - Close Tab
- `Ctrl+N` - New Window
- `Ctrl+Shift+T` - Reopen Closed Tab
- `Ctrl+Tab` - Switch Tabs
- `Ctrl+L` - Focus Address Bar
- `Ctrl+R` / `F5` - Reload Page
- `Ctrl+Shift+R` - Hard Reload

**Browser Functions:**
- `Ctrl+P` - Print
- `Ctrl+S` - Save Page (we override this!)
- `Ctrl+O` - Open File
- `Ctrl+F` - Find (shared with Monaco)
- `Ctrl+Shift+Del` - Clear Browsing Data
- `F11` - Fullscreen
- `F12` - DevTools

## Available for Custom Commands

### Safe Keystrokes (No Conflicts)

**Ctrl+Shift combinations:**
- ✅ `Ctrl+Shift+C` - **Available** (cite search)
- ✅ `Ctrl+Shift+R` - ❌ Browser reload (use `Ctrl+Shift+B` instead?)
- ✅ `Ctrl+Shift+M` - **Available** (math mode)
- ✅ `Ctrl+Shift+I` - ❌ DevTools (use `Ctrl+Shift+E` instead?)
- ✅ `Ctrl+Shift+B` - **Available** (bold)
- ✅ `Ctrl+Shift+K` - **Available**
- ✅ `Ctrl+Shift+;` - **Available**

**Ctrl+Alt combinations:**
- ✅ `Ctrl+Alt+C` - **Available**
- ✅ `Ctrl+Alt+R` - **Available**
- ✅ `Ctrl+Alt+B` - **Available**
- ⚠️ `Ctrl+Alt+Up/Down` - Monaco cursor (can override)

**Ctrl+K prefix (VS Code style):**
- ✅ `Ctrl+K C` - **Available** (add comment)
- ✅ `Ctrl+K U` - **Available** (remove comment)
- ✅ `Ctrl+K S` - **Available** (save all)
- ✅ `Ctrl+K Ctrl+S` - **Available** (describe-bindings)

**Alt combinations:**
- ⚠️ `Alt+Up/Down` - Monaco move line (can override)
- ✅ `Alt+Left/Right` - **Available**
- ✅ `Alt+Shift+Up/Down` - **Available**

**F-keys:**
- ✅ `F1` - **Available** (command palette)
- ❌ `F2` - Monaco rename
- ❌ `F3` - Monaco find next
- ✅ `F4-F10` - **Available**
- ❌ `F11` - Browser fullscreen
- ❌ `F12` - Browser DevTools

**Number keys:**
- ✅ `Ctrl+1-9` - **Available** (section jump)
- ✅ `Alt+1-9` - **Available**

## Recommended Keybinding Allocation

### Citation Commands
```
Ctrl+Shift+C  → Quick cite (search BibTeX)
Ctrl+Shift+B  → Add to bibliography
\cite{        → Auto-complete trigger
```

### LaTeX Commands
```
Ctrl+;        → Toggle comment (% prefix)
Ctrl+B        → Bold \textbf{}     (or Ctrl+Shift+B if conflicts)
Ctrl+I        → Italic \emph{}     (or Ctrl+Shift+E)
Ctrl+M        → Math mode $$       (or Ctrl+Shift+M)
Ctrl+Shift+M  → Display math \[\]
```

### Navigation
```
Ctrl+1        → Jump to Abstract
Ctrl+2        → Jump to Introduction
Ctrl+3        → Jump to Methods
Ctrl+4        → Jump to Results
Ctrl+5        → Jump to Discussion
Ctrl+6        → Jump to References
Ctrl+7        → Jump to Figures
Alt+Shift+Up  → Previous section
Alt+Shift+Down→ Next section
```

### Discovery & Help
```
F1            → Command palette
Ctrl+K Ctrl+S → Describe-bindings (keybinding reference)
Ctrl+Shift+P  → Command palette (VS Code style)
```

### Symbols (Auto-Replace)
```
-->           → → (arrow right)
<--           → ← (arrow left)
+-            → ± (plus-minus)
<=            → ≤ (less or equal)
>=            → ≥ (greater or equal)
~=            → ≈ (approximately)
---           → — (em-dash)
--            → – (en-dash)
```

### Symbol Search
```
Ctrl+K        → Symbol search/insert palette
```

## Browser Conflicts to Handle

**Ctrl+S (Save):**
- Currently overridden successfully
- Works for section save

**Ctrl+P (Print):**
- Consider overriding for "Compile PDF"
- Or use Ctrl+Shift+P for compile

**Ctrl+W (Close Tab):**
- Cannot override
- Show warning if unsaved changes (beforeunload event)

## Implementation Notes

**Monaco Keybinding API:**
```javascript
editor.addAction({
    id: 'scitex.toggleComment',
    label: 'Toggle LaTeX Comment',
    keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.Semicolon],
    run: function(ed) {
        // Toggle % prefix
    }
});
```

**Keybinding Priority:**
```javascript
// Higher priority overrides Monaco defaults
editor.addAction({
    id: 'custom.action',
    keybindings: [...],
    keybindingContext: null,
    contextMenuGroupId: 'navigation',
    contextMenuOrder: 1.5,
    run: () => {}
});
```

## Next Steps

1. **Test each proposed keystroke** in actual browser/Monaco
2. **Document conflicts** encountered
3. **Create fallback keybindings** for conflicts
4. **Implement keybinding registry** system
5. **Add describe-bindings** command to show all active keys

---

**References:**
- Monaco Editor Keybinding API: https://microsoft.github.io/monaco-editor/api/interfaces/monaco.editor.IStandaloneCodeEditor.html#addAction
- Browser Keyboard Events: https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/key
