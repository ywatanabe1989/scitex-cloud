/**
 * Resize Handler for WorkspaceFilesTree
 * Allows resizing the file tree height with Ctrl+drag (vertical)
 *
 * Usage: Hold Ctrl (or Cmd on Mac) and drag vertically to resize the tree height
 */

console.log('[DEBUG] ResizeHandler.ts loaded');

const STORAGE_KEY_PREFIX = 'scitex-tree-height-';
const MIN_HEIGHT = 150;
const MAX_HEIGHT = 800;
const DEFAULT_HEIGHT = 400;

export class ResizeHandler {
  private container: HTMLElement;
  private storageKey: string;
  private isResizing = false;
  private startY = 0;
  private startHeight = 0;

  // Bound handlers for proper cleanup
  private boundMouseMove: (e: MouseEvent) => void;
  private boundMouseUp: () => void;
  private boundMouseDown: (e: MouseEvent) => void;
  private boundContainerMouseMove: (e: MouseEvent) => void;
  private boundContainerMouseLeave: () => void;

  constructor(container: HTMLElement, mode: string) {
    this.container = container;
    this.storageKey = `${STORAGE_KEY_PREFIX}${mode}`;

    // Bind handlers
    this.boundMouseMove = this.handleMouseMove.bind(this);
    this.boundMouseUp = this.handleMouseUp.bind(this);
    this.boundMouseDown = this.handleMouseDown.bind(this);
    this.boundContainerMouseMove = this.handleContainerMouseMove.bind(this);
    this.boundContainerMouseLeave = this.handleContainerMouseLeave.bind(this);
  }

  /**
   * Initialize the resize functionality
   */
  initialize(): void {
    // Restore saved height
    this.restoreHeight();

    // Attach event listeners
    this.container.addEventListener('mousedown', this.boundMouseDown);
    this.container.addEventListener('mousemove', this.boundContainerMouseMove);
    this.container.addEventListener('mouseleave', this.boundContainerMouseLeave);

    // Global listeners for tracking mouse during resize
    document.addEventListener('mousemove', this.boundMouseMove);
    document.addEventListener('mouseup', this.boundMouseUp);

    console.log('[ResizeHandler] Initialized - Ctrl+drag to resize tree height');
  }

  /**
   * Clean up event listeners
   */
  destroy(): void {
    this.container.removeEventListener('mousedown', this.boundMouseDown);
    this.container.removeEventListener('mousemove', this.boundContainerMouseMove);
    this.container.removeEventListener('mouseleave', this.boundContainerMouseLeave);
    document.removeEventListener('mousemove', this.boundMouseMove);
    document.removeEventListener('mouseup', this.boundMouseUp);
  }

  /**
   * Handle mousedown - start resize if Ctrl is held
   */
  private handleMouseDown(e: MouseEvent): void {
    if (e.ctrlKey || e.metaKey) {
      this.startResize(e);
    }
  }

  /**
   * Start resize operation
   */
  private startResize(e: MouseEvent): void {
    this.isResizing = true;
    this.startY = e.clientY;
    this.startHeight = this.container.getBoundingClientRect().height;
    document.body.style.cursor = 'row-resize';
    document.body.style.userSelect = 'none';
    e.preventDefault();
    e.stopPropagation();
    console.log('[ResizeHandler] Resize started');
  }

  /**
   * Handle mouse move during resize
   */
  private handleMouseMove(e: MouseEvent): void {
    if (!this.isResizing) return;

    const delta = e.clientY - this.startY;
    const newHeight = Math.max(MIN_HEIGHT, Math.min(MAX_HEIGHT, this.startHeight + delta));
    this.setHeight(newHeight);
  }

  /**
   * Handle mouse up - end resize
   */
  private handleMouseUp(): void {
    if (this.isResizing) {
      this.isResizing = false;
      document.body.style.cursor = '';
      document.body.style.userSelect = '';

      // Save height to localStorage
      const height = this.container.getBoundingClientRect().height;
      localStorage.setItem(this.storageKey, height.toString());
      console.log('[ResizeHandler] Saved height:', height);
    }
  }

  /**
   * Handle mouse move on container - change cursor when Ctrl held
   */
  private handleContainerMouseMove(e: MouseEvent): void {
    if (!this.isResizing && (e.ctrlKey || e.metaKey)) {
      this.container.style.cursor = 'row-resize';
    } else if (!this.isResizing) {
      this.container.style.cursor = '';
    }
  }

  /**
   * Handle mouse leave - reset cursor
   */
  private handleContainerMouseLeave(): void {
    if (!this.isResizing) {
      this.container.style.cursor = '';
    }
  }

  /**
   * Set the container height
   */
  private setHeight(height: number): void {
    this.container.style.height = `${height}px`;
    this.container.style.maxHeight = `${height}px`;
    this.container.style.minHeight = `${height}px`;
  }

  /**
   * Restore saved height from localStorage
   */
  private restoreHeight(): void {
    const savedHeight = localStorage.getItem(this.storageKey);
    if (savedHeight) {
      const height = parseInt(savedHeight, 10);
      if (height >= MIN_HEIGHT && height <= MAX_HEIGHT) {
        this.setHeight(height);
        console.log('[ResizeHandler] Restored height:', height);
      }
    }
  }

  /**
   * Get current height
   */
  getHeight(): number {
    return this.container.getBoundingClientRect().height;
  }

  /**
   * Set height programmatically
   */
  setHeightProgrammatic(height: number): void {
    const clampedHeight = Math.max(MIN_HEIGHT, Math.min(MAX_HEIGHT, height));
    this.setHeight(clampedHeight);
    localStorage.setItem(this.storageKey, clampedHeight.toString());
  }
}
