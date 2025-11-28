/**
 * Repository Admin Maintenance Module
 * Entry point for repository health monitoring and maintenance operations
 * @module repository/admin
 */

// Export types
export type {
  HealthStats,
  RepositoryIssue,
  HealthData,
  PendingAction,
  FilterType,
} from "./types.js";

// Export UI functions
export {
  escapeHtml,
  renderHealthStatus,
  renderIssue,
  renderIssues,
  applyFilter,
  showDialog,
  closeDialog,
  showError,
  getCSRFToken,
} from "./ui.js";

// Export cleanup operations
export { confirmDelete, deleteRepository } from "./cleanup.js";

// Export backup/restore operations
export {
  confirmRestore,
  getRestoreProjectName,
  restoreRepository,
} from "./backup.js";

// Export main maintenance functionality
export { initializeRepositoryMaintenance } from "./maintenance.js";

// Re-export for backwards compatibility
import { initializeRepositoryMaintenance } from "./maintenance.js";

// Auto-initialize when imported
initializeRepositoryMaintenance();

console.log(
  "[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/project_app/static/project_app/ts/repository/admin/index.ts loaded",
);
