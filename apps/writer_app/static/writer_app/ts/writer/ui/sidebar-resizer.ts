/**
 * Sidebar Resizer Module
 * Handles the resizable sidebar functionality
 */

console.log(
  "[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/writer/ui/sidebar-resizer.ts loaded"
);

const STORAGE_KEY = "scitex-writer-sidebar-width";
const MIN_WIDTH = 200;
const MAX_WIDTH = 500;
const DEFAULT_WIDTH = 280;

/**
 * Initialize the sidebar resizer
 */
export const initSidebarResizer = (): void => {
  console.log("[SidebarResizer] Initializing...");
  const resizer = document.getElementById("sidebar-resizer");
  const sidebar = document.getElementById("writer-sidebar");

  console.log("[SidebarResizer] Elements found:", { resizer: !!resizer, sidebar: !!sidebar });

  if (!resizer || !sidebar) {
    console.warn("[SidebarResizer] Required elements not found, skipping initialization");
    return;
  }

  let isResizing = false;
  let startX = 0;
  let startWidth = 0;

  resizer.addEventListener("mousedown", (e: MouseEvent) => {
    isResizing = true;
    startX = e.clientX;
    startWidth = sidebar.getBoundingClientRect().width;
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  });

  document.addEventListener("mousemove", (e: MouseEvent) => {
    if (!isResizing) return;

    const delta = e.clientX - startX;
    const newWidth = Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, startWidth + delta));
    sidebar.style.width = `${newWidth}px`;
  });

  document.addEventListener("mouseup", () => {
    if (isResizing) {
      isResizing = false;
      document.body.style.cursor = "";
      document.body.style.userSelect = "";

      // Save width to localStorage
      const width = sidebar.getBoundingClientRect().width;
      localStorage.setItem(STORAGE_KEY, width.toString());
    }
  });

  // Restore saved width
  const savedWidth = localStorage.getItem(STORAGE_KEY);
  if (savedWidth) {
    const width = parseInt(savedWidth, 10);
    if (width >= MIN_WIDTH && width <= MAX_WIDTH) {
      sidebar.style.width = `${width}px`;
    }
  }
};

/**
 * Get current sidebar width
 */
export const getSidebarWidth = (): number => {
  const sidebar = document.getElementById("writer-sidebar");
  if (!sidebar) return DEFAULT_WIDTH;
  return sidebar.getBoundingClientRect().width;
};

/**
 * Set sidebar width programmatically
 */
export const setSidebarWidth = (width: number): void => {
  const sidebar = document.getElementById("writer-sidebar");
  if (!sidebar) return;

  const clampedWidth = Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, width));
  sidebar.style.width = `${clampedWidth}px`;
  localStorage.setItem(STORAGE_KEY, clampedWidth.toString());
};

// Auto-initialize when DOM is ready
// This ensures the resizer works even if initSidebarResizer() is not explicitly called
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initSidebarResizer);
} else {
  // DOM already loaded, initialize immediately
  initSidebarResizer();
}
