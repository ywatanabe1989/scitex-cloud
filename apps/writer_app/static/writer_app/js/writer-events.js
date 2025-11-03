/**
 * Writer Events Module
 * Handles editor and section event listeners
 */
import { switchSection } from './writer-sections.js';
import { saveSections, scheduleSave } from './writer-storage.js';
import { scheduleAutoCompile, handleCompileFull, handleCompile } from './writer-compilation.js';
import { updateWordCountDisplay } from './writer-ui.js';
import { showCommitModal, handleGitCommit } from './writer-git.js';

/**
 * Setup editor event listeners
 */
export function setupEditorListeners(editor, sectionsManager, compilationManager, state, pdfPreviewManager) {
    if (!editor)
        return;

    // Track changes
    editor.onChange((content, wordCount) => {
        const currentSection = state.currentSection;

        // Skip tracking changes for compiled sections (read-only)
        const isCompiledSection = currentSection && (currentSection.endsWith('/compiled_pdf') ||
            currentSection.endsWith('/compiled_tex'));

        if (isCompiledSection) {
            console.log('[Writer] Skipping change tracking for compiled section:', currentSection);
            return;
        }

        sectionsManager.setContent(currentSection, content);
        state.unsavedSections.add(currentSection);

        // Update word count display
        updateWordCountDisplay(currentSection, wordCount);

        // Schedule auto-save
        scheduleSave(editor, sectionsManager, state);

        // Schedule auto-compile for live PDF preview (skip for compiled_pdf sections)
        if (pdfPreviewManager && !currentSection.endsWith('/compiled_pdf')) {
            scheduleAutoCompile(pdfPreviewManager, content, currentSection);
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + S to save
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            saveSections(sectionsManager, state);
        }

        // Ctrl/Cmd + Shift + X to compile
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'X') {
            e.preventDefault();
            handleCompile(editor, sectionsManager, compilationManager, state, pdfPreviewManager);
        }
    });

    // Setup save button (Ctrl+S keyboard shortcut is handled below)
    // Note: No explicit save button in toolbar - use keyboard shortcut

    // Setup undo/redo buttons
    const undoBtn = document.getElementById('undo-btn');
    if (undoBtn && editor) {
        undoBtn.addEventListener('click', () => {
            editor.undo();
        });
    }

    const redoBtn = document.getElementById('redo-btn');
    if (redoBtn && editor) {
        redoBtn.addEventListener('click', () => {
            editor.redo();
        });
    }

    // Setup compile button (full manuscript compilation)
    const compileBtn = document.getElementById('compile-btn-toolbar');
    if (compileBtn) {
        compileBtn.addEventListener('click', () => {
            handleCompileFull(compilationManager, state);
        });
    }

    // Setup git commit button
    const commitBtn = document.getElementById('git-commit-btn');
    if (commitBtn) {
        commitBtn.addEventListener('click', () => {
            showCommitModal(state);
        });
    }

    // Setup confirm commit button (in modal)
    const confirmCommitBtn = document.getElementById('confirm-commit-btn');
    if (confirmCommitBtn) {
        confirmCommitBtn.addEventListener('click', async () => {
            await handleGitCommit(state);
        });
    }
}

/**
 * Setup section listeners
 */
export function setupSectionListeners(sectionsManager, editor, state, _storage, pdfPreviewManager) {
    const sectionItems = document.querySelectorAll('.section-tab');
    sectionItems.forEach(item => {
        item.addEventListener('click', (e) => {
            const target = e.target;
            const sectionId = target.dataset.section;
            if (sectionId) {
                switchSection(editor, sectionsManager, state, sectionId, pdfPreviewManager);
            }
        });
    });

    // NO CALLBACKS - direct error handling only
}
