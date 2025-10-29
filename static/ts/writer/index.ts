/**
 * SciTeX Writer Application
 * Main entry point for the writer interface
 *
 * This module coordinates all writer modules:
 * - WriterEditor: CodeMirror editor management
 * - SectionsManager: Section and document structure management
 * - CompilationManager: LaTeX compilation and PDF management
 */

import { WriterEditor, SectionsManager, CompilationManager } from './modules';
import { getCsrfToken } from '@/utils/csrf';
import { writerStorage } from '@/utils/storage';
import { getWriterConfig, createDefaultEditorState } from './helpers';

/**
 * Show toast notification
 */
function showToast(message: string, _type: string = 'info'): void {
    const fn = (window as any).showToast || ((msg: string) => console.log(msg));
    fn(message);
}

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    console.log('[Writer] Initializing application');

    const config = getWriterConfig();
    console.log('[Writer] Config:', config);

    // Check if workspace is initialized
    if (!config.writerInitialized && !config.isDemo) {
        console.log('[Writer] Workspace not initialized - skipping editor setup');
        setupWorkspaceInitialization(config);
        return;
    }

    // Initialize editor components
    initializeEditor(config);
});

/**
 * Setup workspace initialization button
 */
function setupWorkspaceInitialization(config: any): void {
    const initBtn = document.getElementById('init-writer-btn');
    if (!initBtn) return;

    initBtn.addEventListener('click', async (e) => {
        e.preventDefault();

        if (!config.projectSlug) {
            showToast('Error: No project selected', 'error');
            return;
        }

        initBtn.setAttribute('disabled', 'true');
        initBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Creating workspace...';

        try {
            const response = await fetch('/writer/api/initialize-workspace/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    username: config.username,
                    project_slug: config.projectSlug
                })
            });

            const data = await response.json();

            if (data.success) {
                showToast('Workspace initialized successfully', 'success');
                window.location.reload();
            } else {
                showToast('Failed to initialize workspace: ' + data.error, 'error');
                initBtn.removeAttribute('disabled');
                initBtn.innerHTML = '<i class="fas fa-rocket me-2"></i>Create';
            }
        } catch (error) {
            showToast('Error: ' + (error instanceof Error ? error.message : 'Unknown error'), 'error');
            initBtn.removeAttribute('disabled');
            initBtn.innerHTML = '<i class="fas fa-rocket me-2"></i>Create';
        }
    });
}

/**
 * Initialize editor and its components
 */
function initializeEditor(config: any): void {
    console.log('[Writer] Setting up editor components');

    // Initialize editor
    let editor: WriterEditor | null = null;
    try {
        editor = new WriterEditor({
            elementId: 'editor-textarea',
            mode: 'text/x-latex',
            theme: 'default'
        });
    } catch (error) {
        console.error('[Writer] Failed to initialize editor:', error);
        showToast('Failed to initialize editor', 'error');
        return;
    }

    // Initialize sections manager
    const sectionsManager = new SectionsManager();

    // Initialize compilation manager
    const compilationManager = new CompilationManager('/writer');

    // Setup state management
    const state = createDefaultEditorState();

    // Setup event listeners
    if (editor) {
        setupEditorListeners(editor, sectionsManager, compilationManager, state);
        setupSectionListeners(sectionsManager, editor, state, writerStorage);
    }
    setupCompilationListeners(compilationManager, config);
    setupThemeListener();

    // Load initial content
    const currentSection = state.currentSection || 'abstract';
    const content = sectionsManager.getContent(currentSection);
    if (editor && content) {
        editor.setContent(content);
    }

    console.log('[Writer] Editor initialized successfully');
}

/**
 * Setup editor event listeners
 */
function setupEditorListeners(
    editor: WriterEditor | null,
    sectionsManager: SectionsManager,
    compilationManager: CompilationManager,
    state: any
): void {
    if (!editor) return;
    // Track changes
    editor.onChange((content: string, wordCount: number) => {
        const currentSection = state.currentSection;
        sectionsManager.setContent(currentSection, content);
        state.unsavedSections.add(currentSection);

        // Update word count display
        updateWordCountDisplay(currentSection, wordCount);

        // Schedule auto-save
        scheduleSave(editor, sectionsManager, state);
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
            handleCompile(editor, sectionsManager, compilationManager, state);
        }
    });

    // Setup save button
    const saveBtn = document.getElementById('save-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            saveSections(sectionsManager, state);
        });
    }

    // Setup compile button
    const compileBtn = document.getElementById('compile-btn');
    if (compileBtn) {
        compileBtn.addEventListener('click', () => {
            handleCompile(editor, sectionsManager, compilationManager, state);
        });
    }
}

/**
 * Setup section listeners
 */
function setupSectionListeners(
    sectionsManager: SectionsManager,
    editor: WriterEditor,
    state: any,
    _storage: any
): void {
    const sectionItems = document.querySelectorAll('.section-tab');
    sectionItems.forEach(item => {
        item.addEventListener('click', (e: Event) => {
            const target = e.target as HTMLElement;
            const sectionId = target.dataset.section;
            if (sectionId) {
                switchSection(editor, sectionsManager, state, sectionId);
            }
        });
    });

    // Listen for section changes
    sectionsManager.onSectionChange((sectionId: string) => {
        const content = sectionsManager.getContent(sectionId);
        editor.setContent(content);
        state.currentSection = sectionId;
        updateSectionUI(sectionId);
    });
}

/**
 * Setup compilation listeners
 */
function setupCompilationListeners(compilationManager: CompilationManager, _config: any): void {
    compilationManager.onProgress((progress: number, status: string) => {
        const progressBar = document.getElementById('compilation-progress');
        if (progressBar) {
            (progressBar as HTMLInputElement).value = String(progress);
        }

        const statusText = document.getElementById('compilation-status');
        if (statusText) {
            statusText.textContent = status;
        }
    });

    compilationManager.onComplete((_jobId: string, pdfUrl: string) => {
        const showToast = (window as any).showToast || ((msg: string) => console.log(msg));
        showToast('Compilation completed successfully');
        if (pdfUrl) {
            openPDF(pdfUrl);
        }
    });

    compilationManager.onError((error: string) => {
        const showToast = (window as any).showToast || ((msg: string) => console.error(msg));
        showToast('Compilation error: ' + error);
    });
}

/**
 * Setup theme listener
 */
function setupThemeListener(): void {
    const themeSelector = document.getElementById('theme-selector') as HTMLSelectElement;
    if (!themeSelector) return;

    themeSelector.addEventListener('change', () => {
        const theme = themeSelector.value;
        document.documentElement.setAttribute('data-theme', theme);
        writerStorage.save('theme', theme);

        // Apply theme to CodeMirror if available
        const cmEditor = (document.querySelector('.CodeMirror') as any)?.CodeMirror;
        if (cmEditor) {
            cmEditor.setOption('theme', theme === 'dark' ? 'material-darker' : 'default');
        }
    });
}

/**
 * Switch to a section
 */
function switchSection(
    editor: WriterEditor,
    sectionsManager: SectionsManager,
    state: any,
    sectionId: string
): void {
    // Save current section
    const currentContent = editor.getContent();
    sectionsManager.setContent(state.currentSection, currentContent);

    // Switch to new section
    sectionsManager.switchTo(sectionId);
    state.currentSection = sectionId;

    updateSectionUI(sectionId);
}

/**
 * Update section UI
 */
function updateSectionUI(sectionId: string): void {
    document.querySelectorAll('.section-tab').forEach(tab => {
        tab.classList.toggle('active', (tab as HTMLElement).dataset.section === sectionId);
    });
}

/**
 * Update word count display
 */
function updateWordCountDisplay(section: string, count: number): void {
    const display = document.querySelector(`[data-word-count="${section}"]`);
    if (display) {
        display.textContent = String(count);
    }
}

/**
 * Schedule auto-save
 */
let saveTimeout: ReturnType<typeof setTimeout>;
function scheduleSave(_editor: WriterEditor | null, sectionsManager: SectionsManager, state: any): void {
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(() => {
        saveSections(sectionsManager, state);
    }, 5000); // Auto-save after 5 seconds of inactivity
}

/**
 * Save sections
 */
async function saveSections(sectionsManager: SectionsManager, state: any): Promise<void> {
    try {
        const sections = sectionsManager.getAll();
        const response = await fetch('/writer/api/save-sections/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ sections })
        });

        const data = await response.json();
        if (data.success) {
            state.unsavedSections.clear();
            showToast('Sections saved', 'success');
        } else {
            showToast('Failed to save sections', 'error');
        }
    } catch (error) {
        showToast('Error saving sections', 'error');
    }
}

/**
 * Handle compilation
 */
async function handleCompile(
    _editor: WriterEditor | null,
    sectionsManager: SectionsManager,
    compilationManager: CompilationManager,
    state: any
): Promise<void> {
    if (compilationManager.getIsCompiling()) {
        showToast('Compilation already in progress', 'warning');
        return;
    }

    const config = getWriterConfig();
    const content = sectionsManager.exportCombined();

    const job = await compilationManager.compile({
        projectSlug: config.projectSlug!,
        docType: state.currentDocType,
        content
    });

    if (!job) {
        showToast('Failed to start compilation', 'error');
    }
}

/**
 * Open PDF
 */
function openPDF(url: string): void {
    const pdfWindow = window.open(url, '_blank');
    if (!pdfWindow) {
        const showToast = (window as any).showToast || ((msg: string) => console.warn(msg));
        showToast('Failed to open PDF. Please check popup blocker settings.');
    }
}
