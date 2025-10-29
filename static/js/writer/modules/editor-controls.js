/**
 * Editor Controls Module
 * Handles font size adjustment and auto-preview functionality
 */
export class EditorControls {
    constructor(options = {}) {
        this.autoPreviewTimeout = null;
        this.defaultFontSize = 14;
        this.storageFontSizeKey = 'scitex-editor-font-size';
        this.storageAutoPreviewKey = 'scitex-auto-preview';
        this.fontSizeSlider = document.getElementById('font-size-slider');
        this.fontSizeDisplay = document.getElementById('font-size-display');
        this.autoPreviewCheckbox = document.getElementById('auto-preview-checkbox');
        this.previewButton = document.getElementById('preview-btn-toolbar');
        this.latexEditor = document.getElementById('latex-editor-textarea');
        this.pdfPreviewManager = options.pdfPreviewManager;
        this._compilationManager = options.compilationManager;
        if (this.fontSizeSlider || this.autoPreviewCheckbox || this.previewButton) {
            this.initialize();
        }
    }
    /**
     * Initialize editor controls with event listeners
     */
    initialize() {
        // Font size control
        if (this.fontSizeSlider && this.fontSizeDisplay) {
            this.loadFontSize();
            this.fontSizeSlider.addEventListener('input', this.handleFontSizeChange.bind(this));
            console.log('[EditorControls] Font size slider initialized');
        }
        // Auto preview control
        if (this.autoPreviewCheckbox) {
            this.loadAutoPreviewPreference();
            this.autoPreviewCheckbox.addEventListener('change', this.handleAutoPreviewToggle.bind(this));
            console.log('[EditorControls] Auto preview checkbox initialized');
        }
        // Preview button
        if (this.previewButton) {
            this.previewButton.addEventListener('click', this.handlePreviewClick.bind(this));
            console.log('[EditorControls] Preview button initialized');
        }
        // Setup auto-preview trigger on editor changes
        if (this.latexEditor && this.autoPreviewCheckbox && this.autoPreviewCheckbox.checked) {
            this.setupAutoPreviewTrigger();
        }
        console.log('[EditorControls] All controls initialized');
    }
    /**
     * Handle font size slider change
     */
    handleFontSizeChange(event) {
        const target = event.target;
        const fontSize = parseInt(target.value, 10);
        if (this.latexEditor) {
            this.latexEditor.style.fontSize = `${fontSize}px`;
        }
        if (this.fontSizeDisplay) {
            this.fontSizeDisplay.textContent = fontSize.toString();
        }
        // Save to localStorage
        localStorage.setItem(this.storageFontSizeKey, fontSize.toString());
        console.log(`[EditorControls] Font size changed to ${fontSize}px`);
    }
    /**
     * Load font size from localStorage
     */
    loadFontSize() {
        const saved = localStorage.getItem(this.storageFontSizeKey);
        const fontSize = saved ? parseInt(saved, 10) : this.defaultFontSize;
        if (this.fontSizeSlider) {
            this.fontSizeSlider.value = fontSize.toString();
        }
        if (this.latexEditor) {
            this.latexEditor.style.fontSize = `${fontSize}px`;
        }
        if (this.fontSizeDisplay) {
            this.fontSizeDisplay.textContent = fontSize.toString();
        }
        console.log(`[EditorControls] Loaded font size: ${fontSize}px`);
    }
    /**
     * Handle auto preview checkbox toggle
     */
    handleAutoPreviewToggle(event) {
        const target = event.target;
        const isEnabled = target.checked;
        // Save preference to localStorage
        localStorage.setItem(this.storageAutoPreviewKey, isEnabled ? 'true' : 'false');
        if (isEnabled) {
            this.setupAutoPreviewTrigger();
            console.log('[EditorControls] Auto preview enabled');
        }
        else {
            this.clearAutoPreviewTimeout();
            console.log('[EditorControls] Auto preview disabled');
        }
    }
    /**
     * Load auto-preview preference from localStorage
     */
    loadAutoPreviewPreference() {
        const saved = localStorage.getItem(this.storageAutoPreviewKey);
        const isEnabled = saved !== 'false'; // Default to true
        if (this.autoPreviewCheckbox) {
            this.autoPreviewCheckbox.checked = isEnabled;
        }
    }
    /**
     * Setup auto-preview trigger on editor changes
     */
    setupAutoPreviewTrigger() {
        if (!this.latexEditor)
            return;
        this.latexEditor.addEventListener('input', () => {
            if (!this.autoPreviewCheckbox || !this.autoPreviewCheckbox.checked)
                return;
            // Clear existing timeout
            this.clearAutoPreviewTimeout();
            // Schedule auto-compile after 5 seconds of inactivity
            this.autoPreviewTimeout = setTimeout(() => {
                this.triggerPreview();
            }, 5000); // 5 second delay
            console.log('[EditorControls] Auto-preview scheduled for 5s');
        });
    }
    /**
     * Clear auto-preview timeout
     */
    clearAutoPreviewTimeout() {
        if (this.autoPreviewTimeout) {
            clearTimeout(this.autoPreviewTimeout);
            this.autoPreviewTimeout = null;
        }
    }
    /**
     * Handle preview button click
     */
    handlePreviewClick(event) {
        event.preventDefault();
        console.log('[EditorControls] Preview button clicked');
        this.triggerPreview();
    }
    /**
     * Trigger PDF preview compilation
     */
    triggerPreview() {
        if (this.pdfPreviewManager && this.latexEditor) {
            const editorContent = this.latexEditor.value;
            if (editorContent.trim()) {
                console.log('[EditorControls] Triggering PDF preview compilation');
                // Use quick compile for live preview (text only)
                this.pdfPreviewManager.compileQuick(editorContent);
            }
        }
    }
    /**
     * Set PDF preview manager reference (for dynamic initialization)
     */
    setPDFPreviewManager(pdfPreviewManager) {
        this.pdfPreviewManager = pdfPreviewManager;
    }
    /**
     * Set compilation manager reference (for dynamic initialization)
     */
    setCompilationManager(compilationManager) {
        this._compilationManager = compilationManager;
    }
    /**
     * Get current font size
     */
    getFontSize() {
        if (this.fontSizeSlider) {
            return parseInt(this.fontSizeSlider.value, 10);
        }
        return this.defaultFontSize;
    }
    /**
     * Set font size programmatically
     */
    setFontSize(fontSize) {
        if (fontSize >= 10 && fontSize <= 20) {
            if (this.fontSizeSlider) {
                this.fontSizeSlider.value = fontSize.toString();
                const event = new Event('input', { bubbles: true });
                this.fontSizeSlider.dispatchEvent(event);
            }
        }
    }
    /**
     * Check if auto-preview is enabled
     */
    isAutoPreviewEnabled() {
        return this.autoPreviewCheckbox ? this.autoPreviewCheckbox.checked : false;
    }
    /**
     * Set auto-preview enabled state
     */
    setAutoPreviewEnabled(enabled) {
        if (this.autoPreviewCheckbox) {
            this.autoPreviewCheckbox.checked = enabled;
            const event = new Event('change', { bubbles: true });
            this.autoPreviewCheckbox.dispatchEvent(event);
        }
    }
}
//# sourceMappingURL=editor-controls.js.map