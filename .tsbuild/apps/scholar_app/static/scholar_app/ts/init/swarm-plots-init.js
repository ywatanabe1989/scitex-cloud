/**

 * SwarmPlots Initialization Module
 *
 * Handles initialization of SwarmPlots visualization when search results are available.
 * This module waits for both DOM ready and SwarmPlots module availability before initializing.
 *
 * @module init/swarm-plots-init
 */
console.log("[DEBUG] apps/scholar_app/static/scholar_app/ts/init/swarm-plots-init.ts loaded");
/**
 * Initialize swarm plots with retry mechanism
 *
 * @param {number} maxRetries - Maximum number of retry attempts (default: 3)
 * @param {number} retryDelay - Delay between retries in milliseconds (default: 500)
 */
function initializeSwarmPlots(maxRetries = 3, retryDelay = 500) {
    console.log('[Swarm Plots Init] Starting initialization...');
    // Check if search results are available
    if (!window.SCHOLAR_SEARCH_RESULTS || window.SCHOLAR_SEARCH_RESULTS.length === 0) {
        console.log('[Swarm Plots Init] No search results available, skipping initialization');
        return;
    }
    console.log('[Swarm Plots Init] Found', window.SCHOLAR_SEARCH_RESULTS.length, 'search results');
    let attempt = 0;
    function attemptInit() {
        attempt++;
        console.log(`[Swarm Plots Init] Attempt ${attempt}/${maxRetries}`);
        if (window.SwarmPlots && typeof window.SwarmPlots.init === 'function') {
            console.log('[Swarm Plots Init] SwarmPlots module found, initializing...');
            try {
                window.SwarmPlots.init(window.SCHOLAR_SEARCH_RESULTS);
                console.log('[Swarm Plots Init] Successfully initialized swarm plots');
            }
            catch (error) {
                console.error('[Swarm Plots Init] Error during initialization:', error);
            }
        }
        else if (attempt < maxRetries) {
            console.log('[Swarm Plots Init] SwarmPlots module not yet available, retrying...');
            setTimeout(attemptInit, retryDelay);
        }
        else {
            console.warn('[Swarm Plots Init] SwarmPlots module not available after', maxRetries, 'attempts');
        }
    }
    attemptInit();
}
/**
 * Initialize when DOM is ready
 */
function onDOMReady() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => initializeSwarmPlots());
    }
    else {
        // DOM already loaded
        initializeSwarmPlots();
    }
}
// Auto-initialize when script loads
onDOMReady();
// Export for manual initialization if needed
export { initializeSwarmPlots };
//# sourceMappingURL=swarm-plots-init.js.map