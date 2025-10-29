function getCsrfToken() {
    // First, try to get from WRITER_CONFIG (set in template)
    if (window.WRITER_CONFIG?.csrfToken) {
        return window.WRITER_CONFIG.csrfToken;
    }

    // Try to get CSRF token from form input
    const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    if (tokenElement) {
        return tokenElement.value;
    }

    // Fallback: try to get from cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return decodeURIComponent(value);
        }
    }

    // If no CSRF token found, return empty string and let Django handle it
    console.warn('[Writer] CSRF token not found in form, config, or cookies');
    return '';
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('[Writer] Initializing project writer interface');
    // Use WRITER_CONFIG object passed from Django template
    const projectId = window.WRITER_CONFIG?.projectId || null;
    const username = window.WRITER_CONFIG?.username || null;
    const projectSlug = window.WRITER_CONFIG?.projectSlug || null;
    const isDemo = window.WRITER_CONFIG?.isDemo || false;
    const isAnonymous = window.WRITER_CONFIG?.isAnonymous || false;
    const writerInitialized = window.WRITER_CONFIG?.writerInitialized || false;
    console.log('[Writer] User:', username, 'Project:', projectSlug, 'Demo:', isDemo, 'Anonymous:', isAnonymous, 'Initialized:', writerInitialized);

    // Handle writer workspace initialization
    const initWriterBtn = document.getElementById('init-writer-btn');
    console.log('[Writer Init] Looking for init-writer-btn button...', initWriterBtn);

    if (initWriterBtn) {
        console.log('[Writer Init] ✓ Button found, adding click listener');
        console.log('[Writer Init] Project available:', username, '/', projectSlug);

        initWriterBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('[Writer Init] ✓ Button clicked!');
            console.log('[Writer Init] Project:', username, '/', projectSlug);

            if (!projectSlug) {
                console.error('[Writer Init] ✗ No project selected');
                alert('Error: No project selected');
                return;
            }

            // For guest users, username will be null - that's ok
            if (!username) {
                console.log('[Writer Init] Guest user (username is null), using project slug only');
            }

            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Creating workspace...';
            console.log('[Writer Init] Sending POST to /writer/api/initialize-workspace/');

            fetch(`/writer/api/initialize-workspace/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    username: username,
                    project_slug: projectSlug
                })
            })
            .then(response => {
                console.log('[Writer Init] Response status:', response.status);
                if (!response.ok) {
                    console.error('[Writer Init] ✗ HTTP error:', response.status);
                }
                return response.json();
            })
            .then(data => {
                console.log('[Writer Init] Response data:', data);
                if (data.success) {
                    console.log('[Writer Init] ✓ Workspace initialized successfully');
                    console.log('[Writer Init] Reloading page...');
                    window.location.reload();
                } else {
                    console.error('[Writer Init] ✗ Initialization failed:', data.error);
                    alert('Failed to initialize workspace: ' + (data.error || 'Unknown error'));
                    this.disabled = false;
                    this.innerHTML = '<i class="fas fa-rocket me-2"></i>Create';
                }
            })
            .catch(error => {
                console.error('[Writer Init] ✗ Fetch error:', error);
                alert('Error initializing workspace: ' + error.message);
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-rocket me-2"></i>Create';
            });
        });

        console.log('[Writer Init] ✓ Click listener attached successfully');
    } else {
        console.warn('[Writer Init] ⚠ init-writer-btn button not found in DOM');
    }

    // Skip editor initialization if not initialized yet
    if (!writerInitialized && !isDemo) {
        console.log('[Writer] Workspace not initialized - skipping editor setup');
        return;
    }

    let currentSection = 'abstract';
    let currentDocType = 'manuscript';
    let liveCompileTimeout;
    let currentlyCompiling = false;
    let liveCompilationEnabled = true; // Enable live compilation by default

    // Server-provided word counts (from database)
    const serverWordCounts = {
        manuscript: window.WRITER_CONFIG?.wordCounts || {
            abstract: 0,
            introduction: 0,
            methods: 0,
            results: 0,
            discussion: 0
        }
    };

    // Undo/Redo History - Store last 30 save points per section
    const MAX_HISTORY = 30;
    let undoHistory = {}; // { section: [{content, timestamp, wordCount}] }
    let currentHistoryIndex = {}; // { section: index }

    function initializeHistory(section) {
        if (!undoHistory[section]) {
            undoHistory[section] = [];
            currentHistoryIndex[section] = -1;
        }
    }

    function addToHistory(section, content, wordCount) {
        initializeHistory(section);

        // Remove any "future" history if we're in the middle of undo stack
        if (currentHistoryIndex[section] < undoHistory[section].length - 1) {
            undoHistory[section] = undoHistory[section].slice(0, currentHistoryIndex[section] + 1);
        }

        // Add new save point
        undoHistory[section].push({
            content: content,
            timestamp: new Date().toISOString(),
            wordCount: wordCount
        });

        // Keep only last 30 save points
        if (undoHistory[section].length > MAX_HISTORY) {
            undoHistory[section].shift();
        } else {
            currentHistoryIndex[section]++;
        }

        // Persist to localStorage
        saveHistoryToLocalStorage();
        updateUndoRedoButtons();
    }

    function undo() {
        const section = currentSection;
        initializeHistory(section);

        if (currentHistoryIndex[section] > 0) {
            currentHistoryIndex[section]--;
            const historyPoint = undoHistory[section][currentHistoryIndex[section]];

            // Temporarily disable change tracking to avoid triggering markAsUnsaved
            const tempContent = historyPoint.content;
            codeMirrorEditor.setValue(tempContent);

            // Update preview and word count
            const textContent = convertFromLatex(section, tempContent);
            textPreview.textContent = textContent;
            updateWordCount();

            // Mark as saved since we're restoring a saved state
            markAsSaved(section);

            updateUndoRedoButtons();
            showToast(`Restored to ${new Date(historyPoint.timestamp).toLocaleTimeString()}`, 'info');
        }
    }

    function redo() {
        const section = currentSection;
        initializeHistory(section);

        if (currentHistoryIndex[section] < undoHistory[section].length - 1) {
            currentHistoryIndex[section]++;
            const historyPoint = undoHistory[section][currentHistoryIndex[section]];

            // Temporarily disable change tracking to avoid triggering markAsUnsaved
            const tempContent = historyPoint.content;
            codeMirrorEditor.setValue(tempContent);

            // Update preview and word count
            const textContent = convertFromLatex(section, tempContent);
            textPreview.textContent = textContent;
            updateWordCount();

            // Mark as saved since we're restoring a saved state
            markAsSaved(section);

            updateUndoRedoButtons();
            showToast(`Restored to ${new Date(historyPoint.timestamp).toLocaleTimeString()}`, 'info');
        }
    }

    function updateUndoRedoButtons() {
        const section = currentSection;
        initializeHistory(section);

        const undoBtn = document.getElementById('undo-btn');
        const redoBtn = document.getElementById('redo-btn');

        if (undoBtn) {
            undoBtn.disabled = currentHistoryIndex[section] <= 0;
        }
        if (redoBtn) {
            redoBtn.disabled = currentHistoryIndex[section] >= undoHistory[section].length - 1;
        }
    }

    function saveHistoryToLocalStorage() {
        try {
            localStorage.setItem(`history_${projectId}`, JSON.stringify({
                undoHistory: undoHistory,
                currentHistoryIndex: currentHistoryIndex
            }));
        } catch (e) {
            console.warn('Failed to save history to localStorage:', e);
        }
    }

    function loadHistoryFromLocalStorage() {
        try {
            const saved = localStorage.getItem(`history_${projectId}`);
            if (saved) {
                const data = JSON.parse(saved);
                undoHistory = data.undoHistory || {};
                currentHistoryIndex = data.currentHistoryIndex || {};
                updateUndoRedoButtons();
            }
        } catch (e) {
            console.warn('Failed to load history from localStorage:', e);
        }
    }

    // All available sections by document type (pool)
    const allAvailableSections = {
        shared: ['title', 'authors', 'keywords', 'journal_name'],
        manuscript: ['abstract', 'highlights', 'introduction', 'methods', 'results', 'discussion', 'conclusion', 'figures', 'tables'],
        supplementary: ['methods', 'results', 'figures', 'tables', 'references'],
        revision: ['introduction', 'editor', 'reviewer1', 'reviewer2', 'conclusion']
    };

    // Active sections per document type
    let activeSections = {
        shared: ['title', 'authors', 'keywords', 'journal_name'],
        manuscript: ['abstract', 'introduction', 'methods', 'results', 'discussion'],
        supplementary: ['methods', 'results'],
        revision: ['introduction', 'editor', 'reviewer1', 'reviewer2', 'conclusion']
    };

    // Section data by document type
    const sectionsData = {
        shared: {
            title: '',
            authors: '',
            keywords: '',
            journal_name: ''
        },
        manuscript: {
            abstract: window.WRITER_CONFIG?.sections?.abstract || '',
            highlights: window.WRITER_CONFIG?.sections?.highlights || '',
            introduction: window.WRITER_CONFIG?.sections?.introduction || '',
            methods: window.WRITER_CONFIG?.sections?.methods || '',
            results: window.WRITER_CONFIG?.sections?.results || '',
            discussion: window.WRITER_CONFIG?.sections?.discussion || '',
            conclusion: window.WRITER_CONFIG?.sections?.conclusion || '',
            figures: '',
            tables: ''
        },
        supplementary: {
            methods: '',
            results: '',
            figures: '',
            tables: '',
            references: ''
        },
        revision: {
            introduction: '',
            editor: '',
            reviewer1: '',
            reviewer2: '',
            conclusion: ''
        }
    };

    // Section titles by document type
    const sectionTitles = {
        shared: {
            title: 'Manuscript Title',
            authors: 'Authors',
            keywords: 'Keywords',
            journal_name: 'Target Journal'
        },
        manuscript: {
            abstract: 'Abstract',
            highlights: 'Highlights',
            introduction: 'Introduction',
            methods: 'Methods',
            results: 'Results',
            discussion: 'Discussion',
            conclusion: 'Conclusion',
            figures: 'Figures',
            tables: 'Tables'
        },
        supplementary: {
            methods: 'Supplementary Methods',
            results: 'Supplementary Results',
            figures: 'Supplementary Figures',
            tables: 'Supplementary Tables',
            references: 'Supplementary References'
        },
        revision: {
            introduction: 'Introduction',
            editor: 'Editor Comments',
            reviewer1: 'Reviewer #1',
            reviewer2: 'Reviewer #2',
            conclusion: 'Conclusion'
        }
    };

    // Section placeholders by document type
    const sectionPlaceholders = {
        shared: {
            title: 'Enter the full title of your manuscript',
            authors: 'List all authors with their affiliations in LaTeX format (e.g., \\author{First Author\\inst{1}, Second Author\\inst{2}})',
            keywords: 'Enter 3-7 keywords separated by commas',
            journal_name: 'Enter the target journal name (e.g., Nature Neuroscience, Science, Cell)'
        },
        manuscript: {
            abstract: 'Write a concise summary of your research objectives, methods, key findings, and conclusions. Typically 150-300 words.',
            highlights: 'List 3-5 key bullet points highlighting the main contributions and novel findings of your research.',
            introduction: 'Provide background context, literature review, and clearly state your research question or hypothesis.',
            methods: 'Describe your experimental design, data collection methods, and analytical approaches in sufficient detail for replication.',
            results: 'Present your findings objectively with appropriate statistical analysis. Use figures and tables to support key results.',
            discussion: 'Interpret your results, discuss limitations, compare with existing literature, and suggest future research directions.',
            conclusion: 'Summarize key findings and their broader implications.',
            figures: 'Figure captions and descriptions for main manuscript figures.',
            tables: 'Table captions and data for main manuscript tables.'
        },
        supplementary: {
            methods: 'Additional methodological details not included in the main manuscript.',
            results: 'Extended results, additional figures, and supporting data.',
            figures: 'Supplementary figure captions and descriptions.',
            tables: 'Supplementary table captions and data.',
            references: 'Complete bibliography for supplementary material.'
        },
        revision: {
            introduction: 'Brief introduction to the revision letter.',
            editor: 'Editor comments/responses (managed as comment-response pairs in subdirectory)',
            reviewer1: 'Reviewer #1 comments/responses (managed as R1_XX_comments.tex, R1_XX_response.tex, R1_XX_revision.tex)',
            reviewer2: 'Reviewer #2 comments/responses (managed as R2_XX_comments.tex, R2_XX_response.tex, R2_XX_revision.tex)',
            conclusion: 'Summary of key revisions and improvements made.'
        }
    };

    // Initialize CodeMirror editor
    let codeMirrorEditor = null;
    const latexEditorTextarea = document.getElementById('latex-editor-textarea');
    const textPreview = document.getElementById('text-preview');

    // Load saved theme preferences for each mode
    const savedDarkTheme = localStorage.getItem(`codemirror_theme_dark_${projectId}`) || 'dracula';
    const savedLightTheme = localStorage.getItem(`codemirror_theme_light_${projectId}`) || 'neat';

    // Determine current site theme
    const currentSiteTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const initialTheme = currentSiteTheme === 'dark' ? savedDarkTheme : savedLightTheme;

    // Create CodeMirror instance
    codeMirrorEditor = CodeMirror.fromTextArea(latexEditorTextarea, {
        mode: 'stex',
        theme: initialTheme,
        lineNumbers: true,
        lineWrapping: true,
        indentUnit: 2,
        tabSize: 2,
        indentWithTabs: false,
        autofocus: true,
        styleActiveLine: true
    });
    const saveBtn = document.getElementById('save-btn');
    const compileBtn = document.getElementById('compile-btn');
    const liveCompileToggle = document.getElementById('live-compile-toggle');
    const exportBtn = document.getElementById('export-btn');
    const saveStatus = document.getElementById('save-status');
    const currentWordCount = document.getElementById('current-word-count');
    const doctypeSelector = document.getElementById('doctype-selector');
    const themeSelector = document.getElementById('theme-selector');

    // Set theme selector to current theme
    if (themeSelector) {
        themeSelector.value = initialTheme;
    }

    // Theme switcher - save preference per light/dark mode
    if (themeSelector) {
        themeSelector.addEventListener('change', function() {
            const newTheme = this.value;
            const currentSiteTheme = document.documentElement.getAttribute('data-theme') || 'light';

            codeMirrorEditor.setOption('theme', newTheme);

            // Save theme preference for current mode (light or dark)
            if (currentSiteTheme === 'dark') {
                localStorage.setItem(`codemirror_theme_dark_${projectId}`, newTheme);
            } else {
                localStorage.setItem(`codemirror_theme_light_${projectId}`, newTheme);
            }
        });
    }

    // Update theme selector options based on current mode
    function updateThemeSelectorOptions() {
        if (!themeSelector) return;

        const currentSiteTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const isDarkMode = currentSiteTheme === 'dark';

        // Show/hide optgroups based on mode
        const darkGroup = themeSelector.querySelector('optgroup[label="Dark Themes"]');
        const lightGroup = themeSelector.querySelector('optgroup[label="Light Themes"]');

        if (isDarkMode && darkGroup && lightGroup) {
            darkGroup.style.display = '';
            lightGroup.style.display = 'none';
        } else if (darkGroup && lightGroup) {
            darkGroup.style.display = 'none';
            lightGroup.style.display = '';
        }
    }

    // Initial update
    updateThemeSelectorOptions();

    // Listen for site theme changes and switch CodeMirror theme accordingly
    const themeObserver = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.attributeName === 'data-theme') {
                const newSiteTheme = document.documentElement.getAttribute('data-theme') || 'light';

                // Get current saved preference for this mode
                const preferredTheme = newSiteTheme === 'dark'
                    ? localStorage.getItem(`codemirror_theme_dark_${projectId}`) || 'zenburn'
                    : localStorage.getItem(`codemirror_theme_light_${projectId}`) || 'eclipse';

                codeMirrorEditor.setOption('theme', preferredTheme);
                if (themeSelector) {
                    themeSelector.value = preferredTheme;
                }

                // Update dropdown options
                updateThemeSelectorOptions();

                console.log(`Site theme changed to ${newSiteTheme}, CodeMirror theme: ${preferredTheme}`);
            }
        });
    });

    // Observe data-theme attribute changes on <html>
    themeObserver.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-theme']
    });
    const sectionsTitle = document.getElementById('sections-title');
    const sectionList = document.querySelector('.section-list');
    const manageSectionsBtn = document.getElementById('manage-sections-btn');
    const sectionPool = document.getElementById('section-pool');
    const availableSectionsContainer = document.getElementById('available-sections');
    const sectionTitleLatex = document.getElementById('section-title-latex');
    const sectionTitlePreview = document.getElementById('section-title-preview');
    const compilationProgress = document.getElementById('compilation-progress');
    const progressBar = document.getElementById('progress-bar');
    const compilationLog = document.getElementById('compilation-log');
    const pdfViewerContainer = document.getElementById('pdf-viewer-container');
    const pdfViewer = document.getElementById('pdf-viewer');
    const pdfViewLink = document.getElementById('pdf-view-link');
    const pdfDownloadLink = document.getElementById('pdf-download-link');
    const diffPdfViewer = document.getElementById('diff-pdf-viewer');
    const diffPdfViewLink = document.getElementById('diff-pdf-view-link');
    const diffPdfDownloadLink = document.getElementById('diff-pdf-download-link');
    const mainPdfContainer = document.getElementById('main-pdf-container');
    const diffPdfContainer = document.getElementById('diff-pdf-container');
    const showMainPdfBtn = document.getElementById('show-main-pdf');
    const showDiffPdfBtn = document.getElementById('show-diff-pdf');

    // Debug: Log which elements are null
    console.log('[Writer] Element check:', {
        sectionList: !!sectionList,
        manageSectionsBtn: !!manageSectionsBtn,
        sectionPool: !!sectionPool,
        sectionTitleLatex: !!sectionTitleLatex,
        sectionTitlePreview: !!sectionTitlePreview
    });

    let hasUnsavedChanges = false;
    let logExpanded = false;
    let hasDiffPdf = false;
    let mainPdfDoc = null;
    let diffPdfDoc = null;
    let compilationStartTime = null;
    let timerInterval = null;

    // Load state from localStorage
    function loadState() {
        const savedState = localStorage.getItem(`writer_state_${projectId}`);
        if (savedState) {
            try {
                const state = JSON.parse(savedState);
                if (state.activeSections) {
                    activeSections = state.activeSections;
                }
                if (state.currentDocType) {
                    currentDocType = state.currentDocType;
                    doctypeSelector.value = currentDocType;
                }
                if (state.currentSection && activeSections[currentDocType].includes(state.currentSection)) {
                    currentSection = state.currentSection;
                } else {
                    currentSection = activeSections[currentDocType][0];
                }
            } catch (e) {
                console.error('Error loading state:', e);
            }
        }
    }

    // Save state to localStorage
    function saveState() {
        const state = {
            activeSections: activeSections,
            currentDocType: currentDocType,
            currentSection: currentSection
        };
        localStorage.setItem(`writer_state_${projectId}`, JSON.stringify(state));
    }

    // Initialize
    console.log('[Writer] Starting initialization...');
    loadState();
    console.log('[Writer] State loaded, rendering sections for:', currentDocType);
    renderSections(currentDocType);
    console.log('[Writer] Sections rendered, loading word counts');
    loadAllWordCountsFromLocalStorage(); // Load cached word counts from localStorage
    loadHistoryFromLocalStorage(); // Load undo/redo history
    console.log('[Writer] Loading section:', currentSection);
    loadLatexSection(currentSection);
    updateWordCount();
    console.log('[Writer] Initialization complete');

    // Setup compilation panel toggle (after DOM is ready)
    setupCompilationPanelToggle();

    // Undo/Redo button event listeners
    const undoBtn = document.getElementById('undo-btn');
    const redoBtn = document.getElementById('redo-btn');
    if (undoBtn) undoBtn.addEventListener('click', undo);
    if (redoBtn) redoBtn.addEventListener('click', redo);

    // Keyboard shortcuts for undo/redo
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
            e.preventDefault();
            undo();
        } else if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
            e.preventDefault();
            redo();
        }
    });

    // Repository switching (dropdown)
    const repositorySelector = document.getElementById('repository-selector');
    if (repositorySelector) {
        repositorySelector.addEventListener('change', function() {
            const newProjectId = this.value;
            const currentUsername = window.WRITER_CONFIG?.username || 'user';
            // Redirect to the new project's writer page
            window.location.href = `/${currentUsername}/${newProjectId}/?mode=writer`;
        });
    }

    // Document type switching (dropdown)
    if (doctypeSelector) {
        doctypeSelector.addEventListener('change', function() {
            const newDocType = this.value;
            switchDocumentType(newDocType);
        });
    }

    // Manage sections toggle
    if (manageSectionsBtn) {
        manageSectionsBtn.addEventListener('click', function() {
            const isVisible = sectionPool.style.display !== 'none';
            sectionPool.style.display = isVisible ? 'none' : 'block';
            if (!isVisible) {
                renderAvailableSections();
            }
        });
    }

    // Manual save button
    if (saveBtn) {
        saveBtn.addEventListener('click', function() {
            saveCurrentSectionManually();
        });
    }

    // Section switching (delegated event listener)
    if (sectionList) {
        sectionList.addEventListener('click', function(e) {
            const sectionItem = e.target.closest('.section-item');
            if (sectionItem && !e.target.closest('.section-remove-btn')) {
                const section = sectionItem.dataset.section;

                // If we are viewing compilation panel, switch back to editor first
                const compilationOutput = document.getElementById('compilation-output');
                const editorContentWrapper = document.getElementById('editor-content-wrapper') || document.querySelector('.editor-content-wrapper');
                const toggleCompilationBtn = document.getElementById('toggle-compilation-panel');

                if (compilationOutput && compilationOutput.style.display !== 'none') {
                    // Switch back to editor
                    editorContentWrapper.style.display = 'flex';
                    compilationOutput.style.display = 'none';
                    toggleCompilationBtn.innerHTML = '<i class="fas fa-file-pdf me-2"></i>View PDF';
                    toggleCompilationBtn.classList.remove('btn-info');
                    toggleCompilationBtn.classList.add('btn-primary');
                }

                if (section !== currentSection) {
                    // Warn if there are unsaved changes
                    if (hasUnsavedChanges) {
                        if (!confirm(`You have unsaved changes in ${sectionTitles[currentDocType][currentSection]}. Switch anyway? (Changes will be lost)`)) {
                            return;
                        }
                    }

                    // Switch to new section
                    switchToSection(section);
                }
            }
        });
    } else {
        console.error('[Writer] sectionList element not found!');
    }

    // Update preview and mark as unsaved on CodeMirror change
    codeMirrorEditor.on('change', function(editor) {
        // Update preview in real-time
        const latexContent = editor.getValue();
        const textContent = convertFromLatex(currentSection, latexContent);
        textPreview.textContent = textContent;

        // Update word count
        updateWordCount();

        // For demo mode, save to sectionsData immediately
        if (isDemo || !projectId) {
            sectionsData[currentDocType][currentSection] = latexContent;
            console.log('[Writer] Saved to sectionsData:', currentSection);
        }

        // Mark as unsaved
        markAsUnsaved();
    });

    // Compile manuscript
    if (compileBtn) {
        compileBtn.addEventListener('click', function() {
            if (hasUnsavedChanges) {
                if (confirm('You have unsaved changes. Save before compiling?')) {
                    saveCurrentSectionManually();
                    // Wait a moment for save to complete before compiling
                    setTimeout(() => compileManuscript(), 500);
                } else {
                    compileManuscript();
                }
            } else {
                compileManuscript();
            }
        });
    }

    // Live compilation toggle
    if (liveCompileToggle) {
        liveCompileToggle.addEventListener('click', function() {
            liveCompilationEnabled = !liveCompilationEnabled;
            this.classList.toggle('active', liveCompilationEnabled);
            this.classList.toggle('btn-outline-success', liveCompilationEnabled);
            this.classList.toggle('btn-outline-secondary', !liveCompilationEnabled);

            if (liveCompilationEnabled) {
                this.innerHTML = '<i class="fas fa-magic me-2"></i>Live Compile';
                showToast('Live compilation enabled', 'success');
            } else {
                this.innerHTML = '<i class="fas fa-magic me-2"></i>Manual Only';
                showToast('Live compilation disabled', 'info');
                clearTimeout(liveCompileTimeout);
            }
        });
    }

    // Export functionality
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            exportManuscript();
        });
    }

    function setupCompilationPanelToggle() {
        const toggleCompilationBtn = document.getElementById('toggle-compilation-panel');
        const editorContentWrapper = document.getElementById('editor-content-wrapper') || document.querySelector('.editor-content-wrapper');
        const compilationOutput = document.getElementById('compilation-output');

        console.log('[PDF TOGGLE] Setting up compilation panel...', {
            toggleBtn: !!toggleCompilationBtn,
            toggleBtnElement: toggleCompilationBtn,
            editorContentWrapper: !!editorContentWrapper,
            compilationOutput: !!compilationOutput
        });

        if (!toggleCompilationBtn) {
            console.error('[PDF TOGGLE] ✗ toggle-compilation-panel button not found!');
            return;
        }
        if (!editorContentWrapper) {
            console.error('[PDF TOGGLE] ✗ editor-content-wrapper div not found!');
            return;
        }
        if (!compilationOutput) {
            console.error('[PDF TOGGLE] ✗ compilation-output div not found!');
            return;
        }

        console.log('[PDF TOGGLE] ✓ All elements found, adding click listener...');

        // Make sure the button exists before adding event listener
        if (!toggleCompilationBtn || typeof toggleCompilationBtn.addEventListener !== 'function') {
            console.error('[PDF TOGGLE] ✗ Cannot add event listener - button is not valid');
            return;
        }

        toggleCompilationBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('[PDF TOGGLE] ✓ Button clicked!');
            const isShowingCompilation = compilationOutput.style.display !== 'none';
            console.log('[PDF TOGGLE] Current state - showing compilation:', isShowingCompilation);

            if (isShowingCompilation) {
                // Switch back to editor
                editorContentWrapper.style.display = 'flex';
                compilationOutput.style.display = 'none';
                this.innerHTML = '<i class="fas fa-file-pdf me-2"></i>View PDF';
                this.classList.remove('btn-info');
                this.classList.add('btn-primary');
            } else {
                // Switch to compilation view
                editorContentWrapper.style.display = 'none';
                compilationOutput.style.display = 'flex';
                this.innerHTML = '<i class="fas fa-code me-2"></i>Back to Editor';
                this.classList.remove('btn-primary');
                this.classList.add('btn-info');

                // Load PDFs if they exist
                checkForExistingPDFsPanel();

                // Compile button in panel
                const compileBtnPanel = document.getElementById('compile-btn-panel');
                console.log('Looking for compile-btn-panel:', !!compileBtnPanel);

                if (compileBtnPanel) {
                    console.log('✓ Compile button in panel found');
                    compileBtnPanel.addEventListener('click', function() {
                        console.log('✓ Compile button clicked in panel');

                        // Inline compilation start
                        const stopBtn = document.getElementById('stop-compile-btn');
                        const logPanel = document.getElementById('compilation-log-panel');

                        this.disabled = true;
                        this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Compiling...';
                        if (stopBtn) stopBtn.style.display = 'block';
                        logPanel.textContent = 'Starting compilation...\n';

                        fetch(`/writer/project/${projectId}/compile/`, {
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': getCsrfToken()
                            }
                        })
                        .then(response => {
                            console.log('[COMPILE] Response status:', response.status);
                            return response.json();
                        })
                        .then(data => {
                            console.log('[COMPILE] Response data:', data);
                            if (data.success) {
                                localStorage.setItem(`last_compile_job_${projectId}`, data.job_id);
                                logPanel.textContent += `Email notification sent.\nJob ID: ${data.job_id}\nMonitoring progress...\n`;
                                showToast('Compilation started! Email notification sent.', 'success');
                                pollCompilationStatusPanel(data.job_id);
                            } else {
                                logPanel.textContent += `\nError: ${data.error}`;
                                showToast('Compilation failed: ' + (data.error || 'Unknown error'), 'danger');
                                this.disabled = false;
                                this.innerHTML = '<i class="fas fa-file-pdf me-2"></i>Compile PDF';
                            }
                        })
                        .catch(error => {
                            console.error('[COMPILE] Fetch error:', error);
                            logPanel.textContent += `\nFetch error: ${error.message}`;
                            this.disabled = false;
                            this.innerHTML = '<i class="fas fa-file-pdf me-2"></i>Compile PDF';
                        });
                    });
                } else {
                    console.error('✗ Compile button panel NOT FOUND');
                }

                // Quick Compile button in panel
                const quickCompileBtnPanel = document.getElementById('quick-compile-btn-panel');
                if (quickCompileBtnPanel) {
                    console.log('✓ Quick compile button in panel found');
                    quickCompileBtnPanel.addEventListener('click', function() {
                        console.log('✓ Quick compile button clicked in panel');

                        const stopBtn = document.getElementById('stop-compile-btn');
                        const logPanel = document.getElementById('compilation-log-panel');

                        this.disabled = true;
                        this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Quick compiling...';
                        compileBtnPanel.disabled = true;  // Disable regular compile too
                        if (stopBtn) stopBtn.style.display = 'block';
                        logPanel.textContent = 'Starting quick compilation (text only, no figures)...\n';

                        fetch(`/writer/project/${projectId}/compile/`, {
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': getCsrfToken(),
                                'Content-Type': 'application/x-www-form-urlencoded'
                            },
                            body: 'quick=true'
                        })
                        .then(response => {
                            console.log('[QUICK-COMPILE] Response status:', response.status);
                            return response.json();
                        })
                        .then(data => {
                            console.log('[QUICK-COMPILE] Response data:', data);
                            if (data.success) {
                                localStorage.setItem(`last_compile_job_${projectId}`, data.job_id);
                                logPanel.textContent += `Email notification sent.\nJob ID: ${data.job_id}\nMonitoring progress...\n`;
                                showToast('Quick compilation started!', 'success');
                                pollCompilationStatusPanel(data.job_id);
                            } else {
                                logPanel.textContent += `\nError: ${data.error}`;
                                showToast('Quick compilation failed: ' + (data.error || 'Unknown error'), 'danger');
                                this.disabled = false;
                                compileBtnPanel.disabled = false;
                                this.innerHTML = '<i class="fas fa-bolt me-2"></i>Quick Compile (text only)';
                            }
                        })
                        .catch(error => {
                            console.error('[QUICK-COMPILE] Fetch error:', error);
                            logPanel.textContent += `\nFetch error: ${error.message}`;
                            this.disabled = false;
                            compileBtnPanel.disabled = false;
                            this.innerHTML = '<i class="fas fa-bolt me-2"></i>Quick Compile (text only)';
                        });
                    });
                } else {
                    console.error('✗ Quick compile button panel NOT FOUND');
                }
            }
        });
    }

    function switchToSection(section) {
        currentSection = section;

        // Save state
        saveState();

        // Update UI - use querySelectorAll to get current items
        const currentItems = document.querySelectorAll('.section-item');
        currentItems.forEach(item => {
            item.classList.toggle('active', item.dataset.section === section);
        });

        // Update section titles in headers
        const sectionTitle = sectionTitles[currentDocType][section];
        sectionTitleLatex.textContent = `${sectionTitle} - LaTeX`;
        sectionTitlePreview.textContent = `${sectionTitle} - Preview`;

        // Load section LaTeX content
        loadLatexSection(section);
    }

    function loadLatexSection(section) {
        console.log('[Writer] Loading section:', section, 'for doc type:', currentDocType);

        // Update section titles in headers
        const sectionTitle = sectionTitles[currentDocType][section];
        sectionTitleLatex.textContent = `${sectionTitle} - LaTeX`;
        sectionTitlePreview.textContent = `${sectionTitle} - Preview`;

        // For demo/guest users without projectId, load from local sectionsData
        if (!projectId || isDemo) {
            console.log('[Writer] Demo mode - loading from sectionsData');
            const content = sectionsData[currentDocType][section] || `% ${sectionTitle}\n\n`;
            codeMirrorEditor.setValue(content);

            // Update preview
            const textContent = convertFromLatex(section, content);
            textPreview.textContent = textContent;

            // Update word count
            updateWordCount();

            // Mark as saved
            markAsSaved();
            return;
        }

        // Load actual LaTeX content from server for project users
        console.log('[Writer] Loading from server for project:', projectId);
        fetch(`/writer/project/${projectId}/load-latex/?section=${section}&doc_type=${currentDocType}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                codeMirrorEditor.setValue(data.latex_content);

                // Update preview
                const textContent = convertFromLatex(section, data.latex_content);
                textPreview.textContent = textContent;

                // Update word count
                updateWordCount();

                // Mark as saved (just loaded from server)
                markAsSaved();
            } else {
                console.error('Failed to load LaTeX content:', data.error);
                codeMirrorEditor.setValue(`% ${sectionTitles[currentDocType][section]}\n\n`);
                textPreview.textContent = '';
                markAsSaved();
            }
        })
        .catch(error => {
            console.error('Load LaTeX error:', error);
            codeMirrorEditor.setValue(`% ${sectionTitles[currentDocType][section]}\n\n`);
            textPreview.textContent = '';
            markAsSaved();
        });
    }

    function switchDocumentType(docType) {
        // Warn if there are unsaved changes
        if (hasUnsavedChanges) {
            if (!confirm(`You have unsaved changes in ${sectionTitles[currentDocType][currentSection]}. Switch document type anyway? (Changes will be lost)`)) {
                // Revert selector to current doctype
                doctypeSelector.value = currentDocType;
                return;
            }
        }

        currentDocType = docType;

        // Save state
        saveState();

        // Keep title as "Active Sections" - no need to change per doc type
        sectionsTitle.textContent = 'Active Sections';

        // Render new sections
        renderSections(docType);

        // Update available sections pool if visible
        if (sectionPool.style.display !== 'none') {
            renderAvailableSections();
        }

        // Switch to first active section of new document type
        const firstSection = activeSections[docType][0];
        currentSection = firstSection;
        loadLatexSection(firstSection);
    }

    function renderSections(docType) {
        const sectionsContainer = sectionList.querySelector('.section-items');
        if (!sectionsContainer) return;

        // Clear existing sections
        sectionsContainer.innerHTML = '';

        // Render only active sections for current document type
        const activeList = activeSections[docType];
        activeList.forEach((section, index) => {
            const sectionDiv = document.createElement('div');
            const isCurrentSection = section === currentSection;
            sectionDiv.className = `section-item ${isCurrentSection ? 'active' : ''}`;
            sectionDiv.dataset.section = section;
            sectionDiv.draggable = true;

            sectionDiv.innerHTML = `
                <span class="section-drag-handle">
                    <i class="fas fa-grip-vertical"></i>
                </span>
                <div class="d-flex justify-content-between align-items-start" style="padding-left: 1.5rem;">
                    <div class="flex-grow-1">
                        <div class="section-name">${sectionTitles[docType][section]}</div>
                        <div class="section-stats">
                            <div class="word-count">
                                <span id="words-${section}">0</span> words
                            </div>
                        </div>
                        <div class="section-actions mt-1" style="display: flex; align-items: center; gap: 0.5rem;">
                            <button class="btn btn-sm btn-primary section-save-btn" data-section="${section}" style="font-size: 0.7rem; padding: 0.15rem 0.5rem;">
                                <i class="fas fa-save me-1"></i>Save
                            </button>
                            <span class="section-save-status text-muted" id="save-status-${section}" style="font-size: 0.7rem;">
                                <i class="fas fa-check-circle text-success me-1"></i>Saved
                            </span>
                        </div>
                    </div>
                    <button class="section-remove-btn" data-section="${section}" title="Move to pool">
                        <i class="fas fa-minus-circle"></i>
                    </button>
                </div>
                <div class="completion-indicator" style="margin-left: 1.5rem;">
                    <div class="completion-fill" style="width: 0%;"></div>
                </div>
            `;

            // Drag and drop event listeners
            sectionDiv.addEventListener('dragstart', handleDragStart);
            sectionDiv.addEventListener('dragend', handleDragEnd);
            sectionDiv.addEventListener('dragover', handleDragOver);
            sectionDiv.addEventListener('drop', handleDrop);
            sectionDiv.addEventListener('dragleave', handleDragLeave);

            sectionsContainer.appendChild(sectionDiv);
        });

        // Add event listeners to remove buttons
        sectionsContainer.querySelectorAll('.section-remove-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const section = this.dataset.section;
                removeSection(section);
            });
        });

        // Add event listeners to section save buttons
        sectionsContainer.querySelectorAll('.section-save-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const section = this.dataset.section;
                // If this is the current section, save it
                if (section === currentSection) {
                    saveCurrentSectionManually();
                } else {
                    // Switch to that section first, then save
                    switchToSection(section);
                    setTimeout(() => saveCurrentSectionManually(), 100);
                }
            });
        });
    }

    let draggedElement = null;
    let dragSource = null; // 'active' or 'pool'

    function handleDragStart(e) {
        draggedElement = this;
        dragSource = 'active';
        this.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', this.dataset.section);
    }

    function handleDragEnd(e) {
        this.classList.remove('dragging');
        document.querySelectorAll('.section-item').forEach(item => {
            item.classList.remove('drag-over');
        });
        document.querySelectorAll('.drop-zone-active').forEach(el => {
            el.classList.remove('drop-zone-active');
        });
        dragSource = null;
    }

    function handleDragOver(e) {
        if (e.preventDefault) {
            e.preventDefault();
        }
        e.dataTransfer.dropEffect = 'move';
        return false;
    }

    function handleDrop(e) {
        if (e.stopPropagation) {
            e.stopPropagation();
        }
        if (e.preventDefault) {
            e.preventDefault();
        }

        if (draggedElement !== this) {
            const activeList = activeSections[currentDocType];
            const draggedSection = draggedElement.dataset.section;
            const targetSection = this.dataset.section;

            const draggedIndex = activeList.indexOf(draggedSection);
            const targetIndex = activeList.indexOf(targetSection);

            if (draggedIndex > -1 && targetIndex > -1) {
                // Reordering within active sections
                activeList.splice(draggedIndex, 1);
                activeList.splice(targetIndex, 0, draggedSection);

                saveState();
                renderSections(currentDocType);
                showToast('Section order updated', 'info');
            }
        }

        this.classList.remove('drag-over');
        return false;
    }

    function handleDragLeave(e) {
        this.classList.remove('drag-over');
    }

    function setupDropZones() {
        const sectionsContainer = sectionList.querySelector('.section-items');

        // Drop zone for active sections (to add from pool)
        sectionsContainer.addEventListener('dragover', function(e) {
            if (dragSource === 'pool') {
                e.preventDefault();
                this.classList.add('drop-zone-active');
            }
        });

        sectionsContainer.addEventListener('dragleave', function(e) {
            this.classList.remove('drop-zone-active');
        });

        sectionsContainer.addEventListener('drop', function(e) {
            if (dragSource === 'pool' && draggedElement) {
                e.preventDefault();
                e.stopPropagation();
                const section = draggedElement.dataset.section;
                addSection(section);
                this.classList.remove('drop-zone-active');
            }
        });

        // Drop zone for pool (to remove from active)
        availableSectionsContainer.addEventListener('dragover', function(e) {
            if (dragSource === 'active') {
                e.preventDefault();
                this.classList.add('drop-zone-active');
            }
        });

        availableSectionsContainer.addEventListener('dragleave', function(e) {
            this.classList.remove('drop-zone-active');
        });

        availableSectionsContainer.addEventListener('drop', function(e) {
            if (dragSource === 'active' && draggedElement) {
                e.preventDefault();
                e.stopPropagation();
                const section = draggedElement.dataset.section;
                removeSection(section);
                this.classList.remove('drop-zone-active');
            }
        });
    }

    function renderAvailableSections() {
        availableSectionsContainer.innerHTML = '';

        // Get sections not currently active
        const allSections = allAvailableSections[currentDocType];
        const activeList = activeSections[currentDocType];
        const availableSectionsList = allSections.filter(s => !activeList.includes(s));

        if (availableSectionsList.length === 0) {
            availableSectionsContainer.innerHTML = '<p class="text-muted small mb-0">All sections are active</p>';
            return;
        }

        availableSectionsList.forEach(section => {
            const sectionDiv = document.createElement('div');
            sectionDiv.className = 'available-section-item';
            sectionDiv.dataset.section = section;
            sectionDiv.draggable = true;

            sectionDiv.innerHTML = `
                <span>${sectionTitles[currentDocType][section]}</span>
                <span class="section-add-btn">
                    <i class="fas fa-plus-circle"></i>
                </span>
            `;

            // Click to add
            sectionDiv.addEventListener('click', function() {
                addSection(section);
            });

            // Drag from pool to active
            sectionDiv.addEventListener('dragstart', function(e) {
                draggedElement = this;
                this.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/plain', section);
                e.dataTransfer.setData('source', 'pool');
            });

            sectionDiv.addEventListener('dragend', function(e) {
                this.classList.remove('dragging');
                document.querySelectorAll('.drop-zone-active').forEach(el => {
                    el.classList.remove('drop-zone-active');
                });
            });

            availableSectionsContainer.appendChild(sectionDiv);
        });

        // Make active sections container a drop zone for pool items
        setupDropZones();
    }

    function addSection(section) {
        if (!activeSections[currentDocType].includes(section)) {
            activeSections[currentDocType].push(section);

            // Initialize section data if not exists (preserve existing data)
            if (sectionsData[currentDocType][section] === undefined) {
                sectionsData[currentDocType][section] = '';
            }

            // Save state
            saveState();

            // Re-render sections
            renderSections(currentDocType);
            renderAvailableSections();

            const wordCount = sectionsData[currentDocType][section] ?
                sectionsData[currentDocType][section].trim().split(/\s+/).filter(w => w.length > 0).length : 0;
            const statusMsg = wordCount > 0 ?
                ` (${wordCount} words preserved)` : '';
            showToast(`Activated: ${sectionTitles[currentDocType][section]}${statusMsg}`, 'success');
        }
    }

    function removeSection(section) {
        const activeList = activeSections[currentDocType];
        const index = activeList.indexOf(section);

        if (index > -1 && activeList.length > 1) {  // Keep at least one section
            // Save current content before removing
            if (currentSection === section) {
                const latexContent = latexEditorTextarea.value;
                saveCurrentSectionFromLatex();
            }

            // Remove from active list (data retained in sectionsData)
            activeList.splice(index, 1);

            // If we're currently viewing this section, switch to first available
            if (currentSection === section) {
                currentSection = activeList[0];
                loadLatexSection(currentSection);
            }

            // Save state
            saveState();

            // Re-render sections
            renderSections(currentDocType);
            renderAvailableSections();

            showToast(`Moved to pool: ${sectionTitles[currentDocType][section]}`, 'info');
        } else if (activeList.length === 1) {
            showToast('Cannot remove the last section', 'warning');
        }
    }

    function markAsUnsaved(section = currentSection) {
        hasUnsavedChanges = true;

        // Update section-specific save button and status
        const sectionSaveBtn = document.querySelector(`.section-save-btn[data-section="${section}"]`);
        const sectionStatus = document.getElementById(`save-status-${section}`);

        if (sectionSaveBtn) {
            sectionSaveBtn.classList.add('btn-warning');
            sectionSaveBtn.classList.remove('btn-primary');
            sectionSaveBtn.innerHTML = '<i class="fas fa-save me-1"></i>Save *';
        }

        if (sectionStatus) {
            sectionStatus.innerHTML = '<i class="fas fa-exclamation-circle text-warning me-1"></i>Unsaved';
        }
    }

    function markAsSaved(section = currentSection) {
        hasUnsavedChanges = false;

        // Update section-specific save button and status
        const sectionSaveBtn = document.querySelector(`.section-save-btn[data-section="${section}"]`);
        const sectionStatus = document.getElementById(`save-status-${section}`);

        if (sectionSaveBtn) {
            sectionSaveBtn.classList.remove('btn-warning');
            sectionSaveBtn.classList.add('btn-primary');
            sectionSaveBtn.innerHTML = '<i class="fas fa-save me-1"></i>Save';
        }

        if (sectionStatus) {
            sectionStatus.innerHTML = '<i class="fas fa-check-circle text-success me-1"></i>Saved';
        }
    }

    function saveCurrentSectionManually() {
        console.log('[Writer] Manual save triggered');

        // Check if in demo mode - show guidance message
        if (isDemo) {
            console.log('[Writer] Demo mode - showing guidance');
            if (isAnonymous) {
                showToast('Demo Mode: Sign up to save your work permanently. <a href="/auth/signup/" class="alert-link">Sign Up</a> or <a href="/auth/login/" class="alert-link">Log In</a>', 'info', 5000);
            } else {
                showToast('Create a project to save your work permanently. <a href="/new/" class="alert-link">Create Project</a>', 'warning', 5000);
            }
            // Still save to localStorage for demo users
            const latexContent = codeMirrorEditor.getValue();
            sectionsData[currentDocType][currentSection] = latexContent;
            markAsSaved();
            return;
        }

        const latexContent = codeMirrorEditor.getValue();
        const sectionToSave = currentSection;  // Capture current section

        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Saving...';
        saveStatus.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Saving...';

        // Save LaTeX content directly to file
        fetch(`/writer/project/${projectId}/save-latex/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                section: sectionToSave,
                doc_type: currentDocType,
                latex_content: latexContent
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateSectionWordCount(sectionToSave, data.word_count);
                updateTotalWordCount(data.total_words);
                markAsSaved();

                // Add to undo/redo history
                addToHistory(sectionToSave, latexContent, data.word_count);

                showToast(`${sectionTitles[currentDocType][sectionToSave]} saved successfully`, 'success');
            } else {
                saveStatus.innerHTML = '<i class="fas fa-times-circle text-danger me-1"></i>Error saving';
                showToast('Error saving: ' + (data.error || 'Unknown error'), 'danger');
            }
        })
        .catch(error => {
            console.error('Save error:', error);
            saveStatus.innerHTML = '<i class="fas fa-times-circle text-danger me-1"></i>Save failed';
            showToast('Save failed: ' + error.message, 'danger');
        })
        .finally(() => {
            saveBtn.disabled = false;
        });
    }


    function scheduleLiveCompilation() {
        clearTimeout(liveCompileTimeout);
        liveCompileTimeout = setTimeout(() => {
            performLiveCompilation();
        }, 5000); // Compile 5 seconds after last change
    }

    function performLiveCompilation() {
        if (currentlyCompiling) return;

        currentlyCompiling = true;
        showSaveStatus('Auto-compiling...', 'info');

        fetch(`/writer/project/${projectId}/compile/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSaveStatus('Auto-compiled successfully', 'success');
                checkCompilationStatus(data.job_id);
            } else {
                showSaveStatus('Auto-compile failed', 'danger');
            }
        })
        .catch(error => {
            console.error('Live compilation error:', error);
            showSaveStatus('Auto-compile error', 'danger');
        })
        .finally(() => {
            currentlyCompiling = false;
        });
    }

    function checkCompilationStatus(jobId) {
        fetch(`/writer/api/status/${jobId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'completed') {
                showSaveStatus('PDF ready', 'success');
                // Could update a preview here
            } else if (data.status === 'failed') {
                showSaveStatus('Compilation failed', 'danger');
            } else if (data.status === 'running') {
                // Check again in 2 seconds
                setTimeout(() => checkCompilationStatus(jobId), 2000);
            }
        })
        .catch(error => {
            console.error('Status check error:', error);
        });
    }


    function convertToLatex(section, content) {
        if (section === 'abstract') {
            return `% Abstract\n\\begin{abstract}\n${content}\n\\end{abstract}\n`;
        } else {
            return `% ${sectionTitles[section]}\n\\section{${sectionTitles[section]}}\n${content}\n`;
        }
    }

    function convertFromLatex(section, latexContent) {
        let content = latexContent;

        // Remove LaTeX comments
        content = content.replace(/^%.*$/gm, '');

        if (section === 'abstract') {
            // Extract content from \begin{abstract}...\end{abstract}
            const abstractMatch = content.match(/\\begin\{abstract\}([\s\S]*?)\\end\{abstract\}/);
            if (abstractMatch) {
                content = abstractMatch[1];
            }
        } else {
            // Remove \section{...} command
            content = content.replace(/\\section\{[^}]*\}\s*/g, '');
        }

        // Remove common LaTeX commands while preserving text
        content = content
            // Remove simple commands like \textbf{}, \emph{}, \cite{}
            .replace(/\\(?:textbf|emph|textit|texttt|cite)\{([^}]*)\}/g, '$1')
            // Remove \label{} commands
            .replace(/\\label\{[^}]*\}/g, '')
            // Convert \\ to line breaks
            .replace(/\\\\/g, '\n')
            // Remove remaining single backslashes (but keep escaped characters)
            .replace(/\\(?![\\{}])/g, '')
            // Clean up extra whitespace
            .replace(/\n\s*\n/g, '\n\n')
            .trim();

        return content;
    }

    function updateWordCount() {
        // Convert LaTeX to plain text for word counting
        const latexContent = codeMirrorEditor.getValue();
        const content = convertFromLatex(currentSection, latexContent);
        const words = content.trim().split(/\s+/).filter(word => word.length > 0).length;
        currentWordCount.textContent = words;

        // Also update the section card's word count in real-time
        updateSectionWordCount(currentSection, words);

        // Save to localStorage for persistence
        saveWordCountToLocalStorage(currentSection, currentDocType, words);
    }

    function updateSectionWordCount(section, count) {
        const wordElement = document.getElementById(`words-${section}`);
        if (wordElement) {
            wordElement.textContent = count;
        }

        // Update completion indicator
        const completionFill = document.querySelector(`[data-section="${section}"] .completion-fill`);
        if (completionFill) {
            completionFill.style.width = count > 0 ? '100%' : '0%';
        }
    }

    function saveWordCountToLocalStorage(section, docType, count) {
        const key = `wordcount_${projectId}_${docType}_${section}`;
        localStorage.setItem(key, count);
    }

    function loadWordCountFromLocalStorage(section, docType) {
        const key = `wordcount_${projectId}_${docType}_${section}`;
        const count = localStorage.getItem(key);

        if (count !== null) {
            return parseInt(count, 10);
        }

        // Fallback to server data if localStorage is empty (e.g., after hard refresh)
        if (serverWordCounts[docType] && serverWordCounts[docType][section] !== undefined) {
            return serverWordCounts[docType][section];
        }

        return 0;
    }

    function loadAllWordCountsFromLocalStorage() {
        // Load word counts for all sections from localStorage
        Object.keys(sectionTitles).forEach(docType => {
            Object.keys(sectionTitles[docType]).forEach(section => {
                const count = loadWordCountFromLocalStorage(section, docType);
                if (count > 0) {
                    updateSectionWordCount(section, count);
                }
            });
        });
    }

    function updateTotalWordCount(total) {
        document.getElementById('total-words').textContent = total;
    }

    function compileManuscript() {
        compileBtn.disabled = true;
        compileBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Compiling...';

        // Show progress UI
        compilationProgress.style.display = 'block';
        progressBar.style.width = '10%';
        progressBar.textContent = '10%';
        compilationLog.textContent = 'Starting compilation...';

        fetch(`/writer/project/${projectId}/compile/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Store job ID in localStorage for persistence
                localStorage.setItem(`last_compile_job_${projectId}`, data.job_id);

                compilationLog.textContent += '\nEmail notification sent.\nMonitoring progress...';
                showToast('Compilation started! Email notification sent.', 'success');
                // Poll for completion status
                pollCompilationStatus(data.job_id);
            } else {
                compilationLog.textContent += `\nError: ${data.error}`;
                showToast('Compilation failed: ' + (data.error || 'Unknown error'), 'danger');
                compileBtn.disabled = false;
                compileBtn.innerHTML = '<i class="fas fa-file-pdf me-2"></i>Compile PDF';
                progressBar.classList.add('bg-danger');
            }
        })
        .catch(error => {
            compilationLog.textContent += `\nError: ${error.message}`;
            showToast('Compilation error: ' + error.message, 'danger');
            compileBtn.disabled = false;
            compileBtn.innerHTML = '<i class="fas fa-file-pdf me-2"></i>Compile PDF';
            progressBar.classList.add('bg-danger');
        });
    }

    function pollCompilationStatus(jobId, attempts = 0) {
        if (attempts > 60) {  // Max 60 attempts (2 minutes)
            compilationLog.textContent += '\nTimeout - compilation may still be running';
            showToast('Compilation timeout - please refresh to check status', 'warning');
            compileBtn.disabled = false;
            compileBtn.innerHTML = '<i class="fas fa-file-pdf me-2"></i>Compile PDF';
            progressBar.classList.add('bg-warning');
            return;
        }

        fetch(`/writer/api/status/${jobId}/`)
        .then(response => response.json())
        .then(data => {
            // Update progress bar
            const progress = data.progress || 50;
            progressBar.style.width = `${progress}%`;
            progressBar.textContent = `${progress}%`;

            // Always show the full log if available (not just preview)
            if (data.log) {
                compilationLog.textContent = data.log;
                compilationLog.scrollTop = compilationLog.scrollHeight;
            } else if (data.log_preview) {
                compilationLog.textContent = data.log_preview;
                compilationLog.scrollTop = compilationLog.scrollHeight;
            }

            if (data.status === 'completed') {
                progressBar.style.width = '100%';
                progressBar.textContent = '100%';
                progressBar.classList.remove('progress-bar-animated');
                progressBar.classList.add('bg-success');
                compileBtn.innerHTML = '<i class="fas fa-check me-2"></i>Compiled!';

                // Ensure full log is displayed
                if (data.log) {
                    compilationLog.textContent = data.log;
                    compilationLog.scrollTop = compilationLog.scrollHeight;
                }

                // Show PDF viewer
                const pdfUrl = `/writer/project/${projectId}/pdf/`;
                pdfViewer.src = pdfUrl;
                pdfViewLink.href = pdfUrl;
                pdfDownloadLink.href = `${pdfUrl}?mode=download`;
                pdfViewerContainer.style.display = 'block';

                // Check for diff PDF and load it too
                checkForDiffPDF();

                showToast('PDF compiled successfully!', 'success');

                setTimeout(() => {
                    compileBtn.disabled = false;
                    compileBtn.innerHTML = '<i class="fas fa-file-pdf me-2"></i>Compile PDF';
                }, 3000);
            } else if (data.status === 'failed') {
                progressBar.classList.add('bg-danger');
                progressBar.classList.remove('progress-bar-animated');

                const errorMsg = data.error || 'Unknown error';
                compilationLog.textContent = `ERROR: ${errorMsg}\n\n${data.error_details || data.log || ''}`;
                compilationLog.scrollTop = compilationLog.scrollHeight;

                showToast(`Compilation failed: ${errorMsg}`, 'danger');
                compileBtn.disabled = false;
                compileBtn.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i>Failed';

                setTimeout(() => {
                    compileBtn.innerHTML = '<i class="fas fa-file-pdf me-2"></i>Compile PDF';
                }, 3000);
            } else {
                // Still running or queued - poll again
                compileBtn.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${progress}%`;
                setTimeout(() => pollCompilationStatus(jobId, attempts + 1), 2000);
            }
        })
        .catch(error => {
            console.error('Status check error:', error);
            // Retry polling on error
            setTimeout(() => pollCompilationStatus(jobId, attempts + 1), 2000);
        });
    }

    function exportManuscript() {
        console.log('[Writer] Exporting manuscript');
        // Create export data
        const exportData = {
            project: window.WRITER_CONFIG?.projectName || 'Demo Project',
            manuscript: window.WRITER_CONFIG?.manuscriptTitle || 'Untitled Manuscript',
            sections: sectionsData,
            stats: {
                totalWords: document.getElementById('total-words').textContent,
                citations: document.getElementById('citation-count').textContent
            },
            exported: new Date().toISOString()
        };

        // Download as JSON
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${exportData.project.replace(/\s+/g, '_')}_manuscript.json`;
        a.click();
        URL.revokeObjectURL(url);

        showToast('Manuscript exported successfully!', 'success');
    }

    function showSaveStatus(message, type) {
        const icon = type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : 'times-circle';
        const color = type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'danger';

        autoSaveStatus.innerHTML = `<i class="fas fa-${icon} text-${color} me-1"></i>${message}`;
    }

    function showToast(message, type, duration = 5000) {
        console.log('[Writer] Showing toast:', type, message);
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show`;
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        container.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, duration);
    }

    function checkForExistingPDF() {
        // Check if main PDF exists
        fetch(`/writer/project/${projectId}/pdf/`)
        .then(response => {
            if (response.ok) {
                // Main PDF exists - show the viewer
                const pdfUrl = `/writer/project/${projectId}/pdf/`;
                pdfViewer.src = pdfUrl;
                pdfViewLink.href = pdfUrl;
                pdfDownloadLink.href = `${pdfUrl}?mode=download`;
                pdfViewerContainer.style.display = 'block';

                // Check if diff PDF also exists
                checkForDiffPDF();
            }
        })
        .catch(error => {
            // No PDF exists yet - that's fine
            console.log('No compiled PDF found yet');
        });
    }

    function checkForDiffPDF() {
        // Check if diff PDF exists
        fetch(`/writer/project/${projectId}/pdf/?type=diff`)
        .then(response => {
            if (response.ok) {
                // Diff PDF exists - enable the diff button
                hasDiffPdf = true;
                showDiffPdfBtn.disabled = false;
                showDiffPdfBtn.classList.remove('disabled');

                // Set up diff PDF viewer
                const diffPdfUrl = `/writer/project/${projectId}/pdf/?type=diff`;
                diffPdfViewer.src = diffPdfUrl;
                diffPdfViewLink.href = diffPdfUrl;
                diffPdfDownloadLink.href = `${diffPdfUrl}&mode=download`;
            } else {
                // No diff PDF yet
                hasDiffPdf = false;
                showDiffPdfBtn.disabled = true;
                showDiffPdfBtn.classList.add('disabled');
                showDiffPdfBtn.title = 'Diff PDF not available yet (compile again after changes)';
            }
        })
        .catch(error => {
            hasDiffPdf = false;
            console.log('No diff PDF found');
        });
    }

    window.showPDF = function(type) {
        if (type === 'main') {
            mainPdfContainer.style.display = 'block';
            diffPdfContainer.style.display = 'none';
            showMainPdfBtn.classList.add('active');
            showMainPdfBtn.classList.remove('btn-outline-primary');
            showMainPdfBtn.classList.add('btn-primary');
            showDiffPdfBtn.classList.remove('active', 'btn-primary');
            showDiffPdfBtn.classList.add('btn-outline-secondary');
        } else if (type === 'diff') {
            if (hasDiffPdf) {
                mainPdfContainer.style.display = 'none';
                diffPdfContainer.style.display = 'block';
                showDiffPdfBtn.classList.add('active');
                showDiffPdfBtn.classList.remove('btn-outline-secondary');
                showDiffPdfBtn.classList.add('btn-primary');
                showMainPdfBtn.classList.remove('active', 'btn-primary');
                showMainPdfBtn.classList.add('btn-outline-primary');
            }
        }
    }

    function checkForRunningCompilation() {
        // Check if there's a recent compilation job
        // Get the last job ID from localStorage
        const lastJobId = localStorage.getItem(`last_compile_job_${projectId}`);
        if (lastJobId) {
            fetch(`/writer/api/status/${lastJobId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'running' || data.status === 'queued') {
                    // Resume showing progress
                    compilationProgress.style.display = 'block';
                    showToast('Resuming compilation monitoring...', 'info');
                    pollCompilationStatus(lastJobId);
                } else if (data.status === 'completed' && data.log) {
                    // Show completed status with logs
                    compilationProgress.style.display = 'block';
                    progressBar.style.width = '100%';
                    progressBar.textContent = '100%';
                    progressBar.classList.remove('progress-bar-animated');
                    progressBar.classList.add('bg-success');
                    compilationLog.textContent = data.log;
                }
            })
            .catch(error => {
                // Job not found or error - clear the stored ID
                localStorage.removeItem(`last_compile_job_${projectId}`);
            });
        }
    }

    function checkForExistingPDFsPanel() {
        // Load PDF.js if not already loaded
        if (typeof pdfjsLib === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js';
            script.onload = function() {
                pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
                loadPDFsPanel();
            };
            document.head.appendChild(script);
        } else {
            loadPDFsPanel();
        }
    }

    function loadPDFsPanel() {
        console.log('[Writer] Loading PDF panel');
        if (!window.WRITER_CONFIG?.projectId) {
            console.log('[Writer] No project - skipping PDF load');
            const pdfViewerPanel = document.getElementById('pdf-viewer-panel');
            const message = window.WRITER_CONFIG?.isAnonymous ? 'Sign up to compile PDFs' : 'Create a project to compile PDFs';
            pdfViewerPanel.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: var(--color-fg-muted);">' + message + '</div>';
            return;
        }

        const username = window.WRITER_CONFIG?.username || 'user';
        const slug = window.WRITER_CONFIG?.projectSlug || '';

        // Load main PDF
        const pdfBlobUrl = `/${username}/${slug}/blob/paper/01_manuscript/manuscript.pdf?mode=raw`;
        const pdfViewerPanel = document.getElementById('pdf-viewer-panel');
        const pdfViewLinkPanel = document.getElementById('pdf-view-link-panel');
        const pdfDownloadLinkPanel = document.getElementById('pdf-download-link-panel');

        pdfViewLinkPanel.href = `/${username}/${slug}/blob/paper/01_manuscript/manuscript.pdf`;
        pdfDownloadLinkPanel.href = pdfBlobUrl;

        pdfViewerPanel.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: var(--color-fg-muted);"><i class="fas fa-spinner fa-spin me-2"></i>Loading PDF...</div>';

        pdfjsLib.getDocument({
            url: pdfBlobUrl,
            withCredentials: true  // Include cookies for authentication
        }).promise.then(function(pdf) {
            mainPdfDoc = pdf;
            renderPDFWithOutline(pdf, pdfViewerPanel, 'pdf-outline-items-main', 1.2);
        }).catch(function(error) {
            pdfViewerPanel.innerHTML = `<div style="padding: 2rem; text-align: center; color: var(--color-fg-muted);">
                <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                <p>PDF not found or error loading</p>
                <small>Error: ${error.message}</small>
                <p class="mt-3"><a href="${pdfBlobUrl}" target="_blank" class="btn btn-sm btn-primary">Open PDF Directly</a></p>
            </div>`;
            console.error('Error loading main PDF:', error, 'URL:', pdfBlobUrl);
        });

        // Load diff PDF
        const diffPdfBlobUrl = `/${username}/${slug}/blob/paper/01_manuscript/manuscript_diff.pdf?mode=raw`;
        const diffPdfViewerPanel = document.getElementById('diff-pdf-viewer-panel');
        const diffPdfViewLinkPanel = document.getElementById('diff-pdf-view-link-panel');
        const diffPdfDownloadLinkPanel = document.getElementById('diff-pdf-download-link-panel');
        const diffPdfPlaceholder = document.getElementById('diff-pdf-placeholder');
        const toggleOutlineDiff = document.getElementById('toggle-outline-diff');

        diffPdfViewLinkPanel.href = `/${username}/${slug}/blob/paper/01_manuscript/manuscript_diff.pdf`;
        diffPdfDownloadLinkPanel.href = diffPdfBlobUrl;

        pdfjsLib.getDocument({
            url: diffPdfBlobUrl,
            withCredentials: true  // Include cookies for authentication
        }).promise.then(function(pdf) {
            diffPdfDoc = pdf;
            renderPDFWithOutline(pdf, diffPdfViewerPanel, 'pdf-outline-items-diff', 1.2);
            diffPdfPlaceholder.style.display = 'none';
            diffPdfViewerPanel.style.display = 'block';
            toggleOutlineDiff.style.display = 'inline-block';
        }).catch(function(error) {
            // Diff PDF doesn't exist yet - that's OK
            console.log('Diff PDF not available yet:', error.message);
        });

        // Setup outline toggle buttons
        document.getElementById('toggle-outline-main').addEventListener('click', function() {
            const outline = document.getElementById('pdf-outline-main');
            outline.style.display = outline.style.display === 'none' ? 'block' : 'none';
        });

        const toggleOutlineDiffBtn = document.getElementById('toggle-outline-diff');
        if (toggleOutlineDiffBtn) {
            toggleOutlineDiffBtn.addEventListener('click', function() {
                const outline = document.getElementById('pdf-outline-diff');
                outline.style.display = outline.style.display === 'none' ? 'block' : 'none';
            });
        }
    }

    function renderPDFWithOutline(pdf, container, outlineContainerId, scale) {
        // Render pages
        container.innerHTML = '';
        container.style.overflowY = 'auto';
        container.style.padding = '0.5rem';

        // Calculate scale to fit container width while maintaining A4 ratio
        // A4: 210mm x 297mm (1:1.414 ratio)
        // PDF.js default: 595pt x 842pt
        const containerWidth = container.clientWidth - 40; // Account for padding
        const a4Width = 595; // PDF points
        const calculatedScale = containerWidth / a4Width;

        for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
            const pageContainer = document.createElement('div');
            pageContainer.style.cssText = 'margin: 0.5rem auto; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); position: relative;';
            pageContainer.id = `page-${outlineContainerId}-${pageNum}`;
            pageContainer.dataset.pageNum = pageNum;

            container.appendChild(pageContainer);

            pdf.getPage(pageNum).then(function(page) {
                const viewport = page.getViewport({ scale: calculatedScale });
                const canvas = document.createElement('canvas');
                const context = canvas.getContext('2d');
                canvas.height = viewport.height;
                canvas.width = viewport.width;

                // Maintain A4 aspect ratio
                canvas.style.cssText = 'display: block; width: 100%; height: auto;';

                pageContainer.appendChild(canvas);

                page.render({
                    canvasContext: context,
                    viewport: viewport
                });
            });
        }

        // Load and render outline
        pdf.getOutline().then(function(outline) {
            if (outline && outline.length > 0) {
                const outlineContainer = document.getElementById(outlineContainerId);
                outlineContainer.innerHTML = '';

                function renderOutlineItem(item) {
                    const div = document.createElement('div');
                    div.className = 'pdf-outline-item-writer';
                    div.textContent = item.title;

                    div.addEventListener('click', function(e) {
                        e.preventDefault();
                        if (item.dest) {
                            pdf.getDestination(item.dest).then(function(dest) {
                                if (dest) {
                                    pdf.getPageIndex(dest[0]).then(function(pageIndex) {
                                        const pageNum = pageIndex + 1;
                                        const pageElement = document.getElementById(`page-${outlineContainerId}-${pageNum}`);
                                        if (pageElement && container) {
                                            // Scroll within PDF container only, not the page
                                            const elementTop = pageElement.offsetTop - container.offsetTop;
                                            container.scrollTop = elementTop;
                                        }
                                    });
                                }
                            });
                        }
                    });

                    outlineContainer.appendChild(div);

                    // Render children with indentation
                    if (item.items && item.items.length > 0) {
                        item.items.forEach(function(childItem) {
                            const childDiv = document.createElement('div');
                            childDiv.className = 'pdf-outline-item-writer pdf-outline-child-writer';
                            childDiv.textContent = childItem.title;

                            childDiv.addEventListener('click', function(e) {
                                e.preventDefault();
                                if (childItem.dest) {
                                    pdf.getDestination(childItem.dest).then(function(dest) {
                                        if (dest) {
                                            pdf.getPageIndex(dest[0]).then(function(pageIndex) {
                                                const pageNum = pageIndex + 1;
                                                const pageElement = document.getElementById(`page-${outlineContainerId}-${pageNum}`);
                                                if (pageElement && container) {
                                                    // Scroll within PDF container only, not the page
                                                    const elementTop = pageElement.offsetTop - container.offsetTop;
                                                    container.scrollTop = elementTop;
                                                }
                                            });
                                        }
                                    });
                                }
                            });

                            outlineContainer.appendChild(childDiv);
                        });
                    }
                }

                outline.forEach(renderOutlineItem);
            }
        }).catch(function() {
            console.log('No outline available for this PDF');
        });
    }

    function compileManuscriptPanel() {
        const compileBtnPanel = document.getElementById('compile-btn-panel');
        const stopBtn = document.getElementById('stop-compile-btn');
        const progressPanel = document.getElementById('compilation-progress-panel');
        const progressBarPanel = document.getElementById('progress-bar-panel');
        const logPanel = document.getElementById('compilation-log-panel');
        const timerDisplay = document.getElementById('compilation-timer');

        compileBtnPanel.disabled = true;
        compileBtnPanel.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Compiling... (0:00)';
        stopBtn.style.display = 'block';
        progressPanel.style.display = 'block';
        progressBarPanel.style.width = '10%';
        progressBarPanel.textContent = '10%';
        logPanel.textContent = 'Starting compilation...\n';

        // Start timer (updates button text)
        compilationStartTime = Date.now();
        startTimerInButton();

        fetch(`/writer/project/${projectId}/compile/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => {
            console.log('[COMPILE] Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('[COMPILE] Response data:', data);
            if (data.success) {
                localStorage.setItem(`last_compile_job_${projectId}`, data.job_id);
                logPanel.textContent += `Email notification sent.\nJob ID: ${data.job_id}\nMonitoring progress...\n`;
                showToast('Compilation started! Email notification sent.', 'success');
                pollCompilationStatusPanel(data.job_id);
            } else {
                logPanel.textContent += `\nError: ${data.error}`;
                showToast('Compilation failed: ' + (data.error || 'Unknown error'), 'danger');
                compileBtnPanel.disabled = false;
                compileBtnPanel.innerHTML = '<i class="fas fa-file-pdf me-2"></i>Compile PDF';
            }
        })
        .catch(error => {
            console.error('[COMPILE] Fetch error:', error);
            logPanel.textContent += `\nFetch error: ${error.message}`;
            compileBtnPanel.disabled = false;
            compileBtnPanel.innerHTML = '<i class="fas fa-file-pdf me-2"></i>Compile PDF';
        });
    }

    function pollCompilationStatusPanel(jobId, attempts = 0) {
        console.log(`[POLL] Attempt ${attempts}, Job ID: ${jobId}`);

        if (attempts > 90) {
            document.getElementById('compilation-log-panel').textContent += '\nTimeout';
            return;
        }

        const logPanel = document.getElementById('compilation-log-panel');
        const compileBtnPanel = document.getElementById('compile-btn-panel');

        fetch(`/writer/api/status/${jobId}/`)
        .then(response => response.json())
        .then(data => {
            console.log(`[POLL] Status: ${data.status}, Has log: ${!!data.log}`);

            // Update log immediately if available
            if (data.log) {
                logPanel.textContent = data.log;
                logPanel.scrollTop = logPanel.scrollHeight;
                console.log(`[POLL] Updated log, length: ${data.log.length}`);
            } else {
                console.log('[POLL] No log in response');
            }

            if (data.status === 'completed') {
                const stopBtn = document.getElementById('stop-compile-btn');
                if (stopBtn) stopBtn.style.display = 'none';
                compileBtnPanel.innerHTML = '<i class="fas fa-check me-2"></i>Compiled!';

                // Load the PDFs
                checkForExistingPDFsPanel();

                showToast('PDF compiled successfully!', 'success');

                setTimeout(() => {
                    compileBtnPanel.disabled = false;
                    compileBtnPanel.innerHTML = '<i class="fas fa-file-pdf me-2"></i>Compile PDF';
                    const quickCompileBtnPanel = document.getElementById('quick-compile-btn-panel');
                    if (quickCompileBtnPanel) {
                        quickCompileBtnPanel.disabled = false;
                        quickCompileBtnPanel.innerHTML = '<i class="fas fa-bolt me-2"></i>Quick Compile (text only)';
                    }
                }, 3000);
            } else if (data.status === 'failed') {
                logPanel.textContent = `ERROR: ${data.error}\n\n${data.log || ''}`;
                compileBtnPanel.disabled = false;
                compileBtnPanel.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i>Failed';
                const quickCompileBtnPanel = document.getElementById('quick-compile-btn-panel');
                if (quickCompileBtnPanel) {
                    quickCompileBtnPanel.disabled = false;
                    quickCompileBtnPanel.innerHTML = '<i class="fas fa-bolt me-2"></i>Quick Compile (text only)';
                }
            } else {
                setTimeout(() => pollCompilationStatusPanel(jobId, attempts + 1), 2000);
            }
        });
    }

    function startTimerInButton() {
        const compileBtnPanel = document.getElementById('compile-btn-panel');
        if (timerInterval) clearInterval(timerInterval);

        timerInterval = setInterval(function() {
            if (compilationStartTime) {
                const elapsed = Math.floor((Date.now() - compilationStartTime) / 1000);
                const minutes = Math.floor(elapsed / 60);
                const seconds = elapsed % 60;
                const timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`;
                compileBtnPanel.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>Compiling... (${timeStr})`;
            }
        }, 1000);
    }

    function stopTimer() {
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
    }

    // Removed duplicate getCsrfToken and initializeWriterWorkspace - now handled by DOMContentLoaded event listener above

    // Stop button handler
    const stopCompileBtn = document.getElementById('stop-compile-btn');
    if (stopCompileBtn) {
        stopCompileBtn.addEventListener('click', function() {
            if (confirm('Stop monitoring compilation? (Process will continue in background)')) {
                stopTimer();
                this.style.display = 'none';
                document.getElementById('compile-btn-panel').disabled = false;
                document.getElementById('compile-btn-panel').innerHTML = '<i class="fas fa-file-pdf me-2"></i>Compile PDF';
                showToast('Stopped monitoring. Check back later for results.', 'info');
            }
        });
    }

    // Warn before leaving if there are unsaved changes
    window.addEventListener('beforeunload', function(e) {
        if (hasUnsavedChanges) {
            e.preventDefault();
            e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
            return e.returnValue;
        }
    });

    // Keyboard shortcut: Ctrl+S or Cmd+S to save
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            if (hasUnsavedChanges) {
                saveCurrentSectionManually();
            }
        }
    });

    // ========================================
    // TeX Files Browser
    // ========================================

    let texFilesList = [];
    let currentTexFile = null;
    const texFilesListContainer = document.getElementById('tex-files-list');
    const refreshFilesBtn = document.getElementById('refresh-files-btn');

    function loadTexFilesList() {
        if (!projectId) {
            console.log('[TeX Browser] No project ID, showing "no project selected" message');
            texFilesListContainer.innerHTML = '<div class="text-muted text-center py-3" style="font-size: 0.85rem;"><i class="fas fa-folder-open me-2"></i>No project selected</div>';
            return;
        }

        console.log('[TeX Browser] Loading TeX files list for project', projectId);

        texFilesListContainer.innerHTML = '<div class="text-muted text-center py-3" style="font-size: 0.85rem;"><i class="fas fa-spinner fa-spin me-2"></i>Loading files...</div>';

        // Set up timeout to prevent infinite loading
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 10000); // 10 second timeout

        fetch(`/writer/project/${projectId}/list-tex-files/`, { signal: controller.signal })
            .then(response => {
                clearTimeout(timeout);
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    texFilesList = data.files || [];
                    renderTexFilesList();
                    console.log(`[TeX Browser] Loaded ${texFilesList.length} TeX files`);
                } else {
                    texFilesListContainer.innerHTML = '<div class="text-muted text-center py-3" style="font-size: 0.85rem;"><i class="fas fa-exclamation-triangle me-2"></i>Failed to load files</div>';
                    console.error('[TeX Browser] Failed to load files:', data.message);
                }
            })
            .catch(error => {
                clearTimeout(timeout);
                console.error('[TeX Browser] Error loading files:', error);
                texFilesListContainer.innerHTML = '<div class="text-muted text-center py-3" style="font-size: 0.85rem;"><i class="fas fa-exclamation-triangle me-2"></i>Error loading files</div>';
            });
    }

    function renderTexFilesList() {
        if (!texFilesList || texFilesList.length === 0) {
            texFilesListContainer.innerHTML = '<div class="text-muted text-center py-3" style="font-size: 0.85rem;"><i class="fas fa-folder-open me-2"></i>No TeX files found</div>';
            return;
        }

        // Group files by doc_type
        const groupedFiles = {};
        texFilesList.forEach(file => {
            if (!groupedFiles[file.doc_type]) {
                groupedFiles[file.doc_type] = [];
            }
            groupedFiles[file.doc_type].push(file);
        });

        let html = '';
        const docTypeOrder = ['manuscript', 'supplementary', 'revision', 'shared'];

        docTypeOrder.forEach(docType => {
            if (groupedFiles[docType]) {
                groupedFiles[docType].forEach(file => {
                    const isActive = currentTexFile && currentTexFile.section === file.section && currentTexFile.doc_type === file.doc_type;
                    const modifiedClass = ''; // Will be updated based on save status

                    // Generate Gitea repository link if available
                    const giteaLink = file.gitea_url
                        ? `<a href="${file.gitea_url}" target="_blank" rel="noopener"
                               class="tex-file-repo-link" title="View in repository"
                               onclick="event.stopPropagation();">
                               <i class="fas fa-code-branch"></i>
                           </a>`
                        : '';

                    html += `
                        <div class="tex-file-item ${isActive ? 'active' : ''} ${modifiedClass}"
                             data-section="${file.section}"
                             data-doc-type="${file.doc_type}"
                             data-file-name="${file.name}">
                            <div class="tex-file-info">
                                <div class="tex-file-name">${file.name}</div>
                                <div class="tex-file-meta">
                                    <span class="tex-file-doc-type">${file.doc_type}</span>
                                    <span>${file.word_count} words</span>
                                </div>
                            </div>
                            <div class="tex-file-actions">
                                ${giteaLink}
                                <div class="tex-file-status saved" title="Saved"></div>
                            </div>
                        </div>
                    `;
                });
            }
        });

        texFilesListContainer.innerHTML = html;

        // Add click handlers
        document.querySelectorAll('.tex-file-item').forEach(item => {
            item.addEventListener('click', () => {
                const section = item.dataset.section;
                const docType = item.dataset.docType;
                switchToTexFile(section, docType);
            });
        });
    }

    function switchToTexFile(section, docType) {
        console.log(`[TeX Browser] Switching to ${docType}/${section}`);

        // Check for unsaved changes
        if (hasUnsavedChanges) {
            if (!confirm('You have unsaved changes. Do you want to switch files? (Changes will be lost)')) {
                return;
            }
        }

        // Update current file
        currentTexFile = {section, doc_type: docType};

        // Switch document type if needed
        if (currentDocType !== docType) {
            const doctypeSelector = document.getElementById('doctype-selector');
            if (doctypeSelector) {
                doctypeSelector.value = docType;
                currentDocType = docType;
            }
        }

        // Switch section
        currentSection = section;

        // Load the section content
        loadSection(section);

        // Update UI
        renderTexFilesList();
        updateSectionList();
    }

    function updateFileStatus(section, docType, status) {
        const fileItem = texFilesListContainer.querySelector(
            `.tex-file-item[data-section="${section}"][data-doc-type="${docType}"]`
        );

        if (fileItem) {
            const statusIndicator = fileItem.querySelector('.tex-file-status');
            if (statusIndicator) {
                statusIndicator.classList.remove('saved', 'modified');
                statusIndicator.classList.add(status);
                statusIndicator.title = status === 'saved' ? 'Saved' : 'Modified';
            }

            if (status === 'modified') {
                fileItem.classList.add('modified');
            } else {
                fileItem.classList.remove('modified');
            }
        }
    }

    // Refresh button handler
    if (refreshFilesBtn) {
        refreshFilesBtn.addEventListener('click', () => {
            console.log('[TeX Browser] Refreshing file list');
            loadTexFilesList();
        });
    }

    // Load files on initialization
    if (writerInitialized || isDemo) {
        loadTexFilesList();
    }

    // Hook into save/load to update file status
    const originalMarkAsUnsaved = markAsUnsaved;
    markAsUnsaved = function(section) {
        originalMarkAsUnsaved(section);
        updateFileStatus(section, currentDocType, 'modified');
    };

    const originalMarkAsSaved = markAsSaved;
    markAsSaved = function(section) {
        originalMarkAsSaved(section);
        updateFileStatus(section, currentDocType, 'saved');
    };

    // Initialize real-time collaboration (Phase 1.1 - WebSocket)
    if (window.WRITER_CONFIG?.isAuthenticated && window.WRITER_CONFIG?.projectId) {
        console.log('[Writer] Initializing collaboration');
        const collaboration = new WriterCollaboration(
            window.WRITER_CONFIG.projectId,
            window.WRITER_CONFIG.userId,
            window.WRITER_CONFIG.username
        );
        window.collaboration = collaboration;

        // Integrate with Writer UI
        collaboration.integrateWithWriter();

        console.log('✓ Real-time collaboration initialized with section locking');
    }

    // ========================================================================
    // NEW UI IMPROVEMENTS - Sidebar Toggle, View Tabs, Floating Panel, etc.
    // ========================================================================

    // 1. SIDEBAR TOGGLE FUNCTIONALITY
    // ========================================================================
    const toggleSidebarBtn = document.getElementById('toggle-sidebar');
    const writerSidebar = document.querySelector('.writer-sidebar');
    const mainEditor = document.querySelector('.writer-main-editor');

    if (toggleSidebarBtn && writerSidebar) {
        console.log('[Writer] Initializing sidebar toggle');

        // Load saved sidebar state from localStorage
        const sidebarCollapsed = localStorage.getItem(`sidebar_collapsed_${projectId}`) === 'true';
        if (sidebarCollapsed) {
            writerSidebar.classList.add('collapsed');
            console.log('[Writer] Sidebar restored to collapsed state');
        }

        // Add click event listener
        toggleSidebarBtn.addEventListener('click', function() {
            const isCollapsed = writerSidebar.classList.toggle('collapsed');

            // Save state to localStorage
            localStorage.setItem(`sidebar_collapsed_${projectId}`, isCollapsed);

            console.log('[Writer] Sidebar toggled:', isCollapsed ? 'collapsed' : 'expanded');

            // Update icon
            const icon = this.querySelector('i');
            if (icon) {
                if (isCollapsed) {
                    icon.classList.remove('fa-bars');
                    icon.classList.add('fa-arrow-right');
                } else {
                    icon.classList.remove('fa-arrow-right');
                    icon.classList.add('fa-bars');
                }
            }
        });
    }

    // 2. EDITOR VIEW TABS FUNCTIONALITY
    // ========================================================================
    const viewTabs = document.querySelectorAll('.view-tab');
    const editorViewLatex = document.getElementById('editor-view-latex');
    const editorViewPreview = document.getElementById('editor-view-preview');
    const editorViewSplit = document.getElementById('editor-view-split');

    if (viewTabs.length > 0) {
        console.log('[Writer] Initializing view tabs');

        // Load saved view preference from localStorage
        const savedView = localStorage.getItem(`editor_view_${projectId}`) || 'split';
        switchEditorView(savedView);

        // Add click event listeners to all view tabs
        viewTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const view = this.dataset.view;
                switchEditorView(view);

                // Save preference to localStorage
                localStorage.setItem(`editor_view_${projectId}`, view);

                console.log('[Writer] View switched to:', view);
            });
        });
    }

    function switchEditorView(view) {
        // Remove active class from all tabs
        viewTabs.forEach(tab => tab.classList.remove('active'));

        // Add active class to selected tab
        const activeTab = document.querySelector(`.view-tab[data-view="${view}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }

        // Hide all views
        if (editorViewLatex) editorViewLatex.style.display = 'none';
        if (editorViewPreview) editorViewPreview.style.display = 'none';
        if (editorViewSplit) editorViewSplit.style.display = 'none';

        // Show selected view
        switch(view) {
            case 'latex':
                if (editorViewLatex) {
                    editorViewLatex.style.display = 'flex';
                    // Refresh CodeMirror if it exists
                    if (codeMirrorEditor) {
                        setTimeout(() => codeMirrorEditor.refresh(), 100);
                    }
                }
                break;
            case 'preview':
                if (editorViewPreview) {
                    editorViewPreview.style.display = 'flex';
                }
                break;
            case 'split':
                if (editorViewSplit) {
                    editorViewSplit.style.display = 'flex';
                    // Refresh CodeMirror if it exists
                    if (codeMirrorEditor) {
                        setTimeout(() => codeMirrorEditor.refresh(), 100);
                    }
                }
                break;
        }

        console.log('[Writer] View switched to:', view);
    }

    // 3. FLOATING SECTION PANEL FUNCTIONALITY
    // ========================================================================
    const toggleSectionPanelBtn = document.getElementById('toggle-section-panel');
    const floatingPanel = document.getElementById('floating-section-panel');

    if (toggleSectionPanelBtn && floatingPanel) {
        console.log('[Writer] Initializing floating section panel');

        // Load saved panel state and position from localStorage
        const panelVisible = localStorage.getItem(`section_panel_visible_${projectId}`) === 'true';
        const panelTop = localStorage.getItem(`section_panel_top_${projectId}`) || '80px';
        const panelRight = localStorage.getItem(`section_panel_right_${projectId}`) || '2rem';

        if (panelVisible) {
            floatingPanel.style.display = 'block';
            floatingPanel.style.top = panelTop;
            floatingPanel.style.right = panelRight;
            console.log('[Writer] Section panel restored to visible state');
        }

        // Toggle panel visibility
        toggleSectionPanelBtn.addEventListener('click', function() {
            const isVisible = floatingPanel.style.display !== 'none';

            if (isVisible) {
                floatingPanel.style.display = 'none';
                localStorage.setItem(`section_panel_visible_${projectId}`, 'false');
                console.log('[Writer] Section panel hidden');
            } else {
                floatingPanel.style.display = 'block';
                localStorage.setItem(`section_panel_visible_${projectId}`, 'true');
                console.log('[Writer] Section panel shown');
            }
        });

        // Make panel draggable
        makeDraggable(floatingPanel);
    }

    function makeDraggable(element) {
        let isDragging = false;
        let currentX;
        let currentY;
        let initialX;
        let initialY;
        let xOffset = 0;
        let yOffset = 0;

        const header = element.querySelector('.floating-panel-header');
        if (!header) return;

        header.style.cursor = 'move';

        header.addEventListener('mousedown', dragStart);
        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', dragEnd);

        function dragStart(e) {
            const rect = element.getBoundingClientRect();
            initialX = e.clientX - rect.left;
            initialY = e.clientY - rect.top;

            isDragging = true;
        }

        function drag(e) {
            if (!isDragging) return;

            e.preventDefault();

            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;

            xOffset = currentX;
            yOffset = currentY;

            // Calculate position from top and right
            const top = currentY;
            const right = window.innerWidth - currentX - element.offsetWidth;

            element.style.top = top + 'px';
            element.style.right = right + 'px';
        }

        function dragEnd(e) {
            if (!isDragging) return;

            initialX = currentX;
            initialY = currentY;
            isDragging = false;

            // Save position to localStorage
            localStorage.setItem(`section_panel_top_${projectId}`, element.style.top);
            localStorage.setItem(`section_panel_right_${projectId}`, element.style.right);

            console.log('[Writer] Section panel position saved:', element.style.top, element.style.right);
        }
    }

    // 4. COMPILE TOOLBAR BUTTON FUNCTIONALITY
    // ========================================================================
    const compileToolbarBtn = document.getElementById('compile-btn-toolbar');
    let compileOutputDiv = null;

    if (compileToolbarBtn) {
        console.log('[Writer] Initializing compile toolbar button');

        compileToolbarBtn.addEventListener('click', function() {
            console.log('[Writer] Compile button clicked (toolbar)');

            // Check if we're in demo mode or not initialized
            if (isDemo || !writerInitialized) {
                console.log('[Writer] Demo mode or not initialized - showing demo message');
                showCompileDemo();
                return;
            }

            // Trigger compilation
            compileDocument();
        });
    }

    function showCompileDemo() {
        // Create or get compile output div
        if (!compileOutputDiv) {
            compileOutputDiv = document.createElement('div');
            compileOutputDiv.id = 'compile-output';
            compileOutputDiv.className = 'compile-output';
            compileOutputDiv.style.cssText = `
                margin-top: 1rem;
                padding: 1rem;
                background: var(--color-canvas-subtle);
                border: 1px solid var(--color-border-default);
                border-radius: 0.375rem;
                font-family: monospace;
                font-size: 0.875rem;
            `;

            // Insert after the editor toolbar
            const toolbar = document.querySelector('.writer-toolbar-sticky');
            if (toolbar && toolbar.parentNode) {
                toolbar.parentNode.insertBefore(compileOutputDiv, toolbar.nextSibling);
            }
        }

        // Show demo compilation output
        compileOutputDiv.innerHTML = `
            <div style="color: var(--color-attention-fg);">
                <strong>Demo Mode:</strong> LaTeX compilation is available for authenticated users with initialized projects.
            </div>
            <div style="margin-top: 0.5rem; color: var(--color-fg-muted);">
                Create an account and initialize your writer workspace to use this feature.
            </div>
        `;
        compileOutputDiv.style.display = 'block';

        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (compileOutputDiv) {
                compileOutputDiv.style.display = 'none';
            }
        }, 5000);
    }

    function compileDocument() {
        // Show loading state
        if (compileToolbarBtn) {
            const originalHtml = compileToolbarBtn.innerHTML;
            compileToolbarBtn.disabled = true;
            compileToolbarBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Compiling...';

            // Create or get compile output div
            if (!compileOutputDiv) {
                compileOutputDiv = document.createElement('div');
                compileOutputDiv.id = 'compile-output';
                compileOutputDiv.className = 'compile-output';
                compileOutputDiv.style.cssText = `
                    margin-top: 1rem;
                    padding: 1rem;
                    background: var(--color-canvas-subtle);
                    border: 1px solid var(--color-border-default);
                    border-radius: 0.375rem;
                    font-family: monospace;
                    font-size: 0.875rem;
                    max-height: 300px;
                    overflow-y: auto;
                `;

                // Insert after the editor toolbar
                const toolbar = document.querySelector('.writer-toolbar-sticky');
                if (toolbar && toolbar.parentNode) {
                    toolbar.parentNode.insertBefore(compileOutputDiv, toolbar.nextSibling);
                }
            }

            compileOutputDiv.innerHTML = '<div style="color: var(--color-attention-fg);"><i class="fas fa-spinner fa-spin me-2"></i>Starting compilation...</div>';
            compileOutputDiv.style.display = 'block';

            // Make API call to compile endpoint
            fetch(`/writer/project/${projectId}/compile/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    doc_type: currentDocType
                })
            })
            .then(response => response.json())
            .then(data => {
                compileToolbarBtn.disabled = false;
                compileToolbarBtn.innerHTML = originalHtml;

                if (data.success) {
                    console.log('[Writer] Compilation started:', data.job_id);
                    compileOutputDiv.innerHTML = `
                        <div style="color: var(--color-success-fg);">
                            <i class="fas fa-check-circle me-2"></i>Compilation started successfully
                        </div>
                        <div style="margin-top: 0.5rem; color: var(--color-fg-muted);">
                            Job ID: ${data.job_id}
                        </div>
                        <div style="margin-top: 0.5rem; color: var(--color-fg-muted);">
                            Status: ${data.status || 'Processing...'}
                        </div>
                    `;

                    // Poll for compilation status
                    if (data.job_id) {
                        pollCompilationStatus(data.job_id);
                    }
                } else {
                    console.error('[Writer] Compilation failed:', data.error);
                    compileOutputDiv.innerHTML = `
                        <div style="color: var(--color-danger-fg);">
                            <i class="fas fa-exclamation-circle me-2"></i>Compilation failed
                        </div>
                        <div style="margin-top: 0.5rem; color: var(--color-fg-muted);">
                            ${data.error || 'Unknown error'}
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('[Writer] Compilation error:', error);
                compileToolbarBtn.disabled = false;
                compileToolbarBtn.innerHTML = originalHtml;

                compileOutputDiv.innerHTML = `
                    <div style="color: var(--color-danger-fg);">
                        <i class="fas fa-exclamation-circle me-2"></i>Error
                    </div>
                    <div style="margin-top: 0.5rem; color: var(--color-fg-muted);">
                        ${error.message}
                    </div>
                `;
            });
        }
    }

    function pollCompilationStatus(jobId) {
        console.log('[Writer] Polling compilation status for job:', jobId);

        const pollInterval = setInterval(() => {
            fetch(`/writer/project/${projectId}/compile-status/?job_id=${jobId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'completed') {
                    clearInterval(pollInterval);
                    compileOutputDiv.innerHTML = `
                        <div style="color: var(--color-success-fg);">
                            <i class="fas fa-check-circle me-2"></i>Compilation completed successfully
                        </div>
                        <div style="margin-top: 0.5rem;">
                            <a href="${data.pdf_url}" target="_blank" class="btn btn-sm btn-primary">
                                <i class="fas fa-file-pdf me-1"></i>View PDF
                            </a>
                        </div>
                    `;
                    console.log('[Writer] Compilation completed:', data.pdf_url);
                } else if (data.status === 'failed') {
                    clearInterval(pollInterval);
                    compileOutputDiv.innerHTML = `
                        <div style="color: var(--color-danger-fg);">
                            <i class="fas fa-exclamation-circle me-2"></i>Compilation failed
                        </div>
                        <div style="margin-top: 0.5rem; color: var(--color-fg-muted);">
                            ${data.error || 'Unknown error'}
                        </div>
                    `;
                    console.error('[Writer] Compilation failed:', data.error);
                } else {
                    // Still processing
                    compileOutputDiv.innerHTML = `
                        <div style="color: var(--color-attention-fg);">
                            <i class="fas fa-spinner fa-spin me-2"></i>Compiling...
                        </div>
                        <div style="margin-top: 0.5rem; color: var(--color-fg-muted);">
                            Status: ${data.status || 'Processing...'}
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('[Writer] Error polling status:', error);
                clearInterval(pollInterval);
            });
        }, 2000); // Poll every 2 seconds
    }

    // 5. SAVE STATUS INDICATOR ENHANCEMENT
    // ========================================================================
    const saveStatusIndicator = document.getElementById('save-status');

    if (saveStatusIndicator) {
        console.log('[Writer] Initializing save status indicator');

        // Override the markAsSaved and markAsUnsaved functions to update toolbar status
        const originalMarkAsSaved2 = markAsSaved;
        markAsSaved = function(section) {
            originalMarkAsSaved2(section);
            updateSaveStatus('saved', new Date().toLocaleTimeString());
        };

        const originalMarkAsUnsaved2 = markAsUnsaved;
        markAsUnsaved = function(section) {
            originalMarkAsUnsaved2(section);
            updateSaveStatus('modified');
        };

        // Also wrap saveCurrentSectionManually to show saving state
        if (typeof saveCurrentSectionManually !== 'undefined') {
            const originalSave = saveCurrentSectionManually;
            saveCurrentSectionManually = function() {
                updateSaveStatus('saving');
                return originalSave.apply(this, arguments);
            };
        }
    }

    function updateSaveStatus(status, timestamp = null) {
        if (!saveStatusIndicator) return;

        // Remove all status classes
        saveStatusIndicator.classList.remove('saving', 'saved', 'error');

        // Get icon and text elements
        const icon = saveStatusIndicator.querySelector('i');
        const statusText = saveStatusIndicator.querySelector('.status-text');

        switch(status) {
            case 'saving':
                saveStatusIndicator.classList.add('saving');
                if (icon) {
                    icon.className = 'fas fa-spinner fa-spin text-warning';
                }
                if (statusText) {
                    statusText.textContent = 'Saving...';
                }
                console.log('[Writer] Save status: saving');
                break;

            case 'saved':
                saveStatusIndicator.classList.add('saved');
                if (icon) {
                    icon.className = 'fas fa-check-circle text-success';
                }
                if (statusText) {
                    const time = timestamp || new Date().toLocaleTimeString();
                    statusText.textContent = `Saved ${time}`;
                }
                console.log('[Writer] Save status: saved');
                break;

            case 'modified':
                // Don't add a specific class, just show modified state
                if (icon) {
                    icon.className = 'fas fa-circle text-warning';
                }
                if (statusText) {
                    statusText.textContent = 'Modified';
                }
                console.log('[Writer] Save status: modified');
                break;

            case 'error':
                saveStatusIndicator.classList.add('error');
                if (icon) {
                    icon.className = 'fas fa-exclamation-circle text-danger';
                }
                if (statusText) {
                    statusText.textContent = 'Error saving';
                }
                console.log('[Writer] Save status: error');
                break;
        }
    }

    // Expose updateSaveStatus globally so it can be called from save operations
    window.updateSaveStatus = updateSaveStatus;

    console.log('[Writer] All new UI improvements initialized');

}); // Close DOMContentLoaded
1
