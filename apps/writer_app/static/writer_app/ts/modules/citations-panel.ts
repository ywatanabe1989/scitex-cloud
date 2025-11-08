/**
 * Citations Panel Module
 * Manages the draggable citations panel in Writer interface
 */

console.log("[DEBUG] citations-panel.ts loaded");

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

        console.log('[CitationsPanel] Initialized with project:', this.projectId);
    }

    /**
     * Setup event listeners
     */
    private setupEventListeners(): void {
        // Search input
        const searchInput = document.getElementById('citations-search-input') as HTMLInputElement;
        if (searchInput) {
            searchInput.addEventListener('input', () => this.handleSearch());
        }

        // Clear search button
        const clearBtn = document.getElementById('clear-citations-search');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                if (searchInput) {
                    searchInput.value = '';
                    this.handleSearch();
                }
            });
        }

        // Sort select
        const sortSelect = document.getElementById('citations-sort-select') as HTMLSelectElement;
        if (sortSelect) {
            sortSelect.addEventListener('change', () => this.handleSort(sortSelect.value));
        }

        console.log('[CitationsPanel] Event listeners setup complete');
    }

    /**
     * Load citations from API
     */
    async loadCitations(): Promise<void> {
        if (this.isLoaded) {
            console.log('[CitationsPanel] Already loaded, skipping');
            return;
        }

        if (!this.projectId) {
            console.error('[CitationsPanel] No project ID available');
            this.showEmptyState();
            return;
        }

        this.showLoading();

        try {
            const apiUrl = `/writer/api/project/${this.projectId}/citations/`;
            console.log('[CitationsPanel] Fetching from:', apiUrl);

            const response = await fetch(apiUrl);
            const data = await response.json();

            if (data.success && data.citations) {
                this.citations = data.citations;
                this.filteredCitations = [...this.citations];
                this.isLoaded = true;

                console.log(`[CitationsPanel] Loaded ${this.citations.length} citations`);

                // Apply default sort (citation count)
                this.handleSort('citation-count');
            } else {
                console.warn('[CitationsPanel] No citations found');
                this.showEmptyState();
            }
        } catch (error) {
            console.error('[CitationsPanel] Error loading citations:', error);
            this.showEmptyState();
        }
    }

    /**
     * Render citations as cards
     */
    private renderCitations(): void {
        const container = document.getElementById('citations-cards-container');
        if (!container) return;

        // Hide all empty states
        this.hideAllStates();

        // Update count display
        this.updateCountDisplay();

        if (this.filteredCitations.length === 0) {
            const searchInput = document.getElementById('citations-search-input') as HTMLInputElement;
            if (searchInput && searchInput.value.trim()) {
                this.showNoResults();
            } else {
                this.showEmptyState();
            }
            return;
        }

        // Render cards
        container.innerHTML = this.filteredCitations.map(citation => this.createCardHTML(citation)).join('');

        // Attach drag event listeners
        this.attachDragListeners();

        console.log(`[CitationsPanel] Rendered ${this.filteredCitations.length} citation cards`);
    }

    /**
     * Create HTML for a single citation card
     */
    private createCardHTML(citation: Citation): string {
        const authors = Array.isArray(citation.authors) ?
            citation.authors.slice(0, 3).join(', ') + (citation.authors.length > 3 ? ' et al.' : '') :
            'Unknown authors';

        const citationCount = citation.citation_count || 0;
        const citationClass = citationCount > 100 ? 'high-citations' : '';
        const isSelected = this.selectedCards.has(citation.key);

        return `
<div class="citation-card ${isSelected ? 'selected' : ''}"
     draggable="true"
     data-citation-key="${citation.key}"
     data-citation-title="${this.escapeHtml(citation.title || '')}">
  <!-- Selection Checkbox -->
  <input type="checkbox"
         class="citation-checkbox"
         data-citation-key="${citation.key}"
         ${isSelected ? 'checked' : ''}
         title="Select for bulk insert">

  <div class="citation-card-header">
    <span class="citation-key">${this.escapeHtml(citation.key)}</span>
    <div class="citation-metrics">
      ${citation.year ? `<span class="citation-metric"><i class="fas fa-calendar"></i>${citation.year}</span>` : ''}
      ${citationCount > 0 ? `<span class="citation-metric ${citationClass}"><i class="fas fa-quote-right"></i>${citationCount}</span>` : ''}
    </div>
  </div>
  <div class="citation-title">${this.escapeHtml(citation.title || 'Untitled')}</div>
  <div class="citation-authors">${this.escapeHtml(authors)}</div>
  ${citation.journal ? `
    <div class="citation-journal">
      <i class="fas fa-book-open"></i>
      ${this.escapeHtml(citation.journal)}
      ${citation.impact_factor ? `<span class="impact-factor">IF ${citation.impact_factor}</span>` : ''}
    </div>
  ` : ''}
</div>`;
    }

    /**
     * Attach drag and click event listeners to cards
     */
    private attachDragListeners(): void {
        const cards = document.querySelectorAll('.citation-card');

        cards.forEach(card => {
            card.addEventListener('dragstart', (e) => this.handleDragStart(e as DragEvent));
            card.addEventListener('dragend', (e) => this.handleDragEnd(e as DragEvent));
            card.addEventListener('click', (e) => this.handleCardClick(e as MouseEvent));
        });

        // Attach checkbox listeners
        const checkboxes = document.querySelectorAll('.citation-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (e) => this.handleCheckboxChange(e as Event));
        });

        console.log(`[CitationsPanel] Attached drag and click listeners to ${cards.length} cards`);
    }

    /**
     * Handle checkbox change
     */
    private handleCheckboxChange(e: Event): void {
        e.stopPropagation();
        const checkbox = e.target as HTMLInputElement;
        const citationKey = checkbox.dataset.citationKey;

        if (!citationKey) return;

        const card = checkbox.closest('.citation-card') as HTMLElement;

        if (checkbox.checked) {
            this.selectedCards.add(citationKey);
            if (card) card.classList.add('selected');
        } else {
            this.selectedCards.delete(citationKey);
            if (card) card.classList.remove('selected');
        }

        console.log('[CitationsPanel] Selected cards:', Array.from(this.selectedCards));
        this.updateSelectionUI();
    }

    /**
     * Handle card click for multi-select (Ctrl/Cmd + Click)
     */
    private handleCardClick(e: MouseEvent): void {
        const target = e.target as HTMLElement;

        // Don't handle clicks on checkbox itself
        if (target.classList.contains('citation-checkbox')) {
            return;
        }

        const card = e.currentTarget as HTMLElement;
        const citationKey = card.dataset.citationKey;

        if (!citationKey) return;

        // Handle multi-select if Ctrl (Windows/Linux) or Cmd (Mac) is pressed
        if (e.ctrlKey || e.metaKey) {
            e.preventDefault();

            const checkbox = card.querySelector('.citation-checkbox') as HTMLInputElement;

            // Toggle selection
            if (this.selectedCards.has(citationKey)) {
                this.selectedCards.delete(citationKey);
                card.classList.remove('selected');
                if (checkbox) checkbox.checked = false;
            } else {
                this.selectedCards.add(citationKey);
                card.classList.add('selected');
                if (checkbox) checkbox.checked = true;
            }

            console.log('[CitationsPanel] Selected cards:', Array.from(this.selectedCards));
            this.updateSelectionUI();
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
            const keys = Array.from(this.selectedCards).join(',');
            e.dataTransfer.setData('text/plain', keys);
            console.log('[CitationsPanel] Drag started (multi):', keys);
        } else {
            // Drag single citation
            e.dataTransfer.setData('text/plain', citationKey);
            console.log('[CitationsPanel] Drag started (single):', citationKey);
        }

        e.dataTransfer.effectAllowed = 'copy';

        // Add visual feedback
        card.classList.add('dragging');
    }

    /**
     * Handle drag end
     */
    private handleDragEnd(e: DragEvent): void {
        const card = e.target as HTMLElement;
        card.classList.remove('dragging');
    }

    /**
     * Handle search with fuzzy matching
     */
    private handleSearch(): void {
        const searchInput = document.getElementById('citations-search-input') as HTMLInputElement;
        const clearBtn = document.getElementById('clear-citations-search');

        if (!searchInput) return;

        const query = searchInput.value.trim().toLowerCase();

        // Show/hide clear button
        if (clearBtn) {
            clearBtn.style.display = query ? 'block' : 'none';
        }

        if (!query) {
            this.filteredCitations = [...this.citations];
        } else {
            // Fuzzy matching: Split query into terms, match all terms in any order
            const searchTerms = query.split(/\s+/).filter(t => t.length > 0);

            this.filteredCitations = this.citations.filter(cite => {
                // Build searchable text from all fields
                const searchableText = [
                    cite.key,
                    cite.title || '',
                    cite.journal || '',
                    cite.year || '',
                    ...(cite.authors || []),
                    cite.abstract || ''
                ].join(' ').toLowerCase();

                // Check if ALL search terms appear in searchable text (fuzzy)
                return searchTerms.every(term => searchableText.includes(term));
            }).map(cite => {
                // Calculate relevance score for sorting
                const score = this.calculateRelevanceScore(cite, searchTerms);
                return { citation: cite, score };
            }).sort((a, b) => b.score - a.score)  // Sort by relevance
              .map(item => item.citation);
        }

        this.renderCitations();
    }

    /**
     * Calculate relevance score for fuzzy search results
     */
    private calculateRelevanceScore(citation: Citation, searchTerms: string[]): number {
        let score = 0;

        searchTerms.forEach(term => {
            // Key match (highest priority)
            if (citation.key.toLowerCase().includes(term)) {
                score += 10;
                // Bonus for exact match or word boundary
                if (citation.key.toLowerCase() === term ||
                    citation.key.toLowerCase().startsWith(term)) {
                    score += 5;
                }
            }

            // Title match
            if (citation.title && citation.title.toLowerCase().includes(term)) {
                score += 5;
                // Bonus for word boundary match
                if (citation.title.toLowerCase().split(/\s+/).some(word => word.startsWith(term))) {
                    score += 2;
                }
            }

            // Authors match
            if (citation.authors && citation.authors.some(author => author.toLowerCase().includes(term))) {
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
        console.log('[CitationsPanel] Sorting by:', sortBy);

        switch (sortBy) {
            case 'citation-count':
                this.filteredCitations.sort((a, b) => (b.citation_count || 0) - (a.citation_count || 0));
                break;
            case 'year-desc':
                this.filteredCitations.sort((a, b) => (b.year || '0').localeCompare(a.year || '0'));
                break;
            case 'year-asc':
                this.filteredCitations.sort((a, b) => (a.year || '0').localeCompare(b.year || '0'));
                break;
            case 'alpha':
                this.filteredCitations.sort((a, b) => a.key.localeCompare(b.key));
                break;
        }

        this.renderCitations();
    }

    /**
     * Update count display
     */
    private updateCountDisplay(): void {
        const totalEl = document.getElementById('citations-total');
        const filteredEl = document.getElementById('citations-filtered');
        const filteredCountEl = document.getElementById('citations-filtered-count');

        if (totalEl) {
            totalEl.textContent = String(this.citations.length);
        }

        if (filteredEl && filteredCountEl) {
            if (this.filteredCitations.length < this.citations.length) {
                filteredEl.style.display = 'inline';
                filteredCountEl.textContent = String(this.filteredCitations.length);
            } else {
                filteredEl.style.display = 'none';
            }
        }
    }

    /**
     * Show/hide states
     */
    private showLoading(): void {
        this.hideAllStates();
        const loading = document.getElementById('citations-loading');
        if (loading) loading.style.display = 'flex';
    }

    private showEmptyState(): void {
        this.hideAllStates();
        const empty = document.getElementById('citations-empty');
        if (empty) empty.style.display = 'flex';
    }

    private showNoResults(): void {
        this.hideAllStates();
        const noResults = document.getElementById('citations-no-results');
        if (noResults) noResults.style.display = 'flex';
    }

    private hideAllStates(): void {
        ['citations-loading', 'citations-empty', 'citations-no-results'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = 'none';
        });
    }

    /**
     * Update selection UI (show count, clear button, etc.)
     */
    private updateSelectionUI(): void {
        const count = this.selectedCards.size;

        // Update selection count badge
        let badge = document.getElementById('citations-selection-badge');
        if (count > 0) {
            if (!badge) {
                // Create badge if it doesn't exist
                const summary = document.querySelector('.citations-summary');
                if (summary) {
                    badge = document.createElement('div');
                    badge.id = 'citations-selection-badge';
                    badge.style.cssText = 'display: inline-flex; align-items: center; gap: 0.5rem; margin-left: 1rem; padding: 0.25rem 0.75rem; background: var(--color-accent-emphasis); color: white; border-radius: 4px; font-size: 0.85rem; font-weight: 600;';
                    summary.appendChild(badge);
                }
            }

            if (badge) {
                badge.innerHTML = `
                    <i class="fas fa-check-square"></i>
                    ${count} selected
                    <button onclick="citationsPanel.clearSelection()" style="background: none; border: none; color: white; cursor: pointer; padding: 0 0 0 0.5rem; font-size: 1rem;" title="Clear selection">
                        <i class="fas fa-times"></i>
                    </button>
                `;
                badge.style.display = 'inline-flex';
            }
        } else if (badge) {
            badge.style.display = 'none';
        }
    }

    /**
     * Clear all selections
     */
    public clearSelection(): void {
        this.selectedCards.clear();
        document.querySelectorAll('.citation-card.selected').forEach(card => {
            card.classList.remove('selected');
            const checkbox = card.querySelector('.citation-checkbox') as HTMLInputElement;
            if (checkbox) checkbox.checked = false;
        });
        this.updateSelectionUI();
        console.log('[CitationsPanel] Selection cleared');
    }

    /**
     * Escape HTML
     */
    private escapeHtml(text: string): string {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
