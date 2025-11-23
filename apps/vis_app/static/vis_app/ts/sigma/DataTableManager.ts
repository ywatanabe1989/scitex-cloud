/**
 * DataTableManager - Orchestrator for data table operations
 *
 * REFACTORED: Now delegates to 7 focused modules:
 * - TableData: Data management, CSV import, demo data
 * - TableRendering: Rendering & virtual scrolling
 * - TableSelection: Cell/column/row selection
 * - TableEditing: Cell editing & keyboard navigation
 * - TableClipboard: Copy/paste operations
 * - TableFillHandle: Fill handle drag functionality
 * - TableColumnRow: Column/row operations & resizing
 */

import { Dataset } from './types.js';
import { TableData } from './data-table/TableData.js';
import { TableRendering } from './data-table/TableRendering.js';
import { TableSelection } from './data-table/TableSelection.js';
import { TableEditing } from './data-table/TableEditing.js';
import { TableClipboard } from './data-table/TableClipboard.js';
import { TableFillHandle } from './data-table/TableFillHandle.js';
import { TableColumnRow } from './data-table/TableColumnRow.js';

export class DataTableManager {
    // Module instances
    private tableData: TableData;
    private tableRendering: TableRendering;
    private tableSelection: TableSelection;
    private tableEditing: TableEditing;
    private tableClipboard: TableClipboard;
    private tableFillHandle: TableFillHandle;
    private tableColumnRow: TableColumnRow;

    constructor(
        private statusBarCallback?: (message: string) => void,
        private updateColumnDropdownsCallback?: () => void,
        private updateRulersAreaTransformCallback?: () => void
    ) {
        // Initialize TableData module
        this.tableData = new TableData(
            statusBarCallback,
            updateColumnDropdownsCallback
        );

        // Initialize TableRendering module
        this.tableRendering = new TableRendering(
            () => this.tableData.getCurrentData(),
            statusBarCallback,
            updateRulersAreaTransformCallback
        );

        // Set column widths reference
        this.tableRendering.setColumnWidths(new Map());
        this.tableRendering.setFirstColIsIndex(false);

        // Initialize TableSelection module
        this.tableSelection = new TableSelection(
            (row: number, col: number) => this.getCellAt(row, col),
            statusBarCallback
        );

        // Initialize TableEditing module
        this.tableEditing = new TableEditing({
            getCurrentData: () => this.tableData.getCurrentData(),
            setCurrentData: (data: Dataset | null) => this.tableData.setCurrentData(data),
            getCellAt: (row: number, col: number) => this.getCellAt(row, col),
            renderCallback: () => this.renderEditableDataTable(),
            getSelection: () => this.tableSelection.getSelectionState(),
            updateSelection: () => this.tableSelection.updateSelection(),
            statusBarCallback: statusBarCallback
        });

        // Initialize TableClipboard module
        this.tableClipboard = new TableClipboard(
            () => this.tableData.getCurrentData(),
            (data: Dataset | null) => this.tableData.setCurrentData(data),
            () => this.tableSelection.getSelectionState(),
            () => this.renderEditableDataTable(),
            statusBarCallback
        );

        // Initialize TableFillHandle module
        this.tableFillHandle = new TableFillHandle({
            getCurrentData: () => this.tableData.getCurrentData(),
            setCurrentData: (data: Dataset | null) => this.tableData.setCurrentData(data),
            getCellAt: (row: number, col: number) => this.getCellAt(row, col),
            renderCallback: () => this.renderEditableDataTable(),
            statusBarCallback: statusBarCallback
        });

        // Initialize TableColumnRow module
        this.tableColumnRow = new TableColumnRow(
            () => this.tableData.getCurrentData(),
            (data: Dataset | null) => this.tableData.setCurrentData(data),
            () => this.renderEditableDataTable(),
            statusBarCallback
        );
    }

    // ========================================
    // PUBLIC API - Data Operations
    // ========================================

    public getCurrentData(): Dataset | null {
        return this.tableData.getCurrentData();
    }

    public setCurrentData(data: Dataset | null): void {
        this.tableData.setCurrentData(data);
    }

    public initializeBlankTable(): void {
        this.tableData.initializeBlankTable();
        this.renderEditableDataTable();
    }

    public handleFileImport(file: File): void {
        this.tableData.handleFileImport(file);
    }

    public loadDemoData(): void {
        this.tableData.loadDemoData();
        this.renderEditableDataTable();
    }

    // ========================================
    // PUBLIC API - Rendering
    // ========================================

    public renderDataTable(): void {
        this.tableRendering.renderDataTable();
    }

    public renderEditableDataTable(): void {
        this.tableRendering.renderEditableDataTable();
        this.setupEventHandlers();
    }

    public generateTableHTML(data: Dataset, tableType: string): string {
        return this.tableRendering.generateTableHTML(data, tableType);
    }

    // ========================================
    // PUBLIC API - Column/Row Operations
    // ========================================

    public setupColumnResizing(): void {
        this.tableColumnRow.setupColumnResizing();
    }

    public addColumns(count: number): void {
        this.tableColumnRow.addColumns(count);
    }

    public addRows(count: number): void {
        this.tableColumnRow.addRows(count);
    }

    // ========================================
    // PUBLIC API - Selection
    // ========================================

    public clearSelection(): void {
        this.tableSelection.clearSelection();
    }

    // ========================================
    // PRIVATE - Event Handler Setup
    // ========================================

    private setupEventHandlers(): void {
        const dataContainer = document.querySelector('.data-table-container') as HTMLElement;
        if (!dataContainer) return;

        const table = dataContainer.querySelector('.data-table') as HTMLTableElement;
        if (!table) return;

        // Setup cell event handlers
        const cells = table.querySelectorAll('td[data-row][data-col]');
        cells.forEach((cell: Element) => {
            const tdCell = cell as HTMLElement;

            // Selection handlers
            tdCell.addEventListener('mousedown', (e) => {
                this.tableSelection.handleCellMouseDown(e as MouseEvent, tdCell);
            });

            tdCell.addEventListener('mouseover', () => {
                this.tableSelection.handleCellMouseOver(tdCell);
            });

            // Double-click to edit
            tdCell.addEventListener('dblclick', () => {
                this.tableEditing.enterEditMode(tdCell);
            });
        });

        // Setup column header handlers
        const columnHeaders = table.querySelectorAll('th[data-col]');
        columnHeaders.forEach((header: Element) => {
            const thHeader = header as HTMLElement;

            thHeader.addEventListener('mousedown', (e) => {
                this.tableSelection.handleColumnHeaderMouseDown(e as MouseEvent, thHeader);
            });

            thHeader.addEventListener('mouseover', () => {
                this.tableSelection.handleColumnHeaderMouseOver(thHeader);
            });

            // Double-click to edit column name
            thHeader.addEventListener('dblclick', () => {
                this.tableEditing.enterEditMode(thHeader);
            });
        });

        // Setup row number handlers
        const rowNumbers = table.querySelectorAll('.row-number');
        rowNumbers.forEach((rowElement: Element) => {
            const rowDiv = rowElement as HTMLElement;

            rowDiv.addEventListener('mousedown', (e) => {
                this.tableSelection.handleRowNumberMouseDown(e as MouseEvent, rowDiv);
            });

            rowDiv.addEventListener('mouseover', () => {
                this.tableSelection.handleRowNumberMouseOver(rowDiv);
            });
        });

        // Global mouseup to stop selection
        document.addEventListener('mouseup', () => {
            this.tableSelection.stopSelection();
        });

        // Keyboard events
        dataContainer.addEventListener('keydown', (e) => {
            const target = e.target as HTMLElement;
            if (target.tagName === 'TD' || target.tagName === 'TH') {
                this.tableEditing.handleCellKeydown(e as KeyboardEvent, target);
            }
        });

        // Clipboard events
        dataContainer.addEventListener('copy', (e) => {
            this.tableClipboard.handleTableCopy(e as ClipboardEvent);
        });

        dataContainer.addEventListener('paste', (e) => {
            this.tableClipboard.handleTablePaste(e as ClipboardEvent);
        });

        // Fill handle events
        const fillHandle = dataContainer.querySelector('.fill-handle') as HTMLElement;
        if (fillHandle) {
            fillHandle.addEventListener('mousedown', (e) => {
                const selectionState = this.tableSelection.getSelectionState();
                this.tableFillHandle.handleFillHandleMouseDown(
                    e as MouseEvent,
                    selectionState.selectionStart,
                    selectionState.selectionEnd
                );
            });
        }
    }

    // ========================================
    // PRIVATE - Helper Methods
    // ========================================

    private getCellAt(row: number, col: number): HTMLElement | null {
        const dataContainer = document.querySelector('.data-table-container') as HTMLElement;
        if (!dataContainer) return null;

        const table = dataContainer.querySelector('.data-table') as HTMLTableElement;
        if (!table) return null;

        return table.querySelector(`td[data-row="${row}"][data-col="${col}"]`) as HTMLElement;
    }
}
