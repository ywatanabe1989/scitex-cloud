/**
 * Writer Module Index
 * Central export for all writer-related functionality extracted from index.ts
 *
 * This module coordinates the refactored components:
 * - Compilation: Progress UI, status, and log management
 * - Sections: Section loading, switching, management, and operations
 * - UI: Panel switching and navigation
 * - Listeners: Event handlers for editor and UI interactions
 * - Files: File loading operations
 * - Downloads: PDF and citation download handlers
 * - Initialization: Component initialization and event handler setup
 */

// Compilation module
export * from "./compilation/index.js";

// Initialization modules
export { ComponentInitializer, EventHandlerSetup } from "./initialization/index.js";
export type { InitializedComponents } from "./initialization/index.js";

// Section modules
export { SectionManagement } from "./sections/SectionManagement.js";
export {
  loadSectionContent,
  switchSection,
  updateSectionUI,
  loadCompiledPDF,
  setPdfPreviewManager as setSectionOpsPdfPreviewManager,
  clearCompileTimeout,
} from "./sections/SectionOperations.js";

// UI modules
export { PanelSwitcher } from "./ui/PanelSwitcher.js";

// Listener modules
export { EditorListeners } from "./listeners/EditorListeners.js";

// File modules
export { loadTexFile } from "./files/FileLoader.js";

// Download modules
export {
  handleDownloadFullPDF,
  handleDownloadCurrentPDF,
  handleDownloadCitationsBibTeX,
  handleDownloadSectionPDF,
  setPdfPreviewManager as setDownloadPdfPreviewManager,
} from "./downloads/DownloadHandlers.js";
