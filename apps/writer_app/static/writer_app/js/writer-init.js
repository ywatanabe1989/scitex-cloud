/**
 * Writer Initialization Module
 * Handles editor initialization, workspace setup, and file loading
 */
import { WriterEditor, EnhancedEditor, SectionsManager, CompilationManager, FileTreeManager, PDFPreviewManager, PanelResizer, EditorControls } from './modules/index.js';
import { PDFScrollZoomHandler } from './modules/pdf-scroll-zoom.js';
import { getCsrfToken } from '@/utils/csrf.js';
import { writerStorage } from '@/utils/storage.js';
import { getWriterConfig, createDefaultEditorState } from './helpers.js';
import { switchSection, handleDocTypeSwitch } from './writer-sections.js';
import { setupEditorListeners, setupSectionListeners } from './writer-events.js';
import { setupCompilationListeners } from './writer-compilation.js';
import { setupThemeListener, setupKeybindingListener, setupSidebarButtons, showToast } from './writer-ui.js';
import { setupPDFZoomControls } from './writer-pdf.js';

/**
 * Wait for Monaco to load asynchronously
 */
export async function waitForMonaco(maxWaitMs = 10000) {
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
export async function loadTexFile(filePath, editor) {
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
export async function populateSectionDropdownDirect(docType = 'manuscript', onFileSelectCallback = null) {
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
export function setupPDFScrollPriority() {
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
 * Setup workspace initialization button
 */
export function setupWorkspaceInitialization(config) {
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
export async function initializeEditor(config) {
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
                        handleDocTypeSwitch(editor, sectionsManager, state, newDocType, pdfPreviewManager);
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
