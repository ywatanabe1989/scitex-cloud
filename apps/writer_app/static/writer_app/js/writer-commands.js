/**
 * Writer Commands Module
 * Modular command functions for custom keybindings
 */

/**
 * Command Registry
 * Maps command IDs to their implementations
 */
export const commands = {
    // LaTeX Commands
    'latex.toggleComment': toggleComment,
    'latex.wrapBold': wrapBold,
    'latex.wrapItalic': wrapItalic,
    'latex.wrapMath': wrapMath,

    // Navigation Commands
    'navigation.jumpToSection': jumpToSection,
    'navigation.nextSection': navigateNextSection,
    'navigation.previousSection': navigatePreviousSection,

    // Citation Commands (placeholder - needs Scholar integration)
    'citation.quickCite': quickCite,
    'citation.addReference': addReference,
};

/**
 * Toggle LaTeX comment (% prefix)
 * Adds or removes % at the start of selected lines
 *
 * @param {monaco.editor.IStandaloneCodeEditor} editor - Monaco editor instance
 */
export function toggleComment(editor) {
    const selection = editor.getSelection();
    if (!selection) return;

    const model = editor.getModel();
    if (!model) return;

    const startLine = selection.startLineNumber;
    const endLine = selection.endLineNumber;

    const edits = [];
    let allCommented = true;

    // Check if all lines are commented
    for (let line = startLine; line <= endLine; line++) {
        const lineContent = model.getLineContent(line);
        const trimmed = lineContent.trimStart();
        if (trimmed && !trimmed.startsWith('%')) {
            allCommented = false;
            break;
        }
    }

    // Toggle comments
    for (let line = startLine; line <= endLine; line++) {
        const lineContent = model.getLineContent(line);
        const firstNonWhitespace = lineContent.search(/\S/);

        if (firstNonWhitespace === -1) continue; // Skip empty lines

        if (allCommented) {
            // Remove comment
            const uncommented = lineContent.replace(/^(\s*)%\s?/, '$1');
            edits.push({
                range: {
                    startLineNumber: line,
                    startColumn: 1,
                    endLineNumber: line,
                    endColumn: lineContent.length + 1
                },
                text: uncommented
            });
        } else {
            // Add comment
            const commented = lineContent.substring(0, firstNonWhitespace) +
                            '% ' +
                            lineContent.substring(firstNonWhitespace);
            edits.push({
                range: {
                    startLineNumber: line,
                    startColumn: 1,
                    endLineNumber: line,
                    endColumn: lineContent.length + 1
                },
                text: commented
            });
        }
    }

    // Apply all edits
    editor.executeEdits('toggleComment', edits);
    console.log(`[Command] Toggle comment: ${allCommented ? 'uncommented' : 'commented'} ${edits.length} lines`);
}

/**
 * Wrap selection in \textbf{}
 */
export function wrapBold(editor) {
    wrapSelection(editor, '\\textbf{', '}', 'bold');
}

/**
 * Wrap selection in \emph{}
 */
export function wrapItalic(editor) {
    wrapSelection(editor, '\\emph{', '}', 'italic');
}

/**
 * Wrap selection in $$
 */
export function wrapMath(editor) {
    wrapSelection(editor, '$', '$', 'math');
}

/**
 * Generic wrapper function
 * @private
 */
function wrapSelection(editor, prefix, suffix, commandName) {
    const selection = editor.getSelection();
    if (!selection) return;

    const model = editor.getModel();
    if (!model) return;

    const selectedText = model.getValueInRange(selection);
    const wrappedText = prefix + selectedText + suffix;

    editor.executeEdits(commandName, [{
        range: selection,
        text: wrappedText
    }]);

    // Move cursor inside wrapper if selection was empty
    if (!selectedText) {
        const newPosition = {
            lineNumber: selection.startLineNumber,
            column: selection.startColumn + prefix.length
        };
        editor.setPosition(newPosition);
    }

    console.log(`[Command] Wrapped text in ${commandName}: "${selectedText}"`);
}

/**
 * Jump to specific section
 *
 * @param {number} sectionIndex - Section index (1-7)
 */
export function jumpToSection(sectionIndex) {
    // This will trigger section switching via the existing system
    const sectionMap = {
        1: 'manuscript/abstract',
        2: 'manuscript/introduction',
        3: 'manuscript/methods',
        4: 'manuscript/results',
        5: 'manuscript/discussion',
        6: 'manuscript/references',
        7: 'manuscript/figures'
    };

    const sectionId = sectionMap[sectionIndex];
    if (!sectionId) {
        console.warn(`[Command] Invalid section index: ${sectionIndex}`);
        return;
    }

    // Update dropdown to trigger section switch
    const dropdown = document.getElementById('texfile-selector');
    if (dropdown) {
        dropdown.value = sectionId;
        dropdown.dispatchEvent(new Event('change', { bubbles: true }));
        console.log(`[Command] Jumped to section: ${sectionId}`);
    }
}

/**
 * Navigate to next section
 */
export function navigateNextSection() {
    navigateSection(1);
}

/**
 * Navigate to previous section
 */
export function navigatePreviousSection() {
    navigateSection(-1);
}

/**
 * Navigate to adjacent section
 * @private
 */
function navigateSection(direction) {
    const dropdown = document.getElementById('texfile-selector');
    if (!dropdown) return;

    const currentIndex = dropdown.selectedIndex;
    const newIndex = currentIndex + direction;

    if (newIndex >= 0 && newIndex < dropdown.options.length) {
        dropdown.selectedIndex = newIndex;
        dropdown.dispatchEvent(new Event('change', { bubbles: true }));
        console.log(`[Command] Navigate section: ${direction > 0 ? 'next' : 'previous'}`);
    }
}

/**
 * Quick cite - Open BibTeX search (needs Scholar integration)
 * @placeholder
 */
export function quickCite(editor) {
    console.log('[Command] Quick cite - Scholar integration needed');
    // TODO: Open modal to search bibliography
    // TODO: Insert \cite{key} at cursor
    alert('Quick cite - Coming soon! Will integrate with Scholar search.');
}

/**
 * Add reference to bibliography
 * @placeholder
 */
export function addReference(editor) {
    console.log('[Command] Add reference - Scholar integration needed');
    // TODO: Open modal to add BibTeX entry
    alert('Add reference - Coming soon! Will integrate with Scholar.');
}

/**
 * Register all commands with Monaco editor
 *
 * @param {monaco.editor.IStandaloneCodeEditor} editor - Monaco editor instance
 * @param {object} keybindings - Keybinding configuration
 */
export function registerCommands(editor, keybindings = {}) {
    if (!editor || !window.monaco) {
        console.error('[Commands] Cannot register: editor or Monaco not available');
        return;
    }

    // Default keybindings
    const defaults = {
        'latex.toggleComment': monaco.KeyMod.CtrlCmd | monaco.KeyCode.Semicolon,
        'latex.wrapBold': monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyB,
        'latex.wrapItalic': monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyE,
        'latex.wrapMath': monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyM,
        'navigation.nextSection': monaco.KeyMod.Alt | monaco.KeyMod.Shift | monaco.KeyCode.DownArrow,
        'navigation.previousSection': monaco.KeyMod.Alt | monaco.KeyMod.Shift | monaco.KeyCode.UpArrow,
        'citation.quickCite': monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyC,
        'citation.addReference': monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyR,
    };

    // Register each command
    Object.entries(commands).forEach(([id, fn]) => {
        const keybinding = keybindings[id] || defaults[id];
        if (!keybinding) {
            console.warn(`[Commands] No keybinding for ${id}, skipping`);
            return;
        }

        try {
            editor.addAction({
                id: id,
                label: getCommandLabel(id),
                keybindings: [keybinding],
                run: function(ed) {
                    console.log(`[Command] Executing: ${id}`);
                    fn(ed);
                }
            });
            console.log(`[Commands] ✓ Registered: ${id}`);
        } catch (error) {
            console.error(`[Commands] ✗ Failed to register ${id}:`, error);
        }
    });

    // Register section jump commands (Ctrl+1 through Ctrl+7)
    for (let i = 1; i <= 7; i++) {
        try {
            editor.addAction({
                id: `navigation.jumpToSection${i}`,
                label: `Jump to Section ${i}`,
                keybindings: [monaco.KeyMod.CtrlCmd | (monaco.KeyCode.Digit1 + i - 1)],
                run: function() {
                    console.log(`[Command] Executing: Jump to section ${i}`);
                    jumpToSection(i);
                }
            });
            console.log(`[Commands] ✓ Registered: navigation.jumpToSection${i}`);
        } catch (error) {
            console.error(`[Commands] ✗ Failed to register section jump ${i}:`, error);
        }
    }

    console.log('[Commands] Registration complete');
}

/**
 * Get human-readable label for command ID
 * @private
 */
function getCommandLabel(id) {
    const labels = {
        'latex.toggleComment': 'Toggle LaTeX Comment',
        'latex.wrapBold': 'Wrap in Bold (\\textbf)',
        'latex.wrapItalic': 'Wrap in Italic (\\emph)',
        'latex.wrapMath': 'Wrap in Math Mode',
        'navigation.jumpToSection': 'Jump to Section',
        'navigation.nextSection': 'Next Section',
        'navigation.previousSection': 'Previous Section',
        'citation.quickCite': 'Quick Cite (Search BibTeX)',
        'citation.addReference': 'Add Reference',
    };
    return labels[id] || id;
}
