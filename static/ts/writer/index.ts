/**
 * SciTeX Writer Application
 * Main entry point for the writer interface
 *
 * This module coordinates all writer modules:
 * - WriterEditor: CodeMirror editor management
 * - SectionsManager: Section and document structure management
 * - CompilationManager: LaTeX compilation and PDF management
 */

import { WriterEditor, SectionsManager, CompilationManager } from './modules/index.js';
import { getCsrfToken } from '@/utils/csrf.js';
import { writerStorage } from '@/utils/storage.js';
import { getWriterConfig, createDefaultEditorState } from './helpers.js';

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
            elementId: 'latex-editor-textarea',
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
    setupSidebarButtons(config);

    // Load initial content
    const currentSection = state.currentSection || 'abstract';
    const content = sectionsManager.getContent(currentSection);
    if (editor && content) {
        editor.setContent(content);
    }

    // Set split view as default
    const splitViewTab = document.getElementById('view-tab-split');
    if (splitViewTab) {
        // Simulate click to activate split view
        splitViewTab.click();
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

    // Setup save button (Ctrl+S keyboard shortcut is handled below)
    // Note: No explicit save button in toolbar - use keyboard shortcut

    // Setup compile button
    const compileBtn = document.getElementById('compile-btn-toolbar');
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
    _sectionsManager: SectionsManager,
    _compilationManager: CompilationManager,
    _state: any
): Promise<void> {
    // TODO: Implement compilation when backend API is ready
    showToast('Compilation feature coming soon', 'info');
}

/**
 * Setup sidebar button listeners
 */
function setupSidebarButtons(config: any): void {
    // Toggle sidebar button
    const toggleSidebarBtn = document.getElementById('toggle-sidebar');
    const sidebar = document.getElementById('writer-sidebar');
    if (toggleSidebarBtn && sidebar) {
        toggleSidebarBtn.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
        });
    }

    // Refresh files button
    const refreshBtn = document.getElementById('refresh-files-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            showToast('Refreshing files...', 'info');
            // TODO: Implement file refresh logic
        });
    }

    // Export button
    const exportBtn = document.getElementById('export-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            showToast('Exporting manuscript...', 'info');
            // TODO: Implement export logic
        });
    }

    // Initialize workspace button (only shown when not initialized)
    const initBtn = document.getElementById('init-writer-btn');
    if (initBtn && !config.writerInitialized && !config.isDemo) {
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
                        'X-CSRFToken': (window as any).WRITER_CONFIG?.csrfToken || ''
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
                    initBtn.innerHTML = '<i class="fas fa-rocket me-2"></i>Create Workspace';
                }
            } catch (error) {
                showToast('Error: ' + (error instanceof Error ? error.message : 'Unknown error'), 'error');
                initBtn.removeAttribute('disabled');
                initBtn.innerHTML = '<i class="fas fa-rocket me-2"></i>Create Workspace';
            }
        });
    }

    // View/editor mode buttons (LaTeX, Preview, Split)
    const viewTabs = document.querySelectorAll('.view-tab');
    viewTabs.forEach((tab) => {
        tab.addEventListener('click', (e: Event) => {
            const target = e.target as HTMLElement;
            const view = target.getAttribute('data-view');
            if (view) {
                // Hide all views
                document.querySelectorAll('.editor-view').forEach((v) => {
                    v.classList.remove('active');
                });
                // Show selected view
                const selectedView = document.getElementById(`editor-view-${view}`);
                if (selectedView) {
                    selectedView.classList.add('active');
                }
                // Update active tab
                viewTabs.forEach((t) => t.classList.remove('active'));
                target.classList.add('active');
            }
        });
    });

    // Sections panel toggle button
    const toggleSectionPanelBtn = document.getElementById('toggle-section-panel');
    const floatingPanel = document.getElementById('floating-section-panel');
    if (toggleSectionPanelBtn && floatingPanel) {
        toggleSectionPanelBtn.addEventListener('click', () => {
            const isHidden = floatingPanel.style.display === 'none';
            floatingPanel.style.display = isHidden ? 'flex' : 'none';
        });
    }

    // Close section panel button
    const closePanelBtn = document.getElementById('close-section-panel');
    if (closePanelBtn && floatingPanel) {
        closePanelBtn.addEventListener('click', () => {
            floatingPanel.style.display = 'none';
        });
    }

    // TODO: View/Toggle PDF Compilation Panel Button - disabled until compilation API is implemented
    // const toggleCompilationPanelBtn = document.getElementById('toggle-compilation-panel');
    // const compilationPanel = document.getElementById('compilation-panel');
    // if (toggleCompilationPanelBtn && compilationPanel) {
    //     toggleCompilationPanelBtn.addEventListener('click', () => {
    //         const isHidden = compilationPanel.style.display === 'none';
    //         compilationPanel.style.display = isHidden ? '' : 'none';
    //     });
    // }
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
