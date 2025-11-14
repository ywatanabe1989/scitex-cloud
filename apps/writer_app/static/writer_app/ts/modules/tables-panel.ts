/**
 * Tables Panel Module
 * Manages the draggable tables panel in Writer interface
 */

console.log("[DEBUG] tables-panel.ts loaded");

import { statePersistence } from "./state-persistence.js";
import { getCsrfToken } from "../shared/utils.js";

export interface Table {
  id?: number;
  label?: string; // For backwards compatibility
  file_name: string;
  file_path: string;
  file_type?: string;
  file_size?: number;
  file_hash?: string;
  caption?: string;
  dimensions?: string;
  thumbnail_url?: string;
  thumbnail_path?: string;
  width?: number;
  height?: number;
  tags?: string[];
  is_referenced?: number | boolean;
  reference_count?: number;
  source?: string;
  location?: string;
  last_modified?: number;
}

export class TablesPanel {
  private tables: Table[] = [];
  private filteredTables: Table[] = [];
  private isLoaded: boolean = false;
  private projectId: string | null = null;
  private selectedCards: Set<string> = new Set(); // Track selected table labels
  private dragCounter: number = 0;

  constructor() {
    this.init();
  }

  /**
   * Initialize the panel
   */
  private init(): void {
    // Get project ID
    const writerConfig = (window as any).WRITER_CONFIG;
    if (writerConfig?.projectId) {
      this.projectId = String(writerConfig.projectId);
    }

    // Setup event listeners
    this.setupEventListeners();
    this.setupDropZone();

    console.log("[TablesPanel] Initialized with project:", this.projectId);
  }

  /**
   * Setup event listeners
   */
  private setupEventListeners(): void {
    // Search input (toolbar)
    const searchInput = document.getElementById(
      "tables-search-toolbar",
    ) as HTMLInputElement;
    if (searchInput) {
      searchInput.addEventListener("input", () => this.handleSearch());
    }

    // Sort select (toolbar)
    const sortSelect = document.getElementById(
      "tables-sort-toolbar",
    ) as HTMLSelectElement;
    if (sortSelect) {
      // Restore saved sorting preference
      const savedSort = statePersistence.getSavedTablesSorting?.() || "name";
      if (savedSort) {
        sortSelect.value = savedSort;
        console.log("[TablesPanel] Restored sorting preference:", savedSort);
      }

      sortSelect.addEventListener("change", () =>
        this.handleSort(sortSelect.value),
      );
    }

    console.log("[TablesPanel] Event listeners setup complete");
  }

  /**
   * Setup drop zone for file uploads
   */
  private setupDropZone(): void {
    const dropZone = document.getElementById("tables-drop-zone");
    const fileInput = document.getElementById("tables-file-input") as HTMLInputElement;

    if (!dropZone || !fileInput) {
      console.warn("[TablesPanel] Drop zone elements not found");
      return;
    }

    // Prevent defaults
    const preventDefaults = (e: Event) => {
      e.preventDefault();
      e.stopPropagation();
    };

    ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
      dropZone.addEventListener(eventName, preventDefaults, false);
    });

    // Drag enter
    dropZone.addEventListener("dragenter", (e: DragEvent) => {
      this.dragCounter++;
      if (e.dataTransfer) e.dataTransfer.dropEffect = "copy";
      dropZone.classList.add("drag-over");
    });

    // Drag leave
    dropZone.addEventListener("dragleave", () => {
      this.dragCounter--;
      if (this.dragCounter === 0) {
        dropZone.classList.remove("drag-over");
      }
    });

    // Drop
    dropZone.addEventListener("drop", (e: DragEvent) => {
      this.dragCounter = 0;
      dropZone.classList.remove("drag-over");
      const files = e.dataTransfer?.files;
      if (files && files.length > 0) {
        this.handleFileUpload(Array.from(files));
      }
    });

    // Click to browse
    dropZone.addEventListener("click", () => {
      fileInput.click();
    });

    // File input change
    fileInput.addEventListener("change", () => {
      if (fileInput.files && fileInput.files.length > 0) {
        this.handleFileUpload(Array.from(fileInput.files));
        fileInput.value = ""; // Reset input
      }
    });

    console.log("[TablesPanel] Drop zone setup complete");
  }

  /**
   * Handle file upload
   */
  private async handleFileUpload(files: File[]): Promise<void> {
    if (!this.projectId) {
      console.error("[TablesPanel] No project ID for upload");
      alert("Error: No project ID found");
      return;
    }

    // Validate file types
    const validExtensions = [".csv", ".xlsx", ".xls", ".tsv", ".ods"];
    const invalidFiles = files.filter((file) => {
      const ext = "." + file.name.split(".").pop()?.toLowerCase();
      return !validExtensions.includes(ext);
    });

    if (invalidFiles.length > 0) {
      alert(
        `Invalid file types: ${invalidFiles.map((f) => f.name).join(", ")}\nSupported: CSV, Excel, TSV, ODS`,
      );
      return;
    }

    // Upload files
    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const apiUrl = `/writer/api/project/${this.projectId}/upload-tables/`;
      console.log(`[TablesPanel] Uploading ${files.length} files to:`, apiUrl);

      const response = await fetch(apiUrl, {
        method: "POST",
        body: formData,
        headers: {
          "X-CSRFToken": getCsrfToken(),
        },
      });

      const data = await response.json();

      if (data.success) {
        console.log("[TablesPanel] Upload successful:", data);
        alert(`Successfully uploaded ${files.length} table(s)`);
        // Reload tables to show new uploads
        this.isLoaded = false;
        await this.loadTables();
      } else {
        console.error("[TablesPanel] Upload failed:", data);
        alert(`Upload failed: ${data.error || "Unknown error"}`);
      }
    } catch (error) {
      console.error("[TablesPanel] Upload error:", error);
      alert("Upload failed due to network error");
    }
  }

  /**
   * Load tables from API
   */
  async loadTables(): Promise<void> {
    if (this.isLoaded) {
      console.log("[TablesPanel] Already loaded, skipping");
      return;
    }

    if (!this.projectId) {
      console.error("[TablesPanel] No project ID available");
      this.showEmptyState();
      return;
    }

    this.showLoading();

    try {
      const apiUrl = `/writer/api/project/${this.projectId}/tables/`;
      console.log("[TablesPanel] Fetching from:", apiUrl);

      const response = await fetch(apiUrl);
      const data = await response.json();

      if (data.success && data.tables) {
        this.tables = data.tables;
        this.filteredTables = [...this.tables];
        this.isLoaded = true;

        console.log(`[TablesPanel] Loaded ${this.tables.length} tables`);

        // Apply saved sort or default to name
        const savedSort = statePersistence.getSavedTablesSorting?.() || "name";
        this.handleSort(savedSort);
      } else {
        console.warn("[TablesPanel] No tables found");
        this.showEmptyState();
      }
    } catch (error) {
      console.error("[TablesPanel] Error loading tables:", error);
      this.showEmptyState();
    }
  }

  /**
   * Render tables as cards
   */
  private renderTables(): void {
    const container = document.getElementById("tables-cards-container");
    if (!container) return;

    // Hide all empty states
    this.hideAllStates();

    // Update count display
    this.updateCountDisplay();

    if (this.filteredTables.length === 0) {
      const searchInput = document.getElementById(
        "tables-search-toolbar",
      ) as HTMLInputElement;
      if (searchInput && searchInput.value.trim()) {
        this.showNoResults();
      } else {
        this.showEmptyState();
      }
      return;
    }

    // Clear container
    container.innerHTML = "";

    // Render each table card
    this.filteredTables.forEach((table) => {
      const card = this.createTableCard(table);
      container.appendChild(card);
    });

    console.log(`[TablesPanel] Rendered ${this.filteredTables.length} tables`);
  }

  /**
   * Create a table card element
   */
  private createTableCard(table: Table): HTMLElement {
    const card = document.createElement("div");
    card.className = "table-card";
    const tableKey = table.label || table.file_name;
    card.dataset.label = tableKey;

    // Add "referenced" badge if table is used in paper
    if (table.is_referenced) {
      const badge = document.createElement("div");
      badge.className = "table-badge";
      badge.textContent = `In Paper (${table.reference_count || 0}×)`;
      card.appendChild(badge);
    }

    // Drag handle
    const dragHandle = document.createElement("div");
    dragHandle.className = "table-drag-handle";
    dragHandle.innerHTML = '<i class="fas fa-grip-vertical"></i>';

    // Thumbnail
    const thumbnail = document.createElement("div");
    thumbnail.className = "table-thumbnail";
    if (table.thumbnail_url) {
      const img = document.createElement("img");
      img.src = table.thumbnail_url;
      img.alt = tableKey;
      img.onerror = () => {
        // Fallback to icon if image fails to load
        thumbnail.innerHTML = '<i class="fas fa-image"></i>';
      };
      thumbnail.appendChild(img);
    } else {
      thumbnail.innerHTML = '<i class="fas fa-image"></i>';
    }

    // Content
    const content = document.createElement("div");
    content.className = "table-content";

    // Label (use filename without extension)
    const label = document.createElement("div");
    label.className = "table-label";
    const displayName = table.label || table.file_name.replace(/\.[^/.]+$/, "");
    label.textContent = displayName;

    // Caption (use source/location info)
    const caption = document.createElement("div");
    caption.className = "table-caption";
    caption.textContent = table.caption || table.location || "No location info";

    // Metadata
    const metadata = document.createElement("div");
    metadata.className = "table-metadata";

    const fileName = document.createElement("span");
    fileName.className = "table-file-name";
    fileName.textContent = table.file_name;
    metadata.appendChild(fileName);

    if (table.file_size) {
      const dot1 = document.createElement("span");
      dot1.className = "meta-dot";
      dot1.textContent = "•";
      metadata.appendChild(dot1);

      const fileSize = document.createElement("span");
      fileSize.className = "table-file-size";
      // Format bytes to KB
      const sizeKB = Math.round(table.file_size / 1024);
      fileSize.textContent = `${sizeKB} KB`;
      metadata.appendChild(fileSize);
    }

    if (table.file_type) {
      const dot2 = document.createElement("span");
      dot2.className = "meta-dot";
      dot2.textContent = "•";
      metadata.appendChild(dot2);

      const fileType = document.createElement("span");
      fileType.className = "table-file-type";
      fileType.textContent = table.file_type.toUpperCase();
      metadata.appendChild(fileType);
    }

    content.appendChild(label);
    content.appendChild(caption);
    content.appendChild(metadata);

    // Checkbox corner
    const checkboxCorner = document.createElement("div");
    checkboxCorner.className = "table-checkbox-corner";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "table-checkbox";
    checkbox.checked = this.selectedCards.has(tableKey);
    checkbox.addEventListener("change", (e) => {
      e.stopPropagation();
      this.handleCheckboxChange(tableKey, checkbox.checked);
    });

    checkboxCorner.appendChild(checkbox);

    // Assemble card
    card.appendChild(dragHandle);
    card.appendChild(thumbnail);
    card.appendChild(content);
    card.appendChild(checkboxCorner);

    // Event listeners
    card.addEventListener("click", (e) => {
      if (!(e.target as HTMLElement).closest(".table-checkbox")) {
        this.handleCardClick(table);
      }
    });

    card.addEventListener("dblclick", () => {
      this.handleCardDoubleClick(card, table);
    });

    // Drag and drop
    card.draggable = true;
    card.addEventListener("dragstart", (e) => this.handleDragStart(e, table));
    card.addEventListener("dragend", (e) => this.handleDragEnd(e));

    return card;
  }

  /**
   * Handle search
   */
  private handleSearch(): void {
    const searchInput = document.getElementById(
      "tables-search-toolbar",
    ) as HTMLInputElement;
    if (!searchInput) return;

    const query = searchInput.value.toLowerCase().trim();

    if (!query) {
      this.filteredTables = [...this.tables];
    } else {
      this.filteredTables = this.tables.filter(
        (table) =>
          (table.label || table.file_name).toLowerCase().includes(query) ||
          table.file_name.toLowerCase().includes(query) ||
          table.caption?.toLowerCase().includes(query) ||
          table.location?.toLowerCase().includes(query),
      );
    }

    this.renderTables();
    console.log(`[TablesPanel] Search: "${query}" -> ${this.filteredTables.length} results`);
  }

  /**
   * Handle sort
   */
  private handleSort(sortBy: string): void {
    console.log("[TablesPanel] Sorting by:", sortBy);

    switch (sortBy) {
      case "name":
        this.filteredTables.sort((a, b) => {
          const aName = a.label || a.file_name;
          const bName = b.label || b.file_name;
          return aName.localeCompare(bName);
        });
        break;
      case "name-desc":
        this.filteredTables.sort((a, b) => {
          const aName = a.label || a.file_name;
          const bName = b.label || b.file_name;
          return bName.localeCompare(aName);
        });
        break;
      case "size":
        this.filteredTables.sort((a, b) => (b.file_size || 0) - (a.file_size || 0));
        break;
      case "size-desc":
        this.filteredTables.sort((a, b) => (a.file_size || 0) - (b.file_size || 0));
        break;
      case "recent":
        this.filteredTables.sort((a, b) => (b.last_modified || 0) - (a.last_modified || 0));
        break;
      default:
        this.filteredTables.sort((a, b) => {
          const aName = a.label || a.file_name;
          const bName = b.label || b.file_name;
          return aName.localeCompare(bName);
        });
    }

    // Save sorting preference (if available)
    if (typeof (statePersistence as any).saveTablesSorting === 'function') {
      (statePersistence as any).saveTablesSorting(sortBy);
    }

    this.renderTables();
  }

  /**
   * Handle checkbox change
   */
  private handleCheckboxChange(label: string, checked: boolean): void {
    if (checked) {
      this.selectedCards.add(label);
    } else {
      this.selectedCards.delete(label);
    }

    // Update selected card styling
    const card = document.querySelector(
      `.table-card[data-label="${label}"]`,
    ) as HTMLElement;
    if (card) {
      card.classList.toggle("selected", checked);
    }

    this.updateCountDisplay();
    console.log(`[TablesPanel] ${label} ${checked ? "selected" : "deselected"}`);
  }

  /**
   * Handle card click - Open table preview modal
   */
  private handleCardClick(table: Table): void {
    const tableKey = table.label || table.file_name;
    console.log("[TablesPanel] Card clicked:", tableKey);

    // Open preview modal if available
    const tablePreviewModal = (window as any).tablePreviewModal;
    if (tablePreviewModal && table.file_hash) {
      tablePreviewModal.openTable(table.file_hash, table.file_name);
    } else {
      console.warn("[TablesPanel] Table preview modal not available or no file hash");
    }
  }

  /**
   * Handle card double click
   */
  private handleCardDoubleClick(card: HTMLElement, table: Table): void {
    const tableKey = table.label || table.file_name;
    console.log("[TablesPanel] Card double-clicked:", tableKey);

    // Toggle expanded view
    let expandedView = card.querySelector(".table-expanded-view") as HTMLElement;

    if (expandedView) {
      expandedView.remove();
    } else {
      expandedView = this.createExpandedView(table);
      card.appendChild(expandedView);
    }
  }

  /**
   * Create expanded view for table
   */
  private createExpandedView(table: Table): HTMLElement {
    const expanded = document.createElement("div");
    expanded.className = "table-expanded-view";

    // Preview
    if (table.thumbnail_url) {
      const preview = document.createElement("div");
      preview.className = "table-expanded-preview";
      const img = document.createElement("img");
      img.src = table.thumbnail_url;
      img.alt = table.label || table.file_name;
      preview.appendChild(img);
      expanded.appendChild(preview);
    }

    // Details
    const details = document.createElement("div");
    details.className = "table-expanded-details";

    details.innerHTML = `
      <div><strong>File:</strong> ${table.file_name}</div>
      <div><strong>Path:</strong> ${table.file_path}</div>
      ${table.file_size ? `<div><strong>Size:</strong> ${table.file_size}</div>` : ""}
      ${table.dimensions ? `<div><strong>Dimensions:</strong> ${table.dimensions}</div>` : ""}
    `;

    expanded.appendChild(details);

    return expanded;
  }

  /**
   * Handle drag start
   */
  private handleDragStart(event: DragEvent, table: Table): void {
    if (!event.dataTransfer) return;

    const tableKey = table.label || table.file_name;
    const figLabel = `fig:${tableKey.replace(/\.[^/.]+$/, "").replace(/[^a-zA-Z0-9_-]/g, "_")}`;

    const latexCode = `\\begin{table}[h]
  \\centering
  \\includegraphics[width=0.8\\textwidth]{${table.file_path}}
  \\caption{${table.caption || "Caption here"}}
  \\label{${figLabel}}
\\end{table}`;

    event.dataTransfer.setData("text/plain", latexCode);
    event.dataTransfer.effectAllowed = "copy";

    const target = event.target as HTMLElement;
    target.classList.add("dragging");

    console.log("[TablesPanel] Drag started:", tableKey);
  }

  /**
   * Handle drag end
   */
  private handleDragEnd(event: DragEvent): void {
    const target = event.target as HTMLElement;
    target.classList.remove("dragging");
  }

  /**
   * Update count display
   */
  private updateCountDisplay(): void {
    const selectedCountEl = document.getElementById(
      "tables-selected-count-toolbar",
    );
    const totalCountEl = document.getElementById(
      "tables-total-for-selection-toolbar",
    );

    if (selectedCountEl) {
      selectedCountEl.textContent = String(this.selectedCards.size);
    }

    if (totalCountEl) {
      totalCountEl.textContent = String(this.filteredTables.length);
    }
  }

  /**
   * Show loading state
   */
  private showLoading(): void {
    this.hideAllStates();
    const loading = document.getElementById("tables-loading");
    if (loading) loading.style.display = "flex";
  }

  /**
   * Show empty state
   */
  private showEmptyState(): void {
    this.hideAllStates();
    const empty = document.getElementById("tables-empty");
    if (empty) empty.style.display = "flex";
  }

  /**
   * Show no results state
   */
  private showNoResults(): void {
    this.hideAllStates();
    const noResults = document.getElementById("tables-no-results");
    if (noResults) noResults.style.display = "flex";
  }

  /**
   * Hide all states
   */
  private hideAllStates(): void {
    const states = ["tables-loading", "tables-empty", "tables-no-results"];
    states.forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.style.display = "none";
    });
  }
}

// Initialize and expose globally
const tablesPanel = new TablesPanel();
(window as any).tablesPanel = tablesPanel;

console.log("[TablesPanel] Module initialized and exposed globally");
