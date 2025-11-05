/**
 * Editor Controls Module
 * Handles font size adjustment and auto-preview functionality
 */

console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/modules/editor-controls.ts loaded");
export interface EditorControlsOptions {
    pdfPreviewManager?: any;
    compilationManager?: any;
    editor?: any;
}

export class EditorControls {
    private fontSizeSelector: HTMLSelectElement | null;
    private autoPreviewCheckbox: HTMLInputElement | null;
    private autoPreviewCheckboxPanel: HTMLInputElement | null;
    private previewButton: HTMLButtonElement | null;
    private previewButtonPanel: HTMLButtonElement | null;
    private latexEditor: HTMLTextAreaElement | null;
    private pdfPreviewManager: any;
    private editor: any;
    // @ts-ignore - compilation manager available for future use
    private _compilationManager: any;
    private autoPreviewTimeout: ReturnType<typeof setTimeout> | null = null;
    private defaultFontSize: number = 14;
    private storageFontSizeKey: string = 'scitex-editor-font-size';
    private storageAutoPreviewKey: string = 'scitex-auto-preview';

    constructor(options: EditorControlsOptions = {}) {
        this.fontSizeSelector = document.getElementById('font-size-selector') as HTMLSelectElement;
        this.autoPreviewCheckbox = document.getElementById('auto-preview-checkbox') as HTMLInputElement;
        this.autoPreviewCheckboxPanel = document.getElementById('auto-preview-checkbox-panel') as HTMLInputElement;
        this.previewButton = document.getElementById('preview-btn-toolbar') as HTMLButtonElement;
        this.previewButtonPanel = document.getElementById('preview-btn-panel') as HTMLButtonElement;
        this.latexEditor = document.getElementById('latex-editor-textarea') as HTMLTextAreaElement;
        this.pdfPreviewManager = options.pdfPreviewManager;
        this.editor = options.editor;
        this._compilationManager = options.compilationManager;

        if (this.fontSizeSelector || this.autoPreviewCheckbox || this.previewButton) {
            this.initialize();
        }
    }

    /**
     * Initialize editor controls with event listeners
     */
    private initialize(): void {
        // Font size control
        if (this.fontSizeSelector) {
            this.loadFontSize();
            this.fontSizeSelector.addEventListener('change', this.handleFontSizeChange.bind(this));
            console.log('[EditorControls] Font size selector initialized');
        }

        // Ctrl+Middle mouse drag for font size
        this.setupFontSizeDrag();

        // Auto preview control - toolbar checkbox
        if (this.autoPreviewCheckbox) {
            this.loadAutoPreviewPreference();
            this.autoPreviewCheckbox.addEventListener('change', (e) => {
                this.handleAutoPreviewToggle(e);
                // Sync panel checkbox
                if (this.autoPreviewCheckboxPanel) {
                    this.autoPreviewCheckboxPanel.checked = (e.target as HTMLInputElement).checked;
                }
            });
            console.log('[EditorControls] Auto preview checkbox (toolbar) initialized');
        }

        // Auto preview control - panel checkbox
        if (this.autoPreviewCheckboxPanel) {
            this.loadAutoPreviewPreference(this.autoPreviewCheckboxPanel);
            this.autoPreviewCheckboxPanel.addEventListener('change', (e) => {
                this.handleAutoPreviewToggle(e);
                // Sync toolbar checkbox
                if (this.autoPreviewCheckbox) {
                    this.autoPreviewCheckbox.checked = (e.target as HTMLInputElement).checked;
                }
            });
            console.log('[EditorControls] Auto preview checkbox (panel) initialized');
        }

        // Preview button - toolbar
        if (this.previewButton) {
            this.previewButton.addEventListener('click', this.handlePreviewClick.bind(this));
            console.log('[EditorControls] Preview button (toolbar) initialized');
        }

        // Preview button - panel
        if (this.previewButtonPanel) {
            this.previewButtonPanel.addEventListener('click', this.handlePreviewClick.bind(this));
            console.log('[EditorControls] Preview button (panel) initialized');
        }

        // Setup auto-preview trigger on editor changes
        const autoPreviewEnabled = (this.autoPreviewCheckbox && this.autoPreviewCheckbox.checked) ||
                                   (this.autoPreviewCheckboxPanel && this.autoPreviewCheckboxPanel.checked);
        if (this.latexEditor && autoPreviewEnabled) {
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

        // Update textarea (for CodeMirror fallback)
        if (this.latexEditor) {
            this.latexEditor.style.fontSize = `${fontSize}px`;
        }

        // Update Monaco editor if available
        if (this.editor && this.editor.getEditorType && this.editor.getEditorType() === 'monaco') {
            const monacoInstance = this.editor.getInstance();
            if (monacoInstance && monacoInstance.updateOptions) {
                monacoInstance.updateOptions({ fontSize: fontSize });
                console.log(`[EditorControls] Monaco font size updated to ${fontSize}px`);
            }
        }

        // Update CodeMirror if available
        const cmEditor = (document.querySelector('.CodeMirror') as any)?.CodeMirror;
        if (cmEditor && cmEditor.getOption) {
            const currentSize = cmEditor.getOption('fontSize');
            if (currentSize !== `${fontSize}px`) {
                cmEditor.refresh();
                // Apply font size via CSS for CodeMirror
                const cmElement = document.querySelector('.CodeMirror') as HTMLElement;
                if (cmElement) {
                    cmElement.style.fontSize = `${fontSize}px`;
                }
                console.log(`[EditorControls] CodeMirror font size updated to ${fontSize}px`);
            }
        }

        // Update PDF compilation font size
        if (this.pdfPreviewManager && this.pdfPreviewManager.setFontSize) {
            this.pdfPreviewManager.setFontSize(fontSize);
            console.log(`[EditorControls] PDF font size updated to ${fontSize}px`);
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

        if (this.fontSizeSelector) {
            this.fontSizeSelector.value = fontSize.toString();
        }

        // Apply to all editors
        this.applyFontSizeToAllEditors(fontSize);

        console.log(`[EditorControls] Loaded font size: ${fontSize}px`);
    }

    /**
     * Apply font size to all editors (Monaco, CodeMirror, PDF)
     */
    private applyFontSizeToAllEditors(fontSize: number): void {
        // Update textarea
        if (this.latexEditor) {
            this.latexEditor.style.fontSize = `${fontSize}px`;
        }

        // Update Monaco editor if available
        if (this.editor && this.editor.getEditorType && this.editor.getEditorType() === 'monaco') {
            const monacoInstance = this.editor.getInstance();
            if (monacoInstance && monacoInstance.updateOptions) {
                monacoInstance.updateOptions({ fontSize: fontSize });
            }
        }

        // Update CodeMirror if available
        const cmElement = document.querySelector('.CodeMirror') as HTMLElement;
        if (cmElement) {
            cmElement.style.fontSize = `${fontSize}px`;
        }

        // Update PDF compilation font size
        if (this.pdfPreviewManager && this.pdfPreviewManager.setFontSize) {
            this.pdfPreviewManager.setFontSize(fontSize);
        }
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
    private loadAutoPreviewPreference(checkbox: HTMLInputElement | null = null): void {
        const saved = localStorage.getItem(this.storageAutoPreviewKey);
        const isEnabled = saved !== 'false'; // Default to true

        if (checkbox) {
            checkbox.checked = isEnabled;
        } else if (this.autoPreviewCheckbox) {
            this.autoPreviewCheckbox.checked = isEnabled;
        }

        // Sync both checkboxes
        if (this.autoPreviewCheckbox) {
            this.autoPreviewCheckbox.checked = isEnabled;
        }
        if (this.autoPreviewCheckboxPanel) {
            this.autoPreviewCheckboxPanel.checked = isEnabled;
        }
    }

    /**
     * Setup auto-preview trigger on editor changes
     */
    private setupAutoPreviewTrigger(): void {
        if (!this.latexEditor) return;

        this.latexEditor.addEventListener('input', () => {
            // Check if auto-preview is enabled (either checkbox)
            const isEnabled = (this.autoPreviewCheckbox && this.autoPreviewCheckbox.checked) ||
                            (this.autoPreviewCheckboxPanel && this.autoPreviewCheckboxPanel.checked);
            if (!isEnabled) return;

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
        if (this.fontSizeSelector) {
            return parseInt(this.fontSizeSelector.value, 10);
        }
        return this.defaultFontSize;
    }

    /**
     * Set font size programmatically
     */
    public setFontSize(fontSize: number): void {
        if (fontSize >= 10 && fontSize <= 20) {
            if (this.fontSizeSelector) {
                this.fontSizeSelector.value = fontSize.toString();
                const event = new Event('change', { bubbles: true });
                this.fontSizeSelector.dispatchEvent(event);
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

    /**
     * Setup Ctrl+Mouse wheel for font size adjustment
     */
    private setupFontSizeDrag(): void {
        const editorContainer = document.querySelector('.latex-panel');
        if (!editorContainer) {
            console.warn('[EditorControls] Editor container not found for font size control');
            return;
        }

        // Listen on document level with capture to intercept early
        document.addEventListener('wheel', (e: Event) => {
            const wheelEvent = e as WheelEvent;

            console.log('[EditorControls] Wheel event - Ctrl pressed:', wheelEvent.ctrlKey);

            // Only handle when Ctrl is pressed
            if (!wheelEvent.ctrlKey) return;

            // Check if we're over the editor panel (not the PDF panel)
            const target = wheelEvent.target as HTMLElement;
            const pdfPanel = document.querySelector('.preview-panel');

            console.log('[EditorControls] Ctrl+Wheel detected - target:', target.className, 'tagName:', target.tagName);
            console.log('[EditorControls] Is over PDF panel:', pdfPanel?.contains(target));
            console.log('[EditorControls] Is over editor panel:', editorContainer.contains(target));

            // If over PDF panel, ignore (let PDF zoom handler take it)
            if (pdfPanel && pdfPanel.contains(target)) {
                console.log('[EditorControls] Over PDF - skipping font size adjustment');
                return;
            }

            // If not over editor panel, ignore
            if (!editorContainer.contains(target)) {
                console.log('[EditorControls] Not over editor - skipping');
                return;
            }

            console.log('[EditorControls] Ctrl+Wheel over editor - adjusting font size');

            // Prevent default zoom behavior and stop propagation
            e.preventDefault();
            e.stopPropagation();

            // Get current font size
            const currentSize = this.fontSizeSelector?.value;
            const currentFontSize = currentSize ? parseInt(currentSize, 10) : 14;

            // Calculate new font size based on wheel direction
            const delta = wheelEvent.deltaY > 0 ? -1 : 1; // Scroll down = decrease, up = increase
            const newFontSize = Math.max(10, Math.min(20, currentFontSize + delta));

            if (newFontSize !== currentFontSize) {
                this.setFontSize(newFontSize);
                console.log('[EditorControls] Font size changed via Ctrl+Wheel:', currentFontSize, '→', newFontSize);
            }
        }, { passive: false, capture: true }); // Use capture phase to intercept very early

        console.log('[EditorControls] Ctrl+Wheel font size adjustment enabled on editor (document-level listener)');

        // Also add keyboard shortcuts for font size
        document.addEventListener('keydown', (e: KeyboardEvent) => {
            if (!e.ctrlKey && !e.metaKey) return;

            const editorContainer = document.querySelector('.latex-panel');
            if (!editorContainer) return;

            // Check if we're focused on the editor area
            const activeElement = document.activeElement;
            if (!activeElement || !editorContainer.contains(activeElement)) return;

            const currentSize = this.fontSizeSelector?.value;
            const currentFontSize = currentSize ? parseInt(currentSize, 10) : 14;
            let newFontSize = currentFontSize;

            // Ctrl+Plus: increase font size
            if (e.key === '+' || e.key === '=') {
                e.preventDefault();
                newFontSize = Math.min(20, currentFontSize + 1);
                console.log('[EditorControls] Ctrl++ font size increase');
            }
            // Ctrl+Minus: decrease font size
            else if (e.key === '-' || e.key === '_') {
                e.preventDefault();
                newFontSize = Math.max(10, currentFontSize - 1);
                console.log('[EditorControls] Ctrl+- font size decrease');
            }
            // Ctrl+0: reset to default
            else if (e.key === '0') {
                e.preventDefault();
                newFontSize = this.defaultFontSize;
                console.log('[EditorControls] Ctrl+0 font size reset');
            }

            if (newFontSize !== currentFontSize) {
                this.setFontSize(newFontSize);
            }
        });

        console.log('[EditorControls] Font size keyboard shortcuts enabled (Ctrl+/-, Ctrl+0)');
    }
}
