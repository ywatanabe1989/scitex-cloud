/**
 * Element Inspector - Visual Debugging Tool
 *
 * Shows all HTML elements with colored rectangles and labels.
 * Toggle with Ctrl+Shift+I
 */

console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/static/shared/ts/utils/element-inspector.ts loaded");

class ElementInspector {
    private isActive: boolean = false;
    private overlayContainer: HTMLDivElement | null = null;
    private styleElement: HTMLStyleElement | null = null;

    constructor() {
        this.init();
    }

    private init(): void {
        // Add keyboard shortcut: Ctrl+Shift+I
        document.addEventListener('keydown', (e: KeyboardEvent) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'I') {
                e.preventDefault();
                this.toggle();
            }
        });

        console.log('[ElementInspector] Initialized - Press Ctrl+Shift+I to toggle');
    }

    private toggle(): void {
        if (this.isActive) {
            this.deactivate();
        } else {
            this.activate();
        }
    }

    private activate(): void {
        console.log('[ElementInspector] Activating...');
        this.isActive = true;

        // Create overlay container
        this.overlayContainer = document.createElement('div');
        this.overlayContainer.id = 'element-inspector-overlay';
        this.overlayContainer.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 999999;
        `;

        // Add styles
        this.addStyles();

        // Scan all elements and create overlays
        this.scanElements();

        // Append to body
        document.body.appendChild(this.overlayContainer);

        console.log('[ElementInspector] Active - Press Ctrl+Shift+I to deactivate');
    }

    private deactivate(): void {
        console.log('[ElementInspector] Deactivating...');
        this.isActive = false;

        // Remove overlay
        if (this.overlayContainer) {
            this.overlayContainer.remove();
            this.overlayContainer = null;
        }

        // Remove styles
        if (this.styleElement) {
            this.styleElement.remove();
            this.styleElement = null;
        }
    }

    private addStyles(): void {
        this.styleElement = document.createElement('style');
        this.styleElement.textContent = `
            .element-inspector-box {
                position: absolute;
                border: 2px solid;
                box-sizing: border-box;
                pointer-events: none;
                transition: opacity 0.2s;
            }

            .element-inspector-label {
                position: absolute;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 2px 6px;
                font-size: 11px;
                font-family: monospace;
                border-radius: 3px;
                white-space: nowrap;
                pointer-events: none;
                z-index: 1;
            }

            .element-inspector-label-id {
                color: #4EC9B0;
                font-weight: bold;
            }

            .element-inspector-label-class {
                color: #9CDCFE;
            }

            .element-inspector-label-tag {
                color: #CE9178;
            }
        `;
        document.head.appendChild(this.styleElement);
    }

    private scanElements(): void {
        if (!this.overlayContainer) return;

        // Get all elements
        const allElements = document.querySelectorAll('*');
        let count = 0;

        allElements.forEach((element: Element, index: number) => {
            // Skip our own overlay elements
            if (element.closest('#element-inspector-overlay')) return;

            // Skip invisible elements
            if (element instanceof HTMLElement) {
                const computed = window.getComputedStyle(element);
                if (computed.display === 'none' || computed.visibility === 'hidden') return;
            }

            // Get nesting depth for color gradation
            const depth = this.getDepth(element);
            const color = this.getColorForDepth(depth);

            // Create rectangle overlay
            const rect = element.getBoundingClientRect();
            if (rect.width === 0 || rect.height === 0) return;

            const box = document.createElement('div');
            box.className = 'element-inspector-box';
            box.style.cssText = `
                top: ${rect.top + window.scrollY}px;
                left: ${rect.left + window.scrollX}px;
                width: ${rect.width}px;
                height: ${rect.height}px;
                border-color: ${color};
                opacity: 0.6;
            `;

            // Create label
            const label = this.createLabel(element, depth);
            if (label) {
                label.style.top = `${rect.top + window.scrollY - 20}px`;
                label.style.left = `${rect.left + window.scrollX}px`;
            }

            this.overlayContainer!.appendChild(box);
            if (label) {
                this.overlayContainer!.appendChild(label);
            }

            count++;
        });

        console.log(`[ElementInspector] Visualized ${count} elements`);
    }

    private getDepth(element: Element): number {
        let depth = 0;
        let current: Element | null = element;

        while (current && current !== document.body) {
            depth++;
            current = current.parentElement;
        }

        return depth;
    }

    private getColorForDepth(depth: number): string {
        // Color gradation: blue → green → yellow → orange → red
        const colors = [
            '#3B82F6',  // Blue (depth 0-2)
            '#10B981',  // Green (depth 3-5)
            '#F59E0B',  // Yellow (depth 6-8)
            '#EF4444',  // Red (depth 9-11)
            '#EC4899',  // Pink (depth 12+)
        ];

        const index = Math.min(Math.floor(depth / 3), colors.length - 1);
        return colors[index];
    }

    private createLabel(element: Element, depth: number): HTMLDivElement | null {
        const tag = element.tagName.toLowerCase();
        const id = element.id;
        const classes = element.className;

        // Build label text
        let labelText = `<span class="element-inspector-label-tag">&lt;${tag}&gt;</span>`;

        if (id) {
            labelText += ` <span class="element-inspector-label-id">#${id}</span>`;
        }

        if (classes && typeof classes === 'string') {
            const classList = classes.split(/\s+/).filter(c => c.length > 0);
            if (classList.length > 0) {
                const classPreview = classList.slice(0, 3).join(' .');
                labelText += ` <span class="element-inspector-label-class">.${classPreview}</span>`;
                if (classList.length > 3) {
                    labelText += ` <span class="element-inspector-label-class">+${classList.length - 3}</span>`;
                }
            }
        }

        // Add depth indicator
        labelText += ` <span style="color: #808080; margin-left: 4px;">d:${depth}</span>`;

        const label = document.createElement('div');
        label.className = 'element-inspector-label';
        label.innerHTML = labelText;

        return label;
    }

    public refresh(): void {
        if (this.isActive) {
            this.deactivate();
            this.activate();
        }
    }
}

// Initialize global instance
const elementInspector = new ElementInspector();

// Export to window for manual control
(window as any).elementInspector = elementInspector;

// Auto-refresh on window resize (with debounce)
let resizeTimeout: number;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = window.setTimeout(() => {
        if ((window as any).elementInspector?.isActive) {
            (window as any).elementInspector.refresh();
        }
    }, 500);
});
