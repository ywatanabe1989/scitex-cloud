/**
 * RibbonButtons - Manages ribbon/pane header button interactions
 *
 * Responsibilities:
 * - Initialize data import/export buttons
 * - Initialize table transformation buttons (sort, filter)
 * - Initialize table structure buttons (add rows/columns)
 * - Initialize header/index toggle buttons
 * - Initialize quick plot buttons
 * - Handle drag and drop file uploads
 * - Display modal dialogs and help
 *
 * Dependencies:
 * - Callbacks for data operations
 * - References to UI state (headers, indices)
 * - Modal elements in DOM
 */

export class RibbonButtons {
    constructor(
        private handleFileImportCallback?: (file: File) => void,
        private loadDemoDataCallback?: () => void,
        private addColumnsCallback?: (count: number) => void,
        private addRowsCallback?: (count: number) => void,
        private firstRowIsHeaderRef?: { value: boolean },
        private firstColIsIndexRef?: { value: boolean },
        private renderEditableDataTableCallback?: () => void,
        private statusBarCallback?: (message: string) => void,
        private showSortModalCallback?: () => void,
        private showFilterModalCallback?: () => void,
        private showTableHelpCallback?: () => void,
        private createQuickPlotCallback?: (plotType: string) => void,
        private handleExportPlotCSVCallback?: () => void
    ) {}

    /**
     * Initialize all ribbon buttons and their handlers
     */
    public initRibbonButtons(): void {
        const dataInput = document.getElementById('data-file-input') as HTMLInputElement;

        // Import Data buttons (data table header)
        const importDataBtns = document.querySelectorAll('#import-data-btn-small');
        importDataBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                dataInput?.click();
            });
        });

        dataInput?.addEventListener('change', (e) => {
            const file = (e.target as HTMLInputElement).files?.[0];
            if (file && this.handleFileImportCallback) {
                this.handleFileImportCallback(file);
            }
        });

        // Demo Data buttons (data table header)
        const demoDataBtns = document.querySelectorAll('#demo-data-btn-small');
        demoDataBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                if (this.loadDemoDataCallback) {
                    this.loadDemoDataCallback();
                }
            });
        });

        // Header toggle button (data table header)
        const headerToggleBtn = document.getElementById('header-toggle-btn');
        headerToggleBtn?.addEventListener('click', () => {
            if (this.firstRowIsHeaderRef) {
                this.firstRowIsHeaderRef.value = !this.firstRowIsHeaderRef.value;
                headerToggleBtn.classList.toggle('active', this.firstRowIsHeaderRef.value);
                this.updateStatusBar(`First row is now treated as ${this.firstRowIsHeaderRef.value ? 'header' : 'data'}`);
                console.log('[RibbonButtons] First row is header:', this.firstRowIsHeaderRef.value);
            }
        });

        // Index toggle button (data table index)
        const indexToggleBtn = document.getElementById('index-toggle-btn');
        indexToggleBtn?.addEventListener('click', () => {
            if (this.firstColIsIndexRef) {
                this.firstColIsIndexRef.value = !this.firstColIsIndexRef.value;
                indexToggleBtn.classList.toggle('active', this.firstColIsIndexRef.value);
                this.updateStatusBar(`First column is now treated as ${this.firstColIsIndexRef.value ? 'index' : 'data'}`);
                console.log('[RibbonButtons] First column is index:', this.firstColIsIndexRef.value);

                // Re-render table to show/hide index styling
                if (this.renderEditableDataTableCallback) {
                    this.renderEditableDataTableCallback();
                }
            }
        });

        // Sort button (data table header)
        const sortBtn = document.getElementById('transform-sort');
        sortBtn?.addEventListener('click', () => {
            if (this.showSortModalCallback) {
                this.showSortModalCallback();
            }
        });

        // Filter button (data table header)
        const filterBtn = document.getElementById('transform-filter');
        filterBtn?.addEventListener('click', () => {
            if (this.showFilterModalCallback) {
                this.showFilterModalCallback();
            }
        });

        // Add columns button (data table header)
        const addColumnsBtn = document.getElementById('add-columns-btn');
        addColumnsBtn?.addEventListener('click', () => {
            if (this.addColumnsCallback) {
                this.addColumnsCallback(10);
            }
        });

        // Add rows button (data table header)
        const addRowsBtn = document.getElementById('add-rows-btn');
        addRowsBtn?.addEventListener('click', () => {
            if (this.addRowsCallback) {
                this.addRowsCallback(10);
            }
        });

        // Table help button
        const tableHelpBtn = document.getElementById('table-help-btn');
        tableHelpBtn?.addEventListener('click', () => {
            if (this.showTableHelpCallback) {
                this.showTableHelpCallback();
            }
        });

        // Export plot CSV button
        const exportPlotCsvBtn = document.getElementById('export-plot-csv-btn');
        exportPlotCsvBtn?.addEventListener('click', () => {
            if (this.handleExportPlotCSVCallback) {
                this.handleExportPlotCSVCallback();
            }
        });

        // Quick create plot buttons (from canvas pane header)
        const quickPlotBtns = document.querySelectorAll('[data-plot-type]');
        quickPlotBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const plotType = btn.getAttribute('data-plot-type');
                if (plotType && this.createQuickPlotCallback) {
                    this.createQuickPlotCallback(plotType);
                }
            });
        });

        console.log('[RibbonButtons] Ribbon buttons initialized');
    }

    /**
     * Initialize drag and drop for file uploads
     */
    public initDragAndDrop(): void {
        const dropZone = document.body;

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });

        // Highlight drop zone when file is dragged over
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('drag-over');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('drag-over');
            }, false);
        });

        // Handle dropped files
        dropZone.addEventListener('drop', (e: DragEvent) => {
            const files = e.dataTransfer?.files;
            if (files && files.length > 0) {
                const file = files[0];
                if (file.name.endsWith('.csv') || file.name.endsWith('.xlsx')) {
                    if (this.handleFileImportCallback) {
                        this.handleFileImportCallback(file);
                    }
                } else {
                    this.updateStatusBar('Invalid file type. Please drop CSV or Excel files.');
                }
            }
        }, false);

        console.log('[RibbonButtons] Drag and drop initialized');
    }

    /**
     * Update status bar message
     */
    private updateStatusBar(message: string): void {
        if (this.statusBarCallback) {
            this.statusBarCallback(message);
        }
    }
}
