/**
 * Panel Resizer Module
 * Handles draggable resizing of split panels (LaTeX editor and PDF preview)
 */

export class PanelResizer {
    private resizer: HTMLElement | null;
    private leftPanel: HTMLElement | null;
    private rightPanel: HTMLElement | null;
    private container: HTMLElement | null;
    private isResizing: boolean = false;
    private startX: number = 0;
    private startLeftWidth: number = 0;
    private minPanelWidth: number = 300; // Minimum width for each panel (px)
    private storageKey: string = 'scitex-panel-widths';

    constructor() {
        this.resizer = document.getElementById('panel-resizer');
        this.leftPanel = document.querySelector('.latex-panel');
        this.rightPanel = document.querySelector('.preview-panel');
        this.container = document.getElementById('editor-view-split');

        if (this.resizer && this.leftPanel && this.rightPanel && this.container) {
            this.initialize();
        }
    }

    /**
     * Initialize the panel resizer with event listeners
     */
    private initialize(): void {
        this.resizer!.addEventListener('mousedown', this.handleMouseDown.bind(this));
        document.addEventListener('mousemove', this.handleMouseMove.bind(this));
        document.addEventListener('mouseup', this.handleMouseUp.bind(this));

        // Load saved panel widths from localStorage
        this.loadPanelWidths();

        console.log('[PanelResizer] Initialized successfully');
    }

    /**
     * Load previously saved panel widths from localStorage
     */
    private loadPanelWidths(): void {
        const saved = localStorage.getItem(this.storageKey);
        if (saved) {
            try {
                const { leftWidth, rightWidth } = JSON.parse(saved);
                if (leftWidth && rightWidth) {
                    this.leftPanel!.style.flex = `0 0 ${leftWidth}px`;
                    this.rightPanel!.style.flex = `0 0 ${rightWidth}px`;
                    console.log(`[PanelResizer] Restored panel widths: ${leftWidth}px / ${rightWidth}px`);
                }
            } catch (error) {
                console.warn('[PanelResizer] Failed to load saved panel widths:', error);
            }
        }
    }

    /**
     * Save panel widths to localStorage
     */
    private savePanelWidths(): void {
        const leftWidth = this.leftPanel!.getBoundingClientRect().width;
        const rightWidth = this.rightPanel!.getBoundingClientRect().width;
        localStorage.setItem(this.storageKey, JSON.stringify({ leftWidth, rightWidth }));
    }

    /**
     * Handle mouse down on resizer
     */
    private handleMouseDown(event: MouseEvent): void {
        event.preventDefault();
        this.isResizing = true;
        this.startX = event.clientX;
        this.startLeftWidth = this.leftPanel!.getBoundingClientRect().width;

        // Add active state to resizer
        this.resizer!.classList.add('active');

        // Prevent text selection during resize
        document.body.style.userSelect = 'none';
        document.body.style.cursor = 'col-resize';

        console.log('[PanelResizer] Resize started');
    }

    /**
     * Handle mouse move during resize
     */
    private handleMouseMove(event: MouseEvent): void {
        if (!this.isResizing) return;

        event.preventDefault();

        const diff = event.clientX - this.startX;
        const newLeftWidth = this.startLeftWidth + diff;
        const containerWidth = this.container!.getBoundingClientRect().width;
        const resizerWidth = this.resizer!.getBoundingClientRect().width;
        const newRightWidth = containerWidth - newLeftWidth - resizerWidth;

        // Enforce minimum panel widths
        if (newLeftWidth >= this.minPanelWidth && newRightWidth >= this.minPanelWidth) {
            this.leftPanel!.style.flex = `0 0 ${newLeftWidth}px`;
            this.rightPanel!.style.flex = `0 0 ${newRightWidth}px`;
        }
    }

    /**
     * Handle mouse up to end resize
     */
    private handleMouseUp(): void {
        if (!this.isResizing) return;

        this.isResizing = false;

        // Remove active state from resizer
        this.resizer!.classList.remove('active');

        // Restore default cursor and selection
        document.body.style.userSelect = '';
        document.body.style.cursor = '';

        // Save panel widths to localStorage
        this.savePanelWidths();

        console.log('[PanelResizer] Resize ended and saved');
    }

    /**
     * Reset panel widths to equal split (50:50)
     */
    public resetToEqualSplit(): void {
        const containerWidth = this.container!.getBoundingClientRect().width;
        const resizerWidth = this.resizer!.getBoundingClientRect().width;
        const panelWidth = (containerWidth - resizerWidth) / 2;

        this.leftPanel!.style.flex = `0 0 ${panelWidth}px`;
        this.rightPanel!.style.flex = `0 0 ${panelWidth}px`;

        this.savePanelWidths();
        console.log('[PanelResizer] Reset to equal split');
    }

    /**
     * Set specific panel widths
     */
    public setPanelWidths(leftWidth: number, rightWidth: number): void {
        this.leftPanel!.style.flex = `0 0 ${leftWidth}px`;
        this.rightPanel!.style.flex = `0 0 ${rightWidth}px`;
        this.savePanelWidths();
    }

    /**
     * Get current panel widths
     */
    public getPanelWidths(): { leftWidth: number; rightWidth: number } {
        return {
            leftWidth: this.leftPanel!.getBoundingClientRect().width,
            rightWidth: this.rightPanel!.getBoundingClientRect().width
        };
    }

    /**
     * Check if resizer is initialized
     */
    public isInitialized(): boolean {
        return !!this.resizer && !!this.leftPanel && !!this.rightPanel && !!this.container;
    }
}
