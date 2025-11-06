/**

 * SciTeX Unified Search Implementation
 *
 * This file implements the unified search system for SciTeX Scholar that aggregates
 * results from multiple academic sources (PubMed, Google Scholar, arXiv, Semantic Scholar)
 * and the SciTeX Index. Results are deduplicated, merged, and ranked intelligently.
 *
 * @version 1.0.0
 */
declare global {
    interface Window {
        SCHOLAR_CONFIG?: {
            urls?: {
                search?: string;
            };
        };
    }
}
/**
 * Search result interface
 */
interface SearchResult {
    id?: string;
    title?: string;
    authors?: string;
    year?: string | number;
    journal?: string;
    abstract?: string;
    citations?: number;
    pmid?: string;
    doi?: string;
    arxivId?: string;
    externalUrl?: string;
    source?: string;
    pdf_url?: string;
    is_open_access?: boolean;
    impact_factor?: number | string;
}
/**
 * Source configuration
 */
interface SourceConfig {
    name: string;
    endpoint: string;
    maxResults: number;
}
/**
 * Start unified search across all sources
 */
declare function startUnifiedSearch(query: string): void;
/**
 * Search a single source
 */
declare function searchSource(source: SourceConfig, query: string): void;
/**
 * Add a result to the progressive results container
 */
declare function addResultToProgressive(result: SearchResult): void;
/**
 * Create a result card element
 */
declare function createResultCard(result: SearchResult): HTMLElement;
/**
 * Handle search error
 */
declare function handleSearchError(sourceName: string, errorMessage: string): void;
/**
 * Reset progress indicators
 */
declare function resetProgressIndicators(): void;
//# sourceMappingURL=scitex-search.d.ts.map