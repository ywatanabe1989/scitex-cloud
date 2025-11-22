/**
 * Table Preview Modal Module
 * Handles table preview with CRUD operations
 */

console.log("[DEBUG] table-preview-modal.ts loaded");

import { getCsrfToken } from "../shared/utils.js";

interface TableData {
  data: Record<string, any>[];
  columns: string[];
  metadata: {
    file_name: string;
    file_path: string;
    file_type: string;
    file_hash: string;
    rows: number;
    cols: number;
  };
}

export class TablePreviewModal {
  private projectId: string | null = null;
  private currentTable: TableData | null = null;
  private currentFileHash: string | null = null;
  private selectedRows: Set<number> = new Set();
  private modifiedCells: Map<string, any> = new Map(); // key: "row-col", value: new value
  private renamedColumns: Map<string, string> = new Map(); // key: old name, value: new name
  private deletedColumns: Set<string> = new Set();
  private isModified: boolean = false;

  constructor() {
    this.init();
  }

  private init(): void {
    // Get project ID
    const writerConfig = (window as any).WRITER_CONFIG;
    if (writerConfig?.projectId) {
      this.projectId = String(writerConfig.projectId);
    }

    this.setupEventListeners();
    console.log("[TablePreviewModal] Initialized with project:", this.projectId);
  }

  private setupEventListeners(): void {
    // Add row button
    const addRowBtn = document.getElementById("table-add-row-btn");
    if (addRowBtn) {
      addRowBtn.addEventListener("click", () => this.handleAddRow());
    }

    // Add column button
    const addColumnBtn = document.getElementById("table-add-column-btn");
    if (addColumnBtn) {
      addColumnBtn.addEventListener("click", () => this.handleAddColumn());
    }

    // Delete rows button
    const deleteRowsBtn = document.getElementById("table-delete-rows-btn");
    if (deleteRowsBtn) {
      deleteRowsBtn.addEventListener("click", () => this.handleDeleteRows());
    }

    // Save button
    const saveBtn = document.getElementById("table-save-btn");
    if (saveBtn) {
      saveBtn.addEventListener("click", () => this.handleSave());
    }

    // Export button
    const exportBtn = document.getElementById("table-export-btn");
    if (exportBtn) {
      exportBtn.addEventListener("click", () => this.handleExport());
    }

    // Modal close event
    const modal = document.getElementById("tablePreviewModal");
    if (modal) {
      modal.addEventListener("hidden.bs.modal", () => {
        if (this.isModified) {
          const confirm = window.confirm(
            "You have unsaved changes. Are you sure you want to close?",
          );
          if (!confirm) {
            // Re-open modal
            const bsModal = new (window as any).bootstrap.Modal(modal);
            bsModal.show();
          }
        }
      });
    }

    console.log("[TablePreviewModal] Event listeners setup complete");
  }

  /**
   * Open the preview modal for a table
   */
  async openTable(fileHash: string, fileName: string): Promise<void> {
    if (!this.projectId) {
      console.error("[TablePreviewModal] No project ID available");
      alert("Error: No project ID found");
      return;
    }

    // Reset state
    this.currentFileHash = fileHash;
    this.selectedRows.clear();
    this.modifiedCells.clear();
    this.renamedColumns.clear();
    this.deletedColumns.clear();
    this.isModified = false;
    this.updateModifiedBadge();

    // Update modal title
    const titleEl = document.getElementById("table-preview-title");
    if (titleEl) {
      titleEl.textContent = fileName;
    }

    // Show modal
    const modal = document.getElementById("tablePreviewModal");
    if (modal) {
      const bsModal = new (window as any).bootstrap.Modal(modal);
      bsModal.show();
    }

    // Load data
    await this.loadTableData(fileHash);
  }

  private async loadTableData(fileHash: string): Promise<void> {
    const container = document.getElementById("table-preview-container");
    if (!container) return;

    // Show loading
    container.innerHTML = `
      <div class="text-center text-muted py-4">
        <i class="fas fa-spinner fa-spin me-2"></i>Loading table data...
      </div>
    `;

    try {
      const apiUrl = `/writer/api/project/${this.projectId}/table-data/${fileHash}/`;
      console.log("[TablePreviewModal] Fetching from:", apiUrl);

      const response = await fetch(apiUrl);
      const result = await response.json();

      if (result.success) {
        this.currentTable = result;
        this.renderTable();
        this.updateDimensionsBadge();
      } else {
        this.showError(result.error || "Failed to load table data");
      }
    } catch (error) {
      console.error("[TablePreviewModal] Error loading table:", error);
      this.showError("Network error while loading table");
    }
  }

  private renderTable(): void {
    if (!this.currentTable) return;

    const container = document.getElementById("table-preview-container");
    if (!container) return;

    const { data, columns } = this.currentTable;

    // Create table HTML
    let html = `
      <table class="table-preview-table">
        <thead>
          <tr>
            <th><input type="checkbox" id="select-all-checkbox" title="Select all"></th>
            <th>#</th>
    `;

    columns.forEach((col, colIndex) => {
      const displayName = this.renamedColumns.get(col) || col;
      html += `
        <th>
          <div class="table-column-header">
            <div class="table-column-name">
              <input type="text"
                     value="${this.escapeHtml(displayName)}"
                     data-col-index="${colIndex}"
                     data-original-name="${this.escapeHtml(col)}"
                     class="column-name-input"
                     title="Click to rename column">
            </div>
            <span class="table-column-delete" data-col-index="${colIndex}" title="Delete column">
              <i class="fas fa-times"></i>
            </span>
          </div>
        </th>
      `;
    });

    html += `
          </tr>
        </thead>
        <tbody>
    `;

    data.forEach((row, rowIndex) => {
      const isSelected = this.selectedRows.has(rowIndex);
      html += `
        <tr class="${isSelected ? "selected" : ""}" data-row="${rowIndex}">
          <td><input type="checkbox" class="table-row-checkbox" data-row="${rowIndex}" ${isSelected ? "checked" : ""}></td>
          <td class="table-row-number">${rowIndex + 1}</td>
      `;

      columns.forEach((col, colIndex) => {
        const value = row[col] !== null && row[col] !== undefined ? row[col] : "";
        const cellKey = `${rowIndex}-${colIndex}`;
        const isModified = this.modifiedCells.has(cellKey);
        const displayValue = isModified
          ? this.modifiedCells.get(cellKey)
          : value;

        html += `
          <td class="${isModified ? "modified" : ""}">
            <input type="text"
                   value="${this.escapeHtml(String(displayValue))}"
                   data-row="${rowIndex}"
                   data-col="${colIndex}"
                   data-original="${this.escapeHtml(String(value))}">
          </td>
        `;
      });

      html += `</tr>`;
    });

    html += `
        </tbody>
      </table>
    `;

    container.innerHTML = html;

    // Attach event listeners
    this.attachTableEventListeners();
  }

  private attachTableEventListeners(): void {
    // Select all checkbox
    const selectAllCheckbox = document.getElementById(
      "select-all-checkbox",
    ) as HTMLInputElement;
    if (selectAllCheckbox) {
      selectAllCheckbox.addEventListener("change", (e) => {
        const checked = (e.target as HTMLInputElement).checked;
        document
          .querySelectorAll<HTMLInputElement>(".table-row-checkbox")
          .forEach((checkbox) => {
            checkbox.checked = checked;
            const row = parseInt(checkbox.dataset.row || "0");
            if (checked) {
              this.selectedRows.add(row);
            } else {
              this.selectedRows.delete(row);
            }
          });
        this.updateSelectedRows();
      });
    }

    // Row checkboxes
    document
      .querySelectorAll<HTMLInputElement>(".table-row-checkbox")
      .forEach((checkbox) => {
        checkbox.addEventListener("change", (e) => {
          const row = parseInt((e.target as HTMLInputElement).dataset.row || "0");
          if ((e.target as HTMLInputElement).checked) {
            this.selectedRows.add(row);
          } else {
            this.selectedRows.delete(row);
          }
          this.updateSelectedRows();
        });
      });

    // Cell inputs
    document
      .querySelectorAll<HTMLInputElement>(".table-preview-table td input[type='text']")
      .forEach((input) => {
        input.addEventListener("input", (e) => {
          const target = e.target as HTMLInputElement;
          const row = parseInt(target.dataset.row || "0");
          const col = parseInt(target.dataset.col || "0");
          const original = target.dataset.original || "";
          const newValue = target.value;

          const cellKey = `${row}-${col}`;

          if (newValue !== original) {
            this.modifiedCells.set(cellKey, newValue);
            target.parentElement?.classList.add("modified");
            this.isModified = true;
          } else {
            this.modifiedCells.delete(cellKey);
            target.parentElement?.classList.remove("modified");
            this.isModified = this.modifiedCells.size > 0 || this.renamedColumns.size > 0;
          }

          this.updateModifiedBadge();
        });
      });

    // Column name inputs (for renaming)
    document
      .querySelectorAll<HTMLInputElement>(".column-name-input")
      .forEach((input) => {
        input.addEventListener("change", (e) => {
          const target = e.target as HTMLInputElement;
          const originalName = target.dataset.originalName || "";
          const newName = target.value.trim();

          if (newName && newName !== originalName) {
            this.renamedColumns.set(originalName, newName);
            this.isModified = true;
            this.updateModifiedBadge();
            console.log(`[TablePreviewModal] Column renamed: ${originalName} → ${newName}`);
          } else if (this.renamedColumns.has(originalName)) {
            this.renamedColumns.delete(originalName);
            this.isModified = this.modifiedCells.size > 0 || this.renamedColumns.size > 0;
            this.updateModifiedBadge();
          }
        });
      });

    // Column delete buttons
    document
      .querySelectorAll<HTMLSpanElement>(".table-column-delete")
      .forEach((btn) => {
        btn.addEventListener("click", (e) => {
          const colIndex = parseInt((e.currentTarget as HTMLElement).dataset.colIndex || "0");
          this.handleDeleteColumn(colIndex);
        });
      });
  }

  private updateSelectedRows(): void {
    // Update row styling
    document
      .querySelectorAll<HTMLTableRowElement>("table-preview-table tbody tr")
      .forEach((tr) => {
        const row = parseInt(tr.dataset.row || "0");
        if (this.selectedRows.has(row)) {
          tr.classList.add("selected");
        } else {
          tr.classList.remove("selected");
        }
      });

    // Update delete button
    const deleteBtn = document.getElementById(
      "table-delete-rows-btn",
    ) as HTMLButtonElement;
    if (deleteBtn) {
      deleteBtn.disabled = this.selectedRows.size === 0;
    }
  }

  private updateDimensionsBadge(): void {
    if (!this.currentTable) return;

    const badge = document.getElementById("table-dimensions-badge");
    if (badge) {
      badge.textContent = `${this.currentTable.metadata.rows} rows × ${this.currentTable.metadata.cols} cols`;
    }
  }

  private updateModifiedBadge(): void {
    const badge = document.getElementById("table-modified-badge");
    const saveBtn = document.getElementById(
      "table-save-btn",
    ) as HTMLButtonElement;

    if (badge && saveBtn) {
      if (this.isModified) {
        badge.style.display = "inline-block";
        saveBtn.disabled = false;
      } else {
        badge.style.display = "none";
        saveBtn.disabled = true;
      }
    }
  }

  private handleAddRow(): void {
    if (!this.currentTable) return;

    // Add empty row to data
    const newRow: Record<string, any> = {};
    this.currentTable.columns.forEach((col) => {
      newRow[col] = "";
    });

    this.currentTable.data.push(newRow);
    this.currentTable.metadata.rows++;

    this.isModified = true;
    this.renderTable();
    this.updateDimensionsBadge();
    this.updateModifiedBadge();

    console.log("[TablePreviewModal] Added new row");
  }

  private handleDeleteRows(): void {
    if (!this.currentTable || this.selectedRows.size === 0) return;

    const confirm = window.confirm(
      `Are you sure you want to delete ${this.selectedRows.size} row(s)?`,
    );
    if (!confirm) return;

    // Sort rows in descending order to delete from end
    const rowsToDelete = Array.from(this.selectedRows).sort((a, b) => b - a);

    rowsToDelete.forEach((rowIndex) => {
      this.currentTable!.data.splice(rowIndex, 1);
    });

    this.currentTable.metadata.rows = this.currentTable.data.length;
    this.selectedRows.clear();

    // Clear modified cells for deleted rows
    const keysToDelete: string[] = [];
    this.modifiedCells.forEach((value, key) => {
      const [row] = key.split("-").map(Number);
      if (rowsToDelete.includes(row)) {
        keysToDelete.push(key);
      }
    });
    keysToDelete.forEach((key) => this.modifiedCells.delete(key));

    this.isModified = true;
    this.renderTable();
    this.updateDimensionsBadge();
    this.updateModifiedBadge();
    this.updateSelectedRows();

    console.log("[TablePreviewModal] Deleted rows:", rowsToDelete);
  }

  private handleAddColumn(): void {
    if (!this.currentTable) return;

    // Prompt for column name
    const columnName = window.prompt("Enter new column name:");
    if (!columnName || !columnName.trim()) return;

    const newColName = columnName.trim();

    // Check if column already exists
    if (this.currentTable.columns.includes(newColName)) {
      alert(`Column "${newColName}" already exists!`);
      return;
    }

    // Add column to table
    this.currentTable.columns.push(newColName);
    this.currentTable.metadata.cols++;

    // Add empty values for this column in all rows
    this.currentTable.data.forEach((row) => {
      row[newColName] = "";
    });

    this.isModified = true;
    this.renderTable();
    this.updateDimensionsBadge();
    this.updateModifiedBadge();

    console.log("[TablePreviewModal] Added new column:", newColName);
  }

  private handleDeleteColumn(colIndex: number): void {
    if (!this.currentTable) return;

    const columnName = this.currentTable.columns[colIndex];
    if (!columnName) return;

    const confirm = window.confirm(
      `Are you sure you want to delete column "${columnName}"?\nAll data in this column will be lost.`,
    );
    if (!confirm) return;

    // Remove column from columns array
    this.currentTable.columns.splice(colIndex, 1);
    this.currentTable.metadata.cols--;

    // Remove column data from all rows
    this.currentTable.data.forEach((row) => {
      delete row[columnName];
    });

    // Clean up related tracking
    this.renamedColumns.delete(columnName);

    // Clear modified cells for this column
    const keysToDelete: string[] = [];
    this.modifiedCells.forEach((value, key) => {
      const [row, col] = key.split("-").map(Number);
      if (col === colIndex) {
        keysToDelete.push(key);
      } else if (col > colIndex) {
        // Shift keys for columns after the deleted one
        const newKey = `${row}-${col - 1}`;
        this.modifiedCells.set(newKey, value);
        keysToDelete.push(key);
      }
    });
    keysToDelete.forEach((key) => this.modifiedCells.delete(key));

    this.isModified = true;
    this.renderTable();
    this.updateDimensionsBadge();
    this.updateModifiedBadge();

    console.log("[TablePreviewModal] Deleted column:", columnName);
  }

  private async handleSave(): Promise<void> {
    if (!this.currentTable || !this.currentFileHash || !this.projectId) return;

    // Apply all cell modifications to data
    this.modifiedCells.forEach((value, key) => {
      const [row, col] = key.split("-").map(Number);
      const colName = this.currentTable!.columns[col];
      this.currentTable!.data[row][colName] = value;
    });

    // Apply column renames
    if (this.renamedColumns.size > 0) {
      this.renamedColumns.forEach((newName, oldName) => {
        // Update column name in columns array
        const colIndex = this.currentTable!.columns.indexOf(oldName);
        if (colIndex !== -1) {
          this.currentTable!.columns[colIndex] = newName;
        }

        // Update all row data to use new column name
        this.currentTable!.data.forEach((row) => {
          if (oldName in row) {
            row[newName] = row[oldName];
            delete row[oldName];
          }
        });
      });
    }

    try {
      const apiUrl = `/writer/api/project/${this.projectId}/table-update/${this.currentFileHash}/`;
      console.log("[TablePreviewModal] Saving to:", apiUrl);

      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({
          data: this.currentTable.data,
          columns: this.currentTable.columns,
        }),
      });

      const result = await response.json();

      if (result.success) {
        console.log("[TablePreviewModal] Save successful");
        alert("Table saved successfully!");

        // Reset modification state
        this.modifiedCells.clear();
        this.renamedColumns.clear();
        this.isModified = false;
        this.updateModifiedBadge();

        // Reload data to get updated thumbnail
        await this.loadTableData(this.currentFileHash);
      } else {
        this.showError(result.error || "Failed to save table");
      }
    } catch (error) {
      console.error("[TablePreviewModal] Error saving table:", error);
      this.showError("Network error while saving table");
    }
  }

  private handleExport(): void {
    if (!this.currentTable) return;

    // Convert to CSV
    const { data, columns } = this.currentTable;

    // Header
    let csv = columns.map((col) => this.escapeCsv(col)).join(",") + "\n";

    // Data rows
    data.forEach((row) => {
      const values = columns.map((col) => {
        const value = row[col] !== null && row[col] !== undefined ? row[col] : "";
        return this.escapeCsv(String(value));
      });
      csv += values.join(",") + "\n";
    });

    // Download
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", this.currentTable.metadata.file_name);
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    console.log("[TablePreviewModal] Exported CSV");
  }

  private showError(message: string): void {
    const errorDiv = document.getElementById("table-preview-error");
    const errorMessage = document.getElementById("table-error-message");

    if (errorDiv && errorMessage) {
      errorMessage.textContent = message;
      errorDiv.style.display = "block";
    }

    console.error("[TablePreviewModal] Error:", message);
  }

  private escapeHtml(text: string): string {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  private escapeCsv(text: string): string {
    if (text.includes(",") || text.includes('"') || text.includes("\n")) {
      return '"' + text.replace(/"/g, '""') + '"';
    }
    return text;
  }
}

// Initialize and expose globally
const tablePreviewModal = new TablePreviewModal();
(window as any).tablePreviewModal = tablePreviewModal;

console.log("[TablePreviewModal] Module initialized and exposed globally");
