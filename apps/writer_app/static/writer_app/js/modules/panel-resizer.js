/**
 * Panel Resizer Module
 * Handles draggable resizing of split panels (LaTeX editor and PDF preview)
 */
export class PanelResizer {
    constructor() {
        this.isResizing = false;
        this.startX = 0;
        this.startLeftWidth = 0;
        this.minPanelWidth = 300; // Minimum width for each panel (px)
        this.storageKey = 'scitex-panel-widths';
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
    initialize() {
        this.resizer.addEventListener('mousedown', this.handleMouseDown.bind(this));
        document.addEventListener('mousemove', this.handleMouseMove.bind(this));
        document.addEventListener('mouseup', this.handleMouseUp.bind(this));
        // Load saved panel widths from localStorage
        this.loadPanelWidths();
        console.log('[PanelResizer] Initialized successfully');
    }
    /**
     * Load previously saved panel widths from localStorage
     */
    loadPanelWidths() {
        const saved = localStorage.getItem(this.storageKey);
        if (saved) {
            try {
                const { leftWidth, rightWidth } = JSON.parse(saved);
                if (leftWidth && rightWidth) {
                    this.leftPanel.style.flex = `0 0 ${leftWidth}px`;
                    this.rightPanel.style.flex = `0 0 ${rightWidth}px`;
                    console.log(`[PanelResizer] Restored panel widths: ${leftWidth}px / ${rightWidth}px`);
                }
            }
            catch (error) {
                console.warn('[PanelResizer] Failed to load saved panel widths:', error);
            }
        }
    }
    /**
     * Save panel widths to localStorage
     */
    savePanelWidths() {
        const leftWidth = this.leftPanel.getBoundingClientRect().width;
        const rightWidth = this.rightPanel.getBoundingClientRect().width;
        localStorage.setItem(this.storageKey, JSON.stringify({ leftWidth, rightWidth }));
    }
    /**
     * Handle mouse down on resizer
     */
    handleMouseDown(event) {
        event.preventDefault();
        this.isResizing = true;
        this.startX = event.clientX;
        this.startLeftWidth = this.leftPanel.getBoundingClientRect().width;
        // Add active state to resizer
        this.resizer.classList.add('active');
        // Prevent text selection during resize
        document.body.style.userSelect = 'none';
        document.body.style.cursor = 'col-resize';
        console.log('[PanelResizer] Resize started');
    }
    /**
     * Handle mouse move during resize
     */
    handleMouseMove(event) {
        if (!this.isResizing)
            return;
        event.preventDefault();
        const diff = event.clientX - this.startX;
        const newLeftWidth = this.startLeftWidth + diff;
        const containerWidth = this.container.getBoundingClientRect().width;
        const resizerWidth = this.resizer.getBoundingClientRect().width;
        const newRightWidth = containerWidth - newLeftWidth - resizerWidth;
        // Enforce minimum panel widths
        if (newLeftWidth >= this.minPanelWidth && newRightWidth >= this.minPanelWidth) {
            this.leftPanel.style.flex = `0 0 ${newLeftWidth}px`;
            this.rightPanel.style.flex = `0 0 ${newRightWidth}px`;
        }
    }
    /**
     * Handle mouse up to end resize
     */
    handleMouseUp() {
        if (!this.isResizing)
            return;
        this.isResizing = false;
        // Remove active state from resizer
        this.resizer.classList.remove('active');
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
    resetToEqualSplit() {
        const containerWidth = this.container.getBoundingClientRect().width;
        const resizerWidth = this.resizer.getBoundingClientRect().width;
        const panelWidth = (containerWidth - resizerWidth) / 2;
        this.leftPanel.style.flex = `0 0 ${panelWidth}px`;
        this.rightPanel.style.flex = `0 0 ${panelWidth}px`;
        this.savePanelWidths();
        console.log('[PanelResizer] Reset to equal split');
    }
    /**
     * Set specific panel widths
     */
    setPanelWidths(leftWidth, rightWidth) {
        this.leftPanel.style.flex = `0 0 ${leftWidth}px`;
        this.rightPanel.style.flex = `0 0 ${rightWidth}px`;
        this.savePanelWidths();
    }
    /**
     * Get current panel widths
     */
    getPanelWidths() {
        return {
            leftWidth: this.leftPanel.getBoundingClientRect().width,
            rightWidth: this.rightPanel.getBoundingClientRect().width
        };
    }
    /**
     * Check if resizer is initialized
     */
    isInitialized() {
        return !!this.resizer && !!this.leftPanel && !!this.rightPanel && !!this.container;
    }
}
//# sourceMappingURL=panel-resizer.js.map