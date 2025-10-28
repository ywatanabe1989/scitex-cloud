/**
 * Swarm Plot Visualization for Scholar Filters using Plotly.js
 * Shows distribution of papers across Year, Citations, and Impact Factor dimensions
 * Each dot represents an individual paper with synchronized cross-filtering
 */

const SwarmPlots = {
    // Configuration
    config: {
        height: 100,
        margin: { l: 40, r: 40, t: 10, b: 30 },
        includedColor: '#3b82f6',  // Blue for included papers
        filteredColor: '#d1d5db',  // Gray for filtered papers
        hoverColor: '#f59e0b',     // Orange for hover
        dotSize: 8,
        dotOpacity: 0.7,
    },

    // State
    data: [],
    filteredIndices: new Set(),
    filters: {
        yearRange: [1900, 2025],
        citationsRange: [0, 12000],
        impactFactorRange: [0, 50]
    },

    // Flag to track if sliders are being initialized
    initializingSliders: true,

    /**
     * Initialize swarm plots with search results data
     */
    init: function(papers) {
        console.log('[Swarm Plots] Initializing with', papers.length, 'papers');

        if (!papers || papers.length === 0) {
            console.warn('[Swarm Plots] No papers to visualize');
            return;
        }

        this.data = papers;
        this.filteredIndices = new Set(papers.map((_, i) => i)); // All included initially

        // Create containers and plots
        this.createPlotContainers();
        this.createYearSwarmPlot();
        this.createCitationsSwarmPlot();
        this.createImpactFactorSwarmPlot();

        // Attach filter change listeners
        this.attachFilterListeners();

        // Set flag to indicate initialization is complete - now allow filter-triggered searches
        this.initializingSliders = false;
        console.log('[Swarm Plots] Initialized successfully');
    },

    /**
     * Create plot containers above sliders
     */
    createPlotContainers: function() {
        // Year plot container
        const yearSlider = document.getElementById('yearSlider');
        if (yearSlider && !document.getElementById('yearSwarmPlot')) {
            const yearDiv = document.createElement('div');
            yearDiv.id = 'yearSwarmPlot';
            yearDiv.style.width = '100%';
            yearDiv.style.height = this.config.height + 'px';
            yearDiv.style.marginBottom = '8px';
            yearSlider.parentNode.insertBefore(yearDiv, yearSlider);
        }

        // Citations plot container
        const citationsSlider = document.getElementById('citationsSlider');
        if (citationsSlider && !document.getElementById('citationsSwarmPlot')) {
            const citDiv = document.createElement('div');
            citDiv.id = 'citationsSwarmPlot';
            citDiv.style.width = '100%';
            citDiv.style.height = this.config.height + 'px';
            citDiv.style.marginBottom = '8px';
            citationsSlider.parentNode.insertBefore(citDiv, citationsSlider);
        }

        // Impact Factor plot container
        const impactSlider = document.getElementById('impactFactorSlider');
        if (impactSlider && !document.getElementById('impactFactorSwarmPlot')) {
            const impactDiv = document.createElement('div');
            impactDiv.id = 'impactFactorSwarmPlot';
            impactDiv.style.width = '100%';
            impactDiv.style.height = this.config.height + 'px';
            impactDiv.style.marginBottom = '8px';
            impactSlider.parentNode.insertBefore(impactDiv, impactSlider);
        }
    },

    /**
     * Create Year swarm plot
     */
    createYearSwarmPlot: function() {
        const years = this.data.map(p => p.year || null).filter(y => y && y >= 1900 && y <= 2025);

        if (years.length === 0) {
            console.warn('[Swarm Plots] No valid year data');
            return;
        }

        // Calculate dynamic range based on actual data
        const minYear = Math.min(...years);
        const maxYear = Math.max(...years);
        const yearPadding = Math.max(2, Math.ceil((maxYear - minYear) * 0.05)); // 5% padding
        const yearRange = [minYear - yearPadding, maxYear + yearPadding];

        const colors = this.data.map((_, i) =>
            this.filteredIndices.has(i) ? this.config.includedColor : this.config.filteredColor
        );

        const hoverText = this.data.map(p =>
            `<b>${this.escapeHtml(p.title || 'Untitled')}</b><br>` +
            `Year: ${p.year || 'N/A'}<br>` +
            `Citations: ${p.citations || 0}<br>` +
            (p.impact_factor ? `IF: ${p.impact_factor}` : '')
        );

        const trace = {
            x: years,
            y: years.map(() => Math.random() * 0.4 - 0.2), // Jitter for swarm effect
            mode: 'markers',
            type: 'scatter',
            marker: {
                size: this.config.dotSize,
                color: colors,
                opacity: this.config.dotOpacity,
                line: { width: 0 }
            },
            text: hoverText,
            hoverinfo: 'text',
            hoverlabel: {
                bgcolor: 'var(--color-canvas-overlay)',
                bordercolor: 'var(--color-border-default)',
                font: { size: 12, color: 'var(--color-fg-default)' }
            }
        };

        const layout = {
            xaxis: {
                title: '',
                range: yearRange,
                fixedrange: true
            },
            yaxis: {
                visible: false,
                range: [-0.5, 0.5],
                fixedrange: true
            },
            margin: this.config.margin,
            height: this.config.height,
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            showlegend: false,
            hovermode: 'closest'
        };

        const config = {
            displayModeBar: false,
            responsive: true
        };

        Plotly.newPlot('yearSwarmPlot', [trace], layout, config);
    },

    /**
     * Create Citations swarm plot
     */
    createCitationsSwarmPlot: function() {
        const citations = this.data.map(p => p.citations || 0);

        // Calculate dynamic range based on actual data
        const minCitations = Math.min(...citations);
        const maxCitations = Math.max(...citations);
        const citationsPadding = Math.max(10, Math.ceil((maxCitations - minCitations) * 0.05)); // 5% padding, min 10
        const citationsRange = [
            Math.max(0, minCitations - citationsPadding),
            maxCitations + citationsPadding
        ];

        const colors = this.data.map((_, i) =>
            this.filteredIndices.has(i) ? this.config.includedColor : this.config.filteredColor
        );

        const hoverText = this.data.map(p =>
            `<b>${this.escapeHtml(p.title || 'Untitled')}</b><br>` +
            `Year: ${p.year || 'N/A'}<br>` +
            `Citations: ${p.citations || 0}<br>` +
            (p.impact_factor ? `IF: ${p.impact_factor}` : '')
        );

        const trace = {
            x: citations,
            y: citations.map(() => Math.random() * 0.4 - 0.2),
            mode: 'markers',
            type: 'scatter',
            marker: {
                size: this.config.dotSize,
                color: colors,
                opacity: this.config.dotOpacity,
                line: { width: 0 }
            },
            text: hoverText,
            hoverinfo: 'text',
            hoverlabel: {
                bgcolor: 'var(--color-canvas-overlay)',
                bordercolor: 'var(--color-border-default)',
                font: { size: 12, color: 'var(--color-fg-default)' }
            }
        };

        const layout = {
            xaxis: {
                title: '',
                range: citationsRange,
                fixedrange: true
            },
            yaxis: {
                visible: false,
                range: [-0.5, 0.5],
                fixedrange: true
            },
            margin: this.config.margin,
            height: this.config.height,
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            showlegend: false,
            hovermode: 'closest'
        };

        const config = {
            displayModeBar: false,
            responsive: true
        };

        Plotly.newPlot('citationsSwarmPlot', [trace], layout, config);
    },

    /**
     * Create Impact Factor swarm plot
     */
    createImpactFactorSwarmPlot: function() {
        const impactFactors = this.data
            .map(p => p.impact_factor && p.impact_factor > 0 ? p.impact_factor : null);

        const validData = this.data
            .map((p, i) => ({ paper: p, index: i, if: impactFactors[i] }))
            .filter(d => d.if !== null);

        if (validData.length === 0) {
            console.warn('[Swarm Plots] No valid impact factor data');
            // Show empty plot with message
            const layout = {
                xaxis: { title: '', range: [0, 10], fixedrange: true },
                yaxis: { visible: false, range: [-0.5, 0.5], fixedrange: true },
                margin: this.config.margin,
                height: this.config.height,
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                annotations: [{
                    text: 'No impact factor data available',
                    xref: 'paper',
                    yref: 'paper',
                    x: 0.5,
                    y: 0.5,
                    showarrow: false,
                    font: { size: 12, color: '#999' }
                }]
            };
            Plotly.newPlot('impactFactorSwarmPlot', [], layout, { displayModeBar: false });
            return;
        }

        // Calculate dynamic range based on actual impact factor data
        const ifValues = validData.map(d => d.if);
        const minIF = Math.min(...ifValues);
        const maxIF = Math.max(...ifValues);
        const ifPadding = Math.max(0.5, (maxIF - minIF) * 0.05); // 5% padding, min 0.5
        const ifRange = [
            Math.max(0, minIF - ifPadding),
            maxIF + ifPadding
        ];

        const colors = validData.map(d =>
            this.filteredIndices.has(d.index) ? this.config.includedColor : this.config.filteredColor
        );

        const hoverText = validData.map(d =>
            `<b>${this.escapeHtml(d.paper.title || 'Untitled')}</b><br>` +
            `Year: ${d.paper.year || 'N/A'}<br>` +
            `Citations: ${d.paper.citations || 0}<br>` +
            `IF: ${d.if}`
        );

        const trace = {
            x: validData.map(d => d.if),
            y: validData.map(() => Math.random() * 0.4 - 0.2),
            mode: 'markers',
            type: 'scatter',
            marker: {
                size: this.config.dotSize,
                color: colors,
                opacity: this.config.dotOpacity,
                line: { width: 0 }
            },
            text: hoverText,
            hoverinfo: 'text',
            hoverlabel: {
                bgcolor: 'var(--color-canvas-overlay)',
                bordercolor: 'var(--color-border-default)',
                font: { size: 12, color: 'var(--color-fg-default)' }
            }
        };

        const layout = {
            xaxis: {
                title: '',
                range: ifRange,
                fixedrange: true
            },
            yaxis: {
                visible: false,
                range: [-0.5, 0.5],
                fixedrange: true
            },
            margin: this.config.margin,
            height: this.config.height,
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            showlegend: false,
            hovermode: 'closest'
        };

        const config = {
            displayModeBar: false,
            responsive: true
        };

        Plotly.newPlot('impactFactorSwarmPlot', [trace], layout, config);
    },

    /**
     * Update all swarm plots when filters change
     */
    updateSwarmPlots: function() {
        // Recalculate which papers pass all filters
        this.filteredIndices.clear();

        this.data.forEach((paper, i) => {
            const yearOk = !paper.year || (
                paper.year >= this.filters.yearRange[0] &&
                paper.year <= this.filters.yearRange[1]
            );

            const citationsOk = paper.citations === undefined || (
                paper.citations >= this.filters.citationsRange[0] &&
                paper.citations <= this.filters.citationsRange[1]
            );

            const impactOk = !paper.impact_factor || (
                paper.impact_factor >= this.filters.impactFactorRange[0] &&
                paper.impact_factor <= this.filters.impactFactorRange[1]
            );

            if (yearOk && citationsOk && impactOk) {
                this.filteredIndices.add(i);
            }
        });

        // Update colors in all plots
        const newColors = this.data.map((_, i) =>
            this.filteredIndices.has(i) ? this.config.includedColor : this.config.filteredColor
        );

        // Update Year plot
        if (document.getElementById('yearSwarmPlot')) {
            Plotly.restyle('yearSwarmPlot', { 'marker.color': [newColors] });
        }

        // Update Citations plot
        if (document.getElementById('citationsSwarmPlot')) {
            Plotly.restyle('citationsSwarmPlot', { 'marker.color': [newColors] });
        }

        // Update Impact Factor plot (only for papers with IF data)
        if (document.getElementById('impactFactorSwarmPlot')) {
            const impactColors = [];
            this.data.forEach((p, i) => {
                if (p.impact_factor && p.impact_factor > 0) {
                    impactColors.push(this.filteredIndices.has(i) ? this.config.includedColor : this.config.filteredColor);
                }
            });
            if (impactColors.length > 0) {
                Plotly.restyle('impactFactorSwarmPlot', { 'marker.color': [impactColors] });
            }
        }

        console.log('[Swarm Plots] Updated:', this.filteredIndices.size, '/', this.data.length, 'papers visible');
    },

    /**
     * Attach listeners to slider changes
     */
    attachFilterListeners: function() {
        // Year slider
        const yearSlider = document.getElementById('yearSlider');
        if (yearSlider && yearSlider.noUiSlider) {
            yearSlider.noUiSlider.on('update', (values) => {
                this.filters.yearRange = [parseInt(values[0]), parseInt(values[1])];
                this.updateSwarmPlots();
                // Only trigger search if sliders are already initialized (not during initial setup)
                if (!this.initializingSliders) {
                    this.triggerFilteredSearch();
                }
            });
        }

        // Citations slider
        const citationsSlider = document.getElementById('citationsSlider');
        if (citationsSlider && citationsSlider.noUiSlider) {
            citationsSlider.noUiSlider.on('update', (values) => {
                this.filters.citationsRange = [parseInt(values[0]), parseInt(values[1])];
                this.updateSwarmPlots();
                // Only trigger search if sliders are already initialized (not during initial setup)
                if (!this.initializingSliders) {
                    this.triggerFilteredSearch();
                }
            });
        }

        // Impact Factor slider
        const impactFactorSlider = document.getElementById('impactFactorSlider');
        if (impactFactorSlider && impactFactorSlider.noUiSlider) {
            impactFactorSlider.noUiSlider.on('update', (values) => {
                this.filters.impactFactorRange = [parseFloat(values[0]), parseFloat(values[1])];
                this.updateSwarmPlots();
                // Only trigger search if sliders are already initialized (not during initial setup)
                if (!this.initializingSliders) {
                    this.triggerFilteredSearch();
                }
            });
        }

        console.log('[Swarm Plots] Filter listeners attached');
    },

    /**
     * Trigger a new search with current filter values
     */
    triggerFilteredSearch: function() {
        // Get the search form and update hidden inputs
        const form = document.getElementById('literatureSearchForm');
        if (!form) return;

        // Update hidden filter inputs
        const yearFromInput = document.getElementById('yearFromInput');
        const yearToInput = document.getElementById('yearToInput');
        const citationsMinInput = document.getElementById('citationsMinInput');
        const citationsMaxInput = document.getElementById('citationsMaxInput');
        const impactFactorMinInput = document.getElementById('impactFactorMinInput');
        const impactFactorMaxInput = document.getElementById('impactFactorMaxInput');

        if (yearFromInput) yearFromInput.value = this.filters.yearRange[0];
        if (yearToInput) yearToInput.value = this.filters.yearRange[1];
        if (citationsMinInput) citationsMinInput.value = this.filters.citationsRange[0];
        if (citationsMaxInput) citationsMaxInput.value = this.filters.citationsRange[1];
        if (impactFactorMinInput) impactFactorMinInput.value = this.filters.impactFactorRange[0].toFixed(1);
        if (impactFactorMaxInput) impactFactorMaxInput.value = this.filters.impactFactorRange[1].toFixed(1);

        // Submit the form to trigger a new search with updated filters
        form.dispatchEvent(new Event('submit'));
    },

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml: function(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Clear all swarm plots
     */
    clear: function() {
        ['yearSwarmPlot', 'citationsSwarmPlot', 'impactFactorSwarmPlot'].forEach(id => {
            const elem = document.getElementById(id);
            if (elem) {
                Plotly.purge(elem);
                elem.remove();
            }
        });
        console.log('[Swarm Plots] Cleared');
    }
};

// Make globally available
window.SwarmPlots = SwarmPlots;

console.log('[Swarm Plots] Module loaded (Plotly.js version)');
