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
import { PDFScrollZoomHandler } from './modules/pdf-scroll-zoom.js';
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
document.addEventListener('DOMContentLoaded', async () => {
    console.log('[Writer] Initializing application');
    const config = getWriterConfig();
    console.log('[Writer] Config:', config);
    // Check if workspace is initialized
    if (!config.writerInitialized && !config.isDemo) {
        console.log('[Writer] Workspace not initialized - skipping editor setup');
        setupWorkspaceInitialization(config);
        return;
    }
    // Initialize editor components (async to wait for Monaco)
    await initializeEditor(config);
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
 * Wait for Monaco to load asynchronously
 */
async function waitForMonaco(maxWaitMs = 10000) {
    const startTime = Date.now();
    console.log('[Writer] Waiting for Monaco to load...');
    while (Date.now() - startTime < maxWaitMs) {
        if (window.monacoLoaded && window.monaco) {
            console.log('[Writer] Monaco loaded successfully');
            return true;
        }
        // Wait 100ms before checking again
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    console.warn('[Writer] Monaco failed to load within timeout, will fallback to CodeMirror');
    return false;
}
/**
 * Load .tex file content from server
 */
async function loadTexFile(filePath, editor) {
    console.log('[Writer] Loading .tex file:', filePath);
    const config = getWriterConfig();
    if (!config.projectId) {
        console.error('[Writer] Cannot load file: no project ID');
        showToast('Cannot load file: no project selected', 'error');
        return;
    }
    try {
        const response = await fetch(`/writer/api/project/${config.projectId}/read-tex-file/?path=${encodeURIComponent(filePath)}`);
        console.log('[Writer] File API response status:', response.status);
        if (!response.ok) {
            const errorText = await response.text();
            console.error('[Writer] Failed to load file:', response.status, errorText);
            showToast(`Failed to load file: ${response.statusText}`, 'error');
            return;
        }
        const data = await response.json();
        console.log('[Writer] File loaded successfully, length:', data.content?.length || 0);
        if (data.success && data.content !== undefined) {
            editor.setContent(data.content);
            console.log('[Writer] File content set in editor');
            showToast(`Loaded: ${filePath}`, 'success');
        }
        else {
            console.error('[Writer] Invalid response format:', data);
            showToast('Failed to load file: invalid response', 'error');
        }
    }
    catch (error) {
        console.error('[Writer] Error loading file:', error);
        showToast('Error loading file: ' + (error instanceof Error ? error.message : 'Unknown error'), 'error');
    }
}
/**
 * Populate section dropdown directly (fallback when FileTreeManager not available)
 */
async function populateSectionDropdownDirect(docType = 'manuscript', onFileSelectCallback = null) {
    console.log('[Writer] Populating section dropdown directly for:', docType);
    const dropdown = document.getElementById('texfile-selector');
    if (!dropdown) {
        console.warn('[Writer] Section dropdown not found');
        return;
    }
    try {
        const response = await fetch('/writer/api/sections-config/');
        const data = await response.json();
        if (!data.success || !data.hierarchy) {
            console.error('[Writer] Failed to load sections hierarchy');
            return;
        }
        const hierarchy = data.hierarchy;
        dropdown.innerHTML = '';
        let sections = [];
        if (docType === 'manuscript' && hierarchy.manuscript) {
            sections = hierarchy.manuscript.sections;
        }
        else if (docType === 'supplementary' && hierarchy.supplementary) {
            sections = hierarchy.supplementary.sections;
        }
        else if (docType === 'revision' && hierarchy.revision) {
            sections = hierarchy.revision.sections;
        }
        if (sections.length === 0) {
            console.warn('[Writer] No sections found for document type:', docType);
            return;
        }
        const optgroup = document.createElement('optgroup');
        optgroup.label = docType.charAt(0).toUpperCase() + docType.slice(1);
        sections.forEach((section) => {
            const option = document.createElement('option');
            option.value = section.id;
            option.textContent = section.label;
            if (section.is_complete) {
                option.dataset.complete = 'true';
            }
            if (section.read_only) {
                option.dataset.readonly = 'true';
            }
            optgroup.appendChild(option);
        });
        dropdown.appendChild(optgroup);
        console.log('[Writer] Dropdown populated with', sections.length, 'sections');
        // Add change event listener if not already attached
        if (!dropdown.dataset.listenerAttached) {
            dropdown.addEventListener('change', (e) => {
                const target = e.target;
                if (target.value && onFileSelectCallback) {
                    const sectionId = target.value;
                    const selectedOption = target.options[target.selectedIndex];
                    const sectionName = selectedOption.textContent || sectionId;
                    console.log('[Writer] Section selected from dropdown:');
                    console.log('  - Display name:', sectionName);
                    console.log('  - Section ID:', sectionId);
                    console.log('  - Selected index:', target.selectedIndex);
                    console.log('  - Option value:', selectedOption.value);
                    console.log('  - Option text:', selectedOption.textContent);
                    // Trigger callback with section info
                    onFileSelectCallback(sectionId, sectionName);
                }
            });
            dropdown.dataset.listenerAttached = 'true';
        }
        // Select first option and trigger selection manually (not via event)
        if (dropdown.options.length > 0 && onFileSelectCallback) {
            dropdown.selectedIndex = 0;
            const firstOption = dropdown.options[0];
            console.log('[Writer] Auto-selecting first section:', firstOption.value);
            onFileSelectCallback(firstOption.value, firstOption.textContent || '');
        }
    }
    catch (error) {
        console.error('[Writer] Error populating dropdown:', error);
    }
}
/**
 * Setup PDF scroll - prevent page scroll when hovering over PDF
 */
function setupPDFScrollPriority() {
    const textPreview = document.getElementById('text-preview');
    if (!textPreview) {
        console.warn('[PDFScroll] text-preview element not found');
        return;
    }
    console.log('[PDFScroll] Setting up smart scroll: PDF priority when hovering');
    // Prevent page scroll when mouse is over PDF area
    textPreview.addEventListener('wheel', (e) => {
        // Check if PDF is loaded (iframe or embed)
        const pdfElement = textPreview.querySelector('iframe[type="application/pdf"], embed[type="application/pdf"]');
        if (pdfElement) {
            // PDF is loaded - prevent page scroll, let PDF viewer handle it
            e.stopPropagation();
            console.log('[PDFScroll] Scroll over PDF - preventing page scroll (PDF handles internally)');
        }
    }, { passive: true, capture: true });
    // Reset scroll position to top when PDF content is loaded
    const observer = new MutationObserver(() => {
        const pdfContainer = textPreview.querySelector('.pdf-preview-container');
        if (pdfContainer) {
            console.log('[PDFScroll] PDF container detected');
            textPreview.scrollTop = 0;
            const pdfViewer = textPreview.querySelector('.pdf-preview-viewer');
            if (pdfViewer) {
                pdfViewer.scrollTop = 0;
            }
            const pdfElement = pdfContainer.querySelector('iframe[type="application/pdf"], embed[type="application/pdf"]');
            if (pdfElement) {
                console.log('[PDFScroll] PDF loaded - smart scrolling enabled');
            }
        }
    });
    observer.observe(textPreview, { childList: true, subtree: true });
    console.log('[PDFScroll] Smart scroll setup complete');
}
/**
 * Initialize editor and its components
 */
async function initializeEditor(config) {
    console.log('[Writer] Setting up editor components');
    // Wait for Monaco to load if attempting to use it
    const monacoReady = await waitForMonaco();
    // Initialize editor (try Monaco first if ready, fallback to CodeMirror)
    let editor = null;
    try {
        editor = new EnhancedEditor({
            elementId: 'latex-editor-textarea',
            mode: 'text/x-latex',
            theme: 'default',
            useMonaco: monacoReady
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
    const state = createDefaultEditorState(config);
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
    // Initialize PDF scroll and zoom handler
    const pdfScrollZoomHandler = new PDFScrollZoomHandler({
        containerId: 'text-preview',
        minZoom: 50,
        maxZoom: 300,
        zoomStep: 10
    });
    // Observe for PDF viewer changes and reinitialize zoom handler
    pdfScrollZoomHandler.observePDFViewer();
    // Connect color mode changes to recompilation
    pdfScrollZoomHandler.onColorModeChange((colorMode) => {
        console.log('[Writer] PDF color mode changed to:', colorMode, '- triggering recompilation');
        pdfPreviewManager.setColorMode(colorMode);
        // Trigger recompilation with new color mode
        const currentContent = editor?.getContent();
        if (currentContent) {
            pdfPreviewManager.compileQuick(currentContent);
        }
    });
    // Setup PDF zoom control buttons
    setupPDFZoomControls(pdfScrollZoomHandler);
    // Initialize panel resizer for draggable split view
    const panelResizer = new PanelResizer();
    if (!panelResizer.isInitialized()) {
        console.warn('[Writer] Panel resizer could not be initialized');
    }
    // Initialize editor controls (font size, auto-preview, preview button)
    // @ts-ignore - editorControls is initialized and manages its own event listeners
    const editorControls = new EditorControls({
        pdfPreviewManager: pdfPreviewManager,
        compilationManager: compilationManager,
        editor: editor
    });
    // Define shared section/file selection callback
    const onFileSelectHandler = (sectionId, sectionName) => {
        console.log('[Writer] File/section selected:', sectionName, 'ID:', sectionId);
        // Check if this is a known section ID pattern or a file path
        // Section IDs follow: {docType}/{sectionName}
        // File paths have .tex extension or are in shared/* directories
        const sectionPattern = /^(manuscript|supplementary|revision)\/(abstract|introduction|methods|results|discussion|content|figures|tables|response|changes|compiled_pdf|compiled_tex)$/;
        const isKnownSection = sectionPattern.test(sectionId);
        if (isKnownSection) {
            // It's a section ID - switch section
            console.log('[Writer] Detected section ID, switching section:', sectionId);
            switchSection(editor, sectionsManager, state, sectionId, pdfPreviewManager);
        }
        else if (sectionId.endsWith('.tex')) {
            // It's a file path - load from disk
            console.log('[Writer] Detected .tex file, loading from disk:', sectionId);
            loadTexFile(sectionId, editor);
        }
        else {
            // Fallback: try as section first, then as file
            console.log('[Writer] Unknown ID format, trying as section:', sectionId);
            switchSection(editor, sectionsManager, state, sectionId, pdfPreviewManager);
        }
    };
    // Initialize file tree (including demo mode with projectId 0)
    if (config.projectId !== null && config.projectId !== undefined) {
        const fileTreeContainer = document.getElementById('tex-files-list');
        if (fileTreeContainer) {
            const fileTreeManager = new FileTreeManager({
                projectId: config.projectId,
                container: fileTreeContainer,
                texFileDropdownId: 'texfile-selector',
                onFileSelect: onFileSelectHandler
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
        else {
            // No file tree container found - populate dropdown directly
            console.log('[Writer] No file tree container, populating dropdown directly');
            populateSectionDropdownDirect('manuscript', onFileSelectHandler);
        }
    }
    else {
        // No projectId - still need to populate dropdown
        console.log('[Writer] No project, populating dropdown for demo mode');
        populateSectionDropdownDirect('manuscript', onFileSelectHandler);
    }
    // Setup event listeners
    if (editor) {
        setupEditorListeners(editor, sectionsManager, compilationManager, state, pdfPreviewManager);
        setupSectionListeners(sectionsManager, editor, state, writerStorage, pdfPreviewManager);
    }
    setupCompilationListeners(compilationManager, config);
    setupThemeListener(editor);
    setupKeybindingListener(editor);
    setupSidebarButtons(config);
    // Setup scroll priority: PDF scrolling takes priority over page scrolling
    setupPDFScrollPriority();
    // Display PDF preview placeholder
    pdfPreviewManager.displayPlaceholder();
    // Load initial content
    const currentSection = state.currentSection || 'manuscript/compiled_pdf';
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
    switchSection(editor, sectionsManager, state, firstSection, pdfPreviewManager);
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
function setupSectionListeners(sectionsManager, editor, state, _storage, pdfPreviewManager) {
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
 * Get current global page theme (light or dark)
 */
function getPageTheme() {
    const theme = document.documentElement.getAttribute('data-theme');
    return theme === 'light' ? 'light' : 'dark';
}
/**
 * Filter theme dropdown options based on page theme
 */
function filterThemeOptions() {
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
function applyCodeEditorTheme(theme, editor) {
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
function setupThemeListener(editor) {
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
function setupKeybindingListener(editor) {
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
 * Load section content from API
 */
async function loadSectionContent(editor, sectionsManager, _state, sectionId) {
    const config = getWriterConfig();
    if (!config.projectId) {
        console.warn('[Writer] Cannot load section content: no project ID');
        return;
    }
    try {
        // Extract section name and doc type from sectionId (e.g., "manuscript/abstract" -> doc_type="manuscript", section_name="abstract")
        const parts = sectionId.split('/');
        if (parts.length !== 2) {
            console.warn('[Writer] Invalid section ID format:', sectionId);
            return;
        }
        const docType = parts[0];
        const sectionName = parts[1];
        console.log('[Writer] Loading section content:', sectionId, 'docType:', docType, 'sectionName:', sectionName);
        const response = await fetch(`/writer/api/project/${config.projectId}/section/${sectionName}/?doc_type=${docType}`);
        if (!response.ok) {
            const error = await response.text();
            console.error('[Writer] Failed to load section:', response.status, error);
            return;
        }
        const data = await response.json();
        console.log('[Writer] API Response for', sectionId, ':', data);
        if (data.success && data.content !== undefined) {
            console.log('[Writer] ✓ Content loaded for:', sectionId, 'length:', data.content.length);
            console.log('[Writer] First 100 chars:', data.content.substring(0, 100));
            sectionsManager.setContent(sectionId, data.content);
            editor.setContent(data.content);
        }
        else {
            const errorMsg = data.error || 'Unknown error loading section';
            console.error('[Writer] ✗ API Error:', errorMsg);
            throw new Error(errorMsg);
        }
    }
    catch (error) {
        console.error('[Writer] Error loading section content:', error);
        throw error; // Re-throw to let caller handle it
    }
}
/**
 * Switch to a section
 */
async function switchSection(editor, sectionsManager, state, sectionId, pdfPreviewManager) {
    // FIRST: Cancel any pending auto-compile from previous section
    clearTimeout(compileTimeout);

    // Save current section
    const currentContent = editor.getContent();
    sectionsManager.setContent(state.currentSection, currentContent);
    // Update current section
    state.currentSection = sectionId;
    console.log('[Writer] Switching to section:', sectionId);
    updateSectionUI(sectionId);
    syncDropdownToSection(sectionId);

    // Render appropriate PDF (compiled or preview)
    render_pdf(sectionId, pdfPreviewManager);

    // For compiled_pdf sections, load the compiled TeX in editor (read-only)
    if (sectionId.endsWith('/compiled_pdf')) {
        console.log('[Writer] Compiled PDF section - loading compiled TeX');
        // Set editor to read-only
        if (typeof editor.setReadOnly === 'function') {
            editor.setReadOnly(true);
        }
        // Load compiled_tex content
        const compiledTexId = sectionId.replace('/compiled_pdf', '/compiled_tex');
        try {
            await loadSectionContent(editor, sectionsManager, state, compiledTexId);
        }
        catch (error) {
            const errorMsg = `Failed to load compiled TeX: ${error}`;
            console.error('[Writer]', errorMsg);
            editor.setContent(`% ERROR: ${errorMsg}\n% Please check browser console for details`);
        }
        return;
    }
    // For regular editable sections
    if (typeof editor.setReadOnly === 'function') {
        editor.setReadOnly(false);
    }
    // Load fresh content from API
    try {
        await loadSectionContent(editor, sectionsManager, state, sectionId);
    }
    catch (error) {
        const errorMsg = `Failed to load section ${sectionId}: ${error}`;
        console.error('[Writer]', errorMsg);
        editor.setContent(`% ERROR: ${errorMsg}\n% Please check browser console for details`);
    }
}
/**
 * Update section UI
 */
function updateSectionUI(sectionId) {
    document.querySelectorAll('.section-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.section === sectionId);
    });
    // Update the section title label in the editor header
    updateSectionTitleLabel(sectionId);
    // Update PDF preview title as well
    updatePDFPreviewTitle(sectionId);
    // Show/hide commit button based on section type (hide for read-only sections)
    updateCommitButtonVisibility(sectionId);
}
/**
 * Render PDF - Central function for PDF display logic
 * Determines whether to show compiled PDF or trigger preview compilation
 *
 * @param {string} sectionId - Section ID (e.g., 'manuscript/compiled_pdf')
 * @param {object} pdfPreviewManager - PDF preview manager instance (unused for compiled_pdf)
 */
function render_pdf(sectionId, pdfPreviewManager) {
    // For compiled_pdf sections: show full manuscript PDF (NO preview compilation)
    if (sectionId.endsWith('/compiled_pdf')) {
        console.log('[Writer] render_pdf: Showing compiled PDF (no preview compilation)');
        loadCompiledPDF(sectionId);
        return;
    }

    // For other sections: preview will be managed by auto-compile on content change
    console.log('[Writer] render_pdf: Editable section, preview managed by auto-compile');
}

/**
 * Load compiled PDF for display (not quick preview)
 */
function loadCompiledPDF(sectionId) {
    const config = getWriterConfig();
    if (!config.projectId)
        return;
    // Extract doc type from sectionId (e.g., "manuscript/compiled_pdf" -> "manuscript")
    const parts = sectionId.split('/');
    const docType = parts[0];
    // Use API endpoint for PDF (avoids X-Frame-Options issues)
    const pdfUrl = `/writer/api/project/${config.projectId}/pdf/?doc_type=${docType}`;
    console.log('[Writer] Loading compiled PDF for section:', sectionId, 'URL:', pdfUrl);
    // Display the PDF directly (bypass quick preview compilation)
    const textPreview = document.getElementById('text-preview');
    if (textPreview) {
        textPreview.innerHTML = `
            <div class="pdf-preview-container">
                <div class="pdf-preview-viewer" id="pdf-viewer-pane">
                    <iframe
                        src="${pdfUrl}#toolbar=0&navpanes=0&scrollbar=1&view=FitW"
                        type="application/pdf"
                        width="100%"
                        height="100%"
                        title="Compiled PDF"
                        frameborder="0">
                    </iframe>
                </div>
            </div>
        `;
    }
}
/**
 * Update the section title label to show current section name with file link
 */
function updateSectionTitleLabel(sectionId) {
    const titleElement = document.getElementById('editor-section-title');
    if (!titleElement)
        return;
    const config = getWriterConfig();
    // Extract section info from sectionId (e.g., "manuscript/abstract")
    const parts = sectionId.split('/');
    const docType = parts[0];
    const sectionName = parts[parts.length - 1];
    // Capitalize and format the section name
    const formattedName = sectionName
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    // Build file path for link
    const docDirMap = {
        'manuscript': '01_manuscript',
        'supplementary': '02_supplementary',
        'revision': '03_revision',
        'shared': 'shared'
    };
    let filePath = '';
    if (sectionName === 'compiled_pdf' || sectionName === 'compiled_tex') {
        // For compiled_pdf, link to the TEX file (since that's what shows in editor)
        // Compiled files are in the root of doc directory
        filePath = `scitex/writer/${docDirMap[docType]}/${docType}.tex`;
    }
    else {
        // Regular sections are in contents/
        const ext = sectionName === 'bibliography' || sectionName === 'references' ? 'bib' : 'tex';
        if (docType === 'shared') {
            filePath = `scitex/writer/shared/${sectionName}.${ext}`;
        }
        else {
            filePath = `scitex/writer/${docDirMap[docType]}/contents/${sectionName}.${ext}`;
        }
    }
    // Create link to project browser
    const fileLink = config.username && config.projectSlug
        ? `/${config.username}/${config.projectSlug}/blob/${filePath}`
        : '';
    if (fileLink) {
        titleElement.innerHTML = `${formattedName} Source <a href="${fileLink}" target="_blank" style="font-size: 0.8em; opacity: 0.7;">📁</a>`;
    }
    else {
        titleElement.textContent = `${formattedName} Source`;
    }
}
/**
 * Update the PDF preview panel title to show current section with link
 */
function updatePDFPreviewTitle(sectionId) {
    const titleElement = document.getElementById('preview-title');
    if (!titleElement)
        return;
    const config = getWriterConfig();
    // Extract section name from sectionId
    const parts = sectionId.split('/');
    const docType = parts[0];
    const sectionName = parts[parts.length - 1];
    // Capitalize and format
    const docTypeLabel = docType.charAt(0).toUpperCase() + docType.slice(1);
    const formattedName = sectionName
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    // Build PDF file link
    let pdfLink = '';
    if (sectionName === 'compiled_pdf' && config.username && config.projectSlug) {
        // Link to compiled PDF
        const docDirMap = {
            'manuscript': '01_manuscript',
            'supplementary': '02_supplementary',
            'revision': '03_revision'
        };
        pdfLink = `/${config.username}/${config.projectSlug}/blob/scitex/writer/${docDirMap[docType]}/${docType}.pdf`;
    }
    else if (config.username && config.projectSlug) {
        // Link to preview PDF
        pdfLink = `/${config.username}/${config.projectSlug}/blob/scitex/writer/preview_output/preview-${sectionName}.pdf`;
    }
    // Special case for compiled_pdf - don't add "PDF" twice
    let titleText = '';
    if (sectionName === 'compiled_pdf') {
        titleText = `${docTypeLabel} PDF`;
    }
    else {
        titleText = `${docTypeLabel} ${formattedName} PDF`;
    }
    // Add link if available
    if (pdfLink) {
        titleElement.innerHTML = `${titleText} <a href="${pdfLink}" target="_blank" style="font-size: 0.8em; opacity: 0.7;">📁</a>`;
    }
    else {
        titleElement.textContent = titleText;
    }
}
/**
 * Update commit button state based on section type and user authentication
 * - Hides button for guest users (Visitor Mode)
 * - Disables button for read-only sections (keeps it visible to reduce surprise)
 */
function updateCommitButtonVisibility(sectionId) {
    const commitBtn = document.getElementById('git-commit-btn');
    if (!commitBtn)
        return;
    const config = window.WRITER_CONFIG;
    // Hide for guest users (projectId === 0 means demo/guest project)
    if (!config || config.projectId === 0) {
        commitBtn.style.display = 'none';
        return;
    }
    // Always show button for authenticated users
    commitBtn.style.display = '';
    // Extract section name from sectionId (e.g., "manuscript/compiled_pdf" -> "compiled_pdf")
    const parts = sectionId.split('/');
    const sectionName = parts[parts.length - 1];
    // Disable button for read-only sections (but keep it visible)
    // compiled_pdf is the merged/compiled document
    // figures, tables, references are directories or view-only sections
    const readOnlySections = ['compiled_pdf', 'figures', 'tables', 'references'];
    const isReadOnly = readOnlySections.includes(sectionName);
    if (isReadOnly) {
        commitBtn.disabled = true;
        commitBtn.title = 'Cannot commit read-only sections';
    }
    else {
        commitBtn.disabled = false;
        commitBtn.title = 'Create git commit for current changes';
    }
}
/**
 * Update word count display
 */
function updateWordCountDisplay(_section, count) {
    const display = document.getElementById('current-word-count');
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
function scheduleAutoCompile(pdfPreviewManager, content, sectionId) {
    if (!pdfPreviewManager)
        return;
    // Clear existing timeout
    clearTimeout(compileTimeout);
    // Schedule compilation after user stops typing
    compileTimeout = setTimeout(() => {
        console.log('[Writer] Auto-compiling for live preview, section:', sectionId);
        // Pass section ID for section-specific preview
        pdfPreviewManager.compileQuick(content, sectionId);
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
/**
 * Handle full manuscript compilation (no content sent - uses workspace)
 */
async function handleCompileFull(compilationManager, state) {
    if (compilationManager.getIsCompiling()) {
        showToast('Compilation already in progress', 'warning');
        return;
    }
    try {
        const projectId = state.projectId;
        if (!projectId) {
            showToast('No project ID found', 'error');
            return;
        }
        showToast('Compiling full manuscript from workspace...', 'info');
        console.log('[Writer] Starting full compilation for project:', projectId);
        const result = await compilationManager.compileFull({
            projectId: projectId,
            docType: 'manuscript'
        });
        if (result && result.status === 'completed') {
            showToast('Manuscript compiled successfully', 'success');
        }
        else {
            showToast('Compilation failed', 'error');
        }
    }
    catch (error) {
        showToast('Compilation error: ' + (error instanceof Error ? error.message : 'Unknown error'), 'error');
    }
}
/**
 * @deprecated Use handleCompileFull instead for compile button
 * Handle preview compilation (sends content - for auto-preview)
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
        showToast('Starting preview compilation...', 'info');
        await pdfPreviewManager.compile(sectionArray);
    }
    catch (error) {
        showToast('Compilation error: ' + (error instanceof Error ? error.message : 'Unknown error'), 'error');
    }
}
/**
 * Show git commit modal
 */
function showCommitModal(state) {
    const currentSection = state.currentSection;
    if (!currentSection) {
        showToast('No section selected', 'warning');
        return;
    }
    // Update current section info in modal
    const sectionInfoEl = document.getElementById('commit-current-section');
    if (sectionInfoEl) {
        const parts = currentSection.split('/');
        const sectionName = parts[parts.length - 1];
        const formattedName = sectionName
            .split('_')
            .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
        sectionInfoEl.textContent = formattedName;
    }
    // Clear previous message
    const messageInput = document.getElementById('commit-message-input');
    if (messageInput) {
        messageInput.value = '';
        messageInput.focus();
    }
    // Show modal using Bootstrap
    const modalEl = document.getElementById('git-commit-modal');
    if (modalEl) {
        const modal = new window.bootstrap.Modal(modalEl);
        modal.show();
    }
}
/**
 * Handle git commit
 */
async function handleGitCommit(state) {
    const currentSection = state.currentSection;
    if (!currentSection) {
        showToast('No section selected', 'warning');
        return;
    }
    const messageInput = document.getElementById('commit-message-input');
    const commitMessage = messageInput?.value.trim();
    if (!commitMessage) {
        showToast('Please enter a commit message', 'warning');
        messageInput?.focus();
        return;
    }
    try {
        // Extract doc type and section name
        const [docType, sectionName] = currentSection.split('/');
        if (!docType || !sectionName) {
            showToast('Invalid section format', 'error');
            return;
        }
        const config = window.WRITER_CONFIG;
        // First, ensure changes are saved to file (auto-save might not have triggered yet)
        console.log('[Writer] Ensuring section is saved before commit...');
        // We need to get the current editor content and save it
        // This will be handled by calling the section write API
        // For now, we'll proceed with commit assuming auto-save has run
        // Call API endpoint to commit
        const response = await fetch(`/writer/api/project/${config.projectId}/section/${sectionName}/commit/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': config.csrfToken
            },
            body: JSON.stringify({
                doc_type: docType,
                message: commitMessage
            })
        });
        if (!response.ok) {
            const errorText = await response.text();
            console.error('[Writer] Commit HTTP error:', response.status, errorText);
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        const data = await response.json();
        console.log('[Writer] Commit response:', data);
        if (data.success) {
            showToast('Changes committed successfully', 'success');
            // Close modal
            const modalEl = document.getElementById('git-commit-modal');
            if (modalEl) {
                const modal = window.bootstrap.Modal.getInstance(modalEl);
                if (modal) {
                    modal.hide();
                }
            }
        }
        else {
            console.error('[Writer] Commit failed:', data);
            throw new Error(data.error || 'Commit failed');
        }
    }
    catch (error) {
        console.error('[Writer] Git commit error:', error);
        showToast('Failed to commit: ' + (error instanceof Error ? error.message : 'Unknown error'), 'error');
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
 * Setup PDF zoom control buttons
 */
function setupPDFZoomControls(pdfScrollZoomHandler) {
    const zoomInBtn = document.getElementById('pdf-zoom-in-btn');
    const zoomOutBtn = document.getElementById('pdf-zoom-out-btn');
    const fitWidthBtn = document.getElementById('pdf-fit-width-btn');
    const resetZoomBtn = document.getElementById('pdf-reset-zoom-btn');
    const colorModeBtn = document.getElementById('pdf-color-mode-btn');
    const zoomControls = document.querySelector('.pdf-zoom-controls');
    if (zoomInBtn) {
        zoomInBtn.addEventListener('click', () => {
            pdfScrollZoomHandler.zoomIn();
        });
    }
    if (zoomOutBtn) {
        zoomOutBtn.addEventListener('click', () => {
            pdfScrollZoomHandler.zoomOut();
        });
    }
    if (fitWidthBtn) {
        fitWidthBtn.addEventListener('click', () => {
            pdfScrollZoomHandler.fitToWidth();
        });
    }
    if (resetZoomBtn) {
        resetZoomBtn.addEventListener('click', () => {
            pdfScrollZoomHandler.resetZoom();
        });
    }
    if (colorModeBtn) {
        colorModeBtn.addEventListener('click', () => {
            pdfScrollZoomHandler.toggleColorMode();
        });
    }
    // Show/hide zoom controls based on PDF presence
    const observer = new MutationObserver(() => {
        const hasPDF = document.querySelector('.pdf-preview-container') !== null;
        if (zoomControls) {
            zoomControls.style.display = hasPDF ? 'flex' : 'none';
        }
    });
    const previewPanel = document.querySelector('.preview-panel');
    if (previewPanel) {
        observer.observe(previewPanel, { childList: true, subtree: true });
    }
    console.log('[Writer] PDF zoom controls initialized');
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
// Export functions to global scope for ES6 module compatibility
window.populateSectionDropdownDirect = populateSectionDropdownDirect;
//# sourceMappingURL=index.js.map
