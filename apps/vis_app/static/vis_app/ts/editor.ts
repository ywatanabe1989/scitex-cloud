/**
 * SciTeX Vis - Scientific Figure Editor
 * Canvas-based editor using Fabric.js for publication-quality figures
 */

// Fabric.js is loaded via CDN in the template
declare namespace fabric {
  type Canvas = any;
  type Object = any;
  type Rect = any;
  type Text = any;
  type Image = any;
  type Line = any;
  type Circle = any;
  type Polygon = any;
  type Path = any;
  type Group = any;
}
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
    // Maximum canvas dimensions (scientific publishing standards)
    private readonly MAX_CANVAS_WIDTH: number = 2126;  // 180mm @ 300dpi
    private readonly MAX_CANVAS_HEIGHT: number = 2539; // 215mm @ 300dpi

    private canvas: fabric.Canvas | null = null;
    private currentLayout: string = '1x1';
    private currentPreset: JournalPreset | null = null;
    private gridEnabled: boolean = true;
    private snapEnabled: boolean = true;
    private gridSize: number = 23.622; // 2mm @ 300dpi (11.811 px/mm × 2)
    private snapSize: number = 11.811; // 1mm @ 300dpi (default snap resolution)
    private panelBorders: fabric.Rect[] = [];
    private panelLabels: fabric.Text[] = [];
    private darkCanvasMode: boolean = false;  // For viewing comfort only
    private panelMetadata: PanelMetadata[] = [];  // Track panel info for swapping
    private labelStyle: 'uppercase' | 'lowercase' | 'numbers' = 'uppercase';
    private zoomLevel: number = 1.0;  // 100% = 1.0
    private rulerEnabled: boolean = true;

    // Version comparison (Original | Edited Cards)
    private comparisonMode: 'edited' | 'original' | 'split' = 'edited';
    private originalCanvasState: any = null;
    private editedCanvasState: any = null;
    private originalCanvas: fabric.Canvas | null = null;  // For split view
    private figureId: string | null = null;

    // Undo/Redo system
    private history: string[] = [];
    private historyIndex: number = -1;
    private maxHistory: number = 50;  // Keep last 50 states

    // Clipboard for copy/paste
    private clipboard: any = null;

    // Ctrl+Drag duplication tracking
    private isDuplicatingWithDrag: boolean = false;
    private dragStartPosition: { x: number, y: number } | null = null;

    // Click cycling through layered objects
    private lastClickPosition: { x: number, y: number } | null = null;
    private lastClickTime: number = 0;
    private clickCycleIndex: number = 0;
    private clickCycleObjects: fabric.Object[] = [];

    // Panning - pan the entire rulers area
    private isPanning: boolean = false;
    private panStartPoint: { x: number, y: number } | null = null;
    private panOffset: { x: number, y: number } = { x: 0, y: 0 };

    // Auto-save
    private autoSaveKey: string = 'scitex_vis_autosave';
    private autoSaveTimer: any = null;

    // Rulers
    private rulerUnit: 'mm' | 'inches' = 'mm';
    private rulerVisible: boolean = true;
    private resizeTimeout: any = null;

    // Wheel throttling to prevent crashes during fast scrolling
    private wheelThrottleFrame: number | null = null;
    private pendingTransform: (() => void) | null = null;

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
    private currentStroke: string = 'rgb(0,0,0)';  // Default black outline
    private currentStrokeStyle: 'solid' | 'dashed' | 'dotted' = 'solid';

    // Label ordering modes
    private labelOrdering: 'horizontal' | 'vertical' | 'custom' | 'original' = 'horizontal';
    private customLabelOrder: string[] = [];

    // Data table for plot data editing
    private dataTable: any = null;

    constructor() {
        this.init();
    }

    private init() {
        console.log("[VisEditor] Initializing...");

        // Get figure ID from page context
        const container = document.querySelector('.vis-container') as HTMLElement;
        if (container && container.dataset.figureId) {
            this.figureId = container.dataset.figureId;
            console.log(`[VisEditor] Figure ID: ${this.figureId}`);
        }

        // Initialize canvas
        this.initCanvas();

        // Set up event listeners
        this.setupEventListeners();
        
        // Setup plot gallery panel
        this.setupGalleryPanel();

        // Restore last active mode (Canvas or Plot)
        this.restoreActiveMode();

        // Ensure all toolbar sections start collapsed
        this.ensureToolbarCollapsed();

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

        // Setup ruler dragging for panning
        this.setupRulerDragging();

        // Setup wheel event handling for ruler areas and wrapper
        this.setupWrapperWheelHandling();

        console.log("[VisEditor] Ready - Auto-save enabled");
    }

    // Quick tips removed - no longer needed

    private initCanvas() {
        const canvasElement = document.getElementById('vis-canvas') as HTMLCanvasElement;
        if (!canvasElement) {
            console.error("[VisEditor] Canvas element not found");
            return;
        }

        // Clean up any old inline styles on container to ensure CSS defaults are used
        const containerEl = document.querySelector('.vis-canvas-container') as HTMLElement;
        if (containerEl) {
            containerEl.style.removeProperty('padding');
            console.log('[VisEditor] Cleared inline padding from canvas container for ruler alignment');
        }

        // Create Fabric canvas with default size (2 columns, full width)
        // Use class constants to enforce maximum dimensions
        const defaultWidth = this.MAX_CANVAS_WIDTH;   // 180mm @ 300dpi (11.811 px/mm)
        const defaultHeight = this.MAX_CANVAS_HEIGHT; // 215mm @ 300dpi

        // SCIENTIFIC INTEGRITY: Canvas background ALWAYS white (#ffffff)
        // regardless of UI theme (light/dark). This ensures exported figures
        // are publication-ready and theme-independent.
        this.canvas = new fabric.Canvas('vis-canvas', {
            width: defaultWidth,
            height: defaultHeight,
            backgroundColor: '#ffffff',  // NEVER change - scientific integrity
            selection: true,
            selectionKey: 'ctrlKey',  // PowerPoint-style: Ctrl+Click for multi-selection
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
            this.canvas!.bringToFront(img);  // Ensure new images are in front
            this.canvas!.setActiveObject(img);
            this.canvas!.renderAll();

            this.updateStatus(`Added image: ${filename}`);
            console.log(`[VisEditor] Image added: ${filename}`);
        });
    }

    private setupCanvasEvents() {
        if (!this.canvas) return;

        // Mouse down - Check for panning (Space key) or Ctrl+Drag duplication
        this.canvas.on('mouse:down', (e) => {
            const evt = e.e as MouseEvent;
            const activeObject = this.canvas?.getActiveObject();

            // Middle mouse button or Space+Click = Pan mode
            if (evt.button === 1 || ((evt as any).spaceKey || (window.event as any)?.keyCode === 32)) {
                this.isPanning = true;
                this.panStartPoint = { x: evt.clientX, y: evt.clientY };
                this.canvas!.selection = false;  // Disable selection while panning
                const canvasEl = document.getElementById('vis-canvas');
                if (canvasEl) canvasEl.style.cursor = 'grabbing';
                return;
            }

            // If Ctrl is held and an object is selected, prepare for duplication
            if ((evt.ctrlKey || evt.metaKey) && activeObject && activeObject.type !== 'activeSelection') {
                this.isDuplicatingWithDrag = true;
                this.dragStartPosition = { x: evt.clientX, y: evt.clientY };
            }
        });

        // Mouse move - Handle panning (pan rulers + canvas together)
        this.canvas.on('mouse:move', (e) => {
            if (this.isPanning && this.panStartPoint) {
                const evt = e.e as MouseEvent;
                let deltaX = evt.clientX - this.panStartPoint.x;
                let deltaY = evt.clientY - this.panStartPoint.y;

                // Alt key = Fine-tuned panning (10% speed)
                if (evt.altKey) {
                    deltaX *= 0.1;
                    deltaY *= 0.1;
                }

                this.panOffset.x += deltaX;
                this.panOffset.y += deltaY;
                this.updateTransform();

                this.panStartPoint = { x: evt.clientX, y: evt.clientY };
            }
        });

        // Object moving - Handle Ctrl+Drag duplication, Alt for fine movement, snap to grid, and show alignment guides
        this.canvas.on('object:moving', (e) => {
            if (!e.target) return;

            const obj = e.target;
            const evt = e.e as MouseEvent;

            // Check for Ctrl+Drag duplication (PowerPoint-style)
            if (this.isDuplicatingWithDrag && this.dragStartPosition) {
                const dx = Math.abs(evt.clientX - this.dragStartPosition.x);
                const dy = Math.abs(evt.clientY - this.dragStartPosition.y);

                // If moved more than 5 pixels, duplicate the object
                if (dx > 5 || dy > 5) {
                    this.isDuplicatingWithDrag = false;
                    this.dragStartPosition = null;

                    // Clone the object at original position
                    obj.clone((cloned: any) => {
                        cloned.set({
                            left: obj.left,
                            top: obj.top,
                        });
                        this.canvas!.add(cloned);
                        this.canvas!.bringToFront(cloned);  // Ensure duplicated objects are in front
                        this.canvas!.setActiveObject(cloned);
                        this.canvas!.renderAll();
                    });

                    this.updateStatus('Duplicating with Ctrl+Drag');
                    return;
                }
            }

            let left = obj.left || 0;
            let top = obj.top || 0;

            // Alt key = Fine-tuned movement (disable snapping, slower movement)
            const isFineTuning = evt.altKey;

            if (isFineTuning) {
                // Fine movement - no snapping, no alignment guides
                // Movement is already slowed by the reduced mouse movement
                this.hideAlignmentGuides();
            } else {
                // Normal movement - apply snapping and alignment

                // Grid snapping (1mm resolution by default)
                if (this.snapEnabled) {
                    left = Math.round(left / this.snapSize) * this.snapSize;
                    top = Math.round(top / this.snapSize) * this.snapSize;
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
            }

            obj.set({ left, top });
        });

        // Mouse up - Reset duplication and panning flags
        this.canvas.on('mouse:up', () => {
            this.isDuplicatingWithDrag = false;
            this.dragStartPosition = null;

            if (this.isPanning) {
                this.isPanning = false;
                this.panStartPoint = null;
                this.canvas!.selection = true;  // Re-enable selection
                const canvasEl = document.getElementById('vis-canvas');
                if (canvasEl) canvasEl.style.cursor = 'default';
            }
        });

        // Clear alignment guides when movement stops
        this.canvas.on('object:modified', () => {
            this.hideAlignmentGuides();
        });

        // Selection changed
        this.canvas.on('selection:created', (e) => {
            this.updatePropertiesPanel();
            // Handle click cycling through layered objects
            this.handleClickCycling(e);
        });
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

        // Right-click context menu
        this.canvas.on('mouse:down', (e) => {
            if (e.button === 3 || (e.e as MouseEvent).button === 2) {
                e.e.preventDefault();
                const obj = this.canvas?.getActiveObject();
                if (obj) {
                    this.showContextMenu(e.e as MouseEvent, obj);
                }
            }
        });

        // Disable browser context menu on canvas
        const canvasElement = this.canvas.getElement();
        if (canvasElement) {
            canvasElement.addEventListener('contextmenu', (e) => {
                e.preventDefault();
            });
        }
    }

    private setupEventListeners() {
        // Mode switcher (Canvas / Plot Backend)
        document.querySelectorAll('.view-switch-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const mode = (e.currentTarget as HTMLElement).dataset.mode;
                if (mode) {
                    this.switchMode(mode);
                }
            });
        });

        // Hash change listener for URL-based navigation
        window.addEventListener('hashchange', () => {
            const hash = window.location.hash.substring(1);
            if (hash === 'canvas' || hash === 'plot') {
                const mode = hash === 'plot' ? 'backend' : 'canvas';
                console.log(`[VisEditor] Hash changed to: ${hash}, switching to mode: ${mode}`);
                this.switchMode(mode);
            }
        });

        // Collapsible toolbar sections
        document.querySelectorAll('.collapsible-header').forEach(header => {
            header.addEventListener('click', (e) => {
                const section = (e.currentTarget as HTMLElement).closest('.toolbar-section');
                if (section) {
                    section.classList.toggle('collapsed');
                }
            });
        });

        // Collapsible style-card sections
        document.querySelectorAll('.style-card-header[data-toggle]').forEach(header => {
            header.addEventListener('click', (e) => {
                const cardName = (header as HTMLElement).getAttribute('data-toggle');
                const contentDiv = document.querySelector(`.style-card-content[data-content="${cardName}"]`) as HTMLElement;
                const chevron = header.querySelector('.fa-chevron-right') as HTMLElement;

                if (contentDiv) {
                    const isHidden = contentDiv.style.display === 'none';
                    contentDiv.style.display = isHidden ? 'block' : 'none';

                    if (chevron) {
                        if (isHidden) {
                            chevron.style.transform = 'rotate(90deg)';
                        } else {
                            chevron.style.transform = 'rotate(0deg)';
                        }
                    }
                }
            });
        });

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

        // Window resize listener - redraw rulers when window size changes
        window.addEventListener('resize', () => {
            // Debounce to avoid excessive redraws during continuous resizing
            if (this.resizeTimeout) {
                clearTimeout(this.resizeTimeout);
            }
            this.resizeTimeout = setTimeout(() => {
                this.drawRulers();
            }, 150); // 150ms debounce
        });

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

        // Panel toggle buttons
        const toggleToolbar = document.getElementById('toggle-toolbar');
        if (toggleToolbar) {
            toggleToolbar.addEventListener('click', () => this.toggleToolbarPanel());
        }

        const toggleProperties = document.getElementById('toggle-properties');
        if (toggleProperties) {
            toggleProperties.addEventListener('click', () => this.togglePropertiesPanel());
        }

        // Zoom controls
        const zoomFitBtn = document.getElementById('zoom-fit');
        if (zoomFitBtn) {
            zoomFitBtn.addEventListener('click', () => this.zoomToFit());
        }

        // Mouse wheel handling - Zoom with Ctrl, Pan without
        // Uses requestAnimationFrame throttling to prevent crashes during fast scrolling
        this.canvas.on('mouse:wheel', (opt: any) => {
            const e = opt.e;
            e.preventDefault();
            e.stopPropagation();

            if (e.ctrlKey || e.metaKey) {
                // Ctrl+Wheel = Zoom centered on cursor
                const delta = e.deltaY;
                const oldZoom = this.zoomLevel;
                let newZoom = oldZoom * (0.999 ** delta);

                // Limit zoom range
                if (newZoom > 5) newZoom = 5;  // Max 500%
                if (newZoom < 0.1) newZoom = 0.1;  // Min 10%

                this.zoomLevel = newZoom;

                // Adjust pan offset to keep cursor position stable
                const pointer = opt.pointer;
                const zoomRatio = newZoom / oldZoom;
                this.panOffset.x = pointer.x - (pointer.x - this.panOffset.x) * zoomRatio;
                this.panOffset.y = pointer.y - (pointer.y - this.panOffset.y) * zoomRatio;

                // Throttle updates using requestAnimationFrame
                // This prevents excessive DOM updates during fast scrolling
                this.pendingTransform = () => {
                    this.updateTransform();
                    this.updateZoomDisplay();
                };

                if (!this.wheelThrottleFrame) {
                    this.wheelThrottleFrame = requestAnimationFrame(() => {
                        if (this.pendingTransform) {
                            this.pendingTransform();
                            this.pendingTransform = null;
                        }
                        this.wheelThrottleFrame = null;
                    });
                }
            } else {
                // Regular wheel = Pan canvas (rulers + canvas together)
                this.panOffset.x -= e.deltaX;
                this.panOffset.y -= e.deltaY;

                // Throttle pan updates as well
                this.pendingTransform = () => {
                    this.updateTransform();
                };

                if (!this.wheelThrottleFrame) {
                    this.wheelThrottleFrame = requestAnimationFrame(() => {
                        if (this.pendingTransform) {
                            this.pendingTransform();
                            this.pendingTransform = null;
                        }
                        this.wheelThrottleFrame = null;
                    });
                }
            }

            return false;
        });

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
            btn.addEventListener('click', (e) => {
                const modal = (e.target as HTMLElement).closest('.modal') as HTMLElement;
                if (modal) modal.style.display = 'none';
            });
        });

        // Skewer Selection modal - Select button
        const skewerSelectBtn = document.getElementById('skewer-select-btn');
        if (skewerSelectBtn) {
            skewerSelectBtn.addEventListener('click', () => {
                this.applySkewerSelection();
            });
        }

        // Color palette
        // Fill color swatches
        document.querySelectorAll('.color-swatch:not(.outline-swatch)').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const color = (e.currentTarget as HTMLElement).dataset.color;
                if (color) {
                    this.setCurrentColor(color);

                    // Update active state
                    document.querySelectorAll('.color-swatch:not(.outline-swatch)').forEach(b => b.classList.remove('active'));
                    (e.currentTarget as HTMLElement).classList.add('active');
                }
            });
        });

        // Custom color picker
        const customColorPicker = document.getElementById('customColorPicker') as HTMLInputElement;
        if (customColorPicker) {
            customColorPicker.addEventListener('change', (e) => {
                const hexColor = (e.target as HTMLInputElement).value;
                // Convert hex to RGB format
                const r = parseInt(hexColor.slice(1, 3), 16);
                const g = parseInt(hexColor.slice(3, 5), 16);
                const b = parseInt(hexColor.slice(5, 7), 16);
                const rgbColor = `rgb(${r},${g},${b})`;

                this.setCurrentColor(rgbColor);

                // Remove active state from all color swatches
                document.querySelectorAll('.color-swatch:not(.outline-swatch)').forEach(b => b.classList.remove('active'));
            });
        }

        // Outline color swatches
        document.querySelectorAll('.outline-swatch').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const outline = (e.currentTarget as HTMLElement).dataset.outline;
                if (outline) {
                    this.setCurrentStroke(outline);

                    // Update active state
                    document.querySelectorAll('.outline-swatch').forEach(b => b.classList.remove('active'));
                    (e.currentTarget as HTMLElement).classList.add('active');
                }
            });
        });

        // Line style buttons
        const lineSolid = document.getElementById('line-solid');
        if (lineSolid) {
            lineSolid.addEventListener('click', () => this.setStrokeStyle('solid'));
        }

        const lineDashed = document.getElementById('line-dashed');
        if (lineDashed) {
            lineDashed.addEventListener('click', () => this.setStrokeStyle('dashed'));
        }

        const lineDotted = document.getElementById('line-dotted');
        if (lineDotted) {
            lineDotted.addEventListener('click', () => this.setStrokeStyle('dotted'));
        }

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

        // Version comparison controls
        const comparisonModeSelect = document.getElementById('comparison-mode') as HTMLSelectElement;
        if (comparisonModeSelect) {
            comparisonModeSelect.addEventListener('change', (e) => {
                this.comparisonMode = (e.target as HTMLSelectElement).value as any;
                this.switchComparisonMode();
            });
        }

        const saveAsOriginalBtn = document.getElementById('save-as-original-btn');
        if (saveAsOriginalBtn) {
            saveAsOriginalBtn.addEventListener('click', () => this.saveAsOriginal());
        }

        const versionsBtn = document.getElementById('versions-btn');
        if (versionsBtn) {
            versionsBtn.addEventListener('click', () => this.showVersionHistory());
        }

        // Keyboard shortcuts

        // Alignment tool buttons
        // Panel dropdown
        const panelSelect = document.getElementById('panel-select') as HTMLSelectElement;
        if (panelSelect) {
            panelSelect.addEventListener('change', () => {
                const value = panelSelect.value;
                if (!value) return;

                switch (value) {
                    case 'split-horizontal':
                        // TODO: Implement split horizontal
                        break;
                    case 'split-vertical':
                        // TODO: Implement split vertical
                        break;
                    case 'remove-panel':
                        // TODO: Implement remove panel
                        break;
                    case 'reset-layout':
                        // TODO: Implement reset layout
                        break;
                    case '2x2':
                        this.setLayout('2x2');
                        break;
                    case '1x3':
                        this.setLayout('1x3');
                        break;
                }

                panelSelect.value = ''; // Reset dropdown
            });
        }

        // Align & Distribute dropdown
        const alignSelect = document.getElementById('align-select') as HTMLSelectElement;
        if (alignSelect) {
            alignSelect.addEventListener('change', () => {
                const value = alignSelect.value;
                if (!value) return;

                switch (value) {
                    case 'left':
                        this.alignLeft();
                        break;
                    case 'center':
                        this.alignCenter();
                        break;
                    case 'right':
                        this.alignRight();
                        break;
                    case 'top':
                        this.alignTop();
                        break;
                    case 'middle':
                        this.alignMiddle();
                        break;
                    case 'bottom':
                        this.alignBottom();
                        break;
                    case 'distribute-h':
                        this.distributeHorizontally();
                        break;
                    case 'distribute-v':
                        this.distributeVertically();
                        break;
                }

                alignSelect.value = ''; // Reset dropdown
            });
        }

        // Distribution tool buttons
        const distributeHBtn = document.getElementById('distribute-h-btn');
        if (distributeHBtn) distributeHBtn.addEventListener('click', () => this.distributeHorizontally());

        const distributeVBtn = document.getElementById('distribute-v-btn');
        if (distributeVBtn) distributeVBtn.addEventListener('click', () => this.distributeVertically());

        // Keyboard shortcuts button
        const shortcutsBtn = document.getElementById('shortcuts-btn');
        if (shortcutsBtn) shortcutsBtn.addEventListener('click', () => this.showKeyboardShortcuts());
        document.addEventListener('keydown', (e) => {
            // Ctrl+C - Copy
            if ((e.ctrlKey || e.metaKey) && e.key === 'c') {
                const activeObject = this.canvas?.getActiveObject();
                if (activeObject && document.activeElement?.tagName !== 'INPUT') {
                    e.preventDefault();
                    this.copyObject();
                }
            }

            // Ctrl+V - Paste
            if ((e.ctrlKey || e.metaKey) && e.key === 'v') {
                if (document.activeElement?.tagName !== 'INPUT') {
                    e.preventDefault();
                    this.pasteObject();
                }
            }

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

            // Ctrl+Shift+] - Bring to front
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === '}') {  // Shift+] produces '}'
                e.preventDefault();
                this.bringToFront();
            }

            // Ctrl+Shift+[ - Send to back
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === '{') {  // Shift+[ produces '{'
                e.preventDefault();
                this.sendToBack();
            }

            // Ctrl+] - Bring forward
            if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key === ']') {
                e.preventDefault();
                this.bringForward();
            }

            // Ctrl+[ - Send backward
            if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key === '[') {
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

            // Ctrl+G - Group selected objects
            if ((e.ctrlKey || e.metaKey) && (e.key === 'g' || e.key === 'G') && !e.shiftKey) {
                e.preventDefault();
                this.groupObjects();
            }

            // Ctrl+Shift+G - Ungroup selected group
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'g' || e.key === 'G')) {
                e.preventDefault();
                this.ungroupObjects();
            }

            // Enter - Enter group to edit contents
            if (e.key === 'Enter' && !e.ctrlKey && !e.metaKey && document.activeElement?.tagName !== 'INPUT') {
                e.preventDefault();
                this.enterGroup();
            }

            // Space - Enable pan mode (visual feedback)
            if (e.key === ' ' && !e.ctrlKey && !e.metaKey && document.activeElement?.tagName !== 'INPUT') {
                e.preventDefault();
                const canvasEl = document.getElementById('vis-canvas');
                if (canvasEl && !this.isPanning) {
                    canvasEl.style.cursor = 'grab';
                }
            }
        });

        // Space key release - Disable pan mode cursor
        document.addEventListener('keyup', (e) => {
            if (e.key === ' ') {
                const canvasEl = document.getElementById('vis-canvas');
                if (canvasEl) {
                    canvasEl.style.cursor = 'default';
                }
            }
        });
    }

    /**
     * Setup plot gallery panel with thumbnails and interactions
     */
    private async setupGalleryPanel() {
        console.log('[VisEditor] Setting up plot gallery panel');

        try {
            // Load plot templates JSON
            const response = await fetch('/static/vis_app/img/plot_gallery/plot_templates.json');
            if (!response.ok) {
                console.error('[VisEditor] Failed to load plot templates');
                return;
            }

            const plotData = await response.json();
            let currentCategory = 'basic';
            let selectedPlotType: string | null = null;

            // Gallery toggle button
            const galleryToggle = document.getElementById('plot-gallery-toggle');
            const galleryDropdown = document.getElementById('plot-gallery-dropdown');

            if (galleryToggle && galleryDropdown) {
                galleryToggle.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const isOpen = galleryDropdown.style.display === 'block';

                    if (isOpen) {
                        galleryDropdown.style.display = 'none';
                        galleryToggle.classList.remove('active');
                    } else {
                        galleryDropdown.style.display = 'block';
                        galleryToggle.classList.add('active');
                        // Load thumbnails on first open if not already loaded
                        if (!galleryDropdown.dataset.loaded) {
                            this.loadGalleryThumbnails(plotData, 'basic');
                            galleryDropdown.dataset.loaded = 'true';
                        }
                    }
                });

                // Close dropdown when clicking outside
                document.addEventListener('click', (e) => {
                    if (!galleryDropdown.contains(e.target as Node) &&
                        e.target !== galleryToggle &&
                        !galleryToggle.contains(e.target as Node)) {
                        galleryDropdown.style.display = 'none';
                        galleryToggle.classList.remove('active');
                    }
                });
            }

            // Gallery tabs - switch category
            const galleryTabs = document.querySelectorAll('.gallery-tab');
            galleryTabs.forEach(tab => {
                tab.addEventListener('click', (e) => {
                    const category = (e.currentTarget as HTMLElement).dataset.category;
                    if (!category) return;

                    // Update active tab
                    galleryTabs.forEach(t => t.classList.remove('active'));
                    (e.currentTarget as HTMLElement).classList.add('active');

                    // Load thumbnails for this category
                    currentCategory = category;
                    this.loadGalleryThumbnails(plotData, category);
                });
            });

            // Close button for info panel
            const closeBtn = document.querySelector('.gallery-info-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    const infoPanel = document.getElementById('gallery-info');
                    if (infoPanel) {
                        infoPanel.style.display = 'none';
                    }
                    selectedPlotType = null;
                    // Clear selected state from thumbnails
                    document.querySelectorAll('.gallery-thumbnail').forEach(thumb => {
                        thumb.classList.remove('selected');
                    });
                });
            }

            // "Add to Canvas" button
            const useBtn = document.getElementById('gallery-use-btn');
            if (useBtn) {
                useBtn.addEventListener('click', () => {
                    if (selectedPlotType) {
                        this.addPlotToCanvas(plotData, selectedPlotType);

                        // Close dropdown and info panel after adding
                        if (galleryDropdown && galleryToggle) {
                            galleryDropdown.style.display = 'none';
                            galleryToggle.classList.remove('active');
                        }
                        const infoPanel = document.getElementById('gallery-info');
                        if (infoPanel) {
                            infoPanel.style.display = 'none';
                        }
                        selectedPlotType = null;
                        document.querySelectorAll('.gallery-thumbnail').forEach(thumb => {
                            thumb.classList.remove('selected');
                        });
                    }
                });
            }

            // Store plotData and selectedPlotType for later use
            (this as any).galleryPlotData = plotData;
            (this as any).gallerySelectedPlotType = () => selectedPlotType;
            (this as any).gallerySetSelectedPlotType = (type: string | null) => { selectedPlotType = type; };

        } catch (error) {
            console.error('[VisEditor] Error setting up gallery panel:', error);
        }
    }

    /**
     * Load and display thumbnails for a specific category
     */
    private loadGalleryThumbnails(plotData: any, category: string) {
        const thumbnailsContainer = document.getElementById('gallery-thumbnails');
        if (!thumbnailsContainer) return;

        // Clear existing thumbnails
        thumbnailsContainer.innerHTML = '';

        // Filter plot types by category
        const plotTypes = Object.entries(plotData.plot_types).filter(
            ([_, data]: [string, any]) => data.category === category
        );

        // Create thumbnail for each plot type
        plotTypes.forEach(([plotType, data]: [string, any]) => {
            const thumb = document.createElement('div');
            thumb.className = 'gallery-thumbnail';
            thumb.dataset.plotType = plotType;

            const img = document.createElement('img');
            img.src = `/static/vis_app/img/plot_gallery/${category}/${data.thumbnail}`;
            img.alt = data.name;
            // No lazy loading - render sample images immediately

            const label = document.createElement('div');
            label.className = 'gallery-thumbnail-label';
            label.textContent = data.name;

            thumb.appendChild(img);
            thumb.appendChild(label);

            // Click handler to show plot info
            thumb.addEventListener('click', () => {
                this.showPlotInfo(plotData, plotType);
            });

            thumbnailsContainer.appendChild(thumb);
        });

        console.log(`[VisEditor] Loaded ${plotTypes.length} thumbnails for category: ${category}`);
    }

    /**
     * Show detailed information about a selected plot type
     */
    private showPlotInfo(plotData: any, plotType: string) {
        const data = plotData.plot_types[plotType];
        if (!data) return;

        // Update selected state
        (this as any).gallerySetSelectedPlotType(plotType);
        document.querySelectorAll('.gallery-thumbnail').forEach(thumb => {
            if ((thumb as HTMLElement).dataset.plotType === plotType) {
                thumb.classList.add('selected');
            } else {
                thumb.classList.remove('selected');
            }
        });

        // Update info panel
        const nameEl = document.getElementById('gallery-plot-name');
        const descEl = document.getElementById('gallery-plot-desc');
        const requiredEl = document.getElementById('gallery-required-cols');
        const optionalEl = document.getElementById('gallery-optional-cols');
        const infoPanel = document.getElementById('gallery-info');

        if (nameEl) nameEl.textContent = data.name;
        if (descEl) descEl.textContent = data.description;
        if (requiredEl) requiredEl.textContent = data.data_columns.required.join(', ');
        if (optionalEl) optionalEl.textContent = data.data_columns.optional.join(', ') || 'None';
        if (infoPanel) infoPanel.style.display = 'block';

        console.log(`[VisEditor] Showing info for plot type: ${plotType}`);
    }

    /**
     * Add a plot image to canvas from gallery
     */
    private addPlotToCanvas(plotData: any, plotType: string) {
        const data = plotData.plot_types[plotType];
        if (!data || !this.canvas) return;

        // Get the image URL
        const imgUrl = `/static/vis_app/img/plot_gallery/${data.category}/${data.thumbnail}`;

        // Load image and add to canvas
        fabric.Image.fromURL(imgUrl, (img: fabric.Image) => {
            if (!this.canvas) return;

            // Scale image to fit canvas nicely (max 500px width)
            const maxWidth = 500;
            if (img.width && img.width > maxWidth) {
                img.scaleToWidth(maxWidth);
            }

            // Center on canvas
            img.set({
                left: (this.canvas.width || 0) / 2 - (img.getScaledWidth() || 0) / 2,
                top: (this.canvas.height || 0) / 2 - (img.getScaledHeight() || 0) / 2,
            });

            this.canvas.add(img);
            this.canvas.setActiveObject(img);
            this.canvas.renderAll();
            this.saveToHistory();

            this.updateStatus(`Added ${data.name} to canvas`);
            console.log(`[VisEditor] Added plot to canvas: ${plotType}`);
        });

        // Hide info panel after adding
        const infoPanel = document.getElementById('gallery-info');
        if (infoPanel) {
            infoPanel.style.display = 'none';
        }
    }


    /**
     * Ensure all toolbar sections start collapsed
     * This prevents localStorage or CSS loading issues from expanding sections
     */
    private ensureToolbarCollapsed() {
        const sections = document.querySelectorAll('.toolbar-section');
        sections.forEach(section => {
            if (!section.classList.contains('collapsed')) {
                section.classList.add('collapsed');
            }
        });
        console.log('[VisEditor] Ensured all toolbar sections are collapsed');
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
                // Enforce maximum dimensions using class constants
                const width = Math.min(preset.width_px, this.MAX_CANVAS_WIDTH);
                const height = Math.min(preset.height_px || Math.round(width * 0.67), this.MAX_CANVAS_HEIGHT);

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

                // Create panel border group (without label for flexibility)
                border.set('id', `panel-border-${baseLabel}`);
                border.set('panelId', baseLabel);
                border.set('selectable', false);  // Border not selectable
                border.set('evented', false);
                border.set('left', x);
                border.set('top', y);

                this.canvas.add(border);
                this.canvas.sendToBack(border);
                this.panelBorders.push(border);

                // Create panel label as separate, independently movable object
                const fontFamily = this.currentPreset?.font_family || 'Arial';
                const labelColor = this.darkCanvasMode ? '#ffffff' : '#000000';

                const text = new fabric.Text(displayLabel, {
                    left: x + 10,  // Position relative to panel
                    top: y + 10,
                    fontSize: this.fontSizes.panelLabel,  // 10pt for panel labels
                    fontFamily: fontFamily,
                    fontWeight: 'bold',
                    fill: labelColor,
                    selectable: true,
                    hasControls: false,  // No resize handles
                    lockScalingX: true,
                    lockScalingY: true,
                    lockRotation: true,
                    hoverCursor: 'move',
                } as any);
                text.set('id', `panel-label-${baseLabel}`);
                text.set('panelId', baseLabel);

                this.canvas.add(text);
                this.panelLabels.push(text);

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
            if (obj.id && obj.id.startsWith('panel-label-')) {
                const panelId = obj.panelId;
                if (panelId) {
                    const newLabel = this.formatPanelLabel(panelId);
                    obj.set('text', newLabel);
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

    // PowerPoint-style alignment methods
    private alignLeft() {
        const selected = this.getSelectedObjects();
        if (selected.length < 2) {
            this.updateStatus('Select at least 2 objects to align');
            return;
        }

        const minLeft = Math.min(...selected.map((obj: any) => obj.left));
        selected.forEach((obj: any) => {
            obj.set('left', minLeft);
            obj.setCoords();
        });

        this.canvas?.renderAll();
        this.saveToHistory();
        this.updateStatus(`${selected.length} objects aligned left`);
    }

    private alignCenter() {
        const selected = this.getSelectedObjects();
        if (selected.length < 2) {
            this.updateStatus('Select at least 2 objects to align');
            return;
        }

        const centers = selected.map((obj: any) => obj.left + (obj.getBoundingRect().width / 2));
        const avgCenter = centers.reduce((a, b) => a + b, 0) / centers.length;

        selected.forEach((obj: any) => {
            const newLeft = avgCenter - (obj.getBoundingRect().width / 2);
            obj.set('left', newLeft);
            obj.setCoords();
        });

        this.canvas?.renderAll();
        this.saveToHistory();
        this.updateStatus(`${selected.length} objects aligned center`);
    }

    private alignRight() {
        const selected = this.getSelectedObjects();
        if (selected.length < 2) {
            this.updateStatus('Select at least 2 objects to align');
            return;
        }

        const maxRight = Math.max(...selected.map((obj: any) => obj.left + obj.getBoundingRect().width));
        selected.forEach((obj: any) => {
            obj.set('left', maxRight - obj.getBoundingRect().width);
            obj.setCoords();
        });

        this.canvas?.renderAll();
        this.saveToHistory();
        this.updateStatus(`${selected.length} objects aligned right`);
    }

    private alignTop() {
        const selected = this.getSelectedObjects();
        if (selected.length < 2) {
            this.updateStatus('Select at least 2 objects to align');
            return;
        }

        const minTop = Math.min(...selected.map((obj: any) => obj.top));
        selected.forEach((obj: any) => {
            obj.set('top', minTop);
            obj.setCoords();
        });

        this.canvas?.renderAll();
        this.saveToHistory();
        this.updateStatus(`${selected.length} objects aligned top`);
    }

    private alignMiddle() {
        const selected = this.getSelectedObjects();
        if (selected.length < 2) {
            this.updateStatus('Select at least 2 objects to align');
            return;
        }

        const middles = selected.map((obj: any) => obj.top + (obj.getBoundingRect().height / 2));
        const avgMiddle = middles.reduce((a, b) => a + b, 0) / middles.length;

        selected.forEach((obj: any) => {
            const newTop = avgMiddle - (obj.getBoundingRect().height / 2);
            obj.set('top', newTop);
            obj.setCoords();
        });

        this.canvas?.renderAll();
        this.saveToHistory();
        this.updateStatus(`${selected.length} objects aligned middle`);
    }

    private alignBottom() {
        const selected = this.getSelectedObjects();
        if (selected.length < 2) {
            this.updateStatus('Select at least 2 objects to align');
            return;
        }

        const maxBottom = Math.max(...selected.map((obj: any) => obj.top + obj.getBoundingRect().height));
        selected.forEach((obj: any) => {
            obj.set('top', maxBottom - obj.getBoundingRect().height);
            obj.setCoords();
        });

        this.canvas?.renderAll();
        this.saveToHistory();
        this.updateStatus(`${selected.length} objects aligned bottom`);
    }

    private distributeHorizontally() {
        const selected = this.getSelectedObjects();
        if (selected.length < 3) {
            this.updateStatus('Select at least 3 objects to distribute');
            return;
        }

        // Sort by left position
        const sorted = selected.sort((a: any, b: any) => a.left - b.left);
        const leftMost = sorted[0].left;
        const rightMost = sorted[sorted.length - 1].left + sorted[sorted.length - 1].getBoundingRect().width;
        const totalSpace = rightMost - leftMost;

        // Calculate total width of all objects
        const totalObjWidth = sorted.reduce((sum: number, obj: any) => sum + obj.getBoundingRect().width, 0);
        const gap = (totalSpace - totalObjWidth) / (sorted.length - 1);

        let currentLeft = leftMost;
        sorted.forEach((obj: any, index: number) => {
            if (index !== 0 && index !== sorted.length - 1) {
                obj.set('left', currentLeft);
                obj.setCoords();
            }
            currentLeft += obj.getBoundingRect().width + gap;
        });

        this.canvas?.renderAll();
        this.saveToHistory();
        this.updateStatus(`${selected.length} objects distributed horizontally`);
    }

    private distributeVertically() {
        const selected = this.getSelectedObjects();
        if (selected.length < 3) {
            this.updateStatus('Select at least 3 objects to distribute');
            return;
        }

        // Sort by top position
        const sorted = selected.sort((a: any, b: any) => a.top - b.top);
        const topMost = sorted[0].top;
        const bottomMost = sorted[sorted.length - 1].top + sorted[sorted.length - 1].getBoundingRect().height;
        const totalSpace = bottomMost - topMost;

        // Calculate total height of all objects
        const totalObjHeight = sorted.reduce((sum: number, obj: any) => sum + obj.getBoundingRect().height, 0);
        const gap = (totalSpace - totalObjHeight) / (sorted.length - 1);

        let currentTop = topMost;
        sorted.forEach((obj: any, index: number) => {
            if (index !== 0 && index !== sorted.length - 1) {
                obj.set('top', currentTop);
                obj.setCoords();
            }
            currentTop += obj.getBoundingRect().height + gap;
        });

        this.canvas?.renderAll();
        this.saveToHistory();
        this.updateStatus(`${selected.length} objects distributed vertically`);
    }

    private getSelectedObjects(): fabric.Object[] {
        if (!this.canvas) return [];

        const activeObject = this.canvas.getActiveObject();
        if (!activeObject) return [];

        // If it's a selection group, get all objects
        if (activeObject.type === 'activeSelection') {
            return (activeObject as any).getObjects();
        }

        // Single object
        return [activeObject];
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

        // Remove existing panel borders and labels
        const objects = this.canvas.getObjects();
        objects.forEach((obj: any) => {
            if (obj.id && (obj.id.startsWith('panel-border-') || obj.id.startsWith('panel-label-'))) {
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
            case 'scientific-notation':
                this.addScientificNotation();
                break;
            case 'scalebar':
                this.addScaleBar();
                break;
            case 'arrow':
                this.addArrow();
                break;
            case 'rect-white':
                this.addRectangle('#ffffff', 'Rectangle');
                break;
            case 'circle':
                this.addCircle();
                break;
            case 'triangle':
                this.addTriangle();
                break;
            case 'diamond':
                this.addDiamond();
                break;
            case 'line':
                this.addLine();
                break;
            case 'ref-rect-1':
                this.addReferenceRectangles();
                break;
            case 'col-ruler':
                this.addColumnWidthRuler();
                break;
            case 'ref-col-0.5':
                this.addColumnReference('0.5');
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

    private addScientificNotation() {
        if (!this.canvas) return;

        const fontSize = this.currentPreset?.font_size_pt || 10;
        const fontFamily = this.currentPreset?.font_family || 'Arial';

        const notation = new fabric.Text('×10⁻³', {
            left: 150,
            top: 50,
            fontSize: fontSize * 2,
            fontFamily: fontFamily,
            fill: '#000000',
            selectable: true,
            evented: true,
        });

        this.canvas.add(notation);
        this.canvas.bringToFront(notation);
        this.canvas.setActiveObject(notation);
        this.canvas.renderAll();
        this.updateStatus('Scientific notation added (×10⁻³)');
    }

    private addReferenceRectangles() {
        if (!this.canvas) return;

        const fontSize = this.currentPreset?.font_size_pt || 10;
        const fontFamily = this.currentPreset?.font_family || 'Arial';
        const dpi = this.currentPreset?.dpi || 300;

        // Rectangle dimensions in mm
        // Order: largest to smallest (will be rendered back to front)
        const rects = [
            { widthMm: 50, heightMm: 50 * 0.7, color: 'rgba(50, 200, 50, 0.3)', label: 'Width 50 mm' },
            { widthMm: 40, heightMm: 40 * 0.7, color: 'rgba(255, 50, 50, 0.3)', label: 'Width 40 mm' },
            { widthMm: 30, heightMm: 30 * 0.7, color: 'rgba(0, 100, 255, 0.3)', label: 'Width 30 mm' }
        ];

        const objects: fabric.Object[] = [];
        const labelYOffset = -(fontSize * 1.5 + 5); // Position labels above the rectangles

        // Create all rectangles overlapped at the same position (top-left aligned)
        rects.forEach((rectSpec, index) => {
            // Use unitToPx for accurate conversion based on current DPI
            const widthPx = this.unitToPx(rectSpec.widthMm, dpi, 'mm');
            const heightPx = this.unitToPx(rectSpec.heightMm, dpi, 'mm');

            // Create rectangle with transparent color and no border
            // All rectangles at position (0, 0) so they overlap
            const rect = new fabric.Rect({
                left: 0,
                top: 0,
                width: widthPx,
                height: heightPx,
                fill: rectSpec.color,
                stroke: 'transparent',
                strokeWidth: 0,
            });

            // Create label positioned to the right of each rectangle with slight offset
            const labelXOffset = widthPx + 5;
            const label = new fabric.Text(rectSpec.label, {
                left: labelXOffset,
                top: 0 + (index * fontSize * 1.5), // Stack labels vertically
                fontSize: fontSize * 1.2,
                fontFamily: fontFamily,
                fill: '#000000',
            });

            objects.push(rect, label);
        });

        // Group all objects together
        const group = new fabric.Group(objects, {
            left: 50,
            top: 50,
            selectable: true,
            evented: true,
        });

        this.canvas.add(group);
        this.canvas.bringToFront(group);
        this.canvas.setActiveObject(group);
        this.canvas.renderAll();
        this.updateStatus('Reference rectangles added (30mm, 40mm, 50mm)');
    }

    private addColumnWidthRuler() {
        if (!this.canvas) return;

        const fontSize = this.currentPreset?.font_size_pt || 10;
        const fontFamily = this.currentPreset?.font_family || 'Arial';
        const dpi = this.currentPreset?.dpi || 300;

        // Standard height for column guides (about 10mm)
        const heightMm = 10;

        // Simplified column widths based on 90mm standard (largest to smallest for back-to-front rendering)
        // 0.5, 1.0, 1.5, 2.0 columns = 45mm, 90mm, 135mm, 180mm
        const columns = [
            { widthMm: 180, color: 'rgba(0, 128, 192, 0.2)', label: '2.0 Col (180mm)' },
            { widthMm: 135, color: 'rgba(0, 128, 192, 0.3)', label: '1.5 Col (135mm)' },
            { widthMm: 90,  color: 'rgba(0, 128, 192, 0.4)', label: '1.0 Col (90mm)' },
            { widthMm: 45,  color: 'rgba(0, 128, 192, 0.5)', label: '0.5 Col (45mm)' }
        ];

        const objects: fabric.Object[] = [];

        // Create overlapped column width rectangles
        columns.forEach((col, index) => {
            const widthPx = this.unitToPx(col.widthMm, dpi, 'mm');
            const heightPx = this.unitToPx(heightMm, dpi, 'mm');

            // Create rectangle with transparent color and no border
            const rect = new fabric.Rect({
                left: 0,
                top: 0,
                width: widthPx,
                height: heightPx,
                fill: col.color,
                stroke: 'transparent',
                strokeWidth: 0,
            });

            // Create label positioned to the right of each rectangle
            const label = new fabric.Text(col.label, {
                left: widthPx + 5,
                top: 0 + (index * fontSize * 1.5), // Stack labels vertically
                fontSize: fontSize * 1.2,
                fontFamily: fontFamily,
                fill: '#000000',
            });

            objects.push(rect, label);
        });

        // Group all objects together
        const group = new fabric.Group(objects, {
            left: 50,
            top: 50,
            selectable: true,
            evented: true,
        });

        this.canvas.add(group);
        this.canvas.bringToFront(group);
        this.canvas.setActiveObject(group);
        this.canvas.renderAll();
        this.updateStatus('Column width guides added (0.5, 1.0, 1.5, 2.0)');
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
            stroke: this.currentColor,
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

    private addCircle() {
        if (!this.canvas) return;

        const circle = new fabric.Circle({
            radius: 50,
            fill: this.currentColor,
            left: 100,
            top: 100,
            selectable: true,
            evented: true,
        } as any);

        this.canvas.add(circle);
        this.canvas.bringToFront(circle);
        this.canvas.setActiveObject(circle);
        this.canvas.renderAll();
        this.updateStatus('Circle added');
    }

    private addTriangle() {
        if (!this.canvas) return;

        const triangle = new fabric.Triangle({
            width: 100,
            height: 100,
            fill: this.currentColor,
            left: 100,
            top: 100,
            selectable: true,
            evented: true,
        } as any);

        this.canvas.add(triangle);
        this.canvas.bringToFront(triangle);
        this.canvas.setActiveObject(triangle);
        this.canvas.renderAll();
        this.updateStatus('Triangle added');
    }

    private addDiamond() {
        if (!this.canvas) return;

        // Create diamond as rotated square
        const diamond = new fabric.Rect({
            width: 80,
            height: 80,
            fill: this.currentColor,
            left: 100,
            top: 100,
            angle: 45,
            selectable: true,
            evented: true,
        } as any);

        this.canvas.add(diamond);
        this.canvas.bringToFront(diamond);
        this.canvas.setActiveObject(diamond);
        this.canvas.renderAll();
        this.updateStatus('Diamond added');
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
        this.canvas.bringToFront(group);  // Ensure new objects are in front
        this.canvas.setActiveObject(group);
        this.canvas.renderAll();
        this.updateStatus(`${size.charAt(0).toUpperCase() + size.slice(1)} reference added (${sizeInMm.width}×${sizeInMm.height}mm)`);
    }

    // Column Width Reference Rectangles
    private addColumnReference(type: '0.5' | 'single' | '1.5' | 'double') {
        if (!this.canvas) return;

        // Standard column widths in mm (simplified: 90mm base)
        // 0.5, 1.0, 1.5, 2.0 columns
        const mmToPx = 11.811;
        const heights = 60; // Standard height
        const widths = {
            '0.5': 45,        // 0.5 column (45mm)
            'single': 90,     // 1.0 column (90mm)
            '1.5': 135,       // 1.5 columns (135mm)
            'double': 180,    // 2.0 columns (180mm)
        };

        // Blue opacity levels (darker = narrower)
        const opacities = {
            '0.5': 1.0,       // Darkest
            'single': 0.8,
            '1.5': 0.6,
            'double': 0.4,    // Lightest
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
        this.canvas.bringToFront(group);  // Ensure new objects are in front
        this.canvas.setActiveObject(group);
        this.canvas.renderAll();
        this.updateStatus(`${type} column reference added (${widthMm}mm)`);
    }

    private groupObjects() {
        if (!this.canvas) return;

        const activeSelection = this.canvas.getActiveObject();
        if (!activeSelection || activeSelection.type !== 'activeSelection') {
            this.updateStatus('Select multiple objects to group (Ctrl+Click)');
            return;
        }

        const selectedObjects = (activeSelection as any).getObjects();
        if (selectedObjects.length < 2) {
            this.updateStatus('Select at least 2 objects to group');
            return;
        }

        // Create group from selected objects
        activeSelection.toGroup();
        this.canvas.requestRenderAll();
        this.saveToHistory();
        this.updateStatus(`${selectedObjects.length} objects grouped`);
    }

    private ungroupObjects() {
        if (!this.canvas) return;

        const activeObject = this.canvas.getActiveObject();
        if (!activeObject) {
            this.updateStatus('No object selected to ungroup');
            return;
        }

        if (activeObject.type !== 'group') {
            this.updateStatus('Selected object is not a group');
            return;
        }

        // Ungroup the selected group
        const group = activeObject as fabric.Group;
        const items = (group as any).getObjects();

        (group as any).toActiveSelection();
        this.canvas.requestRenderAll();
        this.saveToHistory();
        this.updateStatus(`Group ungrouped (${items.length} objects)`);
    }

    private enterGroup() {
        if (!this.canvas) return;

        const activeObject = this.canvas.getActiveObject();
        if (!activeObject) {
            this.updateStatus('No object selected');
            return;
        }

        if (activeObject.type !== 'group') {
            this.updateStatus('Selected object is not a group (select a group and press Enter to edit)');
            return;
        }

        // Convert group to active selection to edit individual objects
        const group = activeObject as fabric.Group;
        const items = (group as any).getObjects();

        (group as any).toActiveSelection();
        this.canvas.requestRenderAll();
        this.updateStatus(`Editing group (${items.length} objects) - Ctrl+G to regroup`);
    }

    private copyObject() {
        if (!this.canvas) return;

        const activeObject = this.canvas.getActiveObject();
        if (!activeObject) {
            this.updateStatus('No object selected to copy');
            return;
        }

        // Clone to clipboard
        activeObject.clone((cloned: any) => {
            this.clipboard = cloned;
            this.updateStatus('Object copied to clipboard');
        });
    }

    private pasteObject() {
        if (!this.canvas) return;

        if (!this.clipboard) {
            this.updateStatus('Clipboard is empty (copy an object first)');
            return;
        }

        // Clone from clipboard
        this.clipboard.clone((cloned: any) => {
            // Offset the pasted object
            cloned.set({
                left: (cloned.left || 0) + 20,
                top: (cloned.top || 0) + 20,
                evented: true,
            });

            // Handle groups properly
            if (cloned.type === 'activeSelection') {
                this.canvas!.discardActiveObject();
                cloned.canvas = this.canvas;
                cloned.forEachObject((obj: any) => {
                    this.canvas!.add(obj);
                    this.canvas!.bringToFront(obj);  // Ensure duplicated objects are in front
                });
                cloned.setCoords();
            } else {
                this.canvas!.add(cloned);
                this.canvas!.bringToFront(cloned);  // Ensure duplicated objects are in front
            }

            // Update clipboard reference for continuous pasting
            this.clipboard.set('top', cloned.top);
            this.clipboard.set('left', cloned.left);

            this.canvas!.setActiveObject(cloned);
            this.canvas!.requestRenderAll();
            this.saveToHistory();
            this.updateStatus('Object pasted');
        });
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
            this.canvas!.bringToFront(cloned);  // Ensure duplicated objects are in front
            this.canvas!.setActiveObject(cloned);
            this.canvas!.renderAll();
            this.updateStatus('Object duplicated');
        });
    }

    private bringToFront() {
        const activeObject = this.canvas?.getActiveObject();
        if (!activeObject || !this.canvas) return;

        const allObjects = this.canvas.getObjects();
        const oldZIndex = allObjects.indexOf(activeObject);
        const fill = (activeObject as any).fill || 'none';
        const stroke = (activeObject as any).stroke || 'none';

        console.log('[Layer Order] BEFORE bringToFront:');
        console.log(`  Object: ${this.getObjectName(activeObject)}, fill: ${fill}, stroke: ${stroke}, z-index: ${oldZIndex}`);

        this.canvas.bringToFront(activeObject);
        this.canvas.requestRenderAll();  // Force full redraw

        const allObjectsAfter = this.canvas.getObjects();
        const newZIndex = allObjectsAfter.indexOf(activeObject);

        console.log('[Layer Order] AFTER bringToFront:');
        console.log(`  Object: ${this.getObjectName(activeObject)}, fill: ${fill}, stroke: ${stroke}, z-index: ${newZIndex}`);
        console.log('[Layer Order] Canvas redraw requested');

        this.updateStatus('Brought to front');
    }

    private sendToBack() {
        const activeObject = this.canvas?.getActiveObject();
        if (!activeObject || !this.canvas) return;

        const allObjects = this.canvas.getObjects();
        const oldZIndex = allObjects.indexOf(activeObject);
        const fill = (activeObject as any).fill || 'none';
        const stroke = (activeObject as any).stroke || 'none';

        console.log('[Layer Order] BEFORE sendToBack:');
        console.log(`  Object: ${this.getObjectName(activeObject)}, fill: ${fill}, stroke: ${stroke}, z-index: ${oldZIndex}`);

        this.canvas.sendToBack(activeObject);
        // Keep grid and panel borders at the very back
        this.canvas.getObjects().forEach((obj: any) => {
            if (obj.id === 'grid-line' || obj.id?.startsWith('panel-border')) {
                this.canvas?.sendToBack(obj);
            }
        });
        this.canvas.requestRenderAll();  // Force full redraw

        const allObjectsAfter = this.canvas.getObjects();
        const newZIndex = allObjectsAfter.indexOf(activeObject);

        console.log('[Layer Order] AFTER sendToBack:');
        console.log(`  Object: ${this.getObjectName(activeObject)}, fill: ${fill}, stroke: ${stroke}, z-index: ${newZIndex}`);
        console.log('[Layer Order] Canvas redraw requested');

        this.updateStatus('Sent to back');
    }

    private bringForward() {
        const activeObject = this.canvas?.getActiveObject();
        if (!activeObject || !this.canvas) return;

        const allObjects = this.canvas.getObjects();
        const oldZIndex = allObjects.indexOf(activeObject);
        const fill = (activeObject as any).fill || 'none';
        const stroke = (activeObject as any).stroke || 'none';

        console.log('[Layer Order] BEFORE bringForward:');
        console.log(`  Object: ${this.getObjectName(activeObject)}, fill: ${fill}, stroke: ${stroke}, z-index: ${oldZIndex}`);

        this.canvas.bringForward(activeObject);
        this.canvas.requestRenderAll();  // Force full redraw

        const allObjectsAfter = this.canvas.getObjects();
        const newZIndex = allObjectsAfter.indexOf(activeObject);

        console.log('[Layer Order] AFTER bringForward:');
        console.log(`  Object: ${this.getObjectName(activeObject)}, fill: ${fill}, stroke: ${stroke}, z-index: ${newZIndex}`);
        console.log(`  Expected: z-index should increase by 1 (was ${oldZIndex}, now ${newZIndex})`);
        console.log('[Layer Order] Canvas redraw requested');

        this.updateStatus('Brought forward');
    }

    private sendBackward() {
        const activeObject = this.canvas?.getActiveObject();
        if (!activeObject || !this.canvas) return;

        const allObjects = this.canvas.getObjects();
        const oldZIndex = allObjects.indexOf(activeObject);
        const fill = (activeObject as any).fill || 'none';
        const stroke = (activeObject as any).stroke || 'none';

        console.log('[Layer Order] BEFORE sendBackward:');
        console.log(`  Object: ${this.getObjectName(activeObject)}, fill: ${fill}, stroke: ${stroke}, z-index: ${oldZIndex}`);

        this.canvas.sendBackwards(activeObject);  // Note: Fabric.js uses 'sendBackwards' with an 's'
        this.canvas.requestRenderAll();  // Force full redraw

        const allObjectsAfter = this.canvas.getObjects();
        const newZIndex = allObjectsAfter.indexOf(activeObject);

        console.log('[Layer Order] AFTER sendBackward:');
        console.log(`  Object: ${this.getObjectName(activeObject)}, fill: ${fill}, stroke: ${stroke}, z-index: ${newZIndex}`);
        console.log(`  Expected: z-index should decrease by 1 (was ${oldZIndex}, now ${newZIndex})`);
        console.log('[Layer Order] Canvas redraw requested');

        this.updateStatus('Sent backward');
    }

    private drawGrid() {
        if (!this.canvas) return;

        const width = this.canvas.getWidth();
        const height = this.canvas.getHeight();

        // Clear existing grid
        this.clearGrid();

        // Choose grid color based on canvas background
        const gridColor = this.darkCanvasMode ? '#404040' : '#e5e5e5';
        const columnLineColor = this.darkCanvasMode ? '#0080c0' : '#0080c0'; // Blue for column positions

        // Column positions in pixels (at 300 DPI)
        const mmToPx = 11.811;
        const columnPositions = [45, 90, 135]; // 0.5, 1.0, 1.5 columns (in mm)

        // Draw 2mm grid - vertical lines
        for (let i = 0; i <= width / this.gridSize; i++) {
            const x = i * this.gridSize;
            const line = new fabric.Line([x, 0, x, height], {
                stroke: gridColor,
                strokeWidth: i % 5 === 0 ? 1 : 0.5,  // Major/minor lines every 10mm
                selectable: false,
                evented: false,
                hoverCursor: 'default',
                excludeFromExport: true,
            } as any);
            line.set('id', 'grid-line');
            line.set('selectable', false);
            line.set('evented', false);
            this.canvas.add(line);
            this.canvas.sendToBack(line);
        }

        // Draw 2mm grid - horizontal lines
        for (let i = 0; i <= height / this.gridSize; i++) {
            const y = i * this.gridSize;
            const line = new fabric.Line([0, y, width, y], {
                stroke: gridColor,
                strokeWidth: i % 5 === 0 ? 1 : 0.5,  // Major/minor lines every 10mm
                selectable: false,
                evented: false,
                hoverCursor: 'default',
                excludeFromExport: true,
            } as any);
            line.set('id', 'grid-line');
            line.set('selectable', false);
            line.set('evented', false);
            this.canvas.add(line);
            this.canvas.sendToBack(line);
        }

        // Draw column position guidelines (45mm, 90mm, 135mm)
        columnPositions.forEach(mmPos => {
            const x = mmPos * mmToPx;
            if (x <= width) {
                const line = new fabric.Line([x, 0, x, height], {
                    stroke: columnLineColor,
                    strokeWidth: 1.5,
                    strokeDashArray: [10, 5], // Dashed line
                    selectable: false,
                    evented: false,
                    hoverCursor: 'default',
                    excludeFromExport: true,
                    opacity: 0.4,
                } as any);
                line.set('id', 'grid-line');
                line.set('selectable', false);
                line.set('evented', false);
                this.canvas.add(line);
                this.canvas.sendToBack(line);
            }
        });

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

    private async exportTIFF() {
        if (!this.canvas) return;

        // TIFF export: Export as high-quality PNG then convert to TIFF at backend
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

            // Convert to TIFF via backend
            this.updateStatus('Converting to TIFF...');
            this.convertPNGtoTIFF(dataURL);
        });
    }

    private async convertPNGtoTIFF(pngDataURL: string) {
        try {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
            const filename = `figure_${timestamp}_300dpi.tiff`;

            const response = await fetch('/vis/api/convert/png-to-tiff/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    image_data: pngDataURL,
                    filename: filename,
                }),
            });

            if (response.ok) {
                // Download the TIFF file
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = filename;
                link.click();
                window.URL.revokeObjectURL(url);

                this.updateStatus('Exported as TIFF (300 DPI, LZW compression)');
                console.log('[Export] TIFF exported successfully');
            } else {
                const errorData = await response.json();
                this.updateStatus(`TIFF export failed: ${errorData.error || 'Unknown error'}`);
                console.error('[Export] TIFF conversion failed:', errorData);
            }
        } catch (error) {
            console.error('[Export] TIFF conversion error:', error);
            this.updateStatus('Error exporting TIFF');
        }
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

        const canvasState = this.canvas.toJSON(['id', 'panelId', 'filename']);
        console.log('[VisEditor] Saving figure...', canvasState);

        // Save to backend if figure ID exists
        if (this.figureId) {
            try {
                const response = await fetch(`/vis/api/figures/${this.figureId}/save/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken(),
                    },
                    body: JSON.stringify({ canvas_state: canvasState }),
                });

                const data = await response.json();

                if (data.success) {
                    this.updateStatus('Figure saved successfully');
                    console.log('[VisEditor] Figure saved to backend');
                } else {
                    this.updateStatus(`Save failed: ${data.error || 'Unknown error'}`);
                    console.error('[VisEditor] Save failed:', data);
                }
            } catch (error) {
                console.error('[VisEditor] Save error:', error);
                this.updateStatus('Error saving figure');
            }
        } else {
            // No figure ID - save to localStorage only
            this.autoSaveToLocalStorage();
            this.updateStatus('Saved to browser (no figure ID)');
        }
    }

    // Scientific Color Palette
    private setCurrentColor(color: string) {
        this.currentColor = color === 'none' ? 'transparent' : color;

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
            this.saveToHistory();
        }

        console.log(`[Color] Set to ${color}`);
    }

    private setCurrentStroke(color: string) {
        this.currentStroke = color === 'none' ? 'transparent' : color;

        // Apply to selected objects
        const activeObjects = this.canvas?.getActiveObjects();
        if (activeObjects && activeObjects.length > 0) {
            activeObjects.forEach((obj: any) => {
                obj.set('stroke', color);
            });
            this.canvas?.renderAll();
            this.saveToHistory();
        }

        console.log(`[Stroke] Set to ${color}`);
    }

    private setStrokeStyle(style: 'solid' | 'dashed' | 'dotted') {
        this.currentStrokeStyle = style;

        // Apply to selected objects
        const activeObjects = this.canvas?.getActiveObjects();
        if (activeObjects && activeObjects.length > 0) {
            const strokeDashArray = style === 'solid' ? [] : style === 'dashed' ? [10, 5] : [2, 2];
            activeObjects.forEach((obj: any) => {
                obj.set('strokeDashArray', strokeDashArray);
            });
            this.canvas?.renderAll();
            this.saveToHistory();
        }

        console.log(`[Stroke Style] Set to ${style}`);
    }

    private showContextMenu(event: MouseEvent, obj: any) {
        // TODO: Implement context menu
        console.log('[ContextMenu] Right-click on object:', obj);
    }

    private showKeyboardShortcuts() {
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        `;

        const content = document.createElement('div');
        content.style.cssText = `
            background: var(--vis-bg);
            border-radius: 8px;
            padding: 24px;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        `;

        const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
        const ctrlKey = isMac ? '⌘' : 'Ctrl';

        content.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2 style="margin: 0; color: var(--vis-text-primary); font-size: 24px;">Keyboard Shortcuts</h2>
                <button id="close-shortcuts" style="background: transparent; border: none; color: var(--vis-text-secondary); font-size: 24px; cursor: pointer; padding: 0; width: 32px; height: 32px;">&times;</button>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
                <!-- Selection & Editing -->
                <div>
                    <h3 style="color: var(--vis-text-primary); font-size: 14px; font-weight: 600; margin: 0 0 12px 0; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid var(--vis-border); padding-bottom: 8px;">Selection & Editing</h3>
                    <div class="shortcut-list">
                        <div class="shortcut-item"><kbd>${ctrlKey}</kbd> + <kbd>Click</kbd><span>Multi-select</span></div>
                        <div class="shortcut-item"><kbd>Alt</kbd> + <kbd>Click</kbd><span>Select from overlapping</span></div>
                        <div class="shortcut-item"><kbd>${ctrlKey}</kbd> + <kbd>C</kbd><span>Copy</span></div>
                        <div class="shortcut-item"><kbd>${ctrlKey}</kbd> + <kbd>V</kbd><span>Paste</span></div>
                        <div class="shortcut-item"><kbd>${ctrlKey}</kbd> + <kbd>D</kbd><span>Duplicate</span></div>
                        <div class="shortcut-item"><kbd>${ctrlKey}</kbd> + <kbd>Drag</kbd><span>Duplicate while dragging</span></div>
                        <div class="shortcut-item"><kbd>Delete</kbd> / <kbd>Backspace</kbd><span>Delete selected</span></div>
                    </div>
                </div>

                <!-- Layers & Grouping -->
                <div>
                    <h3 style="color: var(--vis-text-primary); font-size: 14px; font-weight: 600; margin: 0 0 12px 0; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid var(--vis-border); padding-bottom: 8px;">Layers & Grouping</h3>
                    <div class="shortcut-list">
                        <div class="shortcut-item"><kbd>${ctrlKey}</kbd> + <kbd>]</kbd><span>Bring forward</span></div>
                        <div class="shortcut-item"><kbd>${ctrlKey}</kbd> + <kbd>[</kbd><span>Send backward</span></div>
                        <div class="shortcut-item"><kbd>${ctrlKey}</kbd> + <kbd>G</kbd><span>Group</span></div>
                        <div class="shortcut-item"><kbd>${ctrlKey}</kbd> + <kbd>Shift</kbd> + <kbd>G</kbd><span>Ungroup</span></div>
                    </div>
                </div>

                <!-- View Controls -->
                <div>
                    <h3 style="color: var(--vis-text-primary); font-size: 14px; font-weight: 600; margin: 0 0 12px 0; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid var(--vis-border); padding-bottom: 8px;">View Controls</h3>
                    <div class="shortcut-list">
                        <div class="shortcut-item"><kbd>Space</kbd> + <kbd>Drag</kbd><span>Pan canvas</span></div>
                        <div class="shortcut-item"><kbd>${ctrlKey}</kbd> + <kbd>Wheel</kbd><span>Zoom at cursor</span></div>
                        <div class="shortcut-item"><kbd>+</kbd><span>Zoom in</span></div>
                        <div class="shortcut-item"><kbd>-</kbd><span>Zoom out</span></div>
                        <div class="shortcut-item"><kbd>0</kbd><span>Fit to window</span></div>
                    </div>
                </div>

                <!-- History & File -->
                <div>
                    <h3 style="color: var(--vis-text-primary); font-size: 14px; font-weight: 600; margin: 0 0 12px 0; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid var(--vis-border); padding-bottom: 8px;">History & File</h3>
                    <div class="shortcut-list">
                        <div class="shortcut-item"><kbd>${ctrlKey}</kbd> + <kbd>Z</kbd><span>Undo</span></div>
                        <div class="shortcut-item"><kbd>${ctrlKey}</kbd> + <kbd>Y</kbd><span>Redo</span></div>
                        <div class="shortcut-item"><kbd>${ctrlKey}</kbd> + <kbd>S</kbd><span>Save</span></div>
                    </div>
                </div>
            </div>

            <style>
                .shortcut-list {
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                }
                .shortcut-item {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    font-size: 13px;
                    color: var(--vis-text-secondary);
                }
                .shortcut-item kbd {
                    background: var(--vis-hover-bg);
                    border: 1px solid var(--vis-border);
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 12px;
                    color: var(--vis-text-primary);
                    box-shadow: 0 2px 0 var(--vis-border);
                }
                .shortcut-item span {
                    flex: 1;
                    color: var(--vis-text-primary);
                }
            </style>
        `;

        modal.appendChild(content);
        document.body.appendChild(modal);

        // Close handlers
        const closeBtn = content.querySelector('#close-shortcuts');
        const closeModal = () => {
            modal.remove();
        };

        closeBtn?.addEventListener('click', closeModal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });

        // ESC to close
        const escHandler = (e: KeyboardEvent) => {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);

        console.log('[Shortcuts] Keyboard shortcuts modal displayed');
    }

    // Crosshair Alignment Guides - Fixed positioning for pixel-perfect cursor tracking
    private initCrosshair() {
        const body = document.body;
        const canvasWrapper = document.querySelector('.vis-canvas-wrapper') as HTMLElement;
        if (!canvasWrapper) return;

        // Create crosshair elements with fixed positioning
        if (!this.crosshairH) {
            this.crosshairH = document.createElement('div');
            this.crosshairH.className = 'crosshair-horizontal';
            body.appendChild(this.crosshairH);
        }

        if (!this.crosshairV) {
            this.crosshairV = document.createElement('div');
            this.crosshairV.className = 'crosshair-vertical';
            body.appendChild(this.crosshairV);
        }

        // Mouse move handler - Use viewport coordinates directly
        const handleMouseMove = (e: MouseEvent) => {
            if (!this.crosshairH || !this.crosshairV) return;

            // Use clientX/clientY directly - viewport coordinates
            this.crosshairH.style.top = `${e.clientY}px`;
            this.crosshairV.style.left = `${e.clientX}px`;

            // Show crosshairs
            this.crosshairH.classList.add('visible');
            this.crosshairV.classList.add('visible');
        };

        // Click handler - Add guide lines at crosshair position
        const handleClick = (e: MouseEvent) => {
            if (!this.canvas || !this.crosshairEnabled) return;

            const pointer = this.canvas.getPointer(e);

            // Ctrl+Click = Add vertical guide line
            if (e.ctrlKey || e.metaKey) {
                e.preventDefault();
                this.addGuideLine('vertical', pointer.x);
                return;
            }

            // Shift+Click = Add horizontal guide line
            if (e.shiftKey) {
                e.preventDefault();
                this.addGuideLine('horizontal', pointer.y);
                return;
            }
        };

        const handleMouseLeave = () => {
            if (this.crosshairH) this.crosshairH.classList.remove('visible');
            if (this.crosshairV) this.crosshairV.classList.remove('visible');
        };

        canvasWrapper.addEventListener('mousemove', handleMouseMove);
        canvasWrapper.addEventListener('mouseleave', handleMouseLeave);
        canvasWrapper.addEventListener('click', handleClick);

        console.log('[Crosshair] Enabled - Ctrl+Click for V-line, Shift+Click for H-line');
    }

    private addGuideLine(orientation: 'horizontal' | 'vertical', position: number) {
        if (!this.canvas) return;

        const canvasWidth = this.canvas.getWidth();
        const canvasHeight = this.canvas.getHeight();

        let line: fabric.Line;
        if (orientation === 'horizontal') {
            // Horizontal guide line at Y position
            line = new fabric.Line([0, position, canvasWidth, position], {
                stroke: 'rgba(59, 130, 246, 0.8)',
                strokeWidth: 1,
                strokeDashArray: [5, 5],
                selectable: true,
                evented: true,
                lockRotation: true,
                lockScalingX: true,
                lockScalingY: true,
            } as any);
            line.set('id', 'guide-line-h');
            this.updateStatus('Horizontal guide line added - Drag to reposition');
        } else {
            // Vertical guide line at X position
            line = new fabric.Line([position, 0, position, canvasHeight], {
                stroke: 'rgba(59, 130, 246, 0.8)',
                strokeWidth: 1,
                strokeDashArray: [5, 5],
                selectable: true,
                evented: true,
                lockRotation: true,
                lockScalingX: true,
                lockScalingY: true,
            } as any);
            line.set('id', 'guide-line-v');
            this.updateStatus('Vertical guide line added - Drag to reposition');
        }

        this.canvas.add(line);
        this.canvas.bringToFront(line);  // Ensure new guide lines are in front
        this.canvas.setActiveObject(line);
        this.canvas.renderAll();
        this.saveToHistory();
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

            // Also darken the container (keep padding for ruler alignment)
            if (containerEl) {
                containerEl.style.backgroundColor = '#2a2a2a';
                // Remove inline padding to use CSS default (20px) for ruler alignment
                containerEl.style.removeProperty('padding');
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

            // Restore white container background
            if (containerEl) {
                containerEl.style.backgroundColor = '#ffffff';
                // Remove inline padding to use CSS default (20px) for ruler alignment
                containerEl.style.removeProperty('padding');
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

    private handleClickCycling(e: any) {
        if (!this.canvas) return;

        const currentTime = Date.now();
        const clickTimeout = 1000; // 1 second window for consecutive clicks
        const positionThreshold = 10; // pixels

        // Get pointer position
        const pointer = this.canvas.getPointer(e.e);

        // Check if this is a consecutive click in the same area
        const isSamePosition = this.lastClickPosition &&
            Math.abs(pointer.x - this.lastClickPosition.x) < positionThreshold &&
            Math.abs(pointer.y - this.lastClickPosition.y) < positionThreshold;

        const isWithinTimeout = (currentTime - this.lastClickTime) < clickTimeout;

        if (isSamePosition && isWithinTimeout) {
            // Consecutive click - cycle to next object
            if (this.clickCycleObjects.length > 1) {
                this.clickCycleIndex = (this.clickCycleIndex + 1) % this.clickCycleObjects.length;
                const nextObject = this.clickCycleObjects[this.clickCycleIndex];

                this.canvas.discardActiveObject();
                this.canvas.setActiveObject(nextObject);
                this.canvas.requestRenderAll();

                this.updateStatus(`Cycling through ${this.clickCycleObjects.length} layered objects (${this.clickCycleIndex + 1}/${this.clickCycleObjects.length})`);
            }
        } else {
            // New click location - find all objects at this position
            this.clickCycleObjects = this.getObjectsAtPoint(pointer);
            this.clickCycleIndex = 0;

            if (this.clickCycleObjects.length > 1) {
                this.updateStatus(`${this.clickCycleObjects.length} objects at this location - click again to cycle`);
            }
        }

        // Update tracking variables
        this.lastClickPosition = pointer;
        this.lastClickTime = currentTime;
    }

    private getObjectsAtPoint(pointer: {x: number, y: number}): fabric.Object[] {
        if (!this.canvas) return [];

        const tolerance = 5;
        const objects: fabric.Object[] = [];

        // Get all selectable objects (front to back)
        this.canvas.forEachObject((obj: any) => {
            if (!obj.selectable) return;
            if (obj.id && (obj.id === 'grid-line' || obj.id.startsWith('panel-border'))) return;

            const bound = obj.getBoundingRect();

            if (pointer.x >= bound.left - tolerance &&
                pointer.x <= bound.left + bound.width + tolerance &&
                pointer.y >= bound.top - tolerance &&
                pointer.y <= bound.top + bound.height + tolerance) {
                objects.push(obj);
            }
        });

        // Reverse to get front-to-back order
        return objects.reverse();
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
        // Sort by z-index (highest first - top layer)
        candidates.sort((a, b) => b.zIndex - a.zIndex);

        // Store current candidates and selected index
        (this as any).skewerCandidates = candidates;
        (this as any).skewerSelectedIndex = 0; // Default to top object

        // Populate modal
        const skewerList = document.getElementById('skewer-list');
        if (!skewerList) return;

        skewerList.innerHTML = '';

        candidates.forEach((candidate, index) => {
            const item = document.createElement('div');
            item.className = 'skewer-item';
            item.draggable = true;
            item.dataset.index = index.toString();

            if (index === 0) {
                item.classList.add('selected');
            }

            const type = candidate.object.type || 'object';
            const icon = this.getObjectIconHTML(type);

            item.innerHTML = `
                <i class="fas fa-grip-vertical skewer-handle"></i>
                ${icon}
                <div class="skewer-info">
                    <div class="skewer-name">${this.getObjectName(candidate.object)}</div>
                    <div class="skewer-type">${type}</div>
                </div>
                <div class="skewer-position">${index === 0 ? 'Front' : index === candidates.length - 1 ? 'Back' : `Layer ${candidates.length - index}`}</div>
            `;

            // Click to select
            item.addEventListener('click', () => {
                skewerList.querySelectorAll('.skewer-item').forEach(i => i.classList.remove('selected'));
                item.classList.add('selected');
                (this as any).skewerSelectedIndex = parseInt(item.dataset.index || '0');
            });

            // Drag & Drop events
            item.addEventListener('dragstart', (e) => {
                item.classList.add('dragging');
                e.dataTransfer!.effectAllowed = 'move';
                e.dataTransfer!.setData('text/plain', item.dataset.index || '0');
            });

            item.addEventListener('dragend', () => {
                item.classList.remove('dragging');
                // Update canvas z-order immediately after drag
                this.updateCanvasZOrder();
            });

            item.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer!.dropEffect = 'move';

                const draggingItem = skewerList.querySelector('.dragging');
                if (draggingItem && draggingItem !== item) {
                    const rect = item.getBoundingClientRect();
                    const midY = rect.top + rect.height / 2;
                    if (e.clientY < midY) {
                        skewerList.insertBefore(draggingItem, item);
                    } else {
                        skewerList.insertBefore(draggingItem, item.nextSibling);
                    }
                }
            });

            item.addEventListener('dragenter', (e) => {
                if (item.classList.contains('dragging')) return;
                item.classList.add('drag-over');
            });

            item.addEventListener('dragleave', () => {
                item.classList.remove('drag-over');
            });

            item.addEventListener('drop', (e) => {
                e.preventDefault();
                item.classList.remove('drag-over');
            });

            // Hover to highlight on canvas
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

            skewerList.appendChild(item);
        });

        // Show modal
        const modal = document.getElementById('skewer-modal');
        if (modal) {
            modal.style.display = 'flex';
        }

        this.updateStatus('Select object or drag to reorder');
    }

    private applySkewerSelection() {
        if (!this.canvas) return;

        const skewerList = document.getElementById('skewer-list');
        const modal = document.getElementById('skewer-modal');
        if (!skewerList || !modal) return;

        const candidates = (this as any).skewerCandidates;
        if (!candidates) return;

        // Get current order from DOM (after drag & drop)
        const items = Array.from(skewerList.querySelectorAll('.skewer-item'));
        const newOrder: any[] = [];

        items.forEach(item => {
            const originalIndex = parseInt((item as HTMLElement).dataset.index || '0');
            newOrder.push(candidates[originalIndex]);
        });

        // Apply new z-order on canvas
        // The DOM list shows front-to-back (index 0 = front, last = back)
        // bringToFront() makes each object the topmost, so we need to process in REVERSE
        // Process back-to-front: last item first, then work backwards to index 0
        // This way index 0 (front) is processed last and ends up on top
        for (let i = newOrder.length - 1; i >= 0; i--) {
            this.canvas.bringToFront(newOrder[i].object);
        }

        // Get selected object
        const selectedItem = skewerList.querySelector('.skewer-item.selected') as HTMLElement;
        const selectedIndex = selectedItem ? parseInt(selectedItem.dataset.index || '0') : 0;
        const selectedObject = candidates[selectedIndex].object;

        // Select the object
        this.canvas.setActiveObject(selectedObject);
        this.canvas.renderAll();

        // Save the reordering to history
        this.saveToHistory();

        // Close modal
        modal.style.display = 'none';

        this.updateStatus('Object selected and reordered');
    }

    private updateCanvasZOrder() {
        if (!this.canvas) return;

        const skewerList = document.getElementById('skewer-list');
        if (!skewerList) return;

        const candidates = (this as any).skewerCandidates;
        if (!candidates) return;

        // Get current order from DOM (after drag & drop)
        const items = Array.from(skewerList.querySelectorAll('.skewer-item'));
        const newOrder: any[] = [];

        items.forEach(item => {
            const originalIndex = parseInt((item as HTMLElement).dataset.index || '0');
            newOrder.push(candidates[originalIndex]);
        });

        console.log('[Skewer] BEFORE reordering:');
        const allObjects = this.canvas.getObjects();
        candidates.forEach((candidate: any, idx: number) => {
            const currentZIndex = allObjects.indexOf(candidate.object);
            const fill = candidate.object.fill || 'none';
            const stroke = candidate.object.stroke || 'none';
            console.log(`  [${idx}] ID: ${this.getObjectName(candidate.object)}, fill: ${fill}, stroke: ${stroke}, current z-index: ${currentZIndex}`);
        });

        console.log('[Skewer] NEW ORDER (DOM order, 0=front):');
        newOrder.forEach((item: any, idx: number) => {
            const fill = item.object.fill || 'none';
            const stroke = item.object.stroke || 'none';
            console.log(`  [${idx}] ID: ${this.getObjectName(item.object)}, fill: ${fill}, stroke: ${stroke}`);
        });

        // Apply new z-order on canvas
        // The DOM list shows front-to-back (index 0 = front, last = back)
        // bringToFront() makes each object the topmost, so we need to process in REVERSE
        // Process back-to-front: last item first, then work backwards to index 0
        // This way index 0 (front) is processed last and ends up on top
        for (let i = newOrder.length - 1; i >= 0; i--) {
            this.canvas.bringToFront(newOrder[i].object);
        }

        this.canvas.renderAll();

        console.log('[Skewer] AFTER reordering:');
        const allObjectsAfter = this.canvas.getObjects();
        newOrder.forEach((item: any, idx: number) => {
            const newZIndex = allObjectsAfter.indexOf(item.object);
            const fill = item.object.fill || 'none';
            const stroke = item.object.stroke || 'none';
            console.log(`  [${idx}] ID: ${this.getObjectName(item.object)}, fill: ${fill}, stroke: ${stroke}, new z-index: ${newZIndex}`);
        });
        console.log('[Skewer] Expected: index 0 (front) should have HIGHEST z-index, index ' + (newOrder.length - 1) + ' (back) should have LOWEST z-index');
        console.log('[Skewer] Z-order updated in real-time');

        // Update position labels in the skewer list
        items.forEach((item, index) => {
            const positionEl = (item as HTMLElement).querySelector('.skewer-position');
            if (positionEl) {
                positionEl.textContent = index === 0 ? 'Front' : index === items.length - 1 ? 'Back' : `Layer ${items.length - index}`;
            }
        });

        console.log('[Skewer] Z-order updated in real-time');
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

    private getObjectIconHTML(type: string): string {
        switch (type) {
            case 'text':
            case 'i-text': return '<i class="fas fa-font skewer-icon"></i>';
            case 'image': return '<i class="fas fa-image skewer-icon"></i>';
            case 'line': return '<i class="fas fa-minus skewer-icon"></i>';
            case 'group': return '<i class="fas fa-object-group skewer-icon"></i>';
            case 'rect': return '<i class="fas fa-square skewer-icon"></i>';
            case 'circle': return '<i class="fas fa-circle skewer-icon"></i>';
            case 'triangle': return '<i class="fas fa-play skewer-icon" style="transform: rotate(-30deg);"></i>';
            default: return '<i class="fas fa-shapes skewer-icon"></i>';
        }
    }

    private getObjectName(obj: any): string {
        if (obj.text) return `"${obj.text.substring(0, 20)}"`;
        if (obj.type === 'image' && obj.filename) return obj.filename;
        if (obj.type === 'group') return 'Group';
        return obj.type || 'Object';
    }

    private updateZoomDisplay() {
        // Update zoom display in header
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

    private zoomIn() {
        this.zoomLevel = Math.min(this.zoomLevel * 1.2, 5.0);  // Max 500%
        this.applyZoom();
    }

    private zoomOut() {
        this.zoomLevel = Math.max(this.zoomLevel / 1.2, 0.1);  // Min 10%
        this.applyZoom();
    }

    private toggleToolbarPanel() {
        const toolbar = document.querySelector('.vis-toolbar');
        const toggleBtn = document.getElementById('toggle-toolbar');

        if (toolbar && toggleBtn) {
            toolbar.classList.toggle('minimized');
            const isMinimized = toolbar.classList.contains('minimized');

            // Update button icon
            const icon = toggleBtn.querySelector('i');
            if (icon) {
                icon.className = isMinimized ? 'fas fa-chevron-right' : 'fas fa-chevron-left';
            }

            // Redraw rulers after panel size change
            setTimeout(() => this.drawRulers(), 300);
        }
    }

    private togglePropertiesPanel() {
        const properties = document.querySelector('.vis-properties');
        const toggleBtn = document.getElementById('toggle-properties');

        if (properties && toggleBtn) {
            properties.classList.toggle('minimized');
            const isMinimized = properties.classList.contains('minimized');

            // Update button icon
            const icon = toggleBtn.querySelector('i');
            if (icon) {
                icon.className = isMinimized ? 'fas fa-chevron-left' : 'fas fa-chevron-right';
            }

            // Redraw rulers after panel size change
            setTimeout(() => this.drawRulers(), 300);
        }
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

    // Setup wheel event handling for ruler areas and canvas wrapper
    // This handles scrolling in the "outer space" (rulers, corners, and wrapper background)
    private setupWrapperWheelHandling() {
        const canvasWrapper = document.querySelector('.vis-canvas-wrapper') as HTMLElement;
        const rulersArea = document.querySelector('.vis-rulers-area') as HTMLElement;

        if (!canvasWrapper || !rulersArea) return;

        // Add wheel event handler with throttling
        const handleWheel = (e: WheelEvent) => {
            // Only handle events on the wrapper or ruler elements, not the canvas itself
            const target = e.target as HTMLElement;
            const isCanvasElement = target.tagName === 'CANVAS' || target.closest('#vis-canvas');

            // Let the canvas handler deal with canvas events
            if (isCanvasElement) return;

            e.preventDefault();
            e.stopPropagation();

            if (e.ctrlKey || e.metaKey) {
                // Ctrl+Wheel = Zoom
                const delta = e.deltaY;
                const oldZoom = this.zoomLevel;
                let newZoom = oldZoom * (0.999 ** delta);

                // Limit zoom range
                if (newZoom > 5) newZoom = 5;  // Max 500%
                if (newZoom < 0.1) newZoom = 0.1;  // Min 10%

                this.zoomLevel = newZoom;

                // Center zoom on wrapper center when not on canvas
                const wrapperRect = canvasWrapper.getBoundingClientRect();
                const centerX = wrapperRect.width / 2;
                const centerY = wrapperRect.height / 2;
                const zoomRatio = newZoom / oldZoom;
                this.panOffset.x = centerX - (centerX - this.panOffset.x) * zoomRatio;
                this.panOffset.y = centerY - (centerY - this.panOffset.y) * zoomRatio;

                // Throttle updates using requestAnimationFrame
                this.pendingTransform = () => {
                    this.updateTransform();
                    this.updateZoomDisplay();
                };

                if (!this.wheelThrottleFrame) {
                    this.wheelThrottleFrame = requestAnimationFrame(() => {
                        if (this.pendingTransform) {
                            this.pendingTransform();
                            this.pendingTransform = null;
                        }
                        this.wheelThrottleFrame = null;
                    });
                }
            } else {
                // Regular wheel = Pan
                this.panOffset.x -= e.deltaX;
                this.panOffset.y -= e.deltaY;

                // Throttle pan updates
                this.pendingTransform = () => {
                    this.updateTransform();
                };

                if (!this.wheelThrottleFrame) {
                    this.wheelThrottleFrame = requestAnimationFrame(() => {
                        if (this.pendingTransform) {
                            this.pendingTransform();
                            this.pendingTransform = null;
                        }
                        this.wheelThrottleFrame = null;
                    });
                }
            }
        };

        // Add wheel event listeners to wrapper and rulers area
        canvasWrapper.addEventListener('wheel', handleWheel, { passive: false });
        rulersArea.addEventListener('wheel', handleWheel, { passive: false });

        console.log('[VisEditor] Wrapper wheel handling initialized with throttling');
    }

    private setupRulerDragging() {
        const rulerHorizontal = document.getElementById('ruler-horizontal');
        const rulerVertical = document.getElementById('ruler-vertical');
        const rulerHorizontalBottom = document.getElementById('ruler-horizontal-bottom');
        const rulerVerticalRight = document.getElementById('ruler-vertical-right');
        const rulerCorners = document.querySelectorAll('.ruler-corner');

        const rulers = [rulerHorizontal, rulerVertical, rulerHorizontalBottom, rulerVerticalRight, ...Array.from(rulerCorners)].filter(r => r) as HTMLElement[];

        rulers.forEach(ruler => {
            // Set cursor style
            ruler.style.cursor = 'grab';

            // Mouse down on ruler
            ruler.addEventListener('mousedown', (e) => {
                e.preventDefault();
                this.isPanning = true;
                this.panStartPoint = { x: e.clientX, y: e.clientY };
                ruler.style.cursor = 'grabbing';
            });

            // Mouse enter/leave for cursor feedback
            ruler.addEventListener('mouseenter', () => {
                if (!this.isPanning) ruler.style.cursor = 'grab';
            });

            ruler.addEventListener('mouseleave', () => {
                if (!this.isPanning) ruler.style.cursor = 'default';
            });
        });

        // Global mouse move and up for ruler dragging
        document.addEventListener('mousemove', (e) => {
            if (this.isPanning && this.panStartPoint) {
                let deltaX = e.clientX - this.panStartPoint.x;
                let deltaY = e.clientY - this.panStartPoint.y;

                // Alt key = Fine-tuned panning (10% speed)
                if (e.altKey) {
                    deltaX *= 0.1;
                    deltaY *= 0.1;
                }

                this.panOffset.x += deltaX;
                this.panOffset.y += deltaY;
                this.updateTransform();

                this.panStartPoint = { x: e.clientX, y: e.clientY };
            }
        });

        document.addEventListener('mouseup', () => {
            if (this.isPanning) {
                this.isPanning = false;
                this.panStartPoint = null;

                // Reset all ruler cursors
                rulers.forEach(ruler => {
                    ruler.style.cursor = 'grab';
                });
            }
        });
    }

    private updateTransform() {
        const rulersArea = document.querySelector('.vis-rulers-area') as HTMLElement;
        if (rulersArea) {
            // Apply both zoom and pan to the entire rulers area (rulers + canvas together)
            rulersArea.style.transform = `translate(${this.panOffset.x}px, ${this.panOffset.y}px) scale(${this.zoomLevel})`;
            rulersArea.style.transformOrigin = 'top left';
        }
    }

    private applyZoom() {
        if (!this.canvas) return;

        // Apply transform to rulers area (rulers + canvas stay together)
        this.updateTransform();
        this.updateZoomDisplay();
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

            // Restore grid if enabled (grid lines are not saved in history)
            if (this.gridEnabled) {
                this.drawGrid();
            }

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

                // Restore grid if enabled (grid lines are not saved, must be redrawn)
                if (this.gridEnabled) {
                    this.drawGrid();
                }

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

        // Preserve scroll position to prevent page jumping
        const scrollX = window.scrollX || window.pageXOffset;
        const scrollY = window.scrollY || window.pageYOffset;

        const dpi = this.currentPreset?.dpi || 300;
        const canvasWidth = this.canvas.getWidth();
        const canvasHeight = this.canvas.getHeight();

        this.drawHorizontalRuler(canvasWidth, dpi);
        this.drawVerticalRuler(canvasHeight, dpi);
        this.drawHorizontalBottomRuler(canvasWidth, dpi);
        this.drawVerticalRightRuler(canvasHeight, dpi);

        // Restore scroll position after ruler redraw
        window.scrollTo(scrollX, scrollY);
    }

    private drawHorizontalRuler(width: number, dpi: number) {
        const svg = document.getElementById('ruler-horizontal');
        if (!svg) return;

        svg.innerHTML = '';
        // Set exact dimensions to match canvas width - increased height for easier panning
        const rulerHeight = 60;
        svg.setAttribute('width', width.toString());
        svg.setAttribute('height', rulerHeight.toString());
        svg.setAttribute('viewBox', `0 0 ${width} ${rulerHeight}`);
        svg.style.width = `${width}px`;
        svg.style.height = `${rulerHeight}px`;

        const maxValue = this.pxToUnit(width, dpi, this.rulerUnit);
        const majorInterval = this.rulerUnit === 'mm' ? 10 : 1;      // 10mm or 1 inch
        const middleInterval = this.rulerUnit === 'mm' ? 5 : 0.5;    // 5mm or 0.5 inch
        const minorInterval = this.rulerUnit === 'mm' ? 1 : 0.125;   // 1mm or 1/8 inch

        // Draw all ticks in one pass for efficiency
        for (let i = minorInterval; i <= maxValue; i += minorInterval) {
            const x = this.unitToPx(i, dpi, this.rulerUnit);
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', x.toString());
            line.setAttribute('x2', x.toString());

            // Determine tick size and style based on position
            if (i % majorInterval === 0) {
                // Major tick (10mm) - tallest, with label (20px long)
                line.setAttribute('y1', '40');
                line.setAttribute('y2', rulerHeight.toString());
                line.setAttribute('stroke', '#999');
                line.setAttribute('stroke-width', '1.5');
                svg.appendChild(line);

                // Label with unit
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', x.toString());
                text.setAttribute('y', '40');
                // Use 'end' anchor for last label to prevent cutoff at right edge
                const isLastLabel = Math.abs(i - maxValue) < 0.01;
                text.setAttribute('text-anchor', isLastLabel ? 'end' : 'middle');
                text.setAttribute('font-size', '11');
                text.setAttribute('fill', '#666');
                text.textContent = `${i} ${this.rulerUnit}`;
                svg.appendChild(text);
            } else if (i % middleInterval === 0) {
                // Middle tick (5mm) - medium height (15px long)
                line.setAttribute('y1', '45');
                line.setAttribute('y2', rulerHeight.toString());
                line.setAttribute('stroke', '#aaa');
                line.setAttribute('stroke-width', '1');
                svg.appendChild(line);
            } else {
                // Minor tick (1mm) - shortest (10px long)
                line.setAttribute('y1', '50');
                line.setAttribute('y2', rulerHeight.toString());
                line.setAttribute('stroke', '#ccc');
                line.setAttribute('stroke-width', '0.5');
                svg.appendChild(line);
            }
        }

        // Draw 0 tick and label
        const zeroLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        zeroLine.setAttribute('x1', '0');
        zeroLine.setAttribute('y1', '40');  // Match major tick length
        zeroLine.setAttribute('x2', '0');
        zeroLine.setAttribute('y2', rulerHeight.toString());
        zeroLine.setAttribute('stroke', '#999');
        zeroLine.setAttribute('stroke-width', '1.5');
        svg.appendChild(zeroLine);

        const zeroText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        zeroText.setAttribute('x', '2');
        zeroText.setAttribute('y', '40');
        zeroText.setAttribute('text-anchor', 'start');  // Start anchor so text doesn't get cut off
        zeroText.setAttribute('font-size', '11');
        zeroText.setAttribute('fill', '#666');
        zeroText.textContent = `0 ${this.rulerUnit}`;
        svg.appendChild(zeroText);

        // Add column width markers (0.5, 1.0, 1.5 columns)
        // Column widths: 0.5=45mm, 1.0=90mm, 1.5=135mm
        if (this.rulerUnit === 'mm') {
            const columnMarkers = [
                { widthMm: 45, label: '0.5 col' },
                { widthMm: 90, label: '1.0 col' },
                { widthMm: 135, label: '1.5 col' }
            ];

            columnMarkers.forEach(marker => {
                const xPos = this.unitToPx(marker.widthMm, dpi, 'mm');

                // Only draw if within canvas width
                if (xPos <= width) {
                    // Draw vertical dashed line
                    const dashLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    dashLine.setAttribute('x1', xPos.toString());
                    dashLine.setAttribute('y1', '0');
                    dashLine.setAttribute('x2', xPos.toString());
                    dashLine.setAttribute('y2', rulerHeight.toString());
                    dashLine.setAttribute('stroke', '#0080c0');  // Blue color
                    dashLine.setAttribute('stroke-width', '1.5');
                    dashLine.setAttribute('stroke-dasharray', '4,2');  // Dashed pattern
                    dashLine.setAttribute('opacity', '0.6');
                    svg.appendChild(dashLine);

                    // Add label
                    const colText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                    colText.setAttribute('x', xPos.toString());
                    colText.setAttribute('y', '24');
                    colText.setAttribute('text-anchor', 'middle');
                    colText.setAttribute('font-size', '9');
                    colText.setAttribute('fill', '#0080c0');  // Same blue color
                    colText.setAttribute('font-weight', '600');
                    colText.textContent = marker.label;
                    svg.appendChild(colText);
                }
            });
        }
    }

    private drawVerticalRuler(height: number, dpi: number) {
        const svg = document.getElementById('ruler-vertical');
        if (!svg) return;

        svg.innerHTML = '';
        // Set exact dimensions to match canvas height - increased width for easier panning
        const rulerWidth = 60;
        svg.setAttribute('width', rulerWidth.toString());
        svg.setAttribute('height', height.toString());
        svg.setAttribute('viewBox', `0 0 ${rulerWidth} ${height}`);
        svg.style.width = `${rulerWidth}px`;
        svg.style.height = `${height}px`;

        const maxValue = this.pxToUnit(height, dpi, this.rulerUnit);
        const majorInterval = this.rulerUnit === 'mm' ? 10 : 1;      // 10mm or 1 inch
        const middleInterval = this.rulerUnit === 'mm' ? 5 : 0.5;    // 5mm or 0.5 inch
        const minorInterval = this.rulerUnit === 'mm' ? 1 : 0.125;   // 1mm or 1/8 inch

        // Draw all ticks in one pass for efficiency
        for (let i = minorInterval; i <= maxValue; i += minorInterval) {
            const y = this.unitToPx(i, dpi, this.rulerUnit);
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('y1', y.toString());
            line.setAttribute('y2', y.toString());

            // Determine tick size and style based on position
            if (i % majorInterval === 0) {
                // Major tick (10mm) - tallest, with label
                line.setAttribute('x1', '40');
                line.setAttribute('x2', rulerWidth.toString());
                line.setAttribute('stroke', '#999');
                line.setAttribute('stroke-width', '1.5');
                svg.appendChild(line);

                // Label with unit
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', '40');
                // Adjust y position for last label to prevent cutoff at bottom edge
                const isLastLabel = Math.abs(i - maxValue) < 0.01;
                text.setAttribute('y', isLastLabel ? (y - 8).toString() : (y + 4).toString());
                text.setAttribute('text-anchor', 'middle');
                text.setAttribute('font-size', '11');
                text.setAttribute('fill', '#666');
                text.textContent = `${i} ${this.rulerUnit}`;
                svg.appendChild(text);
            } else if (i % middleInterval === 0) {
                // Middle tick (5mm) - medium height
                line.setAttribute('x1', '45');
                line.setAttribute('x2', rulerWidth.toString());
                line.setAttribute('stroke', '#aaa');
                line.setAttribute('stroke-width', '1');
                svg.appendChild(line);
            } else {
                // Minor tick (1mm) - shortest
                line.setAttribute('x1', '50');
                line.setAttribute('x2', rulerWidth.toString());
                line.setAttribute('stroke', '#ccc');
                line.setAttribute('stroke-width', '0.5');
                svg.appendChild(line);
            }
        }

        // Draw 0 tick and label
        const zeroLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        zeroLine.setAttribute('x1', '40');
        zeroLine.setAttribute('y1', '0');
        zeroLine.setAttribute('x2', rulerWidth.toString());
        zeroLine.setAttribute('y2', '0');
        zeroLine.setAttribute('stroke', '#999');
        zeroLine.setAttribute('stroke-width', '1.5');
        svg.appendChild(zeroLine);

        const zeroText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        zeroText.setAttribute('x', '40');
        zeroText.setAttribute('y', '15');  // Moved down so text is fully visible
        zeroText.setAttribute('text-anchor', 'middle');
        zeroText.setAttribute('font-size', '11');
        zeroText.setAttribute('fill', '#666');
        zeroText.textContent = `0 ${this.rulerUnit}`;
        svg.appendChild(zeroText);
    }

    private drawHorizontalBottomRuler(width: number, dpi: number) {
        const svg = document.getElementById('ruler-horizontal-bottom');
        if (!svg) return;

        svg.innerHTML = '';
        // Set exact dimensions to match canvas width - increased height for easier panning
        const rulerHeight = 60;
        svg.setAttribute('width', width.toString());
        svg.setAttribute('height', rulerHeight.toString());
        svg.setAttribute('viewBox', `0 0 ${width} ${rulerHeight}`);
        svg.style.width = `${width}px`;
        svg.style.height = `${rulerHeight}px`;

        const maxValue = this.pxToUnit(width, dpi, this.rulerUnit);
        const majorInterval = this.rulerUnit === 'mm' ? 10 : 1;      // 10mm or 1 inch
        const middleInterval = this.rulerUnit === 'mm' ? 5 : 0.5;    // 5mm or 0.5 inch
        const minorInterval = this.rulerUnit === 'mm' ? 1 : 0.125;   // 1mm or 1/8 inch

        // Draw all ticks in one pass for efficiency
        for (let i = minorInterval; i <= maxValue; i += minorInterval) {
            const x = this.unitToPx(i, dpi, this.rulerUnit);
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', x.toString());
            line.setAttribute('x2', x.toString());

            // Determine tick size and style based on position
            if (i % majorInterval === 0) {
                // Major tick (10mm) - tallest, with label (20px long)
                line.setAttribute('y1', '0');
                line.setAttribute('y2', '20');
                line.setAttribute('stroke', '#999');
                line.setAttribute('stroke-width', '1.5');
                svg.appendChild(line);

                // Label with unit
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', x.toString());
                text.setAttribute('y', '95');
                // Use 'end' anchor for last label to prevent cutoff at right edge
                const isLastLabel = Math.abs(i - maxValue) < 0.01;
                text.setAttribute('text-anchor', isLastLabel ? 'end' : 'middle');
                text.setAttribute('font-size', '11');
                text.setAttribute('fill', '#666');
                text.textContent = `${i} ${this.rulerUnit}`;
                svg.appendChild(text);
            } else if (i % middleInterval === 0) {
                // Middle tick (5mm) - medium height
                line.setAttribute('y1', '0');
                line.setAttribute('y2', '15');
                line.setAttribute('stroke', '#aaa');
                line.setAttribute('stroke-width', '1');
                svg.appendChild(line);
            } else {
                // Minor tick (1mm) - shortest
                line.setAttribute('y1', '0');
                line.setAttribute('y2', '10');
                line.setAttribute('stroke', '#ccc');
                line.setAttribute('stroke-width', '0.5');
                svg.appendChild(line);
            }
        }

        // Draw 0 tick and label
        const zeroLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        zeroLine.setAttribute('x1', '0');
        zeroLine.setAttribute('y1', '0');
        zeroLine.setAttribute('x2', '0');
        zeroLine.setAttribute('y2', '20');
        zeroLine.setAttribute('stroke', '#999');
        zeroLine.setAttribute('stroke-width', '1.5');
        svg.appendChild(zeroLine);

        const zeroText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        zeroText.setAttribute('x', '2');
        zeroText.setAttribute('y', '95');
        zeroText.setAttribute('text-anchor', 'start');  // Start anchor so text doesn't get cut off
        zeroText.setAttribute('font-size', '11');
        zeroText.setAttribute('fill', '#666');
        zeroText.textContent = `0 ${this.rulerUnit}`;
        svg.appendChild(zeroText);

        // Add column width markers (0.5, 1.0, 1.5 columns)
        // Column widths: 0.5=45mm, 1.0=90mm, 1.5=135mm
        if (this.rulerUnit === 'mm') {
            const columnMarkers = [
                { widthMm: 45, label: '0.5 col' },
                { widthMm: 90, label: '1.0 col' },
                { widthMm: 135, label: '1.5 col' }
            ];

            columnMarkers.forEach(marker => {
                const xPos = this.unitToPx(marker.widthMm, dpi, 'mm');

                // Only draw if within canvas width
                if (xPos <= width) {
                    // Draw vertical dashed line
                    const dashLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    dashLine.setAttribute('x1', xPos.toString());
                    dashLine.setAttribute('y1', '0');
                    dashLine.setAttribute('x2', xPos.toString());
                    dashLine.setAttribute('y2', rulerHeight.toString());
                    dashLine.setAttribute('stroke', '#0080c0');  // Blue color
                    dashLine.setAttribute('stroke-width', '1.5');
                    dashLine.setAttribute('stroke-dasharray', '4,2');  // Dashed pattern
                    dashLine.setAttribute('opacity', '0.6');
                    svg.appendChild(dashLine);

                    // Add label
                    const colText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                    colText.setAttribute('x', xPos.toString());
                    colText.setAttribute('y', '109');
                    colText.setAttribute('text-anchor', 'middle');
                    colText.setAttribute('font-size', '9');
                    colText.setAttribute('fill', '#0080c0');  // Same blue color
                    colText.setAttribute('font-weight', '600');
                    colText.textContent = marker.label;
                    svg.appendChild(colText);
                }
            });
        }
    }

    private drawVerticalRightRuler(height: number, dpi: number) {
        const svg = document.getElementById('ruler-vertical-right');
        if (!svg) return;

        svg.innerHTML = '';
        // Set exact dimensions to match canvas height - increased width for easier panning
        svg.setAttribute('width', '60');
        svg.setAttribute('height', height.toString());
        svg.setAttribute('viewBox', `0 0 60 ${height}`);
        svg.style.width = '60px';
        svg.style.height = `${height}px`;

        const maxValue = this.pxToUnit(height, dpi, this.rulerUnit);
        const majorInterval = this.rulerUnit === 'mm' ? 10 : 1;      // 10mm or 1 inch
        const middleInterval = this.rulerUnit === 'mm' ? 5 : 0.5;    // 5mm or 0.5 inch
        const minorInterval = this.rulerUnit === 'mm' ? 1 : 0.125;   // 1mm or 1/8 inch

        // Draw all ticks in one pass for efficiency
        for (let i = minorInterval; i <= maxValue; i += minorInterval) {
            const y = this.unitToPx(i, dpi, this.rulerUnit);
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('y1', y.toString());
            line.setAttribute('y2', y.toString());

            // Determine tick size and style based on position
            if (i % majorInterval === 0) {
                // Major tick (10mm) - tallest, with label
                line.setAttribute('x1', '0');
                line.setAttribute('x2', '20');
                line.setAttribute('stroke', '#999');
                line.setAttribute('stroke-width', '1.5');
                svg.appendChild(line);

                // Label with unit (rotated for vertical ruler)
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', '83');
                // Use 'end' anchor for last label to prevent cutoff at bottom edge
                const isLastLabel = Math.abs(i - maxValue) < 0.01;
                text.setAttribute('y', (y + 4).toString());
                text.setAttribute('text-anchor', isLastLabel ? 'end' : 'middle');
                text.setAttribute('font-size', '11');
                text.setAttribute('fill', '#666');
                text.setAttribute('transform', `rotate(90, 83, ${y})`);
                text.textContent = `${i} ${this.rulerUnit}`;
                svg.appendChild(text);
            } else if (i % middleInterval === 0) {
                // Middle tick (5mm) - medium height
                line.setAttribute('x1', '0');
                line.setAttribute('x2', '15');
                line.setAttribute('stroke', '#aaa');
                line.setAttribute('stroke-width', '1');
                svg.appendChild(line);
            } else {
                // Minor tick (1mm) - shortest
                line.setAttribute('x1', '0');
                line.setAttribute('x2', '10');
                line.setAttribute('stroke', '#ccc');
                line.setAttribute('stroke-width', '0.5');
                svg.appendChild(line);
            }
        }

        // Draw 0 tick and label
        const zeroLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        zeroLine.setAttribute('x1', '0');
        zeroLine.setAttribute('y1', '0');
        zeroLine.setAttribute('x2', '20');
        zeroLine.setAttribute('y2', '0');
        zeroLine.setAttribute('stroke', '#999');
        zeroLine.setAttribute('stroke-width', '1.5');
        svg.appendChild(zeroLine);

        const zeroText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        zeroText.setAttribute('x', '83');
        zeroText.setAttribute('y', '20');  // Position adjusted for rotated text visibility at top edge
        zeroText.setAttribute('text-anchor', 'start');  // Start anchor so text extends downward after rotation
        zeroText.setAttribute('font-size', '11');
        zeroText.setAttribute('fill', '#666');
        zeroText.setAttribute('transform', 'rotate(90, 83, 0)');
        zeroText.textContent = `0 ${this.rulerUnit}`;
        svg.appendChild(zeroText);
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

    // ========================================================================
    // Mode Switching (Canvas Editor / Plot Backend)
    // ========================================================================

    private restoreActiveMode() {
        try {
            // Priority 1: Check URL hash
            const hash = window.location.hash.substring(1); // Remove # prefix
            if (hash === 'canvas' || hash === 'plot') {
                const mode = hash === 'plot' ? 'backend' : 'canvas';
                console.log(`[VisEditor] Restoring mode from URL hash: ${hash} -> ${mode}`);
                this.switchMode(mode);
                return;
            }

            // Priority 2: Check localStorage
            const savedMode = localStorage.getItem('scitex_vis_active_mode');
            if (savedMode && (savedMode === 'canvas' || savedMode === 'backend')) {
                console.log(`[VisEditor] Restoring saved mode: ${savedMode}`);
                this.switchMode(savedMode);
            } else {
                // Default to canvas mode
                console.log('[VisEditor] No saved mode found, defaulting to canvas');
                this.switchMode('canvas');
            }
        } catch (error) {
            console.error('[VisEditor] Failed to restore mode preference:', error);
            this.switchMode('canvas'); // Fallback to canvas
        }
    }

    private switchMode(mode: string) {
        console.log(`[VisEditor] Switching to ${mode} mode`);

        // Save mode preference to localStorage
        try {
            localStorage.setItem('scitex_vis_active_mode', mode);
            console.log(`[VisEditor] Saved mode preference: ${mode}`);
        } catch (error) {
            console.error('[VisEditor] Failed to save mode preference:', error);
        }

        // Update URL hash
        const hashName = mode === 'backend' ? 'plot' : 'canvas';
        if (window.location.hash !== `#${hashName}`) {
            window.history.replaceState(null, '', `#${hashName}`);
            console.log(`[VisEditor] Updated URL hash to: #${hashName}`);
        }

        // Update button states (CSS handles styling via .active class)
        document.querySelectorAll('.view-switch-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        const activeBtn = document.querySelector(`[data-mode="${mode}"]`) as HTMLElement;
        if (activeBtn) {
            activeBtn.classList.add('active');
        }

        // Show/hide content
        const canvasContent = document.getElementById('canvas-mode-content');
        const backendContent = document.getElementById('backend-mode-content');
        const canvasControls = document.getElementById('canvas-mode-controls');
        const plotTypeButtons = document.getElementById('plot-type-buttons');

        // Switch right panel based on mode
        const canvasPropertiesPanel = document.getElementById('canvas-properties-panel');
        const plotStylesPanel = document.getElementById('plot-styles-panel');

        if (mode === 'canvas') {
            if (canvasContent) canvasContent.style.display = 'block';
            if (backendContent) backendContent.style.display = 'none';
            if (canvasControls) canvasControls.style.display = 'flex';
            if (plotTypeButtons) plotTypeButtons.style.display = 'none';
            if (canvasPropertiesPanel) canvasPropertiesPanel.style.display = 'block';
            if (plotStylesPanel) plotStylesPanel.style.display = 'none';
            this.updateStatus('Canvas Editor mode');
        } else if (mode === 'backend') {
            if (canvasContent) canvasContent.style.display = 'none';
            if (backendContent) backendContent.style.display = 'block';
            if (canvasControls) canvasControls.style.display = 'none';
            if (plotTypeButtons) plotTypeButtons.style.display = 'flex';
            if (canvasPropertiesPanel) canvasPropertiesPanel.style.display = 'none';
            if (plotStylesPanel) plotStylesPanel.style.display = 'block';
            this.updateStatus('Plot Backend mode - Edit JSON and click Render');
            this.setupBackendMode();
        }
    }

    private setupBackendMode() {
        // Set up backend plot renderer event listeners
        const renderBtn = document.getElementById('backend-render-btn');
        const jsonSpec = document.getElementById('backend-json-spec') as HTMLTextAreaElement;
        const resultContainer = document.getElementById('backend-result-container');
        const statusDiv = document.getElementById('backend-status');

        // Example buttons
        document.querySelectorAll('.backend-example-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const example = (e.currentTarget as HTMLElement).dataset.example;
                if (example && jsonSpec) {
                    jsonSpec.value = this.getExampleSpec(example);
                }
            });
        });

        // Plot type wizard buttons (SigmaPlot-style)
        const plotTypeButtons = document.querySelectorAll('.plot-type-btn');
        console.log(`[VisEditor] Found ${plotTypeButtons.length} plot type buttons`);

        plotTypeButtons.forEach(btn => {
            if (!btn.hasAttribute('data-listener-added')) {
                btn.setAttribute('data-listener-added', 'true');
                btn.addEventListener('click', (e) => {
                    const plotType = (e.currentTarget as HTMLElement).dataset.plotType;
                    console.log(`[VisEditor] Plot type button clicked: ${plotType}`);

                    if (plotType && jsonSpec) {
                        // Remove active class from all buttons
                        document.querySelectorAll('.plot-type-btn').forEach(b => b.classList.remove('active'));
                        // Add active class to clicked button
                        (e.currentTarget as HTMLElement).classList.add('active');

                        // Load example spec for the selected plot type
                        jsonSpec.value = this.getPlotTypeTemplate(plotType);
                        this.updateStatus(`${plotType.charAt(0).toUpperCase() + plotType.slice(1)} plot template loaded`);
                        console.log(`[VisEditor] Template loaded for ${plotType}`);

                        // Populate data table with example data
                        this.populateTableFromJSON();
                    } else {
                        console.error('[VisEditor] Missing plotType or jsonSpec element');
                    }
                });
            }
        });

        // File upload for data (CSV/Excel)
        this.setupPlotFileUpload();

        // Form controls synchronization
        this.setupFormControls();

        // Render button
        if (renderBtn && !renderBtn.dataset.listenerAdded) {
            renderBtn.dataset.listenerAdded = 'true';
            renderBtn.addEventListener('click', async () => {
                if (!jsonSpec || !resultContainer || !statusDiv) return;

                try {
                    const spec = JSON.parse(jsonSpec.value);
                    statusDiv.innerHTML = '<span style="color: #6b8fb3;">Rendering...</span>';

                    const response = await fetch('/vis/api/plot/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': this.getCSRFToken(),
                        },
                        body: JSON.stringify(spec),
                    });

                    if (response.ok) {
                        const svgText = await response.text();
                        resultContainer.innerHTML = svgText;
                        statusDiv.innerHTML = '<span style="color: #4a9b7e;">✓ Plot rendered successfully</span>';
                    } else {
                        const error = await response.json();
                        statusDiv.innerHTML = `<span style="color: #ff4444;">✗ Error: ${error.error || 'Unknown error'}</span>`;
                        resultContainer.innerHTML = `<p style="color: var(--text-tertiary);">Rendering failed. Check JSON syntax.</p>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<span style="color: #ff4444;">✗ Invalid JSON: ${(error as Error).message}</span>`;
                    console.error('[Backend] Render error:', error);
                }
            });
        }

        // Setup plot type button dropdown galleries
        this.setupPlotTypeDropdowns();

        // Initialize data table for plot editing
        this.initializeDataTable();
    }

    /**
     * Setup dropdown galleries for plot type buttons
     */
    private async setupPlotTypeDropdowns() {
        try {
            // Load plot templates
            const response = await fetch('/static/vis_app/img/plot_gallery/plot_templates.json');
            if (!response.ok) return;

            const plotData = await response.json();

            // Group plots by base type
            const plotGroups: Record<string, any[]> = {
                line: [],
                scatter: [],
                bar: [],
                histogram: [],
                box: [],
                violin: [],
                heatmap: []
            };

            // Categorize all plots
            Object.entries(plotData.plot_types).forEach(([key, plot]: [string, any]) => {
                // Match plot to group based on name/type
                if (key.includes('line') || key.includes('errorbar') || key.includes('shaded')) {
                    plotGroups.line.push({ key, ...plot });
                } else if (key.includes('scatter')) {
                    plotGroups.scatter.push({ key, ...plot });
                } else if (key.includes('bar') || key.includes('barh')) {
                    plotGroups.bar.push({ key, ...plot });
                } else if (key.includes('hist')) {
                    plotGroups.histogram.push({ key, ...plot });
                } else if (key.includes('box')) {
                    plotGroups.box.push({ key, ...plot });
                } else if (key.includes('violin')) {
                    plotGroups.violin.push({ key, ...plot });
                } else if (key.includes('heatmap') || key.includes('imshow') || key.includes('contour')) {
                    plotGroups.heatmap.push({ key, ...plot });
                }
            });

            // Create dropdown for each plot type button
            const plotButtons = document.querySelectorAll('.plot-type-btn');
            let currentOpenDropdown: HTMLElement | null = null;

            plotButtons.forEach(btn => {
                const plotType = (btn as HTMLElement).dataset.plotType;
                if (!plotType || plotType === 'more') return;

                const plots = plotGroups[plotType];
                if (!plots || plots.length === 0) return;

                // Create dropdown element
                const dropdown = document.createElement('div');
                dropdown.className = 'plot-type-dropdown';
                dropdown.dataset.type = plotType;

                const header = document.createElement('div');
                header.className = 'plot-type-dropdown-header';
                header.textContent = 'Select ' + (btn as HTMLElement).textContent?.trim() + ' Type';

                const grid = document.createElement('div');
                grid.className = 'plot-type-dropdown-grid';

                // Add plot items to grid
                plots.forEach((plot: any) => {
                    const item = document.createElement('div');
                    item.className = 'plot-type-dropdown-item';
                    item.dataset.plotKey = plot.key;

                    const badge = document.createElement('div');
                    badge.className = 'plot-type-dropdown-item-category';
                    badge.textContent = plot.category;

                    const imgContainer = document.createElement('div');
                    imgContainer.className = 'plot-type-dropdown-item-img';

                    const img = document.createElement('img');
                    img.src = '/static/vis_app/img/plot_gallery/' + plot.category + '/' + plot.thumbnail;
                    img.alt = plot.name;
                    // No lazy loading - render sample images immediately

                    const label = document.createElement('div');
                    label.className = 'plot-type-dropdown-item-label';
                    label.textContent = plot.name;

                    imgContainer.appendChild(img);
                    item.appendChild(badge);
                    item.appendChild(imgContainer);
                    item.appendChild(label);

                    // Click handler to select plot
                    item.addEventListener('click', () => {
                        // Update selection
                        grid.querySelectorAll('.plot-type-dropdown-item').forEach(i => i.classList.remove('selected'));
                        item.classList.add('selected');

                        // Set the plot type for rendering
                        console.log('[VisEditor] Selected plot:', plot.key, plot);

                        // Close dropdown after selection
                        setTimeout(() => {
                            dropdown.classList.remove('show');
                            (btn as HTMLElement).classList.remove('has-dropdown-open');
                            currentOpenDropdown = null;
                        }, 200);

                        // TODO: Update plot configuration with selected type
                        this.updateStatus('Selected: ' + plot.name);
                    });

                    grid.appendChild(item);
                });

                dropdown.appendChild(header);
                dropdown.appendChild(grid);
                document.body.appendChild(dropdown);

                // Toggle dropdown on button click
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();

                    // Close any open dropdown
                    if (currentOpenDropdown && currentOpenDropdown !== dropdown) {
                        currentOpenDropdown.classList.remove('show');
                        document.querySelectorAll('.plot-type-btn').forEach(b => b.classList.remove('has-dropdown-open'));
                    }

                    // Toggle this dropdown
                    const isOpen = dropdown.classList.contains('show');
                    dropdown.classList.toggle('show');
                    (btn as HTMLElement).classList.toggle('has-dropdown-open');

                    if (!isOpen) {
                        // Position dropdown below button
                        const rect = (btn as HTMLElement).getBoundingClientRect();
                        const dropdownWidth = 360;
                        const left = rect.left + (rect.width / 2) - (dropdownWidth / 2);
                        const finalLeft = left < 10 ? 10 : (left + dropdownWidth > window.innerWidth - 10 ? window.innerWidth - dropdownWidth - 10 : left);

                        dropdown.style.left = finalLeft + 'px';
                        dropdown.style.top = rect.bottom + 'px';
                        dropdown.style.minWidth = dropdownWidth + 'px';
                        currentOpenDropdown = dropdown;
                    } else {
                        currentOpenDropdown = null;
                    }
                });
            });

            // Close dropdown when clicking outside
            document.addEventListener('click', (e) => {
                if (currentOpenDropdown && !(e.target as HTMLElement).closest('.plot-type-dropdown')) {
                    currentOpenDropdown.classList.remove('show');
                    document.querySelectorAll('.plot-type-btn').forEach(b => b.classList.remove('has-dropdown-open'));
                    currentOpenDropdown = null;
                }
            });

            console.log('[VisEditor] Plot type dropdowns initialized');

        } catch (error) {
            console.error('[VisEditor] Failed to setup plot dropdowns:', error);
        }
    }

    /**
     * Initialize Handsontable for plot data editing
     */
    private initializeDataTable() {
        const container = document.getElementById('data-table-container');
        if (!container || this.dataTable) return;

        // Initialize with empty data
        const data = [
            ['', ''],
            ['', ''],
            ['', ''],
            ['', ''],
            ['', '']
        ];

        // Create Handsontable instance
        this.dataTable = new (window as any).Handsontable(container, {
            data: data,
            rowHeaders: true,
            colHeaders: ['X', 'Y'],
            contextMenu: true,
            manualColumnResize: true,
            manualRowResize: true,
            minSpareRows: 1,
            stretchH: 'all',
            licenseKey: 'non-commercial-and-evaluation',
            afterChange: (changes: any) => {
                if (changes) {
                    this.syncTableToJSON();
                }
            }
        });

        // Set up import CSV button
        const importBtn = document.getElementById('import-csv-btn');
        const fileInput = document.getElementById('csv-file-input') as HTMLInputElement;
        if (importBtn && fileInput) {
            importBtn.addEventListener('click', () => {
                fileInput.click();
            });

            fileInput.addEventListener('change', async (e) => {
                const file = (e.target as HTMLInputElement).files?.[0];
                if (file) {
                    const text = await file.text();
                    this.importCSV(text);
                    fileInput.value = ''; // Reset input
                }
            });
        }

        // Set up paste button
        const pasteBtn = document.getElementById('paste-data-btn');
        if (pasteBtn) {
            pasteBtn.addEventListener('click', async () => {
                try {
                    const text = await navigator.clipboard.readText();
                    this.importCSV(text);
                    this.updateStatus('Data pasted from clipboard');
                } catch (error) {
                    this.updateStatus('Failed to paste from clipboard. Please allow clipboard access.');
                }
            });
        }

        // Set up clear button
        const clearBtn = document.getElementById('clear-table-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.dataTable.loadData([['', ''], ['', ''], ['', ''], ['', ''], ['', '']]);
                this.updateStatus('Table cleared');
            });
        }

        console.log('[VisEditor] Data table initialized');
    }

    /**
     * Import CSV data into the table
     */
    private importCSV(csvText: string) {
        if (!this.dataTable) return;

        const lines = csvText.trim().split('\n');
        const data: any[][] = [];

        for (const line of lines) {
            // Split by comma or tab
            const values = line.split(/,|\t/);
            data.push(values);
        }

        // Check if first row is header (contains non-numeric values)
        const firstRow = data[0];
        const hasHeaders = firstRow.some((val: string) => isNaN(parseFloat(val)));

        if (hasHeaders) {
            // Set column headers
            this.dataTable.updateSettings({
                colHeaders: firstRow
            });
            // Load data without headers
            this.dataTable.loadData(data.slice(1));
        } else {
            // Load all data including first row
            this.dataTable.loadData(data);
        }

        this.updateStatus(`Imported ${data.length} rows`);
        this.syncTableToJSON();
    }

    /**
     * Sync table data to JSON specification
     */
    private syncTableToJSON() {
        if (!this.dataTable) return;

        const jsonSpec = document.getElementById('backend-json-spec') as HTMLTextAreaElement;
        if (!jsonSpec) return;

        try {
            const tableData = this.dataTable.getData();
            const spec = JSON.parse(jsonSpec.value);

            // Convert table data to array format
            const plotData: number[][] = [];
            for (const row of tableData) {
                // Skip empty rows
                if (row[0] === '' && row[1] === '') continue;

                const x = parseFloat(row[0]);
                const y = parseFloat(row[1]);

                if (!isNaN(x) && !isNaN(y)) {
                    plotData.push([x, y]);
                }
            }

            // Update plot data in spec
            if (spec.plot) {
                spec.plot.data = plotData;
                jsonSpec.value = JSON.stringify(spec, null, 2);
            }
        } catch (error) {
            console.error('[VisEditor] Failed to sync table to JSON:', error);
        }
    }

    /**
     * Populate table from JSON specification data
     */
    private populateTableFromJSON() {
        if (!this.dataTable) return;

        const jsonSpec = document.getElementById('backend-json-spec') as HTMLTextAreaElement;
        if (!jsonSpec) return;

        try {
            const spec = JSON.parse(jsonSpec.value);

            if (spec.plot && spec.plot.data && Array.isArray(spec.plot.data)) {
                const data = spec.plot.data;
                const tableData: any[][] = [];

                // Convert plot data to table format
                for (const point of data) {
                    if (Array.isArray(point) && point.length >= 2) {
                        tableData.push([point[0].toString(), point[1].toString()]);
                    }
                }

                // Load data into table (disable afterChange temporarily to avoid circular updates)
                this.dataTable.updateSettings({ afterChange: null });
                this.dataTable.loadData(tableData);
                this.dataTable.updateSettings({
                    afterChange: (changes: any) => {
                        if (changes) {
                            this.syncTableToJSON();
                        }
                    }
                });

                console.log(`[VisEditor] Loaded ${tableData.length} data points into table`);
            }
        } catch (error) {
            console.error('[VisEditor] Failed to populate table from JSON:', error);
        }
    }

    private getExampleSpec(example: string): string {
        const examples: { [key: string]: any } = {
            line: {
                figure: { width_mm: 35, height_mm: 24.5, dpi: 300 },
                style: {
                    tick_length_mm: 0.8,
                    tick_thickness_mm: 0.2,
                    axis_thickness_mm: 0.2,
                    trace_thickness_mm: 0.12,
                    axis_font_size_pt: 8,
                    tick_font_size_pt: 7,
                    title_font_size_pt: 8
                },
                plot: {
                    kind: "line",
                    data: [[0, 0], [1, 1], [2, 4], [3, 9], [4, 16]],
                    color: "blue",
                    xlabel: "X axis",
                    ylabel: "Y axis",
                    title: "Line Plot Example"
                }
            },
            scatter: {
                figure: { width_mm: 35, height_mm: 24.5, dpi: 300 },
                style: {
                    tick_length_mm: 0.8,
                    tick_thickness_mm: 0.2,
                    axis_thickness_mm: 0.2,
                    trace_thickness_mm: 0.12,
                    axis_font_size_pt: 8,
                    tick_font_size_pt: 7,
                    title_font_size_pt: 8
                },
                plot: {
                    kind: "scatter",
                    data: [[1, 2], [2, 3], [3, 1], [4, 4], [5, 3.5]],
                    color: "red",
                    xlabel: "X values",
                    ylabel: "Y values",
                    title: "Scatter Plot Example"
                }
            },
            bar: {
                figure: { width_mm: 35, height_mm: 24.5, dpi: 300 },
                style: {
                    tick_length_mm: 0.8,
                    tick_thickness_mm: 0.2,
                    axis_thickness_mm: 0.2,
                    trace_thickness_mm: 0.12,
                    axis_font_size_pt: 8,
                    tick_font_size_pt: 7,
                    title_font_size_pt: 8
                },
                plot: {
                    kind: "bar",
                    data: [[0, 5], [1, 7], [2, 3], [3, 8], [4, 6]],
                    color: "green",
                    xlabel: "Categories",
                    ylabel: "Values",
                    title: "Bar Plot Example"
                }
            },
            multipanel2: {
                figure: { width_mm: 70, height_mm: 24.5, dpi: 300 },
                style: {
                    tick_length_mm: 0.8,
                    tick_thickness_mm: 0.2,
                    axis_thickness_mm: 0.2,
                    trace_thickness_mm: 0.12,
                    axis_font_size_pt: 8,
                    tick_font_size_pt: 7,
                    title_font_size_pt: 8
                },
                panels: [
                    {
                        id: "A",
                        x_mm: 0,
                        y_mm: 0,
                        width_mm: 35,
                        height_mm: 24.5,
                        plot: {
                            kind: "line",
                            data: [[0, 0], [1, 1], [2, 4], [3, 9]],
                            color: "blue",
                            xlabel: "X",
                            ylabel: "Y",
                            title: "Panel A"
                        }
                    },
                    {
                        id: "B",
                        x_mm: 35,
                        y_mm: 0,
                        width_mm: 35,
                        height_mm: 24.5,
                        plot: {
                            kind: "scatter",
                            data: [[1, 2], [2, 3], [3, 1], [4, 4]],
                            color: "red",
                            xlabel: "X",
                            ylabel: "Y",
                            title: "Panel B"
                        }
                    }
                ]
            },
            multipanel4: {
                figure: { width_mm: 70, height_mm: 49, dpi: 300 },
                style: {
                    tick_length_mm: 0.8,
                    tick_thickness_mm: 0.2,
                    axis_thickness_mm: 0.2,
                    trace_thickness_mm: 0.12,
                    axis_font_size_pt: 8,
                    tick_font_size_pt: 7,
                    title_font_size_pt: 8
                },
                panels: [
                    {
                        id: "A",
                        x_mm: 0,
                        y_mm: 24.5,
                        width_mm: 35,
                        height_mm: 24.5,
                        plot: {
                            kind: "line",
                            data: [[0, 0], [1, 1], [2, 4]],
                            color: "blue",
                            xlabel: "X",
                            ylabel: "Y",
                            title: "Panel A"
                        }
                    },
                    {
                        id: "B",
                        x_mm: 35,
                        y_mm: 24.5,
                        width_mm: 35,
                        height_mm: 24.5,
                        plot: {
                            kind: "scatter",
                            data: [[1, 2], [2, 3], [3, 1]],
                            color: "red",
                            xlabel: "X",
                            ylabel: "Y",
                            title: "Panel B"
                        }
                    },
                    {
                        id: "C",
                        x_mm: 0,
                        y_mm: 0,
                        width_mm: 35,
                        height_mm: 24.5,
                        plot: {
                            kind: "bar",
                            data: [[0, 5], [1, 7], [2, 3]],
                            color: "green",
                            xlabel: "X",
                            ylabel: "Y",
                            title: "Panel C"
                        }
                    },
                    {
                        id: "D",
                        x_mm: 35,
                        y_mm: 0,
                        width_mm: 35,
                        height_mm: 24.5,
                        plot: {
                            kind: "line",
                            data: [[0, 3], [1, 5], [2, 2]],
                            color: "purple",
                            xlabel: "X",
                            ylabel: "Y",
                            title: "Panel D"
                        }
                    }
                ]
            },
            barh: {
                figure: { width_mm: 35, height_mm: 24.5, dpi: 300 },
                style: {
                    tick_length_mm: 0.8,
                    tick_thickness_mm: 0.2,
                    axis_thickness_mm: 0.2,
                    trace_thickness_mm: 0.12,
                    axis_font_size_pt: 8,
                    tick_font_size_pt: 7,
                    title_font_size_pt: 8
                },
                plot: {
                    kind: "barh",
                    data: [[0, 5], [1, 7], [2, 3], [3, 8], [4, 6]],
                    color: "purple",
                    xlabel: "Values",
                    ylabel: "Categories",
                    title: "Horizontal Bar Plot"
                }
            },
            errorbar: {
                figure: { width_mm: 35, height_mm: 24.5, dpi: 300 },
                style: {
                    tick_length_mm: 0.8,
                    tick_thickness_mm: 0.2,
                    axis_thickness_mm: 0.2,
                    trace_thickness_mm: 0.12,
                    axis_font_size_pt: 8,
                    tick_font_size_pt: 7,
                    title_font_size_pt: 8
                },
                plot: {
                    kind: "errorbar",
                    csv_path: "/path/to/errorbar_test.csv",
                    x_column: "x",
                    y_column: "y",
                    yerr_column: "yerr",
                    color: "orange",
                    xlabel: "X values",
                    ylabel: "Y values ± error",
                    title: "Error Bar Plot"
                }
            },
            fill_between: {
                figure: { width_mm: 35, height_mm: 24.5, dpi: 300 },
                style: {
                    tick_length_mm: 0.8,
                    tick_thickness_mm: 0.2,
                    axis_thickness_mm: 0.2,
                    trace_thickness_mm: 0.12,
                    axis_font_size_pt: 8,
                    tick_font_size_pt: 7,
                    title_font_size_pt: 8
                },
                plot: {
                    kind: "fill_between",
                    csv_path: "/path/to/fill_between_test.csv",
                    x_column: "x",
                    y_column: "y",
                    y_lower_column: "y_lower",
                    y_upper_column: "y_upper",
                    color: "blue",
                    xlabel: "Time",
                    ylabel: "Signal ± CI",
                    title: "Confidence Interval"
                }
            },
            hist: {
                figure: { width_mm: 35, height_mm: 24.5, dpi: 300 },
                style: {
                    tick_length_mm: 0.8,
                    tick_thickness_mm: 0.2,
                    axis_thickness_mm: 0.2,
                    trace_thickness_mm: 0.12,
                    axis_font_size_pt: 8,
                    tick_font_size_pt: 7,
                    title_font_size_pt: 8
                },
                plot: {
                    kind: "hist",
                    csv_path: "/path/to/hist_test.csv",
                    data_column: "value",
                    bins: 20,
                    color: "skyblue",
                    xlabel: "Value",
                    ylabel: "Frequency",
                    title: "Histogram"
                }
            },
            boxplot: {
                figure: { width_mm: 35, height_mm: 24.5, dpi: 300 },
                style: {
                    tick_length_mm: 0.8,
                    tick_thickness_mm: 0.2,
                    axis_thickness_mm: 0.2,
                    trace_thickness_mm: 0.12,
                    axis_font_size_pt: 8,
                    tick_font_size_pt: 7,
                    title_font_size_pt: 8
                },
                plot: {
                    kind: "boxplot",
                    csv_path: "/path/to/boxplot_test.csv",
                    value_column: "value",
                    group_column: "group",
                    xlabel: "Groups",
                    ylabel: "Values",
                    title: "Box Plot"
                }
            },
            violin: {
                figure: { width_mm: 35, height_mm: 24.5, dpi: 300 },
                style: {
                    tick_length_mm: 0.8,
                    tick_thickness_mm: 0.2,
                    axis_thickness_mm: 0.2,
                    trace_thickness_mm: 0.12,
                    axis_font_size_pt: 8,
                    tick_font_size_pt: 7,
                    title_font_size_pt: 8
                },
                plot: {
                    kind: "violin",
                    csv_path: "/path/to/violin_test.csv",
                    value_column: "value",
                    group_column: "group",
                    xlabel: "Groups",
                    ylabel: "Values",
                    title: "Violin Plot"
                }
            },
            raster: {
                figure: { width_mm: 35, height_mm: 24.5, dpi: 300 },
                style: {
                    tick_length_mm: 0.8,
                    tick_thickness_mm: 0.2,
                    axis_thickness_mm: 0.2,
                    trace_thickness_mm: 0.12,
                    axis_font_size_pt: 8,
                    tick_font_size_pt: 7,
                    title_font_size_pt: 8
                },
                plot: {
                    kind: "raster",
                    csv_path: "/path/to/plot_raster_test.csv",
                    time_column: "time",
                    trial_column: "trial",
                    color: "black",
                    xlabel: "Time (s)",
                    ylabel: "Trial",
                    title: "Raster Plot"
                }
            },
        };

        return JSON.stringify(examples[example] || examples.line, null, 2);
    }

    private getPlotTypeTemplate(plotType: string): string {
        // Map plot type buttons to example templates
        const typeToExample: { [key: string]: string } = {
            'line': 'line',
            'scatter': 'scatter',
            'bar': 'bar',
            'heatmap': 'heatmap',  // Will create this template
            'box': 'boxplot',
            'violin': 'violin',
            'histogram': 'hist',
        };

        // If "more" button clicked, return a helpful template
        if (plotType === 'more') {
            return JSON.stringify({
                figure: { width_mm: 35, height_mm: 24.5, dpi: 300 },
                style: {
                    tick_length_mm: 0.8,
                    tick_thickness_mm: 0.2,
                    axis_thickness_mm: 0.2,
                    trace_thickness_mm: 0.12,
                    axis_font_size_pt: 8,
                    tick_font_size_pt: 7,
                    title_font_size_pt: 8
                },
                plot: {
                    kind: "line",
                    data: [[0, 0], [1, 1], [2, 2]],
                    color: "blue",
                    xlabel: "X axis",
                    ylabel: "Y axis",
                    title: "Change 'kind' to: errorbar, fill_between, barh, or raster"
                }
            }, null, 2);
        }

        // Heatmap template (not in examples yet)
        if (plotType === 'heatmap') {
            return JSON.stringify({
                figure: { width_mm: 35, height_mm: 24.5, dpi: 300 },
                style: {
                    tick_length_mm: 0.8,
                    tick_thickness_mm: 0.2,
                    axis_thickness_mm: 0.2,
                    trace_thickness_mm: 0.12,
                    axis_font_size_pt: 8,
                    tick_font_size_pt: 7,
                    title_font_size_pt: 8
                },
                plot: {
                    kind: "heatmap",
                    csv_path: "/path/to/heatmap_data.csv",
                    xlabel: "X axis",
                    ylabel: "Y axis",
                    title: "Heatmap",
                    cmap: "viridis"
                }
            }, null, 2);
        }

        // Use existing examples for other plot types
        const exampleKey = typeToExample[plotType] || 'line';
        return this.getExampleSpec(exampleKey);
    }

    private setupPlotFileUpload() {
        const dropArea = document.getElementById('plot-drop-area');
        const fileInput = document.getElementById('plot-data-file-input') as HTMLInputElement;
        const browseBtn = document.getElementById('plot-browse-btn');
        const dropContent = dropArea?.querySelector('.plot-drop-content');
        const uploadedFilesDiv = document.getElementById('plot-uploaded-files');

        if (!dropArea || !fileInput || !browseBtn) return;

        // Store uploaded files
        const uploadedFiles: File[] = [];

        // Browse button click
        browseBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            e.preventDefault();
            fileInput.click();
        });

        // Click on drop area (but not on the browse button)
        dropArea.addEventListener('click', (e) => {
            // Don't trigger if clicking on the browse button or its children
            if (e.target === browseBtn || browseBtn.contains(e.target as Node)) {
                return;
            }
            fileInput.click();
        });

        // Drag & drop events
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        dropArea.addEventListener('dragenter', () => {
            dropArea.classList.add('drag-over');
        });

        dropArea.addEventListener('dragleave', (e) => {
            if (e.target === dropArea) {
                dropArea.classList.remove('drag-over');
            }
        });

        dropArea.addEventListener('drop', (e) => {
            dropArea.classList.remove('drag-over');
            const dt = (e as DragEvent).dataTransfer;
            if (dt?.files) {
                handleFiles(dt.files);
            }
        });

        // File input change
        fileInput.addEventListener('change', () => {
            if (fileInput.files) {
                handleFiles(fileInput.files);
            }
        });

        const handleFiles = async (files: FileList) => {
            for (const file of Array.from(files)) {
                // Validate file type
                const validTypes = ['.csv', '.xlsx', '.xls'];
                const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();

                if (validTypes.indexOf(fileExt) === -1) {
                    this.updateStatus(`Invalid file type: ${file.name}. Only CSV and Excel files are supported.`);
                    continue;
                }

                // Check if file already uploaded
                if (uploadedFiles.some(f => f.name === file.name && f.size === file.size)) {
                    this.updateStatus(`File already uploaded: ${file.name}`);
                    continue;
                }

                // Upload file to backend
                try {
                    this.updateStatus(`Uploading ${file.name}...`);
                    const formData = new FormData();
                    formData.append('file', file);

                    const response = await fetch('/vis/api/upload-plot-data/', {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': this.getCSRFToken(),
                        },
                        body: formData
                    });

                    if (!response.ok) {
                        const error = await response.json();
                        this.updateStatus(`Upload failed: ${error.error}`);
                        continue;
                    }

                    const result = await response.json();
                    (file as any).uploadedPath = result.file_path;

                    uploadedFiles.push(file);
                    this.displayUploadedFile(file, uploadedFiles, uploadedFilesDiv, dropContent);
                    this.updateStatus(`✓ Uploaded: ${file.name}`);
                } catch (error) {
                    this.updateStatus(`Upload error: ${(error as Error).message}`);
                    console.error('[Plot Upload] Error:', error);
                }
            }
        };
    }

    private displayUploadedFile(file: File, uploadedFiles: File[], uploadedFilesDiv: HTMLElement | null, dropContent: Element | null | undefined) {
        if (!uploadedFilesDiv) return;

        // Show uploaded files section
        uploadedFilesDiv.style.display = 'block';
        if (dropContent) {
            (dropContent as HTMLElement).style.display = 'none';
        }

        const fileItem = document.createElement('div');
        fileItem.className = 'plot-file-item';

        const fileSize = (file.size / 1024).toFixed(1) + ' KB';
        const fileIcon = file.name.endsWith('.csv') ? 'fa-file-csv' : 'fa-file-excel';

        fileItem.innerHTML = `
            <div class="plot-file-info">
                <i class="fas ${fileIcon} plot-file-icon"></i>
                <span class="plot-file-name" title="${file.name}">${file.name}</span>
                <span class="plot-file-size">${fileSize}</span>
            </div>
            <div style="display: flex; gap: 4px;">
                <button class="plot-file-use" title="Use this file in plot" style="padding: 4px 8px; border: 1px solid var(--border-color); border-radius: 3px; background: var(--button-background); color: var(--text-primary); cursor: pointer; font-size: 11px;">
                    Use
                </button>
                <button class="plot-file-remove" title="Remove file" style="padding: 4px 8px; border: 1px solid var(--border-color); border-radius: 3px; background: var(--button-background); color: var(--text-primary); cursor: pointer;">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // Use button handler
        const useBtn = fileItem.querySelector('.plot-file-use');
        useBtn?.addEventListener('click', () => {
            const jsonSpec = document.getElementById('backend-json-spec') as HTMLTextAreaElement;
            if (!jsonSpec) return;

            try {
                const spec = JSON.parse(jsonSpec.value);
                const filePath = (file as any).uploadedPath;

                if (spec.plot) {
                    // Single plot - update csv_path
                    spec.plot.csv_path = filePath;
                    delete spec.plot.data; // Remove inline data if present
                } else if (spec.panels && spec.panels.length > 0) {
                    // Multi-panel - update first panel's csv_path
                    spec.panels[0].plot.csv_path = filePath;
                    delete spec.panels[0].plot.data;
                }

                jsonSpec.value = JSON.stringify(spec, null, 2);
                this.updateStatus(`✓ Using ${file.name} in plot specification`);

                // Read and load CSV into data table
                const reader = new FileReader();
                reader.onload = (e) => {
                    const csvText = e.target?.result as string;
                    if (csvText && this.dataTable) {
                        this.importCSV(csvText);
                    }
                };
                reader.readAsText(file);
            } catch (error) {
                this.updateStatus(`Error updating spec: ${(error as Error).message}`);
            }
        });

        // Remove button handler
        const removeBtn = fileItem.querySelector('.plot-file-remove');
        removeBtn?.addEventListener('click', () => {
            const index = uploadedFiles.findIndex(f => f.name === file.name && f.size === file.size);
            if (index > -1) {
                uploadedFiles.splice(index, 1);
            }
            fileItem.remove();

            // If no files left, show drop content again
            if (uploadedFiles.length === 0) {
                uploadedFilesDiv.style.display = 'none';
                if (dropContent) {
                    (dropContent as HTMLElement).style.display = 'block';
                }
            }
        });

        uploadedFilesDiv.appendChild(fileItem);
    }

    private setupFormControls() {
        const jsonSpec = document.getElementById('backend-json-spec') as HTMLTextAreaElement;
        const showJsonBtn = document.getElementById('backend-show-json-btn');
        const formControls = document.getElementById('backend-form-controls') as HTMLElement;

        if (!jsonSpec || !showJsonBtn || !formControls) return;

        // Show/Hide JSON toggle
        let showingJson = false;
        showJsonBtn.addEventListener('click', () => {
            showingJson = !showingJson;
            if (showingJson) {
                jsonSpec.style.display = 'block';
                formControls.style.display = 'none';
                showJsonBtn.textContent = 'Hide JSON';
                showJsonBtn.classList.add('active');
            } else {
                jsonSpec.style.display = 'none';
                formControls.style.display = 'block';
                showJsonBtn.textContent = 'Show JSON';
                showJsonBtn.classList.remove('active');
            }
        });

        // Initialize form values from JSON
        const initializeFormFromJSON = () => {
            try {
                const spec = JSON.parse(jsonSpec.value);

                // Figure settings
                if (spec.figure) {
                    this.setInputValue('fig-width', spec.figure.width_mm, 35);
                    this.setInputValue('fig-height', spec.figure.height_mm, 24.5);
                    this.setInputValue('fig-dpi', spec.figure.dpi, 300);
                }

                // Style settings
                if (spec.style) {
                    this.setInputValue('style-tick-length', spec.style.tick_length_mm, 0.8);
                    this.setInputValue('style-tick-thickness', spec.style.tick_thickness_mm, 0.2);
                    this.setInputValue('style-axis-thickness', spec.style.axis_thickness_mm, 0.2);
                    this.setInputValue('style-trace-thickness', spec.style.trace_thickness_mm, 0.12);
                    this.setInputValue('style-axis-font', spec.style.axis_font_size_pt, 8);
                    this.setInputValue('style-tick-font', spec.style.tick_font_size_pt, 7);
                    this.setInputValue('style-title-font', spec.style.title_font_size_pt, 8);
                }

                // Plot settings (only if single plot, not panels)
                if (spec.plot) {
                    this.setSelectValue('plot-kind', spec.plot.kind);
                    this.setTextValue('plot-color', spec.plot.color);
                    this.setTextValue('plot-xlabel', spec.plot.xlabel);
                    this.setTextValue('plot-ylabel', spec.plot.ylabel);
                    this.setTextValue('plot-title', spec.plot.title);
                }
            } catch (error) {
                console.error('[FormControls] Failed to parse JSON:', error);
            }
        };

        // Update JSON from form controls
        const updateJSONFromForm = () => {
            try {
                const spec = JSON.parse(jsonSpec.value);

                // Update figure settings
                if (!spec.figure) spec.figure = {};
                spec.figure.width_mm = parseFloat((document.getElementById('fig-width') as HTMLInputElement).value);
                spec.figure.height_mm = parseFloat((document.getElementById('fig-height') as HTMLInputElement).value);
                spec.figure.dpi = parseInt((document.getElementById('fig-dpi') as HTMLInputElement).value);

                // Update style settings
                if (!spec.style) spec.style = {};
                spec.style.tick_length_mm = parseFloat((document.getElementById('style-tick-length') as HTMLInputElement).value);
                spec.style.tick_thickness_mm = parseFloat((document.getElementById('style-tick-thickness') as HTMLInputElement).value);
                spec.style.axis_thickness_mm = parseFloat((document.getElementById('style-axis-thickness') as HTMLInputElement).value);
                spec.style.trace_thickness_mm = parseFloat((document.getElementById('style-trace-thickness') as HTMLInputElement).value);
                spec.style.axis_font_size_pt = parseFloat((document.getElementById('style-axis-font') as HTMLInputElement).value);
                spec.style.tick_font_size_pt = parseFloat((document.getElementById('style-tick-font') as HTMLInputElement).value);
                spec.style.title_font_size_pt = parseFloat((document.getElementById('style-title-font') as HTMLInputElement).value);

                // Update plot settings (only if single plot)
                if (spec.plot) {
                    spec.plot.kind = (document.getElementById('plot-kind') as HTMLSelectElement).value;
                    spec.plot.color = (document.getElementById('plot-color') as HTMLInputElement).value;
                    spec.plot.xlabel = (document.getElementById('plot-xlabel') as HTMLInputElement).value;
                    spec.plot.ylabel = (document.getElementById('plot-ylabel') as HTMLInputElement).value;
                    spec.plot.title = (document.getElementById('plot-title') as HTMLInputElement).value;
                }

                jsonSpec.value = JSON.stringify(spec, null, 2);
            } catch (error) {
                console.error('[FormControls] Failed to update JSON:', error);
            }
        };

        // Add event listeners to all form controls
        const addFormListeners = () => {
            // Range sliders with value display
            const sliders = [
                'fig-width', 'fig-height', 'fig-dpi',
                'style-tick-length', 'style-tick-thickness', 'style-axis-thickness',
                'style-trace-thickness', 'style-axis-font', 'style-tick-font', 'style-title-font'
            ];

            sliders.forEach(id => {
                const slider = document.getElementById(id) as HTMLInputElement;
                const valueSpan = document.getElementById(`${id}-val`);

                if (slider && valueSpan) {
                    slider.addEventListener('input', () => {
                        valueSpan.textContent = slider.value;
                        updateJSONFromForm();
                    });
                }
            });

            // Text inputs and select
            const textInputs = ['plot-color', 'plot-xlabel', 'plot-ylabel', 'plot-title'];
            textInputs.forEach(id => {
                const input = document.getElementById(id) as HTMLInputElement;
                if (input) {
                    input.addEventListener('input', updateJSONFromForm);
                }
            });

            const plotKind = document.getElementById('plot-kind') as HTMLSelectElement;
            if (plotKind) {
                plotKind.addEventListener('change', updateJSONFromForm);
            }
        };

        // Update visual preview
        const updateStylePreview = () => {
            // Update tick thickness
            const tickThickness = parseFloat((document.getElementById('style-tick-thickness-main') as HTMLInputElement)?.value || '0.2');
            document.querySelectorAll('#preview-y-ticks line, #preview-x-ticks line').forEach(line => {
                (line as SVGLineElement).setAttribute('stroke-width', (tickThickness * 7.5).toString());
            });

            // Update tick length
            const tickLength = parseFloat((document.getElementById('style-tick-length-main') as HTMLInputElement)?.value || '0.8');
            const tickLengthPx = tickLength * 6;
            document.getElementById('preview-tick-y1')?.setAttribute('x2', (70 - tickLengthPx).toString());
            document.getElementById('preview-tick-y2')?.setAttribute('x2', (70 - tickLengthPx).toString());
            document.getElementById('preview-tick-x1')?.setAttribute('y2', (200 + tickLengthPx).toString());
            document.getElementById('preview-tick-x2')?.setAttribute('y2', (200 + tickLengthPx).toString());
            document.getElementById('preview-tick-x3')?.setAttribute('y2', (200 + tickLengthPx).toString());

            // Update axis thickness
            const axisThickness = parseFloat((document.getElementById('style-axis-thickness-main') as HTMLInputElement)?.value || '0.2');
            document.getElementById('preview-y-axis')?.setAttribute('stroke-width', (axisThickness * 10).toString());
            document.getElementById('preview-x-axis')?.setAttribute('stroke-width', (axisThickness * 10).toString());

            // Update line thickness
            const traceThickness = parseFloat((document.getElementById('style-trace-thickness-main') as HTMLInputElement)?.value || '0.12');
            document.getElementById('preview-line')?.setAttribute('stroke-width', (traceThickness * 16.67).toString());

            // Update title font size
            const titleFontSize = parseFloat((document.getElementById('style-title-font-main') as HTMLInputElement)?.value || '8');
            document.getElementById('preview-title')?.setAttribute('font-size', (titleFontSize * 1.75).toString());

            // Update axis label font size
            const axisFontSize = parseFloat((document.getElementById('style-axis-font-main') as HTMLInputElement)?.value || '8');
            document.getElementById('preview-xlabel')?.setAttribute('font-size', (axisFontSize * 1.5).toString());
            document.getElementById('preview-ylabel')?.setAttribute('font-size', (axisFontSize * 1.5).toString());

            // Update tick label font size
            const tickFontSize = parseFloat((document.getElementById('style-tick-font-main') as HTMLInputElement)?.value || '7');
            document.querySelectorAll('.clickable-element[data-control="style-tick-font-main"] text').forEach(text => {
                (text as SVGTextElement).setAttribute('font-size', (tickFontSize * 1.57).toString());
            });
        };

        // Setup reset buttons
        const setupResetButtons = () => {
            document.querySelectorAll('.setting-reset-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const target = (btn as HTMLElement).dataset.target;
                    if (!target) return;

                    const input = document.getElementById(target) as HTMLInputElement;
                    const valueSpan = document.getElementById(`${target}-val`);

                    if (input) {
                        const defaultValue = input.dataset.default;
                        if (defaultValue) {
                            input.value = defaultValue;
                            if (valueSpan) {
                                valueSpan.textContent = defaultValue;
                            }
                            // Trigger input event to update JSON and preview
                            input.dispatchEvent(new Event('input'));
                            updateStylePreview();
                            this.updateStatus(`Reset ${target} to default`);
                        }
                    }
                });
            });
        };

        // Setup preview update listeners for main panel inputs
        const setupPreviewListeners = () => {
            const mainPanelInputs = [
                'style-tick-length-main', 'style-tick-thickness-main',
                'style-axis-thickness-main', 'style-trace-thickness-main',
                'style-axis-font-main', 'style-tick-font-main', 'style-title-font-main'
            ];

            mainPanelInputs.forEach(id => {
                const input = document.getElementById(id) as HTMLInputElement;

                if (input) {
                    // Handle number inputs
                    input.addEventListener('input', () => {
                        updateStylePreview();
                    });
                    input.addEventListener('change', () => {
                        updateStylePreview();
                    });
                }
            });

            // Setup clickable preview elements
            document.querySelectorAll('.clickable-element').forEach(element => {
                element.addEventListener('click', (e) => {
                    e.preventDefault();
                    const controlIds = (element as SVGElement).dataset.control;
                    if (controlIds) {
                        const ids = controlIds.split(',');
                        const firstInput = document.getElementById(ids[0]) as HTMLInputElement;
                        if (firstInput) {
                            firstInput.focus();
                            firstInput.select();

                            // Add temporary highlight to the control container
                            const container = firstInput.closest('.inline-control') as HTMLElement;
                            if (container) {
                                container.style.backgroundColor = 'rgba(31, 111, 235, 0.15)';
                                container.style.borderRadius = '4px';
                                setTimeout(() => {
                                    container.style.backgroundColor = '';
                                }, 800);
                            }
                        }
                    }
                });
            });

            // Sync inline width/height controls with range sliders
            const widthInline = document.getElementById('fig-width-inline') as HTMLInputElement;
            const widthRange = document.getElementById('fig-width-right') as HTMLInputElement;
            const heightInline = document.getElementById('fig-height-inline') as HTMLInputElement;
            const heightRange = document.getElementById('fig-height-right') as HTMLInputElement;

            if (widthInline && widthRange) {
                widthInline.addEventListener('input', () => {
                    widthRange.value = widthInline.value;
                    const valueSpan = document.getElementById('fig-width-right-val');
                    if (valueSpan) valueSpan.textContent = widthInline.value;
                    updateStylePreview();
                });
                widthRange.addEventListener('input', () => {
                    widthInline.value = widthRange.value;
                });
            }

            if (heightInline && heightRange) {
                heightInline.addEventListener('input', () => {
                    heightRange.value = heightInline.value;
                    const valueSpan = document.getElementById('fig-height-right-val');
                    if (valueSpan) valueSpan.textContent = heightInline.value;
                    updateStylePreview();
                });
                heightRange.addEventListener('input', () => {
                    heightInline.value = heightRange.value;
                });
            }
        };

        // Initialize
        initializeFormFromJSON();
        addFormListeners();
        setupResetButtons();
        setupPreviewListeners();
        updateStylePreview(); // Initial preview update

        // Re-initialize when example buttons are clicked
        document.querySelectorAll('.backend-example-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                setTimeout(() => {
                    initializeFormFromJSON();
                    updateStylePreview();
                }, 100);
            });
        });
    }

    private setInputValue(id: string, value: any, defaultValue: number) {
        const input = document.getElementById(id) as HTMLInputElement;
        const valueSpan = document.getElementById(`${id}-val`);
        if (input) {
            input.value = value !== undefined ? value.toString() : defaultValue.toString();
            if (valueSpan) {
                valueSpan.textContent = input.value;
            }
        }
    }

    private setSelectValue(id: string, value: any) {
        const select = document.getElementById(id) as HTMLSelectElement;
        if (select && value) {
            select.value = value;
        }
    }

    private setTextValue(id: string, value: any) {
        const input = document.getElementById(id) as HTMLInputElement;
        if (input && value) {
            input.value = value;
        }
    }


    // ========================================================================
    // Version Comparison (Original | Edited Cards)
    // ========================================================================

    private async switchComparisonMode() {
        if (!this.canvas) return;

        console.log(`[VisEditor] Switching to ${this.comparisonMode} mode`);

        switch (this.comparisonMode) {
            case 'edited':
                await this.showEditedView();
                break;
            case 'original':
                await this.showOriginalView();
                break;
            case 'split':
                await this.showSplitView();
                break;
        }
    }

    private async showEditedView() {
        // Save current state as edited
        if (this.canvas) {
            this.editedCanvasState = this.canvas.toJSON(['id', 'panelId', 'filename']);
        }

        // Show single canvas with edited version
        const canvasContainer = document.querySelector('.vis-canvas-container') as HTMLElement;
        if (canvasContainer) {
            canvasContainer.style.display = 'block';
            canvasContainer.style.width = '100%';
        }

        // Hide original canvas if it exists
        const originalContainer = document.getElementById('original-canvas-container');
        if (originalContainer) {
            originalContainer.style.display = 'none';
        }

        // Restore edited state
        if (this.editedCanvasState && this.canvas) {
            this.canvas.loadFromJSON(this.editedCanvasState, () => {
                this.canvas!.renderAll();

                // Restore grid if enabled
                if (this.gridEnabled) {
                    this.drawGrid();
                }
            });
        }

        this.updateStatus('Showing edited version');
    }

    private async showOriginalView() {
        if (!this.canvas) return;

        // Load original version from server
        if (!this.originalCanvasState) {
            await this.loadOriginalVersion();
        }

        if (!this.originalCanvasState) {
            this.updateStatus('No original version found. Save one first.');
            return;
        }

        // Show single canvas with original version
        const canvasContainer = document.querySelector('.vis-canvas-container') as HTMLElement;
        if (canvasContainer) {
            canvasContainer.style.display = 'block';
            canvasContainer.style.width = '100%';
        }

        // Load original state
        this.canvas.loadFromJSON(this.originalCanvasState, () => {
            this.canvas!.renderAll();

            // Restore grid if enabled
            if (this.gridEnabled) {
                this.drawGrid();
            }

            this.updateStatus('Showing original version (read-only)');
        });
    }

    private async showSplitView() {
        if (!this.canvas) return;

        // Load original version if not loaded
        if (!this.originalCanvasState) {
            await this.loadOriginalVersion();
        }

        if (!this.originalCanvasState) {
            this.updateStatus('No original version found. Save one first.');
            return;
        }

        // Save current edited state
        this.editedCanvasState = this.canvas.toJSON(['id', 'panelId', 'filename']);

        // Create split view layout
        const canvasWrapper = document.querySelector('.vis-canvas-wrapper') as HTMLElement;
        if (!canvasWrapper) return;

        // Resize main canvas container for split view (50% width)
        const canvasContainer = document.querySelector('.vis-canvas-container') as HTMLElement;
        if (canvasContainer) {
            canvasContainer.style.width = '49%';
            canvasContainer.style.display = 'inline-block';
        }

        // Create or show original canvas container
        let originalContainer = document.getElementById('original-canvas-container') as HTMLElement;
        if (!originalContainer) {
            originalContainer = document.createElement('div');
            originalContainer.id = 'original-canvas-container';
            originalContainer.style.width = '49%';
            originalContainer.style.display = 'inline-block';
            originalContainer.style.verticalAlign = 'top';
            originalContainer.style.marginLeft = '2%';
            originalContainer.style.position = 'relative';
            originalContainer.innerHTML = `
                <div style="text-align: center; margin-bottom: 8px; font-weight: bold; color: #666;">
                    Original
                </div>
                <canvas id="original-canvas"></canvas>
            `;
            canvasWrapper.appendChild(originalContainer);
        } else {
            originalContainer.style.display = 'inline-block';
        }

        // Add label to edited canvas
        let editedLabel = canvasContainer.querySelector('.canvas-label') as HTMLElement;
        if (!editedLabel) {
            editedLabel = document.createElement('div');
            editedLabel.className = 'canvas-label';
            editedLabel.style.textAlign = 'center';
            editedLabel.style.marginBottom = '8px';
            editedLabel.style.fontWeight = 'bold';
            editedLabel.style.color = '#666';
            editedLabel.textContent = 'Edited';
            canvasContainer.insertBefore(editedLabel, canvasContainer.firstChild);
        }

        // Create original canvas if doesn't exist
        if (!this.originalCanvas) {
            const originalCanvasEl = document.getElementById('original-canvas') as HTMLCanvasElement;
            if (originalCanvasEl) {
                this.originalCanvas = new fabric.Canvas('original-canvas', {
                    width: this.canvas.getWidth(),
                    height: this.canvas.getHeight(),
                    backgroundColor: '#ffffff',
                    selection: false,  // Read-only
                });

                // Disable all interactions on original canvas
                this.originalCanvas.selection = false;
                this.originalCanvas.forEachObject((obj: any) => {
                    obj.selectable = false;
                    obj.evented = false;
                });
            }
        }

        // Load states into both canvases
        if (this.originalCanvas) {
            this.originalCanvas.loadFromJSON(this.originalCanvasState, () => {
                this.originalCanvas!.renderAll();
                // Note: Grid is not drawn on original canvas (read-only comparison view)
            });
        }

        this.canvas.loadFromJSON(this.editedCanvasState, () => {
            this.canvas!.renderAll();

            // Restore grid if enabled (on edited canvas only)
            if (this.gridEnabled) {
                this.drawGrid();
            }
        });

        this.updateStatus('Split view: Original | Edited');
    }

    private async saveAsOriginal() {
        if (!this.canvas) return;

        const canvasState = this.canvas.toJSON(['id', 'panelId', 'filename']);

        try {
            const response = await fetch(`/vis/api/figures/${this.figureId}/versions/create/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    version_type: 'original',
                    label: 'Original',
                    canvas_state: canvasState,
                }),
            });

            const data = await response.json();

            if (data.success) {
                this.originalCanvasState = canvasState;
                this.updateStatus('Saved as original version');
                console.log('[VisEditor] Original version saved:', data.version_id);
            } else {
                this.updateStatus('Failed to save original version');
            }
        } catch (error) {
            console.error('[VisEditor] Save original failed:', error);
            this.updateStatus('Error saving original version');
        }
    }

    private async loadOriginalVersion() {
        try {
            const response = await fetch(`/vis/api/figures/${this.figureId}/versions/original/`);
            const data = await response.json();

            if (data.success) {
                this.originalCanvasState = data.canvas_state;
                console.log('[VisEditor] Original version loaded');
            } else {
                console.log('[VisEditor] No original version found');
                this.originalCanvasState = null;
            }
        } catch (error) {
            console.error('[VisEditor] Load original failed:', error);
            this.originalCanvasState = null;
        }
    }

    private async showVersionHistory() {
        const modal = document.getElementById('version-history-modal');
        if (!modal) return;

        modal.style.display = 'flex';

        // Load versions
        await this.loadVersionsList();
    }

    private async loadVersionsList() {
        const versionsList = document.getElementById('versions-list');
        if (!versionsList) return;

        versionsList.innerHTML = '<p>Loading versions...</p>';

        try {
            const response = await fetch(`/vis/api/figures/${this.figureId}/versions/`);
            const data = await response.json();

            if (data.success && data.versions.length > 0) {
                versionsList.innerHTML = data.versions.map((v: any) => `
                    <div class="version-item" data-version-id="${v.id}">
                        <div class="version-info">
                            <strong>${v.label}</strong>
                            <span class="version-meta">${new Date(v.created_at).toLocaleString()}</span>
                            <span class="version-meta">by ${v.created_by}</span>
                        </div>
                        <div class="version-actions">
                            <button class="btn btn-sm load-version-btn" data-version-id="${v.id}">
                                <i class="fas fa-upload"></i> Load
                            </button>
                            <button class="btn btn-sm set-original-btn" data-version-id="${v.id}">
                                <i class="fas fa-bookmark"></i> Set as Original
                            </button>
                        </div>
                    </div>
                `).join('');

                // Add event listeners
                versionsList.querySelectorAll('.load-version-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        const versionId = (e.currentTarget as HTMLElement).dataset.versionId;
                        if (versionId) this.loadVersion(versionId);
                    });
                });

                versionsList.querySelectorAll('.set-original-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        const versionId = (e.currentTarget as HTMLElement).dataset.versionId;
                        if (versionId) this.setAsOriginal(versionId);
                    });
                });
            } else {
                versionsList.innerHTML = '<p class="text-muted">No versions found</p>';
            }
        } catch (error) {
            console.error('[VisEditor] Load versions failed:', error);
            versionsList.innerHTML = '<p class="text-error">Failed to load versions</p>';
        }
    }

    private async loadVersion(versionId: string) {
        if (!this.canvas) return;

        try {
            const response = await fetch(`/vis/api/figures/${this.figureId}/versions/${versionId}/`);
            const data = await response.json();

            if (data.success) {
                this.canvas.loadFromJSON(data.canvas_state, () => {
                    this.canvas!.renderAll();

                    // Restore grid if enabled (grid lines are not saved in versions)
                    if (this.gridEnabled) {
                        this.drawGrid();
                    }

                    this.updateStatus(`Loaded version: ${data.label}`);
                    console.log('[VisEditor] Version loaded:', versionId);
                });

                // Close modal
                const modal = document.getElementById('version-history-modal');
                if (modal) modal.style.display = 'none';
            }
        } catch (error) {
            console.error('[VisEditor] Load version failed:', error);
            this.updateStatus('Error loading version');
        }
    }

    private async setAsOriginal(versionId: string) {
        try {
            const response = await fetch(`/vis/api/figures/${this.figureId}/versions/original/set/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({ version_id: versionId }),
            });

            const data = await response.json();

            if (data.success) {
                this.updateStatus('Original version updated');
                await this.loadVersionsList();  // Refresh list
                await this.loadOriginalVersion();  // Reload original state
            }
        } catch (error) {
            console.error('[VisEditor] Set original failed:', error);
            this.updateStatus('Error setting original version');
        }
    }

    private getCSRFToken(): string {
        const token = document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement;
        return token ? token.value : '';
    }
}

// Tab Switcher and Demo Gallery Functions
function initTabSwitcher(): void {
    const userDataTab = document.getElementById('user-data-tab') as HTMLButtonElement;
    const demoGalleryTab = document.getElementById('demo-gallery-tab') as HTMLButtonElement;
    const userDataSection = document.getElementById('user-data-section') as HTMLDivElement;
    const demoGallerySection = document.getElementById('demo-gallery-section') as HTMLDivElement;

    if (!userDataTab || !demoGalleryTab || !userDataSection || !demoGallerySection) {
        console.warn('[TabSwitcher] Required elements not found');
        return;
    }

    // Tab click handlers
    userDataTab.addEventListener('click', () => {
        userDataTab.classList.add('active');
        demoGalleryTab.classList.remove('active');
        userDataSection.style.display = 'block';
        demoGallerySection.style.display = 'none';
        showNotification('Switched to Your Data tab', 'info');
    });

    demoGalleryTab.addEventListener('click', () => {
        demoGalleryTab.classList.add('active');
        userDataTab.classList.remove('active');
        demoGallerySection.style.display = 'block';
        userDataSection.style.display = 'none';
        showNotification('Switched to Demo Gallery', 'info');
    });

    // Demo gallery item click handlers
    const galleryItems = document.querySelectorAll('.demo-gallery-item');
    galleryItems.forEach(item => {
        item.addEventListener('click', () => {
            const demoName = item.getAttribute('data-demo');
            if (demoName) {
                loadDemoExample(demoName);
            }
        });
    });

    console.log('[TabSwitcher] Initialized with', galleryItems.length, 'demo items');
}

let currentDemoName: string | null = null;

async function loadDemoExample(demoName: string): Promise<void> {
    try {
        showNotification(`Loading demo: ${demoName}...`, 'info');

        const jsonPath = `/static/vis_app/img/plot_gallery/${demoName}.json`;
        const response = await fetch(jsonPath);

        if (!response.ok) {
            throw new Error(`Failed to fetch ${jsonPath}: ${response.status} ${response.statusText}`);
        }

        const metadata = await response.json();
        console.log('[DemoLoader] Loaded metadata:', metadata);

        // Store current demo name for data import
        currentDemoName = demoName;

        // Automatically load CSV data into demo data table
        await loadDemoDataToTable(demoName);

        // Store plot data for rendering
        currentPlotData = {
            plot: {
                kind: metadata.plot_type || metadata.method || 'line',
                data: [[0, 0], [1, 1], [2, 4], [3, 9], [4, 16]],  // Demo data
                xlabel: metadata.axes?.x?.label || 'X Axis',
                ylabel: metadata.axes?.y?.label || 'Y Axis',
                title: metadata.id || 'Demo Plot',
            },
        };

        // Populate the Visual Style Editor with metadata
        populateStyleEditorFromMetadata(metadata);

        // Display the demo image in the right panel
        displayDemoImage(demoName);

        // Trigger initial render with loaded style
        renderPlotWithCurrentStyle();

        showNotification(`Demo loaded: ${demoName}`, 'success');
    } catch (error) {
        console.error('[DemoLoader] Failed to load demo:', error);
        showNotification(`Failed to load demo: ${demoName}`, 'error');
    }
}

async function importDemoDataToSpreadsheet(): Promise<void> {
    if (!currentDemoName) {
        showNotification('No demo selected', 'error');
        return;
    }

    try {
        const csvPath = `/static/vis_app/img/plot_gallery/${currentDemoName}.csv`;
        const response = await fetch(csvPath);

        if (!response.ok) {
            throw new Error(`CSV not found: ${csvPath}`);
        }

        const csvText = await response.text();
        console.log('[DemoData] Loaded CSV:', csvText.substring(0, 200));

        // Parse CSV
        const lines = csvText.trim().split('\n');
        if (lines.length < 2) {
            throw new Error('CSV file is empty or invalid');
        }

        const headers = lines[0].split(',');
        const rows = lines.slice(1);

        // Clear and populate spreadsheet
        const table = document.getElementById('data-spreadsheet') as HTMLTableElement;
        if (!table) {
            throw new Error('Spreadsheet table not found');
        }

        // Update headers
        const headerRow = table.querySelector('thead tr');
        if (headerRow) {
            headerRow.innerHTML = '';
            headers.forEach(header => {
                const th = document.createElement('th');
                th.contentEditable = 'true';
                th.style.cssText = 'padding: 6px; border: 1px solid var(--border-color); font-weight: 600; min-width: 80px;';
                th.textContent = header.trim();
                headerRow.appendChild(th);
            });
        }

        // Update data rows
        const tbody = table.querySelector('tbody');
        if (tbody) {
            tbody.innerHTML = '';
            rows.forEach(rowText => {
                const values = rowText.split(',');
                const tr = document.createElement('tr');
                values.forEach(value => {
                    const td = document.createElement('td');
                    td.contentEditable = 'true';
                    td.style.cssText = 'padding: 6px; border: 1px solid var(--border-color);';
                    td.textContent = value.trim();
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
        }

        // Switch to "Your Data" tab and Spreadsheet sub-tab
        const userDataTab = document.getElementById('user-data-tab') as HTMLButtonElement;
        const spreadsheetTab = document.getElementById('spreadsheet-data-tab') as HTMLButtonElement;

        if (userDataTab) {
            userDataTab.click();  // Switch to "Your Data"
        }

        if (spreadsheetTab) {
            spreadsheetTab.click();  // Switch to "Spreadsheet"
        }

        showNotification(`Imported ${rows.length} rows from demo`, 'success');
    } catch (error) {
        console.error('[DemoData] Import failed:', error);
        showNotification(`Failed to import demo data: ${error}`, 'error');
    }
}

async function loadDemoDataToTable(demoName: string): Promise<void> {
    try {
        // Use scitex.io.load via backend API
        const csvPath = `/static/vis_app/img/plot_gallery/${demoName}.csv`;

        // TODO: Replace with proper scitex.io.load API call
        // For now, fetch CSV and let backend handle with scitex.io.load in future
        const response = await fetch(csvPath);

        if (!response.ok) {
            console.warn(`[DemoData] CSV not found: ${csvPath}`);
            return;
        }

        const csvText = await response.text();
        const lines = csvText.trim().split('\n');
        if (lines.length < 2) {
            return;
        }

        const headers = lines[0].split(',');
        const rows = lines.slice(1).slice(0, 50); // Limit to first 50 rows for performance

        // Create HTML table
        const tableContainer = document.getElementById('demo-data-table-container');
        if (!tableContainer) return;

        let tableHTML = '<table style="width: 100%; border-collapse: collapse; font-size: 10px;">';
        tableHTML += '<thead style="background: #f8f9fa; position: sticky; top: 0; z-index: 1;"><tr>';
        headers.forEach(header => {
            tableHTML += `<th style="padding: 4px 6px; border: 1px solid #ddd; font-weight: 600; text-align: left; font-size: 10px;">${header.trim()}</th>`;
        });
        tableHTML += '</tr></thead><tbody>';

        rows.forEach(rowText => {
            const values = rowText.split(',');
            tableHTML += '<tr style="transition: background 0.1s;">';
            values.forEach(value => {
                const numValue = parseFloat(value);
                const displayValue = !isNaN(numValue) && value.includes('.')
                    ? numValue.toFixed(3)
                    : value.trim();
                tableHTML += `<td style="padding: 4px 6px; border: 1px solid #eee; font-family: monospace;">${displayValue}</td>`;
            });
            tableHTML += '</tr>';
        });

        tableHTML += '</tbody></table>';

        // Add row count info if truncated
        if (lines.length > 51) {
            tableHTML += `<div style="padding: 8px; text-align: center; font-size: 10px; color: var(--text-muted); background: #f8f9fa; border-top: 1px solid #ddd;">Showing first 50 of ${lines.length - 1} rows</div>`;
        }

        tableContainer.innerHTML = tableHTML;

        console.log(`[DemoData] Loaded ${rows.length} rows (via scitex.io.load in future)`);
    } catch (error) {
        console.error('[DemoData] Failed to load demo data:', error);
    }
}

function populateStyleEditorFromMetadata(metadata: any): void {
    if (!metadata || !metadata.scitex) {
        console.warn('[StyleEditor] Invalid metadata structure');
        return;
    }

    const scitex = metadata.scitex;
    const style = scitex.style_mm || {};
    const dimensions = metadata.dimensions || {};
    const margins = metadata.margins_mm || {};

    // Detect plot type and update control states
    const plotType = detectPlotType(metadata);
    console.log('[StyleEditor] Detected plot type:', plotType);
    updateControlStates(plotType);

    // Dimensions
    setInputValue('ax-width-mm', dimensions.axes_size_mm?.[0]);
    setInputValue('ax-height-mm', dimensions.axes_size_mm?.[1]);

    // Typography
    setInputValue('title-font-size-pt', style.title_font_size_pt);
    setInputValue('axis-font-size-pt', style.axis_font_size_pt);
    setInputValue('tick-font-size-pt', style.tick_font_size_pt);
    setInputValue('font-family', style.font_family);
    setInputValue('font-weight', style.font_weight);

    // Line Properties
    setInputValue('trace-thickness-mm', style.trace_thickness_mm);
    setInputValue('axis-thickness-mm', style.axis_thickness_mm);
    setInputValue('tick-thickness-mm', style.tick_thickness_mm);
    setInputValue('tick-length-mm', style.tick_length_mm);

    // Additional Fonts
    setInputValue('suptitle-font-size-pt', style.suptitle_font_size_pt);
    setInputValue('legend-font-size-pt', style.legend_font_size_pt);

    // Plot Elements
    setInputValue('errorbar-capsize-mm', style.errorbar_capsize_mm);
    setInputValue('errorbar-thickness-mm', style.errorbar_thickness_mm);
    setInputValue('bar-edge-thickness-mm', style.bar_edge_thickness_mm);
    setInputValue('kde-bandwidth', style.kde_bandwidth);
    setInputValue('scatter-size-mm', style.scatter_size_mm);

    // Spacing
    setInputValue('label-pad-pt', style.label_pad_pt);
    setInputValue('tick-pad-pt', style.tick_pad_pt);
    setInputValue('title-pad-pt', style.title_pad_pt);
    setInputValue('left-margin-mm', margins.left);
    setInputValue('bottom-margin-mm', margins.bottom);
    setInputValue('right-margin-mm', margins.right);
    setInputValue('top-margin-mm', margins.top);

    // Advanced Settings
    setInputValue('n-ticks', style.n_ticks);
    setInputValue('dpi', dimensions.dpi);
    setInputValue('mode', scitex.mode);
    setInputValue('transparent', metadata.transparent);
    setInputValue('auto-scale-axes', metadata.auto_scale_axes);

    console.log('[StyleEditor] Populated controls from metadata (plot type:', plotType, ')');
}

function setInputValue(id: string, value: any): void {
    if (value === undefined || value === null) return;

    const input = document.getElementById(id) as HTMLInputElement | HTMLSelectElement;
    if (!input) {
        console.warn(`[StyleEditor] Input not found: ${id}`);
        return;
    }

    if (input.type === 'checkbox') {
        (input as HTMLInputElement).checked = Boolean(value);
    } else {
        input.value = String(value);
    }
}

function displayDemoImage(demoName: string): void {
    const imagePath = `/static/vis_app/img/plot_gallery/${demoName}.jpg`;

    // Find or create image display area in the right panel
    let imageContainer = document.getElementById('demo-image-display');

    if (!imageContainer) {
        // Create image container if it doesn't exist
        const rightPanel = document.querySelector('.vis-right-panel');
        if (rightPanel) {
            imageContainer = document.createElement('div');
            imageContainer.id = 'demo-image-display';
            imageContainer.style.cssText = 'width: 100%; padding: 20px; box-sizing: border-box;';
            rightPanel.prepend(imageContainer);
        }
    }

    if (imageContainer) {
        imageContainer.innerHTML = `
            <div style="background: white; border-radius: 8px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h3 style="margin: 0 0 12px 0; font-size: 14px; color: #333;">
                    <i class="fas fa-eye"></i> Demo Preview
                </h3>
                <img src="${imagePath}" alt="${demoName}" style="width: 100%; height: auto; border-radius: 4px; border: 1px solid #e0e0e0;">
                <p style="margin: 12px 0 0 0; font-size: 12px; color: #666; text-align: center;">
                    ${demoName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </p>
            </div>
        `;
    }
}

function showNotification(message: string, type: 'success' | 'error' | 'info' = 'info'): void {
    const typeUpper = type.toUpperCase();
    console.log(`[${typeUpper}] ${message}`);

    // You can enhance this with a visual notification later
    // For now, just console logging
}

// Plot Type Detection and Conditional Control Management
type PlotType = 'line' | 'scatter' | 'bar' | 'image' | 'contour' | 'errorbar' | 'kde' | 'violin' | 'box' | 'heatmap' | 'shaded_line' | 'mean_std' | 'ecdf' | 'unknown';

interface ControlRelevance {
    [controlId: string]: PlotType[];
}

// Define which controls are relevant for which plot types
const CONTROL_RELEVANCE: ControlRelevance = {
    // Dimensions - always relevant
    'ax-width-mm': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],
    'ax-height-mm': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],

    // Typography - always relevant
    'title-font-size-pt': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],
    'axis-font-size-pt': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],
    'tick-font-size-pt': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],
    'font-family': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],
    'font-weight': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],

    // Line Properties
    'trace-thickness-mm': ['line', 'shaded_line', 'mean_std', 'ecdf', 'contour'],  // Line-based plots
    'axis-thickness-mm': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],
    'tick-thickness-mm': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],
    'tick-length-mm': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],

    // Additional Fonts
    'suptitle-font-size-pt': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],
    'legend-font-size-pt': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],

    // Plot Elements - plot-type specific
    'errorbar-capsize-mm': ['errorbar', 'mean_std', 'bar'],  // Plots with error bars
    'errorbar-thickness-mm': ['errorbar', 'mean_std', 'bar'],  // Plots with error bars
    'bar-edge-thickness-mm': ['bar', 'violin', 'box'],  // Bar-like plots
    'kde-bandwidth': ['kde', 'violin'],  // KDE plots
    'scatter-size-mm': ['scatter'],  // Scatter plots

    // Spacing - always relevant
    'label-pad-pt': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],
    'tick-pad-pt': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],
    'title-pad-pt': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],
    'left-margin-mm': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],
    'bottom-margin-mm': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],
    'right-margin-mm': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],
    'top-margin-mm': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],

    // Advanced Settings - always relevant
    'n-ticks': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],
    'dpi': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],
    'mode': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],
    'transparent': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],
    'auto-scale-axes': ['line', 'scatter', 'bar', 'image', 'contour', 'errorbar', 'kde', 'violin', 'box', 'heatmap', 'shaded_line', 'mean_std', 'ecdf'],
};

function detectPlotType(metadata: any): PlotType {
    if (!metadata) return 'unknown';

    // Check metadata.plot_type first
    if (metadata.plot_type) {
        const plotType = metadata.plot_type.toLowerCase();

        // Map known plot types
        const plotTypeMap: { [key: string]: PlotType } = {
            'line': 'line',
            'scatter': 'scatter',
            'bar': 'bar',
            'image': 'image',
            'contour': 'contour',
            'errorbar': 'errorbar',
            'kde': 'kde',
            'violin': 'violin',
            'box': 'box',
            'heatmap': 'heatmap',
            'shaded_line': 'shaded_line',
            'mean_std': 'mean_std',
            'ecdf': 'ecdf',
        };

        if (plotTypeMap[plotType]) {
            return plotTypeMap[plotType];
        }
    }

    // Fallback to method detection
    if (metadata.method) {
        const method = metadata.method.toLowerCase();

        const methodMap: { [key: string]: PlotType } = {
            'plot': 'line',
            'scatter': 'scatter',
            'bar': 'bar',
            'barh': 'bar',
            'imshow': 'image',
            'contour': 'contour',
            'contourf': 'contour',
        };

        if (methodMap[method]) {
            return methodMap[method];
        }
    }

    return 'unknown';
}

function updateControlStates(plotType: PlotType): void {
    console.log('[ControlManager] Updating control states for plot type:', plotType);

    // If unknown plot type, enable all controls
    if (plotType === 'unknown') {
        console.log('[ControlManager] Unknown plot type - enabling all controls');
        enableAllControls();
        return;
    }

    // Iterate through all controls and enable/disable based on relevance
    Object.keys(CONTROL_RELEVANCE).forEach(controlId => {
        const input = document.getElementById(controlId) as HTMLInputElement | HTMLSelectElement;
        if (!input) {
            return;
        }

        const relevantPlotTypes = CONTROL_RELEVANCE[controlId];
        const isRelevant = relevantPlotTypes.includes(plotType);

        // Get the parent container (usually a div wrapping label + input)
        const container = input.closest('.control-item, .control-row, div[style*="display"]') as HTMLElement;

        if (isRelevant) {
            // Enable control
            input.disabled = false;
            input.style.opacity = '1';
            input.style.cursor = 'auto';

            if (container) {
                container.style.opacity = '1';
                container.title = '';
            }
        } else {
            // Disable control
            input.disabled = true;
            input.style.opacity = '0.4';
            input.style.cursor = 'not-allowed';

            if (container) {
                container.style.opacity = '0.4';
                container.title = `Not applicable for ${plotType} plots`;
            }
        }
    });

    const enabledCount = Object.keys(CONTROL_RELEVANCE).filter(id => {
        const relevantTypes = CONTROL_RELEVANCE[id];
        return relevantTypes.includes(plotType);
    }).length;

    const totalCount = Object.keys(CONTROL_RELEVANCE).length;
    console.log(`[ControlManager] ${enabledCount}/${totalCount} controls enabled for ${plotType} plots`);
}

function enableAllControls(): void {
    Object.keys(CONTROL_RELEVANCE).forEach(controlId => {
        const input = document.getElementById(controlId) as HTMLInputElement | HTMLSelectElement;
        if (!input) return;

        input.disabled = false;
        input.style.opacity = '1';
        input.style.cursor = 'auto';

        const container = input.closest('.control-item, .control-row, div[style*="display"]') as HTMLElement;
        if (container) {
            container.style.opacity = '1';
            container.title = '';
        }
    });

    console.log('[ControlManager] All controls enabled');
}

// Real-time Backend Rendering
interface StyleSpecification {
    figure: {
        width_mm: number;
        height_mm: number;
        dpi: number;
    };
    style: {
        tick_length_mm?: number;
        tick_thickness_mm?: number;
        axis_thickness_mm?: number;
        trace_thickness_mm?: number;
        errorbar_capsize_mm?: number;
        errorbar_thickness_mm?: number;
        bar_edge_thickness_mm?: number;
        kde_bandwidth?: number;
        scatter_size_mm?: number;
        axis_font_size_pt?: number;
        tick_font_size_pt?: number;
        title_font_size_pt?: number;
        suptitle_font_size_pt?: number;
        legend_font_size_pt?: number;
        label_pad_pt?: number;
        tick_pad_pt?: number;
        title_pad_pt?: number;
        font_family?: string;
        font_weight?: string;
    };
    plot?: {
        kind: string;
        data?: any[];
        csv_path?: string;
        x_column?: string;
        y_column?: string;
        xlabel?: string;
        ylabel?: string;
        title?: string;
        color?: string;
    };
    margins_mm?: {
        left?: number;
        bottom?: number;
        right?: number;
        top?: number;
    };
}

function getInputValue(id: string): any {
    const input = document.getElementById(id) as HTMLInputElement | HTMLSelectElement;
    if (!input) return undefined;

    if (input.type === 'checkbox') {
        return (input as HTMLInputElement).checked;
    } else if (input.type === 'number') {
        const val = parseFloat(input.value);
        return isNaN(val) ? undefined : val;
    } else {
        return input.value || undefined;
    }
}

function collectStyleSpecification(): StyleSpecification {
    // Collect all values from the Visual Style Editor
    const spec: StyleSpecification = {
        figure: {
            width_mm: getInputValue('ax-width-mm') || 40,
            height_mm: getInputValue('ax-height-mm') || 28,
            dpi: getInputValue('dpi') || 300,
        },
        style: {
            // Line Properties
            trace_thickness_mm: getInputValue('trace-thickness-mm'),
            axis_thickness_mm: getInputValue('axis-thickness-mm'),
            tick_thickness_mm: getInputValue('tick-thickness-mm'),
            tick_length_mm: getInputValue('tick-length-mm'),

            // Plot Elements
            errorbar_capsize_mm: getInputValue('errorbar-capsize-mm'),
            errorbar_thickness_mm: getInputValue('errorbar-thickness-mm'),
            bar_edge_thickness_mm: getInputValue('bar-edge-thickness-mm'),
            kde_bandwidth: getInputValue('kde-bandwidth'),
            scatter_size_mm: getInputValue('scatter-size-mm'),

            // Typography
            axis_font_size_pt: getInputValue('axis-font-size-pt'),
            tick_font_size_pt: getInputValue('tick-font-size-pt'),
            title_font_size_pt: getInputValue('title-font-size-pt'),
            suptitle_font_size_pt: getInputValue('suptitle-font-size-pt'),
            legend_font_size_pt: getInputValue('legend-font-size-pt'),
            font_family: getInputValue('font-family'),
            font_weight: getInputValue('font-weight'),

            // Spacing
            label_pad_pt: getInputValue('label-pad-pt'),
            tick_pad_pt: getInputValue('tick-pad-pt'),
            title_pad_pt: getInputValue('title-pad-pt'),
        },
        margins_mm: {
            left: getInputValue('left-margin-mm'),
            bottom: getInputValue('bottom-margin-mm'),
            right: getInputValue('right-margin-mm'),
            top: getInputValue('top-margin-mm'),
        },
    };

    // Remove undefined values to keep spec clean
    Object.keys(spec.style).forEach(key => {
        if (spec.style[key as keyof typeof spec.style] === undefined) {
            delete spec.style[key as keyof typeof spec.style];
        }
    });

    return spec;
}

let currentPlotData: any = null;
let renderDebounceTimer: number | null = null;

async function renderPlotWithCurrentStyle(): Promise<void> {
    if (!currentPlotData) {
        console.warn('[Renderer] No plot data loaded yet');
        return;
    }

    try {
        const spec = collectStyleSpecification();

        // Merge with current plot data
        const fullSpec = {
            ...spec,
            plot: currentPlotData.plot || {
                kind: 'line',
                data: [[0, 0], [1, 1], [2, 4], [3, 9], [4, 16]],  // Default demo data
                xlabel: 'X Axis',
                ylabel: 'Y Axis',
                title: 'Preview',
            },
        };

        console.log('[Renderer] Sending spec to backend:', fullSpec);

        // Send to backend API
        const response = await fetch('/vis/api/plot/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(fullSpec),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }

        // Get SVG response
        const svgText = await response.text();

        // Display in right panel
        displayRenderedPlot(svgText);

        showNotification('Plot rendered successfully', 'success');
    } catch (error) {
        console.error('[Renderer] Failed to render plot:', error);
        showNotification(`Render failed: ${error}`, 'error');
    }
}

function displayRenderedPlot(svgContent: string): void {
    // Find or create SVG display container
    let container = document.getElementById('rendered-plot-display');

    if (!container) {
        const rightPanel = document.querySelector('.vis-right-panel');
        if (rightPanel) {
            container = document.createElement('div');
            container.id = 'rendered-plot-display';
            container.style.cssText = 'width: 100%; padding: 20px; box-sizing: border-box;';
            rightPanel.prepend(container);
        }
    }

    if (container) {
        container.innerHTML = `
            <div style="background: white; border-radius: 8px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h3 style="margin: 0 0 12px 0; font-size: 14px; color: #333;">
                    <i class="fas fa-chart-line"></i> Live Preview
                </h3>
                <div style="width: 100%; overflow: auto; border: 1px solid #e0e0e0; border-radius: 4px; background: #fafafa;">
                    ${svgContent}
                </div>
            </div>
        `;
    }
}

function debouncedRender(delay: number = 500): void {
    if (renderDebounceTimer !== null) {
        window.clearTimeout(renderDebounceTimer);
    }

    renderDebounceTimer = window.setTimeout(() => {
        renderPlotWithCurrentStyle();
        renderDebounceTimer = null;
    }, delay);
}

function attachRenderListeners(): void {
    // Attach change listeners to all control inputs
    Object.keys(CONTROL_RELEVANCE).forEach(controlId => {
        const input = document.getElementById(controlId) as HTMLInputElement | HTMLSelectElement;
        if (!input) return;

        // Use 'input' event for real-time updates as user types/drags
        input.addEventListener('input', () => {
            debouncedRender(500);  // 500ms debounce
        });

        // Also listen to 'change' event for dropdowns and checkboxes
        input.addEventListener('change', () => {
            renderPlotWithCurrentStyle();  // Immediate render on select/checkbox
        });
    });

    console.log('[Renderer] Attached change listeners to', Object.keys(CONTROL_RELEVANCE).length, 'controls');
}

// Spreadsheet Data Management
function initDataInputTabs(): void {
    const uploadTab = document.getElementById('upload-data-tab') as HTMLButtonElement;
    const spreadsheetTab = document.getElementById('spreadsheet-data-tab') as HTMLButtonElement;
    const uploadSection = document.getElementById('upload-section') as HTMLDivElement;
    const spreadsheetSection = document.getElementById('spreadsheet-section') as HTMLDivElement;

    if (!uploadTab || !spreadsheetTab || !uploadSection || !spreadsheetSection) {
        console.warn('[DataInput] Required elements not found');
        return;
    }

    uploadTab.addEventListener('click', () => {
        uploadTab.classList.add('active');
        spreadsheetTab.classList.remove('active');
        uploadTab.style.background = '#4a9b7e';
        uploadTab.style.color = 'white';
        uploadTab.style.borderColor = '#4a9b7e';
        spreadsheetTab.style.background = 'white';
        spreadsheetTab.style.color = 'var(--text-primary)';
        spreadsheetTab.style.borderColor = 'var(--border-color)';
        uploadSection.style.display = 'block';
        spreadsheetSection.style.display = 'none';
    });

    spreadsheetTab.addEventListener('click', () => {
        spreadsheetTab.classList.add('active');
        uploadTab.classList.remove('active');
        spreadsheetTab.style.background = '#4a9b7e';
        spreadsheetTab.style.color = 'white';
        spreadsheetTab.style.borderColor = '#4a9b7e';
        uploadTab.style.background = 'white';
        uploadTab.style.color = 'var(--text-primary)';
        uploadTab.style.borderColor = 'var(--border-color)';
        spreadsheetSection.style.display = 'block';
        uploadSection.style.display = 'none';
    });

    console.log('[DataInput] Tabs initialized');
}

function initSpreadsheet(): void {
    const addColumnBtn = document.getElementById('add-column-btn');
    const addRowBtn = document.getElementById('add-row-btn');
    const clearDataBtn = document.getElementById('clear-data-btn');
    const applyDataBtn = document.getElementById('apply-spreadsheet-data-btn');

    if (addColumnBtn) {
        addColumnBtn.addEventListener('click', addSpreadsheetColumn);
    }

    if (addRowBtn) {
        addRowBtn.addEventListener('click', addSpreadsheetRow);
    }

    if (clearDataBtn) {
        clearDataBtn.addEventListener('click', clearSpreadsheetData);
    }

    if (applyDataBtn) {
        applyDataBtn.addEventListener('click', applySpreadsheetData);
    }

    // Wire up "Import Demo Data" button
    const importDemoBtn = document.getElementById('import-demo-data-btn');
    if (importDemoBtn) {
        importDemoBtn.addEventListener('click', importDemoDataToSpreadsheet);
    }

    console.log('[Spreadsheet] Initialized');
}

function addSpreadsheetColumn(): void {
    const table = document.getElementById('data-spreadsheet') as HTMLTableElement;
    if (!table) return;

    const headerRow = table.querySelector('thead tr');
    const bodyRows = table.querySelectorAll('tbody tr');

    if (headerRow) {
        const th = document.createElement('th');
        th.contentEditable = 'true';
        th.style.cssText = 'padding: 6px; border: 1px solid var(--border-color); font-weight: 600; min-width: 80px;';
        th.textContent = `Col ${headerRow.children.length + 1}`;
        headerRow.appendChild(th);
    }

    bodyRows.forEach(row => {
        const td = document.createElement('td');
        td.contentEditable = 'true';
        td.style.cssText = 'padding: 6px; border: 1px solid var(--border-color);';
        td.textContent = '0';
        row.appendChild(td);
    });

    showNotification('Column added', 'success');
}

function addSpreadsheetRow(): void {
    const table = document.getElementById('data-spreadsheet') as HTMLTableElement;
    if (!table) return;

    const tbody = table.querySelector('tbody');
    const headerRow = table.querySelector('thead tr');

    if (!tbody || !headerRow) return;

    const colCount = headerRow.children.length;
    const tr = document.createElement('tr');

    for (let i = 0; i < colCount; i++) {
        const td = document.createElement('td');
        td.contentEditable = 'true';
        td.style.cssText = 'padding: 6px; border: 1px solid var(--border-color);';
        td.textContent = '0';
        tr.appendChild(td);
    }

    tbody.appendChild(tr);
    showNotification('Row added', 'success');
}

function clearSpreadsheetData(): void {
    const table = document.getElementById('data-spreadsheet') as HTMLTableElement;
    if (!table) return;

    const bodyRows = table.querySelectorAll('tbody tr');
    bodyRows.forEach(row => {
        const cells = row.querySelectorAll('td');
        cells.forEach(cell => {
            (cell as HTMLElement).textContent = '0';
        });
    });

    showNotification('Data cleared', 'info');
}

function applySpreadsheetData(): void {
    const data = getSpreadsheetData();

    if (!data || data.length === 0) {
        showNotification('No data to apply', 'error');
        return;
    }

    // Store spreadsheet data for rendering
    currentPlotData = {
        plot: {
            kind: 'line',
            data: data,
            xlabel: getSpreadsheetHeaders()[0] || 'X',
            ylabel: getSpreadsheetHeaders()[1] || 'Y',
            title: 'Spreadsheet Data',
        },
    };

    // Trigger render
    renderPlotWithCurrentStyle();
    showNotification(`Applied ${data.length} rows of data`, 'success');
}

function getSpreadsheetHeaders(): string[] {
    const table = document.getElementById('data-spreadsheet') as HTMLTableElement;
    if (!table) return [];

    const headerRow = table.querySelector('thead tr');
    if (!headerRow) return [];

    const headers: string[] = [];
    headerRow.querySelectorAll('th').forEach(th => {
        headers.push((th as HTMLElement).textContent || '');
    });

    return headers;
}

function getSpreadsheetData(): number[][] {
    const table = document.getElementById('data-spreadsheet') as HTMLTableElement;
    if (!table) return [];

    const bodyRows = table.querySelectorAll('tbody tr');
    const data: number[][] = [];

    bodyRows.forEach(row => {
        const rowData: number[] = [];
        row.querySelectorAll('td').forEach(cell => {
            const value = parseFloat((cell as HTMLElement).textContent || '0');
            rowData.push(isNaN(value) ? 0 : value);
        });

        if (rowData.length > 0) {
            data.push(rowData);
        }
    });

    return data;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new VisEditor();
        initTabSwitcher();
        initDataInputTabs();
        initSpreadsheet();
        attachRenderListeners();
    });
} else {
    new VisEditor();
    initTabSwitcher();
    initDataInputTabs();
    initSpreadsheet();
    attachRenderListeners();
}
