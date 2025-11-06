/**

 * Swarm Plot Visualization for SciTeX Scholar Filters
 *
 * Creates interactive swarm plots using Plotly.js to visualize the distribution of papers
 * across Year, Citations, and Impact Factor dimensions. Helps users understand their
 * search results visually and identify outliers or clusters.
 *
 * External library: Plotly.js (requires `any` types or @ts-ignore)
 *
 * @version 1.0.0
 */

// @ts-ignore - Plotly library types

console.log("[DEBUG] apps/scholar_app/static/scholar_app/ts/search/swarm-plots.ts loaded");
declare const Plotly: any;

/**
 * Paper data interface
 */
interface PaperData {
    id?: string;
    title?: string;
    year?: number;
    citations?: number;
    impact_factor?: number;
    journal?: string;
    authors?: string;
}

/**
 * Swarm plot configuration
 */
interface SwarmConfig {
    height: number;
    includedColor: string;
    filteredColor: string;
    pointSize: number;
    hovertemplate: string;
}

/**
 * Swarm Plots module using object literal pattern
 */
const SwarmPlots = {
    config: {
        height: 100,
        includedColor: '#3b82f6',
        filteredColor: '#d1d5db',
        pointSize: 8,
        hovertemplate: '%{text}<extra></extra>'
    } as SwarmConfig,

    data: [] as PaperData[],
    filteredIndices: new Set<number>(),

    /**
     * Initialize swarm plots with paper data
     */
    init: function(papers: PaperData[]): void {
        console.log('[SwarmPlots] Initializing with', papers.length, 'papers');
        this.data = papers;
        this.filteredIndices.clear();

        // Create plots if Plotly is available
        if (typeof Plotly === 'undefined') {
            console.warn('[SwarmPlots] Plotly.js not loaded, skipping visualization');
            return;
        }

        this.createYearSwarmPlot();
        this.createCitationsSwarmPlot();
        this.createImpactFactorSwarmPlot();
    },

    /**
     * Create year distribution swarm plot
     */
    createYearSwarmPlot: function(): void {
        const container = document.getElementById('yearSwarmPlot') as HTMLElement | null;
        if (!container) return;

        const years = this.data.map(p => p.year || 0);
        const colors = this.data.map((_, idx) =>
            this.filteredIndices.has(idx) ? this.config.filteredColor : this.config.includedColor
        );
        const texts = this.data.map(p => p.title || 'Unknown');

        const trace = {
            type: 'scatter',
            mode: 'markers',
            x: years,
            y: years.map(() => Math.random() * 0.8 + 0.1), // Jitter for swarm effect
            marker: {
                size: this.config.pointSize,
                color: colors,
                line: { width: 1, color: '#fff' }
            },
            text: texts,
            hovertemplate: this.config.hovertemplate,
            showlegend: false
        };

        const layout = {
            height: this.config.height,
            margin: { l: 40, r: 20, t: 10, b: 30 },
            xaxis: { title: 'Year' },
            yaxis: { visible: false, range: [0, 1] },
            hovermode: 'closest'
        };

        // @ts-ignore - Plotly library
        Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false });
        console.log('[SwarmPlots] Year swarm plot created');
    },

    /**
     * Create citations distribution swarm plot
     */
    createCitationsSwarmPlot: function(): void {
        const container = document.getElementById('citationsSwarmPlot') as HTMLElement | null;
        if (!container) return;

        const citations = this.data.map(p => p.citations || 0);
        const colors = this.data.map((_, idx) =>
            this.filteredIndices.has(idx) ? this.config.filteredColor : this.config.includedColor
        );
        const texts = this.data.map(p => p.title || 'Unknown');

        const trace = {
            type: 'scatter',
            mode: 'markers',
            x: citations,
            y: citations.map(() => Math.random() * 0.8 + 0.1),
            marker: {
                size: this.config.pointSize,
                color: colors,
                line: { width: 1, color: '#fff' }
            },
            text: texts,
            hovertemplate: this.config.hovertemplate,
            showlegend: false
        };

        const layout = {
            height: this.config.height,
            margin: { l: 40, r: 20, t: 10, b: 30 },
            xaxis: { title: 'Citations', type: 'log' },
            yaxis: { visible: false, range: [0, 1] },
            hovermode: 'closest'
        };

        // @ts-ignore - Plotly library
        Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false });
        console.log('[SwarmPlots] Citations swarm plot created');
    },

    /**
     * Create impact factor distribution swarm plot
     */
    createImpactFactorSwarmPlot: function(): void {
        const container = document.getElementById('impactFactorSwarmPlot') as HTMLElement | null;
        if (!container) return;

        const impactFactors = this.data.map(p => p.impact_factor || 0);
        const colors = this.data.map((_, idx) =>
            this.filteredIndices.has(idx) ? this.config.filteredColor : this.config.includedColor
        );
        const texts = this.data.map(p => p.title || 'Unknown');

        const trace = {
            type: 'scatter',
            mode: 'markers',
            x: impactFactors,
            y: impactFactors.map(() => Math.random() * 0.8 + 0.1),
            marker: {
                size: this.config.pointSize,
                color: colors,
                line: { width: 1, color: '#fff' }
            },
            text: texts,
            hovertemplate: this.config.hovertemplate,
            showlegend: false
        };

        const layout = {
            height: this.config.height,
            margin: { l: 40, r: 20, t: 10, b: 30 },
            xaxis: { title: 'Impact Factor' },
            yaxis: { visible: false, range: [0, 1] },
            hovermode: 'closest'
        };

        // @ts-ignore - Plotly library
        Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false });
        console.log('[SwarmPlots] Impact Factor swarm plot created');
    },

    /**
     * Update plots when filters change
     */
    updateFilter: function(yearRange: [number, number] | null, citationsRange: [number, number] | null, impactRange: [number, number] | null): void {
        this.filteredIndices.clear();

        this.data.forEach((paper, idx) => {
            let filtered = false;

            // Year filter
            if (yearRange && paper.year) {
                if (paper.year < yearRange[0] || paper.year > yearRange[1]) {
                    filtered = true;
                }
            }

            // Citations filter
            if (citationsRange && paper.citations !== undefined) {
                if (paper.citations < citationsRange[0] || paper.citations > citationsRange[1]) {
                    filtered = true;
                }
            }

            // Impact factor filter
            if (impactRange && paper.impact_factor !== undefined) {
                if (paper.impact_factor < impactRange[0] || paper.impact_factor > impactRange[1]) {
                    filtered = true;
                }
            }

            if (filtered) {
                this.filteredIndices.add(idx);
            }
        });

        // Re-render all plots
        this.createYearSwarmPlot();
        this.createCitationsSwarmPlot();
        this.createImpactFactorSwarmPlot();

        console.log('[SwarmPlots] Filters updated,', this.filteredIndices.size, 'papers filtered out');
    },

    /**
     * Reset all filters
     */
    resetFilters: function(): void {
        this.filteredIndices.clear();
        this.createYearSwarmPlot();
        this.createCitationsSwarmPlot();
        this.createImpactFactorSwarmPlot();
        console.log('[SwarmPlots] Filters reset');
    }
};

// Expose to global scope
(window as any).SwarmPlots = SwarmPlots;

// Auto-initialize if paper data is available
document.addEventListener('DOMContentLoaded', function() {
    // Check if paper data is available from the page
    const paperDataElement = document.getElementById('paperData') as HTMLElement | null;
    if (paperDataElement && paperDataElement.textContent) {
        try {
            const papers = JSON.parse(paperDataElement.textContent) as PaperData[];
            SwarmPlots.init(papers);
        } catch (e: any) {
            console.warn('[SwarmPlots] Failed to parse paper data:', e.message);
        }
    }
});
