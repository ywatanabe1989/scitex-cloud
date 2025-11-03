/**
 * SciTeX Writer Application
 * Main entry point for the writer interface
 *
 * This module coordinates all writer modules:
 * - writer-init: Editor initialization and workspace setup
 * - writer-sections: Section switching and management
 * - writer-pdf: PDF rendering and zoom controls
 * - writer-compilation: LaTeX compilation and auto-compile
 * - writer-storage: Section saving and auto-save
 * - writer-ui: UI updates and theme management
 * - writer-events: Event listeners for editor and sections
 * - writer-git: Git commit operations
 */

import { getWriterConfig } from './helpers.js';
import { initializeEditor, setupWorkspaceInitialization, populateSectionDropdownDirect } from './writer-init.js';

/**
 * Initialize application
 */
document.addEventListener('DOMContentLoaded', async () => {
    console.log('[Writer] Initializing application');

    const config = getWriterConfig();
    console.log('[Writer] Config:', config);

    // Check if workspace is initialized
    if (!config.writerInitialized && !config.isDemo) {
        console.log('[Writer] Workspace not initialized - skipping editor setup');
        setupWorkspaceInitialization(config);
        return;
    }

    // Initialize editor components (async to wait for Monaco)
    await initializeEditor(config);
});

// Export functions to global scope for ES6 module compatibility
window.populateSectionDropdownDirect = populateSectionDropdownDirect;
