/**
 * ResizerManager - Centralized panel resizing logic
 *
 * Single-source-of-truth for all panel resize operations
 * Ensures minimum width constraints across all affected panels
 */

interface ResizerConfig {
    resizerId: string;
    targetPanel: string;      // The panel being directly resized
    affectedPanels: string[]; // All panels that must maintain minimum width
    minWidth: number;
    maxWidth: number;
    resizeTarget: 'left' | 'right';
}

export class ResizerManager {
    private resizers: Map<string, ResizerConfig> = new Map();

    /**
     * Register a panel resizer with its configuration
     */
    public registerResizer(config: ResizerConfig): void {
        this.resizers.set(config.resizerId, config);
        this.initializeResizer(config);
    }

    /**
     * Initialize a single resizer with event handlers
     */
    private initializeResizer(config: ResizerConfig): void {
        const resizer = document.getElementById(config.resizerId);
        const targetPanel = document.querySelector(config.targetPanel) as HTMLElement;

        if (!resizer || !targetPanel) {
            console.warn(`[ResizerManager] Failed to initialize ${config.resizerId}`);
            return;
        }

        let isResizing = false;
        let startX = 0;
        let startWidth = 0;

        const handleMouseDown = (e: MouseEvent) => {
            isResizing = true;
            startX = e.clientX;
            startWidth = targetPanel.offsetWidth;

            document.body.style.cursor = 'col-resize';
            document.body.style.userSelect = 'none';

            e.preventDefault();
        };

        const handleMouseMove = (e: MouseEvent) => {
            if (!isResizing) return;

            const delta = e.clientX - startX;

            // Calculate new width based on resize direction
            const newWidth = config.resizeTarget === 'left'
                ? startWidth + delta
                : startWidth - delta;

            // Check if new width is within bounds for target panel
            if (newWidth < config.minWidth || newWidth > config.maxWidth) {
                return;
            }

            // Check all affected panels maintain minimum width
            if (!this.checkAllPanelConstraints(config, delta)) {
                return;
            }

            // Apply resize
            targetPanel.style.width = `${newWidth}px`;
            targetPanel.style.flexShrink = '0';
            targetPanel.style.flexGrow = '0';
        };

        const handleMouseUp = () => {
            if (isResizing) {
                isResizing = false;
                document.body.style.cursor = '';
                document.body.style.userSelect = '';
            }
        };

        resizer.addEventListener('mousedown', handleMouseDown);
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);

        console.log(`[ResizerManager] Initialized ${config.resizerId} affecting ${config.affectedPanels.length} panels`);
    }

    /**
     * Check that all affected panels will maintain minimum width after resize
     */
    private checkAllPanelConstraints(config: ResizerConfig, delta: number): boolean {
        for (const panelSelector of config.affectedPanels) {
            const panel = document.querySelector(panelSelector) as HTMLElement;
            if (!panel) continue;

            const currentWidth = panel.offsetWidth;

            // Calculate how this panel will be affected by the resize
            let newWidth = currentWidth;

            if (panelSelector === config.targetPanel) {
                // This is the target panel
                newWidth = config.resizeTarget === 'left'
                    ? currentWidth + delta
                    : currentWidth - delta;
            } else {
                // This is an affected panel - calculate its new width
                // For flexbox layouts, when one panel grows, others shrink
                // The exact calculation depends on the layout structure

                // If target is expanding (delta > 0 for left, delta < 0 for right)
                // then other panels in the same container shrink
                const isTargetExpanding = config.resizeTarget === 'left' ? delta > 0 : delta < 0;

                if (isTargetExpanding) {
                    // Other panels shrink by delta
                    newWidth = currentWidth - Math.abs(delta);
                } else {
                    // Other panels grow by delta
                    newWidth = currentWidth + Math.abs(delta);
                }
            }

            // Check minimum constraint
            if (newWidth < config.minWidth) {
                console.log(`[ResizerManager] Blocked: ${panelSelector} would be ${newWidth}px (min: ${config.minWidth}px)`);
                return false;
            }
        }

        return true;
    }

    /**
     * Initialize all standard Sigma editor panel resizers
     */
    public initializeSigmaResizers(): void {
        // Sidebar resizer: Project ↔ Data Table
        // Affected panels: Project, Data Table, Canvas (all must stay >= 10px)
        this.registerResizer({
            resizerId: 'sidebar-resizer',
            targetPanel: '.sigma-sidebar',
            affectedPanels: ['.sigma-sidebar', '#data-pane', '#canvas-pane'],
            minWidth: 10,
            maxWidth: Infinity,
            resizeTarget: 'left'
        });

        // Split resizer: Data Table ↔ Canvas
        // Affected panels: Data Table, Canvas
        this.registerResizer({
            resizerId: 'split-resizer',
            targetPanel: '#data-pane',
            affectedPanels: ['#data-pane', '#canvas-pane'],
            minWidth: 10,
            maxWidth: Infinity,
            resizeTarget: 'left'
        });

        // Workspace resizer: Workspace ↔ Properties
        // Affected panels: Workspace (including Data + Canvas), Properties
        this.registerResizer({
            resizerId: 'workspace-resizer',
            targetPanel: '.sigma-properties',
            affectedPanels: ['.sigma-workspace', '.sigma-properties'],
            minWidth: 10,
            maxWidth: Infinity,
            resizeTarget: 'right'
        });

        console.log('[ResizerManager] All Sigma editor resizers initialized');
    }
}
