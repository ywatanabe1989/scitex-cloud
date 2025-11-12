/**
 * Element Inspector - Visual Debugging Tool
 *
 * Shows all HTML elements with colored rectangles and labels.
 * Toggle with Alt+I (I for Inspector)
 */

console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/static/shared/ts/utils/element-inspector.ts loaded");

class ElementInspector {
    private isActive: boolean = false;
    private overlayContainer: HTMLDivElement | null = null;
    private styleElement: HTMLStyleElement | null = null;
    private selectionMode: boolean = false;
    private selectionStart: { x: number; y: number } | null = null;
    private selectionRect: HTMLDivElement | null = null;
    private selectionOverlay: HTMLDivElement | null = null;
    private elementBoxMap: Map<HTMLDivElement, Element> = new Map();
    private layerPickerMenu: HTMLDivElement | null = null;
    private currentlyHoveredBox: HTMLDivElement | null = null;
    private currentlyHoveredElement: Element | null = null;
    private currentlySelectedElements: Set<Element> = new Set();

    constructor() {
        this.init();
    }

    private init(): void {
        // Add keyboard shortcuts
        document.addEventListener('keydown', (e: KeyboardEvent) => {
            // Alt+I: Toggle inspector
            if (e.altKey && !e.shiftKey && !e.ctrlKey && e.key === 'i') {
                e.preventDefault();
                this.toggle();
            }

            // Alt+C: Copy full page structure
            if (e.altKey && !e.shiftKey && !e.ctrlKey && (e.key === 'c' || e.key === 'C')) {
                e.preventDefault();
                this.copyPageStructure();
            }

            // Ctrl+Alt+I: Start rectangle selection mode
            if (e.ctrlKey && e.altKey && !e.shiftKey && e.key === 'i') {
                e.preventDefault();
                this.startSelectionMode();
            }

            // Escape: Deactivate inspector and cancel selection mode
            if (e.key === 'Escape') {
                e.preventDefault();
                if (this.selectionMode) {
                    this.cancelSelectionMode();
                    // Also deactivate the inspector visualization
                    this.deactivate();
                } else if (this.isActive) {
                    this.deactivate();
                }
            }
        });

        console.log('[ElementInspector] Initialized');
        console.log('  Alt+I: Toggle inspector overlay');
        console.log('  Alt+C: Copy full page structure');
        console.log('  Ctrl+Alt+I: Rectangle selection mode');
        console.log('  Escape: Deactivate inspector / Cancel selection');
    }

    public toggle(): void {
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

        // Calculate full document height
        const docHeight = Math.max(
            document.body.scrollHeight,
            document.documentElement.scrollHeight,
            document.body.offsetHeight,
            document.documentElement.offsetHeight,
            document.body.clientHeight,
            document.documentElement.clientHeight
        );

        this.overlayContainer.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: ${docHeight}px;
            pointer-events: none;
            z-index: 999999;
        `;

        // Add styles
        this.addStyles();

        // Scan all elements and create overlays
        this.scanElements();

        // Append to body
        document.body.appendChild(this.overlayContainer);

        console.log('[ElementInspector] Active - Press Alt+I to deactivate');
    }

    private deactivate(): void {
        console.log('[ElementInspector] Deactivating...');
        this.isActive = false;

        // Clear element map
        this.elementBoxMap.clear();

        // Clear hover tracking
        this.currentlyHoveredBox = null;
        this.currentlyHoveredElement = null;

        // Close layer picker if open
        this.closeLayerPicker();

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
                pointer-events: auto;
                cursor: pointer;
                transition: all 0.2s;
                background: rgba(255, 255, 255, 0.01);
            }

            .element-inspector-box:hover {
                border-width: 3px;
                background: rgba(59, 130, 246, 0.1);
                box-shadow:
                    0 0 0 2px rgba(255, 255, 255, 0.6),
                    0 0 15px rgba(59, 130, 246, 0.4);
            }

            .element-inspector-box.highlighted {
                border-width: 4px;
                z-index: 999999;
                background: rgba(59, 130, 246, 0.2);
                box-shadow:
                    0 0 0 3px rgba(255, 255, 255, 0.9),
                    0 0 30px rgba(59, 130, 246, 0.8),
                    inset 0 0 30px rgba(59, 130, 246, 0.3);
                animation: pulse 1s ease-in-out infinite;
            }

            .element-inspector-selected {
                /* Colors applied dynamically based on depth */
                transition: outline 0.15s, background 0.15s, box-shadow 0.15s;
            }

            @keyframes pulse {
                0%, 100% {
                    box-shadow:
                        0 0 0 3px rgba(255, 255, 255, 0.9),
                        0 0 30px rgba(59, 130, 246, 0.8),
                        inset 0 0 30px rgba(59, 130, 246, 0.3);
                }
                50% {
                    box-shadow:
                        0 0 0 4px rgba(255, 255, 255, 1),
                        0 0 40px rgba(59, 130, 246, 1),
                        inset 0 0 40px rgba(59, 130, 246, 0.4);
                }
            }

            .element-inspector-label {
                position: absolute;
                background: rgba(0, 0, 0, 0.9);
                color: white;
                padding: 1px 4px;
                font-size: 10px;
                font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
                border-radius: 2px;
                white-space: nowrap;
                pointer-events: auto;
                cursor: pointer;
                z-index: 1000000;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
                line-height: 1.4;
                max-width: 300px;
                overflow: hidden;
                text-overflow: ellipsis;
                transition: background 0.2s, transform 0.1s;
            }

            .element-inspector-label:hover {
                background: rgba(30, 30, 30, 0.95);
                transform: scale(1.05);
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.7);
            }

            .element-inspector-label:active {
                transform: scale(0.98);
            }

            .element-inspector-label.copied {
                background: rgba(16, 185, 129, 0.9);
                animation: copied-flash 0.5s ease;
            }

            @keyframes copied-flash {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }

            @keyframes slideIn {
                from { transform: translateX(400px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }

            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(400px); opacity: 0; }
            }

            .camera-flash {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: white;
                pointer-events: none;
                z-index: 99999999;
                animation: cameraFlash 0.5s ease-out;
            }

            @keyframes cameraFlash {
                0% { opacity: 0; }
                15% { opacity: 0.9; }
                30% { opacity: 0; }
                45% { opacity: 0.6; }
                60% { opacity: 0; }
                100% { opacity: 0; }
            }

            .selection-overlay {
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                width: 100% !important;
                height: 100% !important;
                background: rgba(0, 0, 0, 0.3) !important;
                pointer-events: none !important;
                z-index: 2147483646 !important;
            }

            /* Force crosshair cursor during selection mode */
            body.element-inspector-selection-mode,
            body.element-inspector-selection-mode * {
                cursor: crosshair !important;
            }

            .selection-rectangle {
                position: fixed !important;
                border: 2px dotted rgba(59, 130, 246, 1) !important;
                background: transparent !important;
                pointer-events: none !important;
                z-index: 2147483647 !important;
                box-shadow: 0 0 0 99999px rgba(0, 0, 0, 0.3) !important;
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
            }

            .selection-info {
                position: absolute;
                bottom: -32px;
                right: 0;
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.98) 0%, rgba(37, 99, 235, 0.98) 100%);
                color: white;
                padding: 6px 14px;
                font-size: 13px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                border-radius: 6px;
                pointer-events: none;
                font-weight: 600;
                box-shadow:
                    0 4px 12px rgba(0, 0, 0, 0.4),
                    0 0 20px rgba(59, 130, 246, 0.3);
                white-space: nowrap;
                border: 2px solid rgba(255, 255, 255, 0.3);
                backdrop-filter: blur(4px);
            }

            .selection-toolbar {
                position: absolute;
                top: -40px;
                left: 0;
                display: flex;
                gap: 4px;
                background: rgba(255, 255, 255, 0.98);
                padding: 6px;
                border-radius: 6px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                pointer-events: auto;
            }

            .selection-toolbar-btn {
                padding: 6px 12px;
                border: none;
                background: rgba(59, 130, 246, 0.1);
                color: #1e40af;
                border-radius: 4px;
                font-size: 11px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                cursor: pointer;
                font-weight: 500;
                transition: all 0.2s;
            }

            .selection-toolbar-btn:hover {
                background: rgba(59, 130, 246, 0.2);
                transform: translateY(-1px);
            }

            .selection-corners {
                position: absolute;
                width: 100%;
                height: 100%;
                pointer-events: none;
            }

            .selection-corner {
                position: absolute;
                width: 12px;
                height: 12px;
                background: white;
                border: 3px solid rgba(59, 130, 246, 1);
                border-radius: 2px;
                box-shadow:
                    0 2px 8px rgba(0, 0, 0, 0.4),
                    0 0 12px rgba(59, 130, 246, 0.6);
                animation: corner-pulse 2s ease-in-out infinite;
            }

            @keyframes corner-pulse {
                0%, 100% {
                    transform: scale(1);
                    box-shadow:
                        0 2px 8px rgba(0, 0, 0, 0.4),
                        0 0 12px rgba(59, 130, 246, 0.6);
                }
                50% {
                    transform: scale(1.2);
                    box-shadow:
                        0 2px 12px rgba(0, 0, 0, 0.5),
                        0 0 18px rgba(59, 130, 246, 0.9);
                }
            }

            .selection-corner.top-left { top: -6px; left: -6px; }
            .selection-corner.top-right { top: -6px; right: -6px; }
            .selection-corner.bottom-left { bottom: -6px; left: -6px; }
            .selection-corner.bottom-right { bottom: -6px; right: -6px; }

            .layer-picker-menu {
                position: absolute;
                background: rgba(255, 255, 255, 0.98);
                border: 2px solid #3B82F6;
                border-radius: 6px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
                z-index: 100000000;
                min-width: 250px;
                max-height: 400px;
                overflow-y: auto;
                pointer-events: auto;
            }

            .layer-picker-header {
                padding: 8px 12px;
                background: #3B82F6;
                color: white;
                font-size: 11px;
                font-weight: 600;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }

            .layer-picker-item {
                padding: 8px 12px;
                border-bottom: 1px solid rgba(0, 0, 0, 0.1);
                cursor: pointer;
                font-size: 11px;
                font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
                transition: background 0.15s;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .layer-picker-item:hover {
                background: rgba(59, 130, 246, 0.1);
            }

            .layer-picker-item:active {
                background: rgba(59, 130, 246, 0.2);
            }

            .layer-picker-depth {
                display: inline-block;
                width: 30px;
                text-align: right;
                color: #666;
                font-size: 10px;
            }

            .layer-picker-tag {
                color: #CE9178;
            }

            .layer-picker-id {
                color: #4EC9B0;
                font-weight: bold;
            }

            .layer-picker-class {
                color: #9CDCFE;
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

            /* Responsive: hide labels on very small screens */
            @media (max-width: 768px) {
                .element-inspector-label {
                    font-size: 8px;
                    padding: 1px 3px;
                }
            }
        `;
        document.head.appendChild(this.styleElement);
    }

    private scanElements(): void {
        if (!this.overlayContainer) return;

        // Get all elements
        const allElements = document.querySelectorAll('*');
        let count = 0;
        const occupiedPositions: Array<{top: number, left: number, bottom: number, right: number}> = [];

        allElements.forEach((element: Element) => {
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
            `;

            // Set tooltip showing element info
            const tag = element.tagName.toLowerCase();
            const id = element.id ? `#${element.id}` : '';
            box.title = `Click to copy debug info: ${tag}${id}`;

            // Store element reference for layer picking
            this.elementBoxMap.set(box, element);

            // Track hover on box itself (not just label)
            box.addEventListener('mouseenter', () => {
                this.currentlyHoveredBox = box;
                this.currentlyHoveredElement = element;
            });

            box.addEventListener('mouseleave', () => {
                // Only clear if this is the currently hovered box
                if (this.currentlyHoveredBox === box) {
                    this.currentlyHoveredBox = null;
                    this.currentlyHoveredElement = null;
                }
            });

            // Make entire box area clickable - use hovered element if available
            box.addEventListener('click', async (e: MouseEvent) => {
                e.preventDefault();
                e.stopPropagation();

                let selectedBox: HTMLDivElement;
                let selectedElement: Element;

                // If we have a currently hovered element, use that (keeps hover and click consistent)
                if (this.currentlyHoveredBox && this.currentlyHoveredElement) {
                    selectedBox = this.currentlyHoveredBox;
                    selectedElement = this.currentlyHoveredElement;
                } else {
                    // Otherwise, find all overlapping boxes at this click position
                    const overlappingBoxes = this.findOverlappingBoxesAtPoint(e.clientX, e.clientY);

                    // Always select the first one (deepest/top-most element)
                    selectedBox = overlappingBoxes[0] || box;
                    selectedElement = this.elementBoxMap.get(selectedBox) || element;
                }

                // Highlight the selected element
                selectedBox.classList.add('highlighted');

                const debugInfo = this.gatherElementDebugInfo(selectedElement);
                try {
                    await navigator.clipboard.writeText(debugInfo);
                    this.showNotification('✓ Element Info Copied!', 'success');
                    console.log('[ElementInspector] Copied:', debugInfo);

                    setTimeout(() => {
                        selectedBox.classList.remove('highlighted');
                    }, 2000);
                } catch (err) {
                    console.error('[ElementInspector] Copy failed:', err);
                    this.showNotification('✗ Copy Failed', 'error');
                    selectedBox.classList.remove('highlighted');
                }
            });

            // Create label only for important/large elements (sparse mode)
            const shouldShowLabel = this.shouldShowLabel(element, rect, depth);

            if (shouldShowLabel) {
                const label = this.createLabel(element, depth);
                if (label) {
                    // Find non-overlapping position for label
                    const labelPos = this.findLabelPosition(rect, occupiedPositions);

                    // Only add label if we found a good position (not overlapping)
                    if (labelPos.isValid) {
                        label.style.top = `${labelPos.top}px`;
                        label.style.left = `${labelPos.left}px`;

                        // Add click-to-copy functionality
                        this.addCopyToClipboard(label, element);

                        // Add hover highlighting
                        this.addHoverHighlight(label, box, element);

                        // Track occupied space with extra padding to prevent crowding
                        const labelPadding = 8; // Extra space around labels
                        occupiedPositions.push({
                            top: labelPos.top - labelPadding,
                            left: labelPos.left - labelPadding,
                            bottom: labelPos.top + 20 + labelPadding,
                            right: labelPos.left + 250 + labelPadding
                        });

                        this.overlayContainer!.appendChild(label);
                    }
                }
            }

            this.overlayContainer!.appendChild(box);
            count++;
        });

        console.log(`[ElementInspector] Visualized ${count} elements`);
    }

    private shouldShowLabel(element: Element, rect: DOMRect, depth: number): boolean {
        // Criteria for showing labels (SPARSE mode):

        // 1. Element has an ID - always show
        if (element.id) {
            return rect.width > 20 && rect.height > 20;
        }

        // 2. Large elements (100px+) - show
        if (rect.width > 100 || rect.height > 100) {
            return true;
        }

        // 3. Important semantic elements - show if medium sized
        const importantTags = ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer', 'form', 'table'];
        if (importantTags.includes(element.tagName.toLowerCase()) && (rect.width > 50 || rect.height > 50)) {
            return true;
        }

        // 4. Interactive elements with decent size
        const interactiveTags = ['button', 'a', 'input', 'select', 'textarea'];
        if (interactiveTags.includes(element.tagName.toLowerCase()) && (rect.width > 30 || rect.height > 30)) {
            return true;
        }

        // 5. Skip deeply nested small elements
        if (depth > 8 && rect.width < 100 && rect.height < 100) {
            return false;
        }

        // Default: don't show for small elements
        return false;
    }

    private findLabelPosition(
        rect: DOMRect,
        occupiedPositions: Array<{top: number, left: number, bottom: number, right: number}>
    ): {top: number, left: number, isValid: boolean} {
        const scrollY = window.scrollY;
        const scrollX = window.scrollX;

        // Try different positions in order of preference (more positions to avoid overlap)
        const positions = [
            // Top-left (default)
            { top: rect.top + scrollY - 24, left: rect.left + scrollX },
            // Top-right
            { top: rect.top + scrollY - 24, left: rect.right + scrollX - 200 },
            // Inside top-left
            { top: rect.top + scrollY + 4, left: rect.left + scrollX + 4 },
            // Inside top-right
            { top: rect.top + scrollY + 4, left: rect.right + scrollX - 204 },
            // Bottom-left
            { top: rect.bottom + scrollY + 4, left: rect.left + scrollX },
            // Bottom-right
            { top: rect.bottom + scrollY + 4, left: rect.right + scrollX - 200 },
            // Left side (middle)
            { top: rect.top + scrollY + rect.height / 2 - 10, left: rect.left + scrollX - 210 },
            // Right side (middle)
            { top: rect.top + scrollY + rect.height / 2 - 10, left: rect.right + scrollX + 10 },
            // Far top
            { top: rect.top + scrollY - 48, left: rect.left + scrollX },
            // Far bottom
            { top: rect.bottom + scrollY + 28, left: rect.left + scrollX },
        ];

        // Find first non-overlapping position
        for (const pos of positions) {
            if (!this.isPositionOccupied(pos, occupiedPositions)) {
                return { ...pos, isValid: true };
            }
        }

        // If all positions are occupied, don't show this label (too crowded)
        return { top: 0, left: 0, isValid: false };
    }

    private isPositionOccupied(
        pos: {top: number, left: number},
        occupiedPositions: Array<{top: number, left: number, bottom: number, right: number}>
    ): boolean {
        const labelWidth = 250; // Slightly wider to account for longer labels
        const labelHeight = 20;

        for (const occupied of occupiedPositions) {
            // Check if rectangles overlap
            if (!(pos.left + labelWidth < occupied.left ||
                  pos.left > occupied.right ||
                  pos.top + labelHeight < occupied.top ||
                  pos.top > occupied.bottom)) {
                return true;
            }
        }
        return false;
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

        // Build compact label text - prioritize showing ID
        let labelText = `<span class="element-inspector-label-tag">${tag}</span>`;

        // ID is shown prominently right after tag
        if (id) {
            labelText += ` <span class="element-inspector-label-id">#${id}</span>`;
        }

        // Classes come after ID
        if (classes && typeof classes === 'string') {
            const classList = classes.split(/\s+/).filter(c => c.length > 0);
            if (classList.length > 0) {
                // Only show first 2 classes for compactness
                const classPreview = classList.slice(0, 2).join('.');
                labelText += ` <span class="element-inspector-label-class">.${classPreview}</span>`;
                if (classList.length > 2) {
                    labelText += `<span class="element-inspector-label-class">+${classList.length - 2}</span>`;
                }
            }
        }

        // Add depth indicator only for deeper elements
        if (depth > 5) {
            labelText += ` <span style="color: #999; font-size: 9px;">d${depth}</span>`;
        }

        const label = document.createElement('div');
        label.className = 'element-inspector-label';
        label.innerHTML = labelText;
        label.title = 'Click to copy comprehensive debug info for AI';

        return label;
    }

    private addHoverHighlight(label: HTMLDivElement, box: HTMLDivElement, element: Element): void {
        // Highlight box when hovering over label
        label.addEventListener('mouseenter', () => {
            // Track currently hovered element
            this.currentlyHoveredBox = box;
            this.currentlyHoveredElement = element;

            box.classList.add('highlighted');
            // Also add temporary highlight to the actual element
            if (element instanceof HTMLElement) {
                element.style.outline = '3px solid rgba(59, 130, 246, 0.8)';
                element.style.outlineOffset = '2px';
            }
        });

        label.addEventListener('mouseleave', () => {
            // Clear hover tracking when mouse leaves
            this.currentlyHoveredBox = null;
            this.currentlyHoveredElement = null;

            box.classList.remove('highlighted');
            // Remove highlight from actual element
            if (element instanceof HTMLElement) {
                element.style.outline = '';
                element.style.outlineOffset = '';
            }
        });
    }

    private addCopyToClipboard(label: HTMLDivElement, element: Element): void {
        label.addEventListener('click', async (e: MouseEvent) => {
            e.stopPropagation();
            e.preventDefault();

            // Save original text before any modifications
            const originalText = label.innerHTML;

            // Gather comprehensive debugging information
            const debugInfo = this.gatherElementDebugInfo(element);

            // Copy to clipboard
            try {
                await navigator.clipboard.writeText(debugInfo);

                // Visual feedback
                label.classList.add('copied');
                label.innerHTML = '✓ Copied Debug Info!';

                setTimeout(() => {
                    label.classList.remove('copied');
                    label.innerHTML = originalText;
                }, 1500);

                console.log('[ElementInspector] Copied debug info to clipboard');
                console.log(debugInfo);
            } catch (err) {
                console.error('[ElementInspector] Failed to copy:', err);

                // Fallback visual feedback for error
                const originalBg = label.style.background;
                label.style.background = 'rgba(239, 68, 68, 0.9)';
                label.innerHTML = '✗ Copy Failed';
                setTimeout(() => {
                    label.style.background = originalBg;
                    label.innerHTML = originalText;
                }, 1000);
            }
        });
    }

    private gatherElementDebugInfo(element: Element): string {
        const info: any = {};

        // Page Context
        info.url = window.location.href;
        info.timestamp = new Date().toISOString();

        // Element Identification
        const className = typeof element.className === 'string' ? element.className : '';
        info.element = {
            tag: element.tagName.toLowerCase(),
            id: element.id || null,
            classes: className ? className.split(/\s+/).filter(c => c) : [],
            selector: this.buildCSSSelector(element),
            xpath: this.getXPath(element),
        };

        // Attributes
        info.attributes = {};
        for (let i = 0; i < element.attributes.length; i++) {
            const attr = element.attributes[i];
            info.attributes[attr.name] = attr.value;
        }

        // Get computed styles (important ones)
        if (element instanceof HTMLElement) {
            const computed = window.getComputedStyle(element);
            info.styles = {
                display: computed.display,
                position: computed.position,
                width: computed.width,
                height: computed.height,
                margin: computed.margin,
                padding: computed.padding,
                backgroundColor: computed.backgroundColor,
                color: computed.color,
                fontSize: computed.fontSize,
                fontFamily: computed.fontFamily,
                zIndex: computed.zIndex,
                opacity: computed.opacity,
                visibility: computed.visibility,
                overflow: computed.overflow,
            };

            // Inline styles
            if (element.style.cssText) {
                info.inlineStyles = element.style.cssText;
            }

            // Dimensions and position
            const rect = element.getBoundingClientRect();
            info.dimensions = {
                width: rect.width,
                height: rect.height,
                top: rect.top,
                left: rect.left,
                bottom: rect.bottom,
                right: rect.right,
            };

            // Scroll position
            info.scroll = {
                scrollTop: element.scrollTop,
                scrollLeft: element.scrollLeft,
                scrollHeight: element.scrollHeight,
                scrollWidth: element.scrollWidth,
            };

            // Inner content (truncated)
            info.content = {
                innerHTML: element.innerHTML.substring(0, 200) + (element.innerHTML.length > 200 ? '...' : ''),
                textContent: element.textContent?.substring(0, 200) + (element.textContent && element.textContent.length > 200 ? '...' : ''),
            };
        }

        // Event listeners (simplified - can't get all listeners easily)
        info.eventListeners = this.getEventListeners(element);

        // Parent chain
        info.parentChain = this.getParentChain(element);

        // Applied CSS files (approximation via stylesheets)
        info.appliedStylesheets = this.getAppliedStylesheets();

        // Try to find CSS rules that match this element
        info.matchingCSSRules = this.getMatchingCSSRules(element);

        // Format as readable text for AI
        return this.formatDebugInfoForAI(info);
    }

    private buildCSSSelector(element: Element): string {
        const tag = element.tagName.toLowerCase();
        const id = element.id;
        const classes = element.className;

        let selector = tag;
        if (id) {
            selector += `#${id}`;
        }
        if (classes && typeof classes === 'string') {
            const classList = classes.split(/\s+/).filter(c => c);
            if (classList.length > 0) {
                selector += `.${classList.join('.')}`;
            }
        }
        return selector;
    }

    private getXPath(element: Element): string {
        if (element.id) {
            return `//*[@id="${element.id}"]`;
        }

        const parts: string[] = [];
        let current: Element | null = element;

        while (current && current.nodeType === Node.ELEMENT_NODE) {
            let index = 0;
            let sibling = current.previousSibling;

            while (sibling) {
                if (sibling.nodeType === Node.ELEMENT_NODE && sibling.nodeName === current.nodeName) {
                    index++;
                }
                sibling = sibling.previousSibling;
            }

            const tagName = current.nodeName.toLowerCase();
            const pathIndex = index > 0 ? `[${index + 1}]` : '';
            parts.unshift(tagName + pathIndex);

            current = current.parentElement;
        }

        return '/' + parts.join('/');
    }

    private getEventListeners(element: Element): string[] {
        // Note: Can't easily get all event listeners without Chrome DevTools API
        // But we can check common event attributes
        const listeners: string[] = [];
        const eventAttrs = ['onclick', 'onload', 'onchange', 'onsubmit', 'onmouseover', 'onmouseout'];

        eventAttrs.forEach(attr => {
            if (element.hasAttribute(attr)) {
                listeners.push(attr);
            }
        });

        return listeners;
    }

    private getParentChain(element: Element): string[] {
        const chain: string[] = [];
        let current = element.parentElement;
        let depth = 0;

        while (current && depth < 5) {
            chain.push(this.buildCSSSelector(current));
            current = current.parentElement;
            depth++;
        }

        return chain;
    }

    private getAppliedStylesheets(): string[] {
        const sheets: string[] = [];

        for (let i = 0; i < document.styleSheets.length; i++) {
            try {
                const sheet = document.styleSheets[i];
                if (sheet.href) {
                    sheets.push(sheet.href);
                } else if (sheet.ownerNode) {
                    sheets.push('<inline style>');
                }
            } catch (e) {
                // CORS restrictions might prevent access
                sheets.push('<cross-origin stylesheet>');
            }
        }

        return sheets;
    }

    private getMatchingCSSRules(element: Element): any[] {
        const matchingRules: any[] = [];

        for (let i = 0; i < document.styleSheets.length; i++) {
            try {
                const sheet = document.styleSheets[i];
                if (!sheet.cssRules) continue;

                for (let j = 0; j < sheet.cssRules.length; j++) {
                    const rule = sheet.cssRules[j];

                    if (rule instanceof CSSStyleRule) {
                        // Check if this rule's selector matches our element
                        try {
                            if (element.matches(rule.selectorText)) {
                                matchingRules.push({
                                    selector: rule.selectorText,
                                    cssText: rule.cssText.substring(0, 200) + (rule.cssText.length > 200 ? '...' : ''),
                                    source: sheet.href || '<inline style>',
                                    // Note: Can't get exact line number without DevTools API
                                    // but we can show the rule index
                                    ruleIndex: j,
                                });
                            }
                        } catch (e) {
                            // Invalid selector or other error
                        }
                    }
                }
            } catch (e) {
                // CORS or other restrictions
            }
        }

        return matchingRules;
    }

    private formatDebugInfoForAI(info: any): string {
        return `# Element Debug Information

## Page Context
- URL: ${info.url}
- Timestamp: ${info.timestamp}

## Element Identification
- Tag: <${info.element.tag}>
- ID: ${info.element.id || 'none'}
- Classes: ${info.element.classes.join(', ') || 'none'}
- CSS Selector: ${info.element.selector}
- XPath: ${info.element.xpath}

## Attributes
${Object.entries(info.attributes).map(([key, value]) => `- ${key}: ${value}`).join('\n')}

## Computed Styles
${Object.entries(info.styles || {}).map(([key, value]) => `- ${key}: ${value}`).join('\n')}

${info.inlineStyles ? `## Inline Styles\n${info.inlineStyles}\n` : ''}

## Dimensions & Position
- Width: ${info.dimensions?.width}px
- Height: ${info.dimensions?.height}px
- Top: ${info.dimensions?.top}px
- Left: ${info.dimensions?.left}px

## Scroll State
- scrollTop: ${info.scroll?.scrollTop}
- scrollLeft: ${info.scroll?.scrollLeft}

## Content (truncated)
${info.content?.textContent || 'none'}

## Event Listeners
${info.eventListeners.length > 0 ? info.eventListeners.join(', ') : 'none detected'}

## Parent Chain
${info.parentChain.map((p: string, i: number) => `${i + 1}. ${p}`).join('\n')}

## Applied Stylesheets
${info.appliedStylesheets.slice(0, 10).map((s: string, i: number) => `${i + 1}. ${s}`).join('\n')}

## Matching CSS Rules (${info.matchingCSSRules?.length || 0} rules)
${info.matchingCSSRules && info.matchingCSSRules.length > 0 ? info.matchingCSSRules.slice(0, 10).map((rule: any, i: number) => `
### ${i + 1}. ${rule.selector}
- Source: ${rule.source}
- Rule Index: ${rule.ruleIndex}
- CSS: ${rule.cssText}
`).join('\n') : 'No matching rules found (may be due to CORS restrictions)'}

---
This debug information was captured by Element Inspector and can be used for AI-assisted debugging.
Note: Exact CSS line numbers require browser DevTools API access.
`;
    }

    public refresh(): void {
        if (this.isActive) {
            this.deactivate();
            this.activate();
        }
    }

    private async copyPageStructure(): Promise<void> {
        console.log('[ElementInspector] Generating full page structure...');

        // Show camera shutter effect first
        this.showCameraFlash();

        const structure = this.generatePageStructure();

        try {
            await navigator.clipboard.writeText(structure);
            console.log('[ElementInspector] Page structure copied to clipboard!');

            // Show notification after flash
            setTimeout(() => {
                this.showNotification('📸 Page Structure Captured & Copied!', 'success');
            }, 300);
        } catch (err) {
            console.error('[ElementInspector] Failed to copy page structure:', err);
            this.showNotification('✗ Copy Failed', 'error');
        }
    }

    private generatePageStructure(): string {
        const info: any = {
            url: window.location.href,
            timestamp: new Date().toISOString(),
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight,
                scrollX: window.scrollX,
                scrollY: window.scrollY,
            },
            document: {
                title: document.title,
                doctype: document.doctype ? document.doctype.name : 'none',
                characterSet: document.characterSet,
                readyState: document.readyState,
            },
        };

        // Build element tree
        info.structure = this.buildElementTree(document.body, 0, 10); // Max depth 10

        // List all stylesheets
        info.stylesheets = this.getAllStylesheets();

        // List all scripts
        info.scripts = this.getAllScripts();

        return this.formatPageStructureForAI(info);
    }

    private buildElementTree(element: Element, depth: number, maxDepth: number): any {
        if (depth > maxDepth) {
            return { truncated: true };
        }

        const className = typeof element.className === 'string' ? element.className : '';
        const node: any = {
            tag: element.tagName.toLowerCase(),
            id: element.id || undefined,
            classes: className ? className.split(/\s+/).filter(c => c) : undefined,
        };

        // Add important attributes
        const importantAttrs = ['href', 'src', 'type', 'name', 'value', 'data-*', 'aria-*'];
        const attrs: any = {};
        for (let i = 0; i < element.attributes.length; i++) {
            const attr = element.attributes[i];
            if (importantAttrs.some(pattern => {
                if (pattern.endsWith('*')) {
                    return attr.name.startsWith(pattern.slice(0, -1));
                }
                return attr.name === pattern;
            })) {
                attrs[attr.name] = attr.value;
            }
        }
        if (Object.keys(attrs).length > 0) {
            node.attributes = attrs;
        }

        // Add children
        const children: any[] = [];
        for (let i = 0; i < element.children.length; i++) {
            const child = element.children[i];
            // Skip script and style tags in structure
            if (child.tagName !== 'SCRIPT' && child.tagName !== 'STYLE') {
                children.push(this.buildElementTree(child, depth + 1, maxDepth));
            }
        }
        if (children.length > 0) {
            node.children = children;
        }

        return node;
    }

    private getAllStylesheets(): any[] {
        const sheets: any[] = [];

        for (let i = 0; i < document.styleSheets.length; i++) {
            try {
                const sheet = document.styleSheets[i];
                const sheetInfo: any = {
                    index: i,
                    href: sheet.href || '<inline>',
                    ruleCount: sheet.cssRules?.length || 0,
                };

                // Try to get some sample rules
                if (sheet.cssRules && sheet.cssRules.length > 0) {
                    const sampleRules: string[] = [];
                    for (let j = 0; j < Math.min(5, sheet.cssRules.length); j++) {
                        sampleRules.push(sheet.cssRules[j].cssText);
                    }
                    sheetInfo.sampleRules = sampleRules;
                }

                sheets.push(sheetInfo);
            } catch (e) {
                sheets.push({
                    index: i,
                    href: '<cross-origin or restricted>',
                    error: 'Cannot access due to CORS',
                });
            }
        }

        return sheets;
    }

    private getAllScripts(): any[] {
        const scripts: any[] = [];
        const scriptElements = document.querySelectorAll('script');

        scriptElements.forEach((script, index) => {
            scripts.push({
                index,
                src: script.src || '<inline>',
                type: script.type || 'text/javascript',
                async: script.async,
                defer: script.defer,
            });
        });

        return scripts;
    }

    private formatPageStructureForAI(info: any): string {
        return `# Full Page Structure

## Page Information
- URL: ${info.url}
- Title: ${info.document.title}
- Timestamp: ${info.timestamp}
- Viewport: ${info.viewport.width}x${info.viewport.height}
- Scroll Position: (${info.viewport.scrollX}, ${info.viewport.scrollY})

## Document Structure
\`\`\`json
${JSON.stringify(info.structure, null, 2)}
\`\`\`

## Stylesheets (${info.stylesheets.length} total)
${info.stylesheets.map((s: any, i: number) => `
### ${i + 1}. ${s.href}
- Rules: ${s.ruleCount}
${s.sampleRules ? `- Sample Rules:\n${s.sampleRules.map((r: string) => `  - ${r.substring(0, 100)}...`).join('\n')}` : ''}
${s.error ? `- Error: ${s.error}` : ''}
`).join('\n')}

## Scripts (${info.scripts.length} total)
${info.scripts.map((s: any, i: number) => `${i + 1}. ${s.src} ${s.async ? '[async]' : ''} ${s.defer ? '[defer]' : ''}`).join('\n')}

---
Generated by Element Inspector - Full page structure for AI-assisted debugging.
Press Alt+I to toggle element inspector overlay.
`;
    }

    private showNotification(message: string, type: 'success' | 'error'): void {
        const notification = document.createElement('div');
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 24px;
            background: ${type === 'success' ? 'rgba(16, 185, 129, 0.95)' : 'rgba(239, 68, 68, 0.95)'};
            color: white;
            border-radius: 6px;
            font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
            font-size: 14px;
            font-weight: bold;
            z-index: 10000000;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }

    private showCameraFlash(): void {
        const flash = document.createElement('div');
        flash.className = 'camera-flash';
        document.body.appendChild(flash);

        // Play camera shutter sound if available (optional)
        try {
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGnuTvuWkcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGnuTvuWkcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGnuTvuWkcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGnuTvuWkcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGnuTvuWkcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGnuTvuWkcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGnuTvuWkcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGnuTvuWkcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGnuTvuQ==');
            audio.volume = 0.3;
            audio.play().catch(() => {
                // Ignore if audio play fails (autoplay policy)
            });
        } catch (e) {
            // Silently ignore audio errors
        }

        // Remove flash element after animation
        setTimeout(() => {
            flash.remove();
        }, 500);
    }

    private startSelectionMode(): void {
        this.selectionMode = true;

        // Add class to body to force crosshair cursor on all elements
        document.body.classList.add('element-inspector-selection-mode');

        // Activate element visualization if not already active
        if (!this.isActive) {
            this.activate();
        }

        // Create overlay immediately (on top of element visualization)
        this.selectionOverlay = document.createElement('div');
        this.selectionOverlay.className = 'selection-overlay';
        document.body.appendChild(this.selectionOverlay);

        this.showNotification('🔲 Selection Mode: Click and drag to select area (Esc to cancel)', 'success');

        // Add mouse event listeners
        document.addEventListener('mousedown', this.onSelectionMouseDown);
        document.addEventListener('mousemove', this.onSelectionMouseMove);
        document.addEventListener('mouseup', this.onSelectionMouseUp);
    }

    private cancelSelectionMode(): void {
        this.selectionMode = false;

        // Remove class from body to restore normal cursors
        document.body.classList.remove('element-inspector-selection-mode');

        // Clear selection highlights
        this.clearSelectionHighlights();

        // Remove overlay
        if (this.selectionOverlay) {
            this.selectionOverlay.remove();
            this.selectionOverlay = null;
        }

        // Remove selection rectangle if exists
        if (this.selectionRect) {
            this.selectionRect.remove();
            this.selectionRect = null;
        }

        // Remove event listeners
        document.removeEventListener('mousedown', this.onSelectionMouseDown);
        document.removeEventListener('mousemove', this.onSelectionMouseMove);
        document.removeEventListener('mouseup', this.onSelectionMouseUp);

        this.selectionStart = null;
    }

    private onSelectionMouseDown = (e: MouseEvent): void => {
        if (!this.selectionMode) return;

        e.preventDefault();
        this.selectionStart = {
            x: e.clientX,
            y: e.clientY
        };

        // Create simple selection rectangle
        this.selectionRect = document.createElement('div');
        this.selectionRect.className = 'selection-rectangle';
        this.selectionRect.style.left = `${e.clientX}px`;
        this.selectionRect.style.top = `${e.clientY}px`;
        this.selectionRect.style.width = '0px';
        this.selectionRect.style.height = '0px';

        document.body.appendChild(this.selectionRect);
    };

    private onSelectionMouseMove = (e: MouseEvent): void => {
        if (!this.selectionMode || !this.selectionStart || !this.selectionRect) {
            return;
        }

        e.preventDefault();

        const currentX = e.clientX;
        const currentY = e.clientY;

        const left = Math.min(this.selectionStart.x, currentX);
        const top = Math.min(this.selectionStart.y, currentY);
        const width = Math.abs(currentX - this.selectionStart.x);
        const height = Math.abs(currentY - this.selectionStart.y);

        this.selectionRect.style.left = `${left}px`;
        this.selectionRect.style.top = `${top}px`;
        this.selectionRect.style.width = `${width}px`;
        this.selectionRect.style.height = `${height}px`;

        // Highlight elements that intersect with current selection
        this.updateSelectionHighlights({ left, top, width, height });
    };

    private onSelectionMouseUp = async (e: MouseEvent): Promise<void> => {
        if (!this.selectionMode || !this.selectionStart || !this.selectionRect) return;

        e.preventDefault();

        const currentX = e.clientX;
        const currentY = e.clientY;

        const left = Math.min(this.selectionStart.x, currentX);
        const top = Math.min(this.selectionStart.y, currentY);
        const width = Math.abs(currentX - this.selectionStart.x);
        const height = Math.abs(currentY - this.selectionStart.y);

        // Only proceed if selection is large enough
        if (width < 5 || height < 5) {
            this.cancelSelectionMode();
            this.showNotification('⚠ Selection too small', 'error');
            return;
        }

        // Find all elements in the selected area
        const selectedElements = this.findElementsInRect({
            left,
            top,
            width,
            height
        });

        console.log(`[ElementInspector] Found ${selectedElements.length} elements in selection`);

        // Gather info from all selected elements
        const selectionInfo = this.gatherSelectionInfo(selectedElements, {
            left,
            top,
            width,
            height
        });

        // Copy to clipboard
        try {
            await navigator.clipboard.writeText(selectionInfo);
            this.showNotification(`✓ Copied info for ${selectedElements.length} elements!`, 'success');
            console.log('[ElementInspector] Selection info copied to clipboard');
        } catch (err) {
            console.error('[ElementInspector] Failed to copy:', err);
            this.showNotification('✗ Copy Failed', 'error');
        }

        // Clean up (will also clear highlights)
        this.cancelSelectionMode();
    };

    private updateSelectionHighlights(rect: { left: number; top: number; width: number; height: number }): void {
        // Find elements that are completely inside selection
        const selectedElements = this.findElementsInRect(rect);
        const newSelection = new Set(selectedElements);

        // Track which boxes to highlight
        const selectedBoxes = new Set<HTMLDivElement>();

        // Find corresponding boxes and highlight them
        this.elementBoxMap.forEach((element, box) => {
            if (newSelection.has(element)) {
                selectedBoxes.add(box);
            }
        });

        // Remove highlights from boxes no longer in selection
        this.elementBoxMap.forEach((element, box) => {
            if (this.currentlySelectedElements.has(element) && !newSelection.has(element)) {
                // Remove box highlight
                box.style.borderWidth = '2px';
                box.style.background = 'rgba(255, 255, 255, 0.01)';
                box.style.transform = '';
                box.style.zIndex = '';

                // Remove element highlight
                if (element instanceof HTMLElement) {
                    element.classList.remove('element-inspector-selected');
                }
            }
        });

        // Add highlights to newly selected boxes
        selectedBoxes.forEach(box => {
            const element = this.elementBoxMap.get(box);
            if (element && !this.currentlySelectedElements.has(element)) {
                // Get depth-based color
                const depth = this.getDepth(element);
                const color = this.getColorForDepth(depth);

                // Highlight the box more prominently
                box.style.borderWidth = '4px';
                box.style.background = this.hexToRgba(color, 0.25);
                box.style.transform = 'scale(1.02)';
                box.style.zIndex = '1000000';

                // Also mark the element
                if (element instanceof HTMLElement) {
                    element.classList.add('element-inspector-selected');
                }
            }
        });

        // Update tracked selection
        this.currentlySelectedElements = newSelection;
    }

    private clearSelectionHighlights(): void {
        // Reset boxes to normal state
        this.elementBoxMap.forEach((element, box) => {
            if (this.currentlySelectedElements.has(element)) {
                box.style.borderWidth = '2px';
                box.style.background = 'rgba(255, 255, 255, 0.01)';
                box.style.transform = '';
                box.style.zIndex = '';
            }
        });

        // Clear element classes
        this.currentlySelectedElements.forEach(element => {
            if (element instanceof HTMLElement) {
                element.classList.remove('element-inspector-selected');
            }
        });
        this.currentlySelectedElements.clear();
    }

    private hexToRgba(hex: string, alpha: number): string {
        // Convert hex to RGB
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        if (!result) return `rgba(59, 130, 246, ${alpha})`; // fallback to blue

        const r = parseInt(result[1], 16);
        const g = parseInt(result[2], 16);
        const b = parseInt(result[3], 16);

        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    private findElementsInRect(rect: { left: number; top: number; width: number; height: number }): Element[] {
        const selectedElements: Element[] = [];
        const allElements = document.querySelectorAll('*');

        // Selection rect is in viewport coordinates (fixed position)
        const selectionRect = {
            left: rect.left,
            top: rect.top,
            right: rect.left + rect.width,
            bottom: rect.top + rect.height
        };

        allElements.forEach((element: Element) => {
            // Skip our own inspector elements
            if (element.closest('#element-inspector-overlay') ||
                element.classList.contains('selection-rectangle') ||
                element.classList.contains('selection-overlay')) {
                return;
            }

            // Skip invisible elements
            if (element instanceof HTMLElement) {
                const computed = window.getComputedStyle(element);
                if (computed.display === 'none' || computed.visibility === 'hidden') {
                    return;
                }
            }

            // Element bounds in viewport coordinates (getBoundingClientRect is already viewport-relative)
            const elementRect = element.getBoundingClientRect();
            const elementBounds = {
                left: elementRect.left,
                top: elementRect.top,
                right: elementRect.right,
                bottom: elementRect.bottom
            };

            // Check if element intersects with selection
            const intersects = !(
                elementBounds.right < selectionRect.left ||
                elementBounds.left > selectionRect.right ||
                elementBounds.bottom < selectionRect.top ||
                elementBounds.top > selectionRect.bottom
            );

            if (intersects) {
                selectedElements.push(element);
            }
        });

        return selectedElements;
    }

    private gatherSelectionInfo(elements: Element[], rect: { left: number; top: number; width: number; height: number }): string {
        let info = `# Rectangle Selection Debug Information

## Selection Area
- Position: (${Math.round(rect.left)}, ${Math.round(rect.top)})
- Size: ${Math.round(rect.width)}×${Math.round(rect.height)}px
- URL: ${window.location.href}
- Timestamp: ${new Date().toISOString()}
- Elements Found: ${elements.length}

---

`;

        // Add summary of element types
        const elementTypes: { [key: string]: number } = {};
        elements.forEach(el => {
            const tag = el.tagName.toLowerCase();
            elementTypes[tag] = (elementTypes[tag] || 0) + 1;
        });

        info += `## Element Type Summary\n`;
        Object.entries(elementTypes)
            .sort((a, b) => b[1] - a[1])
            .forEach(([tag, count]) => {
                info += `- ${tag}: ${count}\n`;
            });

        info += `\n---\n\n`;

        // Provide comprehensive debug info for each element
        const maxDetailedElements = 20; // Limit detailed info to avoid huge output
        const detailedCount = Math.min(elements.length, maxDetailedElements);

        info += `## Detailed Element Information (${detailedCount} of ${elements.length} elements)\n\n`;
        info += `> **Note**: Showing comprehensive debug info for the first ${detailedCount} elements.\n`;
        info += `> Each element includes: attributes, computed styles, dimensions, matching CSS rules, etc.\n\n`;
        info += `---\n\n`;

        // Add comprehensive info for first N elements
        elements.slice(0, maxDetailedElements).forEach((element, index) => {
            info += `# Element ${index + 1}/${elements.length}\n\n`;

            // Use the same comprehensive gathering as single element click
            const elementDebugInfo = this.gatherElementDebugInfoForSelection(element, index + 1);
            info += elementDebugInfo;
            info += `\n${'='.repeat(80)}\n\n`;
        });

        // Add basic summary for remaining elements
        if (elements.length > maxDetailedElements) {
            info += `## Remaining Elements (${elements.length - maxDetailedElements} elements - basic info)\n\n`;

            elements.slice(maxDetailedElements).forEach((element, index) => {
                const actualIndex = maxDetailedElements + index + 1;
                const selector = this.buildCSSSelector(element);
                const rect = element.getBoundingClientRect();
                const text = element.textContent?.trim().substring(0, 50);

                info += `### ${actualIndex}. ${selector}\n`;
                info += `- Position: (${Math.round(rect.left)}, ${Math.round(rect.top)}) | Size: ${Math.round(rect.width)}×${Math.round(rect.height)}px\n`;
                if (text) info += `- Text: "${text}${text.length > 50 ? '...' : ''}"\n`;
                info += `\n`;
            });
        }

        info += `\n---\nGenerated by Element Inspector - Rectangle Selection Mode (Enhanced)\n`;
        info += `Press Ctrl+Alt+I to start selection mode again.\n`;

        return info;
    }

    private gatherElementDebugInfoForSelection(element: Element, elementNumber: number): string {
        const info: any = {};

        // Element Identification
        const className = typeof element.className === 'string' ? element.className : '';
        info.element = {
            number: elementNumber,
            tag: element.tagName.toLowerCase(),
            id: element.id || null,
            classes: className ? className.split(/\s+/).filter(c => c) : [],
            selector: this.buildCSSSelector(element),
            xpath: this.getXPath(element),
        };

        // Attributes
        info.attributes = {};
        for (let i = 0; i < element.attributes.length; i++) {
            const attr = element.attributes[i];
            info.attributes[attr.name] = attr.value;
        }

        // Get computed styles (important ones)
        if (element instanceof HTMLElement) {
            const computed = window.getComputedStyle(element);
            info.styles = {
                display: computed.display,
                position: computed.position,
                width: computed.width,
                height: computed.height,
                margin: computed.margin,
                padding: computed.padding,
                backgroundColor: computed.backgroundColor,
                color: computed.color,
                fontSize: computed.fontSize,
                fontFamily: computed.fontFamily,
                zIndex: computed.zIndex,
                opacity: computed.opacity,
                visibility: computed.visibility,
                overflow: computed.overflow,
            };

            // Inline styles
            if (element.style.cssText) {
                info.inlineStyles = element.style.cssText;
            }

            // Dimensions and position
            const rect = element.getBoundingClientRect();
            info.dimensions = {
                width: rect.width,
                height: rect.height,
                top: rect.top,
                left: rect.left,
                bottom: rect.bottom,
                right: rect.right,
            };

            // Content (truncated)
            const textContent = element.textContent?.trim() || '';
            info.content = {
                textLength: textContent.length,
                textPreview: textContent.substring(0, 150) + (textContent.length > 150 ? '...' : ''),
            };
        }

        // Event listeners (simplified)
        info.eventListeners = this.getEventListeners(element);

        // Parent chain (shorter for selection mode)
        const parentChain: string[] = [];
        let current = element.parentElement;
        let depth = 0;
        while (current && depth < 3) {
            parentChain.push(this.buildCSSSelector(current));
            current = current.parentElement;
            depth++;
        }
        info.parentChain = parentChain;

        // Matching CSS rules
        info.matchingCSSRules = this.getMatchingCSSRules(element);

        // Format as readable text
        return this.formatSelectionElementForAI(info);
    }

    private formatSelectionElementForAI(info: any): string {
        return `## Element Identification
- Tag: <${info.element.tag}>
- ID: ${info.element.id || 'none'}
- Classes: ${info.element.classes.join(', ') || 'none'}
- CSS Selector: ${info.element.selector}
- XPath: ${info.element.xpath}

## Attributes
${Object.entries(info.attributes).length > 0 ? Object.entries(info.attributes).map(([key, value]) => `- ${key}: ${value}`).join('\n') : 'No attributes'}

## Computed Styles
${Object.entries(info.styles || {}).map(([key, value]) => `- ${key}: ${value}`).join('\n')}

${info.inlineStyles ? `## Inline Styles\n${info.inlineStyles}\n` : ''}

## Dimensions & Position
- Width: ${info.dimensions?.width}px, Height: ${info.dimensions?.height}px
- Top: ${info.dimensions?.top}px, Left: ${info.dimensions?.left}px

## Content
- Text Length: ${info.content?.textLength || 0} characters
- Preview: ${info.content?.textPreview || 'empty'}

## Event Listeners
${info.eventListeners.length > 0 ? info.eventListeners.join(', ') : 'none detected'}

## Parent Chain (3 levels)
${info.parentChain.length > 0 ? info.parentChain.map((p: string, i: number) => `${i + 1}. ${p}`).join('\n') : 'At document root'}

## Matching CSS Rules (${info.matchingCSSRules?.length || 0} rules)
${info.matchingCSSRules && info.matchingCSSRules.length > 0 ? info.matchingCSSRules.slice(0, 5).map((rule: any, i: number) => `
### ${i + 1}. ${rule.selector}
- Source: ${rule.source}
- Rule Index: ${rule.ruleIndex}
- CSS: ${rule.cssText}
`).join('\n') : 'No matching rules found'}
`;
    }

    private findOverlappingBoxesAtPoint(clientX: number, clientY: number): HTMLDivElement[] {
        const overlapping: HTMLDivElement[] = [];

        this.elementBoxMap.forEach((_element, box) => {
            const rect = box.getBoundingClientRect();

            // Check if click point is inside this box
            if (clientX >= rect.left && clientX <= rect.right &&
                clientY >= rect.top && clientY <= rect.bottom) {
                overlapping.push(box);
            }
        });

        // Sort by element depth (deeper nesting = higher priority/shown first)
        overlapping.sort((a, b) => {
            const elemA = this.elementBoxMap.get(a)!;
            const elemB = this.elementBoxMap.get(b)!;

            const depthA = this.getDepth(elemA);
            const depthB = this.getDepth(elemB);

            // Deeper elements (more nested) come first
            return depthB - depthA;
        });

        return overlapping;
    }

    // @ts-ignore - Reserved for future use
    private _showLayerPicker(boxes: HTMLDivElement[], x: number, y: number): void {
        // Close existing picker
        this.closeLayerPicker();

        // Create layer picker menu
        this.layerPickerMenu = document.createElement('div');
        this.layerPickerMenu.className = 'layer-picker-menu';
        this.layerPickerMenu.style.left = `${x + window.scrollX}px`;
        this.layerPickerMenu.style.top = `${y + window.scrollY}px`;

        // Add header
        const header = document.createElement('div');
        header.className = 'layer-picker-header';
        header.textContent = `Select Element (${boxes.length} layers)`;
        this.layerPickerMenu.appendChild(header);

        // Add items for each layer
        boxes.forEach((box, index) => {
            const element = this.elementBoxMap.get(box);
            if (!element) return;

            const item = document.createElement('div');
            item.className = 'layer-picker-item';

            // @ts-ignore - Reserved for future use
            const _depth = this.getDepth(element);
            const tag = element.tagName.toLowerCase();
            const id = element.id;
            const classes = element.className;

            // Build label
            let label = '';
            label += `<span class="layer-picker-depth">L${index + 1}</span>`;
            label += `<span class="layer-picker-tag">${tag}</span>`;
            if (id) {
                label += ` <span class="layer-picker-id">#${id}</span>`;
            }
            if (classes && typeof classes === 'string') {
                const classList = classes.split(/\s+/).filter(c => c).slice(0, 2);
                if (classList.length > 0) {
                    label += ` <span class="layer-picker-class">.${classList.join('.')}</span>`;
                }
            }

            item.innerHTML = label;

            // Highlight on hover
            item.addEventListener('mouseenter', () => {
                // Remove all highlights
                boxes.forEach(b => b.classList.remove('highlighted'));
                // Highlight this one
                box.classList.add('highlighted');
            });

            item.addEventListener('mouseleave', () => {
                box.classList.remove('highlighted');
            });

            // Click to copy
            item.addEventListener('click', async (e: MouseEvent) => {
                e.stopPropagation();

                box.classList.add('highlighted');
                this.closeLayerPicker();

                const debugInfo = this.gatherElementDebugInfo(element);
                try {
                    await navigator.clipboard.writeText(debugInfo);
                    this.showNotification('✓ Element Info Copied!', 'success');

                    setTimeout(() => {
                        box.classList.remove('highlighted');
                    }, 2000);
                } catch (err) {
                    this.showNotification('✗ Copy Failed', 'error');
                    box.classList.remove('highlighted');
                }
            });

            this.layerPickerMenu!.appendChild(item);
        });

        document.body.appendChild(this.layerPickerMenu);

        // Close picker on click outside
        setTimeout(() => {
            document.addEventListener('click', this.onDocumentClickForLayerPicker);
        }, 100);
    }

    private onDocumentClickForLayerPicker = (e: MouseEvent): void => {
        if (this.layerPickerMenu && !this.layerPickerMenu.contains(e.target as Node)) {
            this.closeLayerPicker();
        }
    };

    private closeLayerPicker(): void {
        if (this.layerPickerMenu) {
            this.layerPickerMenu.remove();
            this.layerPickerMenu = null;
            document.removeEventListener('click', this.onDocumentClickForLayerPicker);

            // Remove all highlights
            this.elementBoxMap.forEach((_element, box) => {
                box.classList.remove('highlighted');
            });
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
