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

            // Load cached results from localStorage on page load
            this.loadCachedResults();

            // Check if SciTeX is available
            this.checkAvailability().then(available => {
                if (available) {
                    console.log('[SciTeX Search] Available and ready');
                    this.setupEventListeners();
                    this.loadEngineCapabilities();
                    // Parallel mode is now the default, no toggle needed
                    // this.injectSearchModeToggle();
                } else {
                    console.warn('[SciTeX Search] Not available, falling back to default search');
                }
            });
        },

        /**
         * Cache search results to localStorage
         */
        cacheResults: function(query, data) {
            try {
                const cacheData = {
                    query: query,
                    results: data,
                    timestamp: Date.now()
                };
                localStorage.setItem('scitex_search_cache', JSON.stringify(cacheData));
                console.log('[SciTeX Search] Results cached to localStorage');
            } catch (error) {
                console.warn('[SciTeX Search] Failed to cache results:', error);
            }
        },

        /**
         * Load cached results from localStorage
         */
        loadCachedResults: function() {
            try {
                const cached = localStorage.getItem('scitex_search_cache');
                if (cached) {
                    const cacheData = JSON.parse(cached);
                    const cacheAge = Date.now() - cacheData.timestamp;
                    const maxAge = 24 * 60 * 60 * 1000; // 24 hours

                    // Only use cache if it's less than 24 hours old
                    if (cacheAge < maxAge) {
                        console.log('[SciTeX Search] Restoring cached results for query:', cacheData.query);

                        // Store results in state
                        this.state.lastResults = cacheData.results;
                        this.state.currentQuery = cacheData.query;

                        // Calculate approximate search time
                        const searchTime = '0.00';

                        // Display the cached results
                        setTimeout(() => {
                            this.displayResults(cacheData.results, searchTime);
                            console.log('[SciTeX Search] Cached results displayed');
                        }, 500);
                    } else {
                        console.log('[SciTeX Search] Cache expired, clearing...');
                        localStorage.removeItem('scitex_search_cache');
                    }
                }
            } catch (error) {
                console.warn('[SciTeX Search] Failed to load cached results:', error);
                localStorage.removeItem('scitex_search_cache');
            }
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
            const searchInput = document.querySelector('.search-input');
            const searchButton = document.getElementById('searchButton');

            if (searchForm) {
                // Intercept form submission
                searchForm.addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.handleSearchSubmit(searchForm);
                });

                console.log('[SciTeX Search] Event listeners attached');
            }

            // Add Enter key listener to search input
            if (searchInput) {
                searchInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        if (searchButton) {
                            searchButton.click();
                        }
                    }
                });
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
                // Instead of showing error, focus on the search input
                const searchInput = document.querySelector('input[name="q"]');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.classList.add('is-invalid');
                    setTimeout(() => {
                        searchInput.classList.remove('is-invalid');
                    }, 2000);
                }
                // Show a gentle reminder in the results area
                const resultsContainer = document.getElementById('scitex-results-container');
                if (resultsContainer) {
                    resultsContainer.innerHTML = `
                        <div class="text-center py-5">
                            <i class="fas fa-search fa-3x text-muted mb-3"></i>
                            <h4 class="text-muted">Enter a search query to find papers</h4>
                            <p class="text-muted">Try searching for topics, authors, or keywords</p>
                        </div>
                    `;
                }
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

                // Show loading spinner in results container
                const resultsContainer = document.getElementById('scitex-results-container');
                if (resultsContainer) {
                    resultsContainer.innerHTML = `
                        <div class="search-loading">
                            <div class="search-loading-spinner"></div>
                            <div class="search-loading-text">Searching for "${query}"...</div>
                        </div>
                    `;
                }

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
            // Show the progressive loading status div
            const progressiveLoadingStatus = document.getElementById('progressiveLoadingStatus');
            if (progressiveLoadingStatus) {
                progressiveLoadingStatus.classList.remove('u-hidden');

                // Update timestamp
                const timestamp = document.getElementById('searchQueueTimestamp');
                if (timestamp) {
                    const now = new Date();
                    timestamp.textContent = now.toLocaleTimeString();
                }

                // Initialize all engines as loading (0 results)
                this.state.engines.forEach(engineName => {
                    this.updateEngineStatus(engineName, 'loading', 0);
                });

                // Update active searches count
                const activeSearchCount = document.getElementById('activeSearchCount');
                if (activeSearchCount) {
                    activeSearchCount.textContent = this.state.engines.length;
                }

                // Reset total results
                const totalResultsCount = document.getElementById('totalResultsCount');
                if (totalResultsCount) {
                    totalResultsCount.textContent = '0';
                }
            }

            // Get or create results container
            let resultsContainer = document.getElementById('scitex-results-container');

            if (!resultsContainer) {
                resultsContainer = document.createElement('div');
                resultsContainer.id = 'scitex-results-container';
                resultsContainer.className = 'mt-4';

                // Insert after progressive loading status
                if (progressiveLoadingStatus && progressiveLoadingStatus.parentElement) {
                    progressiveLoadingStatus.parentElement.insertBefore(resultsContainer, progressiveLoadingStatus.nextSibling);
                }
            }

            // Clear previous results
            resultsContainer.innerHTML = '';
        },

        /**
         * Update individual engine status
         */
        updateEngineStatus: function(engineName, status, count) {
            // Map engine names to data-source values
            const engineMap = {
                'CrossRef': 'crossref',
                'PubMed': 'pubmed',
                'Semantic_Scholar': 'semantic',
                'arXiv': 'arxiv',
                'OpenAlex': 'openalex'
            };

            const dataSource = engineMap[engineName] || engineName.toLowerCase();
            const progressSource = document.querySelector(`[data-source="${dataSource}"]`);

            if (!progressSource) {
                console.warn(`[SciTeX Search] Progress element not found for ${engineName}`);
                return;
            }

            const badge = progressSource.querySelector('.badge');
            const spinner = progressSource.querySelector('.spinner-border');
            const countEl = progressSource.querySelector('.count');

            if (status === 'loading') {
                if (badge) badge.className = 'badge bg-secondary';
                if (spinner) spinner.style.display = 'inline-block';
                if (countEl) countEl.textContent = count || '0';
            } else if (status === 'completed') {
                if (badge) badge.className = 'badge bg-success';
                if (spinner) spinner.style.display = 'none';
                if (countEl) countEl.textContent = count || '0';
            } else if (status === 'error') {
                if (badge) badge.className = 'badge bg-danger';
                if (spinner) spinner.style.display = 'none';
                if (countEl) countEl.textContent = 'Error';
            }
        },

        /**
         * Render engine status badges (legacy - for inline display)
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
            const engineCounts = metadata.engine_counts || {};

            // Cache the results for persistence across hard refreshes
            this.cacheResults(this.state.currentQuery, data);

            // Note: Engine status updates skipped - progress elements are only needed for
            // streaming/real-time engine progress tracking. API results are fetched all at once.

            // Update active searches count (all completed now)
            const activeSearchCount = document.getElementById('activeSearchCount');
            if (activeSearchCount) {
                activeSearchCount.textContent = '0';
            }

            // Update total results count
            const totalResultsCount = document.getElementById('totalResultsCount');
            if (totalResultsCount) {
                totalResultsCount.textContent = results.length;
            }

            // Build results HTML
            let html = `
                <!-- Search Results Header -->
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <div>
                    <h5 class="mb-0">Search Results</h5>
                    <small class="text-muted" id="searchResultsText">
                      Found ${results.length} result${results.length !== 1 ? 's' : ''} - Search completed in ${searchTime}s using ${enginesUsed.length} engine${enginesUsed.length !== 1 ? 's' : ''}
                      <span class="ms-2">
                        ${enginesUsed.map(engine => this.renderEngineSuccessBadge(engine)).join('')}
                      </span>
                    </small>
                  </div>
                  <div class="d-flex align-items-center gap-3">
                    <!-- Global Abstract Toggle -->
                    <div class="d-flex align-items-center gap-2">
                      <small class="text-muted">Abstract:</small>
                      <div class="btn-group btn-group-sm" role="group">
                        <button type="button" class="btn btn-outline-secondary global-abstract-toggle" data-mode="all" title="Show full abstracts">
                          <i class="fas fa-file-alt"></i> All
                        </button>
                        <button type="button" class="btn btn-outline-secondary global-abstract-toggle" data-mode="truncated" title="Show truncated abstracts">
                          <i class="fas fa-ellipsis-h"></i> Truncated
                        </button>
                        <button type="button" class="btn btn-outline-secondary global-abstract-toggle" data-mode="none" title="Hide abstracts">
                          <i class="fas fa-eye-slash"></i> None
                        </button>
                      </div>
                    </div>

                    <!-- Sort Dropdown -->
                    <div>
                      <small class="text-muted">Sort by:</small>
                      <select name="sort_by" class="form-select form-select-sm d-inline-block w-auto ms-2" id="sortSelect" onchange="handleSortChange(this.value)">
                        <option value="relevance">Most Relevant</option>
                        <option value="date_desc">Publication Year (Newest)</option>
                        <option value="date_asc">Publication Year (Oldest)</option>
                        <option value="citations">Citation Count</option>
                        <option value="impact_factor">Impact Factor</option>
                      </select>
                    </div>
                  </div>
                </div>
            `;

            // Add results
            if (results.length > 0) {
                // Add selection toolbar
                html += `
                    <!-- Paper Selection Toolbar -->
                    <div class="card mb-3" style="border-color: var(--scitex-color-05);">
                      <div class="card-body p-2">
                        <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
                          <div class="d-flex align-items-center gap-2">
                            <button type="button" class="btn btn-sm btn-outline-primary" id="selectAllResults">
                              <i class="fas fa-check-double"></i> Select All
                            </button>
                            <button type="button" class="btn btn-sm btn-outline-secondary" id="deselectAllResults">
                              <i class="fas fa-times"></i> Deselect All
                            </button>
                            <span class="text-muted small" id="selectedCount">0 of ${results.length} selected</span>
                          </div>
                          <div class="d-flex gap-2">
                            <button type="button" class="btn btn-sm btn-success" id="exportSelectedBibtex" disabled>
                              <i class="fas fa-file-download"></i> Download as BibTeX
                            </button>
                            <button type="button" class="btn btn-sm btn-warning" id="saveSelectedToProject" disabled>
                              <i class="fas fa-bookmark"></i> Save to Project
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                `;

                // Add paper cards
                results.forEach((paper, index) => {
                    html += this.renderPaperCard(paper, index);
                });
            } else {
                html += this.renderNoResults();
            }

            resultsContainer.innerHTML = html;

            // Setup paper selection and abstract toggle after results are rendered
            if (results.length > 0) {
                setTimeout(() => {
                    if (typeof setupPaperSelection === 'function') {
                        setupPaperSelection();
                    }
                    if (typeof setupGlobalAbstractToggle === 'function') {
                        setupGlobalAbstractToggle();
                    }
                }, 100);
            }

            // Initialize swarm plots with results
            if (window.SwarmPlots && results.length > 0) {
                // Clear any existing swarm plots
                window.SwarmPlots.clear();

                // Wait for DOM to update, then initialize swarm plots
                setTimeout(() => {
                    window.SwarmPlots.init(results);
                    console.log('[SciTeX Search] Swarm plots initialized with', results.length, 'papers');
                }, 100);
            }

            // Scroll to results - DISABLED to prevent auto-scrolling
            // resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
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

            // Determine the best URL for the paper
            const paperUrl = paper.external_url || paper.pdf_url || (paper.doi ? `https://doi.org/${paper.doi}` : null);

            // Format journal with impact factor if available
            let journalInfo = '';
            if (paper.journal) {
                journalInfo = `<br><strong>Journal:</strong> <em>${this.escapeHtml(paper.journal)}</em>`;
                if (paper.impact_factor && paper.impact_factor > 0) {
                    journalInfo += ` <span class="badge bg-warning text-dark">IF: ${paper.impact_factor}</span>`;
                }
            }

            // Create unique ID for the paper
            const paperId = paper.id || `paper-${paper.doi || paper.title}`.replace(/[^a-z0-9]/gi, '_');

            return `
                <div class="card mb-3 result-card" data-paper-id="${this.escapeHtml(paperId)}" data-title="${this.escapeHtml(paper.title || '')}" data-year="${paper.year || ''}" data-citations="${paper.citation_count || 0}" data-impact-factor="${paper.impact_factor || 0}" style="background: var(--color-canvas-default); border: 2px solid var(--color-border-default); box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div class="card-body">
                        <!-- Selection Checkbox and Title -->
                        <div class="d-flex align-items-start gap-2 mb-2">
                            <input type="checkbox" class="form-check-input paper-select-checkbox mt-1" data-paper-id="${this.escapeHtml(paperId)}" data-doi="${this.escapeHtml(paper.doi || '')}" data-title="${this.escapeHtml(paper.title || '')}">
                            <div style="flex: 1;">
                                <!-- Title -->
                                <h5 class="card-title mb-1" style="color: var(--color-fg-default);">
                                    ${index + 1}. ${paperUrl ?
                                        `<a href="${this.escapeHtml(paperUrl)}" target="_blank" style="color: var(--scitex-color-03); text-decoration: none;">
                                            ${this.escapeHtml(paper.title || 'Untitled')}
                                            <i class="fas fa-external-link-alt" style="font-size: 0.7em; margin-left: 4px;"></i>
                                        </a>` :
                                        this.escapeHtml(paper.title || 'Untitled')}
                                </h5>

                                <!-- Authors & Year -->
                                <p class="card-text mb-2" style="color: var(--color-fg-muted);">
                                    <strong>Authors:</strong> ${this.escapeHtml(authors)}${moreAuthors}
                                    ${paper.year ? `<br><strong>Year:</strong> ${paper.year}` : ''}
                                    ${journalInfo}
                                </p>

                                <!-- Abstract -->
                                ${paper.abstract ? `
                                    <div class="result-snippet mt-2">
                                        <div class="abstract-preview" data-abstract-id="${this.escapeHtml(paperId)}" data-mode="truncated" style="color: var(--color-fg-default);">
                                            <span class="abstract-full">${this.escapeHtml(paper.abstract)}</span>
                                            <span class="abstract-short">${this.escapeHtml(paper.abstract.substring(0, 300))}${paper.abstract.length > 300 ? '...' : ''}</span>
                                        </div>
                                    </div>
                                ` : ''}

                                <!-- Metadata Badges -->
                                <div class="d-flex flex-wrap gap-2 mt-3">
                                    ${paper.is_open_access ? '<span class="badge bg-success"><i class="fas fa-unlock"></i> Open Access</span>' : ''}
                                    ${paper.citation_count ? `<span class="badge bg-info"><i class="fas fa-quote-right"></i> ${paper.citation_count} citations</span>` : ''}
                                    ${paper.doi ? `<span class="badge bg-secondary">DOI: ${this.escapeHtml(paper.doi)}</span>` : ''}
                                    ${(paper.source_engines || []).map(e => `<span class="badge" style="background-color: ${(this.engineStatus[e] || {}).color || '#95a5a6'};">${e}</span>`).join('')}
                                </div>

                                <!-- Action Buttons -->
                                <div class="d-flex gap-2 mt-3">
                                    <button class="btn btn-sm btn-outline-primary" onclick="exportCitation(this, 'bibtex')" title="Export as BibTeX">
                                        <i class="fas fa-quote-right"></i> Export
                                    </button>
                                    <button class="btn btn-sm btn-outline-success" onclick="saveToLibrary(this)" title="Save to project library">
                                        <i class="fas fa-bookmark"></i> Save
                                    </button>
                                </div>
                            </div>
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
         * Show citation modal for paper
         */
        showCitation: function(paperIndex) {
            const paper = this.state.lastResults?.results?.[paperIndex];
            if (!paper) {
                alert('Paper not found');
                return;
            }

            // Generate citations in multiple formats
            const citations = this.generateCitations(paper);

            // Create modal
            const modal = `
                <div class="modal fade" id="citationModal" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content" style="background: var(--color-canvas-default); color: var(--color-fg-default);">
                            <div class="modal-header" style="border-bottom: 1px solid var(--color-border-default);">
                                <h5 class="modal-title">
                                    <i class="fas fa-quote-left"></i> Cite this article
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <h6>APA Style</h6>
                                <div class="citation-box mb-3">
                                    <code>${this.escapeHtml(citations.apa)}</code>
                                    <button class="btn btn-sm btn-outline-primary float-end" onclick="ScitexSearch.copyCitation('${this.escapeHtml(citations.apa)}')">
                                        <i class="fas fa-copy"></i> Copy
                                    </button>
                                </div>

                                <h6>MLA Style</h6>
                                <div class="citation-box mb-3">
                                    <code>${this.escapeHtml(citations.mla)}</code>
                                    <button class="btn btn-sm btn-outline-primary float-end" onclick="ScitexSearch.copyCitation('${this.escapeHtml(citations.mla)}')">
                                        <i class="fas fa-copy"></i> Copy
                                    </button>
                                </div>

                                <h6>Chicago Style</h6>
                                <div class="citation-box mb-3">
                                    <code>${this.escapeHtml(citations.chicago)}</code>
                                    <button class="btn btn-sm btn-outline-primary float-end" onclick="ScitexSearch.copyCitation('${this.escapeHtml(citations.chicago)}')">
                                        <i class="fas fa-copy"></i> Copy
                                    </button>
                                </div>

                                <h6>BibTeX</h6>
                                <div class="citation-box mb-3">
                                    <pre><code>${this.escapeHtml(citations.bibtex)}</code></pre>
                                    <button class="btn btn-sm btn-outline-primary float-end" onclick="ScitexSearch.copyCitation(\`${this.escapeHtml(citations.bibtex)}\`)">
                                        <i class="fas fa-copy"></i> Copy
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Remove existing modal if any
            const existing = document.getElementById('citationModal');
            if (existing) existing.remove();

            // Add modal to page
            document.body.insertAdjacentHTML('beforeend', modal);

            // Show modal
            const modalEl = document.getElementById('citationModal');
            const bsModal = new bootstrap.Modal(modalEl);
            bsModal.show();

            // Remove modal from DOM after hiding
            modalEl.addEventListener('hidden.bs.modal', () => {
                modalEl.remove();
            });
        },

        /**
         * Generate citations in multiple formats
         */
        generateCitations: function(paper) {
            const authors = paper.authors || [];
            const title = paper.title || 'Untitled';
            const year = paper.year || 'n.d.';
            const journal = paper.journal || '';
            const doi = paper.doi || '';

            // Format authors for different styles
            const firstAuthor = authors[0] || 'Unknown';
            const authorsAPA = authors.length > 0 ?
                (authors.length === 1 ? firstAuthor :
                 authors.length === 2 ? `${authors[0]} & ${authors[1]}` :
                 `${authors[0]} et al.`) : 'Unknown';

            const authorsMLA = authors.length > 0 ?
                (authors.length === 1 ? firstAuthor :
                 authors.length === 2 ? `${authors[0]}, and ${authors[1]}` :
                 `${authors[0]}, et al.`) : 'Unknown';

            // Generate citations
            return {
                apa: `${authorsAPA}. (${year}). ${title}. ${journal}${doi ? `. https://doi.org/${doi}` : ''}`,
                mla: `${authorsMLA}. "${title}." ${journal}${year !== 'n.d.' ? ` ${year}` : ''}${doi ? `, doi:${doi}` : ''}.`,
                chicago: `${firstAuthor}${authors.length > 1 ? ' et al.' : ''}. "${title}." ${journal}${year !== 'n.d.' ? ` (${year})` : ''}${doi ? `. https://doi.org/${doi}` : ''}.`,
                bibtex: `@article{${(firstAuthor.split(' ')[0] || 'unknown').toLowerCase()}${year},\n  author = {${authors.join(' and ')}},\n  title = {${title}},\n  journal = {${journal}},\n  year = {${year}}${doi ? `,\n  doi = {${doi}}` : ''}\n}`
            };
        },

        /**
         * Copy citation to clipboard
         */
        copyCitation: function(citation) {
            navigator.clipboard.writeText(citation).then(() => {
                alert('Citation copied to clipboard!');
            }).catch(err => {
                console.error('Failed to copy:', err);
                alert('Failed to copy citation');
            });
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

/**
 * Global functions for paper selection and export
 */

/**
 * Setup paper selection event listeners
 */
function setupPaperSelection() {
    console.log('[SciTeX Search] Setting up paper selection...');

    // Select all checkboxes
    const selectAllBtn = document.getElementById('selectAllResults');
    const deselectAllBtn = document.getElementById('deselectAllResults');
    const exportBtn = document.getElementById('exportSelectedBibtex');
    const saveBtn = document.getElementById('saveSelectedToProject');
    const selectedCount = document.getElementById('selectedCount');

    if (!selectAllBtn || !deselectAllBtn) {
        console.warn('[SciTeX Search] Selection buttons not found');
        return;
    }

    // Select all handler
    selectAllBtn.addEventListener('click', function() {
        const checkboxes = document.querySelectorAll('.paper-select-checkbox');
        checkboxes.forEach(cb => cb.checked = true);
        updateSelectedCount();
    });

    // Deselect all handler
    deselectAllBtn.addEventListener('click', function() {
        const checkboxes = document.querySelectorAll('.paper-select-checkbox');
        checkboxes.forEach(cb => cb.checked = false);
        updateSelectedCount();
    });

    // Export BibTeX handler
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            exportSelectedBibtex();
        });
    }

    // Save to project handler
    if (saveBtn) {
        saveBtn.addEventListener('click', function() {
            saveSelectedToProject();
        });
    }

    // Update count on checkbox change
    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('paper-select-checkbox')) {
            updateSelectedCount();
        }
    });

    // Initial count update
    updateSelectedCount();
}

/**
 * Update selected count and enable/disable buttons
 */
function updateSelectedCount() {
    const checkboxes = document.querySelectorAll('.paper-select-checkbox:checked');
    const selectedCountEl = document.getElementById('selectedCount');
    const exportBtn = document.getElementById('exportSelectedBibtex');
    const saveBtn = document.getElementById('saveSelectedToProject');
    const totalCheckboxes = document.querySelectorAll('.paper-select-checkbox').length;

    if (selectedCountEl) {
        selectedCountEl.textContent = `${checkboxes.length} of ${totalCheckboxes} selected`;
    }

    // Enable/disable bulk action buttons
    const hasSelection = checkboxes.length > 0;
    if (exportBtn) exportBtn.disabled = !hasSelection;
    if (saveBtn) saveBtn.disabled = !hasSelection;
}

/**
 * Export citation for a single paper
 */
function exportCitation(button, format) {
    const card = button.closest('.result-card');
    if (!card) {
        console.error('[SciTeX Search] Cannot find paper card');
        return;
    }

    const paperId = card.dataset.paperId;
    const title = card.dataset.title;
    const doi = card.querySelector('.paper-select-checkbox')?.dataset?.doi || '';

    console.log('[SciTeX Search] Export citation:', format, paperId);

    // Generate BibTeX for single paper
    const bibtex = generateBibtex(card);

    if (format === 'bibtex') {
        // Download as file
        downloadTextFile(bibtex, `${sanitizeFilename(title)}.bib`);
    }
}

/**
 * Save a single paper to library
 */
function saveToLibrary(button) {
    const card = button.closest('.result-card');
    if (!card) {
        console.error('[SciTeX Search] Cannot find paper card');
        return;
    }

    // Check if user is authenticated
    const isAuthenticated = document.body.dataset.userAuthenticated === 'true';
    if (!isAuthenticated) {
        if (confirm('To save papers to a project, you need to sign in.\n\nWould you like to sign in now?')) {
            window.location.href = '/accounts/signin/?next=' + encodeURIComponent(window.location.pathname);
        }
        return;
    }

    // Get paper data from the card
    const paperData = {
        paper_id: card.dataset.paperId,
        title: card.dataset.title || card.querySelector('.paper-title')?.textContent,
        authors: card.dataset.authors || card.querySelector('.paper-authors')?.textContent,
        year: card.dataset.year || card.querySelector('.paper-year')?.textContent,
        doi: card.dataset.doi,
        abstract: card.dataset.abstract || card.querySelector('.abstract-preview')?.textContent,
        citations: card.dataset.citations,
        journal: card.dataset.journal || card.querySelector('.paper-journal')?.textContent,
        url: card.dataset.url,
        source: card.dataset.source
    };

    console.log('[SciTeX Search] Save to library:', paperData.title);

    // Show project selector modal
    showProjectSelectorForPaper(paperData);
}

/**
 * Export selected papers as BibTeX
 */
function exportSelectedBibtex() {
    const selectedCheckboxes = document.querySelectorAll('.paper-select-checkbox:checked');

    if (selectedCheckboxes.length === 0) {
        alert('Please select at least one paper to export');
        return;
    }

    console.log('[SciTeX Search] Exporting', selectedCheckboxes.length, 'papers as BibTeX');

    let allBibtex = '';

    selectedCheckboxes.forEach(checkbox => {
        const card = checkbox.closest('.result-card');
        if (card) {
            const bibtex = generateBibtex(card);
            allBibtex += bibtex + '\n\n';
        }
    });

    // Download as file
    const timestamp = new Date().toISOString().split('T')[0];
    downloadTextFile(allBibtex, `scitex_export_${timestamp}.bib`);
}

/**
 * Save selected papers to project
 */
function saveSelectedToProject() {
    const selectedCheckboxes = document.querySelectorAll('.paper-select-checkbox:checked');

    if (selectedCheckboxes.length === 0) {
        alert('Please select at least one paper to save');
        return;
    }

    // Check if user is authenticated
    const isAuthenticated = document.body.dataset.userAuthenticated === 'true';
    if (!isAuthenticated) {
        if (confirm('To save papers to a project, you need to sign in.\n\nWould you like to sign in now?')) {
            window.location.href = '/accounts/signin/?next=' + encodeURIComponent(window.location.pathname);
        }
        return;
    }

    console.log('[SciTeX Search] Saving', selectedCheckboxes.length, 'papers to project');

    // Collect paper data
    const papers = [];
    selectedCheckboxes.forEach(checkbox => {
        const card = checkbox.closest('.result-card');
        if (card) {
            papers.push({
                paper_id: card.dataset.paperId,
                title: card.dataset.title || card.querySelector('.paper-title')?.textContent,
                authors: card.dataset.authors || card.querySelector('.paper-authors')?.textContent,
                year: card.dataset.year || card.querySelector('.paper-year')?.textContent,
                doi: checkbox.dataset.doi || card.dataset.doi,
                abstract: card.dataset.abstract || card.querySelector('.abstract-preview')?.textContent,
                citations: card.dataset.citations,
                journal: card.dataset.journal || card.querySelector('.paper-journal')?.textContent,
                url: card.dataset.url,
                source: card.dataset.source
            });
        }
    });

    // Show bulk save modal
    showBulkProjectSelectorForPapers(papers);
}

/**
 * Generate BibTeX for a paper card
 */
function generateBibtex(card) {
    const title = card.dataset.title || 'Untitled';
    const year = card.dataset.year || '';
    const checkbox = card.querySelector('.paper-select-checkbox');
    const doi = checkbox?.dataset?.doi || '';

    // Extract more details from the card
    const cardBody = card.querySelector('.card-body');
    let authors = '';
    let journal = '';

    if (cardBody) {
        const authorText = cardBody.querySelector('.card-text')?.textContent || '';
        const authorMatch = authorText.match(/Authors:\s*([^\n]+)/);
        if (authorMatch) {
            authors = authorMatch[1].trim().split(',').map(a => a.trim()).join(' and ');
        }

        const journalMatch = authorText.match(/Journal:\s*([^\n]+)/);
        if (journalMatch) {
            journal = journalMatch[1].trim();
        }
    }

    // Generate BibTeX key (first author last name + year)
    const firstAuthor = authors.split(' and ')[0] || 'unknown';
    const lastName = firstAuthor.split(' ').pop().toLowerCase().replace(/[^a-z]/g, '');
    const bibtexKey = `${lastName}${year || '2024'}`;

    // Build BibTeX entry
    let bibtex = `@article{${bibtexKey},\n`;
    if (authors) bibtex += `  author = {${authors}},\n`;
    bibtex += `  title = {${title}},\n`;
    if (journal) bibtex += `  journal = {${journal}},\n`;
    if (year) bibtex += `  year = {${year}},\n`;
    if (doi) bibtex += `  doi = {${doi}},\n`;
    bibtex += `}`;

    return bibtex;
}

/**
 * Download text as a file
 */
function downloadTextFile(text, filename) {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Sanitize filename
 */
function sanitizeFilename(filename) {
    return filename.replace(/[^a-z0-9_\-]/gi, '_').substring(0, 100);
}

/**
 * Setup global abstract toggle
 */
function setupGlobalAbstractToggle() {
    console.log('[SciTeX Search] Setting up global abstract toggle...');

    const toggleButtons = document.querySelectorAll('.global-abstract-toggle');

    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const mode = this.dataset.mode;

            // Update button states
            toggleButtons.forEach(btn => {
                btn.classList.remove('active');
                btn.classList.add('btn-outline-secondary');
                btn.classList.remove('btn-secondary');
            });

            this.classList.add('active');
            this.classList.remove('btn-outline-secondary');
            this.classList.add('btn-secondary');

            // Update all abstract previews
            updateAllAbstractPreviews(mode);
        });
    });

    // Set initial state to "truncated"
    const truncatedBtn = document.querySelector('.global-abstract-toggle[data-mode="truncated"]');
    if (truncatedBtn) {
        truncatedBtn.click();
    }
}

/**
 * Update all abstract previews based on mode
 */
function updateAllAbstractPreviews(mode) {
    const abstractPreviews = document.querySelectorAll('.abstract-preview');

    abstractPreviews.forEach(preview => {
        const fullSpan = preview.querySelector('.abstract-full');
        const shortSpan = preview.querySelector('.abstract-short');

        if (mode === 'all') {
            // Show full abstract
            if (fullSpan) fullSpan.style.display = 'inline';
            if (shortSpan) shortSpan.style.display = 'none';
            preview.style.display = 'block';
        } else if (mode === 'truncated') {
            // Show truncated abstract
            if (fullSpan) fullSpan.style.display = 'none';
            if (shortSpan) shortSpan.style.display = 'inline';
            preview.style.display = 'block';
        } else if (mode === 'none') {
            // Hide abstract entirely
            preview.style.display = 'none';
        }
    });
}

/**
 * Handle sort change
 */
function handleSortChange(sortBy) {
    console.log('[SciTeX Search] Sorting by:', sortBy);

    const resultsContainer = document.getElementById('scitex-results-container');
    if (!resultsContainer) return;

    const cards = Array.from(resultsContainer.querySelectorAll('.result-card'));

    // Sort cards based on selected criterion
    cards.sort((a, b) => {
        switch (sortBy) {
            case 'date_desc':
                return parseInt(b.dataset.year || 0) - parseInt(a.dataset.year || 0);
            case 'date_asc':
                return parseInt(a.dataset.year || 0) - parseInt(b.dataset.year || 0);
            case 'citations':
                return parseInt(b.dataset.citations || 0) - parseInt(a.dataset.citations || 0);
            case 'impact_factor':
                return parseFloat(b.dataset.impactFactor || 0) - parseFloat(a.dataset.impactFactor || 0);
            case 'relevance':
            default:
                return 0; // Keep original order
        }
    });

    // Find the container where cards are located (after the selection toolbar)
    const selectionToolbar = resultsContainer.querySelector('.card.mb-3');
    const insertPoint = selectionToolbar ? selectionToolbar.nextElementSibling : resultsContainer.firstChild;

    // Re-insert cards in sorted order
    cards.forEach((card, index) => {
        // Update numbering
        const title = card.querySelector('.card-title');
        if (title) {
            title.innerHTML = title.innerHTML.replace(/^\d+\./, `${index + 1}.`);
        }
        resultsContainer.appendChild(card);
    });
}

// Initialize functions when results are displayed
document.addEventListener('DOMContentLoaded', function() {
    let isSettingUp = false; // Guard flag to prevent infinite loop

    // Watch for changes to the results container
    const observer = new MutationObserver(function(mutations) {
        // Prevent infinite loop by checking guard flag
        if (isSettingUp) {
            return;
        }

        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                // Check if paper cards were added
                const hasCards = Array.from(mutation.addedNodes).some(node =>
                    node.classList && node.classList.contains('result-card')
                );

                if (hasCards || document.querySelector('.result-card')) {
                    isSettingUp = true; // Set guard flag
                    setupPaperSelection();
                    setupGlobalAbstractToggle();
                    // Reset guard flag after a short delay
                    setTimeout(() => { isSettingUp = false; }, 100);
                }
            }
        });
    });

    const resultsContainer = document.getElementById('scitex-results-container');
    if (resultsContainer) {
        observer.observe(resultsContainer, { childList: true, subtree: true });
    }
});

/**
 * Show project selector modal for a single paper
 */
function showProjectSelectorForPaper(paperData) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('paperProjectSelectorModal');
    if (!modal) {
        modal = createProjectSelectorModal();
        document.body.appendChild(modal);
    }

    // Store paper data for later use
    modal.dataset.paperData = JSON.stringify(paperData);

    // Show modal
    modal.style.display = 'flex';
}

/**
 * Create project selector modal
 */
function createProjectSelectorModal() {
    const modal = document.createElement('div');
    modal.id = 'paperProjectSelectorModal';
    modal.style.cssText = 'display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.5); z-index: 10000; align-items: center; justify-content: center;';

    // Get user projects from page data or fetch them
    const userProjects = window.userProjects || [];
    const currentProject = window.currentProject || null;

    modal.innerHTML = `
        <div style="background: var(--color-canvas-default, #fff); border: 1px solid var(--color-border-default, #ddd); border-radius: 12px; padding: 2rem; max-width: 500px; width: 90%; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);">
            <h3 style="color: var(--color-fg-default, #000); margin-bottom: 1.5rem; font-size: 1.3rem; font-weight: 600;">
                <i class="fas fa-folder-open"></i> Select Project
            </h3>
            ${userProjects.length > 0 ? `
                <div style="margin-bottom: 1.5rem;">
                    <label style="display: block; color: var(--color-fg-muted, #666); margin-bottom: 0.5rem; font-size: 0.95rem;">Choose a project to save this paper:</label>
                    <select id="paperProjectSelectorDropdown" class="form-control" style="width: 100%; padding: 0.75rem; font-size: 1rem;">
                        ${userProjects.map(project => `
                            <option value="${project.id}" ${currentProject && currentProject.id === project.id ? 'selected' : ''}>
                                ${project.name}
                            </option>
                        `).join('')}
                    </select>
                </div>
                <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                    <button onclick="closePaperProjectModal()" class="btn btn-outline-secondary" style="padding: 0.5rem 1.5rem;">
                        Cancel
                    </button>
                    <button onclick="confirmPaperProjectSave()" class="btn btn-warning" style="padding: 0.5rem 1.5rem;">
                        <i class="fas fa-bookmark"></i> Save to Project
                    </button>
                </div>
            ` : `
                <p style="color: var(--color-fg-muted, #666); margin-bottom: 1.5rem;">
                    You don't have any projects yet. Create a project first to save papers.
                </p>
                <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                    <button onclick="closePaperProjectModal()" class="btn btn-outline-secondary" style="padding: 0.5rem 1.5rem;">
                        Close
                    </button>
                    <a href="/new/" class="btn btn-primary" style="padding: 0.5rem 1.5rem;">Create Project</a>
                </div>
            `}
        </div>
    `;

    return modal;
}

/**
 * Close paper project selector modal
 */
window.closePaperProjectModal = function() {
    const modal = document.getElementById('paperProjectSelectorModal');
    if (modal) {
        modal.style.display = 'none';
    }
};

/**
 * Confirm paper save to project
 */
window.confirmPaperProjectSave = function() {
    const modal = document.getElementById('paperProjectSelectorModal');
    const dropdown = document.getElementById('paperProjectSelectorDropdown');

    if (!modal || !dropdown) return;

    const paperData = JSON.parse(modal.dataset.paperData || '{}');
    const projectId = dropdown.value;

    if (!projectId) {
        alert('Please select a project');
        return;
    }

    console.log('[SciTeX Search] Saving paper to project:', projectId, paperData);

    // Call API to save paper to project
    savePaperToProject(paperData, projectId);

    // Close modal
    closePaperProjectModal();
};

/**
 * Save paper to project via API
 */
async function savePaperToProject(paperData, projectId) {
    try {
        // Show loading state
        const saveBtn = event.target;
        if (saveBtn) {
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
        }

        // API call to save paper
        const response = await fetch('/scholar/api/papers/save/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            },
            body: JSON.stringify({
                project_id: projectId,
                paper: paperData
            })
        });

        const result = await response.json();

        if (result.success) {
            // Show success message
            alert(`Paper "${paperData.title}" saved to project successfully!`);
        } else {
            alert('Failed to save paper: ' + (result.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('[SciTeX Search] Error saving paper:', error);
        alert('Failed to save paper. Please try again.');
    }
}

/**
 * Show bulk project selector modal for multiple papers
 */
function showBulkProjectSelectorForPapers(papers) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('bulkProjectSelectorModal');
    if (!modal) {
        modal = createBulkProjectSelectorModal();
        document.body.appendChild(modal);
    }

    // Store papers data for later use
    modal.dataset.papersData = JSON.stringify(papers);

    // Update paper count in modal
    const countSpan = modal.querySelector('#bulkPaperCount');
    if (countSpan) {
        countSpan.textContent = papers.length;
    }

    // Show modal
    modal.style.display = 'flex';
}

/**
 * Create bulk project selector modal
 */
function createBulkProjectSelectorModal() {
    const modal = document.createElement('div');
    modal.id = 'bulkProjectSelectorModal';
    modal.style.cssText = 'display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.5); z-index: 10000; align-items: center; justify-content: center;';

    // Get user projects from page data or fetch them
    const userProjects = window.userProjects || [];
    const currentProject = window.currentProject || null;

    modal.innerHTML = `
        <div style="background: var(--color-canvas-default, #fff); border: 1px solid var(--color-border-default, #ddd); border-radius: 12px; padding: 2rem; max-width: 500px; width: 90%; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);">
            <h3 style="color: var(--color-fg-default, #000); margin-bottom: 1.5rem; font-size: 1.3rem; font-weight: 600;">
                <i class="fas fa-folder-open"></i> Save <span id="bulkPaperCount">0</span> Papers to Project
            </h3>
            ${userProjects.length > 0 ? `
                <div style="margin-bottom: 1.5rem;">
                    <label style="display: block; color: var(--color-fg-muted, #666); margin-bottom: 0.5rem; font-size: 0.95rem;">Choose a project to save these papers:</label>
                    <select id="bulkProjectSelectorDropdown" class="form-control" style="width: 100%; padding: 0.75rem; font-size: 1rem;">
                        ${userProjects.map(project => `
                            <option value="${project.id}" ${currentProject && currentProject.id === project.id ? 'selected' : ''}>
                                ${project.name}
                            </option>
                        `).join('')}
                    </select>
                </div>
                <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                    <button onclick="closeBulkProjectModal()" class="btn btn-outline-secondary" style="padding: 0.5rem 1.5rem;">
                        Cancel
                    </button>
                    <button onclick="confirmBulkProjectSave()" class="btn btn-warning" style="padding: 0.5rem 1.5rem;">
                        <i class="fas fa-bookmark"></i> Save All to Project
                    </button>
                </div>
            ` : `
                <p style="color: var(--color-fg-muted, #666); margin-bottom: 1.5rem;">
                    You don't have any projects yet. Create a project first to save papers.
                </p>
                <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                    <button onclick="closeBulkProjectModal()" class="btn btn-outline-secondary" style="padding: 0.5rem 1.5rem;">
                        Close
                    </button>
                    <a href="/new/" class="btn btn-primary" style="padding: 0.5rem 1.5rem;">Create Project</a>
                </div>
            `}
        </div>
    `;

    return modal;
}

/**
 * Close bulk project selector modal
 */
window.closeBulkProjectModal = function() {
    const modal = document.getElementById('bulkProjectSelectorModal');
    if (modal) {
        modal.style.display = 'none';
    }
};

/**
 * Confirm bulk papers save to project
 */
window.confirmBulkProjectSave = async function() {
    const modal = document.getElementById('bulkProjectSelectorModal');
    const dropdown = document.getElementById('bulkProjectSelectorDropdown');

    if (!modal || !dropdown) return;

    const papers = JSON.parse(modal.dataset.papersData || '[]');
    const projectId = dropdown.value;

    if (!projectId) {
        alert('Please select a project');
        return;
    }

    console.log('[SciTeX Search] Saving', papers.length, 'papers to project:', projectId);

    try {
        // Show loading state
        const saveBtn = event.target;
        if (saveBtn) {
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
        }

        // API call to save papers
        const response = await fetch('/scholar/api/papers/save-bulk/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            },
            body: JSON.stringify({
                project_id: projectId,
                papers: papers
            })
        });

        const result = await response.json();

        if (result.success) {
            // Show success message
            alert(`${papers.length} papers saved to project successfully!`);

            // Uncheck all checkboxes
            document.querySelectorAll('.paper-select-checkbox:checked').forEach(cb => {
                cb.checked = false;
            });

            // Hide selection toolbar if visible
            const toolbar = document.querySelector('.selection-toolbar');
            if (toolbar) {
                toolbar.style.display = 'none';
            }
        } else {
            alert('Failed to save papers: ' + (result.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('[SciTeX Search] Error saving papers:', error);
        alert('Failed to save papers. Please try again.');
    } finally {
        // Close modal
        closeBulkProjectModal();
    }
};
