/**
 * TableData - Handles data storage and loading operations
 *
 * Responsibilities:
 * - Data storage (currentData)
 * - Initialize blank table
 * - File import (CSV)
 * - CSV parsing
 * - Demo data loading
 * - Data state management
 */

import { Dataset, DataRow, TABLE_CONSTANTS } from '../types.js';

export class TableData {
    private currentData: Dataset | null = null;
    private firstRowIsHeader: boolean = true;
    private firstColIsIndex: boolean = false;
    private defaultRows: number = TABLE_CONSTANTS.DEFAULT_ROWS;
    private defaultCols: number = TABLE_CONSTANTS.DEFAULT_COLS;
    private maxRows: number = TABLE_CONSTANTS.MAX_ROWS;
    private maxCols: number = TABLE_CONSTANTS.MAX_COLS;

    constructor(
        private statusBarCallback?: (message: string) => void,
        private updateColumnDropdownsCallback?: () => void
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
     * Get first row is header setting
     */
    public getFirstRowIsHeader(): boolean {
        return this.firstRowIsHeader;
    }

    /**
     * Set first row is header setting
     */
    public setFirstRowIsHeader(value: boolean): void {
        this.firstRowIsHeader = value;
    }

    /**
     * Get first column is index setting
     */
    public getFirstColIsIndex(): boolean {
        return this.firstColIsIndex;
    }

    /**
     * Set first column is index setting
     */
    public setFirstColIsIndex(value: boolean): void {
        this.firstColIsIndex = value;
    }

    /**
     * Get max rows
     */
    public getMaxRows(): number {
        return this.maxRows;
    }

    /**
     * Get max columns
     */
    public getMaxCols(): number {
        return this.maxCols;
    }

    /**
     * Initialize blank table based on container size
     * @returns The created dataset
     */
    public initializeBlankTable(): Dataset {
        const startTime = performance.now();
        console.log('[TableData] Starting table initialization...');

        // PERFORMANCE: Start with large table that supports virtual scrolling
        // Virtual scrolling will handle rendering efficiently
        const initialRows = 1000;  // 1000 rows - virtual scrolling handles performance
        const initialCols = 32;  // 32 columns (A-AF)
        console.log(`[TableData] Creating ${initialRows} rows × ${initialCols} columns = ${initialRows * initialCols} cells`);

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

        const dataCreateTime = performance.now();
        console.log(`[TableData] Data structure created in ${(dataCreateTime - startTime).toFixed(2)}ms`);

        if (this.statusBarCallback) {
            this.statusBarCallback(`Ready - ${initialRows} rows × ${initialCols} columns`);
        }

        console.log('[TableData] Blank table initialized:', initialRows, 'x', initialCols);

        return this.currentData;
    }

    /**
     * Handle file import
     */
    public handleFileImport(file: File): void {
        console.log(`[TableData] Importing file: ${file.name}`);

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
                console.warn('[TableData] Excel import not yet implemented');
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

            if (this.updateColumnDropdownsCallback) {
                this.updateColumnDropdownsCallback();
            }

            if (this.statusBarCallback) {
                this.statusBarCallback(`Loaded ${filename} - ${rows.length} rows × ${headers.length} columns`);
            }

            console.log('[TableData] Data loaded:', this.currentData);
        } catch (error) {
            console.error('[TableData] CSV parsing error:', error);
            if (this.statusBarCallback) {
                this.statusBarCallback('Error parsing CSV file');
            }
        }
    }

    /**
     * Load demo data
     */
    public loadDemoData(): void {
        console.log('[TableData] Loading demo data...');

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

        if (this.updateColumnDropdownsCallback) {
            this.updateColumnDropdownsCallback();
        }

        if (this.statusBarCallback) {
            this.statusBarCallback(`Demo data loaded - ${rows.length} rows × 2 columns`);
        }

        console.log('[TableData] Demo data loaded:', this.currentData);
    }

    /**
     * Get column label (1, 2, 3, ...)
     */
    private getColumnLabel(index: number): string {
        return `${index + 1}`;
    }

    /**
     * Add columns to the table
     */
    public addColumns(count: number): boolean {
        if (!this.currentData) return false;

        const currentColCount = this.currentData.columns.length;
        const newColCount = Math.min(currentColCount + count, this.maxCols);

        if (newColCount === currentColCount) {
            console.warn('[TableData] Cannot add columns - max columns reached');
            return false;
        }

        for (let i = currentColCount; i < newColCount; i++) {
            const newColName = this.getColumnLabel(i);
            this.currentData.columns.push(newColName);
            // Add empty cells to existing rows
            this.currentData.rows.forEach(row => {
                row[newColName] = '';
            });
        }

        const addedCount = newColCount - currentColCount;
        if (this.statusBarCallback) {
            this.statusBarCallback(`Added ${addedCount} columns (Total: ${this.currentData.rows.length} rows × ${this.currentData.columns.length} columns)`);
        }

        console.log(`[TableData] Columns added. Total: ${this.currentData.columns.length}`);
        return true;
    }

    /**
     * Add rows to the table
     */
    public addRows(count: number): boolean {
        if (!this.currentData) return false;

        const currentRowCount = this.currentData.rows.length;
        const newRowCount = Math.min(currentRowCount + count, this.maxRows);

        if (newRowCount === currentRowCount) {
            console.warn('[TableData] Cannot add rows - max rows reached');
            return false;
        }

        for (let i = currentRowCount; i < newRowCount; i++) {
            const newRow: DataRow = {};
            this.currentData.columns.forEach(col => {
                newRow[col] = '';
            });
            this.currentData.rows.push(newRow);
        }

        const addedCount = newRowCount - currentRowCount;
        if (this.statusBarCallback) {
            this.statusBarCallback(`Added ${addedCount} rows (Total: ${this.currentData.rows.length} rows × ${this.currentData.columns.length} columns)`);
        }

        console.log(`[TableData] Rows added. Total: ${this.currentData.rows.length}`);
        return true;
    }
}
