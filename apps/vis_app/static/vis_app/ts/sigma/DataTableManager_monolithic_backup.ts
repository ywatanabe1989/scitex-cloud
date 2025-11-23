/**
 * DataTableManager - Handles all data table operations
 *
 * Responsibilities:
 * - Initialize and render editable data table
 * - Handle cell selection (single, range, column, row)
 * - Cell editing (double-click, keyboard)
 * - Copy/paste operations (Excel-compatible)
 * - File import (CSV)
 * - Column/row addition and resizing
 * - Keyboard navigation
 * - Fill handle (drag to fill)
 */

import { Dataset, DataRow, TABLE_CONSTANTS } from './types.js';

export class DataTableManager {
    private currentData: Dataset | null = null;
    private firstRowIsHeader: boolean = true;
    private firstColIsIndex: boolean = false;
    private defaultRows: number = TABLE_CONSTANTS.DEFAULT_ROWS;
    private defaultCols: number = TABLE_CONSTANTS.DEFAULT_COLS;
    private readonly ROW_HEIGHT: number = TABLE_CONSTANTS.ROW_HEIGHT;
    private readonly COL_WIDTH: number = TABLE_CONSTANTS.COL_WIDTH;
    private maxRows: number = TABLE_CONSTANTS.MAX_ROWS;
    private maxCols: number = TABLE_CONSTANTS.MAX_COLS;

    // Virtual scrolling state
    private virtualScrollEnabled: boolean = true;
    private visibleRowStart: number = 0;
    private visibleRowEnd: number = 50;  // Initial visible rows
    private visibleColStart: number = 0;
    private visibleColEnd: number = 32;  // Show all 32 columns initially
    private readonly BUFFER_ROWS: number = 20;  // Extra rows to render above/below viewport

    // Selection state
    private selectedCell: HTMLElement | null = null;
    private selectionStart: { row: number, col: number } | null = null;
    private selectionEnd: { row: number, col: number } | null = null;
    private isSelecting: boolean = false;
    private selectedColumns: Set<number> = new Set();
    private selectedRows: Set<number> = new Set();
    private isSelectingColumns: boolean = false;
    private isSelectingRows: boolean = false;
    private columnSelectionStart: number = -1;
    private rowSelectionStart: number = -1;
    private isResizingTable: boolean = false;

    // Editing state
    private editingCell: HTMLElement | null = null;
    private editingCellBlurHandler: (() => void) | null = null;

    // Column resizing
    private columnWidths: Map<number, number> = new Map();
    private isResizingColumn: boolean = false;
    private resizingColumnIndex: number = -1;
    private resizeStartX: number = 0;
    private resizeStartWidth: number = 0;

    constructor(
        private statusBarCallback?: (message: string) => void,
        private updateColumnDropdownsCallback?: () => void,
        private updateRulersAreaTransformCallback?: () => void
    ) {}

    /**
     * Get current dataset
     */
    public getCurrentData(): Dataset | null {
        return this.currentData;
    }

    /**
     * Set current dataset
     */
    public setCurrentData(data: Dataset | null): void {
        this.currentData = data;
    }

    /**
     * Initialize blank table based on container size
     */
    public initializeBlankTable(): void {
        const startTime = performance.now();
        console.log('[DataTableManager] Starting table initialization...');

        const container = document.querySelector('.data-table-container') as HTMLElement;

        // PERFORMANCE: Start with large table that supports virtual scrolling
        // Virtual scrolling will handle rendering efficiently
        const initialRows = 1000;  // 1000 rows - virtual scrolling handles performance
        const initialCols = 32;  // 32 columns (A-AF)
        console.log(`[DataTableManager] Creating ${initialRows} rows × ${initialCols} columns = ${initialRows * initialCols} cells`);

        const columns: string[] = [];
        for (let i = 0; i < initialCols; i++) {
            columns.push(this.getColumnLabel(i));
        }

        const rows: DataRow[] = [];
        for (let i = 0; i < initialRows; i++) {
            const row: DataRow = {};
            columns.forEach(col => {
                row[col] = '';
            });
            rows.push(row);
        }

        this.currentData = { columns, rows };

        // Enable virtual scrolling for large initial table
        if (rows.length > 100) {
            this.virtualScrollEnabled = true;
            this.visibleRowStart = 0;
            this.visibleRowEnd = 50;
            console.log(`[DataTableManager] Virtual scrolling enabled for ${rows.length} rows`);
        } else {
            this.virtualScrollEnabled = false;
        }

        const dataCreateTime = performance.now();
        console.log(`[DataTableManager] Data structure created in ${(dataCreateTime - startTime).toFixed(2)}ms`);

        this.renderEditableDataTable();

        const totalTime = performance.now();
        console.log(`[DataTableManager] ✅ Table initialization complete in ${(totalTime - startTime).toFixed(2)}ms`);

        if (this.statusBarCallback) {
            this.statusBarCallback(`Ready - ${initialRows} rows × ${initialCols} columns`);
        }

        console.log('[DataTableManager] Blank table initialized:', initialRows, 'x', initialCols);
    }

    /**
     * Setup column resizing functionality (Excel-like column border dragging)
     */
    public setupColumnResizing(): void {
        const dataContainer = document.querySelector('.data-table-container') as HTMLElement;
        if (!dataContainer) return;

        // Use event delegation for resize handles (since table is re-rendered)
        dataContainer.addEventListener('mousedown', (e: MouseEvent) => {
            const target = e.target as HTMLElement;
            if (!target.classList.contains('column-resize-handle')) return;

            const colIndex = parseInt(target.getAttribute('data-col') || '-1');
            if (colIndex === -1) return;

            // CRITICAL: Prevent event propagation to avoid triggering page resizers
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();

            this.isResizingColumn = true;
            this.resizingColumnIndex = colIndex;
            this.resizeStartX = e.clientX;
            this.resizeStartWidth = this.columnWidths.get(colIndex) || this.COL_WIDTH;

            document.body.style.cursor = 'col-resize';
            document.body.style.userSelect = 'none';

            console.log(`[DataTableManager] Started resizing column ${colIndex}, initial width: ${this.resizeStartWidth}px`);
        }, true); // Use capture phase to intercept before other handlers

        document.addEventListener('mousemove', (e: MouseEvent) => {
            if (!this.isResizingColumn) return;

            e.preventDefault();
            e.stopPropagation();

            const deltaX = e.clientX - this.resizeStartX;
            const newWidth = Math.max(30, this.resizeStartWidth + deltaX); // Minimum 30px

            // Update the stored width
            this.columnWidths.set(this.resizingColumnIndex, newWidth);

            // Apply width to all cells in this column
            const table = dataContainer.querySelector('.data-table') as HTMLTableElement;
            if (table) {
                // Update header
                const header = table.querySelector(`th[data-col="${this.resizingColumnIndex}"]`) as HTMLElement;
                if (header) {
                    header.style.minWidth = `${newWidth}px`;
                    header.style.width = `${newWidth}px`;
                }

                // Update all data cells in this column
                const cells = table.querySelectorAll(`td[data-col="${this.resizingColumnIndex}"]`);
                cells.forEach((cell: Element) => {
                    const td = cell as HTMLElement;
                    td.style.minWidth = `${newWidth}px`;
                    td.style.width = `${newWidth}px`;
                });
            }
        }, true); // Use capture phase

        document.addEventListener('mouseup', () => {
            if (this.isResizingColumn) {
                console.log(`[DataTableManager] Finished resizing column ${this.resizingColumnIndex}, final width: ${this.columnWidths.get(this.resizingColumnIndex)}px`);

                this.isResizingColumn = false;
                this.resizingColumnIndex = -1;

                document.body.style.cursor = '';
                document.body.style.userSelect = '';
            }
        }, true); // Use capture phase

        console.log('[DataTableManager] Column resizing initialized');
    }

    /**
     * Add columns to the table
     */
    public addColumns(count: number): void {
        if (!this.currentData) return;

        const currentColCount = this.currentData.columns.length;
        const newColCount = Math.min(currentColCount + count, this.maxCols);

        for (let i = currentColCount; i < newColCount; i++) {
            const newColName = this.getColumnLabel(i);
            this.currentData.columns.push(newColName);
            // Add empty cells to existing rows
            this.currentData.rows.forEach(row => {
                row[newColName] = '';
            });
        }

        this.renderEditableDataTable();

        if (this.statusBarCallback) {
            this.statusBarCallback(`Added ${newColCount - currentColCount} columns (Total: ${this.currentData.rows.length} rows × ${this.currentData.columns.length} columns)`);
        }

        console.log(`[DataTableManager] Columns added. Total: ${this.currentData.columns.length}`);
    }

    /**
     * Add rows to the table
     */
    public addRows(count: number): void {
        if (!this.currentData) return;

        const currentRowCount = this.currentData.rows.length;
        const newRowCount = Math.min(currentRowCount + count, this.maxRows);

        for (let i = currentRowCount; i < newRowCount; i++) {
            const newRow: DataRow = {};
            this.currentData.columns.forEach(col => {
                newRow[col] = '';
            });
            this.currentData.rows.push(newRow);
        }

        this.renderEditableDataTable();

        if (this.statusBarCallback) {
            this.statusBarCallback(`Added ${newRowCount - currentRowCount} rows (Total: ${this.currentData.rows.length} rows × ${this.currentData.columns.length} columns)`);
        }

        console.log(`[DataTableManager] Rows added. Total: ${this.currentData.rows.length}`);
    }

    /**
     * Handle file import
     */
    public handleFileImport(file: File): void {
        console.log(`[DataTableManager] Importing file: ${file.name}`);

        if (this.statusBarCallback) {
            this.statusBarCallback(`Loading ${file.name}...`);
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target?.result as string;
            if (file.name.endsWith('.csv')) {
                this.parseCSV(content, file.name);
            } else {
                if (this.statusBarCallback) {
                    this.statusBarCallback('Excel import coming soon');
                }
                console.warn('[DataTableManager] Excel import not yet implemented');
            }
        };
        reader.readAsText(file);
    }

    /**
     * Parse CSV content
     */
    private parseCSV(content: string, filename: string): void {
        try {
            const lines = content.trim().split('\n');
            if (lines.length < 2) {
                if (this.statusBarCallback) {
                    this.statusBarCallback('Invalid CSV: needs headers and at least one row');
                }
                return;
            }

            // Parse headers
            const headers = lines[0].split(',').map(h => h.trim());

            // Parse rows
            const rows: DataRow[] = [];
            for (let i = 1; i < lines.length; i++) {
                const values = lines[i].split(',').map(v => v.trim());
                const row: DataRow = {};
                headers.forEach((header, index) => {
                    const value = values[index];
                    // Try to parse as number
                    const numValue = parseFloat(value);
                    row[header] = isNaN(numValue) ? value : numValue;
                });
                rows.push(row);
            }

            this.currentData = { columns: headers, rows };
            this.renderDataTable();

            if (this.statusBarCallback) {
                this.statusBarCallback(`Loaded ${filename} - ${rows.length} rows × ${headers.length} columns`);
            }

            console.log('[DataTableManager] Data loaded:', this.currentData);
        } catch (error) {
            console.error('[DataTableManager] CSV parsing error:', error);
            if (this.statusBarCallback) {
                this.statusBarCallback('Error parsing CSV file');
            }
        }
    }

    /**
     * Load demo data
     */
    public loadDemoData(): void {
        console.log('[DataTableManager] Loading demo data...');

        if (this.statusBarCallback) {
            this.statusBarCallback('Loading demo data...');
        }

        // Create scientific demo data
        const xValues: number[] = [];
        const yValues: number[] = [];
        for (let i = 0; i <= 20; i++) {
            const x = i * 0.5;
            xValues.push(x);
            yValues.push(Math.sin(x) * Math.exp(-x / 10) + (Math.random() - 0.5) * 0.1);
        }

        const rows: DataRow[] = xValues.map((x, i) => ({
            'Time (s)': x,
            'Signal (mV)': parseFloat(yValues[i].toFixed(4))
        }));

        this.currentData = {
            columns: ['Time (s)', 'Signal (mV)'],
            rows
        };

        this.renderDataTable();

        if (this.statusBarCallback) {
            this.statusBarCallback(`Demo data loaded - ${rows.length} rows × 2 columns`);
        }

        console.log('[DataTableManager] Demo data loaded:', this.currentData);
    }

    /**
     * Render data table (non-editable view)
     */
    public renderDataTable(): void {
        if (!this.currentData) return;

        const dataContainer = document.querySelector('.data-table-container');
        if (dataContainer) {
            dataContainer.innerHTML = this.generateTableHTML(this.currentData, 'main');
        }

        // Update column dropdowns in properties panel
        if (this.updateColumnDropdownsCallback) {
            this.updateColumnDropdownsCallback();
        }
    }

    /**
     * Render editable data table with paste support
     */
    public renderEditableDataTable(): void {
        const renderStart = performance.now();
        console.log('[DataTableManager] Starting table render...');

        if (!this.currentData) return;

        const dataContainer = document.querySelector('.data-table-container');
        if (!dataContainer) return;

        // Performance optimized: Use CSS classes instead of inline styles (95% HTML size reduction)
        let html = '<table class="data-table editable-table">';

        // Header row with row/column numbers
        html += '<thead><tr>';
        // Top-left corner cell (empty)
        html += `<th class="row-number-header"></th>`;
        // Column headers (Col 1, Col 2, ...)
        this.currentData.columns.forEach((col, colIndex) => {
            const isIndexCol = this.firstColIsIndex && colIndex === 0;
            const colName = isIndexCol ? 'None' : col;
            html += `<th data-col="${colIndex}" tabindex="0">${colName}<div class="column-resize-handle" data-col="${colIndex}"></div></th>`;
        });
        html += '</tr></thead>';

        // Data rows with row numbers (with virtual scrolling support)
        html += '<tbody>';

        // Determine which rows to render based on virtual scrolling
        const totalRows = this.currentData.rows.length;
        const startRow = this.virtualScrollEnabled ? this.visibleRowStart : 0;
        const endRow = this.virtualScrollEnabled ? Math.min(this.visibleRowEnd, totalRows) : totalRows;

        console.log(`[DataTableManager] Rendering rows ${startRow} to ${endRow} of ${totalRows}`);

        // Render only visible rows
        for (let rowIndex = startRow; rowIndex < endRow; rowIndex++) {
            const row = this.currentData.rows[rowIndex];
            const rowClass = rowIndex % 2 === 0 ? 'row-even' : 'row-odd';
            html += `<tr class="${rowClass}">`;
            // Row number
            html += `<td class="row-number">${rowIndex + 1}</td>`;
            // Data cells
            this.currentData!.columns.forEach((col, colIndex) => {
                const value = row[col] || '';
                const isIndexCol = this.firstColIsIndex && colIndex === 0;
                const cellClass = isIndexCol ? 'index-col' : 'data-cell';
                html += `<td data-row="${rowIndex}" data-col="${colIndex}" tabindex="0" class="${cellClass}">${value}</td>`;
            });
            html += '</tr>';
        }
        html += '</tbody></table>';

        const htmlBuildTime = performance.now();
        console.log(`[DataTableManager] HTML string built in ${(htmlBuildTime - renderStart).toFixed(2)}ms`);

        // Generate dynamic CSS for column widths (NO INLINE STYLES!)
        let dynamicCSS = '<style id="data-table-dynamic-widths">';
        this.currentData.columns.forEach((col, colIndex) => {
            const columnWidth = this.columnWidths.get(colIndex) || this.COL_WIDTH;
            dynamicCSS += `
                .data-table th[data-col="${colIndex}"],
                .data-table td[data-col="${colIndex}"] {
                    width: ${columnWidth}px;
                    min-width: ${columnWidth}px;
                }
            `;
        });
        dynamicCSS += '</style>';

        dataContainer.innerHTML = dynamicCSS + html;

        const domInsertTime = performance.now();
        console.log(`[DataTableManager] DOM insertion (innerHTML) took ${(domInsertTime - htmlBuildTime).toFixed(2)}ms`);

        // Add copy event listener (native browser copy command)
        dataContainer.addEventListener('copy', (e) => this.handleTableCopy(e as ClipboardEvent));

        // Add paste event listener
        dataContainer.addEventListener('paste', (e) => this.handleTablePaste(e as ClipboardEvent));

        // Setup virtual scrolling
        this.setupVirtualScrolling();

        // ============================================================
        // EVENT DELEGATION - Attach listeners to container, not cells
        // This dramatically improves performance (4 listeners vs 1000s)
        // ============================================================

        // Delegated mousedown handler for cells, headers, and row numbers
        dataContainer.addEventListener('mousedown', (e) => {
            const target = e.target as HTMLElement;

            // Handle data cell mousedown
            const cell = target.closest('td[data-row]') as HTMLElement;
            if (cell) {
                this.handleCellMouseDown(e as MouseEvent, cell);
                return;
            }

            // Handle column header mousedown
            const header = target.closest('th[data-col]') as HTMLElement;
            if (header) {
                this.handleColumnHeaderMouseDown(e as MouseEvent, header);
                return;
            }

            // Handle row number mousedown
            const rowNum = target.closest('td.row-number') as HTMLElement;
            if (rowNum) {
                this.handleRowNumberMouseDown(e as MouseEvent, rowNum);
                return;
            }
        });

        // Delegated mouseover handler for cells, headers, and row numbers
        dataContainer.addEventListener('mouseover', (e) => {
            const target = e.target as HTMLElement;

            // Handle data cell mouseover
            const cell = target.closest('td[data-row]') as HTMLElement;
            if (cell) {
                this.handleCellMouseOver(cell);
                return;
            }

            // Handle column header mouseover
            const header = target.closest('th[data-col]') as HTMLElement;
            if (header) {
                this.handleColumnHeaderMouseOver(header);
                return;
            }

            // Handle row number mouseover
            const rowNum = target.closest('td.row-number') as HTMLElement;
            if (rowNum) {
                this.handleRowNumberMouseOver(rowNum);
                return;
            }
        });

        // Delegated dblclick handler for cells (edit mode)
        dataContainer.addEventListener('dblclick', (e) => {
            const target = e.target as HTMLElement;
            const cell = target.closest('td[data-row]') as HTMLElement;
            if (cell) {
                this.enterEditMode(cell);
            }
        });

        // Delegated keydown handler for cells
        dataContainer.addEventListener('keydown', (e) => {
            const target = e.target as HTMLElement;
            const cell = target.closest('td[data-row]') as HTMLElement;
            if (cell) {
                this.handleCellKeydown(e as KeyboardEvent, cell);
            }
        });

        // Global mouse events
        const globalMouseUp = () => {
            this.isSelecting = false;
            this.isSelectingColumns = false;
            this.isSelectingRows = false;
            this.isResizingTable = false;
        };
        const globalMouseMove = (e: MouseEvent) => {
            if (this.isSelecting && e.buttons === 1) {
                // Get element under mouse
                const element = document.elementFromPoint(e.clientX, e.clientY) as HTMLElement;
                if (element && (element.hasAttribute('data-row') || element.hasAttribute('data-col'))) {
                    this.handleCellMouseOver(element);
                }
            }
        };

        document.addEventListener('mouseup', globalMouseUp);
        document.addEventListener('mousemove', globalMouseMove);

        const eventSetupTime = performance.now();
        console.log(`[DataTableManager] Event delegation setup took ${(eventSetupTime - domInsertTime).toFixed(2)}ms`);
        console.log(`[DataTableManager] ✅ Total render time: ${(eventSetupTime - renderStart).toFixed(2)}ms`);

        // Update column dropdowns
        if (this.updateColumnDropdownsCallback) {
            this.updateColumnDropdownsCallback();
        }
    }

    /**
     * Handle mouse down on cell
     */
    private handleCellMouseDown(e: MouseEvent, cell: HTMLElement): void {
        e.preventDefault();
        e.stopPropagation();  // Prevent event from bubbling to panel resizers

        const rowIndex = parseInt(cell.getAttribute('data-row') || '-1');
        const colIndex = parseInt(cell.getAttribute('data-col') || '-1');

        // Exit edit mode if editing
        if (this.editingCell) {
            this.exitEditMode();
        }

        // Clear column/row selections when clicking on regular cells
        this.selectedColumns.clear();
        this.selectedRows.clear();

        // Start selection
        this.isSelecting = true;
        this.selectionStart = { row: rowIndex, col: colIndex };
        this.selectionEnd = { row: rowIndex, col: colIndex };
        this.selectedCell = cell;

        // Track if Ctrl is pressed for table resizing
        this.isResizingTable = e.ctrlKey || e.metaKey;

        // Update visual selection
        this.updateSelection();

        // Focus the cell for keyboard events
        cell.focus();

        console.log(`[DataTableManager] Cell selected: [${rowIndex}, ${colIndex}], Ctrl/Cmd pressed: ${this.isResizingTable}`);
    }

    /**
     * Handle mouse over on cell (for drag selection)
     */
    private handleCellMouseOver(cell: HTMLElement): void {
        if (!this.isSelecting || !this.selectionStart) return;

        const rowIndex = parseInt(cell.getAttribute('data-row') || '-1');
        const colIndex = parseInt(cell.getAttribute('data-col') || '-1');

        if (rowIndex === -1 || colIndex === -1) return;

        this.selectionEnd = { row: rowIndex, col: colIndex };

        // If Ctrl+dragging, resize table to match selection
        if (this.isResizingTable) {
            this.resizeTableToSelection();
        }

        this.updateSelection();

        console.log(`[DataTableManager] Selection extended to: [${rowIndex}, ${colIndex}]`);
    }

    /**
     * Enter edit mode for a cell
     */
    private enterEditMode(cell: HTMLElement): void {
        this.exitEditMode(); // Exit any existing edit mode

        cell.contentEditable = 'true';
        cell.focus();
        this.editingCell = cell;

        // Select all text
        const range = document.createRange();
        range.selectNodeContents(cell);
        const selection = window.getSelection();
        selection?.removeAllRanges();
        selection?.addRange(range);

        // On blur, exit edit mode
        this.editingCellBlurHandler = () => {
            // Only exit if we're still editing this cell
            if (this.editingCell === cell) {
                this.exitEditMode();
            }
        };
        cell.addEventListener('blur', this.editingCellBlurHandler);
    }

    /**
     * Exit edit mode
     */
    private exitEditMode(): void {
        if (!this.editingCell) return;

        // Remove blur handler
        if (this.editingCellBlurHandler) {
            this.editingCell.removeEventListener('blur', this.editingCellBlurHandler);
            this.editingCellBlurHandler = null;
        }

        this.editingCell.contentEditable = 'false';
        this.handleCellEdit(this.editingCell);
        this.editingCell = null;
    }

    /**
     * Handle cell editing
     */
    private handleCellEdit(cell: HTMLElement): void {
        const rowIndex = cell.getAttribute('data-row');
        const colIndex = cell.getAttribute('data-col');
        const value = cell.textContent?.trim() || '';

        if (cell.tagName === 'TH' && colIndex !== null) {
            // Update column name
            const idx = parseInt(colIndex);
            if (this.currentData && idx < this.currentData.columns.length) {
                const oldName = this.currentData.columns[idx];
                const newName = value || this.getColumnLabel(idx);
                this.currentData.columns[idx] = newName;

                // Update all row data with new column name
                this.currentData.rows.forEach(row => {
                    if (oldName in row) {
                        row[newName] = row[oldName];
                        if (oldName !== newName) {
                            delete row[oldName];
                        }
                    }
                });

                if (this.updateColumnDropdownsCallback) {
                    this.updateColumnDropdownsCallback();
                }
                console.log('[DataTableManager] Column renamed:', oldName, '->', newName);
            }
        } else if (rowIndex !== null && colIndex !== null) {
            // Update cell value
            const rIdx = parseInt(rowIndex);
            const cIdx = parseInt(colIndex);
            if (this.currentData && rIdx < this.currentData.rows.length && cIdx < this.currentData.columns.length) {
                const colName = this.currentData.columns[cIdx];
                const numValue = parseFloat(value);
                this.currentData.rows[rIdx][colName] = isNaN(numValue) || value === '' ? value : numValue;
                console.log(`[DataTableManager] Cell updated [${rIdx},${cIdx}]:`, value);
            }
        }
    }

    /**
     * Update visual selection
     */
    private updateSelection(): void {
        if (!this.selectionStart || !this.selectionEnd) return;

        // Clear previous selection
        const allCells = document.querySelectorAll('.data-table td, .data-table th');
        allCells.forEach(cell => cell.classList.remove('selected', 'header-highlighted'));

        // Remove previous border and fill handle
        document.querySelectorAll('.selection-border-overlay, .fill-handle').forEach(el => el.remove());

        // Calculate selection bounds
        const startRow = Math.min(this.selectionStart.row, this.selectionEnd.row);
        const endRow = Math.max(this.selectionStart.row, this.selectionEnd.row);
        const startCol = Math.min(this.selectionStart.col, this.selectionEnd.col);
        const endCol = Math.max(this.selectionStart.col, this.selectionEnd.col);

        // Apply selection
        let firstCell: HTMLElement | null = null;
        let lastCell: HTMLElement | null = null;

        for (let r = startRow; r <= endRow; r++) {
            for (let c = startCol; c <= endCol; c++) {
                const cell = this.getCellAt(r, c);
                if (cell) {
                    cell.classList.add('selected');
                    if (!firstCell) firstCell = cell;
                    lastCell = cell;
                }
            }
        }

        // Highlight corresponding row numbers and column headers (Excel-like)
        const allRowNumbers = document.querySelectorAll('.row-number');
        for (let r = startRow; r <= endRow; r++) {
            if (allRowNumbers[r]) {
                allRowNumbers[r].classList.add('header-highlighted');
            }
        }

        for (let c = startCol; c <= endCol; c++) {
            const columnHeader = document.querySelector(`th[data-col="${c}"]`);
            if (columnHeader) {
                columnHeader.classList.add('header-highlighted');
            }
        }

        // Add dashed border overlay and fill handle
        if (firstCell && lastCell) {
            const container = document.querySelector('.data-table-container') as HTMLElement;
            if (!container) return;

            const containerRect = container.getBoundingClientRect();
            const firstRect = firstCell.getBoundingClientRect();
            const lastRect = lastCell.getBoundingClientRect();

            const borderOffset = 1;

            const left = firstRect.left - containerRect.left + container.scrollLeft;
            const top = firstRect.top - containerRect.top + container.scrollTop;
            const width = lastRect.right - firstRect.left;
            const height = lastRect.bottom - firstRect.top;

            // Create dashed border overlay
            const borderOverlay = document.createElement('div');
            borderOverlay.className = 'selection-border-overlay';
            borderOverlay.style.left = (left - borderOffset) + 'px';
            borderOverlay.style.top = (top - borderOffset) + 'px';
            borderOverlay.style.width = (width + borderOffset * 2) + 'px';
            borderOverlay.style.height = (height + borderOffset * 2) + 'px';
            container.appendChild(borderOverlay);

            // Create fill handle (small square at bottom-right)
            const fillHandle = document.createElement('div');
            fillHandle.className = 'fill-handle';
            fillHandle.style.left = (left + width - 4 + borderOffset) + 'px';
            fillHandle.style.top = (top + height - 4 + borderOffset) + 'px';
            container.appendChild(fillHandle);

            // Add fill handle drag functionality
            fillHandle.addEventListener('mousedown', (e) => this.handleFillHandleMouseDown(e));
        }
    }

    /**
     * Handle fill handle mouse down (start drag-to-fill)
     */
    private handleFillHandleMouseDown(e: MouseEvent): void {
        e.preventDefault();
        e.stopPropagation();

        if (!this.selectionStart || !this.selectionEnd || !this.currentData) return;

        const startRow = Math.min(this.selectionStart.row, this.selectionEnd.row);
        const endRow = Math.max(this.selectionStart.row, this.selectionEnd.row);
        const startCol = Math.min(this.selectionStart.col, this.selectionEnd.col);
        const endCol = Math.max(this.selectionStart.col, this.selectionEnd.col);

        let isFilling = true;
        let fillRow = endRow;
        let fillCol = endCol;

        const handleMouseMove = (e: MouseEvent) => {
            if (!isFilling) return;

            // Get cell under mouse
            const element = document.elementFromPoint(e.clientX, e.clientY) as HTMLElement;
            if (!element || !element.hasAttribute('data-row')) return;

            const newFillRow = parseInt(element.getAttribute('data-row') || '0');
            const newFillCol = parseInt(element.getAttribute('data-col') || '0');

            // Update fill preview
            if (newFillRow !== fillRow || newFillCol !== fillCol) {
                fillRow = newFillRow;
                fillCol = newFillCol;
                this.showFillPreview(startRow, endRow, startCol, endCol, fillRow, fillCol);
            }
        };

        const handleMouseUp = () => {
            if (!isFilling) return;
            isFilling = false;

            // Apply fill
            this.applyFill(startRow, endRow, startCol, endCol, fillRow, fillCol);

            // Clean up
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
            document.querySelectorAll('.fill-preview').forEach(el => el.classList.remove('fill-preview'));
        };

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);

        console.log('[DataTableManager] Fill handle drag started');
    }

    /**
     * Show fill preview
     */
    private showFillPreview(startRow: number, endRow: number, startCol: number, endCol: number,
                           fillRow: number, fillCol: number): void {
        // Remove previous preview
        document.querySelectorAll('.fill-preview').forEach(el => el.classList.remove('fill-preview'));

        // Add preview class to fill range
        const fillStartRow = Math.min(endRow + 1, fillRow);
        const fillEndRow = Math.max(endRow, fillRow);
        const fillStartCol = Math.min(endCol + 1, fillCol);
        const fillEndCol = Math.max(endCol, fillCol);

        for (let r = fillStartRow; r <= fillEndRow; r++) {
            for (let c = fillStartCol; c <= fillEndCol; c++) {
                const cell = this.getCellAt(r, c);
                if (cell) {
                    cell.classList.add('fill-preview');
                }
            }
        }
    }

    /**
     * Apply fill (auto-fill cells)
     */
    private applyFill(startRow: number, endRow: number, startCol: number, endCol: number,
                     fillRow: number, fillCol: number): void {
        if (!this.currentData) return;

        // Determine fill direction
        const fillDown = fillRow > endRow;
        const fillRight = fillCol > endCol;

        if (fillDown) {
            // Fill down
            for (let r = endRow + 1; r <= fillRow; r++) {
                for (let c = startCol; c <= endCol; c++) {
                    // Copy from the row above (simple fill)
                    const sourceRow = endRow;
                    const sourceCol = c;
                    const sourceCell = this.getCellAt(sourceRow, sourceCol);
                    if (sourceCell && r < this.currentData.rows.length && c < this.currentData.columns.length) {
                        const colName = this.currentData.columns[c];
                        const value = this.currentData.rows[sourceRow][colName];
                        this.currentData.rows[r][colName] = value;
                    }
                }
            }
        }

        if (fillRight) {
            // Fill right
            for (let c = endCol + 1; c <= fillCol; c++) {
                for (let r = startRow; r <= endRow; r++) {
                    // Copy from the column to the left
                    const sourceRow = r;
                    const sourceCol = endCol;
                    const sourceCell = this.getCellAt(sourceRow, sourceCol);
                    if (sourceCell && r < this.currentData.rows.length && c < this.currentData.columns.length) {
                        const colName = this.currentData.columns[c];
                        const sourceColName = this.currentData.columns[sourceCol];
                        const value = this.currentData.rows[r][sourceColName];
                        this.currentData.rows[r][colName] = value;
                    }
                }
            }
        }

        this.renderEditableDataTable();

        if (this.statusBarCallback) {
            this.statusBarCallback('Fill completed');
        }
        console.log('[DataTableManager] Fill applied');
    }

    /**
     * Handle column header mouse down (start column selection)
     */
    private handleColumnHeaderMouseDown(e: MouseEvent, header: HTMLElement): void {
        e.preventDefault();
        e.stopPropagation();  // Prevent event from bubbling to panel resizers

        const colIndex = parseInt(header.getAttribute('data-col') || '-1');
        if (colIndex === -1) return;

        // Clear previous selections
        this.selectedColumns.clear();
        this.selectedRows.clear();

        // Start column drag selection
        this.isSelectingColumns = true;
        this.columnSelectionStart = colIndex;
        this.selectedColumns.add(colIndex);

        this.updateColumnRowSelection();
        console.log('[DataTableManager] Column selection started:', colIndex);
    }

    /**
     * Handle column header mouse over (during drag)
     */
    private handleColumnHeaderMouseOver(header: HTMLElement): void {
        if (!this.isSelectingColumns) return;

        const colIndex = parseInt(header.getAttribute('data-col') || '-1');
        if (colIndex === -1) return;

        // Select range from start to current
        this.selectedColumns.clear();
        const start = Math.min(this.columnSelectionStart, colIndex);
        const end = Math.max(this.columnSelectionStart, colIndex);

        for (let i = start; i <= end; i++) {
            this.selectedColumns.add(i);
        }

        this.updateColumnRowSelection();
    }

    /**
     * Handle row number mouse down (start row selection)
     */
    private handleRowNumberMouseDown(e: MouseEvent, rowElement: HTMLElement): void {
        e.preventDefault();
        e.stopPropagation();  // Prevent event from bubbling to panel resizers

        // Get row index from the parent tr
        const tr = rowElement.closest('tr');
        if (!tr) return;

        const firstCell = tr.querySelector('td[data-row]') as HTMLElement;
        if (!firstCell) return;

        const rowIndex = parseInt(firstCell.getAttribute('data-row') || '-1');
        if (rowIndex === -1) return;

        // Clear previous selections
        this.selectedColumns.clear();
        this.selectedRows.clear();

        // Start row drag selection
        this.isSelectingRows = true;
        this.rowSelectionStart = rowIndex;
        this.selectedRows.add(rowIndex);

        this.updateColumnRowSelection();
        console.log('[DataTableManager] Row selection started:', rowIndex);
    }

    /**
     * Handle row number mouse over (during drag)
     */
    private handleRowNumberMouseOver(rowElement: HTMLElement): void {
        if (!this.isSelectingRows) return;

        // Get row index from the parent tr
        const tr = rowElement.closest('tr');
        if (!tr) return;

        const firstCell = tr.querySelector('td[data-row]') as HTMLElement;
        if (!firstCell) return;

        const rowIndex = parseInt(firstCell.getAttribute('data-row') || '-1');
        if (rowIndex === -1) return;

        // Select range from start to current
        this.selectedRows.clear();
        const start = Math.min(this.rowSelectionStart, rowIndex);
        const end = Math.max(this.rowSelectionStart, rowIndex);

        for (let i = start; i <= end; i++) {
            this.selectedRows.add(i);
        }

        this.updateColumnRowSelection();
    }

    /**
     * Update visual selection for columns/rows
     */
    private updateColumnRowSelection(): void {
        // Clear all selections first
        const allCells = document.querySelectorAll('.data-table td, .data-table th');
        allCells.forEach(cell => cell.classList.remove('selected'));

        // Select columns
        this.selectedColumns.forEach(colIndex => {
            // Select header
            const header = document.querySelector(`th[data-col="${colIndex}"]`);
            header?.classList.add('selected');

            // Select all cells in column
            const cells = document.querySelectorAll(`td[data-col="${colIndex}"]`);
            cells.forEach(cell => cell.classList.add('selected'));
        });

        // Select rows
        this.selectedRows.forEach(rowIndex => {
            // Select row number
            const cells = document.querySelectorAll(`td[data-row="${rowIndex}"]`);
            cells.forEach(cell => cell.classList.add('selected'));
        });
    }

    /**
     * Handle table copy event (native browser copy)
     */
    private handleTableCopy(e: ClipboardEvent): void {
        e.preventDefault();
        this.copySelectionToClipboard();
    }

    /**
     * Copy selected cells to clipboard (Excel-compatible format)
     */
    private async copySelectionToClipboard(): Promise<void> {
        console.log('[DataTableManager] Copy called');

        if (!this.currentData || !this.selectionStart || !this.selectionEnd) {
            console.warn('[DataTableManager] No selection to copy');
            return;
        }

        const startRow = Math.min(this.selectionStart.row, this.selectionEnd.row);
        const endRow = Math.max(this.selectionStart.row, this.selectionEnd.row);
        const startCol = Math.min(this.selectionStart.col, this.selectionEnd.col);
        const endCol = Math.max(this.selectionStart.col, this.selectionEnd.col);

        // Build tab-separated text (Excel format)
        const lines: string[] = [];
        for (let r = startRow; r <= endRow; r++) {
            const rowValues: string[] = [];
            for (let c = startCol; c <= endCol; c++) {
                if (r < this.currentData.rows.length && c < this.currentData.columns.length) {
                    const colName = this.currentData.columns[c];
                    const value = this.currentData.rows[r][colName];
                    rowValues.push(value !== undefined && value !== null ? String(value) : '');
                } else {
                    rowValues.push('');
                }
            }
            lines.push(rowValues.join('\t'));
        }

        const textToCopy = lines.join('\n');

        try {
            await navigator.clipboard.writeText(textToCopy);
            const rowCount = endRow - startRow + 1;
            const colCount = endCol - startCol + 1;

            if (this.statusBarCallback) {
                this.statusBarCallback(`Copied ${rowCount} row${rowCount > 1 ? 's' : ''} × ${colCount} column${colCount > 1 ? 's' : ''}`);
            }

            console.log('[DataTableManager] Successfully copied to clipboard');
        } catch (error) {
            console.error('[DataTableManager] Failed to copy to clipboard:', error);
            if (this.statusBarCallback) {
                this.statusBarCallback('Copy failed - clipboard access denied');
            }
        }
    }

    /**
     * Handle paste from Excel/clipboard
     */
    private handleTablePaste(e: ClipboardEvent): void {
        e.preventDefault();

        const pasteData = e.clipboardData?.getData('text');
        if (!pasteData) return;

        console.log('[DataTableManager] Paste detected');

        // Parse tab-separated or newline-separated values
        const lines = pasteData.trim().split('\n');
        const rows: string[][] = lines.map(line => {
            if (line.includes('\t')) {
                return line.split('\t');
            } else if (line.split(',').length > 1) {
                return line.split(',');
            } else {
                return [line];
            }
        });

        if (rows.length === 0) return;

        // If we have a selected cell, paste starting from that cell
        if (this.selectedCell) {
            this.pasteToCells(rows);
            return;
        }

        // Otherwise, paste to first data cell (row 0, col 0)
        const firstCell = document.querySelector('td[data-row="0"][data-col="0"]') as HTMLElement;
        if (firstCell) {
            this.selectedCell = firstCell;
            this.pasteToCells(rows);
            return;
        }

        // Otherwise, replace entire table
        const hasHeaders = false;
        const startRow = hasHeaders ? 1 : 0;
        const columns = hasHeaders
            ? rows[0].slice(0, this.maxCols)
            : rows[0].slice(0, this.maxCols).map((_, i) => this.getColumnLabel(i));

        const maxDataRows = Math.min(rows.length - startRow, this.maxRows);

        const dataRows: DataRow[] = [];
        for (let i = startRow; i < startRow + maxDataRows; i++) {
            if (i >= rows.length) break;
            const row: DataRow = {};
            columns.forEach((col, colIndex) => {
                const value = rows[i][colIndex]?.trim() || '';
                const numValue = parseFloat(value);
                row[col] = isNaN(numValue) || value === '' ? value : numValue;
            });
            dataRows.push(row);
        }

        this.currentData = { columns, rows: dataRows };

        // Enable virtual scrolling for large datasets
        if (dataRows.length > 100) {
            this.virtualScrollEnabled = true;
            this.visibleRowStart = 0;
            this.visibleRowEnd = 50;  // Start by showing first 50 rows
            console.log(`[DataTableManager] Large dataset detected (${dataRows.length} rows) - virtual scrolling enabled`);
        }

        this.renderEditableDataTable();

        const truncatedMsg = (rows.length - startRow > this.maxRows || rows[0].length > this.maxCols)
            ? ' (truncated to fit limits)'
            : '';

        if (this.statusBarCallback) {
            this.statusBarCallback(`Pasted ${dataRows.length} rows × ${columns.length} columns${truncatedMsg}`);
        }

        console.log('[DataTableManager] Data pasted:', this.currentData);
    }

    /**
     * Paste data to cells starting from selected cell
     */
    private pasteToCells(rows: string[][]): void {
        if (!this.selectedCell || !this.currentData) return;

        const startRow = parseInt(this.selectedCell.getAttribute('data-row') || '0');
        const startCol = parseInt(this.selectedCell.getAttribute('data-col') || '0');

        const neededRows = startRow + rows.length;
        const neededCols = startCol + (rows[0]?.length || 0);

        // Expand columns if needed (up to max)
        while (this.currentData.columns.length < neededCols && this.currentData.columns.length < this.maxCols) {
            const newColIndex = this.currentData.columns.length;
            const newColName = this.getColumnLabel(newColIndex);
            this.currentData.columns.push(newColName);
            // Add empty cells to existing rows
            this.currentData.rows.forEach(row => {
                row[newColName] = '';
            });
        }

        // Expand rows if needed (up to max)
        while (this.currentData.rows.length < neededRows && this.currentData.rows.length < this.maxRows) {
            const newRow: DataRow = {};
            this.currentData.columns.forEach(col => {
                newRow[col] = '';
            });
            this.currentData.rows.push(newRow);
        }

        // Paste data cell by cell
        for (let r = 0; r < rows.length; r++) {
            const targetRow = startRow + r;
            if (targetRow >= this.currentData.rows.length) break;

            for (let c = 0; c < rows[r].length; c++) {
                const targetCol = startCol + c;
                if (targetCol >= this.currentData.columns.length) break;

                const colName = this.currentData.columns[targetCol];
                const value = rows[r][c]?.trim() || '';
                const numValue = parseFloat(value);
                this.currentData.rows[targetRow][colName] = isNaN(numValue) || value === '' ? value : numValue;
            }
        }

        this.renderEditableDataTable();

        if (this.statusBarCallback) {
            this.statusBarCallback(`Pasted ${rows.length} rows × ${rows[0].length} columns (Table expanded to ${this.currentData.rows.length} × ${this.currentData.columns.length})`);
        }

        console.log('[DataTableManager] Cell paste completed with expansion');
    }

    /**
     * Handle keyboard navigation in cells
     */
    private handleCellKeydown(e: KeyboardEvent, cell: HTMLElement): void {
        // If in edit mode, handle differently
        if (this.editingCell === cell) {
            if (e.key === 'Escape') {
                e.preventDefault();
                this.exitEditMode();
                cell.focus();
            } else if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.exitEditMode();
                // Move down
                const rowIndex = parseInt(cell.getAttribute('data-row') || '-1');
                const colIndex = parseInt(cell.getAttribute('data-col') || '-1');
                if (this.currentData && rowIndex < this.currentData.rows.length - 1) {
                    const targetCell = this.getCellAt(rowIndex + 1, colIndex);
                    if (targetCell) {
                        this.handleCellMouseDown(new MouseEvent('mousedown'), targetCell);
                    }
                }
            } else if (e.key === 'Enter' && e.shiftKey) {
                e.preventDefault();
                this.exitEditMode();
                // Move up with Shift+Enter
                const rowIndex = parseInt(cell.getAttribute('data-row') || '-1');
                const colIndex = parseInt(cell.getAttribute('data-col') || '-1');
                if (rowIndex > 0) {
                    const targetCell = this.getCellAt(rowIndex - 1, colIndex);
                    if (targetCell) {
                        this.handleCellMouseDown(new MouseEvent('mousedown'), targetCell);
                    }
                }
            } else if (e.key === 'Tab' && !e.shiftKey) {
                e.preventDefault();
                this.exitEditMode();
                // Move right with Tab
                const rowIndex = parseInt(cell.getAttribute('data-row') || '-1');
                const colIndex = parseInt(cell.getAttribute('data-col') || '-1');
                if (this.currentData && colIndex < this.currentData.columns.length - 1) {
                    const targetCell = this.getCellAt(rowIndex, colIndex + 1);
                    if (targetCell) {
                        this.handleCellMouseDown(new MouseEvent('mousedown'), targetCell);
                    }
                } else if (this.currentData && rowIndex < this.currentData.rows.length - 1) {
                    // Wrap to next row
                    const targetCell = this.getCellAt(rowIndex + 1, 0);
                    if (targetCell) {
                        this.handleCellMouseDown(new MouseEvent('mousedown'), targetCell);
                    }
                }
            } else if (e.key === 'Tab' && e.shiftKey) {
                e.preventDefault();
                this.exitEditMode();
                // Move left with Shift+Tab
                const rowIndex = parseInt(cell.getAttribute('data-row') || '-1');
                const colIndex = parseInt(cell.getAttribute('data-col') || '-1');
                if (colIndex > 0) {
                    const targetCell = this.getCellAt(rowIndex, colIndex - 1);
                    if (targetCell) {
                        this.handleCellMouseDown(new MouseEvent('mousedown'), targetCell);
                    }
                } else if (rowIndex > 0 && this.currentData) {
                    // Wrap to previous row
                    const targetCell = this.getCellAt(rowIndex - 1, this.currentData.columns.length - 1);
                    if (targetCell) {
                        this.handleCellMouseDown(new MouseEvent('mousedown'), targetCell);
                    }
                }
            } else if (e.key === 'F2') {
                // F2 in edit mode - exit edit mode
                e.preventDefault();
                this.exitEditMode();
                cell.focus();
            }
            return;
        }

        const rowIndex = parseInt(cell.getAttribute('data-row') || '-1');
        const colIndex = parseInt(cell.getAttribute('data-col') || '-1');

        if (rowIndex === -1 || colIndex === -1) return;

        let targetCell: HTMLElement | null = null;

        // Check if it's a printable character or backspace/delete
        if (e.key.length === 1 || e.key === 'Backspace' || e.key === 'Delete') {
            // Enter edit mode and let the character be typed
            this.enterEditMode(cell);
            if (e.key === 'Backspace' || e.key === 'Delete') {
                e.preventDefault();
                cell.textContent = '';
            }
            return;
        }

        switch (e.key) {
            case 'ArrowUp':
                e.preventDefault();
                if (rowIndex > 0) {
                    targetCell = this.getCellAt(rowIndex - 1, colIndex);
                }
                break;

            case 'ArrowDown':
                e.preventDefault();
                if (this.currentData && rowIndex < this.currentData.rows.length - 1) {
                    targetCell = this.getCellAt(rowIndex + 1, colIndex);
                }
                break;

            case 'ArrowLeft':
                e.preventDefault();
                if (colIndex > 0) {
                    targetCell = this.getCellAt(rowIndex, colIndex - 1);
                }
                break;

            case 'ArrowRight':
                e.preventDefault();
                if (this.currentData && colIndex < this.currentData.columns.length - 1) {
                    targetCell = this.getCellAt(rowIndex, colIndex + 1);
                }
                break;

            case 'Tab':
                e.preventDefault();
                if (e.shiftKey) {
                    // Shift+Tab - move left
                    if (colIndex > 0) {
                        targetCell = this.getCellAt(rowIndex, colIndex - 1);
                    } else if (rowIndex > 0) {
                        targetCell = this.getCellAt(rowIndex - 1, (this.currentData?.columns.length || 1) - 1);
                    }
                } else {
                    // Tab - move right
                    if (this.currentData && colIndex < this.currentData.columns.length - 1) {
                        targetCell = this.getCellAt(rowIndex, colIndex + 1);
                    } else if (this.currentData && rowIndex < this.currentData.rows.length - 1) {
                        targetCell = this.getCellAt(rowIndex + 1, 0);
                    }
                }
                break;

            case 'Enter':
                e.preventDefault();
                if (e.shiftKey) {
                    // Shift+Enter - move up
                    if (rowIndex > 0) {
                        targetCell = this.getCellAt(rowIndex - 1, colIndex);
                    }
                } else {
                    // Enter - move down (Excel behavior)
                    if (this.currentData && rowIndex < this.currentData.rows.length - 1) {
                        targetCell = this.getCellAt(rowIndex + 1, colIndex);
                    }
                }
                break;

            case 'F2':
                e.preventDefault();
                // F2 - enter edit mode
                this.enterEditMode(cell);
                break;
        }

        if (targetCell) {
            this.handleCellMouseDown(new MouseEvent('mousedown'), targetCell);
        }
    }

    /**
     * Get cell element at specific position
     */
    private getCellAt(row: number, col: number): HTMLElement | null {
        // Try td first (data cells)
        let cell = document.querySelector(`td[data-row="${row}"][data-col="${col}"]`);
        // If not found and row is -1, try th (header cells)
        if (!cell && row === -1) {
            cell = document.querySelector(`th[data-col="${col}"]`);
        }
        return cell as HTMLElement | null;
    }

    /**
     * Resize table to match current selection (Ctrl+drag)
     */
    private resizeTableToSelection(): void {
        if (!this.selectionStart || !this.selectionEnd || !this.currentData) return;

        const endRow = Math.max(this.selectionStart.row, this.selectionEnd.row);
        const endCol = Math.max(this.selectionStart.col, this.selectionEnd.col);

        const currentRowCount = this.currentData.rows.length;
        const currentColCount = this.currentData.columns.length;

        const needRows = endRow + 1;  // +1 because rows are 0-indexed
        const needCols = endCol + 1;  // +1 because cols are 0-indexed

        let changed = false;

        // Add rows if needed
        if (needRows > currentRowCount) {
            const rowsToAdd = needRows - currentRowCount;
            for (let i = 0; i < rowsToAdd; i++) {
                const row: DataRow = {};
                this.currentData.columns.forEach(col => {
                    row[col] = '';
                });
                this.currentData.rows.push(row);
            }
            changed = true;
        }

        // Add columns if needed
        if (needCols > currentColCount) {
            const colsToAdd = needCols - currentColCount;
            for (let i = 0; i < colsToAdd; i++) {
                const newColLabel = this.getColumnLabel(currentColCount + i);
                this.currentData.columns.push(newColLabel);
                // Add empty value to all rows for new column
                this.currentData.rows.forEach(row => {
                    row[newColLabel] = '';
                });
            }
            changed = true;
        }

        // Re-render table if changed
        if (changed) {
            // Preserve current selection state
            const prevSelectionStart = this.selectionStart;
            const prevSelectionEnd = this.selectionEnd;

            this.renderEditableDataTable();

            // Restore selection state after re-render
            this.selectionStart = prevSelectionStart;
            this.selectionEnd = prevSelectionEnd;
            this.updateSelection();

            // Reapply rulers area transform after table re-render
            if (this.updateRulersAreaTransformCallback) {
                this.updateRulersAreaTransformCallback();
            }

            const rowCount = this.currentData.rows.length;
            const colCount = this.currentData.columns.length;

            if (this.statusBarCallback) {
                this.statusBarCallback(`Resized - ${rowCount} rows × ${colCount} columns`);
            }
        }
    }

    /**
     * Clear cell selection
     */
    public clearSelection(): void {
        this.selectionStart = null;
        this.selectionEnd = null;
    }

    /**
     * Get column label (1, 2, 3, ...)
     */
    private getColumnLabel(index: number): string {
        return `${index + 1}`;
    }

    /**
     * Generate HTML table
     */
    public generateTableHTML(data: Dataset, tableType: string): string {
        const tableClass = tableType === 'mini' ? 'mini-table' : 'data-table';
        let html = `<table class="${tableClass}" style="width: 100%; border-collapse: collapse; font-size: ${tableType === 'mini' ? '11px' : '13px'};">`;

        // Headers
        html += '<thead style="background: var(--bg-secondary); position: sticky; top: 0;"><tr>';
        data.columns.forEach(col => {
            html += `<th style="padding: 8px; text-align: left; border-bottom: 2px solid var(--border-default); font-weight: 600;">${col}</th>`;
        });
        html += '</tr></thead>';

        // Rows
        html += '<tbody>';
        data.rows.forEach((row, index) => {
            const bgColor = index % 2 === 0 ? 'var(--bg-primary)' : 'var(--bg-secondary)';
            html += `<tr style="background: ${bgColor};">`;
            data.columns.forEach(col => {
                const value = row[col];
                const displayValue = typeof value === 'number' ? value.toFixed(4) : value;
                html += `<td style="padding: 6px 8px; border-bottom: 1px solid var(--border-muted);">${displayValue}</td>`;
            });
            html += '</tr>';
        });
        html += '</tbody></table>';

        return html;
    }

    /**
     * Setup virtual scrolling for incremental rendering
     */
    private setupVirtualScrolling(): void {
        const dataContainer = document.querySelector('.data-table-container') as HTMLElement;
        if (!dataContainer || !this.virtualScrollEnabled) return;

        let scrollTimeout: number | null = null;

        dataContainer.addEventListener('scroll', () => {
            // Debounce scroll events for performance
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }

            scrollTimeout = window.setTimeout(() => {
                this.updateVisibleRange();
            }, 100);  // 100ms debounce
        });

        console.log('[DataTableManager] Virtual scrolling enabled');
    }

    /**
     * Update visible row range based on scroll position
     */
    private updateVisibleRange(): void {
        if (!this.currentData || !this.virtualScrollEnabled) return;

        const dataContainer = document.querySelector('.data-table-container') as HTMLElement;
        if (!dataContainer) return;

        const scrollTop = dataContainer.scrollTop;
        const containerHeight = dataContainer.clientHeight;

        // Calculate which rows are visible
        const firstVisibleRow = Math.floor(scrollTop / this.ROW_HEIGHT);
        const visibleRowCount = Math.ceil(containerHeight / this.ROW_HEIGHT);

        // Add buffer rows above and below
        const newStart = Math.max(0, firstVisibleRow - this.BUFFER_ROWS);
        const newEnd = Math.min(this.currentData.rows.length, firstVisibleRow + visibleRowCount + this.BUFFER_ROWS);

        // Only re-render if range changed significantly
        if (newStart !== this.visibleRowStart || newEnd !== this.visibleRowEnd) {
            this.visibleRowStart = newStart;
            this.visibleRowEnd = newEnd;

            console.log(`[DataTableManager] Scroll update: rendering rows ${newStart}-${newEnd}`);
            this.renderEditableDataTable();
        }
    }
}
