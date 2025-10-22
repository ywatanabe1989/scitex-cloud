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
                    // Parallel mode is now the default, no toggle needed
                    // this.injectSearchModeToggle();
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

            // Update engine statuses with result counts
            enginesUsed.forEach(engineName => {
                const count = engineCounts[engineName] || 0;
                this.updateEngineStatus(engineName, 'completed', count);
            });

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

            return `
                <div class="card mb-3" style="background: var(--color-canvas-default); border: 2px solid var(--color-border-default); box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div class="card-body">
                        <!-- Title -->
                        <h5 class="card-title" style="color: var(--color-fg-default);">
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
