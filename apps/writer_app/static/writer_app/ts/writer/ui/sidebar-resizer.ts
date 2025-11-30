/**
 * Sidebar Resizer Module
 * Handles the resizable sidebar functionality
 *
 * Supports two resize methods:
 * 1. Dragging the dedicated resizer handle
 * 2. Ctrl+drag anywhere in the file tree area
 */

console.log(
  "[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/writer/ui/sidebar-resizer.ts loaded"
);

const STORAGE_KEY = "scitex-writer-sidebar-width";
const MIN_WIDTH = 200;
const MAX_WIDTH = 600;
const DEFAULT_WIDTH = 280;

// Module-level state for resize operations
let isResizing = false;
let startX = 0;
let startWidth = 0;
let sidebarElement: HTMLElement | null = null;

/**
 * Start resize operation
 */
const startResize = (e: MouseEvent, sidebar: HTMLElement): void => {
  isResizing = true;
  sidebarElement = sidebar;
  startX = e.clientX;
  startWidth = sidebar.getBoundingClientRect().width;
  document.body.style.cursor = "col-resize";
  document.body.style.userSelect = "none";
  e.preventDefault();
};

/**
 * Handle mouse move during resize
 */
const handleMouseMove = (e: MouseEvent): void => {
  if (!isResizing || !sidebarElement) return;

  const delta = e.clientX - startX;
  const newWidth = Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, startWidth + delta));
  sidebarElement.style.width = `${newWidth}px`;
};

/**
 * End resize operation
 */
const handleMouseUp = (): void => {
  if (isResizing && sidebarElement) {
    isResizing = false;
    document.body.style.cursor = "";
    document.body.style.userSelect = "";

    // Save width to localStorage
    const width = sidebarElement.getBoundingClientRect().width;
    localStorage.setItem(STORAGE_KEY, width.toString());
    console.log("[SidebarResizer] Saved width:", width);
    sidebarElement = null;
  }
};

/**
 * Initialize the sidebar resizer
 */
export const initSidebarResizer = (): void => {
  console.log("[SidebarResizer] Initializing...");
  const resizer = document.getElementById("sidebar-resizer");
  const sidebar = document.getElementById("writer-sidebar");
  const fileTree = document.getElementById("writer-file-tree");

  console.log("[SidebarResizer] Elements found:", {
    resizer: !!resizer,
    sidebar: !!sidebar,
    fileTree: !!fileTree
  });

  if (!sidebar) {
    console.warn("[SidebarResizer] Sidebar not found, skipping initialization");
    return;
  }

  // Method 1: Dedicated resizer handle
  if (resizer) {
    resizer.addEventListener("mousedown", (e: MouseEvent) => {
      startResize(e, sidebar);
    });
  }

  // Method 2: Ctrl+drag on file tree
  if (fileTree) {
    fileTree.addEventListener("mousedown", (e: MouseEvent) => {
      if (e.ctrlKey || e.metaKey) {
        console.log("[SidebarResizer] Ctrl+drag resize started");
        startResize(e, sidebar);
      }
    });

    // Change cursor when Ctrl is held over file tree
    fileTree.addEventListener("mousemove", (e: MouseEvent) => {
      if (!isResizing && (e.ctrlKey || e.metaKey)) {
        fileTree.style.cursor = "col-resize";
      } else if (!isResizing) {
        fileTree.style.cursor = "";
      }
    });

    fileTree.addEventListener("mouseleave", () => {
      if (!isResizing) {
        fileTree.style.cursor = "";
      }
    });
  }

  // Global mouse move and up handlers
  document.addEventListener("mousemove", handleMouseMove);
  document.addEventListener("mouseup", handleMouseUp);

  // Restore saved width
  const savedWidth = localStorage.getItem(STORAGE_KEY);
  if (savedWidth) {
    const width = parseInt(savedWidth, 10);
    if (width >= MIN_WIDTH && width <= MAX_WIDTH) {
      sidebar.style.width = `${width}px`;
      console.log("[SidebarResizer] Restored width:", width);
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
