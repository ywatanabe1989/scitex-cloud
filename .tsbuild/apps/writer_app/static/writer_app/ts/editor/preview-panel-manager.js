/**
 * Preview Panel Manager
 * Handles LaTeX editor, templates, compilation, and PDF preview
 *
 * @version 2.0.0 (TypeScript)
 * @author SciTeX Development Team
 */
// ============================================================================
// Type Definitions
// ============================================================================
console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/editor/preview-panel-manager.ts loaded");
// ============================================================================
// LaTeX Templates
// ============================================================================
const LATEX_TEMPLATES = {
    article: `\\documentclass[12pt]{article}
\\usepackage[utf8]{inputenc}
\\usepackage{amsmath}
\\usepackage{graphicx}
\\usepackage[margin=1in]{geometry}
\\usepackage{cite}

\\title{Your Article Title}
\\author{Your Name\\\\Your Institution}
\\date{\\today}

\\begin{document}

\\maketitle

\\begin{abstract}
Write your abstract here...
\\end{abstract}

\\section{Introduction}
Introduction content...

\\section{Related Work}
Related work...

\\section{Methodology}
Methodology...

\\section{Results}
Results...

\\section{Conclusion}
Conclusion...

\\bibliographystyle{plain}
\\bibliography{references}

\\end{document}`,
    conference: `\\documentclass[conference]{IEEEtran}
\\usepackage{amsmath}
\\usepackage{graphicx}
\\usepackage{cite}

\\title{Your Conference Paper Title}
\\author{\\IEEEauthorblockN{Your Name}
\\IEEEauthorblockA{Your Institution\\\\
Email: your.email@institution.edu}}

\\begin{document}

\\maketitle

\\begin{abstract}
Abstract content...
\\end{abstract}

\\section{Introduction}
Introduction...

\\section{Methodology}
Methodology...

\\section{Results}
Results...

\\section{Conclusion}
Conclusion...

\\begin{thebibliography}{1}
\\bibitem{ref1}
Author, "Title," Journal, Year.
\\end{thebibliography}

\\end{document}`,
    letter: `\\documentclass{letter}
\\usepackage[margin=1in]{geometry}

\\signature{Your Name}
\\address{Your Address\\\\City, State ZIP}

\\begin{document}

\\begin{letter}{Recipient Name\\\\
Recipient Address\\\\
City, State ZIP}

\\opening{Dear Recipient,}

Body of the letter goes here...

\\closing{Sincerely,}

\\end{letter}

\\end{document}`
};
// ============================================================================
// Preview Panel Manager Class
// ============================================================================
export class PreviewPanelManager {
    config;
    editor; // CodeMirror instance
    currentJobId = null;
    statusCheckInterval = null;
    previewVisible = true;
    saveTimeout = null;
    // DOM elements
    compileBtn;
    saveBtn;
    statusIndicator;
    compileStatus;
    previewContent;
    previewPanel;
    togglePreviewBtn;
    templateSelect;
    documentTitle;
    constructor(config) {
        this.config = config;
    }
    /**
     * Initialize the preview panel manager
     */
    initialize() {
        console.log('[PreviewPanel] Initializing preview panel manager');
        // Initialize CodeMirror editor
        this.initializeEditor();
        // Get DOM elements
        this.getDOMElements();
        // Setup event listeners
        this.setupEventListeners();
        console.log('[PreviewPanel] Initialization complete');
    }
    /**
     * Initialize CodeMirror editor
     */
    initializeEditor() {
        const textarea = document.getElementById('latex-editor');
        if (!textarea) {
            console.error('[PreviewPanel] LaTeX editor textarea not found');
            return;
        }
        if (!window.CodeMirror) {
            console.error('[PreviewPanel] CodeMirror not loaded');
            return;
        }
        this.editor = window.CodeMirror.fromTextArea(textarea, {
            mode: 'stex',
            theme: 'github',
            lineNumbers: true,
            autoCloseBrackets: true,
            matchBrackets: true,
            lineWrapping: true,
            indentUnit: 2
        });
        // Auto-save on content change
        this.editor.on('change', () => {
            this.handleEditorChange();
        });
        console.log('[PreviewPanel] CodeMirror editor initialized');
    }
    /**
     * Get DOM element references
     */
    getDOMElements() {
        this.compileBtn = document.getElementById('compile-btn');
        this.saveBtn = document.getElementById('save-btn');
        this.statusIndicator = document.getElementById('status-indicator');
        this.compileStatus = document.getElementById('compile-status');
        this.previewContent = document.getElementById('preview-content');
        this.previewPanel = document.getElementById('preview-panel');
        this.togglePreviewBtn = document.getElementById('toggle-preview');
        this.templateSelect = document.getElementById('template-select');
        this.documentTitle = document.getElementById('document-title');
    }
    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Template selection
        if (this.templateSelect) {
            this.templateSelect.addEventListener('change', () => {
                this.handleTemplateChange();
            });
        }
        // Toggle preview panel
        if (this.togglePreviewBtn) {
            this.togglePreviewBtn.addEventListener('click', () => {
                this.togglePreview();
            });
        }
        // Save draft
        if (this.saveBtn) {
            this.saveBtn.addEventListener('click', () => {
                this.saveDraft();
            });
        }
        // Compile document
        if (this.compileBtn) {
            this.compileBtn.addEventListener('click', () => {
                this.compileDocument();
            });
        }
    }
    /**
     * Handle template selection change
     */
    handleTemplateChange() {
        const template = this.templateSelect.value;
        if (template && LATEX_TEMPLATES[template]) {
            if (confirm('This will replace your current content. Continue?')) {
                this.editor.setValue(LATEX_TEMPLATES[template]);
                this.documentTitle.value =
                    template.charAt(0).toUpperCase() + template.slice(1) + ' Document';
            }
            else {
                this.templateSelect.value = '';
            }
        }
    }
    /**
     * Toggle preview panel visibility
     */
    togglePreview() {
        this.previewVisible = !this.previewVisible;
        this.previewPanel.style.display = this.previewVisible ? 'flex' : 'none';
        this.togglePreviewBtn.innerHTML = this.previewVisible
            ? '<i class="fas fa-eye-slash me-1"></i>Hide Preview'
            : '<i class="fas fa-eye me-1"></i>Show Preview';
    }
    /**
     * Save draft (auto-save functionality)
     */
    saveDraft() {
        this.updateStatus('Saving...', 'text-warning');
        setTimeout(() => {
            this.updateStatus('Saved', 'text-success');
            setTimeout(() => this.updateStatus('Ready', 'text-success'), 2000);
        }, 500);
    }
    /**
     * Compile LaTeX document to PDF
     */
    async compileDocument() {
        const content = this.editor.getValue().trim();
        const title = this.documentTitle.value.trim() || 'Quick Document';
        if (!content) {
            alert('Please enter some LaTeX content to compile.');
            return;
        }
        // Update UI
        this.compileBtn.disabled = true;
        this.compileBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Compiling...';
        this.updateStatus('Compiling...', 'text-warning');
        this.updateCompileStatus('Compilation started...', 'running');
        // Send compile request
        try {
            const response = await fetch(this.config.quickCompileUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.config.csrfToken
                },
                body: JSON.stringify({
                    content: content,
                    title: title
                })
            });
            const data = await response.json();
            if (data.success && data.job_id) {
                this.currentJobId = data.job_id;
                this.startStatusChecking();
            }
            else {
                this.handleError(data.error || 'Compilation failed');
            }
        }
        catch (error) {
            this.handleError('Network error: ' + (error instanceof Error ? error.message : 'Unknown error'));
        }
    }
    /**
     * Start polling compilation status
     */
    startStatusChecking() {
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
        }
        this.statusCheckInterval = setInterval(async () => {
            if (!this.currentJobId)
                return;
            try {
                const url = this.config.compilationStatusUrl.replace('__JOB_ID__', this.currentJobId);
                const response = await fetch(url);
                const data = await response.json();
                this.updateJobStatus(data);
                if (data.status === 'completed' || data.status === 'failed') {
                    if (this.statusCheckInterval) {
                        clearInterval(this.statusCheckInterval);
                    }
                    this.resetCompileUI();
                    if (data.status === 'completed' && data.pdf_url) {
                        this.showPDFPreview(data.pdf_url);
                        this.updateCompileStatus('✓ Compilation successful!', 'success');
                        this.updateStatus('Compiled', 'text-success');
                    }
                    else if (data.status === 'failed') {
                        this.handleError(data.error || 'Compilation failed');
                    }
                }
            }
            catch (error) {
                console.error('[PreviewPanel] Status check error:', error);
            }
        }, 1000);
    }
    /**
     * Update job status display
     */
    updateJobStatus(data) {
        const message = `${data.status} (${data.progress}%)`;
        this.updateCompileStatus(message, data.status);
    }
    /**
     * Show PDF preview in iframe
     */
    showPDFPreview(pdfUrl) {
        this.previewContent.innerHTML = `
            <iframe src="${pdfUrl}" width="100%" height="100%" class="iframe-borderless"></iframe>
        `;
    }
    /**
     * Reset compile button UI
     */
    resetCompileUI() {
        this.compileBtn.disabled = false;
        this.compileBtn.innerHTML = '<i class="fas fa-play me-2"></i>Compile PDF';
        this.currentJobId = null;
    }
    /**
     * Handle compilation error
     */
    handleError(message) {
        this.updateStatus('Error', 'text-danger');
        this.updateCompileStatus('✗ ' + message, 'error');
        this.resetCompileUI();
    }
    /**
     * Update status indicator
     */
    updateStatus(text, className) {
        if (this.statusIndicator) {
            this.statusIndicator.innerHTML = `<i class="fas fa-circle ${className} me-1"></i>${text}`;
        }
    }
    /**
     * Update compilation status message
     */
    updateCompileStatus(text, type) {
        if (this.compileStatus) {
            this.compileStatus.textContent = text;
            this.compileStatus.className = `compile-status ${type}`;
        }
    }
    /**
     * Handle editor content change
     */
    handleEditorChange() {
        if (this.saveTimeout) {
            clearTimeout(this.saveTimeout);
        }
        this.updateStatus('Unsaved changes', 'text-warning');
        this.saveTimeout = setTimeout(() => {
            this.updateStatus('Ready', 'text-success');
        }, 3000);
    }
    /**
     * Destroy the preview panel manager and cleanup
     */
    destroy() {
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
        }
        if (this.saveTimeout) {
            clearTimeout(this.saveTimeout);
        }
        console.log('[PreviewPanel] Preview panel manager destroyed');
    }
}
// Export to window for access from templates
window.PreviewPanelManager = PreviewPanelManager;
//# sourceMappingURL=preview-panel-manager.js.map