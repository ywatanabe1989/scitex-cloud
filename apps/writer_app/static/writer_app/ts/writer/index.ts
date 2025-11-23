/**
 * Writer Module Index
 * Central export for all writer-related functionality extracted from index.ts
 *
 * This module coordinates the refactored components:
 * - Compilation: Progress UI, status, and log management
 * - Sections: Section loading, switching, and UI management
 * - Initialization: Workspace setup and editor initialization
 * - PDF: PDF loading and preview management
 * - Listeners: Event handlers for various UI interactions
 */

// Compilation module
export * from "./compilation/index.js";

// Note: Other modules (sections, initialization, pdf, listeners) will be added
// as they are extracted from the main index.ts file
