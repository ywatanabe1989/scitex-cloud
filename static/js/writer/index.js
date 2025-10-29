/**
 * SciTeX Writer Application
 * Main entry point for the writer interface
 *
 * This module coordinates all writer modules:
 * - WriterEditor: CodeMirror editor management
 * - SectionsManager: Section and document structure management
 * - CompilationManager: LaTeX compilation and PDF management
 */
import { WriterEditor, EnhancedEditor, SectionsManager, CompilationManager, FileTreeManager, PDFPreviewManager, PanelResizer, EditorControls } from './modules/index.js';
import { getCsrfToken } from '@/utils/csrf.js';
import { writerStorage } from '@/utils/storage.js';
import { getWriterConfig, createDefaultEditorState } from './helpers.js';
/**
 * Show toast notification
 */
function showToast(message, _type = 'info') {
    const fn = window.showToast || ((msg) => console.log(msg));
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
function setupWorkspaceInitialization(config) {
    const initBtn = document.getElementById('init-writer-btn');
    if (!initBtn)
        return;
    // Setup project selector
    const repoSelector = document.getElementById('repository-selector');
    if (repoSelector) {
        repoSelector.addEventListener('change', (e) => {
            const target = e.target;
            const projectId = target.value;
            if (projectId) {
                // Redirect to the selected project's writer page
                window.location.href = `/writer/project/${projectId}/`;
            }
        });
    }
    initBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        // Validate project exists
        if (!config.projectId) {
            showToast('Error: No project selected. Please select or create a project first.', 'error');
            initBtn.removeAttribute('disabled');
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
                    project_id: config.projectId
                })
            });
            const data = await response.json();
            if (response.ok && data.success) {
                showToast('Workspace initialized successfully', 'success');
                // Small delay before reload to let user see success message
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            }
            else {
                showToast('Failed to initialize workspace: ' + (data.error || 'Unknown error'), 'error');
                initBtn.removeAttribute('disabled');
                initBtn.innerHTML = '<i class="fas fa-rocket me-2"></i>Create Workspace';
            }
        }
        catch (error) {
            showToast('Error: ' + (error instanceof Error ? error.message : 'Unknown error'), 'error');
            initBtn.removeAttribute('disabled');
            initBtn.innerHTML = '<i class="fas fa-rocket me-2"></i>Create Workspace';
        }
    });
}
/**
 * Initialize editor and its components
 */
function initializeEditor(config) {
    console.log('[Writer] Setting up editor components');
    // Initialize editor (try Monaco first, fallback to CodeMirror)
    let editor = null;
    try {
        editor = new EnhancedEditor({
            elementId: 'latex-editor-textarea',
            mode: 'text/x-latex',
            theme: 'default',
            useMonaco: true
        });
    }
    catch (error) {
        console.error('[Writer] Failed to initialize enhanced editor, trying basic editor:', error);
        try {
            editor = new WriterEditor({
                elementId: 'latex-editor-textarea',
                mode: 'text/x-latex',
                theme: 'default'
            });
        }
        catch (fallbackError) {
            console.error('[Writer] Failed to initialize any editor:', fallbackError);
            showToast('Failed to initialize editor', 'error');
            return;
        }
    }
    // Initialize sections manager
    const sectionsManager = new SectionsManager();
    // Initialize compilation manager
    const compilationManager = new CompilationManager('');
    // Setup state management
    const state = createDefaultEditorState();
    // Initialize PDF preview manager
    const pdfPreviewManager = new PDFPreviewManager({
        containerId: 'text-preview',
        projectId: config.projectId || 0,
        manuscriptTitle: config.manuscriptTitle || 'Untitled',
        author: config.username || '',
        autoCompile: true,
        compileDelay: 2000, // 2 seconds delay for live preview
        apiBaseUrl: '',
        docType: state.currentDocType || 'manuscript'
    });
    // Initialize panel resizer for draggable split view
    const panelResizer = new PanelResizer();
    if (!panelResizer.isInitialized()) {
        console.warn('[Writer] Panel resizer could not be initialized');
    }
    // Initialize editor controls (font size, auto-preview, preview button)
    // @ts-ignore - editorControls is initialized and manages its own event listeners
    const editorControls = new EditorControls({
        pdfPreviewManager: pdfPreviewManager,
        compilationManager: compilationManager
    });
    // Initialize file tree if project exists
    if (config.projectId) {
        const fileTreeContainer = document.getElementById('tex-files-list');
        if (fileTreeContainer) {
            const fileTreeManager = new FileTreeManager({
                projectId: config.projectId,
                container: fileTreeContainer,
                texFileDropdownId: 'texfile-selector',
                onFileSelect: (sectionId, sectionName) => {
                    console.log('[Writer] Section selected from dropdown:', sectionName);
                    // Switch to the selected section
                    switchSection(editor, sectionsManager, state, sectionId);
                }
            });
            // Load file tree
            fileTreeManager.load().catch((error) => {
                console.warn('[Writer] Failed to load file tree:', error);
            });
            // Setup refresh button
            const refreshBtn = document.getElementById('refresh-files-btn');
            if (refreshBtn) {
                refreshBtn.addEventListener('click', () => {
                    fileTreeManager.refresh();
                });
            }
            // Listen to document type changes
            const docTypeSelector = document.getElementById('doctype-selector');
            if (docTypeSelector) {
                docTypeSelector.addEventListener('change', (e) => {
                    const newDocType = e.target.value;
                    console.log('[Writer] Document type changed to:', newDocType);
                    if (editor && state.currentSection) {
                        // Save current section before switching
                        const currentContent = editor.getContent();
                        sectionsManager.setContent(state.currentSection, currentContent);
                        // Update state with new document type
                        state.currentDocType = newDocType;
                        // Update section dropdown for the new document type
                        fileTreeManager.updateForDocType(newDocType);
                        // Update PDF preview manager to use the new document type
                        pdfPreviewManager.setDocType(newDocType);
                        // Switch to first section of the new document type
                        handleDocTypeSwitch(editor, sectionsManager, state, newDocType);
                    }
                });
            }
        }
    }
    // Setup event listeners
    if (editor) {
        setupEditorListeners(editor, sectionsManager, compilationManager, state, pdfPreviewManager);
        setupSectionListeners(sectionsManager, editor, state, writerStorage);
    }
    setupCompilationListeners(compilationManager, config);
    setupThemeListener();
    setupSidebarButtons(config);
    // Display PDF preview placeholder
    pdfPreviewManager.displayPlaceholder();
    // Load initial content
    const currentSection = state.currentSection || 'abstract';
    const content = sectionsManager.getContent(currentSection);
    if (editor && content) {
        editor.setContent(content);
    }
    // Show only split view - all views are split by default in HTML
    document.querySelectorAll('.editor-view').forEach((view) => {
        view.classList.add('active');
    });
    console.log('[Writer] Editor initialized successfully');
    console.log('[Writer] Using editor type:', editor?.getEditorType?.() || 'CodeMirror');
}
/**
 * Sync dropdown selection with current section
 */
function syncDropdownToSection(sectionId) {
    const dropdown = document.getElementById('texfile-selector');
    if (dropdown) {
        dropdown.value = sectionId;
    }
}
/**
 * Handle document type switch
 */
function handleDocTypeSwitch(editor, sectionsManager, state, newDocType) {
    // Map of first section for each document type
    const firstSectionByDocType = {
        'manuscript': 'abstract',
        'supplementary': 'content',
        'revision': 'response',
        'shared': '' // No sections for shared type
    };
    const firstSection = firstSectionByDocType[newDocType] || 'abstract';
    if (!firstSection) {
        console.warn('[Writer] No sections available for document type:', newDocType);
        console.log('[Writer] Keeping current section:', state.currentSection);
        // Don't switch sections if document type has no sections
        return;
    }
    // Switch to the first section of the new document type
    console.log('[Writer] Switching to', firstSection, 'for', newDocType);
    switchSection(editor, sectionsManager, state, firstSection);
}
/**
 * Setup editor event listeners
 */
function setupEditorListeners(editor, sectionsManager, compilationManager, state, pdfPreviewManager) {
    if (!editor)
        return;
    // Track changes
    editor.onChange((content, wordCount) => {
        const currentSection = state.currentSection;
        sectionsManager.setContent(currentSection, content);
        state.unsavedSections.add(currentSection);
        // Update word count display
        updateWordCountDisplay(currentSection, wordCount);
        // Schedule auto-save
        scheduleSave(editor, sectionsManager, state);
        // Schedule auto-compile for live PDF preview
        if (pdfPreviewManager) {
            scheduleAutoCompile(pdfPreviewManager, content);
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
    // Setup compile button
    const compileBtn = document.getElementById('compile-btn-toolbar');
    if (compileBtn) {
        compileBtn.addEventListener('click', () => {
            handleCompile(editor, sectionsManager, compilationManager, state, pdfPreviewManager);
        });
    }
}
/**
 * Setup section listeners
 */
function setupSectionListeners(sectionsManager, editor, state, _storage) {
    const sectionItems = document.querySelectorAll('.section-tab');
    sectionItems.forEach(item => {
        item.addEventListener('click', (e) => {
            const target = e.target;
            const sectionId = target.dataset.section;
            if (sectionId) {
                switchSection(editor, sectionsManager, state, sectionId);
            }
        });
    });
    // Listen for section changes
    sectionsManager.onSectionChange((sectionId) => {
        const content = sectionsManager.getContent(sectionId);
        editor.setContent(content);
        state.currentSection = sectionId;
        updateSectionUI(sectionId);
    });
}
/**
 * Setup compilation listeners
 */
function setupCompilationListeners(compilationManager, _config) {
    compilationManager.onProgress((progress, status) => {
        const progressBar = document.getElementById('compilation-progress');
        if (progressBar) {
            progressBar.value = String(progress);
        }
        const statusText = document.getElementById('compilation-status');
        if (statusText) {
            statusText.textContent = status;
        }
    });
    compilationManager.onComplete((_jobId, pdfUrl) => {
        const showToast = window.showToast || ((msg) => console.log(msg));
        showToast('Compilation completed successfully');
        if (pdfUrl) {
            openPDF(pdfUrl);
        }
    });
    compilationManager.onError((error) => {
        const showToast = window.showToast || ((msg) => console.error(msg));
        showToast('Compilation error: ' + error);
    });
}
/**
 * Setup theme listener
 */
function setupThemeListener() {
    const themeSelector = document.getElementById('theme-selector');
    if (!themeSelector)
        return;
    themeSelector.addEventListener('change', () => {
        const theme = themeSelector.value;
        document.documentElement.setAttribute('data-theme', theme);
        writerStorage.save('theme', theme);
        // Apply theme to CodeMirror if available
        const cmEditor = document.querySelector('.CodeMirror')?.CodeMirror;
        if (cmEditor) {
            cmEditor.setOption('theme', theme === 'dark' ? 'material-darker' : 'default');
        }
    });
}
/**
 * Switch to a section
 */
function switchSection(editor, sectionsManager, state, sectionId) {
    // Save current section
    const currentContent = editor.getContent();
    sectionsManager.setContent(state.currentSection, currentContent);
    // Switch to new section
    sectionsManager.switchTo(sectionId);
    state.currentSection = sectionId;
    updateSectionUI(sectionId);
    // Sync dropdown to show currently selected section
    syncDropdownToSection(sectionId);
}
/**
 * Update section UI
 */
function updateSectionUI(sectionId) {
    document.querySelectorAll('.section-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.section === sectionId);
    });
}
/**
 * Update word count display
 */
function updateWordCountDisplay(section, count) {
    const display = document.querySelector(`[data-word-count="${section}"]`);
    if (display) {
        display.textContent = String(count);
    }
}
/**
 * Schedule auto-save
 */
let saveTimeout;
function scheduleSave(_editor, sectionsManager, state) {
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(() => {
        saveSections(sectionsManager, state);
    }, 5000); // Auto-save after 5 seconds of inactivity
}
/**
 * Schedule auto-compile for live PDF preview
 */
let compileTimeout;
function scheduleAutoCompile(pdfPreviewManager, content) {
    if (!pdfPreviewManager)
        return;
    // Clear existing timeout
    clearTimeout(compileTimeout);
    // Schedule compilation after user stops typing
    compileTimeout = setTimeout(() => {
        console.log('[Writer] Auto-compiling for live preview');
        pdfPreviewManager.compileQuick(content);
    }, 2000); // Wait 2 seconds after user stops typing
}
/**
 * Save sections
 */
async function saveSections(sectionsManager, state) {
    try {
        // Get project ID from page config
        const config = getWriterConfig();
        if (!config.projectId) {
            console.warn('[Writer] Cannot save sections: no project ID');
            return;
        }
        const allSections = sectionsManager.getAll();
        // Filter out empty sections to avoid unnecessary writes
        const sections = {};
        for (const [name, contentValue] of Object.entries(allSections)) {
            const content = String(contentValue || '');
            if (content.trim().length > 0) {
                sections[name] = content;
            }
        }
        if (Object.keys(sections).length === 0) {
            console.log('[Writer] No non-empty sections to save');
            return;
        }
        console.log(`[Writer] Saving ${Object.keys(sections).length} sections for ${state.currentDocType || 'manuscript'}`);
        const response = await fetch(`/writer/api/project/${config.projectId}/save-sections/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                sections,
                doc_type: state.currentDocType || 'manuscript'
            })
        });
        const data = await response.json();
        if (data.success) {
            state.unsavedSections.clear();
            console.log(`[Writer] Sections saved: ${data.sections_saved} saved, ${data.sections_skipped || 0} skipped`);
            showToast('Sections saved', 'success');
        }
        else {
            const errorMsg = data.error || 'Unknown error';
            console.error('[Writer] Save failed:', errorMsg);
            if (data.traceback) {
                console.error('[Writer] Server traceback:', data.traceback);
            }
            showToast(`Failed to save sections: ${errorMsg}`, 'error');
        }
    }
    catch (error) {
        console.error('[Writer] Error saving sections:', error);
        showToast('Error saving sections', 'error');
    }
}
/**
 * Handle compilation
 */
async function handleCompile(_editor, sectionsManager, _compilationManager, _state, pdfPreviewManager) {
    if (!pdfPreviewManager) {
        showToast('PDF preview not initialized', 'error');
        return;
    }
    if (pdfPreviewManager.isCompiling()) {
        showToast('Compilation already in progress', 'warning');
        return;
    }
    try {
        const sections = sectionsManager.getAll();
        const sectionArray = Object.entries(sections).map(([name, content]) => ({
            name: name.charAt(0).toUpperCase() + name.slice(1),
            content: content
        }));
        showToast('Starting compilation...', 'info');
        await pdfPreviewManager.compile(sectionArray);
    }
    catch (error) {
        showToast('Compilation error: ' + (error instanceof Error ? error.message : 'Unknown error'), 'error');
    }
}
/**
 * Setup sidebar button listeners
 */
function setupSidebarButtons(_config) {
    // Button listeners are set up in their respective initialization functions
    // No additional setup needed here
}
/**
 * Open PDF
 */
function openPDF(url) {
    const pdfWindow = window.open(url, '_blank');
    if (!pdfWindow) {
        const showToast = window.showToast || ((msg) => console.warn(msg));
        showToast('Failed to open PDF. Please check popup blocker settings.');
    }
}
//# sourceMappingURL=index.js.map