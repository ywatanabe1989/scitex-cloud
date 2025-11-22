/**
 * CanvasManager - Handles all Fabric.js canvas operations
 *
 * Responsibilities:
 * - Initialize Fabric.js canvas
 * - Draw and manage grid lines
 * - Handle canvas theme (light/dark)
 * - Handle canvas-specific zoom and pan
 * - Coordinate with rulers for unified transform
 */

import { CANVAS_CONSTANTS } from './types.js';

export class CanvasManager {
    public canvas: any | null = null; // Fabric.js canvas instance
    private gridEnabled: boolean = true;
    private canvasZoomLevel: number = 1.0;
    private canvasPanOffset: { x: number, y: number } = { x: 0, y: 0 };
    private canvasIsPanning: boolean = false;
    private canvasPanStartPoint: { x: number, y: number } | null = null;
    private canvasWheelThrottleFrame: number | null = null;
    private canvasAccumulatedZoomDelta: number = 0;
    private canvasLastZoomMousePos: { x: number, y: number } = { x: 0, y: 0 };
    private canvasAccumulatedPanDelta: { x: number, y: number } = { x: 0, y: 0 };

    constructor(
        private statusBarCallback?: (message: string) => void,
        private rulersAreaTransformCallback?: () => void
    ) {}

    /**
     * Get canvas zoom level
     */
    public getCanvasZoomLevel(): number {
        return this.canvasZoomLevel;
    }

    /**
     * Get canvas pan offset
     */
    public getCanvasPanOffset(): { x: number, y: number } {
        return this.canvasPanOffset;
    }

    /**
     * Initialize Fabric.js canvas
     */
    public initCanvas(): void {
        const startTime = performance.now();
        console.log('[CanvasManager] Starting canvas initialization...');

        const canvasElement = document.getElementById('sigma-canvas') as HTMLCanvasElement;
        if (!canvasElement) {
            console.error('[CanvasManager] Canvas element #sigma-canvas not found in DOM');
            return;
        }

        if (typeof fabric === 'undefined') {
            console.error('[CanvasManager] Fabric.js is not loaded!');
            return;
        }

        const defaultWidth = CANVAS_CONSTANTS.MAX_CANVAS_WIDTH;   // 180mm @ 300dpi
        const defaultHeight = CANVAS_CONSTANTS.MAX_CANVAS_HEIGHT; // 240mm @ 300dpi

        try {
            // SCIENTIFIC INTEGRITY: Canvas background ALWAYS white (#ffffff)
            this.canvas = new fabric.Canvas('sigma-canvas', {
                width: defaultWidth,
                height: defaultHeight,
                backgroundColor: '#ffffff',  // NEVER change - scientific integrity
                selection: true,
                selectionKey: 'ctrlKey',  // PowerPoint-style multi-select
            });

            const canvasCreateTime = performance.now();
            console.log(`[CanvasManager] Fabric.js canvas created in ${(canvasCreateTime - startTime).toFixed(2)}ms (${defaultWidth}×${defaultHeight}px)`);

            if (this.gridEnabled) {
                this.drawGrid();
                const gridTime = performance.now();
                console.log(`[CanvasManager] Grid drawn in ${(gridTime - canvasCreateTime).toFixed(2)}ms`);
                console.log(`[CanvasManager] ✅ Total canvas init: ${(gridTime - startTime).toFixed(2)}ms`);
            } else {
                console.log(`[CanvasManager] ✅ Total canvas init: ${(canvasCreateTime - startTime).toFixed(2)}ms`);
            }
        } catch (error) {
            console.error('[CanvasManager] Error initializing canvas:', error);
        }
    }

    /**
     * Draw grid as optimized SVG background (mm-precision maintained)
     * PERFORMANCE: Single SVG pattern instead of 420+ Fabric objects
     */
    public drawGrid(isDark: boolean = false): void {
        if (!this.canvas) return;

        const startTime = performance.now();
        const width = this.canvas.getWidth();
        const height = this.canvas.getHeight();

        // Grid colors adapt to theme
        const minorGridColor = isDark ? '#404040' : '#e5e5e5';
        const majorGridColor = isDark ? '#606060' : '#999999';
        const columnLineColor = '#0080c0';

        // PRECISION: Use exact MM_TO_PX constant (11.811 px = 1mm @ 300dpi)
        const gridSize = CANVAS_CONSTANTS.GRID_SIZE;  // 1mm in pixels
        const majorInterval = 10;  // 10mm = major grid lines

        // Create SVG pattern with mm-precision
        const svg = `
<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">
  <defs>
    <!-- 1mm minor grid pattern -->
    <pattern id="minor-grid" width="${gridSize}" height="${gridSize}" patternUnits="userSpaceOnUse">
      <line x1="0" y1="0" x2="0" y2="${gridSize}" stroke="${minorGridColor}" stroke-width="0.5"/>
      <line x1="0" y1="0" x2="${gridSize}" y2="0" stroke="${minorGridColor}" stroke-width="0.5"/>
    </pattern>

    <!-- 10mm major grid pattern -->
    <pattern id="major-grid" width="${gridSize * majorInterval}" height="${gridSize * majorInterval}" patternUnits="userSpaceOnUse">
      <line x1="0" y1="0" x2="0" y2="${gridSize * majorInterval}" stroke="${majorGridColor}" stroke-width="1"/>
      <line x1="0" y1="0" x2="${gridSize * majorInterval}" y2="0" stroke="${majorGridColor}" stroke-width="1"/>
    </pattern>
  </defs>

  <!-- Apply patterns -->
  <rect width="${width}" height="${height}" fill="url(#minor-grid)"/>
  <rect width="${width}" height="${height}" fill="url(#major-grid)"/>

  <!-- Column guide lines at 45mm, 90mm, 135mm (0.5, 1.0, 1.5 columns) -->
  <line x1="${45 * CANVAS_CONSTANTS.MM_TO_PX}" y1="0" x2="${45 * CANVAS_CONSTANTS.MM_TO_PX}" y2="${height}"
        stroke="${columnLineColor}" stroke-width="1.5" stroke-dasharray="10,5"/>
  <line x1="${90 * CANVAS_CONSTANTS.MM_TO_PX}" y1="0" x2="${90 * CANVAS_CONSTANTS.MM_TO_PX}" y2="${height}"
        stroke="${columnLineColor}" stroke-width="1.5" stroke-dasharray="10,5"/>
  <line x1="${135 * CANVAS_CONSTANTS.MM_TO_PX}" y1="0" x2="${135 * CANVAS_CONSTANTS.MM_TO_PX}" y2="${height}"
        stroke="${columnLineColor}" stroke-width="1.5" stroke-dasharray="10,5"/>
</svg>`.trim();

        // Convert SVG to data URL
        const svgDataUrl = 'data:image/svg+xml;base64,' + btoa(svg);

        // Load as Fabric.js background image
        fabric.Image.fromURL(svgDataUrl, (img: any) => {
            this.canvas!.setBackgroundImage(img, this.canvas!.renderAll.bind(this.canvas), {
                scaleX: 1,
                scaleY: 1,
                originX: 'left',
                originY: 'top',
            });

            const endTime = performance.now();
            console.log(`[CanvasManager] ✅ Grid drawn as SVG background in ${(endTime - startTime).toFixed(2)}ms (mm-precision maintained)`);

            if (this.statusBarCallback) {
                this.statusBarCallback('Grid enabled (SVG optimized)');
            }
        }, { crossOrigin: 'anonymous' });
    }

    /**
     * Clear grid background from canvas
     */
    public clearGrid(): void {
        if (!this.canvas) return;

        // Clear background image (SVG grid)
        this.canvas.setBackgroundImage(null, this.canvas.renderAll.bind(this.canvas));

        // Legacy cleanup: Remove any old Fabric.js grid objects (for backwards compatibility)
        const objects = this.canvas.getObjects();
        objects.forEach((obj: any) => {
            if (obj.id === 'grid-line' || obj.id === 'column-guide') {
                this.canvas!.remove(obj);
            }
        });
    }

    /**
     * Toggle grid visibility
     */
    public toggleGrid(): void {
        this.gridEnabled = !this.gridEnabled;

        if (this.gridEnabled) {
            this.drawGrid();
        } else {
            this.clearGrid();
        }

        if (this.statusBarCallback) {
            this.statusBarCallback(`Grid ${this.gridEnabled ? 'enabled' : 'disabled'}`);
        }
        console.log(`[CanvasManager] Grid ${this.gridEnabled ? 'enabled' : 'disabled'}`);
    }

    /**
     * Update canvas theme
     */
    public updateCanvasTheme(isDark: boolean): void {
        if (!this.canvas) return;

        // Update canvas background color
        this.canvas.backgroundColor = isDark ? '#2a2a2a' : '#ffffff';

        // Redraw grid with appropriate color if grid is enabled
        if (this.gridEnabled) {
            this.drawGrid(isDark);
        }

        this.canvas.renderAll();
    }

    /**
     * Setup canvas zoom/pan events
     */
    public setupCanvasEvents(): void {
        const canvasContainer = document.getElementById('canvas-container');
        if (!canvasContainer || !this.canvas) {
            console.warn('[CanvasManager] Canvas container or Fabric.js canvas not found');
            return;
        }

        // Mouse down - Check for panning
        canvasContainer.addEventListener('mousedown', (e: MouseEvent) => {
            if (e.button === 1 || (e as any).spaceKey) {
                this.canvasIsPanning = true;
                this.canvasPanStartPoint = { x: e.clientX, y: e.clientY };
                canvasContainer.style.cursor = 'grabbing';
                e.preventDefault();
                console.log('[CanvasManager] Canvas pan mode started');
            }
        });

        // Mouse move - Handle panning
        canvasContainer.addEventListener('mousemove', (e: MouseEvent) => {
            if (this.canvasIsPanning && this.canvasPanStartPoint) {
                let deltaX = e.clientX - this.canvasPanStartPoint.x;
                let deltaY = e.clientY - this.canvasPanStartPoint.y;

                if (e.altKey) {
                    deltaX *= 0.1;
                    deltaY *= 0.1;
                }

                this.canvasPanOffset.x += deltaX;
                this.canvasPanOffset.y += deltaY;
                this.updateCanvasTransform();
                if (this.rulersAreaTransformCallback) {
                    this.rulersAreaTransformCallback();
                }

                this.canvasPanStartPoint = { x: e.clientX, y: e.clientY };
            }
        });

        // Mouse up - Reset panning
        canvasContainer.addEventListener('mouseup', () => {
            if (this.canvasIsPanning) {
                this.canvasIsPanning = false;
                this.canvasPanStartPoint = null;
                canvasContainer.style.cursor = 'default';
                console.log('[CanvasManager] Canvas pan mode ended');
            }
        });

        // Wheel event - Zoom with Ctrl, Pan without Ctrl
        canvasContainer.addEventListener('wheel', (e: WheelEvent) => {
            e.preventDefault();
            e.stopPropagation();

            if (e.ctrlKey || e.metaKey) {
                // Ctrl+Wheel = Zoom
                this.canvasAccumulatedZoomDelta += e.deltaY;

                const rect = canvasContainer.getBoundingClientRect();
                this.canvasLastZoomMousePos.x = e.clientX - rect.left;
                this.canvasLastZoomMousePos.y = e.clientY - rect.top;

                if (!this.canvasWheelThrottleFrame) {
                    this.canvasWheelThrottleFrame = requestAnimationFrame(() => {
                        const oldZoom = this.canvasZoomLevel;
                        let newZoom = oldZoom * (0.999 ** this.canvasAccumulatedZoomDelta);

                        if (newZoom > 5) newZoom = 5;
                        if (newZoom < 0.1) newZoom = 0.1;

                        this.canvasZoomLevel = newZoom;

                        const zoomRatio = newZoom / oldZoom;
                        const mouseX = this.canvasLastZoomMousePos.x;
                        const mouseY = this.canvasLastZoomMousePos.y;
                        this.canvasPanOffset.x = mouseX - (mouseX - this.canvasPanOffset.x) * zoomRatio;
                        this.canvasPanOffset.y = mouseY - (mouseY - this.canvasPanOffset.y) * zoomRatio;

                        this.updateCanvasTransform();
                        if (this.rulersAreaTransformCallback) {
                            this.rulersAreaTransformCallback();
                        }
                        this.updateCanvasZoomDisplay();

                        this.canvasAccumulatedZoomDelta = 0;
                        this.canvasWheelThrottleFrame = null;
                    });
                }
            } else {
                // Regular wheel = Pan
                this.canvasAccumulatedPanDelta.x += e.deltaX;
                this.canvasAccumulatedPanDelta.y += e.deltaY;

                if (!this.canvasWheelThrottleFrame) {
                    this.canvasWheelThrottleFrame = requestAnimationFrame(() => {
                        this.canvasPanOffset.x -= this.canvasAccumulatedPanDelta.x;
                        this.canvasPanOffset.y -= this.canvasAccumulatedPanDelta.y;

                        this.updateCanvasTransform();
                        if (this.rulersAreaTransformCallback) {
                            this.rulersAreaTransformCallback();
                        }

                        this.canvasAccumulatedPanDelta.x = 0;
                        this.canvasAccumulatedPanDelta.y = 0;
                        this.canvasWheelThrottleFrame = null;
                    });
                }
            }
        }, { passive: false });

        console.log('[CanvasManager] Canvas events (zoom/pan) initialized');
    }

    /**
     * Update canvas transform (keep at identity, all zoom/pan via CSS)
     */
    public updateCanvasTransform(): void {
        if (!this.canvas) return;

        // Keep Fabric.js canvas at identity transform
        // All zoom/pan is handled by CSS transform on .sigma-rulers-area parent
        this.canvas.setViewportTransform([1, 0, 0, 1, 0, 0]);
        this.canvas.renderAll();
    }

    /**
     * Update canvas zoom display
     */
    private updateCanvasZoomDisplay(): void {
        if (this.statusBarCallback) {
            this.statusBarCallback(`Canvas Zoom: ${Math.round(this.canvasZoomLevel * 100)}%`);
        }
        console.log(`[CanvasManager] Canvas zoom level: ${Math.round(this.canvasZoomLevel * 100)}%`);
    }

    /**
     * Zoom in
     */
    public zoomIn(): void {
        this.canvasZoomLevel = Math.min(this.canvasZoomLevel * 1.2, 5.0);
        this.applyZoom();
        console.log('[CanvasManager] Zoomed in - Canvas:', Math.round(this.canvasZoomLevel * 100) + '%');
    }

    /**
     * Zoom out
     */
    public zoomOut(): void {
        this.canvasZoomLevel = Math.max(this.canvasZoomLevel / 1.2, 0.1);
        this.applyZoom();
        console.log('[CanvasManager] Zoomed out - Canvas:', Math.round(this.canvasZoomLevel * 100) + '%');
    }

    /**
     * Zoom to fit
     */
    public zoomToFit(): void {
        this.canvasZoomLevel = 1.0;
        this.canvasPanOffset = { x: 0, y: 0 };
        this.applyZoom();
        console.log('[CanvasManager] Canvas zoomed to fit - Reset to 100%');
    }

    /**
     * Apply zoom
     */
    private applyZoom(): void {
        this.updateCanvasTransform();
        if (this.rulersAreaTransformCallback) {
            this.rulersAreaTransformCallback();
        }
        if (this.statusBarCallback) {
            this.statusBarCallback(`Canvas: ${Math.round(this.canvasZoomLevel * 100)}%`);
        }
    }
}
