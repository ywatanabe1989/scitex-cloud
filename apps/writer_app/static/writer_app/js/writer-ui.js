/**
 * Writer UI Module
 * Handles UI updates, theme management, and keybinding settings
 */
import { writerStorage } from '@/utils/storage.js';

/**
 * Update word count display
 */
export function updateWordCountDisplay(_section, count) {
    const display = document.getElementById('current-word-count');
    if (display) {
        display.textContent = String(count);
    }
}

/**
 * Show toast notification
 */
export function showToast(message, _type = 'info') {
    const fn = window.showToast || ((msg) => console.log(msg));
    fn(message);
}

/**
 * Get current global page theme (light or dark)
 */
export function getPageTheme() {
    const theme = document.documentElement.getAttribute('data-theme');
    return theme === 'light' ? 'light' : 'dark';
}

/**
 * Filter theme dropdown options based on page theme
 */
export function filterThemeOptions() {
    const themeSelector = document.getElementById('theme-selector');
    if (!themeSelector)
        return;

    const pageTheme = getPageTheme();
    const optgroups = themeSelector.querySelectorAll('optgroup');

    optgroups.forEach((optgroup) => {
        const label = optgroup.label.toLowerCase();
        const isLightGroup = label.includes('light');
        const isDarkGroup = label.includes('dark');

        // Show only matching theme group
        if (pageTheme === 'light' && isLightGroup) {
            optgroup.style.display = '';
        }
        else if (pageTheme === 'dark' && isDarkGroup) {
            optgroup.style.display = '';
        }
        else {
            optgroup.style.display = 'none';
        }
    });

    // If current selected option is hidden, select first visible option
    const currentOption = themeSelector.options[themeSelector.selectedIndex];
    if (currentOption && currentOption.parentElement instanceof HTMLOptGroupElement) {
        if (currentOption.parentElement.style.display === 'none') {
            // Find first visible option
            for (let i = 0; i < themeSelector.options.length; i++) {
                const option = themeSelector.options[i];
                if (option.parentElement instanceof HTMLOptGroupElement &&
                    option.parentElement.style.display !== 'none') {
                    themeSelector.selectedIndex = i;
                    // Trigger change to apply the new theme
                    themeSelector.dispatchEvent(new Event('change'));
                    break;
                }
            }
        }
    }
}

/**
 * Apply code editor theme to Monaco or CodeMirror
 */
export function applyCodeEditorTheme(theme, editor) {
    if (!editor)
        return;

    const editorType = editor.getEditorType ? editor.getEditorType() : 'codemirror';

    if (editorType === 'monaco' && editor.setTheme) {
        console.log('[Writer] Applying Monaco theme:', theme);
        editor.setTheme(theme);
    }
    else {
        // CodeMirror
        const cmEditor = document.querySelector('.CodeMirror')?.CodeMirror;
        if (cmEditor) {
            console.log('[Writer] Applying CodeMirror theme:', theme);
            cmEditor.setOption('theme', theme);
        }
    }
}

/**
 * Setup theme listener
 */
export function setupThemeListener(editor) {
    const themeSelector = document.getElementById('theme-selector');
    if (!themeSelector)
        return;

    // Initial filter based on page theme
    filterThemeOptions();

    // Load saved theme or use default
    const savedTheme = writerStorage.load('editor_theme');
    if (savedTheme && typeof savedTheme === 'string') {
        themeSelector.value = savedTheme;
        if (editor) {
            applyCodeEditorTheme(savedTheme, editor);
        }
    }

    // Listen for code editor theme changes
    themeSelector.addEventListener('change', () => {
        const theme = themeSelector.value;
        writerStorage.save('editor_theme', theme);
        console.log('[Writer] Code editor theme changed to:', theme);
        if (editor) {
            applyCodeEditorTheme(theme, editor);
        }
    });

    // Listen for global page theme changes
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
                console.log('[Writer] Page theme changed, filtering code editor themes');
                filterThemeOptions();
            }
        });
    });

    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-theme']
    });
}

/**
 * Setup keybinding listener
 */
export function setupKeybindingListener(editor) {
    const keybindingSelector = document.getElementById('keybinding-selector');
    if (!keybindingSelector)
        return;

    // Load saved keybinding
    const savedKeybinding = writerStorage.load('editor_keybinding');
    if (savedKeybinding && typeof savedKeybinding === 'string') {
        keybindingSelector.value = savedKeybinding;
        if (editor && editor.setKeyBinding) {
            editor.setKeyBinding(savedKeybinding);
        }
    }

    // Listen for keybinding changes
    keybindingSelector.addEventListener('change', () => {
        const keybinding = keybindingSelector.value;
        writerStorage.save('editor_keybinding', keybinding);
        console.log('[Writer] Keybinding changed to:', keybinding);
        if (editor && editor.setKeyBinding) {
            editor.setKeyBinding(keybinding);
        }
    });
}

/**
 * Setup sidebar button listeners
 */
export function setupSidebarButtons(_config) {
    // Button listeners are set up in their respective initialization functions
    // No additional setup needed here
}
