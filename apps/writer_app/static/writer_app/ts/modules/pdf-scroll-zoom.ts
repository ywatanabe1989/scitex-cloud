/**
 * PDF Scroll and Zoom Handler
 * Provides native PDF viewer-like interaction:
 * - Mouse wheel scrolling within PDF (doesn't scroll page)
 * - Ctrl+drag for zoom with cursor centering
 * - Zoom level indicator and controls
 */

console.log(
  "[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/modules/pdf-scroll-zoom.ts loaded",
);

import { statePersistence } from "./state-persistence.js";

export interface PDFScrollZoomOptions {
  containerId: string;
  minZoom?: number;
  maxZoom?: number;
  zoomStep?: number;
}

type PDFColorMode = "light" | "dark";

export interface PDFColorTheme {
  name: string;
  label: string;
  filter: string;
  backgroundColor: string;
}

const PDF_COLOR_THEMES: Record<PDFColorMode, PDFColorTheme> = {
  light: {
    name: "light",
    label: "Light",
    filter: "none",
    backgroundColor: "#ffffff",
  },
  dark: {
    name: "dark",
    label: "Dark",
    filter: "none", // No filter - colors handled by LaTeX compilation
    backgroundColor: "#1a1a1a",
  },
};

export class PDFScrollZoomHandler {
  private container: HTMLElement | null;
  private pdfViewer: HTMLElement | null = null;
  private currentZoom: number = 125; // Default to 125% for better readability
  private minZoom: number = 50;
  private maxZoom: number = 300;
  private zoomStep: number = 10;
  private isCtrlPressed: boolean = false;
  private isSpacePressed: boolean = false;
  private isDraggingZoom: boolean = false;
  private isPanning: boolean = false;
  private dragStartX: number = 0;
  private dragStartY: number = 0;
  private dragStartZoom: number = 125;
  private panStartScrollTop: number = 0;
  private panStartScrollLeft: number = 0;
  private originalOverflow: string = "";
  private originalCursor: string = "";
  private colorMode: PDFColorMode = "light";
  private onColorModeChangeCallback?: (colorMode: PDFColorMode) => void;
  private scrollSaveTimeout: number | null = null;
  private isWaitingForCommand: boolean = false;
  private commandTimeout: number | null = null;
  private currentMode: "text" | "hand" | "zoom" = "text"; // Default to text selection mode

  constructor(options: PDFScrollZoomOptions) {
    this.container = document.getElementById(options.containerId);
    this.minZoom = options.minZoom || 50;
    this.maxZoom = options.maxZoom || 300;
    this.zoomStep = options.zoomStep || 10;

    console.log(
      "[PDFScrollZoom] Constructor called, containerId:",
      options.containerId,
    );
    console.log("[PDFScrollZoom] Container found:", !!this.container);

    if (this.container) {
      // Try to find existing PDF viewer immediately
      const existingViewer = this.container.querySelector(
        ".pdf-preview-viewer",
      );
      console.log(
        "[PDFScrollZoom] Existing PDF viewer found:",
        !!existingViewer,
      );
      if (existingViewer) {
        this.pdfViewer = existingViewer as HTMLElement;
        console.log("[PDFScrollZoom] Set pdfViewer reference on construction");
      }

      this.setupEventListeners();
    } else {
      console.warn("[PDFScrollZoom] Container not found!");
    }
  }

  /**
   * Setup all event listeners for scroll and zoom
   */
  private setupEventListeners(): void {
    if (!this.container) return;

    // Track Ctrl key state
    document.addEventListener("keydown", (e) => this.handleKeyDown(e));
    document.addEventListener("keyup", (e) => this.handleKeyUp(e));

    // Mouse wheel scrolling within PDF (use capture phase)
    this.container.addEventListener("wheel", (e) => this.handleWheel(e), true);

    // Also handle editor scrolling - find editor container and prioritize it
    const editorContainer = document.querySelector(".latex-panel");
    if (editorContainer) {
      editorContainer.addEventListener(
        "wheel",
        (e: any) => this.handleEditorWheel(e as WheelEvent),
        true,
      );
    }

    // Ctrl+drag for zoom
    document.addEventListener("mousedown", (e: any) =>
      this.handleMouseDown(e as MouseEvent),
    );
    document.addEventListener("mousemove", (e: any) =>
      this.handleMouseMove(e as MouseEvent),
    );
    document.addEventListener("mouseup", () => this.handleMouseUp());

    // Touch gestures for zoom (pinch)
    this.container.addEventListener(
      "touchstart",
      (e) => this.handleTouchStart(e),
      true,
    );
    this.container.addEventListener(
      "touchmove",
      (e) => this.handleTouchMove(e),
      true,
    );
    this.container.addEventListener(
      "touchend",
      (e) => this.handleTouchEnd(e),
      true,
    );

    // Setup mutation observer to detect PDF viewer changes
    this.setupMutationObserver();

    // Setup PDF zoom button controls
    this.setupZoomButtons();

    // Load saved zoom level
    this.loadSavedZoom();

    console.log("[PDFScrollZoom] Event listeners initialized");
  }

  /**
   * Setup PDF zoom dropdown control
   */
  private setupZoomButtons(): void {
    const zoomSelect = document.getElementById("pdf-zoom-select") as HTMLSelectElement;

    if (zoomSelect) {
      // Set initial value
      zoomSelect.value = this.currentZoom.toString();

      // Handle dropdown change
      zoomSelect.addEventListener("change", () => {
        const newZoom = parseInt(zoomSelect.value, 10);
        this.setZoom(newZoom);
        console.log(`[PDFScrollZoom] Zoom changed to ${newZoom}% via dropdown`);
      });

      console.log("[PDFScrollZoom] Zoom dropdown control initialized");
    } else {
      console.warn("[PDFScrollZoom] Zoom dropdown not found");
    }
  }

  /**
   * Load saved zoom level from state persistence
   * Applies zoom immediately to iframe if present
   */
  private loadSavedZoom(): void {
    const savedZoom = statePersistence.getSavedPdfZoom();
    if (savedZoom && savedZoom >= this.minZoom && savedZoom <= this.maxZoom) {
      this.currentZoom = savedZoom;

      // Update dropdown to reflect saved zoom
      const zoomSelect = document.getElementById("pdf-zoom-select") as HTMLSelectElement;
      if (zoomSelect) {
        zoomSelect.value = savedZoom.toString();
      }

      console.log("[PDFScrollZoom] Loaded saved zoom level:", savedZoom);
    } else {
      console.log("[PDFScrollZoom] No saved zoom or invalid value, using default:", this.currentZoom);
    }

    // Apply zoom immediately
    this.applyZoomToIframe();
  }

  /**
   * Apply current zoom level to iframe
   */
  private applyZoomToIframe(): void {
    console.log("[PDFScrollZoom] applyZoomToIframe() - checking for iframe...");

    if (!this.pdfViewer) {
      console.log("[PDFScrollZoom] ✗ No pdfViewer reference, cannot apply zoom");
      return;
    }

    const iframe = this.pdfViewer.querySelector("iframe, embed");
    if (iframe) {
      const scaleRatio = this.currentZoom / 100;
      console.log("[PDFScrollZoom] Found iframe/embed, applying scale:", scaleRatio);
      (iframe as HTMLElement).style.transform = `scale(${scaleRatio})`;
      (iframe as HTMLElement).style.transformOrigin = "top center";
      (iframe as HTMLElement).style.transition = "transform 0.2s ease";
      this.updateZoomIndicator();
      console.log("[PDFScrollZoom] ✓ Zoom applied successfully:", this.currentZoom + "%");
    } else {
      console.log("[PDFScrollZoom] ✗ No iframe/embed found in pdfViewer");
    }
  }

  /**
   * Restore saved PDF scroll position
   * Waits for iframe to load before restoring
   */
  private restoreSavedScrollPosition(): void {
    console.log("[PDFScrollZoom] ----------------------------------------");
    console.log("[PDFScrollZoom] restoreSavedScrollPosition() called");

    if (!this.pdfViewer) {
      console.log("[PDFScrollZoom] ✗ No pdfViewer reference, cannot restore");
      return;
    }

    const savedPosition = statePersistence.getSavedPdfScrollPosition();
    if (!savedPosition) {
      console.log("[PDFScrollZoom] No saved scroll position found");
      return;
    }

    console.log("[PDFScrollZoom] Found saved position:", savedPosition);

    const iframe = this.pdfViewer.querySelector("iframe");
    if (!iframe) {
      console.log("[PDFScrollZoom] ✗ No iframe found in pdfViewer");
      return;
    }

    console.log("[PDFScrollZoom] Found iframe, setting up restoration...");

    // Wait for iframe to fully load before restoring scroll position
    const restoreScroll = () => {
      console.log("[PDFScrollZoom] restoreScroll() function executing...");
      // Use multiple RAF calls to ensure PDF is fully rendered
      requestAnimationFrame(() => {
        console.log("[PDFScrollZoom] First RAF");
        requestAnimationFrame(() => {
          console.log("[PDFScrollZoom] Second RAF, applying scroll position...");
          if (this.pdfViewer) {
            this.pdfViewer.scrollTop = savedPosition.scrollTop;
            this.pdfViewer.scrollLeft = savedPosition.scrollLeft;
            console.log("[PDFScrollZoom] ✓ Scroll position SET to:", {
              scrollTop: this.pdfViewer.scrollTop,
              scrollLeft: this.pdfViewer.scrollLeft
            });
            console.log("[PDFScrollZoom] ✓ Successfully restored scroll position!");
          }
        });
      });
    };

    // If iframe already loaded, restore immediately
    if (iframe.contentDocument?.readyState === "complete") {
      console.log("[PDFScrollZoom] Iframe contentDocument.readyState = 'complete', restoring immediately");
      restoreScroll();
    } else {
      console.log("[PDFScrollZoom] Iframe not yet loaded, adding load event listener...");
      console.log("[PDFScrollZoom] Current readyState:", iframe.contentDocument?.readyState);
      // Wait for iframe to load
      iframe.addEventListener("load", () => {
        console.log("[PDFScrollZoom] ✓ Iframe 'load' event fired!");
        restoreScroll();
      }, { once: true });
    }
    console.log("[PDFScrollZoom] ----------------------------------------");
  }

  /**
   * Save current PDF scroll position (debounced)
   */
  private saveScrollPosition(): void {
    if (!this.pdfViewer) return;

    // Debounce to avoid excessive saves
    if (this.scrollSaveTimeout) {
      clearTimeout(this.scrollSaveTimeout);
    }

    this.scrollSaveTimeout = window.setTimeout(() => {
      if (this.pdfViewer) {
        const scrollTop = this.pdfViewer.scrollTop;
        const scrollLeft = this.pdfViewer.scrollLeft;
        statePersistence.savePdfScrollPosition(scrollTop, scrollLeft);
        console.log("[PDFScrollZoom] 💾 Saved scroll position to localStorage:", { scrollTop, scrollLeft });
      }
    }, 500); // Save after 500ms of no scrolling
  }

  /**
   * Setup scroll position tracking for PDF viewer
   */
  private setupScrollTracking(): void {
    console.log("[PDFScrollZoom] setupScrollTracking() called");

    if (!this.pdfViewer) {
      console.log("[PDFScrollZoom] ✗ No pdfViewer, cannot setup tracking");
      return;
    }

    this.pdfViewer.addEventListener("scroll", () => {
      this.saveScrollPosition();
    });

    console.log("[PDFScrollZoom] ✓ Scroll event listener attached to pdfViewer");
  }

  /**
   * Handle mouse wheel for editor - just tracking, let CSS handle scrolling
   */
  private handleEditorWheel(e: WheelEvent): void {
    const editorContainer = e.currentTarget as HTMLElement;
    if (!editorContainer) return;

    // Check if target is actually inside the editor
    if (!editorContainer.contains(e.target as Node)) return;

    // DON'T prevent default - let browser handle native scrolling
    // The CSS will make the editor scrollable
  }

  /**
   * Setup mutation observer to track PDF viewer changes
   */
  private setupMutationObserver(): void {
    if (!this.container) return;

    let observerCallCount = 0;

    const observer = new MutationObserver(() => {
      observerCallCount++;
      const currentViewer = this.container?.querySelector(
        ".pdf-preview-viewer",
      );

      // Log every mutation to debug
      if (observerCallCount % 10 === 0) {
        console.log(
          "[PDFScrollZoom] Observer called",
          observerCallCount,
          "times",
        );
      }

      // If viewer changed, update reference
      if (currentViewer && currentViewer !== this.pdfViewer) {
        console.log("[PDFScrollZoom] ========================================");
        console.log("[PDFScrollZoom] 🔄 MUTATION OBSERVER DETECTED CHANGE!");
        console.log("[PDFScrollZoom] Old pdfViewer:", this.pdfViewer);
        console.log("[PDFScrollZoom] New pdfViewer:", currentViewer);

        this.pdfViewer = currentViewer as HTMLElement;
        console.log("[PDFScrollZoom] ✓ pdfViewer reference updated");

        // Restore saved zoom level instead of resetting to 100
        console.log("[PDFScrollZoom] Step 1: Loading saved zoom...");
        this.loadSavedZoom();

        // Restore saved scroll position and setup tracking
        console.log("[PDFScrollZoom] Step 2: Restoring scroll position...");
        this.restoreSavedScrollPosition();

        console.log("[PDFScrollZoom] Step 3: Setting up scroll tracking...");
        this.setupScrollTracking();

        console.log("[PDFScrollZoom] Step 4: Loading color mode...");
        this.loadColorModePreference();
        this.applyColorMode();
        this.updateColorModeButton();

        console.log("[PDFScrollZoom] PDF viewer dimensions:");
        console.log("[PDFScrollZoom]   scrollHeight:", this.pdfViewer?.scrollHeight);
        console.log("[PDFScrollZoom]   clientHeight:", this.pdfViewer?.clientHeight);
        console.log("[PDFScrollZoom] ✓ All restoration steps completed");
        console.log("[PDFScrollZoom] ========================================");
      }
    });

    observer.observe(this.container, {
      childList: true,
      subtree: true,
      attributes: false,
      characterData: false,
    });

    console.log(
      "[PDFScrollZoom] Mutation observer setup on container:",
      this.container,
    );
  }

  /**
   * Show command mode indicator
   */
  private showCommandModeIndicator(): void {
    // Remove any existing indicator
    this.hideCommandModeIndicator();

    const indicator = document.createElement("div");
    indicator.id = "pdf-command-mode-indicator";
    indicator.innerHTML = `
      <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                  background: rgba(0, 0, 0, 0.8); color: white; padding: 1rem 2rem;
                  border-radius: 8px; z-index: 10000; font-size: 1.2rem;
                  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);">
        🎯 Command Mode: <kbd>T</kbd> Text | <kbd>H</kbd> Hand | <kbd>Z</kbd> Zoom
      </div>
    `;
    document.body.appendChild(indicator);
  }

  /**
   * Hide command mode indicator
   */
  private hideCommandModeIndicator(): void {
    const indicator = document.getElementById("pdf-command-mode-indicator");
    if (indicator) indicator.remove();
  }

  /**
   * Show temporary mode message
   */
  private showModeMessage(message: string): void {
    // Remove any existing message
    const existingMsg = document.getElementById("pdf-mode-message");
    if (existingMsg) existingMsg.remove();

    const msgDiv = document.createElement("div");
    msgDiv.id = "pdf-mode-message";
    msgDiv.innerHTML = `
      <div style="position: fixed; top: 20px; right: 20px;
                  background: rgba(59, 130, 246, 0.95); color: white;
                  padding: 0.75rem 1.5rem; border-radius: 6px; z-index: 10000;
                  font-size: 0.9rem; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                  animation: slideInRight 0.3s ease;">
        ${message}
      </div>
      <style>
        @keyframes slideInRight {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      </style>
    `;
    document.body.appendChild(msgDiv);

    // Auto-remove after 3 seconds
    setTimeout(() => {
      if (msgDiv.parentNode) msgDiv.remove();
    }, 3000);
  }

  /**
   * Handle keyboard - track Ctrl key
   */
  private handleKeyDown(e: KeyboardEvent): void {
    if (e.key === "Control" || e.key === "Meta") {
      this.isCtrlPressed = true;
    }

    // Ctrl+Space: Enter command mode (prefix key)
    if (this.isCtrlPressed && e.key === " " && !this.isWaitingForCommand) {
      e.preventDefault();
      this.isWaitingForCommand = true;
      console.log("[PDFScrollZoom] 🎯 Command mode activated - Press T (text), H (hand), or Z (zoom)");

      // Show visual indicator
      this.showCommandModeIndicator();

      // Auto-exit command mode after 2 seconds if no command pressed
      if (this.commandTimeout) clearTimeout(this.commandTimeout);
      this.commandTimeout = window.setTimeout(() => {
        this.isWaitingForCommand = false;
        this.hideCommandModeIndicator();
        console.log("[PDFScrollZoom] Command mode timeout - exited");
      }, 2000);

      return;
    }

    // Handle commands when in command mode
    if (this.isWaitingForCommand) {
      e.preventDefault();
      this.isWaitingForCommand = false;
      if (this.commandTimeout) clearTimeout(this.commandTimeout);
      this.hideCommandModeIndicator();

      switch (e.key.toLowerCase()) {
        case "t":
          console.log("[PDFScrollZoom] 📝 Text selection mode activated");
          this.currentMode = "text";
          this.isSpacePressed = false; // Disable hand mode
          if (this.pdfViewer) {
            this.pdfViewer.style.cursor = "auto"; // Default cursor for text selection
          }
          this.showModeMessage("Text Selection Mode");
          break;
        case "h":
          console.log("[PDFScrollZoom] ✋ Hand/Pan mode activated");
          this.currentMode = "hand";
          this.isSpacePressed = true;
          if (this.pdfViewer) {
            this.originalCursor = this.pdfViewer.style.cursor;
            this.pdfViewer.style.cursor = "grab";
          }
          this.showModeMessage("Hand/Pan Mode (press ESC to exit)");
          break;
        case "z":
          console.log("[PDFScrollZoom] 🔍 Zoom mode activated - Use Ctrl+drag or Ctrl+wheel");
          this.currentMode = "zoom";
          this.isSpacePressed = false; // Disable hand mode
          if (this.pdfViewer) {
            this.pdfViewer.style.cursor = "crosshair"; // Zoom cursor
          }
          this.showModeMessage("Zoom Mode - Use Ctrl+drag or Ctrl+wheel");
          break;
        default:
          console.log("[PDFScrollZoom] Unknown command:", e.key);
          this.showModeMessage("Unknown command: " + e.key);
      }
      return;
    }

    // Escape: Exit hand/zoom mode to text mode, or cancel command mode
    if (e.key === "Escape") {
      if (this.isWaitingForCommand) {
        this.isWaitingForCommand = false;
        if (this.commandTimeout) clearTimeout(this.commandTimeout);
        this.hideCommandModeIndicator();
        console.log("[PDFScrollZoom] Command mode cancelled");
      } else if (this.currentMode !== "text") {
        // Reset to text selection mode
        this.currentMode = "text";
        this.isSpacePressed = false;
        if (this.pdfViewer) {
          this.pdfViewer.style.cursor = "auto";
        }
        this.showModeMessage("Text Selection Mode (default)");
        console.log("[PDFScrollZoom] Returned to text selection mode via Escape");
      }
      return;
    }

    // Spacebar: activate hand/pan tool (like PDF Studio)
    if (e.key === " " && !this.isSpacePressed && !this.isCtrlPressed) {
      this.isSpacePressed = true;
      // Change cursor to grab/hand when spacebar is held
      if (this.pdfViewer) {
        this.originalCursor = this.pdfViewer.style.cursor;
        this.pdfViewer.style.cursor = "grab";
      }
      console.log("[PDFScrollZoom] Spacebar pressed - Hand tool activated");
    }

    // Ctrl + Plus: zoom in
    if (this.isCtrlPressed && (e.key === "+" || e.key === "=")) {
      e.preventDefault();
      this.zoomIn();
    }

    // Ctrl + Minus: zoom out
    if (this.isCtrlPressed && e.key === "-") {
      e.preventDefault();
      this.zoomOut();
    }

    // Ctrl + 0: reset zoom
    if (this.isCtrlPressed && e.key === "0") {
      e.preventDefault();
      this.resetZoom();
    }
  }

  /**
   * Handle keyboard - untrack Ctrl key
   */
  private handleKeyUp(e: KeyboardEvent): void {
    if (e.key === "Control" || e.key === "Meta") {
      this.isCtrlPressed = false;
    }

    // Spacebar released: deactivate hand/pan tool
    if (e.key === " " && this.isSpacePressed) {
      this.isSpacePressed = false;
      // Restore original cursor
      if (this.pdfViewer && !this.isPanning) {
        this.pdfViewer.style.cursor = this.originalCursor || "auto";
      }
      console.log("[PDFScrollZoom] Spacebar released - Hand tool deactivated");
    }
  }

  /**
   * Handle mouse wheel - ALWAYS prioritize PDF scroll
   * Don't prevent default - let CSS handle scrolling, just check if we're over PDF
   */
  private handleWheel(e: WheelEvent): void {
    if (!this.container) return;
    if (!this.pdfViewer) return;

    const isOverPDF = this.container.contains(e.target as Node);
    if (!isOverPDF) return;

    // DON'T prevent default - let browser handle native scrolling
    // The CSS will make the PDF viewer scrollable with overflow-y: scroll
    // This allows native smooth scrolling
  }

  /**
   * Handle mouse down - start zoom drag or panning
   */
  private handleMouseDown(e: MouseEvent): void {
    if (!this.container) return;

    const isOverPDF = this.container.contains(e.target as Node);
    if (!isOverPDF) return;

    // Spacebar + left click OR middle mouse button OR hand mode for panning
    // But NOT in text selection mode
    const canPan = (e.button === 0 && this.isSpacePressed) ||
                   (e.button === 1) ||
                   (e.button === 0 && this.currentMode === "hand");

    if (canPan && this.currentMode !== "text") {
      e.preventDefault();
      this.isPanning = true;
      this.dragStartX = e.clientX;
      this.dragStartY = e.clientY;

      // Save current scroll position
      const textPreview = this.container.querySelector(".text-preview");
      if (textPreview) {
        this.panStartScrollTop = textPreview.scrollTop;
        this.panStartScrollLeft = textPreview.scrollLeft;
      }

      // Change cursor to indicate pan mode
      if (this.pdfViewer) {
        this.originalCursor = this.pdfViewer.style.cursor;
        this.pdfViewer.style.cursor = "grabbing";
      }

      console.log("[PDFScrollZoom] Starting pan mode");
      return;
    }

    // Ctrl + left mouse button for zoom drag
    if (e.button === 0 && this.isCtrlPressed) {
      e.preventDefault();
      this.isDraggingZoom = true;
      this.dragStartX = e.clientX;
      this.dragStartY = e.clientY;
      this.dragStartZoom = this.currentZoom;

      console.log("[PDFScrollZoom] Starting zoom drag from:", this.currentZoom);

      // Change cursor to indicate zoom mode
      if (this.pdfViewer) {
        this.originalCursor = this.pdfViewer.style.cursor;
        this.pdfViewer.style.cursor = "grabbing";
      }
    }
  }

  /**
   * Handle mouse move - drag zoom or panning
   */
  private handleMouseMove(e: MouseEvent): void {
    // Handle panning
    if (this.isPanning && this.container) {
      const textPreview = this.container.querySelector(".text-preview");
      if (textPreview) {
        const deltaX = e.clientX - this.dragStartX;
        const deltaY = e.clientY - this.dragStartY;

        // Pan by adjusting scroll position (inverted for natural feel)
        textPreview.scrollTop = this.panStartScrollTop - deltaY;
        textPreview.scrollLeft = this.panStartScrollLeft - deltaX;
      }
      return;
    }

    // Handle zoom drag
    if (!this.isDraggingZoom || !this.pdfViewer) return;

    // Use both X and Y delta for better zoom control (diagonal drag for better UX)
    const deltaY = this.dragStartY - e.clientY;
    const deltaX = e.clientX - this.dragStartX;
    const delta = deltaY + deltaX * 0.5; // Y movement is primary, X is secondary
    const zoomDelta = (delta / 100) * this.zoomStep;
    const newZoom = Math.max(
      this.minZoom,
      Math.min(this.maxZoom, this.dragStartZoom + zoomDelta),
    );

    this.setZoom(newZoom, e.clientX, e.clientY);
  }

  /**
   * Handle mouse up - end zoom drag or panning
   */
  private handleMouseUp(): void {
    // End panning
    if (this.isPanning) {
      this.isPanning = false;
      if (this.pdfViewer) {
        this.pdfViewer.style.cursor = this.originalCursor || "auto";
      }
      console.log("[PDFScrollZoom] Ended pan mode");
    }

    // End zoom drag
    if (this.isDraggingZoom) {
      this.isDraggingZoom = false;
      if (this.pdfViewer) {
        this.pdfViewer.style.cursor = this.originalCursor || "auto";
      }
    }
  }

  /**
   * Handle touch start - start pinch zoom
   */
  private handleTouchStart(e: TouchEvent): void {
    if (e.touches.length !== 2) return;
    e.preventDefault();

    const touch1 = e.touches[0];
    const touch2 = e.touches[1];
    const distance = Math.hypot(
      touch2.clientX - touch1.clientX,
      touch2.clientY - touch1.clientY,
    );

    (e as any).pinchStartDistance = distance;
    (e as any).pinchStartZoom = this.currentZoom;
  }

  /**
   * Handle touch move - pinch zoom
   */
  private handleTouchMove(e: TouchEvent): void {
    if (e.touches.length !== 2 || !(e as any).pinchStartDistance) return;
    e.preventDefault();

    const touch1 = e.touches[0];
    const touch2 = e.touches[1];
    const distance = Math.hypot(
      touch2.clientX - touch1.clientX,
      touch2.clientY - touch1.clientY,
    );

    const zoomRatio = distance / (e as any).pinchStartDistance;
    const centerX = (touch1.clientX + touch2.clientX) / 2;
    const centerY = (touch1.clientY + touch2.clientY) / 2;

    const newZoom = Math.max(
      this.minZoom,
      Math.min(this.maxZoom, (e as any).pinchStartZoom * zoomRatio),
    );
    this.setZoom(newZoom, centerX, centerY);
  }

  /**
   * Handle touch end
   */
  private handleTouchEnd(e: TouchEvent): void {
    (e as any).pinchStartDistance = null;
    (e as any).pinchStartZoom = null;
  }

  /**
   * Set zoom level with cursor/center point preservation
   */
  private setZoom(zoomLevel: number, cursorX?: number, cursorY?: number): void {
    if (!this.pdfViewer) return;

    const oldZoom = this.currentZoom;
    this.currentZoom = Math.max(
      this.minZoom,
      Math.min(this.maxZoom, zoomLevel),
    );

    // Apply zoom via transform to iframe/embed
    const embed = this.pdfViewer.querySelector("embed, iframe");
    if (embed) {
      const scaleRatio = this.currentZoom / 100;
      (embed as HTMLElement).style.transform = `scale(${scaleRatio})`;
      (embed as HTMLElement).style.transformOrigin = "top center";
      (embed as HTMLElement).style.transition = "none";

      // If cursor position provided, center zoom on cursor
      if (cursorX !== undefined && cursorY !== undefined) {
        this.centerZoomOnPoint(cursorX, cursorY, oldZoom);
      }
    }

    this.updateZoomIndicator();

    // Save zoom level to state persistence
    statePersistence.savePdfZoom(this.currentZoom);

    console.log(`[PDFScrollZoom] Zoom: ${this.currentZoom.toFixed(0)}%`);
  }

  /**
   * Center zoom on a specific point (cursor/touch point)
   */
  private centerZoomOnPoint(
    pointX: number,
    pointY: number,
    oldZoom: number,
  ): void {
    if (!this.pdfViewer) return;

    const rect = this.pdfViewer.getBoundingClientRect();
    const relX = pointX - rect.left;
    const relY = pointY - rect.top;

    // Calculate scroll adjustment to keep point centered
    const zoomRatio = this.currentZoom / oldZoom;
    const scrollLeftAdjust = (relX * (zoomRatio - 1)) / zoomRatio;
    const scrollTopAdjust = (relY * (zoomRatio - 1)) / zoomRatio;

    requestAnimationFrame(() => {
      this.pdfViewer!.scrollLeft += scrollLeftAdjust;
      this.pdfViewer!.scrollTop += scrollTopAdjust;
    });
  }

  /**
   * Zoom in
   */
  zoomIn(): void {
    const newZoom = this.currentZoom + this.zoomStep;
    this.setZoom(newZoom);
  }

  /**
   * Zoom out
   */
  zoomOut(): void {
    const newZoom = this.currentZoom - this.zoomStep;
    this.setZoom(newZoom);
  }

  /**
   * Reset zoom to 125% (default)
   */
  resetZoom(): void {
    this.setZoom(125);
  }

  /**
   * Set zoom to fit page width
   */
  fitToWidth(): void {
    if (!this.pdfViewer || !this.pdfViewer.querySelector("embed")) return;

    const embed = this.pdfViewer.querySelector("embed") as HTMLEmbedElement;
    const embedWidth = embed.scrollWidth;
    const containerWidth = this.pdfViewer.clientWidth;

    const zoomLevel = (containerWidth / embedWidth) * 100;
    this.setZoom(zoomLevel);
  }

  /**
   * Set zoom to fit page height
   */
  fitToHeight(): void {
    if (!this.pdfViewer || !this.pdfViewer.querySelector("embed")) return;

    const embed = this.pdfViewer.querySelector("embed") as HTMLEmbedElement;
    const embedHeight = embed.scrollHeight;
    const containerHeight = this.pdfViewer.clientHeight;

    const zoomLevel = (containerHeight / embedHeight) * 100;
    this.setZoom(zoomLevel);
  }

  /**
   * Update zoom indicator in UI
   */
  private updateZoomIndicator(): void {
    // Update zoom dropdown
    const zoomSelect = document.getElementById("pdf-zoom-select") as HTMLSelectElement;
    if (zoomSelect) {
      // Round to nearest preset value or set custom value
      const roundedZoom = this.currentZoom.toFixed(0);

      // Check if the current zoom matches any preset option
      const hasMatchingOption = Array.from(zoomSelect.options).some(
        option => option.value === roundedZoom
      );

      if (hasMatchingOption) {
        zoomSelect.value = roundedZoom;
      } else {
        // If zoom doesn't match any preset, select the closest one
        const presetValues = Array.from(zoomSelect.options).map(opt => parseInt(opt.value, 10));
        const closest = presetValues.reduce((prev, curr) =>
          Math.abs(curr - this.currentZoom) < Math.abs(prev - this.currentZoom) ? curr : prev
        );
        zoomSelect.value = closest.toString();
      }
    }
  }

  /**
   * Get current zoom level
   */
  getCurrentZoom(): number {
    return this.currentZoom;
  }

  /**
   * Cycle through available PDF color modes
   */
  cycleColorMode(): void {
    const modes: PDFColorMode[] = ["light", "dark"];
    const currentIndex = modes.indexOf(this.colorMode);
    const nextIndex = (currentIndex + 1) % modes.length;
    this.colorMode = modes[nextIndex];
    this.applyColorMode();
    this.saveColorModePreference();
    this.updateColorModeButton();
    console.log("[PDFScrollZoom] Color mode toggled to:", this.colorMode);

    // Trigger recompilation to apply color mode
    this.notifyColorModeChange();
  }

  /**
   * Alias for backward compatibility - toggle between light and dark
   */
  toggleColorMode(): void {
    this.cycleColorMode();
  }

  /**
   * Set PDF color mode explicitly
   */
  setColorMode(mode: PDFColorMode): void {
    if (!(mode in PDF_COLOR_THEMES)) {
      console.warn("[PDFScrollZoom] Unknown color mode:", mode);
      return;
    }
    this.colorMode = mode;
    this.applyColorMode();
    this.saveColorModePreference();
    this.updateColorModeButton();
    console.log("[PDFScrollZoom] Color mode set to:", this.colorMode);
  }

  /**
   * Get current color mode
   */
  getColorMode(): PDFColorMode {
    return this.colorMode;
  }

  /**
   * Apply color mode/theme filters to PDF embed
   * Uses CSS filters to apply different visual themes
   */
  private applyColorMode(): void {
    const embed = this.pdfViewer?.querySelector("embed");
    if (!embed) return;

    const theme = PDF_COLOR_THEMES[this.colorMode];
    if (!theme) {
      console.warn("[PDFScrollZoom] Unknown color mode:", this.colorMode);
      return;
    }

    embed.style.filter = theme.filter;
    if (this.pdfViewer) {
      this.pdfViewer.style.backgroundColor = theme.backgroundColor;
    }

    // Set data attribute on all PDF-related containers for theme-responsive scrollbar
    const textPreview = document.getElementById("text-preview");
    if (textPreview) {
      textPreview.setAttribute("data-pdf-theme", this.colorMode);
    }

    const pdfPreviewContainer = document.querySelector(
      ".pdf-preview-container",
    );
    if (pdfPreviewContainer) {
      pdfPreviewContainer.setAttribute("data-pdf-theme", this.colorMode);
    }

    if (this.pdfViewer) {
      this.pdfViewer.setAttribute("data-pdf-theme", this.colorMode);
    }

    console.log("[PDFScrollZoom] Applied theme:", theme.label);
  }

  /**
   * Load saved color mode preference from localStorage
   * Defaults to global theme if no PDF-specific preference is saved
   */
  private loadColorModePreference(): void {
    const savedMode = localStorage.getItem(
      "pdf-color-mode",
    ) as PDFColorMode | null;

    if (savedMode === "dark" || savedMode === "light") {
      // Use saved PDF-specific preference
      this.colorMode = savedMode;
    } else {
      // Default to global theme
      const globalTheme =
        document.documentElement.getAttribute("data-theme") ||
        localStorage.getItem("theme") ||
        "light";
      this.colorMode = (
        globalTheme === "dark" ? "dark" : "light"
      ) as PDFColorMode;
      console.log(
        "[PDFScrollZoom] No PDF theme saved, defaulting to global theme:",
        this.colorMode,
      );
    }
  }

  /**
   * Save color mode preference to localStorage
   */
  private saveColorModePreference(): void {
    localStorage.setItem("pdf-color-mode", this.colorMode);
  }

  /**
   * Update color mode button state
   */
  private updateColorModeButton(): void {
    const btn = document.getElementById("pdf-color-mode-btn");
    if (!btn) return;

    const theme = PDF_COLOR_THEMES[this.colorMode];
    const iconEl = btn.querySelector(".theme-icon");

    // Map color modes to emoji - show what the PDF SHOULD look like
    // Moon = dark mode (black bg, white text), Sun = light mode (white bg, black text)
    const iconMap: Record<PDFColorMode, string> = {
      dark: "🌙", // Moon emoji = Dark mode (BLACK background, WHITE text)
      light: "☀️", // Sun emoji = Light mode (WHITE background, BLACK text)
    };

    if (iconEl) {
      iconEl.textContent = iconMap[this.colorMode];
    }

    btn.setAttribute("title", `PDF Theme: ${theme.label} (Click to toggle)`);
  }

  /**
   * Get available color modes
   */
  getAvailableColorModes(): { name: PDFColorMode; label: string }[] {
    return [
      { name: "light", label: "Light" },
      { name: "dark", label: "Dark" },
    ];
  }

  /**
   * Register callback for color mode changes
   */
  onColorModeChange(callback: (colorMode: PDFColorMode) => void): void {
    this.onColorModeChangeCallback = callback;
  }

  /**
   * Notify color mode change
   */
  private notifyColorModeChange(): void {
    if (this.onColorModeChangeCallback) {
      this.onColorModeChangeCallback(this.colorMode);
    }
  }

  /**
   * Observe PDF viewer changes and reinitialize
   * (Already handled by setupMutationObserver in setupEventListeners)
   */
  observePDFViewer(): void {
    if (!this.container) {
      console.warn("[PDFScrollZoom] No container found for observing");
      return;
    }

    // First, check if PDF viewer already exists
    const existingViewer = this.container.querySelector(".pdf-preview-viewer");
    if (existingViewer) {
      this.pdfViewer = existingViewer as HTMLElement;

      // Restore saved zoom level instead of resetting to 100
      this.loadSavedZoom();

      this.loadColorModePreference();
      this.applyColorMode();
      this.updateColorModeButton();
      console.log("[PDFScrollZoom] Found existing PDF viewer");
    }

    // Load preference on first initialization
    // Note: Will default to global theme if no PDF-specific preference saved
    this.loadColorModePreference();

    // Apply the theme and update button icon immediately on page load
    this.applyColorMode();
    this.updateColorModeButton();
  }
}
