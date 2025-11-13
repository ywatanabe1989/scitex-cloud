/**
 * PDF.js Viewer for Writer App
 * Replaces iframe-based PDF viewing with canvas-based rendering
 * Provides full control over scrollbars, themes, and rendering
 */

import { statePersistence } from "./state-persistence.js";

console.log("[DEBUG] pdf-viewer-pdfjs.ts loaded");

export interface PDFViewerOptions {
  containerId: string;
  colorMode?: "light" | "dark";
  fitToWidth?: boolean;
  onPageChange?: (pageNum: number) => void;
  renderQuality?: number; // Quality multiplier: 1.0 = standard, 2.0 = 2x, 4.0 = 300+ DPI
}

export class PDFJSViewer {
  private container: HTMLElement | null;
  private pdfDoc: any = null;
  private currentScale: number = 1.5;
  private currentPage: number = 1;
  private colorMode: "light" | "dark" = "light";
  private fitToWidth: boolean = true;
  private onPageChangeCallback?: (pageNum: number) => void;
  private pdfjsLib: any = null;
  private isLoading: boolean = false;
  private scrollSaveTimeout: number | null = null;
  private savedScrollPosition: { scrollTop: number; scrollLeft: number } | null = null;
  private renderQuality: number = 2.0; // 2x quality by default for crisp rendering

  // Mouse panning state
  private isDragging: boolean = false;
  private startX: number = 0;
  private startY: number = 0;
  private scrollLeft: number = 0;
  private scrollTop: number = 0;

  // Mode tracking for interaction
  public currentMode: "text" | "hand" | "zoom" = "text";

  constructor(options: PDFViewerOptions) {
    this.container = document.getElementById(options.containerId);
    this.colorMode = options.colorMode || "light";
    this.fitToWidth = options.fitToWidth ?? true;
    this.onPageChangeCallback = options.onPageChange;
    this.renderQuality = options.renderQuality ?? 2.0; // Default 2x for crisp rendering

    console.log(
      "[PDFJSViewer] Initialized with container:",
      options.containerId,
      "theme:",
      this.colorMode,
      "quality:",
      this.renderQuality + "x",
    );

    // Restore saved zoom level
    this.restoreSavedZoom();

    // Load PDF.js library
    this.loadPDFJS();
  }

  /**
   * Restore zoom level from localStorage
   */
  private restoreSavedZoom(): void {
    const savedZoom = statePersistence.getSavedPdfZoom();
    if (savedZoom) {
      // Convert percentage (50-300) to scale (0.5-3.0)
      this.currentScale = savedZoom / 100;
      console.log("[PDFJSViewer] Restored saved zoom:", savedZoom + "%", "scale:", this.currentScale);
    }
  }

  /**
   * Load PDF.js from CDN
   */
  private loadPDFJS(): void {
    // Check if already loaded
    if ((window as any).pdfjsLib) {
      this.pdfjsLib = (window as any).pdfjsLib;
      console.log("[PDFJSViewer] PDF.js already loaded");
      return;
    }

    const script = document.createElement("script");
    script.src =
      "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js";
    script.onload = () => {
      this.pdfjsLib = (window as any).pdfjsLib;
      if (this.pdfjsLib) {
        this.pdfjsLib.GlobalWorkerOptions.workerSrc =
          "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
        console.log("[PDFJSViewer] PDF.js loaded successfully");
      }
    };
    script.onerror = () => {
      console.error("[PDFJSViewer] Failed to load PDF.js");
    };
    document.head.appendChild(script);
  }

  /**
   * Load and render a PDF
   */
  async loadPDF(pdfUrl: string): Promise<void> {
    if (!this.container) {
      console.error("[PDFJSViewer] No container found");
      return;
    }

    if (!this.pdfjsLib) {
      console.warn("[PDFJSViewer] PDF.js not loaded yet, waiting...");
      // Wait for library to load
      await new Promise((resolve) => setTimeout(resolve, 500));
      if (!this.pdfjsLib) {
        console.error("[PDFJSViewer] PDF.js still not available");
        return;
      }
    }

    if (this.isLoading) {
      console.warn("[PDFJSViewer] Already loading a PDF");
      return;
    }

    this.isLoading = true;

    // Show loading indicator
    this.container.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: var(--color-fg-muted);">
                <div style="text-align: center;">
                    <i class="fas fa-spinner fa-spin fa-2x mb-2"></i>
                    <p>Loading PDF...</p>
                </div>
            </div>
        `;

    try {
      console.log(
        "[PDFJSViewer] Loading PDF:",
        pdfUrl,
        "theme:",
        this.colorMode,
      );

      const loadingTask = this.pdfjsLib.getDocument(pdfUrl);
      this.pdfDoc = await loadingTask.promise;

      console.log("[PDFJSViewer] PDF loaded:", this.pdfDoc.numPages, "pages");

      // Render all pages
      await this.renderAllPages();

      this.isLoading = false;
    } catch (error) {
      console.error("[PDFJSViewer] Error loading PDF:", error);
      this.isLoading = false;

      if (this.container) {
        this.container.innerHTML = `
                    <div style="display: flex; align-items: center; justify-content: center; height: 100%; padding: 2rem; text-align: center; color: var(--color-danger-fg);">
                        <div>
                            <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                            <h5>Error Loading PDF</h5>
                            <p>${error instanceof Error ? error.message : "Unknown error"}</p>
                        </div>
                    </div>
                `;
      }
    }
  }

  /**
   * Render all pages to canvas elements
   */
  private async renderAllPages(): Promise<void> {
    if (!this.pdfDoc || !this.container) return;

    // Create scrollable container with theme-responsive styling
    // Note: No whitespace to prevent top spacing issues
    const viewerHtml = `<div class="pdfjs-viewer" id="pdfjs-viewer" data-theme="${this.colorMode}"></div>`;

    this.container.innerHTML = viewerHtml;

    const viewer = document.getElementById("pdfjs-viewer");
    if (!viewer) return;

    // Calculate scale for fit-to-width (only if no saved zoom)
    if (this.fitToWidth && !statePersistence.getSavedPdfZoom()) {
      // Use viewer's actual width (clientWidth already accounts for scrollbar)
      const viewerWidth = viewer.clientWidth;
      // Don't subtract scrollbar - let PDF use full available width
      const availableWidth = viewerWidth;
      // Standard PDF page width is 612 points
      this.currentScale = availableWidth / 612;
      console.log(
        "[PDFJSViewer] Fit to width:",
        "viewer width:", viewerWidth,
        "available width:", availableWidth,
        "scale:", this.currentScale.toFixed(2)
      );

      // Update dropdown to show "Fit to Width"
      const zoomSelect = document.getElementById("pdf-zoom-select") as HTMLSelectElement;
      if (zoomSelect) {
        zoomSelect.value = "fit-width";
        console.log("[PDFJSViewer] ✓ Dropdown set to 'Fit to Width'");
      }
    }

    // Render each page
    for (let pageNum = 1; pageNum <= this.pdfDoc.numPages; pageNum++) {
      await this.renderPage(pageNum, viewer);
    }

    // Setup scroll listener
    this.setupScrollListener();

    // Setup mouse wheel zoom
    this.setupMouseZoomListener();

    // Setup mouse panning (click and drag)
    this.setupMousePanListener();

    // Restore scroll position after rendering
    this.restoreScrollPosition();
  }

  /**
   * Render a single page
   */
  private async renderPage(
    pageNum: number,
    container: HTMLElement,
  ): Promise<void> {
    try {
      const page = await this.pdfDoc.getPage(pageNum);
      const viewport = page.getViewport({ scale: this.currentScale });

      // Get device pixel ratio for high-DPI displays (Retina, 4K, etc.)
      const dpr = window.devicePixelRatio || 1;

      // Apply quality multiplier for ultra-crisp rendering
      // renderQuality = 2.0 → ~150 DPI
      // renderQuality = 4.0 → ~300 DPI (print quality)
      const totalScale = dpr * this.renderQuality;

      console.log(
        "[PDFJSViewer] Rendering page", pageNum,
        "| DPR:", dpr,
        "| Quality:", this.renderQuality + "x",
        "| Total scale:", totalScale + "x",
        "| Effective DPI:", Math.round(72 * totalScale)
      );

      // Create page container
      const pageContainer = document.createElement("div");
      pageContainer.className = "pdfjs-page-container";
      pageContainer.id = `pdfjs-page-${pageNum}`;
      pageContainer.dataset.pageNum = String(pageNum);
      pageContainer.style.cssText = `
                margin: ${pageNum === 1 ? "0" : "0.5rem 0 0 0"};
                background: ${this.colorMode === "dark" ? "#1a1a1a" : "white"};
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                position: relative;
                width: ${viewport.width}px;
                height: ${viewport.height}px;
            `;

      // Create canvas
      const canvas = document.createElement("canvas");
      const context = canvas.getContext("2d");
      if (!context) return;

      // Scale canvas for high-DPI displays + quality multiplier
      // Canvas internal resolution (ultra high-res for print-quality rendering)
      canvas.width = viewport.width * totalScale;
      canvas.height = viewport.height * totalScale;

      // Canvas CSS size (visual size on screen - unchanged)
      canvas.style.width = viewport.width + "px";
      canvas.style.height = viewport.height + "px";
      canvas.style.display = "block";

      // Scale the canvas context to match total scale
      context.scale(totalScale, totalScale);

      pageContainer.appendChild(canvas);
      container.appendChild(pageContainer);

      // Render PDF page to canvas
      const renderContext = {
        canvasContext: context,
        viewport: viewport,
      };

      await page.render(renderContext).promise;

      // Render text layer for text selection (use same viewport as canvas)
      await this.renderTextLayer(page, pageContainer, viewport, this.currentScale);

      // NOTE: Link annotations NOT rendered - we use iframe PDF viewing, not PDF.js
      // For link highlighting, see LaTeX hyperref configuration in latex-wrapper.ts
      // await this.renderAnnotations(page, pageContainer, viewport);

      console.log("[PDFJSViewer] Rendered page", pageNum);
    } catch (error) {
      console.error(`[PDFJSViewer] Error rendering page ${pageNum}:`, error);
    }
  }

  /**
   * Render text layer for text selection
   */
  private async renderTextLayer(page: any, container: HTMLElement, viewport: any, scale: number): Promise<void> {
    try {
      // Get text content
      const textContent = await page.getTextContent();

      // Create text layer container
      const textLayerDiv = document.createElement("div");
      textLayerDiv.className = "textLayer";

      // Set width and height to match viewport exactly
      // IMPORTANT: --scale-factor CSS variable is required by PDF.js for proper text positioning
      textLayerDiv.style.cssText = `
        position: absolute;
        left: 0;
        top: 0;
        width: ${viewport.width}px;
        height: ${viewport.height}px;
        overflow: hidden;
        opacity: 1;
        line-height: 1.0;
        --scale-factor: ${viewport.scale};
      `;

      container.appendChild(textLayerDiv);

      // Render text layer using PDF.js text layer builder
      // IMPORTANT: Use the same viewport as canvas rendering
      if ((window as any).pdfjsLib && (window as any).pdfjsLib.renderTextLayer) {
        const renderTask = (window as any).pdfjsLib.renderTextLayer({
          textContent: textContent,
          container: textLayerDiv,
          viewport: viewport,
          textDivs: [],
          textContentItemsStr: [], // Required for better positioning
        });

        await renderTask.promise;
        console.log("[PDFJSViewer] ✓ Text layer rendered for page at scale:", scale);
      } else {
        console.warn("[PDFJSViewer] PDF.js renderTextLayer not available");
      }
    } catch (error) {
      console.error("[PDFJSViewer] Error rendering text layer:", error);
    }
  }

  /**
   * Render link annotations as overlay elements
   *
   * ⚠️ WARNING: THIS METHOD IS NOT CURRENTLY USED
   *
   * This application uses IFRAME-based PDF viewing, NOT PDF.js canvas rendering.
   * After extensive testing, iframe proved superior for browser compatibility,
   * performance, and native PDF features.
   *
   * For link highlighting, we use LaTeX hyperref package configuration in
   * latex-wrapper.ts instead (bold green text), which works with iframe viewing.
   *
   * This code is kept for reference only in case we switch back to PDF.js.
   */
  private async renderAnnotations(
    page: any,
    pageContainer: HTMLElement,
    viewport: any,
  ): Promise<void> {
    try {
      const annotations = await page.getAnnotations();

      // Filter for link annotations only
      const linkAnnotations = annotations.filter(
        (ann: any) => ann.subtype === "Link",
      );

      if (linkAnnotations.length === 0) {
        return;
      }

      console.log(
        `[PDFJSViewer] Found ${linkAnnotations.length} link(s) on page`,
      );

      // Create annotation layer container
      const annotationLayer = document.createElement("div");
      annotationLayer.className = "pdfjs-annotation-layer";
      annotationLayer.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
            `;
      pageContainer.appendChild(annotationLayer);

      // Render each link annotation
      for (const annotation of linkAnnotations) {
        const linkElement = this.createLinkElement(annotation, viewport);
        if (linkElement) {
          annotationLayer.appendChild(linkElement);
        }
      }
    } catch (error) {
      console.error("[PDFJSViewer] Error rendering annotations:", error);
    }
  }

  /**
   * Create a link overlay element from annotation data
   *
   * ⚠️ WARNING: THIS METHOD IS NOT CURRENTLY USED
   *
   * This is part of the PDF.js annotation system which is not active.
   * See renderAnnotations() documentation for details.
   */
  private createLinkElement(
    annotation: any,
    viewport: any,
  ): HTMLElement | null {
    if (!annotation.rect || annotation.rect.length < 4) {
      return null;
    }

    // Transform annotation rectangle to viewport coordinates
    const rect = viewport.convertToViewportRectangle(annotation.rect);

    // Calculate position and size (PDF coordinates are bottom-left origin)
    const left = Math.min(rect[0], rect[2]);
    const top = Math.min(rect[1], rect[3]);
    const width = Math.abs(rect[2] - rect[0]);
    const height = Math.abs(rect[3] - rect[1]);

    // Create link element
    const linkEl = document.createElement("a");
    linkEl.className = "pdfjs-link-annotation";

    // Set link URL
    let linkUrl = "";
    if (annotation.url) {
      linkUrl = annotation.url;
    } else if (annotation.dest) {
      // Internal link (destination within PDF)
      linkUrl = `#page=${annotation.dest}`;
    }

    if (linkUrl) {
      linkEl.href = linkUrl;
      if (annotation.url) {
        // External links open in new tab
        linkEl.target = "_blank";
        linkEl.rel = "noopener noreferrer";
      }
    }

    // Position and style the link overlay
    linkEl.style.cssText = `
            position: absolute;
            left: ${left}px;
            top: ${top}px;
            width: ${width}px;
            height: ${height}px;
            pointer-events: auto;
            cursor: pointer;
            border: 1.5px solid ${this.colorMode === "dark" ? "rgba(100, 149, 237, 0.6)" : "rgba(0, 102, 204, 0.5)"};
            background: ${this.colorMode === "dark" ? "rgba(100, 149, 237, 0.1)" : "rgba(0, 102, 204, 0.08)"};
            border-radius: 2px;
            transition: all 0.2s ease;
        `;

    // Add hover effect
    linkEl.addEventListener("mouseenter", () => {
      linkEl.style.background =
        this.colorMode === "dark"
          ? "rgba(100, 149, 237, 0.2)"
          : "rgba(0, 102, 204, 0.15)";
      linkEl.style.borderColor =
        this.colorMode === "dark"
          ? "rgba(100, 149, 237, 0.9)"
          : "rgba(0, 102, 204, 0.8)";
    });

    linkEl.addEventListener("mouseleave", () => {
      linkEl.style.background =
        this.colorMode === "dark"
          ? "rgba(100, 149, 237, 0.1)"
          : "rgba(0, 102, 204, 0.08)";
      linkEl.style.borderColor =
        this.colorMode === "dark"
          ? "rgba(100, 149, 237, 0.6)"
          : "rgba(0, 102, 204, 0.5)";
    });

    // Add title tooltip
    if (annotation.url) {
      linkEl.title = `External link: ${annotation.url}`;
    } else if (annotation.dest) {
      linkEl.title = "Internal link";
    }

    return linkEl;
  }

  /**
   * Setup scroll listener for page tracking and scroll position saving
   */
  private setupScrollListener(): void {
    const viewer = document.getElementById("pdfjs-viewer");
    if (!viewer) return;

    let scrollTimeout: number;

    viewer.addEventListener("scroll", () => {
      clearTimeout(scrollTimeout);
      scrollTimeout = window.setTimeout(() => {
        this.updateCurrentPageFromScroll();
      }, 100);

      // Save scroll position (debounced)
      this.saveScrollPositionDebounced();
    });

    console.log("[PDFJSViewer] ✓ Scroll listener attached, will save position every 500ms");
  }

  /**
   * Setup mouse wheel zoom (Ctrl+Wheel)
   */
  private setupMouseZoomListener(): void {
    const viewer = document.getElementById("pdfjs-viewer");
    if (!viewer) return;

    viewer.addEventListener("wheel", (e: WheelEvent) => {
      // Only zoom if Ctrl is pressed
      if (!e.ctrlKey && !e.metaKey) {
        return;
      }

      // Prevent default page zoom
      e.preventDefault();

      // Calculate zoom delta
      const delta = -e.deltaY / 100;
      const zoomFactor = 1 + delta * 0.1; // 10% per 100 deltaY

      // Calculate new scale
      let newScale = this.currentScale * zoomFactor;

      // Clamp between 0.5x and 3.0x
      newScale = Math.max(0.5, Math.min(3.0, newScale));

      // Only update if scale actually changed
      if (newScale !== this.currentScale) {
        console.log("[PDFJSViewer] Mouse wheel zoom:", (newScale * 100).toFixed(0) + "%");
        this.setScale(newScale);
      }
    }, { passive: false }); // passive: false allows preventDefault()

    console.log("[PDFJSViewer] ✓ Mouse wheel zoom enabled (Ctrl+Wheel)");
  }

  /**
   * Setup mouse panning (click and drag to move)
   */
  private setupMousePanListener(): void {
    const viewer = document.getElementById("pdfjs-viewer");
    if (!viewer) return;

    // Cursor will be managed by mode changes
    // Default to auto for text selection
    viewer.style.cursor = "auto";

    // Mouse down - start dragging (only in hand mode or with middle button)
    viewer.addEventListener("mousedown", (e: MouseEvent) => {
      // Only pan in hand mode with left button, or with middle button in any mode
      const canPan = (e.button === 0 && this.currentMode === "hand") || e.button === 1;
      if (!canPan) return;

      e.preventDefault(); // Prevent default for middle button
      this.isDragging = true;
      this.startX = e.pageX - viewer.offsetLeft;
      this.startY = e.pageY - viewer.offsetTop;
      this.scrollLeft = viewer.scrollLeft;
      this.scrollTop = viewer.scrollTop;

      viewer.style.cursor = "grabbing";
      viewer.style.userSelect = "none"; // Prevent text selection while dragging

      console.log("[PDFJSViewer] Panning started (mode:", this.currentMode, ")");
    });

    // Mouse move - pan if dragging
    viewer.addEventListener("mousemove", (e: MouseEvent) => {
      if (!this.isDragging) return;

      e.preventDefault();

      const x = e.pageX - viewer.offsetLeft;
      const y = e.pageY - viewer.offsetTop;
      const walkX = (x - this.startX) * 1.5; // Multiply for faster panning
      const walkY = (y - this.startY) * 1.5;

      viewer.scrollLeft = this.scrollLeft - walkX;
      viewer.scrollTop = this.scrollTop - walkY;
    });

    // Mouse up - stop dragging
    const stopDragging = () => {
      if (this.isDragging) {
        console.log("[PDFJSViewer] Panning stopped");
      }
      this.isDragging = false;
      // Restore cursor based on mode
      viewer.style.cursor = this.currentMode === "hand" ? "grab" :
                            this.currentMode === "zoom" ? "crosshair" : "auto";
      viewer.style.userSelect = ""; // Re-enable text selection
    };

    viewer.addEventListener("mouseup", stopDragging);
    viewer.addEventListener("mouseleave", stopDragging); // Stop if mouse leaves viewer

    console.log("[PDFJSViewer] ✓ Mouse panning enabled (click and drag)");
  }

  /**
   * Save scroll position to localStorage (debounced)
   */
  private saveScrollPositionDebounced(): void {
    if (this.scrollSaveTimeout) {
      clearTimeout(this.scrollSaveTimeout);
    }

    this.scrollSaveTimeout = window.setTimeout(() => {
      const viewer = document.getElementById("pdfjs-viewer");
      if (viewer) {
        const scrollTop = viewer.scrollTop;
        const scrollLeft = viewer.scrollLeft;
        statePersistence.savePdfScrollPosition(scrollTop, scrollLeft);
        console.log("[PDFJSViewer] 💾 Saved scroll position:", { scrollTop, scrollLeft });
      }
    }, 500);
  }

  /**
   * Restore scroll position from localStorage
   */
  private restoreScrollPosition(): void {
    const viewer = document.getElementById("pdfjs-viewer");
    if (!viewer) {
      console.log("[PDFJSViewer] Cannot restore scroll: viewer not found");
      return;
    }

    // First try to restore from temporary saved position (during re-render)
    if (this.savedScrollPosition) {
      console.log("[PDFJSViewer] Restoring scroll from temporary save:", this.savedScrollPosition);
      requestAnimationFrame(() => {
        viewer.scrollTop = this.savedScrollPosition!.scrollTop;
        viewer.scrollLeft = this.savedScrollPosition!.scrollLeft;
        console.log("[PDFJSViewer] ✓ Scroll restored from temporary save");
        this.savedScrollPosition = null; // Clear after use
      });
      return;
    }

    // Otherwise restore from localStorage
    const savedPosition = statePersistence.getSavedPdfScrollPosition();
    if (savedPosition) {
      console.log("[PDFJSViewer] Restoring scroll from localStorage:", savedPosition);
      requestAnimationFrame(() => {
        viewer.scrollTop = savedPosition.scrollTop;
        viewer.scrollLeft = savedPosition.scrollLeft;
        console.log("[PDFJSViewer] ✓ Scroll restored from localStorage");
      });
    } else {
      console.log("[PDFJSViewer] No saved scroll position found");
    }
  }

  /**
   * Update current page based on scroll position
   */
  private updateCurrentPageFromScroll(): void {
    const viewer = document.getElementById("pdfjs-viewer");
    if (!viewer) return;

    const pages = Array.from(viewer.querySelectorAll(".pdfjs-page-container"));
    const scrollTop = viewer.scrollTop;
    const viewportMiddle = scrollTop + viewer.clientHeight / 3;

    for (const page of pages) {
      const pageElement = page as HTMLElement;
      const pageTop = pageElement.offsetTop;
      const pageBottom = pageTop + pageElement.offsetHeight;

      if (viewportMiddle >= pageTop && viewportMiddle < pageBottom) {
        const pageNumStr = pageElement.dataset.pageNum;
        if (pageNumStr) {
          const pageNum = parseInt(pageNumStr);
          if (pageNum !== this.currentPage) {
            this.currentPage = pageNum;
            if (this.onPageChangeCallback) {
              this.onPageChangeCallback(pageNum);
            }
            console.log("[PDFJSViewer] Current page:", pageNum);
          }
        }
        break;
      }
    }
  }

  /**
   * Set color mode and re-render
   */
  setColorMode(colorMode: "light" | "dark"): void {
    if (this.colorMode === colorMode) return;

    // Save current scroll position before re-render
    const viewer = document.getElementById("pdfjs-viewer");
    if (viewer) {
      this.savedScrollPosition = {
        scrollTop: viewer.scrollTop,
        scrollLeft: viewer.scrollLeft,
      };
      console.log("[PDFJSViewer] Saved scroll position before theme change:", this.savedScrollPosition);
    }

    this.colorMode = colorMode;
    console.log("[PDFJSViewer] Color mode changed to:", colorMode);

    // Re-render pages with new theme (will restore scroll after)
    if (this.pdfDoc) {
      this.renderAllPages();
    }
  }

  /**
   * Set zoom level and re-render
   */
  setScale(scale: number): void {
    if (scale < 0.5 || scale > 3.0) return;

    // Save current scroll position before re-render
    const viewer = document.getElementById("pdfjs-viewer");
    if (viewer) {
      this.savedScrollPosition = {
        scrollTop: viewer.scrollTop,
        scrollLeft: viewer.scrollLeft,
      };
      console.log("[PDFJSViewer] Saved scroll position before zoom change:", this.savedScrollPosition);
    }

    this.currentScale = scale;
    console.log("[PDFJSViewer] Scale changed to:", scale);

    // Save zoom level to localStorage
    const zoomPercent = Math.round(scale * 100);
    statePersistence.savePdfZoom(zoomPercent);
    console.log("[PDFJSViewer] 💾 Saved zoom to localStorage:", zoomPercent + "%");

    // Update toolbar dropdown to match current zoom
    this.updateZoomDropdown(zoomPercent);

    if (this.pdfDoc) {
      this.renderAllPages();
    }
  }

  /**
   * Update the zoom dropdown in the toolbar to match current zoom level
   */
  private updateZoomDropdown(zoomPercent: number): void {
    const zoomSelect = document.getElementById("pdf-zoom-select") as HTMLSelectElement;
    if (!zoomSelect) return;

    // Predefined zoom levels in the dropdown (excluding "fit-width")
    const predefinedZooms = [50, 75, 100, 125, 150, 200];

    // If exact match exists in dropdown, select it
    const exactOption = Array.from(zoomSelect.options).find(
      opt => parseInt(opt.value) === zoomPercent
    );

    if (exactOption) {
      zoomSelect.value = zoomPercent.toString();
      console.log("[PDFJSViewer] ✓ Toolbar updated to exact zoom:", zoomPercent + "%");
    } else {
      // Add custom zoom value if it doesn't exist
      const customOption = document.createElement("option");
      customOption.value = zoomPercent.toString();
      customOption.text = zoomPercent + "%";
      customOption.selected = true;

      // Insert in sorted order (after "fit-width")
      let inserted = false;
      for (let i = 0; i < zoomSelect.options.length; i++) {
        const optValue = zoomSelect.options[i].value;
        // Skip "fit-width" option
        if (optValue === "fit-width") continue;

        const numericValue = parseInt(optValue);
        if (zoomPercent < numericValue) {
          zoomSelect.add(customOption, i);
          inserted = true;
          break;
        }
      }
      if (!inserted) {
        zoomSelect.add(customOption);
      }

      // Remove old custom values (keep "fit-width", predefined, and current custom)
      for (let i = zoomSelect.options.length - 1; i >= 0; i--) {
        const optValue = zoomSelect.options[i].value;
        if (optValue === "fit-width") continue; // Never remove "fit-width"

        const numericValue = parseInt(optValue);
        // Skip non-numeric values (like if "fit-width" wasn't caught above)
        if (isNaN(numericValue)) continue;

        if (!predefinedZooms.includes(numericValue) && numericValue !== zoomPercent) {
          zoomSelect.remove(i);
        }
      }

      console.log("[PDFJSViewer] ✓ Toolbar updated with custom zoom:", zoomPercent + "%");
    }
  }

  /**
   * Zoom in
   */
  zoomIn(): void {
    this.setScale(this.currentScale + 0.25);
  }

  /**
   * Zoom out
   */
  zoomOut(): void {
    this.setScale(this.currentScale - 0.25);
  }

  /**
   * Fit to width
   */
  fitWidth(): void {
    if (!this.container) return;
    const containerWidth = this.container.clientWidth;
    const newScale = (containerWidth - 40) / 612; // Standard PDF width
    this.setScale(newScale);
  }

  /**
   * Go to page
   */
  gotoPage(pageNum: number): void {
    if (pageNum < 1 || (this.pdfDoc && pageNum > this.pdfDoc.numPages)) return;

    this.currentPage = pageNum;
    const pageElement = document.getElementById(`pdfjs-page-${pageNum}`);
    if (pageElement) {
      pageElement.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  /**
   * Get total pages
   */
  getPageCount(): number {
    return this.pdfDoc ? this.pdfDoc.numPages : 0;
  }

  /**
   * Get current page
   */
  getCurrentPage(): number {
    return this.currentPage;
  }

  /**
   * Get current scale
   */
  getCurrentScale(): number {
    return this.currentScale;
  }

  /**
   * Get current scroll position
   */
  getCurrentScrollPosition(): { scrollTop: number; scrollLeft: number } | null {
    const viewer = document.getElementById("pdfjs-viewer");
    if (viewer) {
      return {
        scrollTop: viewer.scrollTop,
        scrollLeft: viewer.scrollLeft,
      };
    }
    return null;
  }

  /**
   * Get current color mode
   */
  getColorMode(): "light" | "dark" {
    return this.colorMode;
  }

  /**
   * Set render quality (1.0 = standard, 2.0 = 2x, 4.0 = ~300 DPI)
   */
  setRenderQuality(quality: number): void {
    if (quality < 0.5 || quality > 5.0) {
      console.warn("[PDFJSViewer] Quality must be between 0.5 and 5.0");
      return;
    }

    // Save scroll before re-render
    const viewer = document.getElementById("pdfjs-viewer");
    if (viewer) {
      this.savedScrollPosition = {
        scrollTop: viewer.scrollTop,
        scrollLeft: viewer.scrollLeft,
      };
    }

    this.renderQuality = quality;
    console.log("[PDFJSViewer] Render quality changed to:", quality + "x");

    // Re-render with new quality
    if (this.pdfDoc) {
      this.renderAllPages();
    }
  }

  /**
   * Get current render quality
   */
  getRenderQuality(): number {
    return this.renderQuality;
  }
}

// EOF
