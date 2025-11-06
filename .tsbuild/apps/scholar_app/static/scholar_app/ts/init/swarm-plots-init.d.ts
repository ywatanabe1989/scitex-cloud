/**

 * SwarmPlots Initialization Module
 *
 * Handles initialization of SwarmPlots visualization when search results are available.
 * This module waits for both DOM ready and SwarmPlots module availability before initializing.
 *
 * @module init/swarm-plots-init
 */
declare global {
    interface Window {
        SCHOLAR_SEARCH_RESULTS?: Array<{
            title: string;
            year: number | null;
            citations: number;
            impact_factor: number | null;
            authors: string;
            journal: string;
            url: string;
        }>;
        SwarmPlots?: {
            init: (data: any[]) => void;
        };
    }
}
/**
 * Initialize swarm plots with retry mechanism
 *
 * @param {number} maxRetries - Maximum number of retry attempts (default: 3)
 * @param {number} retryDelay - Delay between retries in milliseconds (default: 500)
 */
declare function initializeSwarmPlots(maxRetries?: number, retryDelay?: number): void;
export { initializeSwarmPlots };
//# sourceMappingURL=swarm-plots-init.d.ts.map