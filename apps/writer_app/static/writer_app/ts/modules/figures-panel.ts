/**
 * Figures Panel Module
 * Manages the draggable figures panel in Writer interface
 */

console.log("[DEBUG] figures-panel.ts loaded");

import { statePersistence } from "./state-persistence.js";
import { getCsrfToken } from "../shared/utils.js";

export interface Figure {
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

export class FiguresPanel {
  private figures: Figure[] = [];
  private filteredFigures: Figure[] = [];
  private isLoaded: boolean = false;
  private projectId: string | null = null;
  private selectedCards: Set<string> = new Set(); // Track selected figure labels

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

    console.log("[FiguresPanel] Initialized with project:", this.projectId);
  }

  /**
   * Setup event listeners
   */
  private setupEventListeners(): void {
    // Search input (toolbar)
    const searchInput = document.getElementById(
      "figures-search-toolbar",
    ) as HTMLInputElement;
    if (searchInput) {
      searchInput.addEventListener("input", () => this.handleSearch());
    }

    // Sort select (toolbar)
    const sortSelect = document.getElementById(
      "figures-sort-toolbar",
    ) as HTMLSelectElement;
    if (sortSelect) {
      // Restore saved sorting preference
      const savedSort = statePersistence.getSavedFiguresSorting?.() || "name";
      if (savedSort) {
        sortSelect.value = savedSort;
        console.log("[FiguresPanel] Restored sorting preference:", savedSort);
      }

      sortSelect.addEventListener("change", () =>
        this.handleSort(sortSelect.value),
      );
    }

    console.log("[FiguresPanel] Event listeners setup complete");
  }

  /**
   * Setup drop zone for file uploads
   */
  private setupDropZone(): void {
    const dropZone = document.getElementById("figures-drop-zone");
    const fileInput = document.getElementById("figures-file-input") as HTMLInputElement;

    if (!dropZone || !fileInput) {
      console.warn("[FiguresPanel] Drop zone elements not found");
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

    console.log("[FiguresPanel] Drop zone setup complete");
  }

  /**
   * Handle file upload
   */
  private async handleFileUpload(files: File[]): Promise<void> {
    if (!this.projectId) {
      console.error("[FiguresPanel] No project ID for upload");
      alert("Error: No project ID found");
      return;
    }

    // Validate file types
    const validExtensions = [".png", ".jpg", ".jpeg", ".pdf", ".svg"];
    const invalidFiles = files.filter((file) => {
      const ext = "." + file.name.split(".").pop()?.toLowerCase();
      return !validExtensions.includes(ext);
    });

    if (invalidFiles.length > 0) {
      alert(
        `Invalid file types: ${invalidFiles.map((f) => f.name).join(", ")}\nSupported: PNG, JPG, PDF, SVG`,
      );
      return;
    }

    // Upload files
    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const apiUrl = `/writer/api/project/${this.projectId}/upload-figures/`;
      console.log(`[FiguresPanel] Uploading ${files.length} files to:`, apiUrl);

      const response = await fetch(apiUrl, {
        method: "POST",
        body: formData,
        headers: {
          "X-CSRFToken": getCsrfToken(),
        },
      });

      const data = await response.json();

      if (data.success) {
        console.log("[FiguresPanel] Upload successful:", data);
        alert(`Successfully uploaded ${files.length} figure(s)`);
        // Reload figures to show new uploads
        this.isLoaded = false;
        await this.loadFigures();
      } else {
        console.error("[FiguresPanel] Upload failed:", data);
        alert(`Upload failed: ${data.error || "Unknown error"}`);
      }
    } catch (error) {
      console.error("[FiguresPanel] Upload error:", error);
      alert("Upload failed due to network error");
    }
  }

  /**
   * Load figures from API
   */
  async loadFigures(): Promise<void> {
    if (this.isLoaded) {
      console.log("[FiguresPanel] Already loaded, skipping");
      return;
    }

    if (!this.projectId) {
      console.error("[FiguresPanel] No project ID available");
      this.showEmptyState();
      return;
    }

    this.showLoading();

    try {
      const apiUrl = `/writer/api/project/${this.projectId}/figures/`;
      console.log("[FiguresPanel] Fetching from:", apiUrl);

      const response = await fetch(apiUrl);
      const data = await response.json();

      if (data.success && data.figures) {
        this.figures = data.figures;
        this.filteredFigures = [...this.figures];
        this.isLoaded = true;

        console.log(`[FiguresPanel] Loaded ${this.figures.length} figures`);

        // Apply saved sort or default to name
        const savedSort = statePersistence.getSavedFiguresSorting?.() || "name";
        this.handleSort(savedSort);
      } else {
        console.warn("[FiguresPanel] No figures found");
        this.showEmptyState();
      }
    } catch (error) {
      console.error("[FiguresPanel] Error loading figures:", error);
      this.showEmptyState();
    }
  }

  /**
   * Render figures as cards
   */
  private renderFigures(): void {
    const container = document.getElementById("figures-cards-container");
    if (!container) return;

    // Hide all empty states
    this.hideAllStates();

    // Update count display
    this.updateCountDisplay();

    if (this.filteredFigures.length === 0) {
      const searchInput = document.getElementById(
        "figures-search-toolbar",
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

    // Render each figure card
    this.filteredFigures.forEach((figure) => {
      const card = this.createFigureCard(figure);
      container.appendChild(card);
    });

    console.log(`[FiguresPanel] Rendered ${this.filteredFigures.length} figures`);
  }

  /**
   * Create a figure card element
   */
  private createFigureCard(figure: Figure): HTMLElement {
    const card = document.createElement("div");
    card.className = "figure-card";
    const figureKey = figure.label || figure.file_name;
    card.dataset.label = figureKey;

    // Add "referenced" badge if figure is used in paper
    if (figure.is_referenced) {
      const badge = document.createElement("div");
      badge.className = "figure-badge";
      badge.textContent = `In Paper (${figure.reference_count || 0}×)`;
      card.appendChild(badge);
    }

    // Drag handle
    const dragHandle = document.createElement("div");
    dragHandle.className = "figure-drag-handle";
    dragHandle.innerHTML = '<i class="fas fa-grip-vertical"></i>';

    // Thumbnail
    const thumbnail = document.createElement("div");
    thumbnail.className = "figure-thumbnail";
    if (figure.thumbnail_url) {
      const img = document.createElement("img");
      img.src = figure.thumbnail_url;
      img.alt = figureKey;
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
    content.className = "figure-content";

    // Label (use filename without extension)
    const label = document.createElement("div");
    label.className = "figure-label";
    const displayName = figure.label || figure.file_name.replace(/\.[^/.]+$/, "");
    label.textContent = displayName;

    // Caption (use source/location info)
    const caption = document.createElement("div");
    caption.className = "figure-caption";
    caption.textContent = figure.caption || figure.location || "No location info";

    // Metadata
    const metadata = document.createElement("div");
    metadata.className = "figure-metadata";

    const fileName = document.createElement("span");
    fileName.className = "figure-file-name";
    fileName.textContent = figure.file_name;
    metadata.appendChild(fileName);

    if (figure.file_size) {
      const dot1 = document.createElement("span");
      dot1.className = "meta-dot";
      dot1.textContent = "•";
      metadata.appendChild(dot1);

      const fileSize = document.createElement("span");
      fileSize.className = "figure-file-size";
      // Format bytes to KB
      const sizeKB = Math.round(figure.file_size / 1024);
      fileSize.textContent = `${sizeKB} KB`;
      metadata.appendChild(fileSize);
    }

    if (figure.file_type) {
      const dot2 = document.createElement("span");
      dot2.className = "meta-dot";
      dot2.textContent = "•";
      metadata.appendChild(dot2);

      const fileType = document.createElement("span");
      fileType.className = "figure-file-type";
      fileType.textContent = figure.file_type.toUpperCase();
      metadata.appendChild(fileType);
    }

    content.appendChild(label);
    content.appendChild(caption);
    content.appendChild(metadata);

    // Checkbox corner
    const checkboxCorner = document.createElement("div");
    checkboxCorner.className = "figure-checkbox-corner";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "figure-checkbox";
    checkbox.checked = this.selectedCards.has(figureKey);
    checkbox.addEventListener("change", (e) => {
      e.stopPropagation();
      this.handleCheckboxChange(figureKey, checkbox.checked);
    });

    checkboxCorner.appendChild(checkbox);

    // Assemble card
    card.appendChild(dragHandle);
    card.appendChild(thumbnail);
    card.appendChild(content);
    card.appendChild(checkboxCorner);

    // Event listeners
    card.addEventListener("click", (e) => {
      if (!(e.target as HTMLElement).closest(".figure-checkbox")) {
        this.handleCardClick(figure);
      }
    });

    card.addEventListener("dblclick", () => {
      this.handleCardDoubleClick(card, figure);
    });

    // Drag and drop
    card.draggable = true;
    card.addEventListener("dragstart", (e) => this.handleDragStart(e, figure));
    card.addEventListener("dragend", (e) => this.handleDragEnd(e));

    return card;
  }

  /**
   * Handle search
   */
  private handleSearch(): void {
    const searchInput = document.getElementById(
      "figures-search-toolbar",
    ) as HTMLInputElement;
    if (!searchInput) return;

    const query = searchInput.value.toLowerCase().trim();

    if (!query) {
      this.filteredFigures = [...this.figures];
    } else {
      this.filteredFigures = this.figures.filter(
        (figure) =>
          (figure.label || figure.file_name).toLowerCase().includes(query) ||
          figure.file_name.toLowerCase().includes(query) ||
          figure.caption?.toLowerCase().includes(query) ||
          figure.location?.toLowerCase().includes(query),
      );
    }

    this.renderFigures();
    console.log(`[FiguresPanel] Search: "${query}" -> ${this.filteredFigures.length} results`);
  }

  /**
   * Handle sort
   */
  private handleSort(sortBy: string): void {
    console.log("[FiguresPanel] Sorting by:", sortBy);

    switch (sortBy) {
      case "name":
        this.filteredFigures.sort((a, b) => {
          const aName = a.label || a.file_name;
          const bName = b.label || b.file_name;
          return aName.localeCompare(bName);
        });
        break;
      case "name-desc":
        this.filteredFigures.sort((a, b) => {
          const aName = a.label || a.file_name;
          const bName = b.label || b.file_name;
          return bName.localeCompare(aName);
        });
        break;
      case "size":
        this.filteredFigures.sort((a, b) => (b.file_size || 0) - (a.file_size || 0));
        break;
      case "size-desc":
        this.filteredFigures.sort((a, b) => (a.file_size || 0) - (b.file_size || 0));
        break;
      case "recent":
        this.filteredFigures.sort((a, b) => (b.last_modified || 0) - (a.last_modified || 0));
        break;
      default:
        this.filteredFigures.sort((a, b) => {
          const aName = a.label || a.file_name;
          const bName = b.label || b.file_name;
          return aName.localeCompare(bName);
        });
    }

    // Save sorting preference (if available)
    if (typeof (statePersistence as any).saveFiguresSorting === 'function') {
      (statePersistence as any).saveFiguresSorting(sortBy);
    }

    this.renderFigures();
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
      `.figure-card[data-label="${label}"]`,
    ) as HTMLElement;
    if (card) {
      card.classList.toggle("selected", checked);
    }

    this.updateCountDisplay();
    console.log(`[FiguresPanel] ${label} ${checked ? "selected" : "deselected"}`);
  }

  /**
   * Handle card click
   */
  private handleCardClick(figure: Figure): void {
    const figureKey = figure.label || figure.file_name;
    console.log("[FiguresPanel] Card clicked:", figureKey);
    // Could implement preview modal here
  }

  /**
   * Handle card double click
   */
  private handleCardDoubleClick(card: HTMLElement, figure: Figure): void {
    const figureKey = figure.label || figure.file_name;
    console.log("[FiguresPanel] Card double-clicked:", figureKey);

    // Toggle expanded view
    let expandedView = card.querySelector(".figure-expanded-view") as HTMLElement;

    if (expandedView) {
      expandedView.remove();
    } else {
      expandedView = this.createExpandedView(figure);
      card.appendChild(expandedView);
    }
  }

  /**
   * Create expanded view for figure
   */
  private createExpandedView(figure: Figure): HTMLElement {
    const expanded = document.createElement("div");
    expanded.className = "figure-expanded-view";

    // Preview
    if (figure.thumbnail_url) {
      const preview = document.createElement("div");
      preview.className = "figure-expanded-preview";
      const img = document.createElement("img");
      img.src = figure.thumbnail_url;
      img.alt = figure.label || figure.file_name;
      preview.appendChild(img);
      expanded.appendChild(preview);
    }

    // Details
    const details = document.createElement("div");
    details.className = "figure-expanded-details";

    details.innerHTML = `
      <div><strong>File:</strong> ${figure.file_name}</div>
      <div><strong>Path:</strong> ${figure.file_path}</div>
      ${figure.file_size ? `<div><strong>Size:</strong> ${figure.file_size}</div>` : ""}
      ${figure.dimensions ? `<div><strong>Dimensions:</strong> ${figure.dimensions}</div>` : ""}
    `;

    expanded.appendChild(details);

    return expanded;
  }

  /**
   * Handle drag start
   */
  private handleDragStart(event: DragEvent, figure: Figure): void {
    if (!event.dataTransfer) return;

    const figureKey = figure.label || figure.file_name;
    const figLabel = `fig:${figureKey.replace(/\.[^/.]+$/, "").replace(/[^a-zA-Z0-9_-]/g, "_")}`;

    const latexCode = `\\begin{figure}[h]
  \\centering
  \\includegraphics[width=0.8\\textwidth]{${figure.file_path}}
  \\caption{${figure.caption || "Caption here"}}
  \\label{${figLabel}}
\\end{figure}`;

    event.dataTransfer.setData("text/plain", latexCode);
    event.dataTransfer.effectAllowed = "copy";

    const target = event.target as HTMLElement;
    target.classList.add("dragging");

    console.log("[FiguresPanel] Drag started:", figureKey);
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
      "figures-selected-count-toolbar",
    );
    const totalCountEl = document.getElementById(
      "figures-total-for-selection-toolbar",
    );

    if (selectedCountEl) {
      selectedCountEl.textContent = String(this.selectedCards.size);
    }

    if (totalCountEl) {
      totalCountEl.textContent = String(this.filteredFigures.length);
    }
  }

  /**
   * Show loading state
   */
  private showLoading(): void {
    this.hideAllStates();
    const loading = document.getElementById("figures-loading");
    if (loading) loading.style.display = "flex";
  }

  /**
   * Show empty state
   */
  private showEmptyState(): void {
    this.hideAllStates();
    const empty = document.getElementById("figures-empty");
    if (empty) empty.style.display = "flex";
  }

  /**
   * Show no results state
   */
  private showNoResults(): void {
    this.hideAllStates();
    const noResults = document.getElementById("figures-no-results");
    if (noResults) noResults.style.display = "flex";
  }

  /**
   * Hide all states
   */
  private hideAllStates(): void {
    const states = ["figures-loading", "figures-empty", "figures-no-results"];
    states.forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.style.display = "none";
    });
  }
}

// Initialize and expose globally
const figuresPanel = new FiguresPanel();
(window as any).figuresPanel = figuresPanel;

console.log("[FiguresPanel] Module initialized and exposed globally");
