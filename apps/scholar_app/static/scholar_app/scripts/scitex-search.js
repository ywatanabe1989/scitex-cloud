/**
 * SciTeX Scholar Search Module
 *
 * Handles integration with SciTeX search pipelines for academic paper search.
 * Provides progressive search with real-time engine status updates.
 *
 * @module scitex-search
 * @version 1.0.0
 * @author SciTeX Team
 */

(function() {
    'use strict';

    /**
     * SciTeX Search Configuration
     */
    const ScitexSearch = {
        // API Endpoints
        endpoints: {
            search: '/scholar/api/search/scitex/',
            searchSingle: '/scholar/api/search/scitex/single/',
            capabilities: '/scholar/api/search/scitex/capabilities/'
        },

        // Search state
        state: {
            isSearching: false,
            currentQuery: null,
            lastResults: null,
            engines: [],
            searchMode: 'parallel' // 'parallel' or 'single'
        },

        // Engine status indicators
        engineStatus: {
            'CrossRef': { name: 'CrossRef', icon: 'fas fa-database', color: '#3498db' },
            'PubMed': { name: 'PubMed', icon: 'fas fa-heartbeat', color: '#e74c3c' },
            'arXiv': { name: 'arXiv', icon: 'fas fa-file-alt', color: '#f39c12' },
            'Semantic_Scholar': { name: 'Semantic Scholar', icon: 'fas fa-brain', color: '#9b59b6' },
            'OpenAlex': { name: 'OpenAlex', icon: 'fas fa-book-open', color: '#1abc9c' }
        },

        /**
         * Initialize SciTeX search functionality
         */
        init: function() {
            console.log('[SciTeX Search] Initializing...');

            // Check if SciTeX is available
            this.checkAvailability().then(available => {
                if (available) {
                    console.log('[SciTeX Search] Available and ready');
                    this.setupEventListeners();
                    this.loadEngineCapabilities();
                    this.injectSearchModeToggle();
                } else {
                    console.warn('[SciTeX Search] Not available, falling back to default search');
                }
            });
        },

        /**
         * Check if SciTeX search is available
         */
        checkAvailability: async function() {
            try {
                const response = await fetch(this.endpoints.capabilities);
                const data = await response.json();
                return data.available === true;
            } catch (error) {
                console.error('[SciTeX Search] Availability check failed:', error);
                return false;
            }
        },

        /**
         * Load engine capabilities from API
         */
        loadEngineCapabilities: async function() {
            try {
                const response = await fetch(this.endpoints.capabilities);
                const data = await response.json();

                if (data.available && data.engines) {
                    this.state.engines = Object.keys(data.engines);
                    console.log('[SciTeX Search] Available engines:', this.state.engines);
                }
            } catch (error) {
                console.error('[SciTeX Search] Failed to load capabilities:', error);
            }
        },

        /**
         * Setup event listeners
         */
        setupEventListeners: function() {
            const searchForm = document.getElementById('literatureSearchForm');

            if (searchForm) {
                // Intercept form submission
                searchForm.addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.handleSearchSubmit(searchForm);
                });

                console.log('[SciTeX Search] Event listeners attached');
            }
        },

        /**
         * Handle search form submission
         */
        handleSearchSubmit: async function(form) {
            if (this.state.isSearching) {
                console.warn('[SciTeX Search] Search already in progress');
                return;
            }

            // Extract form data
            const formData = new FormData(form);
            const query = formData.get('q');

            if (!query || query.trim() === '') {
                this.showError('Please enter a search query');
                return;
            }

            // Build search parameters
            const params = this.buildSearchParams(formData);

            // Execute search
            await this.executeSearch(query, params);
        },

        /**
         * Build search parameters from form data
         */
        buildSearchParams: function(formData) {
            const params = {};

            // Search fields (always include title and abstract for best results)
            params.search_fields = 'title,abstract';

            // Year range
            const yearFrom = formData.get('year_from');
            const yearTo = formData.get('year_to');
            if (yearFrom) params.year_start = yearFrom;
            if (yearTo) params.year_end = yearTo;

            // Open access filter
            if (formData.get('open_access')) {
                params.open_access = 'true';
            }

            // Recent only (last 5 years)
            if (formData.get('recent_only')) {
                const currentYear = new Date().getFullYear();
                params.year_start = currentYear - 5;
            }

            // High impact (IF > 5) - note: this will be handled by post-filtering
            if (formData.get('high_impact')) {
                params.min_impact_factor = 5;
            }

            // Advanced filters
            const author = formData.get('author');
            const journal = formData.get('journal');
            const minCitations = formData.get('min_citations');
            const docType = formData.get('doc_type');

            if (author) params.author = author;
            if (journal) params.journal = journal;
            if (minCitations) params.min_citations = minCitations;
            if (docType) params.document_type = docType;

            // Max results
            params.max_results = 100;

            return params;
        },

        /**
         * Execute SciTeX search
         */
        executeSearch: async function(query, params) {
            this.state.isSearching = true;
            this.state.currentQuery = query;

            try {
                // Show loading state
                this.showLoadingState(query);

                // Build URL with params
                const url = new URL(this.endpoints.search, window.location.origin);
                url.searchParams.set('q', query);

                Object.keys(params).forEach(key => {
                    if (params[key]) {
                        url.searchParams.set(key, params[key]);
                    }
                });

                console.log('[SciTeX Search] Searching:', url.toString());

                // Execute search
                const startTime = Date.now();
                const response = await fetch(url);
                const data = await response.json();
                const searchTime = ((Date.now() - startTime) / 1000).toFixed(2);

                if (data.error) {
                    this.showError(data.error);
                    return;
                }

                // Store results
                this.state.lastResults = data;

                // Display results
                this.displayResults(data, searchTime);

                console.log(`[SciTeX Search] Found ${data.results.length} results in ${searchTime}s`);

            } catch (error) {
                console.error('[SciTeX Search] Search failed:', error);
                this.showError('Search failed. Please try again.');
            } finally {
                this.state.isSearching = false;
            }
        },

        /**
         * Show loading state
         */
        showLoadingState: function(query) {
            // Get or create results container
            let resultsContainer = document.getElementById('scitex-results-container');

            if (!resultsContainer) {
                resultsContainer = document.createElement('div');
                resultsContainer.id = 'scitex-results-container';
                resultsContainer.className = 'mt-4';

                // Insert after search panel
                const searchPanel = document.getElementById('searchPanel');
                if (searchPanel && searchPanel.parentElement) {
                    searchPanel.parentElement.appendChild(resultsContainer);
                }
            }

            resultsContainer.innerHTML = `
                <div class="card" style="background: var(--color-canvas-default); border: 1px solid var(--color-border-default);">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <h5 class="mb-0" style="color: var(--color-fg-default);">
                                Searching for: <strong>"${this.escapeHtml(query)}"</strong>
                            </h5>
                        </div>
                        <div class="progress mb-3" style="height: 4px;">
                            <div class="progress-bar progress-bar-striped progress-bar-animated"
                                 role="progressbar" style="width: 100%;"></div>
                        </div>
                        <div id="engine-status" class="d-flex flex-wrap gap-2">
                            ${this.renderEngineStatus()}
                        </div>
                    </div>
                </div>
            `;
        },

        /**
         * Render engine status badges
         */
        renderEngineStatus: function() {
            return this.state.engines.map(engine => {
                const info = this.engineStatus[engine] || {
                    name: engine,
                    icon: 'fas fa-search',
                    color: '#95a5a6'
                };

                return `
                    <div class="badge bg-secondary" id="engine-${engine}"
                         style="font-size: 0.875rem; padding: 0.5rem 0.75rem;">
                        <i class="${info.icon}"></i> ${info.name}
                        <span class="spinner-border spinner-border-sm ms-1" style="width: 0.75rem; height: 0.75rem;"></span>
                    </div>
                `;
            }).join('');
        },

        /**
         * Display search results
         */
        displayResults: function(data, searchTime) {
            const resultsContainer = document.getElementById('scitex-results-container');

            if (!resultsContainer) {
                console.error('[SciTeX Search] Results container not found');
                return;
            }

            const results = data.results || [];
            const metadata = data.metadata || {};
            const enginesUsed = metadata.engines_used || [];

            // Build results HTML
            let html = `
                <!-- Search Results Header -->
                <div class="card mb-3" style="background: var(--color-canvas-default); border: 1px solid var(--color-border-default);">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h4 style="color: var(--color-fg-default);">
                                    Found ${results.length} result${results.length !== 1 ? 's' : ''}
                                </h4>
                                <small style="color: var(--color-fg-muted);">
                                    Search completed in ${searchTime}s using ${enginesUsed.length} engine${enginesUsed.length !== 1 ? 's' : ''}
                                </small>
                            </div>
                            <div class="d-flex flex-wrap gap-2">
                                ${enginesUsed.map(engine => this.renderEngineSuccessBadge(engine)).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Add results
            if (results.length > 0) {
                results.forEach((paper, index) => {
                    html += this.renderPaperCard(paper, index);
                });
            } else {
                html += this.renderNoResults();
            }

            resultsContainer.innerHTML = html;

            // Scroll to results
            resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        },

        /**
         * Render engine success badge
         */
        renderEngineSuccessBadge: function(engine) {
            const info = this.engineStatus[engine] || {
                name: engine,
                icon: 'fas fa-check',
                color: '#27ae60'
            };

            return `
                <span class="badge" style="background-color: ${info.color}; font-size: 0.875rem;">
                    <i class="${info.icon}"></i> ${info.name}
                </span>
            `;
        },

        /**
         * Render paper result card
         */
        renderPaperCard: function(paper, index) {
            const authors = (paper.authors || []).slice(0, 5).join(', ');
            const moreAuthors = paper.authors && paper.authors.length > 5 ?
                ` + ${paper.authors.length - 5} more` : '';

            return `
                <div class="card mb-3" style="background: var(--color-canvas-default); border: 1px solid var(--color-border-default);">
                    <div class="card-body">
                        <!-- Title -->
                        <h5 class="card-title" style="color: var(--color-fg-default);">
                            ${index + 1}. ${this.escapeHtml(paper.title || 'Untitled')}
                        </h5>

                        <!-- Authors & Year -->
                        <p class="card-text mb-2" style="color: var(--color-fg-muted);">
                            <strong>Authors:</strong> ${this.escapeHtml(authors)}${moreAuthors}
                            ${paper.year ? `<br><strong>Year:</strong> ${paper.year}` : ''}
                            ${paper.journal ? `<br><strong>Journal:</strong> ${this.escapeHtml(paper.journal)}` : ''}
                        </p>

                        <!-- Abstract -->
                        ${paper.abstract ? `
                            <p class="card-text" style="color: var(--color-fg-default);">
                                ${this.escapeHtml(paper.abstract.substring(0, 300))}${paper.abstract.length > 300 ? '...' : ''}
                            </p>
                        ` : ''}

                        <!-- Metadata Badges -->
                        <div class="d-flex flex-wrap gap-2 mb-2">
                            ${paper.is_open_access ? '<span class="badge bg-success"><i class="fas fa-unlock"></i> Open Access</span>' : ''}
                            ${paper.citation_count ? `<span class="badge bg-info"><i class="fas fa-quote-right"></i> ${paper.citation_count} citations</span>` : ''}
                            ${paper.doi ? `<span class="badge bg-secondary">DOI: ${this.escapeHtml(paper.doi)}</span>` : ''}
                            ${(paper.source_engines || []).map(e => `<span class="badge" style="background-color: ${(this.engineStatus[e] || {}).color || '#95a5a6'};">${e}</span>`).join('')}
                        </div>

                        <!-- Actions -->
                        <div class="d-flex gap-2">
                            ${paper.pdf_url ? `
                                <a href="${this.escapeHtml(paper.pdf_url)}" target="_blank" class="btn btn-sm btn-primary">
                                    <i class="fas fa-file-pdf"></i> PDF
                                </a>
                            ` : ''}
                            ${paper.external_url ? `
                                <a href="${this.escapeHtml(paper.external_url)}" target="_blank" class="btn btn-sm btn-outline-secondary">
                                    <i class="fas fa-external-link-alt"></i> View Online
                                </a>
                            ` : ''}
                            <button class="btn btn-sm btn-outline-success" onclick="ScitexSearch.savePaper('${paper.id}')">
                                <i class="fas fa-bookmark"></i> Save
                            </button>
                            <button class="btn btn-sm btn-outline-info" onclick="ScitexSearch.getCitation('${paper.id}')">
                                <i class="fas fa-quote-left"></i> Cite
                            </button>
                        </div>
                    </div>
                </div>
            `;
        },

        /**
         * Render no results message
         */
        renderNoResults: function() {
            return `
                <div class="card" style="background: var(--color-canvas-default); border: 1px solid var(--color-border-default);">
                    <div class="card-body text-center py-5">
                        <i class="fas fa-search fa-3x mb-3" style="color: var(--color-fg-muted);"></i>
                        <h5 style="color: var(--color-fg-default);">No results found</h5>
                        <p style="color: var(--color-fg-muted);">
                            Try adjusting your search terms or filters
                        </p>
                    </div>
                </div>
            `;
        },

        /**
         * Show error message
         */
        showError: function(message) {
            const resultsContainer = document.getElementById('scitex-results-container');

            if (resultsContainer) {
                resultsContainer.innerHTML = `
                    <div class="alert alert-danger" role="alert">
                        <i class="fas fa-exclamation-triangle"></i>
                        <strong>Search Error:</strong> ${this.escapeHtml(message)}
                    </div>
                `;
            } else {
                alert('Search Error: ' + message);
            }
        },

        /**
         * Inject search mode toggle
         */
        injectSearchModeToggle: function() {
            const searchButton = document.getElementById('searchButton');

            if (searchButton && searchButton.parentElement) {
                const toggleHtml = `
                    <button type="button" class="btn btn-sm btn-outline-secondary" id="scitexModeToggle"
                            style="margin-left: 0.5rem;" title="Toggle between parallel (fast) and single (safe) mode">
                        <i class="fas fa-bolt"></i> Parallel
                    </button>
                `;

                searchButton.insertAdjacentHTML('afterend', toggleHtml);

                // Add click handler
                document.getElementById('scitexModeToggle').addEventListener('click', () => {
                    this.toggleSearchMode();
                });
            }
        },

        /**
         * Toggle search mode between parallel and single
         */
        toggleSearchMode: function() {
            const toggle = document.getElementById('scitexModeToggle');

            if (this.state.searchMode === 'parallel') {
                this.state.searchMode = 'single';
                this.endpoints.search = this.endpoints.searchSingle;
                if (toggle) {
                    toggle.innerHTML = '<i class="fas fa-shield-alt"></i> Single';
                    toggle.title = 'Single mode (safer for rate limits)';
                }
            } else {
                this.state.searchMode = 'parallel';
                this.endpoints.search = '/scholar/api/search/scitex/';
                if (toggle) {
                    toggle.innerHTML = '<i class="fas fa-bolt"></i> Parallel';
                    toggle.title = 'Parallel mode (faster)';
                }
            }

            console.log('[SciTeX Search] Mode changed to:', this.state.searchMode);
        },

        /**
         * Save paper to library (placeholder)
         */
        savePaper: function(paperId) {
            console.log('[SciTeX Search] Save paper:', paperId);
            alert('Save paper functionality - to be implemented');
        },

        /**
         * Get citation for paper (placeholder)
         */
        getCitation: function(paperId) {
            console.log('[SciTeX Search] Get citation:', paperId);
            alert('Get citation functionality - to be implemented');
        },

        /**
         * Escape HTML to prevent XSS
         */
        escapeHtml: function(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    };

    // Expose to global scope
    window.ScitexSearch = ScitexSearch;

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => ScitexSearch.init());
    } else {
        ScitexSearch.init();
    }

})();
