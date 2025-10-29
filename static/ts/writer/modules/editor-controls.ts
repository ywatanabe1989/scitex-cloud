/**
 * Editor Controls Module
 * Handles font size adjustment and auto-preview functionality
 */

export interface EditorControlsOptions {
    pdfPreviewManager?: any;
    compilationManager?: any;
}

export class EditorControls {
    private fontSizeSlider: HTMLInputElement | null;
    private fontSizeDisplay: HTMLElement | null;
    private autoPreviewCheckbox: HTMLInputElement | null;
    private previewButton: HTMLButtonElement | null;
    private latexEditor: HTMLTextAreaElement | null;
    private pdfPreviewManager: any;
    // @ts-ignore - compilation manager available for future use
    private _compilationManager: any;
    private autoPreviewTimeout: ReturnType<typeof setTimeout> | null = null;
    private defaultFontSize: number = 14;
    private storageFontSizeKey: string = 'scitex-editor-font-size';
    private storageAutoPreviewKey: string = 'scitex-auto-preview';

    constructor(options: EditorControlsOptions = {}) {
        this.fontSizeSlider = document.getElementById('font-size-slider') as HTMLInputElement;
        this.fontSizeDisplay = document.getElementById('font-size-display');
        this.autoPreviewCheckbox = document.getElementById('auto-preview-checkbox') as HTMLInputElement;
        this.previewButton = document.getElementById('preview-btn-toolbar') as HTMLButtonElement;
        this.latexEditor = document.getElementById('latex-editor-textarea') as HTMLTextAreaElement;
        this.pdfPreviewManager = options.pdfPreviewManager;
        this._compilationManager = options.compilationManager;

        if (this.fontSizeSlider || this.autoPreviewCheckbox || this.previewButton) {
            this.initialize();
        }
    }

    /**
     * Initialize editor controls with event listeners
     */
    private initialize(): void {
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
    private handleFontSizeChange(event: Event): void {
        const target = event.target as HTMLInputElement;
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
    private loadFontSize(): void {
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
    private handleAutoPreviewToggle(event: Event): void {
        const target = event.target as HTMLInputElement;
        const isEnabled = target.checked;

        // Save preference to localStorage
        localStorage.setItem(this.storageAutoPreviewKey, isEnabled ? 'true' : 'false');

        if (isEnabled) {
            this.setupAutoPreviewTrigger();
            console.log('[EditorControls] Auto preview enabled');
        } else {
            this.clearAutoPreviewTimeout();
            console.log('[EditorControls] Auto preview disabled');
        }
    }

    /**
     * Load auto-preview preference from localStorage
     */
    private loadAutoPreviewPreference(): void {
        const saved = localStorage.getItem(this.storageAutoPreviewKey);
        const isEnabled = saved !== 'false'; // Default to true

        if (this.autoPreviewCheckbox) {
            this.autoPreviewCheckbox.checked = isEnabled;
        }
    }

    /**
     * Setup auto-preview trigger on editor changes
     */
    private setupAutoPreviewTrigger(): void {
        if (!this.latexEditor) return;

        this.latexEditor.addEventListener('input', () => {
            if (!this.autoPreviewCheckbox || !this.autoPreviewCheckbox.checked) return;

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
    private clearAutoPreviewTimeout(): void {
        if (this.autoPreviewTimeout) {
            clearTimeout(this.autoPreviewTimeout);
            this.autoPreviewTimeout = null;
        }
    }

    /**
     * Handle preview button click
     */
    private handlePreviewClick(event: Event): void {
        event.preventDefault();
        console.log('[EditorControls] Preview button clicked');
        this.triggerPreview();
    }

    /**
     * Trigger PDF preview compilation
     */
    private triggerPreview(): void {
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
    public setPDFPreviewManager(pdfPreviewManager: any): void {
        this.pdfPreviewManager = pdfPreviewManager;
    }

    /**
     * Set compilation manager reference (for dynamic initialization)
     */
    public setCompilationManager(compilationManager: any): void {
        this._compilationManager = compilationManager;
    }

    /**
     * Get current font size
     */
    public getFontSize(): number {
        if (this.fontSizeSlider) {
            return parseInt(this.fontSizeSlider.value, 10);
        }
        return this.defaultFontSize;
    }

    /**
     * Set font size programmatically
     */
    public setFontSize(fontSize: number): void {
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
    public isAutoPreviewEnabled(): boolean {
        return this.autoPreviewCheckbox ? this.autoPreviewCheckbox.checked : false;
    }

    /**
     * Set auto-preview enabled state
     */
    public setAutoPreviewEnabled(enabled: boolean): void {
        if (this.autoPreviewCheckbox) {
            this.autoPreviewCheckbox.checked = enabled;
            const event = new Event('change', { bubbles: true });
            this.autoPreviewCheckbox.dispatchEvent(event);
        }
    }
}
