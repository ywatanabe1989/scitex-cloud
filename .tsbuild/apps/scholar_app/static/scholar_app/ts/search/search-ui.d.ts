/**

 * Search UI Module
 *
 * Handles search result UI interactions:
 * - Toggle abstract display modes (all/truncated/none)
 * - Sort results by different criteria
 * - Client-side result manipulation
 *
 * @module search/search-ui
 */
declare global {
    interface Window {
        toggleAbstractMode: (button: HTMLElement, paperId: string, mode: string) => void;
        handleSortChange: (sortBy: string) => void;
    }
}
type AbstractMode = 'all' | 'truncated' | 'none';
type SortOption = 'date_desc' | 'date_asc' | 'citations' | 'impact_factor';
/**
 * Toggle abstract display mode for a paper
 *
 * @param {HTMLElement} button - The toggle button clicked
 * @param {string} paperId - The paper ID
 * @param {AbstractMode} mode - The mode to switch to: 'all', 'truncated', or 'none'
 */
declare function toggleAbstractMode(button: HTMLElement, paperId: string, mode: AbstractMode): void;
/**
 * Handle sort option changes for search results
 *
 * @param {SortOption} sortBy - The sort option value
 */
declare function handleSortChange(sortBy: SortOption): void;
/**
 * Get all paper URLs from search results
 *
 * @returns {string[]} Array of paper URLs
 */
declare function getAllPaperUrls(): string[];
/**
 * Open all paper URLs in new tabs
 * Note: Browser may block multiple tabs, user needs to allow popups
 */
declare function openAllPaperUrls(): void;
/**
 * Initialize search UI
 */
declare function initSearchUI(): void;
export { toggleAbstractMode, handleSortChange, getAllPaperUrls, openAllPaperUrls, initSearchUI, };
//# sourceMappingURL=search-ui.d.ts.map