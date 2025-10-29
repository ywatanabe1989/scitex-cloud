/**
 * Panel Resizer Module
 * Handles draggable divider between editor and preview panels
 */

export class PanelResizer {
    private resizer: HTMLElement | null;
    private leftPanel: HTMLElement | null;
    private rightPanel: HTMLElement | null;
    private container: HTMLElement | null;
    private isResizing: boolean = false;
    private startX: number = 0;
    private startLeftWidth: number = 0;
    private _initialized: boolean = false;

    constructor(containerId: string = 'editor-view-split') {
        this.container = document.getElementById(containerId);
        this.resizer = document.getElementById('panel-resizer');
        this.leftPanel = document.querySelector('.latex-panel');
        this.rightPanel = document.querySelector('.preview-panel');

        if (this.resizer && this.container && this.leftPanel && this.rightPanel) {
            this.init();
        } else {
            console.warn('[PanelResizer] Required elements not found');
        }
    }

    /**
     * Initialize resizer event listeners
     */
    private init(): void {
        if (!this.resizer) return;

        this.resizer.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        document.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        document.addEventListener('mouseup', () => this.handleMouseUp());

        this._initialized = true;
        this.restoreSavedWidth();
        console.log('[PanelResizer] Initialized');
    }

    /**
     * Check if panel resizer is initialized
     */
    isInitialized(): boolean {
        return this._initialized;
    }

    /**
     * Handle mouse down on resizer
     */
    private handleMouseDown(e: MouseEvent): void {
        this.isResizing = true;
        this.startX = e.clientX;

        if (this.leftPanel && this.container) {
            this.startLeftWidth = this.leftPanel.getBoundingClientRect().width;
        }

        if (this.resizer) {
            this.resizer.classList.add('active');
        }

        e.preventDefault();
    }

    /**
     * Handle mouse move during resize
     */
    private handleMouseMove(e: MouseEvent): void {
        if (!this.isResizing || !this.leftPanel || !this.rightPanel || !this.container) {
            return;
        }

        const deltaX = e.clientX - this.startX;
        const containerWidth = this.container.getBoundingClientRect().width;
        const newLeftWidth = this.startLeftWidth + deltaX;

        // Minimum width for each panel (200px)
        const minWidth = 200;
        const maxLeftWidth = containerWidth - minWidth;

        if (newLeftWidth >= minWidth && newLeftWidth <= maxLeftWidth) {
            const leftPercent = (newLeftWidth / containerWidth) * 100;
            const rightPercent = 100 - leftPercent;

            this.leftPanel.style.flex = `0 0 ${leftPercent}%`;
            this.rightPanel.style.flex = `0 0 ${rightPercent}%`;

            // Save preference to localStorage
            localStorage.setItem('panelLeftWidth', leftPercent.toString());
        }
    }

    /**
     * Handle mouse up
     */
    private handleMouseUp(): void {
        this.isResizing = false;

        if (this.resizer) {
            this.resizer.classList.remove('active');
        }
    }

    /**
     * Restore saved panel width from localStorage
     */
    restoreSavedWidth(): void {
        const savedWidth = localStorage.getItem('panelLeftWidth');
        if (savedWidth && this.leftPanel && this.rightPanel) {
            const leftPercent = parseFloat(savedWidth);
            const rightPercent = 100 - leftPercent;

            this.leftPanel.style.flex = `0 0 ${leftPercent}%`;
            this.rightPanel.style.flex = `0 0 ${rightPercent}%`;

            console.log('[PanelResizer] Restored panel width:', leftPercent + '%');
        }
    }

    /**
     * Reset to default 50:50 split
     */
    resetToDefault(): void {
        if (!this.leftPanel || !this.rightPanel) return;

        this.leftPanel.style.flex = '0 0 50%';
        this.rightPanel.style.flex = '0 0 50%';
        localStorage.setItem('panelLeftWidth', '50');

        console.log('[PanelResizer] Reset to 50:50 split');
    }

    /**
     * Check if the resizer is properly initialized
     */
    isInitialized(): boolean {
        return !!(this.resizer && this.leftPanel && this.rightPanel && this.container);
    }
}
