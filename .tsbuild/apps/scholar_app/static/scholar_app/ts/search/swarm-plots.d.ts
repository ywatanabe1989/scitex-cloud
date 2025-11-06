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
declare const SwarmPlots: {
    config: SwarmConfig;
    data: PaperData[];
    filteredIndices: Set<number>;
    /**
     * Initialize swarm plots with paper data
     */
    init: (papers: PaperData[]) => void;
    /**
     * Create year distribution swarm plot
     */
    createYearSwarmPlot: () => void;
    /**
     * Create citations distribution swarm plot
     */
    createCitationsSwarmPlot: () => void;
    /**
     * Create impact factor distribution swarm plot
     */
    createImpactFactorSwarmPlot: () => void;
    /**
     * Update plots when filters change
     */
    updateFilter: (yearRange: [number, number] | null, citationsRange: [number, number] | null, impactRange: [number, number] | null) => void;
    /**
     * Reset all filters
     */
    resetFilters: () => void;
};
//# sourceMappingURL=swarm-plots.d.ts.map