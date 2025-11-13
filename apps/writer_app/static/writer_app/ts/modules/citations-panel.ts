/**
 * Citations Panel Module
 * Manages the draggable citations panel in Writer interface
 */

console.log("[DEBUG] citations-panel.ts loaded");

import { statePersistence } from "./state-persistence.js";

export interface Citation {
  key: string;
  title?: string;
  authors?: string[];
  year?: string;
  journal?: string;
  citation_count?: number;
  impact_factor?: number;
  abstract?: string;
  doi?: string;
  detail?: string;
  documentation?: string;
}

export class CitationsPanel {
  private citations: Citation[] = [];
  private filteredCitations: Citation[] = [];
  private isLoaded: boolean = false;
  private projectId: string | null = null;
  private selectedCards: Set<string> = new Set(); // Track selected citation keys

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

    console.log("[CitationsPanel] Initialized with project:", this.projectId);
  }

  /**
   * Setup event listeners
   */
  private setupEventListeners(): void {
    // Search input (toolbar)
    const searchInput = document.getElementById(
      "citations-search-toolbar",
    ) as HTMLInputElement;
    if (searchInput) {
      searchInput.addEventListener("input", () => this.handleSearch());
    }

    // Sort select (toolbar)
    const sortSelect = document.getElementById(
      "citations-sort-toolbar",
    ) as HTMLSelectElement;
    if (sortSelect) {
      // Restore saved sorting preference
      const savedSort = statePersistence.getSavedCitationsSorting();
      if (savedSort) {
        sortSelect.value = savedSort;
        console.log("[CitationsPanel] Restored sorting preference:", savedSort);
      }

      sortSelect.addEventListener("change", () =>
        this.handleSort(sortSelect.value),
      );
    }

    console.log("[CitationsPanel] Event listeners setup complete");
  }

  /**
   * Load citations from API
   */
  async loadCitations(): Promise<void> {
    if (this.isLoaded) {
      console.log("[CitationsPanel] Already loaded, skipping");
      return;
    }

    if (!this.projectId) {
      console.error("[CitationsPanel] No project ID available");
      this.showEmptyState();
      return;
    }

    this.showLoading();

    try {
      const apiUrl = `/writer/api/project/${this.projectId}/citations/`;
      console.log("[CitationsPanel] Fetching from:", apiUrl);

      const response = await fetch(apiUrl);
      const data = await response.json();

      if (data.success && data.citations) {
        this.citations = data.citations;
        this.filteredCitations = [...this.citations];
        this.isLoaded = true;

        console.log(
          `[CitationsPanel] Loaded ${this.citations.length} citations`,
        );

        // Apply saved sort or default to citation count
        const savedSort = statePersistence.getSavedCitationsSorting();
        this.handleSort(savedSort || "citation-count");
      } else {
        console.warn("[CitationsPanel] No citations found");
        this.showEmptyState();
      }
    } catch (error) {
      console.error("[CitationsPanel] Error loading citations:", error);
      this.showEmptyState();
    }
  }

  /**
   * Render citations as cards
   */
  private renderCitations(): void {
    const container = document.getElementById("citations-cards-container");
    if (!container) return;

    // Hide all empty states
    this.hideAllStates();

    // Update count display
    this.updateCountDisplay();

    if (this.filteredCitations.length === 0) {
      const searchInput = document.getElementById(
        "citations-search-toolbar",
      ) as HTMLInputElement;
      if (searchInput && searchInput.value.trim()) {
        this.showNoResults();
      } else {
        this.showEmptyState();
      }
      return;
    }

    // Render cards
    container.innerHTML = this.filteredCitations
      .map((citation) => this.createCardHTML(citation))
      .join("");

    // Attach drag event listeners
    this.attachDragListeners();

    console.log(
      `[CitationsPanel] Rendered ${this.filteredCitations.length} citation cards`,
    );
  }

  /**
   * Create HTML for a single citation card
   */
  private createCardHTML(citation: Citation): string {
    const authors = Array.isArray(citation.authors)
      ? citation.authors.slice(0, 3).join(", ") +
        (citation.authors.length > 3 ? " et al." : "")
      : "Unknown authors";

    const citationCount = citation.citation_count || 0;
    const citationClass = citationCount > 100 ? "high-citations" : "";
    const isSelected = this.selectedCards.has(citation.key);

    return `
<div class="citation-card ${isSelected ? "selected" : ""}"
     draggable="true"
     data-citation-key="${citation.key}"
     data-citation-title="${this.escapeHtml(citation.title || "")}"
     data-expanded="false">
  <!-- Drag Handle Icon -->
  <div class="citation-drag-handle" title="Drag to insert">
    <i class="fas fa-grip-vertical"></i>
  </div>

  <!-- Upper Right Corner: Metrics & Checkbox -->
  <div class="citation-metrics-corner">
    ${citationCount > 0 ? `<span class="citation-count-badge ${citationClass}">${citationCount} cited</span>` : ""}
    ${citation.impact_factor ? `<span class="impact-factor-badge">IF ${citation.impact_factor}</span>` : ""}
    <input type="checkbox"
           class="citation-checkbox"
           data-citation-key="${citation.key}"
           ${isSelected ? "checked" : ""}
           title="Select for bulk insert">
  </div>

  <!-- Compact View (Always Visible) -->
  <div class="citation-compact-view">
    <!-- Line 1: Key | Authors | Journal • Year -->
    <div class="citation-meta-line">
      <span class="citation-key">${this.escapeHtml(citation.key)}</span>
      <span class="citation-authors-inline">${this.escapeHtml(authors)}</span>
      ${citation.journal ? `<span class="meta-dot">•</span>` : ""}
      ${citation.journal ? `<span class="citation-journal-inline">${this.escapeHtml(citation.journal)}</span>` : ""}
      ${citation.year ? `<span class="meta-dot">•</span><span class="citation-year">${citation.year}</span>` : ""}
    </div>
    <!-- Line 2: Title -->
    <div class="citation-title-line">${this.escapeHtml(citation.title || "Untitled")}</div>
  </div>

  <!-- Expanded View (Hidden by default, shown on double-click) -->
  <div class="citation-expanded-view" style="display: none;">
    ${citation.abstract ? `<div class="citation-abstract"><strong>Abstract:</strong> ${this.escapeHtml(citation.abstract)}</div>` : ""}
    ${citation.doi ? `<div class="citation-doi"><strong>DOI:</strong> <a href="https://doi.org/${this.escapeHtml(citation.doi)}" target="_blank">${this.escapeHtml(citation.doi)}</a></div>` : ""}
    ${citation.url ? `<div class="citation-url"><strong>URL:</strong> <a href="${this.escapeHtml(citation.url)}" target="_blank">${this.escapeHtml(citation.url)}</a></div>` : ""}
    ${citation.publisher ? `<div class="citation-publisher"><strong>Publisher:</strong> ${this.escapeHtml(citation.publisher)}</div>` : ""}
  </div>
</div>`;
  }

  /**
   * Attach drag and click event listeners to cards
   */
  private attachDragListeners(): void {
    const cards = document.querySelectorAll(".citation-card");

    cards.forEach((card) => {
      card.addEventListener("dragstart", (e) =>
        this.handleDragStart(e as DragEvent),
      );
      card.addEventListener("dragend", (e) =>
        this.handleDragEnd(e as DragEvent),
      );
      card.addEventListener("click", (e) =>
        this.handleCardClick(e as MouseEvent),
      );
      card.addEventListener("dblclick", (e) =>
        this.handleCardDoubleClick(e as MouseEvent),
      );
    });

    // Attach checkbox listeners
    const checkboxes = document.querySelectorAll(".citation-checkbox");
    checkboxes.forEach((checkbox) => {
      checkbox.addEventListener("change", (e) =>
        this.handleCheckboxChange(e as Event),
      );
    });

    console.log(
      `[CitationsPanel] Attached drag and click listeners to ${cards.length} cards`,
    );
  }

  /**
   * Handle checkbox change
   */
  private handleCheckboxChange(e: Event): void {
    e.stopPropagation();
    const checkbox = e.target as HTMLInputElement;
    const citationKey = checkbox.dataset.citationKey;

    if (!citationKey) return;

    const card = checkbox.closest(".citation-card") as HTMLElement;

    if (checkbox.checked) {
      this.selectedCards.add(citationKey);
      if (card) card.classList.add("selected");
    } else {
      this.selectedCards.delete(citationKey);
      if (card) card.classList.remove("selected");
    }

    console.log(
      "[CitationsPanel] Selected cards:",
      Array.from(this.selectedCards),
    );
    this.updateSelectionUI();
  }

  /**
   * Handle card click to toggle selection
   */
  private handleCardClick(e: MouseEvent): void {
    const target = e.target as HTMLElement;

    // Don't handle clicks on checkbox itself (it has its own handler)
    if (target.classList.contains("citation-checkbox")) {
      return;
    }

    // Don't handle clicks on drag handle
    if (
      target.classList.contains("citation-drag-handle") ||
      target.closest(".citation-drag-handle")
    ) {
      return;
    }

    const card = e.currentTarget as HTMLElement;
    const citationKey = card.dataset.citationKey;

    if (!citationKey) return;

    e.preventDefault();

    const checkbox = card.querySelector(
      ".citation-checkbox",
    ) as HTMLInputElement;

    // Toggle selection
    if (this.selectedCards.has(citationKey)) {
      this.selectedCards.delete(citationKey);
      card.classList.remove("selected");
      if (checkbox) checkbox.checked = false;
    } else {
      this.selectedCards.add(citationKey);
      card.classList.add("selected");
      if (checkbox) checkbox.checked = true;
    }

    console.log(
      "[CitationsPanel] Selected cards:",
      Array.from(this.selectedCards),
    );
    this.updateSelectionUI();
  }

  /**
   * Handle card double-click to toggle expand/collapse
   */
  private handleCardDoubleClick(e: MouseEvent): void {
    const target = e.target as HTMLElement;

    // Don't expand on checkbox or drag handle double-click
    if (
      target.classList.contains("citation-checkbox") ||
      target.classList.contains("citation-drag-handle") ||
      target.closest(".citation-drag-handle") ||
      target.closest(".citation-metrics-corner")
    ) {
      return;
    }

    const card = e.currentTarget as HTMLElement;
    const expandedView = card.querySelector(
      ".citation-expanded-view",
    ) as HTMLElement;

    if (!expandedView) return;

    e.preventDefault();
    e.stopPropagation();

    // Toggle expanded state
    const isExpanded = card.dataset.expanded === "true";

    if (isExpanded) {
      expandedView.style.display = "none";
      card.dataset.expanded = "false";
      console.log("[CitationsPanel] Collapsed citation card");
    } else {
      expandedView.style.display = "block";
      card.dataset.expanded = "true";
      console.log("[CitationsPanel] Expanded citation card");
    }
  }

  /**
   * Handle drag start
   */
  private handleDragStart(e: DragEvent): void {
    const card = e.target as HTMLElement;
    const citationKey = card.dataset.citationKey;

    if (!citationKey || !e.dataTransfer) return;

    // If card is part of multi-selection, drag all selected cards
    if (this.selectedCards.size > 0 && this.selectedCards.has(citationKey)) {
      // Drag multiple citations
      const keys = Array.from(this.selectedCards).join(",");
      e.dataTransfer.setData("text/plain", keys);
      console.log("[CitationsPanel] Drag started (multi):", keys);
    } else {
      // Drag single citation
      e.dataTransfer.setData("text/plain", citationKey);
      console.log("[CitationsPanel] Drag started (single):", citationKey);
    }

    e.dataTransfer.effectAllowed = "copy";

    // Add visual feedback
    card.classList.add("dragging");
  }

  /**
   * Handle drag end
   */
  private handleDragEnd(e: DragEvent): void {
    const card = e.target as HTMLElement;
    card.classList.remove("dragging");
  }

  /**
   * Handle search with fuzzy matching
   */
  private handleSearch(): void {
    const searchInput = document.getElementById(
      "citations-search-toolbar",
    ) as HTMLInputElement;

    if (!searchInput) return;

    const query = searchInput.value.trim().toLowerCase();

    if (!query) {
      this.filteredCitations = [...this.citations];
    } else {
      // Fuzzy matching: Split query into terms, match all terms in any order
      const searchTerms = query.split(/\s+/).filter((t) => t.length > 0);

      this.filteredCitations = this.citations
        .filter((cite) => {
          // Build searchable text from all fields
          const searchableText = [
            cite.key,
            cite.title || "",
            cite.journal || "",
            cite.year || "",
            ...(cite.authors || []),
            cite.abstract || "",
          ]
            .join(" ")
            .toLowerCase();

          // Check if ALL search terms appear in searchable text (fuzzy)
          return searchTerms.every((term) => searchableText.includes(term));
        })
        .map((cite) => {
          // Calculate relevance score for sorting
          const score = this.calculateRelevanceScore(cite, searchTerms);
          return { citation: cite, score };
        })
        .sort((a, b) => b.score - a.score) // Sort by relevance
        .map((item) => item.citation);
    }

    this.renderCitations();
  }

  /**
   * Calculate relevance score for fuzzy search results
   */
  private calculateRelevanceScore(
    citation: Citation,
    searchTerms: string[],
  ): number {
    let score = 0;

    searchTerms.forEach((term) => {
      // Key match (highest priority)
      if (citation.key.toLowerCase().includes(term)) {
        score += 10;
        // Bonus for exact match or word boundary
        if (
          citation.key.toLowerCase() === term ||
          citation.key.toLowerCase().startsWith(term)
        ) {
          score += 5;
        }
      }

      // Title match
      if (citation.title && citation.title.toLowerCase().includes(term)) {
        score += 5;
        // Bonus for word boundary match
        if (
          citation.title
            .toLowerCase()
            .split(/\s+/)
            .some((word) => word.startsWith(term))
        ) {
          score += 2;
        }
      }

      // Authors match
      if (
        citation.authors &&
        citation.authors.some((author) => author.toLowerCase().includes(term))
      ) {
        score += 4;
      }

      // Journal match
      if (citation.journal && citation.journal.toLowerCase().includes(term)) {
        score += 3;
      }

      // Year exact match
      if (citation.year && citation.year === term) {
        score += 6;
      }

      // Abstract match (lower priority)
      if (citation.abstract && citation.abstract.toLowerCase().includes(term)) {
        score += 1;
      }
    });

    return score;
  }

  /**
   * Handle sorting
   */
  private handleSort(sortBy: string): void {
    console.log("[CitationsPanel] Sorting by:", sortBy);

    // Save sorting preference
    statePersistence.saveCitationsSorting(sortBy);

    switch (sortBy) {
      case "citation-count":
        this.filteredCitations.sort(
          (a, b) => (b.citation_count || 0) - (a.citation_count || 0),
        );
        break;
      case "year-desc":
        this.filteredCitations.sort((a, b) =>
          (b.year || "0").localeCompare(a.year || "0"),
        );
        break;
      case "year-asc":
        this.filteredCitations.sort((a, b) =>
          (a.year || "0").localeCompare(b.year || "0"),
        );
        break;
      case "alpha":
        this.filteredCitations.sort((a, b) => a.key.localeCompare(b.key));
        break;
    }

    this.renderCitations();
  }

  /**
   * Update count display (toolbar selection total)
   */
  private updateCountDisplay(): void {
    // Update toolbar total for selection (XX/YY format)
    const totalForSelectionEl = document.getElementById(
      "citations-total-for-selection-toolbar",
    );

    if (totalForSelectionEl) {
      totalForSelectionEl.textContent = String(this.filteredCitations.length);
    }
  }

  /**
   * Show/hide states
   */
  private showLoading(): void {
    this.hideAllStates();
    const loading = document.getElementById("citations-loading");
    if (loading) loading.style.display = "flex";
  }

  private showEmptyState(): void {
    this.hideAllStates();
    const empty = document.getElementById("citations-empty");
    if (empty) empty.style.display = "flex";
  }

  private showNoResults(): void {
    this.hideAllStates();
    const noResults = document.getElementById("citations-no-results");
    if (noResults) noResults.style.display = "flex";
  }

  private hideAllStates(): void {
    ["citations-loading", "citations-empty", "citations-no-results"].forEach(
      (id) => {
        const el = document.getElementById(id);
        if (el) el.style.display = "none";
      },
    );
  }

  /**
   * Update selection UI (show count in toolbar - always visible)
   */
  private updateSelectionUI(): void {
    const count = this.selectedCards.size;

    // Update toolbar selected count (XX/YY Selected format - always visible)
    const selectedCountEl = document.getElementById(
      "citations-selected-count-toolbar",
    );
    const totalForSelectionEl = document.getElementById(
      "citations-total-for-selection-toolbar",
    );

    if (selectedCountEl && totalForSelectionEl) {
      selectedCountEl.textContent = String(count);
      totalForSelectionEl.textContent = String(this.filteredCitations.length);
    }
  }

  /**
   * Clear all selections
   */
  public clearSelection(): void {
    this.selectedCards.clear();
    document.querySelectorAll(".citation-card.selected").forEach((card) => {
      card.classList.remove("selected");
      const checkbox = card.querySelector(
        ".citation-checkbox",
      ) as HTMLInputElement;
      if (checkbox) checkbox.checked = false;
    });
    this.updateSelectionUI();
    console.log("[CitationsPanel] Selection cleared");
  }

  /**
   * Escape HTML
   */
  private escapeHtml(text: string): string {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
}
