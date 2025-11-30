/**
 * KeyboardShortcuts - Handles all keyboard shortcuts for the visualization editor
 *
 * Responsibilities:
 * - Setup keyboard event listeners
 * - Handle zoom shortcuts (+ - 0)
 * - Handle grid toggle (G or Space)
 * - Handle copy selection (Ctrl+C)
 * - Handle undo/redo (Ctrl+Z, Ctrl+Y)
 * - Handle delete operations
 * - Detect when user is editing a cell to avoid shortcut interference
 */

export class KeyboardShortcuts {
    private editingCell: HTMLElement | null = null;

    constructor(
        private createQuickPlotCallback?: (plotType: string) => void,
        private zoomInCallback?: () => void,
        private zoomOutCallback?: () => void,
        private zoomToFitCallback?: () => void,
        private toggleGridCallback?: () => void,
        private copySelectionCallback?: () => void,
        private setEditingCellRef?: (cell: HTMLElement | null) => void,
        private updateStatusBarCallback?: (message: string) => void
    ) {}

    /**
     * Set editing cell reference (for keyboard shortcut detection)
     */
    public setEditingCell(cell: HTMLElement | null): void {
        this.editingCell = cell;
        if (this.setEditingCellRef) {
            this.setEditingCellRef(cell);
        }
    }

    /**
     * Setup keyboard shortcuts
     */
    public setupKeyboardShortcuts(): void {
        document.addEventListener('keydown', (e: KeyboardEvent) => {
            // Prevent shortcuts when typing in inputs
            if (document.activeElement?.tagName === 'INPUT' ||
                document.activeElement?.tagName === 'TEXTAREA' ||
                this.editingCell) {
                return;
            }

            // Ctrl+Z - Undo (placeholder)
            if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
                e.preventDefault();
                console.log('[KeyboardShortcuts] Undo triggered (not yet implemented)');
                this.updateStatusBar('Undo (not yet implemented)');
            }

            // Ctrl+Y or Ctrl+Shift+Z - Redo (placeholder)
            if (((e.ctrlKey || e.metaKey) && e.key === 'y') ||
                ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'z')) {
                e.preventDefault();
                console.log('[KeyboardShortcuts] Redo triggered (not yet implemented)');
                this.updateStatusBar('Redo (not yet implemented)');
            }

            // Ctrl+C - Copy selection
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'c') {
                e.preventDefault();
                if (this.copySelectionCallback) {
                    this.copySelectionCallback();
                }
            }

            // Delete key - Delete selected (placeholder)
            if (e.key === 'Delete' || e.key === 'Backspace') {
                e.preventDefault();
                console.log('[KeyboardShortcuts] Delete triggered (not yet implemented)');
                this.updateStatusBar('Delete (not yet implemented)');
            }

            // + key - Zoom in
            if (e.key === '+' || e.key === '=') {
                if (!e.ctrlKey && !e.metaKey) {
                    e.preventDefault();
                    if (this.zoomInCallback) {
                        this.zoomInCallback();
                    }
                }
            }

            // - key - Zoom out
            if (e.key === '-' || e.key === '_') {
                if (!e.ctrlKey && !e.metaKey) {
                    e.preventDefault();
                    if (this.zoomOutCallback) {
                        this.zoomOutCallback();
                    }
                }
            }

            // 0 key - Fit to window
            if (e.key === '0') {
                if (!e.ctrlKey && !e.metaKey) {
                    e.preventDefault();
                    if (this.zoomToFitCallback) {
                        this.zoomToFitCallback();
                    }
                }
            }

            // G key or Space - Toggle grid
            if (e.key === 'g' || e.key === 'G' || e.key === ' ') {
                if (!e.ctrlKey && !e.metaKey) {
                    e.preventDefault();
                    if (this.toggleGridCallback) {
                        this.toggleGridCallback();
                    }
                }
            }

            // Space - Enable pan mode cursor
            if (e.key === ' ') {
                e.preventDefault();
                const canvasContainer = document.getElementById('canvas-container');
                if (canvasContainer && !(canvasContainer as any).isPanning) {
                    canvasContainer.style.cursor = 'grab';
                }
            }
        });

        // Space key release - Disable pan mode cursor
        document.addEventListener('keyup', (e: KeyboardEvent) => {
            if (e.key === ' ') {
                const canvasContainer = document.getElementById('canvas-container');
                if (canvasContainer) {
                    canvasContainer.style.cursor = 'default';
                }
            }
        });

        console.log('[KeyboardShortcuts] Keyboard shortcuts initialized');
    }

    /**
     * Update status bar
     */
    private updateStatusBar(message?: string): void {
        if (this.updateStatusBarCallback && message) {
            this.updateStatusBarCallback(message);
        }
    }
}
