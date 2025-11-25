/**
 * SciTeX Sigma Editor - SigmaPlot-Inspired Interface
 * TypeScript Implementation with Data Handling and Visualization
 *
 * REFACTORED: Now uses modularized manager components
 */

// Import all managers from the sigma module
import {
    RulersManager,
    CanvasManager,
    DataTableManager,
    PropertiesManager,
    UIManager,
    Dataset,
    CANVAS_CONSTANTS
} from './sigma/index.js';

// Fabric.js type declarations
declare namespace fabric {
    type Canvas = any;
    type Object = any;
    type Line = any;
}
declare const fabric: any;

/**
 * SigmaEditor - Coordinator class that manages all editor components
 *
 * This class now serves as a lightweight coordinator that:
 * - Initializes all manager modules
 * - Connects managers through callbacks
 * - Handles plot creation (not yet extracted)
 * - Maintains overall editor state
 */
class SigmaEditor {
    // Manager instances
    private rulersManager: RulersManager;
    private canvasManager: CanvasManager;
    private dataTableManager: DataTableManager;
    private propertiesManager: PropertiesManager;
    private uiManager: UIManager;

    // Plot-related state (not yet extracted)
    private currentPlot: any = null;
    private currentPlotType: string = '';

    // Shared references for managers
    private firstRowIsHeader: boolean = true;
    private firstColIsIndex: boolean = false;

    constructor() {
        console.log('[SigmaEditor] Initializing modular Sigma Editor...');

        // Initialize CanvasManager
        this.canvasManager = new CanvasManager(
            (message: string) => this.updateStatusBar(message),
            () => this.updateRulersAreaTransform()
        );

        // Initialize RulersManager
        this.rulersManager = new RulersManager(
            null, // Canvas will be set after initialization
            (message: string) => this.updateStatusBar(message)
        );

        // Initialize DataTableManager
        this.dataTableManager = new DataTableManager(
            (message: string) => this.updateStatusBar(message),
            () => this.propertiesManager.updateColumnDropdowns(),
            () => this.updateRulersAreaTransform()
        );

        // Initialize PropertiesManager
        this.propertiesManager = new PropertiesManager(
            () => this.dataTableManager.getCurrentData()
        );

        // Initialize UIManager
        this.uiManager = new UIManager(
            (file: File) => this.dataTableManager.handleFileImport(file),
            () => this.dataTableManager.loadDemoData(),
            (count: number) => this.dataTableManager.addColumns(count),
            (count: number) => this.dataTableManager.addRows(count),
            () => this.dataTableManager['copySelectionToClipboard'](),
            (plotType: string) => this.createQuickPlot(plotType),
            () => this.canvasManager.zoomIn(),
            () => this.canvasManager.zoomOut(),
            () => this.canvasManager.zoomToFit(),
            () => this.canvasManager.toggleGrid(),
            { value: this.firstRowIsHeader },
            { value: this.firstColIsIndex },
            () => this.dataTableManager.renderEditableDataTable(),
            (message: string) => this.updateStatusBar(message)
        );

        // Initialize all components
        this.initializeEditor();
    }

    /**
     * Initialize editor components using parallel execution for independent tasks
     */
    private async initializeEditor(): Promise<void> {
        const totalStart = performance.now();
        console.log('[SigmaEditor] Starting optimized initialization...');

        // PHASE 1: CRITICAL PATH ONLY - Minimal initialization for first paint
        const phase1Start = performance.now();

        // Initialize UI event listeners (fast, no heavy DOM work)
        this.uiManager.initializeEventListeners();

        // Initialize minimal data table (fast with small table)
        this.dataTableManager.initializeBlankTable();

        const phase1End = performance.now();
        console.log(`[SigmaEditor] Phase 1 complete in ${(phase1End - phase1Start).toFixed(2)}ms (critical path - UI ready)`);

        // PHASE 2: DEFERRED - Non-critical components loaded after first paint
        const phase2Start = performance.now();

        // Defer heavy initialization to next event loop tick (allows UI to be responsive)
        await new Promise(resolve => setTimeout(resolve, 0));

        // Setup table events (lightweight)
        this.setupDataTableEvents();
        this.dataTableManager.setupColumnResizing();
        this.uiManager.setupKeyboardShortcuts();

        const phase2End = performance.now();
        console.log(`[SigmaEditor] Phase 2 complete in ${(phase2End - phase2Start).toFixed(2)}ms (table setup finished)`);

        // PHASE 3: DEFERRED - Canvas and heavy graphics work
        const phase3Start = performance.now();

        // Defer to next tick again
        await new Promise(resolve => setTimeout(resolve, 0));

        // Initialize canvas (HEAVY: creates 5000+ grid lines)
        this.canvasManager.initCanvas();
        this.canvasManager.setupCanvasEvents();

        // Initialize rulers (HEAVY: creates 200+ SVG elements)
        this.rulersManager['canvas'] = this.canvasManager.canvas;
        this.rulersManager.initializeRulers();
        this.rulersManager.setupRulerDragging();

        const phase3End = performance.now();
        console.log(`[SigmaEditor] Phase 3 complete in ${(phase3End - phase3Start).toFixed(2)}ms (canvas & rulers initialized)`);

        // PHASE 4: DEFERRED - Properties and final setup
        const phase4Start = performance.now();

        // Defer to next tick
        await new Promise(resolve => setTimeout(resolve, 0));

        // Initialize properties tabs and sliders
        this.propertiesManager.initPropertiesTabs();
        this.propertiesManager.setupPropertySliders();

        // Connect managers
        this.uiManager.setPropertiesManager(this.propertiesManager);
        this.uiManager.setDataTableManager(this.dataTableManager);
        this.uiManager.initializeTreeManager();

        // Update status bar
        this.updateStatusBar('Ready');

        const phase4End = performance.now();
        console.log(`[SigmaEditor] Phase 4 complete in ${(phase4End - phase4Start).toFixed(2)}ms (properties & final setup)`);

        const totalEnd = performance.now();
        console.log(`[SigmaEditor] ✅ Total initialization complete in ${(totalEnd - totalStart).toFixed(2)}ms`);

        // TIMING SUMMARY
        console.log('\n═══════════════════════════════════════════════════════');
        console.log('📊 VIS PAGE LOAD TIMING SUMMARY');
        console.log('═══════════════════════════════════════════════════════');
        console.log(`Phase 1 (parallel init):     ${(phase1End - phase1Start).toFixed(2)}ms`);
        console.log(`Phase 2 (parallel setup):    ${(phase2End - phase2Start).toFixed(2)}ms`);
        console.log(`Phase 3 (rulers):            ${(phase3End - phase3Start).toFixed(2)}ms`);
        console.log(`Phase 4 (connections):       ${(phase4End - phase4Start).toFixed(2)}ms`);
        console.log('───────────────────────────────────────────────────────');
        console.log(`TOTAL:                       ${(totalEnd - totalStart).toFixed(2)}ms`);
        console.log('═══════════════════════════════════════════════════════\n');
    }

    /**
     * Setup data table events (uses native scrolling)
     */
    private setupDataTableEvents(): void {
        // Data tables use native browser scrolling for better usability
        console.log('[SigmaEditor] Data table using native scrolling');
    }

    /**
     * Update rulers area transform (keeps rulers and canvas synchronized)
     */
    private updateRulersAreaTransform(): void {
        const rulersArea = document.querySelector('.sigma-rulers-area') as HTMLElement;
        if (!rulersArea) return;

        const zoom = this.canvasManager.getCanvasZoomLevel();
        const pan = this.canvasManager.getCanvasPanOffset();

        rulersArea.style.transform = `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`;
        rulersArea.style.transformOrigin = '0 0';
    }

    /**
     * Update status bar (delegates to UIManager)
     */
    private updateStatusBar(message?: string): void {
        this.uiManager.updateStatusBar(message);
    }

    /**
     * Create quick plot
     */
    private createQuickPlot(plotType: string): void {
        const currentData = this.dataTableManager.getCurrentData();
        if (!currentData || currentData.rows.length === 0) {
            this.updateStatusBar('Please load data first');
            return;
        }

        console.log(`[SigmaEditor] Creating ${plotType} plot...`);
        this.updateStatusBar(`Creating ${plotType} plot...`);

        // Render plot in split view
        this.renderPlot(plotType);
    }

    /**
     * Render plot using Plotly
     */
    private renderPlot(plotType: string): void {
        const currentData = this.dataTableManager.getCurrentData();
        if (!currentData) return;

        const plotArea = document.getElementById('plot-container-wrapper');
        if (!plotArea) return;

        // Create plot container
        plotArea.innerHTML = '<div id="plot-container" style="width: 100%; height: 100%;"></div>';
        const plotContainer = document.getElementById('plot-container');
        if (!plotContainer) return;

        // Get selected columns from properties panel
        const { xColumn, yColumn } = this.propertiesManager.getSelectedColumns();

        // Get plot properties (line width, marker size, etc.)
        const plotProps = this.propertiesManager.getPlotProperties();

        const xData = currentData.rows.map(row => row[xColumn]);
        const yData = currentData.rows.map(row => row[yColumn]);

        // Prepare trace based on plot type
        let trace: any = {
            x: xData,
            y: yData,
            name: `${yColumn} vs ${xColumn}`,
        };

        switch (plotType) {
            case 'scatter':
                trace.mode = 'markers';
                trace.type = 'scatter';
                trace.marker = { size: plotProps.markerSize, color: '#4a9b7e' };
                break;
            case 'line':
                trace.mode = 'lines';
                trace.type = 'scatter';
                trace.line = { color: '#4a9b7e', width: plotProps.lineWidth };
                break;
            case 'lineMarker':
                trace.mode = 'lines+markers';
                trace.type = 'scatter';
                trace.line = { color: '#4a9b7e', width: plotProps.lineWidth };
                trace.marker = { size: plotProps.markerSize, color: '#4a9b7e' };
                break;
            case 'bar':
                trace.type = 'bar';
                trace.marker = { color: '#4a9b7e' };
                break;
            case 'histogram':
                trace = {
                    x: xData,
                    type: 'histogram',
                    marker: { color: '#4a9b7e' },
                    name: xColumn
                };
                break;
            case 'box':
                trace = {
                    y: yData,
                    type: 'box',
                    name: yColumn,
                    marker: { color: '#4a9b7e' }
                };
                break;
            default:
                trace.mode = 'lines+markers';
                trace.type = 'scatter';
        }

        const layout = {
            title: {
                text: `${plotType.charAt(0).toUpperCase() + plotType.slice(1)} Plot`,
                font: { size: 16, family: 'Arial, sans-serif' }
            },
            xaxis: {
                title: xColumn,
                showgrid: true,
                zeroline: false
            },
            yaxis: {
                title: yColumn,
                showgrid: true,
                zeroline: false
            },
            margin: { l: 60, r: 40, t: 60, b: 60 },
            paper_bgcolor: 'var(--bg-primary)',
            plot_bgcolor: 'var(--bg-primary)',
            font: { color: 'var(--text-primary)' }
        };

        const config = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            displaylogo: false
        };

        // Check if Plotly is available
        if (typeof (window as any).Plotly !== 'undefined') {
            (window as any).Plotly.newPlot(plotContainer, [trace], layout, config);
            this.currentPlot = trace;
            this.currentPlotType = plotType;
            this.updateStatusBar(`${plotType} plot created`);
            console.log('[SigmaEditor] Plot created successfully');
        } else {
            console.error('[SigmaEditor] Plotly.js not available');
            this.updateStatusBar('Plotly.js not available');
        }
    }

    /**
     * Apply journal preset style
     */
    private applyJournalPreset(preset: string): void {
        console.log(`[SigmaEditor] Applying ${preset} style...`);
        this.updateStatusBar(`Applying ${preset} style...`);

        if (!this.currentPlot) {
            this.updateStatusBar('No plot to apply preset to');
            return;
        }

        // Journal presets will be implemented based on requirements
        // Nature: Single column width (89mm), specific fonts
        // Science: Different column widths and styling
        // Cell: Another set of specifications
        this.updateStatusBar(`${preset} style will be implemented`);
    }

    /**
     * Update canvas theme (light/dark mode)
     */
    public updateCanvasTheme(isDark: boolean): void {
        this.canvasManager.updateCanvasTheme(isDark);
        this.rulersManager.updateRulerTheme(isDark);  // Update rulers too!
    }
}

// Initialize editor when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('[SigmaEditor] DOM loaded, initializing editor...');
    const editorInstance = new SigmaEditor();

    // Expose to window for theme switching
    (window as any).sigmaEditor = editorInstance;

    // Setup canvas-specific theme toggle (independent from global theme)
    const themeToggle = document.getElementById('canvas-theme-toggle');
    if (themeToggle) {
        // Get global theme first to use as default
        const globalTheme = localStorage.getItem('scitex-theme-preference') || 'dark';

        // Canvas has its own theme state, but defaults to global theme
        const canvasThemeValue = localStorage.getItem('canvas-theme') || globalTheme;
        let canvasIsDark = canvasThemeValue === 'dark';

        // Function to update theme icon
        const updateThemeIcon = (isDark: boolean) => {
            const icon = themeToggle.querySelector('i');
            if (icon) {
                icon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
            }
        };

        themeToggle.addEventListener('click', () => {
            // Toggle ONLY the canvas theme, not the global theme
            canvasIsDark = !canvasIsDark;
            const canvasTheme = canvasIsDark ? 'dark' : 'light';
            localStorage.setItem('canvas-theme', canvasTheme);

            // Update canvas theme (grid and rulers)
            editorInstance.updateCanvasTheme(canvasIsDark);

            // Update button icon
            updateThemeIcon(canvasIsDark);

            console.log(`[SigmaEditor] Canvas theme toggled to ${canvasTheme} (independent from global theme)`);
        });

        // Set initial icon based on canvas theme
        updateThemeIcon(canvasIsDark);
    } else {
        console.warn('[SigmaEditor] Canvas theme toggle button not found');
    }

    // Apply saved global theme (for website UI)
    // Use the correct key that matches the global theme system
    const savedTheme = localStorage.getItem('scitex-theme-preference') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);

    // Apply saved canvas theme (independent from global theme, but defaults to global theme)
    const savedCanvasTheme = localStorage.getItem('canvas-theme') || savedTheme;
    const canvasDarkMode = savedCanvasTheme === 'dark';
    editorInstance.updateCanvasTheme(canvasDarkMode);

    console.log('[SigmaEditor] Editor ready');
});

// Export for module usage
export { SigmaEditor };
