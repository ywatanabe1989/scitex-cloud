/**
 * Writer Shared State Module
 * Holds shared state/variables that need to be accessed across modules
 */

/**
 * Shared timeout for auto-compilation
 * Needs to be shared between writer-compilation.js and writer-sections.js
 */
export let compileTimeout;

/**
 * Set the compile timeout
 */
export function setCompileTimeout(timeout) {
    compileTimeout = timeout;
}

/**
 * Clear the compile timeout
 */
export function clearCompileTimeout() {
    if (compileTimeout !== undefined) {
        console.log('[WriterShared] Clearing auto-compile timeout:', compileTimeout);
        clearTimeout(compileTimeout);
        compileTimeout = undefined;
    } else {
        console.log('[WriterShared] No pending auto-compile timeout to clear');
    }
}

/**
 * Shared timeout for auto-save
 */
export let saveTimeout;

/**
 * Set the save timeout
 */
export function setSaveTimeout(timeout) {
    saveTimeout = timeout;
}

/**
 * Clear the save timeout
 */
export function clearSaveTimeout() {
    clearTimeout(saveTimeout);
    saveTimeout = undefined;
}
