/**
 * SciTeX Vis - Scientific Figure Editor
 * Canvas-based editor using Fabric.js for publication-quality figures
 */

// Fabric.js is loaded via CDN in the template
declare const fabric: any;

console.log("[DEBUG] vis_app/static/vis_app/ts/editor.ts loaded");

interface JournalPreset {
    id: number;
    name: string;
    column_type: string;
    width_mm: number;
    height_mm: number | null;
    width_px: number;
    height_px: number | null;
    dpi: number;
    font_family: string;
    font_size_pt: number;
    line_width_pt: number;
}

interface PanelLayout {
    rows: number;
    cols: number;
    panels: string[];
}

interface PanelMetadata {
    id: string;
    position: string;  // 'A', 'B', 'C', etc.
    order: number;     // 0, 1, 2, etc.
    x: number;
    y: number;
    width: number;
    height: number;
    borderObject?: fabric.Rect;
    labelObject?: fabric.Text;
}

class VisEditor {
    private canvas: fabric.Canvas | null = null;
    private currentLayout: string = '1x1';
    private currentPreset: JournalPreset | null = null;
    private gridEnabled: boolean = true;
    private snapEnabled: boolean = true;
    private gridSize: number = 20; // pixels
    private panelBorders: fabric.Rect[] = [];
    private panelLabels: fabric.Text[] = [];
    private darkCanvasMode: boolean = false;  // For viewing comfort only
    private panelMetadata: PanelMetadata[] = [];  // Track panel info for swapping
    private labelStyle: 'uppercase' | 'lowercase' | 'numbers' = 'uppercase';
    private zoomLevel: number = 1.0;  // 100% = 1.0
    private rulerEnabled: boolean = true;

    // Undo/Redo system
    private history: string[] = [];
    private historyIndex: number = -1;
    private maxHistory: number = 50;  // Keep last 50 states

    // Auto-save
    private autoSaveKey: string = 'scitex_vis_autosave';
    private autoSaveTimer: any = null;

    // Rulers
    private rulerUnit: 'mm' | 'inches' = 'mm';
    private rulerVisible: boolean = true;

    // Font size standards (scientific publishing)
    private fontSizes = {
        panelLabel: 10,  // pt - panel labels
        title: 8,        // pt - axis titles/group names
        axisLabel: 7,    // pt - tick numbers
        tickLabel: 6,    // pt - insets (scale bar, etc.)
        legend: 6,       // pt
    };

    // Line thickness standards (mm)
    private lineThickness = {
        axis: 0.2,       // mm
        errorBar: 0.2,   // mm
        tick: 0.2,       // mm
        scaleBar: 0.3,   // mm
        rasterPlot: 0.2, // mm
        trace: 0.12,     // mm
    };

    // Scientific color palette
    private scientificColors = {
        blue: 'rgb(0,128,192)',
        red: 'rgb(255,70,50)',
        pink: 'rgb(255,150,200)',
        green: 'rgb(20,180,20)',
        yellow: 'rgb(230,160,20)',
        gray: 'rgb(128,128,128)',
        purple: 'rgb(200,50,255)',
        cyan: 'rgb(20,200,200)',
        brown: 'rgb(128,0,0)',
        navy: 'rgb(0,0,100)',
        orange: 'rgb(228,94,50)',  // Vermilion renamed to Orange
        black: 'rgb(0,0,0)',
        white: 'rgb(255,255,255)',
    };

    // Crosshair and alignment guides
    private crosshairEnabled: boolean = false;
    private crosshairH: HTMLElement | null = null;
    private crosshairV: HTMLElement | null = null;
    private alignmentGuidesEnabled: boolean = true;
    private currentColor: string = 'rgb(0,0,0)';  // Default black

    // Label ordering modes
    private labelOrdering: 'horizontal' | 'vertical' | 'custom' | 'original' = 'horizontal';
    private customLabelOrder: string[] = [];

    constructor() {
        this.init();
    }

    private init() {
        console.log("[VisEditor] Initializing...");

        // Initialize canvas
        this.initCanvas();

        // Set up event listeners
        this.setupEventListeners();

        // Set up file drop handling
        this.setupFileDropHandling();

        // Load journal presets
        this.loadJournalPresets();

        // Restore last session from localStorage
        this.restoreFromLocalStorage();

        // Set up auto-save
        this.setupAutoSave();

        // Draw rulers
        this.drawRulers();

        console.log("[VisEditor] Ready - Auto-save enabled");
    }

    // Quick tips removed - no longer needed

    private initCanvas() {
        const canvasElement = document.getElementById('vis-canvas') as HTMLCanvasElement;
        if (!canvasElement) {
            console.error("[VisEditor] Canvas element not found");
            return;
        }

        // Create Fabric canvas with default size (Nature single column)
        const defaultWidth = 1051;  // 89mm @ 300dpi
        const defaultHeight = 709;  // 60mm @ 300dpi

        // SCIENTIFIC INTEGRITY: Canvas background ALWAYS white (#ffffff)
        // regardless of UI theme (light/dark). This ensures exported figures
        // are publication-ready and theme-independent.
        this.canvas = new fabric.Canvas('vis-canvas', {
            width: defaultWidth,
            height: defaultHeight,
            backgroundColor: '#ffffff',  // NEVER change - scientific integrity
            selection: true,
        });

        // Draw initial grid
        if (this.gridEnabled) {
            this.drawGrid();
        }

        // Set up canvas events
        this.setupCanvasEvents();

        this.updateCanvasInfo();
    }

    private setupFileDropHandling() {
        const canvasWrapper = document.querySelector('.vis-canvas-wrapper') as HTMLElement;
        if (!canvasWrapper) return;

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            canvasWrapper.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        // Highlight drop zone
        canvasWrapper.addEventListener('dragenter', () => {
            canvasWrapper.classList.add('drag-over');
        });

        canvasWrapper.addEventListener('dragleave', (e: any) => {
            if (e.target === canvasWrapper) {
                canvasWrapper.classList.remove('drag-over');
            }
        });

        canvasWrapper.addEventListener('drop', (e: any) => {
            canvasWrapper.classList.remove('drag-over');

            const files = e.dataTransfer?.files;
            if (files && files.length > 0) {
                this.handleDroppedFiles(files);
            }
        });
    }

    private handleDroppedFiles(files: FileList) {
        Array.from(files).forEach((file) => {
            // Only handle image files
            if (!file.type.startsWith('image/')) {
                this.updateStatus(`Skipped ${file.name} (not an image)`);
                return;
            }

            // Read file and add to canvas
            const reader = new FileReader();
            reader.onload = (e) => {
                const imgData = e.target?.result as string;
                this.addImageToCanvas(imgData, file.name);
            };
            reader.readAsDataURL(file);
        });
    }

    private addImageToCanvas(imgDataURL: string, filename: string) {
        if (!this.canvas) return;

        fabric.Image.fromURL(imgDataURL, (img) => {
            // Scale image to fit in canvas if too large
            const maxWidth = this.canvas!.getWidth() * 0.8;
            const maxHeight = this.canvas!.getHeight() * 0.8;

            if (img.width! > maxWidth || img.height! > maxHeight) {
                const scale = Math.min(
                    maxWidth / img.width!,
                    maxHeight / img.height!
                );
                img.scale(scale);
            }

            // Center the image
            img.set({
                left: (this.canvas!.getWidth() - img.getScaledWidth()) / 2,
                top: (this.canvas!.getHeight() - img.getScaledHeight()) / 2,
                selectable: true,
                evented: true,
            });

            // Store filename in object
            (img as any).set('filename', filename);

            this.canvas!.add(img);
            this.canvas!.setActiveObject(img);
            this.canvas!.renderAll();

            this.updateStatus(`Added image: ${filename}`);
            console.log(`[VisEditor] Image added: ${filename}`);
        });
    }

    private setupCanvasEvents() {
        if (!this.canvas) return;

        // Object moving - snap to grid and show alignment guides
        this.canvas.on('object:moving', (e) => {
            if (!e.target) return;

            const obj = e.target;
            let left = obj.left || 0;
            let top = obj.top || 0;

            // Grid snapping
            if (this.snapEnabled) {
                const snapThreshold = this.gridSize;
                left = Math.round(left / snapThreshold) * snapThreshold;
                top = Math.round(top / snapThreshold) * snapThreshold;
            }

            // Smart alignment guides (align with other objects)
            if (this.alignmentGuidesEnabled) {
                const alignResult = this.findAlignmentTargets(obj, left, top);
                if (alignResult) {
                    left = alignResult.left;
                    top = alignResult.top;
                    this.showAlignmentGuides(alignResult.guides);
                } else {
                    this.hideAlignmentGuides();
                }
            }

            obj.set({ left, top });
        });

        // Clear alignment guides when movement stops
        this.canvas.on('object:modified', () => {
            this.hideAlignmentGuides();
        });

        // Selection changed
        this.canvas.on('selection:created', () => this.updatePropertiesPanel());
        this.canvas.on('selection:updated', () => this.updatePropertiesPanel());
        this.canvas.on('selection:cleared', () => this.clearPropertiesPanel());

        // Object modified - save to history
        this.canvas.on('object:modified', () => {
            this.updatePropertiesPanel();
            this.saveToHistory();
        });

        // Object added - save to history
        this.canvas.on('object:added', (e) => {
            // Don't save grid lines or panel groups to history
            const obj = e.target as any;
            if (obj && obj.id && (obj.id === 'grid-line' || obj.id.startsWith('panel-group'))) {
                return;
            }
            this.saveToHistory();
        });

        // Object removed - save to history
        this.canvas.on('object:removed', (e) => {
            const obj = e.target as any;
            if (obj && obj.id && (obj.id === 'grid-line' || obj.id.startsWith('panel-group'))) {
                return;
            }
            this.saveToHistory();
        });

        // Alt+Click: "Skewer selection" - show all objects under pointer
        this.canvas.on('mouse:down', (e) => {
            if (e.e.altKey || (e.e.ctrlKey && e.e.shiftKey)) {
                e.e.preventDefault();
                const pointer = this.canvas!.getPointer(e.e);
                this.showObjectsUnderPointer(pointer);
            }
        });
    }

    private setupEventListeners() {
        // Layout buttons
        document.querySelectorAll('[data-layout]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const layout = (e.currentTarget as HTMLElement).dataset.layout;
                if (layout) {
                    this.setLayout(layout);
                }
            });
        });

        // Journal preset selectors (both left panel and header)
        const presetSelectors = ['journal-preset', 'journal-preset-header'];
        presetSelectors.forEach(id => {
            const presetSelect = document.getElementById(id) as HTMLSelectElement;
            if (presetSelect) {
                presetSelect.addEventListener('change', async (e) => {
                    const presetId = (e.target as HTMLSelectElement).value;
                    if (presetId) {
                        await this.applyJournalPreset(parseInt(presetId));
                    }
                });
            }
        });

        // Tool buttons
        document.querySelectorAll('[data-tool]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tool = (e.currentTarget as HTMLElement).dataset.tool;
                if (tool) {
                    this.activateTool(tool);
                }
            });
        });

        // Grid toggle
        const gridToggle = document.getElementById('grid-toggle') as HTMLInputElement;
        if (gridToggle) {
            gridToggle.addEventListener('change', (e) => {
                this.gridEnabled = (e.target as HTMLInputElement).checked;
                if (this.gridEnabled) {
                    this.drawGrid();
                } else {
                    this.clearGrid();
                }
            });
        }

        // Snap toggle
        const snapToggle = document.getElementById('snap-toggle') as HTMLInputElement;
        if (snapToggle) {
            snapToggle.addEventListener('change', (e) => {
                this.snapEnabled = (e.target as HTMLInputElement).checked;
            });
        }

        // Dark canvas toggle (for viewing comfort - export always white!)
        const darkCanvasToggle = document.getElementById('dark-canvas-toggle') as HTMLInputElement;
        if (darkCanvasToggle) {
            darkCanvasToggle.addEventListener('change', (e) => {
                this.darkCanvasMode = (e.target as HTMLInputElement).checked;
                this.toggleCanvasBackground();
            });
        }

        // Ruler toggle
        const rulerToggle = document.getElementById('ruler-toggle') as HTMLInputElement;
        if (rulerToggle) {
            rulerToggle.addEventListener('change', (e) => {
                this.rulerVisible = (e.target as HTMLInputElement).checked;
                this.toggleRulers();
            });
        }

        // Ruler unit selector
        const rulerUnitSelect = document.getElementById('ruler-unit') as HTMLSelectElement;
        if (rulerUnitSelect) {
            rulerUnitSelect.addEventListener('change', (e) => {
                this.rulerUnit = (e.target as HTMLSelectElement).value as 'mm' | 'inches';
                this.drawRulers();
            });
        }

        // Label order selector
        const labelOrderSelect = document.getElementById('label-order') as HTMLSelectElement;
        if (labelOrderSelect) {
            labelOrderSelect.addEventListener('change', (e) => {
                this.labelOrdering = (e.target as HTMLSelectElement).value as any;
                this.updatePanelLabels();
            });
        }

        // Label style selector
        const labelStyleSelect = document.getElementById('label-style') as HTMLSelectElement;
        if (labelStyleSelect) {
            labelStyleSelect.addEventListener('change', (e) => {
                this.labelStyle = (e.target as HTMLSelectElement).value as any;
                this.updatePanelLabels();
            });
        }

        // Zoom controls
        const zoomFitBtn = document.getElementById('zoom-fit');
        if (zoomFitBtn) {
            zoomFitBtn.addEventListener('click', () => this.zoomToFit());
        }

        // Ctrl + Mouse scroll to zoom
        const canvasWrapper = document.querySelector('.vis-canvas-wrapper');
        if (canvasWrapper) {
            canvasWrapper.addEventListener('wheel', (e: WheelEvent) => {
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    // Scroll up = zoom in, scroll down = zoom out
                    if (e.deltaY < 0) {
                        this.zoomIn();
                    } else {
                        this.zoomOut();
                    }
                }
            }, { passive: false });
        }

        // Export buttons
        const exportPngBtn = document.getElementById('export-png');
        if (exportPngBtn) {
            exportPngBtn.addEventListener('click', () => this.exportPNG());
        }

        const exportTiffBtn = document.getElementById('export-tiff');
        if (exportTiffBtn) {
            exportTiffBtn.addEventListener('click', () => this.exportTIFF());
        }

        const exportSvgBtn = document.getElementById('export-svg');
        if (exportSvgBtn) {
            exportSvgBtn.addEventListener('click', () => this.exportSVG());
        }

        // New figure button
        const newFigureBtn = document.getElementById('new-figure-btn');
        const newFigureModal = document.getElementById('new-figure-modal');
        if (newFigureBtn && newFigureModal) {
            newFigureBtn.addEventListener('click', () => {
                newFigureModal.style.display = 'flex';
            });
        }

        // Modal close buttons
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                const modal = document.getElementById('new-figure-modal');
                if (modal) modal.style.display = 'none';
            });
        });

        // Color palette
        document.querySelectorAll('.color-swatch').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const color = (e.currentTarget as HTMLElement).dataset.color;
                if (color) {
                    this.setCurrentColor(color);

                    // Update active state
                    document.querySelectorAll('.color-swatch').forEach(b => b.classList.remove('active'));
                    (e.currentTarget as HTMLElement).classList.add('active');
                }
            });
        });

        // Crosshair toggle
        const crosshairToggle = document.getElementById('crosshair-toggle') as HTMLInputElement;
        if (crosshairToggle) {
            crosshairToggle.addEventListener('change', (e) => {
                this.crosshairEnabled = (e.target as HTMLInputElement).checked;
                if (this.crosshairEnabled) {
                    this.initCrosshair();
                } else {
                    this.removeCrosshair();
                }
            });
        }

        // Save button (manual save trigger)
        const saveBtn = document.getElementById('save-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.autoSaveToLocalStorage());
        }

        // Undo/Redo buttons
        const undoBtn = document.getElementById('undo-btn');
        const redoBtn = document.getElementById('redo-btn');

        if (undoBtn) {
            undoBtn.addEventListener('click', () => this.undo());
        }
        if (redoBtn) {
            redoBtn.addEventListener('click', () => this.redo());
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl+D or Cmd+D - Duplicate
            if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
                e.preventDefault();
                this.duplicateObject();
            }

            // Ctrl+S or Cmd+S - Save
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                this.saveFigure();
            }

            // Delete or Backspace - Delete selected
            if (e.key === 'Delete' || e.key === 'Backspace') {
                const activeObject = this.canvas?.getActiveObject();
                if (activeObject && document.activeElement?.tagName !== 'INPUT') {
                    e.preventDefault();
                    this.canvas?.remove(activeObject);
                    this.canvas?.renderAll();
                    this.clearPropertiesPanel();
                    this.updateStatus('Object deleted');
                }
            }

            // Ctrl+] - Bring forward
            if ((e.ctrlKey || e.metaKey) && e.key === ']') {
                e.preventDefault();
                this.bringForward();
            }

            // Ctrl+[ - Send backward
            if ((e.ctrlKey || e.metaKey) && e.key === '[') {
                e.preventDefault();
                this.sendBackward();
            }

            // + key - Zoom in
            if (e.key === '+' || e.key === '=') {
                if (!e.ctrlKey && !e.metaKey && document.activeElement?.tagName !== 'INPUT') {
                    e.preventDefault();
                    this.zoomIn();
                }
            }

            // - key - Zoom out
            if (e.key === '-' || e.key === '_') {
                if (!e.ctrlKey && !e.metaKey && document.activeElement?.tagName !== 'INPUT') {
                    e.preventDefault();
                    this.zoomOut();
                }
            }

            // 0 key - Fit to window
            if (e.key === '0') {
                if (!e.ctrlKey && !e.metaKey && document.activeElement?.tagName !== 'INPUT') {
                    e.preventDefault();
                    this.zoomToFit();
                }
            }

            // Ctrl+Z - Undo
            if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
                e.preventDefault();
                this.undo();
            }

            // Ctrl+Y or Ctrl+Shift+Z - Redo
            if (((e.ctrlKey || e.metaKey) && e.key === 'y') ||
                ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'z')) {
                e.preventDefault();
                this.redo();
            }
        });
    }

    private async loadJournalPresets() {
        try {
            const response = await fetch('/vis/api/presets/');
            const data = await response.json();
            console.log('[VisEditor] Loaded journal presets:', data.presets);
        } catch (error) {
            console.error('[VisEditor] Failed to load presets:', error);
        }
    }

    private async applyJournalPreset(presetId: number) {
        try {
            const response = await fetch(`/vis/api/presets/${presetId}/`);
            const preset: JournalPreset = await response.json();

            this.currentPreset = preset;

            // Resize canvas to journal specifications
            if (this.canvas && preset.width_px) {
                const width = preset.width_px;
                const height = preset.height_px || Math.round(width * 0.67); // Default aspect ratio

                this.canvas.setWidth(width);
                this.canvas.setHeight(height);

                // Redraw grid with new dimensions
                if (this.gridEnabled) {
                    this.clearGrid();
                    this.drawGrid();
                }

                // Redraw rulers with new dimensions
                this.drawRulers();

                this.updateCanvasInfo();
                this.updateStatus(`Applied ${preset.name} - ${preset.column_type} (${preset.width_mm}mm)`);

                console.log(`[VisEditor] Applied preset: ${preset.name} - ${width}x${height}px @ ${preset.dpi}dpi`);
            }
        } catch (error) {
            console.error('[VisEditor] Failed to apply preset:', error);
            this.updateStatus('Failed to apply journal preset');
        }
    }

    private setLayout(layout: string) {
        this.currentLayout = layout;
        console.log(`[VisEditor] Layout set to: ${layout}`);

        // Highlight active icon button
        document.querySelectorAll('[data-layout]').forEach(btn => {
            btn.classList.remove('active');
        });
        const activeBtn = document.querySelector(`[data-layout="${layout}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }

        // Generate panel layout
        this.generatePanelLayout(layout);

        this.updateStatus(`Layout changed to ${layout}`);
    }

    private generatePanelLayout(layout: string) {
        if (!this.canvas) return;

        // Clear existing panel borders and labels
        this.clearPanelBorders();
        this.panelMetadata = [];  // Reset metadata

        const layoutConfig = this.getLayoutConfig(layout);
        if (!layoutConfig) return;

        const canvasWidth = this.canvas.getWidth();
        const canvasHeight = this.canvas.getHeight();

        const panelWidth = canvasWidth / layoutConfig.cols;
        const panelHeight = canvasHeight / layoutConfig.rows;

        let panelIndex = 0;

        for (let row = 0; row < layoutConfig.rows; row++) {
            for (let col = 0; col < layoutConfig.cols; col++) {
                if (panelIndex >= layoutConfig.panels.length) break;

                const x = col * panelWidth;
                const y = row * panelHeight;
                const baseLabel = layoutConfig.panels[panelIndex];
                const displayLabel = this.formatPanelLabel(baseLabel);

                // Create panel border (theme-aware colors)
                const borderColor = this.darkCanvasMode ? '#666666' : '#999999';

                const border = new fabric.Rect({
                    left: 0,
                    top: 0,
                    width: panelWidth - 4,  // Slight padding
                    height: panelHeight - 4,
                    fill: 'transparent',
                    stroke: borderColor,
                    strokeWidth: 2,
                    strokeDashArray: [5, 5],
                } as any);

                // Create panel label (dark in white canvas, light in dark canvas)
                const fontFamily = this.currentPreset?.font_family || 'Arial';
                const labelColor = this.darkCanvasMode ? '#ffffff' : '#000000';

                const text = new fabric.Text(displayLabel, {
                    left: 10,
                    top: 10,
                    fontSize: this.fontSizes.panelLabel,  // 10pt for panel labels
                    fontFamily: fontFamily,
                    fontWeight: 'bold',
                    fill: labelColor,
                } as any);

                // Group border and label together as a draggable panel
                const panelGroup = new fabric.Group([border, text], {
                    left: x,
                    top: y,
                    selectable: true,
                    hasControls: false,  // No resize handles
                    lockScalingX: true,
                    lockScalingY: true,
                    lockRotation: true,
                    hoverCursor: 'move',
                } as any);
                panelGroup.set('id', `panel-group-${baseLabel}`);
                panelGroup.set('panelId', baseLabel);

                this.canvas.add(panelGroup);
                this.canvas.sendToBack(panelGroup);

                // Store metadata
                this.panelMetadata.push({
                    id: `panel-${baseLabel}`,
                    position: baseLabel,
                    order: panelIndex,
                    x: x,
                    y: y,
                    width: panelWidth,
                    height: panelHeight,
                    borderObject: border,
                    labelObject: text,
                });

                panelIndex++;
            }
        }

        this.canvas.renderAll();
        console.log(`[VisEditor] Generated ${layoutConfig.panels.length} draggable panels`);
    }

    private formatPanelLabel(baseLabel: string): string {
        switch (this.labelStyle) {
            case 'uppercase':
                return baseLabel.toUpperCase();
            case 'lowercase':
                return baseLabel.toLowerCase();
            case 'numbers':
                // Convert A→1, B→2, etc.
                return (baseLabel.charCodeAt(0) - 64).toString();
            default:
                return baseLabel;
        }
    }

    private updatePanelLabels() {
        if (!this.canvas) return;

        // Update all panel label text based on current style
        this.canvas.getObjects().forEach((obj: any) => {
            if (obj.id && obj.id.startsWith('panel-group-')) {
                const panelId = obj.panelId;
                if (panelId) {
                    const newLabel = this.formatPanelLabel(panelId);
                    // Update the label text within the group
                    const items = obj.getObjects();
                    if (items && items.length > 1) {
                        items[1].set('text', newLabel);  // Second item is the label
                    }
                }
            }
        });

        this.canvas.renderAll();
        this.updateStatus(`Labels updated to ${this.labelStyle}`);
    }

    private swapPanels() {
        // This is now handled by draggable panels
        // Users can drag panels to swap positions
        this.updateStatus('Drag panels to rearrange them');
    }

    private getLayoutConfig(layout: string): PanelLayout | null {
        const configs: { [key: string]: PanelLayout } = {
            '1x1': { rows: 1, cols: 1, panels: ['A'] },
            '2x1': { rows: 1, cols: 2, panels: ['A', 'B'] },
            '1x2': { rows: 2, cols: 1, panels: ['A', 'B'] },
            '2x2': { rows: 2, cols: 2, panels: ['A', 'B', 'C', 'D'] },
            '1x3': { rows: 1, cols: 3, panels: ['A', 'B', 'C'] },
            '3x1': { rows: 3, cols: 1, panels: ['A', 'B', 'C'] },
            '2x3': { rows: 2, cols: 3, panels: ['A', 'B', 'C', 'D', 'E', 'F'] },
            '3x2': { rows: 3, cols: 2, panels: ['A', 'B', 'C', 'D', 'E', 'F'] },
            '3x3': { rows: 3, cols: 3, panels: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'] },
        };

        return configs[layout] || null;
    }

    private clearPanelBorders() {
        if (!this.canvas) return;

        // Remove existing panel groups
        const objects = this.canvas.getObjects();
        objects.forEach((obj: any) => {
            if (obj.id && obj.id.startsWith('panel-group-')) {
                this.canvas!.remove(obj);
            }
        });

        this.panelBorders = [];
        this.panelLabels = [];
        this.panelMetadata = [];

        this.canvas.renderAll();
    }

    private activateTool(tool: string) {
        console.log(`[VisEditor] Tool activated: ${tool}`);

        switch (tool) {
            case 'text':
                this.addText();
                break;
            case 'significance':
                this.addSignificance();
                break;
            case 'scalebar':
                this.addScaleBar();
                break;
            case 'arrow':
                this.addArrow();
                break;
            case 'rect-white':
                this.addRectangle('#ffffff', 'White Rectangle (hides elements)');
                break;
            case 'rect-black':
                this.addRectangle('#000000', 'Black Rectangle');
                break;
            case 'line':
                this.addLine();
                break;
            case 'ref-small':
                this.addReferenceRect('small');
                break;
            case 'ref-medium':
                this.addReferenceRect('medium');
                break;
            case 'ref-large':
                this.addReferenceRect('large');
                break;
            case 'ref-col-single':
                this.addColumnReference('single');
                break;
            case 'ref-col-1.5':
                this.addColumnReference('1.5');
                break;
            case 'ref-col-double':
                this.addColumnReference('double');
                break;
            case 'ref-col-full':
                this.addColumnReference('full');
                break;
            default:
                console.warn(`[VisEditor] Unknown tool: ${tool}`);
        }
    }

    private addText() {
        if (!this.canvas) return;

        const fontSize = this.currentPreset?.font_size_pt || 12;
        const fontFamily = this.currentPreset?.font_family || 'Arial';

        const text = new fabric.IText('Double-click to edit', {
            left: 100,
            top: 100,
            fontSize: fontSize * 2,
            fontFamily: fontFamily,
            fill: '#000000',
            selectable: true,
            evented: true,
        });

        this.canvas.add(text);
        this.canvas.bringToFront(text);  // Ensure it's on top
        this.canvas.setActiveObject(text);
        this.canvas.renderAll();
        this.updateStatus('Text added - Double-click to edit');
    }

    private addSignificance() {
        if (!this.canvas) return;

        const fontSize = this.currentPreset?.font_size_pt || 10;
        const fontFamily = this.currentPreset?.font_family || 'Arial';

        const stars = new fabric.Text('***', {
            left: 150,
            top: 50,
            fontSize: fontSize * 2.5,  // Slightly larger
            fontFamily: fontFamily,
            fill: '#000000',
            fontWeight: 'bold',
            selectable: true,
            evented: true,
        });

        this.canvas.add(stars);
        this.canvas.bringToFront(stars);  // Ensure it's on top
        this.canvas.setActiveObject(stars);
        this.canvas.renderAll();
        this.updateStatus('Significance marker added (p < 0.001)');
    }

    private addScaleBar() {
        if (!this.canvas) return;

        const fontSize = this.currentPreset?.font_size_pt || 12;
        const fontFamily = this.currentPreset?.font_family || 'Arial';
        const lineWidth = this.currentPreset?.line_width_pt || 0.5;

        // Create scale bar line (100 pixels = example)
        const barLength = 100;
        const line = new fabric.Line([0, 0, barLength, 0], {
            stroke: '#000000',
            strokeWidth: lineWidth * 4,  // Make visible
        });

        // Create label
        const text = new fabric.Text('100 μm', {
            fontSize: fontSize * 1.5,
            fontFamily: fontFamily,
            fill: '#000000',
            left: 0,
            top: 12,
        });

        // Group them together
        const scaleBar = new fabric.Group([line, text], {
            left: this.canvas.getWidth() - 150,
            top: this.canvas.getHeight() - 80,
            selectable: true,
            evented: true,
        });

        this.canvas.add(scaleBar);
        this.canvas.bringToFront(scaleBar);  // Ensure it's on top
        this.canvas.setActiveObject(scaleBar);
        this.canvas.renderAll();
        this.updateStatus('Scale bar added (adjust length as needed)');
    }

    private addArrow() {
        if (!this.canvas) return;

        const lineWidth = this.currentPreset?.line_width_pt || 0.5;

        // Create arrow line
        const startX = 50;
        const startY = 50;
        const endX = 200;
        const endY = 50;

        const line = new fabric.Line([startX, startY, endX, endY], {
            stroke: '#000000',
            strokeWidth: lineWidth * 4,
        });

        // Create arrowhead (triangle)
        const headLength = 15;
        const angle = Math.atan2(endY - startY, endX - startX);

        const arrowHead = new fabric.Triangle({
            left: endX,
            top: endY,
            width: headLength,
            height: headLength,
            fill: '#000000',
            angle: (angle * 180 / Math.PI) + 90,
            originX: 'center',
            originY: 'center',
        });

        // Group line and arrowhead
        const arrow = new fabric.Group([line, arrowHead], {
            left: 100,
            top: 100,
            selectable: true,
            evented: true,
        });

        this.canvas.add(arrow);
        this.canvas.bringToFront(arrow);  // Ensure it's on top
        this.canvas.setActiveObject(arrow);
        this.canvas.renderAll();
        this.updateStatus('Arrow added');
    }

    private addRectangle(fillColor: string, description: string) {
        if (!this.canvas) return;

        // SCIENTIFIC INTEGRITY NOTE:
        // White rectangles are commonly used to hide author info, noise, or
        // irrelevant elements. This is acceptable practice when disclosed.
        // The operation is non-destructive (overlays, doesn't modify original).

        const rect = new fabric.Rect({
            left: 100,
            top: 100,
            width: 150,
            height: 100,
            fill: fillColor,
            stroke: fillColor === '#ffffff' ? '#cccccc' : 'none',  // Light border for white
            strokeWidth: 1,
            strokeDashArray: fillColor === '#ffffff' ? [3, 3] : [],
            selectable: true,
            evented: true,
        });

        this.canvas.add(rect);
        this.canvas.bringToFront(rect);
        this.canvas.setActiveObject(rect);
        this.canvas.renderAll();
        this.updateStatus(description + ' added');
    }

    private addLine() {
        if (!this.canvas) return;

        const lineWidth = this.currentPreset?.line_width_pt || 0.5;

        const line = new fabric.Line([50, 50, 200, 50], {
            stroke: '#000000',
            strokeWidth: lineWidth * 4,
            selectable: true,
            evented: true,
        });

        this.canvas.add(line);
        this.canvas.bringToFront(line);
        this.canvas.setActiveObject(line);
        this.canvas.renderAll();
        this.updateStatus('Line added');
    }

    // Reference Rectangles for Size Comparison
    private addReferenceRect(size: 'small' | 'medium' | 'large') {
        if (!this.canvas) return;

        // Sizes in mm at 300 DPI (300/25.4 = 11.811 px/mm)
        const mmToPx = 11.811;
        const sizes = {
            small: { width: 30, height: 30 },    // 30mm × 30mm
            medium: { width: 40, height: 40 },   // 40mm × 40mm (recommended range)
            large: { width: 50, height: 50 },    // 50mm × 50mm
        };

        const sizeInMm = sizes[size];
        const rect = new fabric.Rect({
            left: 100,
            top: 100,
            width: sizeInMm.width * mmToPx,
            height: sizeInMm.height * mmToPx,
            fill: 'rgba(0,128,192,0.15)',  // Light blue transparent
            stroke: this.scientificColors.blue,
            strokeWidth: 2,
            strokeDashArray: [5, 3],
            selectable: true,
            evented: true,
        } as any);

        // Add size label
        const label = new fabric.Text(`${sizeInMm.width}×${sizeInMm.height}mm`, {
            left: 5,
            top: 5,
            fontSize: 8,
            fontFamily: 'Arial',
            fill: this.scientificColors.blue,
            selectable: false,
        } as any);

        const group = new fabric.Group([rect, label], {
            selectable: true,
            hasControls: true,
        } as any);

        this.canvas.add(group);
        this.canvas.setActiveObject(group);
        this.canvas.renderAll();
        this.updateStatus(`${size.charAt(0).toUpperCase() + size.slice(1)} reference added (${sizeInMm.width}×${sizeInMm.height}mm)`);
    }

    // Column Width Reference Rectangles
    private addColumnReference(type: 'single' | '1.5' | 'double' | 'full') {
        if (!this.canvas) return;

        // Standard column widths in mm (Nature/Cell/Science standards)
        const mmToPx = 11.811;
        const heights = 60; // Standard height
        const widths = {
            'single': 89,     // Single column
            '1.5': 120,       // 1.5 column
            'double': 183,    // Double column (full width)
            'full': 183,      // Full page width
        };

        // Blue opacity levels (darker = narrower)
        const opacities = {
            'single': 1.0,    // Darkest
            '1.5': 0.7,
            'double': 0.5,
            'full': 0.3,      // Lightest
        };

        const widthMm = widths[type];
        const opacity = opacities[type];

        const rect = new fabric.Rect({
            left: 100,
            top: 100,
            width: widthMm * mmToPx,
            height: heights * mmToPx,
            fill: `rgba(0,128,192,${opacity * 0.2})`,
            stroke: `rgba(0,128,192,${opacity})`,
            strokeWidth: 2,
            selectable: true,
            evented: true,
        } as any);

        // Add label
        const label = new fabric.Text(`${widthMm}mm (${type} col)`, {
            left: 5,
            top: 5,
            fontSize: 8,
            fontFamily: 'Arial',
            fill: this.scientificColors.blue,
            selectable: false,
        } as any);

        const group = new fabric.Group([rect, label], {
            selectable: true,
            hasControls: true,
        } as any);

        this.canvas.add(group);
        this.canvas.setActiveObject(group);
        this.canvas.renderAll();
        this.updateStatus(`${type} column reference added (${widthMm}mm)`);
    }

    private duplicateObject() {
        if (!this.canvas) return;

        const activeObject = this.canvas.getActiveObject();
        if (!activeObject) {
            this.updateStatus('No object selected to duplicate');
            return;
        }

        // Clone the object
        activeObject.clone((cloned: any) => {
            // Offset the clone slightly
            cloned.set({
                left: (activeObject.left || 0) + 20,
                top: (activeObject.top || 0) + 20,
            });

            this.canvas!.add(cloned);
            this.canvas!.setActiveObject(cloned);
            this.canvas!.renderAll();
            this.updateStatus('Object duplicated');
        });
    }

    private bringToFront() {
        const activeObject = this.canvas?.getActiveObject();
        if (activeObject) {
            this.canvas?.bringToFront(activeObject);
            this.canvas?.renderAll();
            this.updateStatus('Brought to front');
        }
    }

    private sendToBack() {
        const activeObject = this.canvas?.getActiveObject();
        if (activeObject) {
            this.canvas?.sendToBack(activeObject);
            // Keep grid and panel borders at the very back
            this.canvas?.getObjects().forEach((obj: any) => {
                if (obj.id === 'grid-line' || obj.id?.startsWith('panel-border')) {
                    this.canvas?.sendToBack(obj);
                }
            });
            this.canvas?.renderAll();
            this.updateStatus('Sent to back');
        }
    }

    private bringForward() {
        const activeObject = this.canvas?.getActiveObject();
        if (activeObject) {
            this.canvas?.bringForward(activeObject);
            this.canvas?.renderAll();
            this.updateStatus('Brought forward');
        }
    }

    private sendBackward() {
        const activeObject = this.canvas?.getActiveObject();
        if (activeObject) {
            this.canvas?.sendBackward(activeObject);
            this.canvas?.renderAll();
            this.updateStatus('Sent backward');
        }
    }

    private drawGrid() {
        if (!this.canvas) return;

        const width = this.canvas.getWidth();
        const height = this.canvas.getHeight();

        // Clear existing grid
        this.clearGrid();

        // Choose grid color based on canvas background
        // Light grid for white canvas, darker grid for dark canvas
        const gridColor = this.darkCanvasMode ? '#404040' : '#e5e5e5';

        // Draw vertical lines
        for (let i = 0; i <= width / this.gridSize; i++) {
            const x = i * this.gridSize;
            const line = new fabric.Line([x, 0, x, height], {
                stroke: gridColor,
                strokeWidth: i % 5 === 0 ? 1 : 0.5,  // Major/minor lines
                selectable: false,
                evented: false,
            } as any);
            line.set('id', 'grid-line');
            this.canvas.add(line);
            this.canvas.sendToBack(line);
        }

        // Draw horizontal lines
        for (let i = 0; i <= height / this.gridSize; i++) {
            const y = i * this.gridSize;
            const line = new fabric.Line([0, y, width, y], {
                stroke: gridColor,
                strokeWidth: i % 5 === 0 ? 1 : 0.5,  // Major/minor lines
                selectable: false,
                evented: false,
            } as any);
            line.set('id', 'grid-line');
            this.canvas.add(line);
            this.canvas.sendToBack(line);
        }

        this.canvas.renderAll();
    }

    private clearGrid() {
        if (!this.canvas) return;

        const objects = this.canvas.getObjects();
        objects.forEach((obj: any) => {
            if (obj.id === 'grid-line') {
                this.canvas!.remove(obj);
            }
        });
        this.canvas.renderAll();
    }

    private updatePropertiesPanel() {
        const activeObject = this.canvas?.getActiveObject();
        if (!activeObject) return;

        const propertiesContent = document.getElementById('properties-content');
        if (!propertiesContent) return;

        const type = activeObject.type || 'object';
        const left = Math.round(activeObject.left || 0);
        const top = Math.round(activeObject.top || 0);
        const width = Math.round((activeObject.width || 0) * (activeObject.scaleX || 1));
        const height = Math.round((activeObject.height || 0) * (activeObject.scaleY || 1));

        propertiesContent.innerHTML = `
            <div class="property-group">
                <label class="property-label">Type</label>
                <div class="property-value">${type}</div>
            </div>
            <div class="property-group">
                <label class="property-label">Position</label>
                <div class="property-value">X: ${left}px</div>
                <div class="property-value">Y: ${top}px</div>
            </div>
            <div class="property-group">
                <label class="property-label">Size</label>
                <div class="property-value">W: ${width}px</div>
                <div class="property-value">H: ${height}px</div>
            </div>
            <div class="property-group">
                <label class="property-label">Layer Order</label>
                <div style="display: flex; gap: 4px; margin-top: 6px;">
                    <button class="btn btn-sm" id="bring-to-front-btn" title="Bring to Front (Ctrl+Shift+])">
                        <i class="fas fa-angle-double-up"></i>
                    </button>
                    <button class="btn btn-sm" id="bring-forward-btn" title="Bring Forward (Ctrl+])">
                        <i class="fas fa-angle-up"></i>
                    </button>
                    <button class="btn btn-sm" id="send-backward-btn" title="Send Backward (Ctrl+[)">
                        <i class="fas fa-angle-down"></i>
                    </button>
                    <button class="btn btn-sm" id="send-to-back-btn" title="Send to Back (Ctrl+Shift+[)">
                        <i class="fas fa-angle-double-down"></i>
                    </button>
                </div>
            </div>
            <div class="property-group">
                <label class="property-label">Actions</label>
                <div style="display: flex; gap: 8px; margin-top: 6px;">
                    <button class="btn btn-sm btn-secondary" id="duplicate-object-btn" title="Duplicate (Ctrl+D)">
                        <i class="fas fa-copy"></i> Duplicate
                    </button>
                    <button class="btn btn-sm btn-danger" id="delete-object-btn" title="Delete (Del)">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `;

        // Add button handlers
        const deleteBtn = document.getElementById('delete-object-btn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => {
                const active = this.canvas?.getActiveObject();
                if (active) {
                    this.canvas?.remove(active);
                    this.canvas?.renderAll();
                    this.clearPropertiesPanel();
                    this.updateStatus('Object deleted');
                }
            });
        }

        const duplicateBtn = document.getElementById('duplicate-object-btn');
        if (duplicateBtn) {
            duplicateBtn.addEventListener('click', () => this.duplicateObject());
        }

        const bringToFrontBtn = document.getElementById('bring-to-front-btn');
        if (bringToFrontBtn) {
            bringToFrontBtn.addEventListener('click', () => this.bringToFront());
        }

        const bringForwardBtn = document.getElementById('bring-forward-btn');
        if (bringForwardBtn) {
            bringForwardBtn.addEventListener('click', () => this.bringForward());
        }

        const sendBackwardBtn = document.getElementById('send-backward-btn');
        if (sendBackwardBtn) {
            sendBackwardBtn.addEventListener('click', () => this.sendBackward());
        }

        const sendToBackBtn = document.getElementById('send-to-back-btn');
        if (sendToBackBtn) {
            sendToBackBtn.addEventListener('click', () => this.sendToBack());
        }
    }

    private clearPropertiesPanel() {
        const propertiesContent = document.getElementById('properties-content');
        if (propertiesContent) {
            propertiesContent.innerHTML = '<p class="properties-empty">Select an object to edit properties</p>';
        }
    }

    private exportPNG() {
        if (!this.canvas) return;

        // SCIENTIFIC INTEGRITY: Always export with WHITE background
        // regardless of viewing mode (dark canvas)

        // Save current background
        const originalBg = this.canvas.backgroundColor;
        const gridWasEnabled = this.gridEnabled;

        // Force white background for export
        this.canvas.setBackgroundColor('#ffffff', () => {
            if (gridWasEnabled) {
                this.clearGrid();
            }

            // Export at high quality with WHITE background
            const dataURL = this.canvas!.toDataURL({
                format: 'png',
                quality: 1.0,
                multiplier: 1,
            });

            // Restore original background
            this.canvas!.setBackgroundColor(originalBg as string, () => {
                if (gridWasEnabled) {
                    this.drawGrid();
                }
                this.canvas!.renderAll();
            });

            // Trigger download
            const link = document.createElement('a');
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
            link.download = `figure_${timestamp}.png`;
            link.href = dataURL;
            link.click();

            this.updateStatus('Exported as PNG (white background)');
        });
    }

    private exportTIFF() {
        if (!this.canvas) return;

        // TIFF export: Export as high-quality PNG then convert to TIFF
        // For publication-quality TIFF at 300 DPI

        const originalBg = this.canvas.backgroundColor;
        const gridWasEnabled = this.gridEnabled;

        this.canvas.setBackgroundColor('#ffffff', () => {
            if (gridWasEnabled) {
                this.clearGrid();
            }

            // Export at actual size (300 DPI already embedded in canvas)
            const dataURL = this.canvas!.toDataURL({
                format: 'png',
                quality: 1.0,
                multiplier: 1,  // Keep at 300 DPI
            });

            // Restore original background
            this.canvas!.setBackgroundColor(originalBg as string, () => {
                if (gridWasEnabled) {
                    this.drawGrid();
                }
                this.canvas!.renderAll();
            });

            // Download as PNG (browser limitation - TIFF conversion needs backend)
            const link = document.createElement('a');
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
            link.download = `figure_${timestamp}_300dpi.png`;
            link.href = dataURL;
            link.click();

            // TODO: Add backend endpoint to convert PNG to TIFF at 300 DPI
            this.updateStatus('Exported as PNG (300 DPI) - Convert to TIFF for submission');
            console.log('[Export] To convert to TIFF: Use ImageMagick or Python PIL');
            console.log('[Export] Command: convert figure.png -compress lzw figure.tif');
        });
    }

    private exportSVG() {
        if (!this.canvas) return;

        // SCIENTIFIC INTEGRITY: Always export with WHITE background
        // regardless of viewing mode (dark canvas)

        // Save current background
        const originalBg = this.canvas.backgroundColor;
        const gridWasEnabled = this.gridEnabled;

        // Force white background for export
        this.canvas.setBackgroundColor('#ffffff', () => {
            if (gridWasEnabled) {
                this.clearGrid();
            }

            const svg = this.canvas!.toSVG();

            // Restore original background
            this.canvas!.setBackgroundColor(originalBg as string, () => {
                if (gridWasEnabled) {
                    this.drawGrid();
                }
                this.canvas!.renderAll();
            });

            const blob = new Blob([svg], { type: 'image/svg+xml' });
            const url = URL.createObjectURL(blob);

            const link = document.createElement('a');
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
            link.download = `figure_${timestamp}.svg`;
            link.href = url;
            link.click();

            URL.revokeObjectURL(url);
            this.updateStatus('Exported as SVG (white background)');
        });
    }

    private async saveFigure() {
        if (!this.canvas) return;

        const canvasState = this.canvas.toJSON();
        console.log('[VisEditor] Saving figure...', canvasState);

        // TODO: Get figure ID from page context
        // For now, just show success
        this.updateStatus('Figure saved (TODO: connect to backend)');
    }

    // Scientific Color Palette
    private setCurrentColor(color: string) {
        this.currentColor = color;

        // Apply to selected objects
        const activeObjects = this.canvas?.getActiveObjects();
        if (activeObjects && activeObjects.length > 0) {
            activeObjects.forEach((obj: any) => {
                if (obj.type === 'rect' || obj.type === 'circle' || obj.type === 'polygon') {
                    obj.set('fill', color);
                } else if (obj.type === 'line' || obj.type === 'path') {
                    obj.set('stroke', color);
                } else if (obj.type === 'text' || obj.type === 'i-text') {
                    obj.set('fill', color);
                }
            });
            this.canvas?.renderAll();
            this.saveHistory();
        }

        console.log(`[Color] Set to ${color}`);
    }

    // Crosshair Alignment Guides
    private initCrosshair() {
        const canvasWrapper = document.querySelector('.vis-canvas-wrapper') as HTMLElement;
        if (!canvasWrapper) return;

        // Create crosshair elements if they don't exist
        if (!this.crosshairH) {
            this.crosshairH = document.createElement('div');
            this.crosshairH.className = 'crosshair-horizontal';
            canvasWrapper.appendChild(this.crosshairH);
        }

        if (!this.crosshairV) {
            this.crosshairV = document.createElement('div');
            this.crosshairV.className = 'crosshair-vertical';
            canvasWrapper.appendChild(this.crosshairV);
        }

        // Mouse move handler
        const handleMouseMove = (e: MouseEvent) => {
            if (!this.crosshairH || !this.crosshairV) return;

            const rect = canvasWrapper.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            // Update crosshair positions
            this.crosshairH.style.top = `${y}px`;
            this.crosshairV.style.left = `${x}px`;

            // Show crosshairs
            this.crosshairH.classList.add('visible');
            this.crosshairV.classList.add('visible');
        };

        const handleMouseLeave = () => {
            if (this.crosshairH) this.crosshairH.classList.remove('visible');
            if (this.crosshairV) this.crosshairV.classList.remove('visible');
        };

        canvasWrapper.addEventListener('mousemove', handleMouseMove);
        canvasWrapper.addEventListener('mouseleave', handleMouseLeave);

        console.log('[Crosshair] Enabled');
    }

    private removeCrosshair() {
        if (this.crosshairH) {
            this.crosshairH.remove();
            this.crosshairH = null;
        }
        if (this.crosshairV) {
            this.crosshairV.remove();
            this.crosshairV = null;
        }

        console.log('[Crosshair] Disabled');
    }

    // Smart Alignment Guides
    private findAlignmentTargets(movingObj: any, left: number, top: number): {left: number, top: number, guides: any[]} | null {
        if (!this.canvas) return null;

        const snapDistance = 5; // pixels
        const guides: any[] = [];
        let snappedLeft = left;
        let snappedTop = top;

        const movingBounds = movingObj.getBoundingRect();
        const movingCenter = {
            x: left + (movingBounds.width / 2),
            y: top + (movingBounds.height / 2)
        };

        // Check all other objects
        const objects = this.canvas.getObjects().filter((obj: any) =>
            obj !== movingObj &&
            !obj.id?.includes('grid') &&
            !obj.id?.includes('panel-border') &&
            !obj.id?.includes('panel-label')
        );

        objects.forEach((obj: any) => {
            const bounds = obj.getBoundingRect();
            const center = {
                x: obj.left + (bounds.width / 2),
                y: obj.top + (bounds.height / 2)
            };

            // Horizontal alignment (center, top, bottom)
            if (Math.abs(center.y - movingCenter.y) < snapDistance) {
                snappedTop = obj.top - (movingBounds.height / 2) + (bounds.height / 2);
                guides.push({ type: 'horizontal', y: center.y });
            } else if (Math.abs(obj.top - top) < snapDistance) {
                snappedTop = obj.top;
                guides.push({ type: 'horizontal', y: obj.top });
            } else if (Math.abs((obj.top + bounds.height) - (top + movingBounds.height)) < snapDistance) {
                snappedTop = obj.top + bounds.height - movingBounds.height;
                guides.push({ type: 'horizontal', y: obj.top + bounds.height });
            }

            // Vertical alignment (center, left, right)
            if (Math.abs(center.x - movingCenter.x) < snapDistance) {
                snappedLeft = obj.left - (movingBounds.width / 2) + (bounds.width / 2);
                guides.push({ type: 'vertical', x: center.x });
            } else if (Math.abs(obj.left - left) < snapDistance) {
                snappedLeft = obj.left;
                guides.push({ type: 'vertical', x: obj.left });
            } else if (Math.abs((obj.left + bounds.width) - (left + movingBounds.width)) < snapDistance) {
                snappedLeft = obj.left + bounds.width - movingBounds.width;
                guides.push({ type: 'vertical', x: obj.left + bounds.width });
            }
        });

        if (guides.length > 0) {
            return { left: snappedLeft, top: snappedTop, guides };
        }

        return null;
    }

    private showAlignmentGuides(guides: any[]) {
        // Remove existing guides
        this.hideAlignmentGuides();

        const canvasWrapper = document.querySelector('.vis-canvas-wrapper') as HTMLElement;
        if (!canvasWrapper) return;

        guides.forEach(guide => {
            const line = document.createElement('div');
            line.className = `alignment-guide ${guide.type}`;
            line.setAttribute('data-alignment-guide', 'true');

            if (guide.type === 'horizontal') {
                line.style.top = `${guide.y}px`;
            } else {
                line.style.left = `${guide.x}px`;
            }

            canvasWrapper.appendChild(line);
        });
    }

    private hideAlignmentGuides() {
        document.querySelectorAll('[data-alignment-guide]').forEach(guide => guide.remove());
    }

    private updateCanvasInfo() {
        if (!this.canvas) return;

        const width = this.canvas.getWidth();
        const height = this.canvas.getHeight();
        const dpi = this.currentPreset?.dpi || 300;

        // Calculate mm dimensions
        const widthMm = (width / dpi) * 25.4;
        const heightMm = (height / dpi) * 25.4;

        const sizeEl = document.getElementById('canvas-size');
        if (sizeEl) {
            sizeEl.textContent = `${Math.round(widthMm)}mm × ${Math.round(heightMm)}mm (${width} × ${height}px)`;
        }

        const dpiEl = document.getElementById('canvas-dpi');
        if (dpiEl) {
            dpiEl.textContent = `${dpi} DPI`;
        }
    }

    private toggleCanvasBackground() {
        if (!this.canvas) return;

        const warningEl = document.getElementById('dark-canvas-warning');
        const containerEl = document.querySelector('.vis-canvas-container') as HTMLElement;

        if (this.darkCanvasMode) {
            // Switch to dark background (for viewing comfort - eyes)
            this.canvas.setBackgroundColor('#2a2a2a', () => {
                this.canvas!.renderAll();
            });

            // Also darken the container (remove white margins)
            if (containerEl) {
                containerEl.style.backgroundColor = '#2a2a2a';
                containerEl.style.padding = '0';  // Remove padding to eliminate white margins
            }

            // Show warning
            if (warningEl) {
                warningEl.style.display = 'flex';
            }

            this.updateStatus('Dark canvas enabled (viewing only - export will be white)');
            console.log('[VisEditor] Dark canvas mode: ON (export will be white)');

        } else {
            // Switch back to white background
            this.canvas.setBackgroundColor('#ffffff', () => {
                this.canvas!.renderAll();
            });

            // Restore white container with padding
            if (containerEl) {
                containerEl.style.backgroundColor = '#ffffff';
                containerEl.style.padding = '20px';  // Restore original padding
            }

            // Hide warning
            if (warningEl) {
                warningEl.style.display = 'none';
            }

            this.updateStatus('White canvas restored');
            console.log('[VisEditor] Dark canvas mode: OFF');
        }

        // Update grid visibility if needed
        if (this.gridEnabled) {
            this.clearGrid();
            this.drawGrid();
        }
    }

    private showObjectsUnderPointer(pointer: {x: number, y: number}) {
        if (!this.canvas) return;

        // Get all objects under pointer (with tolerance)
        const tolerance = 15;  // pixels
        const candidates: any[] = [];

        this.canvas.forEachObject((obj: any) => {
            if (!obj.selectable) return;
            if (obj.id && (obj.id === 'grid-line' || obj.id.startsWith('panel-group'))) return;

            const bound = obj.getBoundingRect();

            if (pointer.x >= bound.left - tolerance &&
                pointer.x <= bound.left + bound.width + tolerance &&
                pointer.y >= bound.top - tolerance &&
                pointer.y <= bound.top + bound.height + tolerance) {

                const zIndex = this.canvas!.getObjects().indexOf(obj);
                candidates.push({ object: obj, zIndex: zIndex });
            }
        });

        if (candidates.length === 0) {
            this.updateStatus('No objects under pointer');
            return;
        }

        if (candidates.length === 1) {
            // Only one object - select it directly
            this.canvas.setActiveObject(candidates[0].object);
            this.canvas.renderAll();
            return;
        }

        // Multiple objects - show selection popup
        this.showSelectionPopup(candidates, pointer);
    }

    private showSelectionPopup(candidates: any[], pointer: {x: number, y: number}) {
        // Remove existing popup
        const existing = document.getElementById('skewer-selection-popup');
        if (existing) existing.remove();

        // Create popup
        const popup = document.createElement('div');
        popup.id = 'skewer-selection-popup';
        popup.className = 'skewer-popup';
        popup.style.position = 'absolute';
        popup.style.left = `${pointer.x + 10}px`;
        popup.style.top = `${pointer.y + 10}px`;
        popup.style.zIndex = '10000';

        // Title
        const title = document.createElement('div');
        title.className = 'skewer-popup-title';
        title.textContent = `${candidates.length} objects here`;
        popup.appendChild(title);

        // Sort by z-index (highest first - top layer)
        candidates.sort((a, b) => b.zIndex - a.zIndex);

        // List
        candidates.forEach((candidate, index) => {
            const item = document.createElement('div');
            item.className = 'skewer-popup-item';

            const type = candidate.object.type || 'object';
            const icon = this.getObjectIcon(type);

            item.innerHTML = `
                <span class="skewer-icon">${icon}</span>
                <span class="skewer-name">${this.getObjectName(candidate.object)}</span>
                <span class="skewer-layer">L${candidate.zIndex}</span>
                <span class="skewer-actions">
                    ${index > 0 ? '<button class="skewer-btn" data-action="up">↑</button>' : ''}
                    ${index < candidates.length - 1 ? '<button class="skewer-btn" data-action="down">↓</button>' : ''}
                </span>
            `;

            // Click to select
            item.addEventListener('click', (e) => {
                if ((e.target as HTMLElement).classList.contains('skewer-btn')) return;
                this.canvas!.setActiveObject(candidate.object);
                this.canvas!.renderAll();
                popup.remove();
            });

            // Layer order buttons
            const upBtn = item.querySelector('[data-action="up"]');
            const downBtn = item.querySelector('[data-action="down"]');

            if (upBtn) {
                upBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.canvas!.bringForward(candidate.object);
                    this.showObjectsUnderPointer(pointer);  // Refresh
                });
            }

            if (downBtn) {
                downBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.canvas!.sendBackwards(candidate.object);
                    this.showObjectsUnderPointer(pointer);  // Refresh
                });
            }

            // Hover to highlight
            item.addEventListener('mouseenter', () => {
                const origStroke = candidate.object.stroke;
                const origStrokeWidth = candidate.object.strokeWidth;
                candidate.object.set({ stroke: '#00ff00', strokeWidth: 3 });
                this.canvas!.renderAll();

                item.addEventListener('mouseleave', () => {
                    candidate.object.set({ stroke: origStroke, strokeWidth: origStrokeWidth });
                    this.canvas!.renderAll();
                }, { once: true });
            });

            popup.appendChild(item);
        });

        // Add to canvas container
        const container = document.querySelector('.vis-canvas-container');
        if (container) {
            container.appendChild(popup);
        }

        // Close on outside click
        setTimeout(() => {
            const closeHandler = (e: MouseEvent) => {
                if (!popup.contains(e.target as Node)) {
                    popup.remove();
                    document.removeEventListener('click', closeHandler);
                }
            };
            document.addEventListener('click', closeHandler);
        }, 100);

        this.updateStatus('Alt+Click: Select from list');
    }

    private getObjectIcon(type: string): string {
        switch (type) {
            case 'text':
            case 'i-text': return '📝';
            case 'image': return '🖼️';
            case 'line': return '━';
            case 'group': return '📦';
            case 'rect': return '▭';
            case 'triangle': return '▲';
            default: return '•';
        }
    }

    private getObjectName(obj: any): string {
        if (obj.text) return `"${obj.text.substring(0, 20)}"`;
        if (obj.type === 'image' && obj.filename) return obj.filename;
        if (obj.type === 'group') return 'Group';
        return obj.type || 'Object';
    }

    private zoomIn() {
        this.zoomLevel = Math.min(this.zoomLevel * 1.2, 5.0);  // Max 500%
        this.applyZoom();
    }

    private zoomOut() {
        this.zoomLevel = Math.max(this.zoomLevel / 1.2, 0.1);  // Min 10%
        this.applyZoom();
    }

    private zoomToFit() {
        if (!this.canvas) return;

        const wrapper = document.querySelector('.vis-canvas-wrapper');
        if (!wrapper) return;

        const wrapperWidth = wrapper.clientWidth - 40;  // Padding
        const wrapperHeight = wrapper.clientHeight - 40;

        const canvasWidth = this.canvas.getWidth();
        const canvasHeight = this.canvas.getHeight();

        const scaleX = wrapperWidth / canvasWidth;
        const scaleY = wrapperHeight / canvasHeight;

        this.zoomLevel = Math.min(scaleX, scaleY, 1.0);  // Don't zoom in beyond 100%
        this.applyZoom();
    }

    private applyZoom() {
        if (!this.canvas) return;

        const container = document.querySelector('.vis-canvas-container') as HTMLElement;
        if (container) {
            container.style.transform = `scale(${this.zoomLevel})`;
            container.style.transformOrigin = 'center center';
        }

        // Update zoom display
        const zoomDisplay = document.getElementById('zoom-level');
        if (zoomDisplay) {
            zoomDisplay.textContent = `${Math.round(this.zoomLevel * 100)}%`;
        }

        // Update status bar zoom
        const canvasZoom = document.getElementById('canvas-zoom');
        if (canvasZoom) {
            canvasZoom.textContent = `${Math.round(this.zoomLevel * 100)}%`;
        }

        this.updateStatus(`Zoom: ${Math.round(this.zoomLevel * 100)}%`);
    }

    private saveToHistory() {
        if (!this.canvas) return;

        const json = JSON.stringify(this.canvas.toJSON(['id', 'panelId', 'filename', 'hierarchyId']));

        // Remove states after current index (if we undid and then made changes)
        if (this.historyIndex < this.history.length - 1) {
            this.history = this.history.slice(0, this.historyIndex + 1);
        }

        // Add new state
        this.history.push(json);

        // Limit history size
        if (this.history.length > this.maxHistory) {
            this.history.shift();
        } else {
            this.historyIndex++;
        }

        // Update undo/redo button states
        this.updateUndoRedoButtons();

        // Trigger auto-save
        this.scheduleAutoSave();

        console.log(`[VisEditor] History saved (${this.historyIndex + 1}/${this.history.length})`);
    }

    private undo() {
        if (!this.canvas || this.historyIndex <= 0) {
            this.updateStatus('Nothing to undo');
            return;
        }

        this.historyIndex--;
        this.restoreFromHistory(this.historyIndex);
        this.updateStatus(`Undo (${this.history.length - this.historyIndex - 1} redo available)`);
    }

    private redo() {
        if (!this.canvas || this.historyIndex >= this.history.length - 1) {
            this.updateStatus('Nothing to redo');
            return;
        }

        this.historyIndex++;
        this.restoreFromHistory(this.historyIndex);
        this.updateStatus(`Redo (${this.historyIndex} undo available)`);
    }

    private restoreFromHistory(index: number) {
        if (!this.canvas || index < 0 || index >= this.history.length) return;

        const state = this.history[index];
        this.canvas.loadFromJSON(state, () => {
            this.canvas!.renderAll();
            this.updateUndoRedoButtons();
            console.log(`[VisEditor] Restored state ${index + 1}/${this.history.length}`);
        });
    }

    private updateUndoRedoButtons() {
        const undoBtn = document.querySelector('[title*="Undo"]') as HTMLButtonElement;
        const redoBtn = document.querySelector('[title*="Redo"]') as HTMLButtonElement;

        if (undoBtn) {
            undoBtn.disabled = this.historyIndex <= 0;
        }
        if (redoBtn) {
            redoBtn.disabled = this.historyIndex >= this.history.length - 1;
        }
    }

    private setupAutoSave() {
        // Save initial state to history
        this.saveToHistory();
    }

    private scheduleAutoSave() {
        // Debounce auto-save (wait 2 seconds after last change)
        if (this.autoSaveTimer) {
            clearTimeout(this.autoSaveTimer);
        }

        this.autoSaveTimer = setTimeout(() => {
            this.autoSaveToLocalStorage();
        }, 2000);
    }

    private autoSaveToLocalStorage() {
        if (!this.canvas) return;

        try {
            const state = {
                canvas: this.canvas.toJSON(['id', 'panelId', 'filename', 'hierarchyId']),
                layout: this.currentLayout,
                preset: this.currentPreset,
                darkMode: this.darkCanvasMode,
                gridEnabled: this.gridEnabled,
                snapEnabled: this.snapEnabled,
                labelStyle: this.labelStyle,
                zoomLevel: this.zoomLevel,
                history: this.history,
                historyIndex: this.historyIndex,
                timestamp: new Date().toISOString(),
            };

            localStorage.setItem(this.autoSaveKey, JSON.stringify(state));

            // Show save indicator briefly
            const saveBtn = document.getElementById('save-btn');
            if (saveBtn) {
                const originalText = saveBtn.innerHTML;
                saveBtn.innerHTML = '<i class="fas fa-check"></i> Saved';
                saveBtn.classList.add('btn-success');

                setTimeout(() => {
                    saveBtn.innerHTML = originalText;
                    saveBtn.classList.remove('btn-success');
                }, 1500);
            }

            console.log('[VisEditor] Auto-saved to localStorage');
        } catch (e) {
            console.error('[VisEditor] Auto-save failed:', e);
        }
    }

    private restoreFromLocalStorage() {
        if (!this.canvas) return;

        try {
            const saved = localStorage.getItem(this.autoSaveKey);
            if (!saved) {
                console.log('[VisEditor] No saved state found');
                return;
            }

            const state = JSON.parse(saved);

            // Restore canvas
            this.canvas.loadFromJSON(state.canvas, () => {
                this.canvas!.renderAll();

                // Restore settings
                this.currentLayout = state.layout || '1x1';
                this.darkCanvasMode = state.darkMode || false;
                this.gridEnabled = state.gridEnabled !== false;
                this.snapEnabled = state.snapEnabled !== false;
                this.labelStyle = state.labelStyle || 'uppercase';
                this.zoomLevel = state.zoomLevel || 1.0;

                // Restore history
                this.history = state.history || [];
                this.historyIndex = state.historyIndex || 0;

                // Apply restored settings
                if (this.darkCanvasMode) {
                    this.toggleCanvasBackground();
                }
                if (state.preset) {
                    this.currentPreset = state.preset;
                }
                if (this.zoomLevel !== 1.0) {
                    this.applyZoom();
                }

                // Update UI
                this.updateUndoRedoButtons();
                this.updateCanvasInfo();

                const timestamp = new Date(state.timestamp).toLocaleString();
                this.updateStatus(`Restored session from ${timestamp}`);
                console.log('[VisEditor] Restored from localStorage:', timestamp);
            });

        } catch (e) {
            console.error('[VisEditor] Restore failed:', e);
            this.updateStatus('Failed to restore session');
        }
    }

    private toggleRulers() {
        const rulersArea = document.querySelector('.vis-rulers-area');
        if (rulersArea) {
            if (this.rulerVisible) {
                rulersArea.classList.remove('rulers-hidden');
                this.drawRulers();
            } else {
                rulersArea.classList.add('rulers-hidden');
            }
        }
    }

    private drawRulers() {
        if (!this.canvas || !this.rulerVisible) return;

        const dpi = this.currentPreset?.dpi || 300;
        const canvasWidth = this.canvas.getWidth();
        const canvasHeight = this.canvas.getHeight();

        this.drawHorizontalRuler(canvasWidth, dpi);
        this.drawVerticalRuler(canvasHeight, dpi);
    }

    private drawHorizontalRuler(width: number, dpi: number) {
        const svg = document.getElementById('ruler-horizontal');
        if (!svg) return;

        svg.innerHTML = '';
        svg.setAttribute('width', width.toString());
        svg.setAttribute('height', '25');
        svg.setAttribute('viewBox', `0 0 ${width} 25`);

        const maxValue = this.pxToUnit(width, dpi, this.rulerUnit);
        const majorInterval = this.rulerUnit === 'mm' ? 10 : 1;
        const minorInterval = this.rulerUnit === 'mm' ? 5 : 0.5;

        // Draw minor ticks
        for (let i = minorInterval; i <= maxValue; i += minorInterval) {
            if (i % majorInterval === 0) continue;  // Skip major ticks

            const x = this.unitToPx(i, dpi, this.rulerUnit);
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', x.toString());
            line.setAttribute('y1', '18');
            line.setAttribute('x2', x.toString());
            line.setAttribute('y2', '25');
            line.setAttribute('stroke', '#ccc');
            line.setAttribute('stroke-width', '0.5');
            svg.appendChild(line);
        }

        // Draw major ticks with labels
        for (let i = 0; i <= maxValue; i += majorInterval) {
            const x = this.unitToPx(i, dpi, this.rulerUnit);

            // Tick line
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', x.toString());
            line.setAttribute('y1', '12');
            line.setAttribute('x2', x.toString());
            line.setAttribute('y2', '25');
            line.setAttribute('stroke', '#999');
            line.setAttribute('stroke-width', '1');
            svg.appendChild(line);

            // Label
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', x.toString());
            text.setAttribute('y', '10');
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('font-size', '9');
            text.setAttribute('fill', '#666');
            text.textContent = i.toString();
            svg.appendChild(text);
        }

        // Unit label at end
        const unitText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        unitText.setAttribute('x', (width - 15).toString());
        unitText.setAttribute('y', '10');
        unitText.setAttribute('font-size', '8');
        unitText.setAttribute('fill', '#999');
        unitText.textContent = this.rulerUnit;
        svg.appendChild(unitText);
    }

    private drawVerticalRuler(height: number, dpi: number) {
        const svg = document.getElementById('ruler-vertical');
        if (!svg) return;

        svg.innerHTML = '';
        svg.setAttribute('width', '25');
        svg.setAttribute('height', height.toString());
        svg.setAttribute('viewBox', `0 0 25 ${height}`);

        const maxValue = this.pxToUnit(height, dpi, this.rulerUnit);
        const majorInterval = this.rulerUnit === 'mm' ? 10 : 1;
        const minorInterval = this.rulerUnit === 'mm' ? 5 : 0.5;

        // Draw minor ticks
        for (let i = minorInterval; i <= maxValue; i += minorInterval) {
            if (i % majorInterval === 0) continue;

            const y = this.unitToPx(i, dpi, this.rulerUnit);
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', '18');
            line.setAttribute('y1', y.toString());
            line.setAttribute('x2', '25');
            line.setAttribute('y2', y.toString());
            line.setAttribute('stroke', '#ccc');
            line.setAttribute('stroke-width', '0.5');
            svg.appendChild(line);
        }

        // Draw major ticks with labels
        for (let i = 0; i <= maxValue; i += majorInterval) {
            const y = this.unitToPx(i, dpi, this.rulerUnit);

            // Tick line
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', '12');
            line.setAttribute('y1', y.toString());
            line.setAttribute('x2', '25');
            line.setAttribute('y2', y.toString());
            line.setAttribute('stroke', '#999');
            line.setAttribute('stroke-width', '1');
            svg.appendChild(line);

            // Label
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', '10');
            text.setAttribute('y', (y + 3).toString());
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('font-size', '9');
            text.setAttribute('fill', '#666');
            text.textContent = i.toString();
            svg.appendChild(text);
        }
    }

    private pxToUnit(px: number, dpi: number, unit: 'mm' | 'inches'): number {
        const inches = px / dpi;
        return unit === 'mm' ? inches * 25.4 : inches;
    }

    private unitToPx(value: number, dpi: number, unit: 'mm' | 'inches'): number {
        const inches = unit === 'mm' ? value / 25.4 : value;
        return inches * dpi;
    }

    private updateStatus(message: string) {
        const statusEl = document.getElementById('status-message');
        if (statusEl) {
            statusEl.textContent = message;

            // Clear status after 3 seconds
            setTimeout(() => {
                statusEl.textContent = 'Ready';
            }, 3000);
        }
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new VisEditor();
    });
} else {
    new VisEditor();
}
