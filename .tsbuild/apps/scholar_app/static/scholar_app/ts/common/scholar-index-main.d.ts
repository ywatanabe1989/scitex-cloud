/**

 * SciTeX Scholar Main Index - Core Functionality
 *
 * This is the main entry point for the Scholar app, handling search, filters, results display,
 * source selection, BibTeX management, and all core user interactions.
 *
 * @version 1.0.0
 */
declare global {
    interface Window {
        _scholarSortInitialized?: boolean;
        scholarConfig?: {
            user?: {
                isAuthenticated?: boolean;
            };
        };
        SCHOLAR_CONFIG?: {
            urls?: {
                bibtexUpload?: string;
                resourceStatus?: string;
            };
        };
    }
}
//# sourceMappingURL=scholar-index-main.d.ts.map