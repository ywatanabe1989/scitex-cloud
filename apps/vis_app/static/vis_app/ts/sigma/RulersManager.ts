/**
 * RulersManager - Handles all ruler rendering, unit toggling, and dragging
 *
 * Responsibilities:
 * - Initialize and draw all four rulers (top, bottom, left, right)
 * - Toggle between mm and inch units
 * - Render ruler markings with appropriate intervals
 * - Handle ruler dragging for canvas panning
 * - Synchronize ruler transform with canvas zoom/pan
 */

import { RulerUnit, CANVAS_CONSTANTS } from './types.js';

export class RulersManager {
    private rulerUnit: RulerUnit = 'mm';
    private canvasZoomLevel: number = 1.0;
    private canvasPanOffset: { x: number, y: number } = { x: 0, y: 0 };
    private canvasIsPanning: boolean = false;
    private canvasPanStartPoint: { x: number, y: number } | null = null;

    constructor(
        private canvas: any, // Fabric.js canvas instance
        private statusBarCallback?: (message: string) => void
    ) {}

    /**
     * Get current ruler unit
     */
    public getRulerUnit(): RulerUnit {
        return this.rulerUnit;
    }

    /**
     * Set canvas zoom level (called from main editor)
     */
    public setCanvasZoomLevel(level: number): void {
        this.canvasZoomLevel = level;
    }

    /**
     * Set canvas pan offset (called from main editor)
     */
    public setCanvasPanOffset(offset: { x: number, y: number }): void {
        this.canvasPanOffset = offset;
    }

    /**
     * Get canvas pan offset (for coordination with other managers)
     */
    public getCanvasPanOffset(): { x: number, y: number } {
        return this.canvasPanOffset;
    }

    /**
     * Get canvas zoom level (for coordination with other managers)
     */
    public getCanvasZoomLevel(): number {
        return this.canvasZoomLevel;
    }

    /**
     * Initialize rulers on canvas load
     */
    public initializeRulers(): void {
        this.drawRulers();
    }

    /**
     * Draw all rulers based on canvas dimensions
     */
    public drawRulers(): void {
        if (!this.canvas) return;

        const canvasWidth = this.canvas.getWidth();
        const canvasHeight = this.canvas.getHeight();
        const dpi = CANVAS_CONSTANTS.DPI;

        // Render all four rulers
        this.renderHorizontalRuler(canvasWidth, dpi, 'ruler-h');  // Top
        this.renderHorizontalRuler(canvasWidth, dpi, 'ruler-b');  // Bottom
        this.renderVerticalRuler(canvasHeight, dpi, 'ruler-v');   // Left
        this.renderVerticalRuler(canvasHeight, dpi, 'ruler-r');   // Right
    }

    /**
     * Toggle ruler unit between mm and inch
     */
    public toggleRulerUnit(): void {
        this.rulerUnit = this.rulerUnit === 'mm' ? 'inch' : 'mm';

        // Update button label
        const label = document.getElementById('ruler-unit-label');
        if (label) {
            label.textContent = this.rulerUnit;
        }

        // Redraw rulers with new unit
        this.drawRulers();

        console.log(`Ruler unit changed to: ${this.rulerUnit}`);
        if (this.statusBarCallback) {
            this.statusBarCallback(`Ruler units: ${this.rulerUnit}`);
        }
    }

    /**
     * Render horizontal ruler with mm or inch markings
     */
    private renderHorizontalRuler(width: number, dpi: number, rulerId: string = 'ruler-h'): void {
        const svg = document.getElementById(rulerId);
        if (!svg) return;

        svg.innerHTML = '';
        const rulerHeight = 60;
        svg.setAttribute('width', width.toString());
        svg.setAttribute('height', rulerHeight.toString());
        svg.setAttribute('viewBox', `0 0 ${width} ${rulerHeight}`);
        svg.style.width = `${width}px`;
        svg.style.height = `${rulerHeight}px`;

        if (this.rulerUnit === 'mm') {
            this.renderHorizontalRulerMm(svg, width, dpi, rulerHeight);
        } else {
            this.renderHorizontalRulerInch(svg, width, dpi, rulerHeight);
        }
    }

    /**
     * Render horizontal ruler with mm markings
     */
    private renderHorizontalRulerMm(svg: HTMLElement, width: number, dpi: number, rulerHeight: number): void {
        // Convert pixels to mm (using DPI)
        const pxToMm = (px: number) => (px / dpi) * 25.4;
        const mmToPx = (mm: number) => (mm * dpi) / 25.4;

        const maxMm = pxToMm(width);
        const majorInterval = 10;  // 10mm
        const middleInterval = 5;   // 5mm
        const minorInterval = 1;    // 1mm

        // Draw all ticks
        for (let mm = minorInterval; mm <= maxMm; mm += minorInterval) {
            const x = mmToPx(mm);
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', x.toString());
            line.setAttribute('x2', x.toString());

            if (mm % majorInterval === 0) {
                // Major tick (10mm)
                line.setAttribute('y1', '40');
                line.setAttribute('y2', rulerHeight.toString());
                line.setAttribute('stroke', '#999');
                line.setAttribute('stroke-width', '1.5');
                svg.appendChild(line);

                // Label
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', x.toString());
                text.setAttribute('y', '35');
                text.setAttribute('text-anchor', 'middle');
                text.setAttribute('font-size', '11');
                text.setAttribute('fill', '#666');
                text.textContent = `${mm}mm`;
                svg.appendChild(text);
            } else if (mm % middleInterval === 0) {
                // Middle tick (5mm)
                line.setAttribute('y1', '48');
                line.setAttribute('y2', rulerHeight.toString());
                line.setAttribute('stroke', '#999');
                line.setAttribute('stroke-width', '1');
                svg.appendChild(line);
            } else {
                // Minor tick (1mm)
                line.setAttribute('y1', '54');
                line.setAttribute('y2', rulerHeight.toString());
                line.setAttribute('stroke', '#ccc');
                line.setAttribute('stroke-width', '0.5');
                svg.appendChild(line);
            }
        }

        // Add column width markers (0.5, 1.0, 1.5 columns)
        // Column widths: 0.5=45mm, 1.0=90mm, 1.5=135mm
        const columnMarkers = [
            { mm: 45, label: '0.5 col' },
            { mm: 90, label: '1.0 col' },
            { mm: 135, label: '1.5 col' }
        ];

        columnMarkers.forEach(marker => {
            const x = mmToPx(marker.mm);
            if (x <= width) {
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', x.toString());
                text.setAttribute('y', '10');
                text.setAttribute('text-anchor', 'middle');
                text.setAttribute('font-size', '9');
                text.setAttribute('fill', '#0080c0');
                text.setAttribute('font-weight', '600');
                text.textContent = marker.label;
                svg.appendChild(text);
            }
        });
    }

    /**
     * Render horizontal ruler with inch markings
     */
    private renderHorizontalRulerInch(svg: HTMLElement, width: number, dpi: number, rulerHeight: number): void {
        const pxToInch = (px: number) => px / dpi;
        const inchToPx = (inch: number) => inch * dpi;

        const maxInch = pxToInch(width);

        // Draw full inch markers
        for (let inch = 0; inch <= maxInch; inch++) {
            const x = inchToPx(inch);
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', x.toString());
            line.setAttribute('x2', x.toString());
            line.setAttribute('y1', '40');
            line.setAttribute('y2', rulerHeight.toString());
            line.setAttribute('stroke', '#999');
            line.setAttribute('stroke-width', '1.5');
            svg.appendChild(line);

            // Label
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', x.toString());
            text.setAttribute('y', '35');
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('font-size', '11');
            text.setAttribute('fill', '#666');
            text.textContent = `${inch}"`;
            svg.appendChild(text);
        }

        // Draw fractional inch markers (1/2, 1/4, 1/8, 1/16)
        const fractions = [
            { divisor: 2, y: 48, stroke: '#999', width: '1' },      // 1/2"
            { divisor: 4, y: 51, stroke: '#999', width: '0.8' },    // 1/4"
            { divisor: 8, y: 54, stroke: '#ccc', width: '0.6' },    // 1/8"
            { divisor: 16, y: 56, stroke: '#ccc', width: '0.4' }    // 1/16"
        ];

        fractions.forEach(frac => {
            for (let inch = 0; inch <= maxInch; inch++) {
                for (let i = 1; i < frac.divisor; i++) {
                    // Skip if this fraction is already covered by a larger one
                    if (i % 2 === 0 && frac.divisor > 2) continue;
                    if (i % 4 === 0 && frac.divisor > 4) continue;
                    if (i % 8 === 0 && frac.divisor > 8) continue;

                    const position = inch + (i / frac.divisor);
                    const x = inchToPx(position);

                    if (x <= width) {
                        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                        line.setAttribute('x1', x.toString());
                        line.setAttribute('x2', x.toString());
                        line.setAttribute('y1', frac.y.toString());
                        line.setAttribute('y2', rulerHeight.toString());
                        line.setAttribute('stroke', frac.stroke);
                        line.setAttribute('stroke-width', frac.width);
                        svg.appendChild(line);
                    }
                }
            }
        });

        // Add column width markers (convert from mm to inch)
        // Column widths: 0.5=45mm≈1.77", 1.0=90mm≈3.54", 1.5=135mm≈5.31"
        const columnMarkersInch = [
            { inch: 45 / 25.4, label: '0.5 col' },
            { inch: 90 / 25.4, label: '1.0 col' },
            { inch: 135 / 25.4, label: '1.5 col' }
        ];

        columnMarkersInch.forEach(marker => {
            const x = inchToPx(marker.inch);
            if (x <= width) {
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', x.toString());
                text.setAttribute('y', '10');
                text.setAttribute('text-anchor', 'middle');
                text.setAttribute('font-size', '9');
                text.setAttribute('fill', '#0080c0');
                text.setAttribute('font-weight', '600');
                text.textContent = marker.label;
                svg.appendChild(text);
            }
        });
    }

    /**
     * Render vertical ruler with mm or inch markings
     */
    private renderVerticalRuler(height: number, dpi: number, rulerId: string = 'ruler-v'): void {
        const svg = document.getElementById(rulerId);
        if (!svg) return;

        svg.innerHTML = '';
        const rulerWidth = 60;
        svg.setAttribute('width', rulerWidth.toString());
        svg.setAttribute('height', height.toString());
        svg.setAttribute('viewBox', `0 0 ${rulerWidth} ${height}`);
        svg.style.width = `${rulerWidth}px`;
        svg.style.height = `${height}px`;

        if (this.rulerUnit === 'mm') {
            this.renderVerticalRulerMm(svg, height, dpi, rulerWidth);
        } else {
            this.renderVerticalRulerInch(svg, height, dpi, rulerWidth);
        }
    }

    /**
     * Render vertical ruler with mm markings
     */
    private renderVerticalRulerMm(svg: HTMLElement, height: number, dpi: number, rulerWidth: number): void {
        const pxToMm = (px: number) => (px / dpi) * 25.4;
        const mmToPx = (mm: number) => (mm * dpi) / 25.4;

        const maxMm = pxToMm(height);
        const majorInterval = 10;  // 10mm
        const middleInterval = 5;   // 5mm
        const minorInterval = 1;    // 1mm

        for (let mm = minorInterval; mm <= maxMm; mm += minorInterval) {
            const y = mmToPx(mm);
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('y1', y.toString());
            line.setAttribute('y2', y.toString());

            if (mm % majorInterval === 0) {
                // Major tick
                line.setAttribute('x1', '40');
                line.setAttribute('x2', rulerWidth.toString());
                line.setAttribute('stroke', '#999');
                line.setAttribute('stroke-width', '1.5');
                svg.appendChild(line);

                // Label (rotated)
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', '30');
                text.setAttribute('y', y.toString());
                text.setAttribute('text-anchor', 'middle');
                text.setAttribute('dominant-baseline', 'middle');
                text.setAttribute('font-size', '11');
                text.setAttribute('fill', '#666');
                text.setAttribute('transform', `rotate(-90, 30, ${y})`);
                text.textContent = `${mm}mm`;
                svg.appendChild(text);
            } else if (mm % middleInterval === 0) {
                // Middle tick
                line.setAttribute('x1', '48');
                line.setAttribute('x2', rulerWidth.toString());
                line.setAttribute('stroke', '#999');
                line.setAttribute('stroke-width', '1');
                svg.appendChild(line);
            } else {
                // Minor tick
                line.setAttribute('x1', '54');
                line.setAttribute('x2', rulerWidth.toString());
                line.setAttribute('stroke', '#ccc');
                line.setAttribute('stroke-width', '0.5');
                svg.appendChild(line);
            }
        }
    }

    /**
     * Render vertical ruler with inch markings
     */
    private renderVerticalRulerInch(svg: HTMLElement, height: number, dpi: number, rulerWidth: number): void {
        const pxToInch = (px: number) => px / dpi;
        const inchToPx = (inch: number) => inch * dpi;

        const maxInch = pxToInch(height);

        // Draw full inch markers
        for (let inch = 0; inch <= maxInch; inch++) {
            const y = inchToPx(inch);
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('y1', y.toString());
            line.setAttribute('y2', y.toString());
            line.setAttribute('x1', '40');
            line.setAttribute('x2', rulerWidth.toString());
            line.setAttribute('stroke', '#999');
            line.setAttribute('stroke-width', '1.5');
            svg.appendChild(line);

            // Label (rotated)
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', '30');
            text.setAttribute('y', y.toString());
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('dominant-baseline', 'middle');
            text.setAttribute('font-size', '11');
            text.setAttribute('fill', '#666');
            text.setAttribute('transform', `rotate(-90, 30, ${y})`);
            text.textContent = `${inch}"`;
            svg.appendChild(text);
        }

        // Draw fractional inch markers
        const fractions = [
            { divisor: 2, x: 48, stroke: '#999', width: '1' },
            { divisor: 4, x: 51, stroke: '#999', width: '0.8' },
            { divisor: 8, x: 54, stroke: '#ccc', width: '0.6' },
            { divisor: 16, x: 56, stroke: '#ccc', width: '0.4' }
        ];

        fractions.forEach(frac => {
            for (let inch = 0; inch <= maxInch; inch++) {
                for (let i = 1; i < frac.divisor; i++) {
                    if (i % 2 === 0 && frac.divisor > 2) continue;
                    if (i % 4 === 0 && frac.divisor > 4) continue;
                    if (i % 8 === 0 && frac.divisor > 8) continue;

                    const position = inch + (i / frac.divisor);
                    const y = inchToPx(position);

                    if (y <= height) {
                        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                        line.setAttribute('y1', y.toString());
                        line.setAttribute('y2', y.toString());
                        line.setAttribute('x1', frac.x.toString());
                        line.setAttribute('x2', rulerWidth.toString());
                        line.setAttribute('stroke', frac.stroke);
                        line.setAttribute('stroke-width', frac.width);
                        svg.appendChild(line);
                    }
                }
            }
        });
    }

    /**
     * Setup ruler dragging for canvas panning (transform-based)
     */
    public setupRulerDragging(): void {
        const rulerH = document.getElementById('ruler-h');
        const rulerV = document.getElementById('ruler-v');
        const rulerCorners = document.querySelectorAll('.ruler-corner');

        const rulers = [rulerH, rulerV, ...Array.from(rulerCorners)].filter(r => r) as HTMLElement[];

        rulers.forEach(ruler => {
            ruler.style.cursor = 'grab';

            ruler.addEventListener('mousedown', (e) => {
                e.preventDefault();
                this.canvasIsPanning = true;
                this.canvasPanStartPoint = { x: e.clientX, y: e.clientY };
                ruler.style.cursor = 'grabbing';
            });

            ruler.addEventListener('mouseenter', () => {
                if (!this.canvasIsPanning) ruler.style.cursor = 'grab';
            });

            ruler.addEventListener('mouseleave', () => {
                if (!this.canvasIsPanning) ruler.style.cursor = 'default';
            });
        });

        document.addEventListener('mousemove', (e) => {
            if (this.canvasIsPanning && this.canvasPanStartPoint) {
                let deltaX = e.clientX - this.canvasPanStartPoint.x;
                let deltaY = e.clientY - this.canvasPanStartPoint.y;

                if (e.altKey) {
                    deltaX *= 0.1;
                    deltaY *= 0.1;
                }

                this.canvasPanOffset.x += deltaX;
                this.canvasPanOffset.y += deltaY;
                this.updateRulersAreaTransform();

                this.canvasPanStartPoint = { x: e.clientX, y: e.clientY };
            }
        });

        document.addEventListener('mouseup', () => {
            if (this.canvasIsPanning) {
                this.canvasIsPanning = false;
                this.canvasPanStartPoint = null;

                rulers.forEach(ruler => {
                    ruler.style.cursor = 'grab';
                });
            }
        });

        console.log('[RulersManager] Ruler dragging (transform-based) initialized');
    }

    /**
     * Update transform on the entire rulers area (rulers + canvas together)
     */
    public updateRulersAreaTransform(): void {
        const rulersArea = document.querySelector('.sigma-rulers-area') as HTMLElement;
        if (rulersArea) {
            rulersArea.style.transform = `translate(${this.canvasPanOffset.x}px, ${this.canvasPanOffset.y}px) scale(${this.canvasZoomLevel})`;
            rulersArea.style.transformOrigin = 'top left';
        }
    }
}
