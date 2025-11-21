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
        console.log('[CanvasManager] initCanvas() called');

        const canvasElement = document.getElementById('sigma-canvas') as HTMLCanvasElement;
        if (!canvasElement) {
            console.error('[CanvasManager] Canvas element #sigma-canvas not found in DOM');
            return;
        }
        console.log('[CanvasManager] Canvas element found:', canvasElement);

        if (typeof fabric === 'undefined') {
            console.error('[CanvasManager] Fabric.js is not loaded!');
            return;
        }
        console.log('[CanvasManager] Fabric.js is loaded');

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

            console.log(`[CanvasManager] Canvas initialized: ${defaultWidth}×${defaultHeight}px`);

            if (this.gridEnabled) {
                this.drawGrid();
            }
        } catch (error) {
            console.error('[CanvasManager] Error initializing canvas:', error);
        }
    }

    /**
     * Draw grid lines on canvas
     */
    public drawGrid(isDark: boolean = false): void {
        if (!this.canvas) return;

        const width = this.canvas.getWidth();
        const height = this.canvas.getHeight();
        this.clearGrid();

        // Grid color adapts to theme: light gray for light mode, darker gray for dark mode
        const gridColor = isDark ? '#404040' : '#e5e5e5';

        // Column guide positions: 0.5, 1.0, 1.5 columns (45mm, 90mm, 135mm)
        const columnGuides = [45, 90, 135];
        const columnLineColor = '#0080c0'; // Blue color (same as /vis/)

        // Draw vertical grid lines (1mm spacing)
        for (let i = 0; i <= width / CANVAS_CONSTANTS.GRID_SIZE; i++) {
            const x = i * CANVAS_CONSTANTS.GRID_SIZE;
            const line = new fabric.Line([x, 0, x, height], {
                stroke: gridColor,
                strokeWidth: i % 10 === 0 ? 1 : 0.5,  // Major lines every 10mm
                selectable: false,
                evented: false,
                hoverCursor: 'default',
                excludeFromExport: true,  // CRITICAL: not in exports
            } as any);
            line.set('id', 'grid-line');
            this.canvas.add(line);
            this.canvas.sendToBack(line);
        }

        // Draw horizontal grid lines (1mm spacing)
        for (let i = 0; i <= height / CANVAS_CONSTANTS.GRID_SIZE; i++) {
            const y = i * CANVAS_CONSTANTS.GRID_SIZE;
            const line = new fabric.Line([0, y, width, y], {
                stroke: gridColor,
                strokeWidth: i % 10 === 0 ? 1 : 0.5,  // Major lines every 10mm
                selectable: false,
                evented: false,
                hoverCursor: 'default',
                excludeFromExport: true,  // CRITICAL: not in exports
            } as any);
            line.set('id', 'grid-line');
            this.canvas.add(line);
            this.canvas.sendToBack(line);
        }

        // Draw column guide lines at 45mm, 90mm, 135mm (0.5, 1.0, 1.5 columns)
        columnGuides.forEach((columnMm) => {
            const x = columnMm * CANVAS_CONSTANTS.MM_TO_PX;
            if (x <= width) {
                const guideLine = new fabric.Line([x, 0, x, height], {
                    stroke: columnLineColor,
                    strokeWidth: 1.5,
                    strokeDashArray: [10, 5],
                    selectable: false,
                    evented: false,
                    hoverCursor: 'default',
                    excludeFromExport: true,
                } as any);
                guideLine.set('id', 'column-guide');
                this.canvas.add(guideLine);
                this.canvas.sendToBack(guideLine);
            }
        });

        this.canvas.renderAll();
        console.log('[CanvasManager] Grid drawn');
    }

    /**
     * Clear grid lines from canvas
     */
    public clearGrid(): void {
        if (!this.canvas) return;

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
        const canvasContainer = document.getElementById('canvas-container');

        if (canvasContainer) {
            if (this.gridEnabled) {
                canvasContainer.style.backgroundImage =
                    'linear-gradient(rgba(128, 128, 128, 0.1) 1px, transparent 1px), ' +
                    'linear-gradient(90deg, rgba(128, 128, 128, 0.1) 1px, transparent 1px)';
                canvasContainer.style.backgroundSize = '20px 20px';
            } else {
                canvasContainer.style.backgroundImage = 'none';
            }
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
