/**
 * UIManager - Handles all UI interactions and components
 *
 * Responsibilities:
 * - Initialize sidebar and properties panel toggling
 * - Handle panel resizers
 * - Initialize ribbon/pane header buttons
 * - Handle drag and drop
 * - Show modals (sort, filter, help)
 * - Update status bar
 * - Setup keyboard shortcuts
 * - Theme switching
 * - Tree manager integration
 */

import { TreeManager } from './tree-manager.js';
import { ResizerManager } from './ResizerManager.js';
import { PlotDataManager } from './PlotDataManager.js';
import type { Figure } from './types.js';
import type { PropertiesManager } from './PropertiesManager.js';
import type { DataTableManager } from './DataTableManager.js';

export class UIManager {
    private isSidebarCollapsed: boolean = false;
    private resizerManager: ResizerManager;
    private isPropertiesCollapsed: boolean = false;
    private currentWorkspaceMode: string = 'data';
    private treeManager: TreeManager | null = null;
    private editingCell: HTMLElement | null = null; // Track if cell is being edited (for keyboard shortcuts)
    private propertiesManager: PropertiesManager | null = null;
    private plotDataManager: PlotDataManager;
    private dataTableManager: DataTableManager | null = null;
    private currentSelectedPlotId: string | null = null;

    constructor(
        private handleFileImportCallback?: (file: File) => void,
        private loadDemoDataCallback?: () => void,
        private addColumnsCallback?: (count: number) => void,
        private addRowsCallback?: (count: number) => void,
        private copySelectionCallback?: () => void,
        private createQuickPlotCallback?: (plotType: string) => void,
        private zoomInCallback?: () => void,
        private zoomOutCallback?: () => void,
        private zoomToFitCallback?: () => void,
        private toggleGridCallback?: () => void,
        private firstRowIsHeaderRef?: { value: boolean },
        private firstColIsIndexRef?: { value: boolean },
        private renderEditableDataTableCallback?: () => void,
        private statusBarCallback?: (message: string) => void
    ) {
        // Initialize ResizerManager (single-source-of-truth for panel resizing)
        this.resizerManager = new ResizerManager();

        // Initialize PlotDataManager
        this.plotDataManager = new PlotDataManager();
    }

    /**
     * Set editing cell reference (for keyboard shortcut detection)
     */
    public setEditingCell(cell: HTMLElement | null): void {
        this.editingCell = cell;
    }

    /**
     * Set properties manager reference for tab switching
     */
    public setPropertiesManager(manager: PropertiesManager): void {
        this.propertiesManager = manager;
    }

    /**
     * Set data table manager reference for plot-specific data display
     */
    public setDataTableManager(manager: DataTableManager): void {
        this.dataTableManager = manager;
    }

    /**
     * Get plot data manager instance
     */
    public getPlotDataManager(): PlotDataManager {
        return this.plotDataManager;
    }

    /**
     * Get current workspace mode
     */
    public getCurrentWorkspaceMode(): string {
        return this.currentWorkspaceMode;
    }

    /**
     * Initialize all event listeners
     */
    public initializeEventListeners(): void {
        // Sidebar toggle
        this.initSidebarToggle();

        // Properties panel toggle
        this.initPropertiesToggle();

        // Ribbon buttons (now pane header buttons)
        this.initRibbonButtons();

        // Drag and drop
        this.initDragAndDrop();

        // Panel resizers
        this.initPanelResizers();

        console.log('[UIManager] All UI event listeners initialized');
    }

    /**
     * Initialize sidebar toggle
     */
    private initSidebarToggle(): void {
        const toggleBtn = document.getElementById('sidebar-toggle');
        const main = document.querySelector('.sigma-main');
        const icon = toggleBtn?.querySelector('i');

        toggleBtn?.addEventListener('click', () => {
            this.isSidebarCollapsed = !this.isSidebarCollapsed;
            main?.classList.toggle('sidebar-collapsed', this.isSidebarCollapsed);

            // Update icon
            if (icon) {
                icon.className = this.isSidebarCollapsed
                    ? 'fas fa-chevron-right'
                    : 'fas fa-chevron-left';
            }

            console.log(`[UIManager] Sidebar collapsed: ${this.isSidebarCollapsed}`);
        });
    }

    /**
     * Initialize properties panel toggle
     */
    private initPropertiesToggle(): void {
        const toggleBtn = document.getElementById('properties-toggle');
        const main = document.querySelector('.sigma-main');
        const icon = toggleBtn?.querySelector('i');

        toggleBtn?.addEventListener('click', () => {
            this.isPropertiesCollapsed = !this.isPropertiesCollapsed;
            main?.classList.toggle('properties-collapsed', this.isPropertiesCollapsed);

            // Update icon
            if (icon) {
                icon.className = this.isPropertiesCollapsed
                    ? 'fas fa-chevron-left'
                    : 'fas fa-chevron-right';
            }

            console.log(`[UIManager] Properties panel collapsed: ${this.isPropertiesCollapsed}`);
        });
    }

    /**
     * Initialize ribbon/pane header buttons
     */
    private initRibbonButtons(): void {
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
                console.log('[UIManager] First row is header:', this.firstRowIsHeaderRef.value);
            }
        });

        // Index toggle button (data table index)
        const indexToggleBtn = document.getElementById('index-toggle-btn');
        indexToggleBtn?.addEventListener('click', () => {
            if (this.firstColIsIndexRef) {
                this.firstColIsIndexRef.value = !this.firstColIsIndexRef.value;
                indexToggleBtn.classList.toggle('active', this.firstColIsIndexRef.value);
                this.updateStatusBar(`First column is now treated as ${this.firstColIsIndexRef.value ? 'index' : 'data'}`);
                console.log('[UIManager] First column is index:', this.firstColIsIndexRef.value);

                // Re-render table to show/hide index styling
                if (this.renderEditableDataTableCallback) {
                    this.renderEditableDataTableCallback();
                }
            }
        });

        // Sort button (data table header)
        const sortBtn = document.getElementById('transform-sort');
        sortBtn?.addEventListener('click', () => {
            this.showSortModal();
        });

        // Filter button (data table header)
        const filterBtn = document.getElementById('transform-filter');
        filterBtn?.addEventListener('click', () => {
            this.showFilterModal();
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
            this.showTableHelp();
        });

        // Export plot CSV button
        const exportPlotCsvBtn = document.getElementById('export-plot-csv-btn');
        exportPlotCsvBtn?.addEventListener('click', () => {
            this.handleExportPlotCSV();
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

        console.log('[UIManager] Ribbon buttons initialized');
    }

    /**
     * Initialize drag and drop
     */
    private initDragAndDrop(): void {
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

        console.log('[UIManager] Drag and drop initialized');
    }

    /**
     * Initialize panel resizers (delegated to ResizerManager)
     */
    private initPanelResizers(): void {
        // Use ResizerManager for single-source-of-truth resizing logic
        this.resizerManager.initializeSigmaResizers();
        console.log('[UIManager] Panel resizers delegated to ResizerManager');
    }

    /**
     * Show sort modal
     */
    private showSortModal(): void {
        const sortModal = document.getElementById('sort-modal');
        if (sortModal) {
            sortModal.style.display = 'block';
            console.log('[UIManager] Sort modal opened');
        }
    }

    /**
     * Show filter modal
     */
    private showFilterModal(): void {
        const filterModal = document.getElementById('filter-modal');
        if (filterModal) {
            filterModal.style.display = 'block';
            console.log('[UIManager] Filter modal opened');
        }
    }

    /**
     * Show table help
     */
    private showTableHelp(): void {
        const helpModal = document.getElementById('table-help-modal');
        if (helpModal) {
            helpModal.style.display = 'block';
            console.log('[UIManager] Table help modal opened');
        } else {
            // Create a simple help alert if modal doesn't exist
            alert('Table Help:\n\n' +
                '- Click cell to select\n' +
                '- Drag to select range\n' +
                '- Double-click to edit\n' +
                '- Ctrl+C to copy\n' +
                '- Ctrl+V to paste\n' +
                '- Arrow keys to navigate\n' +
                '- F2 to edit cell\n' +
                '- Tab/Shift+Tab to move\n' +
                '- Enter/Shift+Enter to move vertically\n' +
                '- Drag column borders to resize\n' +
                '- Drag fill handle to auto-fill');
        }
    }

    /**
     * Update status bar
     */
    public updateStatusBar(message?: string): void {
        const statusMode = document.getElementById('status-mode');
        const statusMessage = document.getElementById('status-message');

        if (statusMode) {
            statusMode.textContent = this.currentWorkspaceMode === 'data'
                ? 'Data View'
                : 'Canvas View';
        }

        if (statusMessage && message) {
            statusMessage.textContent = message;
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
                console.log('[UIManager] Undo triggered (not yet implemented)');
                this.updateStatusBar('Undo (not yet implemented)');
            }

            // Ctrl+Y or Ctrl+Shift+Z - Redo (placeholder)
            if (((e.ctrlKey || e.metaKey) && e.key === 'y') ||
                ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'z')) {
                e.preventDefault();
                console.log('[UIManager] Redo triggered (not yet implemented)');
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
                console.log('[UIManager] Delete triggered (not yet implemented)');
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

        console.log('[UIManager] Keyboard shortcuts initialized');
    }

    /**
     * Initialize TreeManager for hierarchical figure/axes/plots structure
     */
    public initializeTreeManager(): void {
        this.treeManager = new TreeManager();
        console.log('[UIManager] TreeManager initialized');

        // Load test data for demonstration
        this.loadTestTreeData();

        // Setup tree action event listeners
        this.setupTreeEventListeners();

        // Setup tree section collapse/expand
        this.setupTreeSectionToggle();
    }

    /**
     * Setup tree section collapse/expand functionality
     */
    private setupTreeSectionToggle(): void {
        const sectionHeader = document.querySelector('.tree-section-header') as HTMLElement;
        if (!sectionHeader) return;

        sectionHeader.addEventListener('click', (e) => {
            const target = e.target as HTMLElement;

            // Don't toggle if clicking the + button
            if (target.closest('.tree-add-btn')) return;

            const section = sectionHeader.closest('.tree-section') as HTMLElement;
            const content = section?.querySelector('.tree-section-content') as HTMLElement;
            const toggle = sectionHeader.querySelector('.tree-section-toggle') as HTMLElement;

            if (!content || !toggle) return;

            // Toggle visibility
            const isExpanded = toggle.classList.contains('fa-chevron-down');

            if (isExpanded) {
                // Collapse
                toggle.classList.remove('fa-chevron-down');
                toggle.classList.add('fa-chevron-right');
                content.style.display = 'none';
            } else {
                // Expand
                toggle.classList.remove('fa-chevron-right');
                toggle.classList.add('fa-chevron-down');
                content.style.display = 'block';
            }
        });
    }

    /**
     * Setup event listeners for tree actions
     */
    private setupTreeEventListeners(): void {
        const treeContainer = document.getElementById('figures-tree');
        if (!treeContainer) return;

        // Handle edit events
        treeContainer.addEventListener('tree-item-edit', ((e: CustomEvent) => {
            const { itemType, itemId, label } = e.detail;
            console.log('[UIManager] Tree edit event:', { itemType, itemId, label });
            this.handleTreeItemEdit(e.detail);
        }) as EventListener);

        // Handle delete events
        treeContainer.addEventListener('tree-item-delete', ((e: CustomEvent) => {
            const { itemType, itemId, label } = e.detail;
            console.log('[UIManager] Tree delete event:', { itemType, itemId, label });
            this.handleTreeItemDelete(e.detail);
        }) as EventListener);

        // Handle add events
        treeContainer.addEventListener('tree-item-add', ((e: CustomEvent) => {
            const { parentType, parentId, addableTypes } = e.detail;
            console.log('[UIManager] Tree add event:', { parentType, parentId, addableTypes });
            this.handleTreeItemAdd(e.detail);
        }) as EventListener);

        // Handle selection events (for canvas synchronization)
        treeContainer.addEventListener('tree-item-select', ((e: CustomEvent) => {
            const { itemId, label } = e.detail;
            console.log('[UIManager] Tree select event:', { itemId, label });
            this.handleTreeItemSelect(e.detail);
        }) as EventListener);
    }

    /**
     * Handle tree item edit
     */
    private handleTreeItemEdit(detail: any): void {
        const { itemType, itemId, label } = detail;

        // For now, show a simple prompt (can be replaced with modal later)
        const newLabel = prompt(`Edit ${itemType} label:`, label);

        if (newLabel && newLabel !== label) {
            // Update the label in the tree
            const labelElement = detail.element.querySelector('.tree-label');
            if (labelElement) {
                // Extract the suffix (e.g., "(2 Axes)" for figures)
                const match = labelElement.textContent?.match(/^(.+?)(\s*\([^)]+\))?$/);
                const suffix = match?.[2] || '';
                labelElement.textContent = newLabel + suffix;
            }

            console.log('[UIManager] Updated item label:', { itemType, itemId, oldLabel: label, newLabel });
            // TODO: Update data model when integrated
        }
    }

    /**
     * Handle tree item delete
     */
    private handleTreeItemDelete(detail: any): void {
        const { itemType, itemId, label } = detail;
        console.log('[UIManager] Item deleted:', { itemType, itemId, label });
        // TODO: Remove from data model when integrated
        // TODO: Remove from canvas when integrated
    }

    /**
     * Handle tree item add
     */
    private handleTreeItemAdd(detail: any): void {
        const { parentType, parentId, addableTypes, element } = detail;

        if (addableTypes.length === 0) {
            alert('Cannot add items to this section');
            return;
        }

        // Determine what to add
        let itemTypeToAdd = addableTypes[0];
        if (addableTypes.length > 1) {
            // Show selection dialog
            const selection = prompt(
                `What would you like to add?\nOptions: ${addableTypes.join(', ')}\n\nEnter type:`,
                addableTypes[0]
            );
            if (!selection || !addableTypes.includes(selection.toLowerCase())) {
                return;
            }
            itemTypeToAdd = selection.toLowerCase();
        }

        // Get label for new item
        const newLabel = prompt(`Enter ${itemTypeToAdd} label:`, `New ${itemTypeToAdd}`);
        if (!newLabel) return;

        console.log('[UIManager] Adding new item:', { itemTypeToAdd, newLabel, parentType, parentId });

        // TODO: Add to data model and rebuild tree
        alert(`Adding ${itemTypeToAdd} "${newLabel}" to ${parentType}\n\nThis will create a new ${itemTypeToAdd} when data model is integrated.`);
    }

    /**
     * Handle tree item selection (synchronize with canvas and show properties)
     * Implements 3-pane responsive sync: Tree ↔ Data ↔ Properties
     */
    private handleTreeItemSelect(detail: any): void {
        const { itemId, label, element } = detail;
        console.log('[UIManager] Item selected in tree:', { itemId, label });

        // Determine node type and show appropriate properties
        if (element) {
            let elementType = '';
            let elementLabel = label;

            if (element.classList.contains('tree-plot')) {
                elementType = 'plot';
                // **Plot selected: Show plot-specific data table**
                this.showPlotDataTable(itemId, label);
                this.currentSelectedPlotId = itemId;
            } else if (element.classList.contains('tree-axis')) {
                elementType = 'axis';
                // Axis selected: Clear data table (axes don't have data)
                this.clearDataTable();
                this.currentSelectedPlotId = null;
            } else if (element.classList.contains('tree-guide')) {
                elementType = 'guide';
                // Guide selected: Clear data table
                this.clearDataTable();
                this.currentSelectedPlotId = null;
            } else if (element.classList.contains('tree-annotation')) {
                elementType = 'annotation';
                // Annotation selected: Clear data table
                this.clearDataTable();
                this.currentSelectedPlotId = null;
            } else if (element.classList.contains('tree-figure')) {
                elementType = 'figure';
                // Figure selected: Clear data table
                this.clearDataTable();
                this.currentSelectedPlotId = null;
            }

            // Show properties panel for selected element
            if (elementType && this.propertiesManager) {
                // Get element data from tree (TODO: implement proper data retrieval)
                const elementData = {
                    id: itemId,
                    label: label,
                    // Additional data will be populated from data model
                };

                this.propertiesManager.showPropertiesFor(elementType, elementLabel, elementData);
            }
        }

        // TODO: Find and select corresponding canvas object
        // TODO: Highlight in canvas

        // For now, just log the selection
        console.log('[UIManager] Canvas sync: Would select canvas object with ID:', itemId);
    }

    /**
     * Handle export plot CSV
     */
    private handleExportPlotCSV(): void {
        if (!this.currentSelectedPlotId) {
            alert('No plot selected. Please select a plot from the tree to export its data.');
            return;
        }

        // Download CSV for current plot
        this.plotDataManager.downloadPlotCSV(this.currentSelectedPlotId);

        if (this.statusBarCallback) {
            this.statusBarCallback(`Exported data for plot ${this.currentSelectedPlotId}`);
        }
    }

    /**
     * Show plot-specific data table when plot is selected
     */
    private showPlotDataTable(plotId: string, plotLabel: string): void {
        if (!this.dataTableManager) {
            console.warn('[UIManager] DataTableManager not available');
            return;
        }

        // Check if plot has data
        if (!this.plotDataManager.hasPlotData(plotId)) {
            console.log(`[UIManager] Plot ${plotId} has no data. Creating demo data...`);
            // Create demo data for the plot
            this.plotDataManager.createDemoData(plotId);
        }

        // Get plot data as Dataset
        const dataset = this.plotDataManager.getPlotDataAsDataset(plotId);
        if (!dataset) {
            console.warn(`[UIManager] Failed to get data for plot ${plotId}`);
            return;
        }

        // Load into data table manager
        this.dataTableManager.setCurrentData(dataset);
        this.dataTableManager.renderEditableDataTable();

        // Show export button
        const exportBtn = document.getElementById('export-plot-csv-btn');
        if (exportBtn) {
            exportBtn.style.display = 'inline-block';
        }

        // Update status bar
        if (this.statusBarCallback) {
            const plotData = this.plotDataManager.getPlotData(plotId);
            const source = plotData?.source || `plot-${plotId}.csv`;
            this.statusBarCallback(`Showing data for ${plotLabel} (${source}) - ${dataset.rows.length} rows × ${dataset.columns.length} columns`);
        }

        console.log(`[UIManager] Displaying data table for plot ${plotId}`);
    }

    /**
     * Clear data table when non-plot item is selected
     */
    private clearDataTable(): void {
        if (!this.dataTableManager) return;

        // Clear the data table
        this.dataTableManager.setCurrentData(null);
        const dataContainer = document.querySelector('.data-table-container');
        if (dataContainer) {
            dataContainer.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">Select a plot to view its data</div>';
        }

        // Hide export button
        const exportBtn = document.getElementById('export-plot-csv-btn');
        if (exportBtn) {
            exportBtn.style.display = 'none';
        }

        if (this.statusBarCallback) {
            this.statusBarCallback('No data to display');
        }

        console.log('[UIManager] Data table cleared');
    }

    /**
     * Sync edited data back to PlotDataManager
     */
    public syncDataTableToPlot(): void {
        if (!this.currentSelectedPlotId || !this.dataTableManager) {
            return;
        }

        const currentData = this.dataTableManager.getCurrentData();
        if (!currentData) {
            return;
        }

        // Sync back to plot data manager
        this.plotDataManager.syncFromDataset(this.currentSelectedPlotId, currentData);

        console.log(`[UIManager] Synced data table changes to plot ${this.currentSelectedPlotId}`);
    }

    /**
     * Load test data into tree (for demonstration)
     */
    private loadTestTreeData(): void {
        if (!this.treeManager) return;

        const testData: Figure[] = [
            {
                id: 'fig1',
                label: 'Figure 1',
                axes: [
                    {
                        id: 'ax1',
                        label: 'Ax 1 - Main Plot',
                        title: 'Neural Activity Over Time',
                        xLabel: 'Time (ms)',
                        yLabel: 'Firing Rate (Hz)',
                        plots: [
                            {
                                id: 'plot1',
                                type: 'line',
                                label: 'Plot1',
                                xColumn: 'time',
                                yColumn: 'firing_rate'
                            },
                            {
                                id: 'plot2',
                                type: 'scatter',
                                label: 'Plot2',
                                xColumn: 'time',
                                yColumn: 'threshold'
                            }
                        ],
                        guides: [
                            {
                                id: 'guide1',
                                type: 'legend',
                                label: 'Legend 1',
                                plots: ['plot1', 'plot2']
                            },
                            {
                                id: 'guide2',
                                type: 'colorbar',
                                label: 'Colorbar 1',
                                plots: ['plot1']
                            }
                        ],
                        annotations: [
                            {
                                id: 'annot1',
                                type: 'text',
                                label: 'Significance',
                                content: 'p < 0.01',
                                position: { x: 100, y: 50 }
                            },
                            {
                                id: 'annot2',
                                type: 'scalebar',
                                label: 'Scale bar',
                                content: '10 μm'
                            }
                        ]
                    },
                    {
                        id: 'ax2',
                        label: 'Ax 2 - Histogram',
                        title: 'Distribution',
                        xLabel: 'Value',
                        yLabel: 'Count',
                        plots: [
                            {
                                id: 'plot3',
                                type: 'bar',
                                label: 'Plot3',
                                xColumn: 'bin',
                                yColumn: 'count'
                            }
                        ],
                        guides: [],
                        annotations: []
                    }
                ]
            }
        ];

        this.treeManager.buildTree(testData);
        console.log('[UIManager] Test tree data loaded');
    }

    /**
     * Get tree manager instance
     */
    public getTreeManager(): TreeManager | null {
        return this.treeManager;
    }
}
