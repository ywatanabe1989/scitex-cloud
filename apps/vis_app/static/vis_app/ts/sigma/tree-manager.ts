/**
 * Tree Manager for Hierarchical Figure/Axes/Plots structure
 */

import type { Figure, Axis, Plot, Guide, Annotation } from './types.js';

export class TreeManager {
    private treeContainer: HTMLElement | null = null;
    private readonly STORAGE_KEY = 'sigma-tree-expanded-state';

    constructor() {
        this.initialize();
    }

    /**
     * Initialize tree interactions
     */
    private initialize(): void {
        this.treeContainer = document.getElementById('figures-tree');
        if (!this.treeContainer) {
            console.warn('[TreeManager] Tree container not found');
            return;
        }

        this.setupTreeToggles();
        this.setupTreeActions();
        this.setupTreeSelection();
        console.log('[TreeManager] Initialized');
    }

    /**
     * Setup tree item selection
     */
    private setupTreeSelection(): void {
        if (!this.treeContainer) return;

        // Handle tree item clicks for selection
        this.treeContainer.addEventListener('click', (e) => {
            const target = e.target as HTMLElement;

            // Check if clicked on tree item (not on action buttons or toggles)
            if (target.closest('.tree-action-btn, .tree-add-btn, .tree-toggle')) {
                return; // Ignore clicks on action buttons and toggles
            }

            const item = target.closest('.tree-item') as HTMLElement;
            if (item && item.hasAttribute('data-id')) {
                this.selectItem(item);
            }
        });
    }

    /**
     * Setup expand/collapse toggles for tree items
     */
    private setupTreeToggles(): void {
        if (!this.treeContainer) return;

        // Handle tree toggle clicks (chevrons)
        this.treeContainer.addEventListener('click', (e) => {
            const target = e.target as HTMLElement;
            
            // Check if clicked on toggle icon or header
            const toggle = target.closest('.tree-toggle') as HTMLElement;
            const header = target.closest('.tree-item-header, .tree-group-header') as HTMLElement;
            
            if (toggle || (header && !target.closest('.tree-action-btn, .tree-add-btn'))) {
                e.stopPropagation();
                const parent = header?.closest('.tree-item, .tree-group') as HTMLElement;
                if (parent) {
                    this.toggleTreeItem(parent);
                }
            }
        });
    }

    /**
     * Toggle expand/collapse state of a tree item
     */
    private toggleTreeItem(item: HTMLElement): void {
        const toggle = item.querySelector('.tree-toggle') as HTMLElement;
        const children = item.querySelector('.tree-item-children, .tree-group-children') as HTMLElement;

        if (!toggle || !children) return;

        const isExpanded = toggle.classList.contains('fa-chevron-down');
        const itemId = item.getAttribute('data-id');

        if (isExpanded) {
            // Collapse
            toggle.classList.remove('fa-chevron-down');
            toggle.classList.add('fa-chevron-right');
            children.style.display = 'none';

            // Save collapsed state
            if (itemId) {
                this.saveExpandedState(itemId, false);
            }
        } else {
            // Expand
            toggle.classList.remove('fa-chevron-right');
            toggle.classList.add('fa-chevron-down');
            children.style.display = 'block';

            // Save expanded state
            if (itemId) {
                this.saveExpandedState(itemId, true);
            }
        }

        console.log('[TreeManager] Tree item toggled');
    }

    /**
     * Setup action buttons (edit, delete, add)
     */
    private setupTreeActions(): void {
        if (!this.treeContainer) return;

        // Handle action button clicks
        this.treeContainer.addEventListener('click', (e) => {
            const target = e.target as HTMLElement;
            const btn = target.closest('.tree-action-btn, .tree-add-btn') as HTMLElement;
            
            if (btn) {
                e.stopPropagation();
                this.handleTreeAction(btn);
            }
        });
    }

    /**
     * Handle tree action button clicks
     */
    private handleTreeAction(btn: HTMLElement): void {
        const icon = btn.querySelector('i');
        const item = btn.closest('.tree-item, .tree-group, .tree-section') as HTMLElement;
        const label = item?.querySelector('.tree-label')?.textContent || 'item';

        if (!icon) return;

        if (icon.classList.contains('fa-edit')) {
            console.log('[TreeManager] Edit requested for:', label);
            this.editItem(item);
        } else if (icon.classList.contains('fa-trash')) {
            console.log('[TreeManager] Delete requested for:', label);
            this.deleteItem(item);
        } else if (icon.classList.contains('fa-plus')) {
            console.log('[TreeManager] Add requested in:', label);
            this.addItem(item);
        }
    }

    /**
     * Edit item
     */
    private editItem(item: HTMLElement): void {
        const label = item.querySelector('.tree-label')?.textContent || '';
        const itemId = item.getAttribute('data-id') || '';

        // Determine item type
        let itemType = 'item';
        if (item.classList.contains('tree-figure')) itemType = 'figure';
        else if (item.classList.contains('tree-axis')) itemType = 'axis';
        else if (item.classList.contains('tree-plot')) itemType = 'plot';
        else if (item.classList.contains('tree-guide')) itemType = 'guide';
        else if (item.classList.contains('tree-annotation')) itemType = 'annotation';

        console.log('[TreeManager] Edit requested:', { itemType, itemId, label });

        // Dispatch custom event for parent component to handle
        const editEvent = new CustomEvent('tree-item-edit', {
            detail: { itemType, itemId, label, element: item },
            bubbles: true
        });
        item.dispatchEvent(editEvent);
    }

    /**
     * Delete item
     */
    private deleteItem(item: HTMLElement): void {
        const label = item.querySelector('.tree-label')?.textContent || '';
        const itemId = item.getAttribute('data-id') || '';

        // Determine item type
        let itemType = 'item';
        if (item.classList.contains('tree-figure')) itemType = 'figure';
        else if (item.classList.contains('tree-axis')) itemType = 'axis';
        else if (item.classList.contains('tree-plot')) itemType = 'plot';
        else if (item.classList.contains('tree-guide')) itemType = 'guide';
        else if (item.classList.contains('tree-annotation')) itemType = 'annotation';

        if (confirm(`Delete ${itemType} "${label}"?\n\nThis action cannot be undone.`)) {
            console.log('[TreeManager] Delete requested:', { itemType, itemId, label });

            // Dispatch custom event for parent component to handle
            const deleteEvent = new CustomEvent('tree-item-delete', {
                detail: { itemType, itemId, label, element: item },
                bubbles: true
            });
            item.dispatchEvent(deleteEvent);

            // Remove from DOM (can be prevented by event handler if needed)
            item.remove();
        }
    }

    /**
     * Add item
     */
    private addItem(parent: HTMLElement): void {
        const label = parent.querySelector('.tree-label')?.textContent || 'section';
        const parentId = parent.getAttribute('data-id') || '';

        // Determine parent type and what can be added
        let parentType = 'section';
        let addableTypes: string[] = [];

        if (parent.classList.contains('tree-section')) {
            parentType = 'figures-section';
            addableTypes = ['figure'];
        } else if (parent.classList.contains('tree-figure')) {
            parentType = 'figure';
            addableTypes = ['axis'];
        } else if (parent.classList.contains('tree-axis')) {
            parentType = 'axis';
            addableTypes = ['plot', 'guide', 'annotation'];
        } else if (parent.classList.contains('tree-plots')) {
            parentType = 'plots-group';
            addableTypes = ['plot'];
        } else if (parent.classList.contains('tree-guides')) {
            parentType = 'guides-group';
            addableTypes = ['guide'];
        } else if (parent.classList.contains('tree-annotations')) {
            parentType = 'annotations-group';
            addableTypes = ['annotation'];
        }

        console.log('[TreeManager] Add requested:', { parentType, parentId, label, addableTypes });

        // Dispatch custom event for parent component to handle
        const addEvent = new CustomEvent('tree-item-add', {
            detail: { parentType, parentId, label, addableTypes, element: parent },
            bubbles: true
        });
        parent.dispatchEvent(addEvent);
    }

    /**
     * Select a tree item
     */
    public selectItem(item: HTMLElement): void {
        // Remove previous selection from any header
        const previousSelected = this.treeContainer?.querySelector('.tree-item-header.selected');
        previousSelected?.classList.remove('selected');

        // Add selection to the clicked item's header only
        const header = item.querySelector('.tree-item-header') as HTMLElement;
        if (header) {
            header.classList.add('selected');
        }

        const label = item.querySelector('.tree-label')?.textContent || '';
        const itemId = item.getAttribute('data-id') || '';

        console.log('[TreeManager] Selected:', label);

        // Dispatch selection event for canvas synchronization
        const selectEvent = new CustomEvent('tree-item-select', {
            detail: { itemId, label, element: item },
            bubbles: true
        });
        item.dispatchEvent(selectEvent);
    }

    /**
     * Select tree item by ID (for canvas → tree synchronization)
     */
    public selectItemById(itemId: string): void {
        if (!this.treeContainer) return;

        const item = this.treeContainer.querySelector(`[data-id="${itemId}"]`) as HTMLElement;
        if (item) {
            this.selectItem(item);

            // Expand parent nodes to make item visible
            this.expandParents(item);

            // Scroll into view
            item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    /**
     * Expand all parent nodes of an item
     */
    private expandParents(item: HTMLElement): void {
        let parent = item.parentElement;

        while (parent && parent !== this.treeContainer) {
            if (parent.classList.contains('tree-item-children') ||
                parent.classList.contains('tree-group-children')) {
                // Find the parent item/group
                const parentItem = parent.closest('.tree-item, .tree-group') as HTMLElement;
                if (parentItem) {
                    const toggle = parentItem.querySelector('.tree-toggle') as HTMLElement;
                    const children = parentItem.querySelector('.tree-item-children, .tree-group-children') as HTMLElement;

                    if (toggle && children && toggle.classList.contains('fa-chevron-right')) {
                        // Expand if collapsed
                        toggle.classList.remove('fa-chevron-right');
                        toggle.classList.add('fa-chevron-down');
                        children.style.display = 'block';
                    }
                }
            }
            parent = parent.parentElement;
        }
    }

    /**
     * Expand all tree items
     */
    public expandAll(): void {
        if (!this.treeContainer) return;

        const toggles = this.treeContainer.querySelectorAll('.tree-toggle.fa-chevron-right');
        toggles.forEach(toggle => {
            const parent = toggle.closest('.tree-item, .tree-group') as HTMLElement;
            if (parent) {
                this.toggleTreeItem(parent);
            }
        });

        console.log('[TreeManager] Expanded all items');
    }

    /**
     * Collapse all tree items
     */
    public collapseAll(): void {
        if (!this.treeContainer) return;

        const toggles = this.treeContainer.querySelectorAll('.tree-toggle.fa-chevron-down');
        toggles.forEach(toggle => {
            const parent = toggle.closest('.tree-item, .tree-group') as HTMLElement;
            if (parent) {
                this.toggleTreeItem(parent);
            }
        });

        console.log('[TreeManager] Collapsed all items');
    }

    /**
     * Build tree from data structure
     */
    public buildTree(figures: Figure[]): void {
        if (!this.treeContainer) {
            console.warn('[TreeManager] Cannot build tree: container not found');
            return;
        }

        console.log('[TreeManager] Building tree from data:', figures);

        // Clear existing tree
        this.treeContainer.innerHTML = '';

        // Build tree items for each figure
        figures.forEach(figure => {
            const figureElement = this.createFigureElement(figure);
            this.treeContainer!.appendChild(figureElement);
        });

        // Restore saved expanded/collapsed states
        this.restoreExpandedStates();

        console.log('[TreeManager] Tree built successfully');
    }

    /**
     * Create figure tree element
     */
    private createFigureElement(figure: Figure): HTMLElement {
        const figureDiv = document.createElement('div');
        figureDiv.className = 'tree-item tree-figure';
        figureDiv.setAttribute('data-level', '0');
        figureDiv.setAttribute('data-id', figure.id);

        // Figure header
        const header = document.createElement('div');
        header.className = 'tree-item-header';
        header.innerHTML = `
            <i class="fas fa-chevron-down tree-toggle"></i>
            <i class="fas fa-chart-area tree-icon tree-icon-figure"></i>
            <span class="tree-label">${this.escapeHtml(figure.label)} (${figure.axes.length} ${figure.axes.length === 1 ? 'Axis' : 'Axes'})</span>
            <div class="tree-item-actions">
                <button class="tree-action-btn" title="Edit figure properties"><i class="fas fa-edit"></i></button>
                <button class="tree-action-btn" title="Delete figure"><i class="fas fa-trash"></i></button>
            </div>
        `;

        // Figure children container
        const children = document.createElement('div');
        children.className = 'tree-item-children';

        // Add axes
        figure.axes.forEach(axis => {
            children.appendChild(this.createAxisElement(axis));
        });

        // Add "Add Axis" button
        children.appendChild(this.createAddButton('Add Axis', 'axis'));

        figureDiv.appendChild(header);
        figureDiv.appendChild(children);

        return figureDiv;
    }

    /**
     * Create axis tree element
     */
    private createAxisElement(axis: Axis): HTMLElement {
        const axisDiv = document.createElement('div');
        axisDiv.className = 'tree-item tree-axis';
        axisDiv.setAttribute('data-level', '1');
        axisDiv.setAttribute('data-id', axis.id);

        // Axis header
        const header = document.createElement('div');
        header.className = 'tree-item-header';
        header.innerHTML = `
            <i class="fas fa-chevron-down tree-toggle"></i>
            <i class="fas fa-crosshairs tree-icon tree-icon-axis"></i>
            <span class="tree-label">${this.escapeHtml(axis.label)}</span>
            <div class="tree-item-actions">
                <button class="tree-action-btn" title="Edit axis properties"><i class="fas fa-edit"></i></button>
                <button class="tree-action-btn" title="Delete axis"><i class="fas fa-trash"></i></button>
            </div>
        `;

        // Axis children container
        const children = document.createElement('div');
        children.className = 'tree-item-children';

        // Add axis labels section (Title, X, Y)
        if (axis.title || axis.xLabel || axis.yLabel) {
            children.appendChild(this.createAxisLabelsSection(axis));
        }

        // Add Plots group
        children.appendChild(this.createPlotsGroup(axis.plots));

        // Add Guides group
        children.appendChild(this.createGuidesGroup(axis.guides));

        // Add Annotations group
        children.appendChild(this.createAnnotationsGroup(axis.annotations));

        axisDiv.appendChild(header);
        axisDiv.appendChild(children);

        return axisDiv;
    }

    /**
     * Create axis labels section (Title, X, Y)
     */
    private createAxisLabelsSection(axis: Axis): HTMLElement {
        const section = document.createElement('div');
        section.className = 'tree-group';
        section.setAttribute('data-level', '2');
        section.innerHTML = `
            <div class="tree-group-header">
                <i class="fas fa-chevron-down tree-toggle"></i>
                <i class="fas fa-tags tree-icon"></i>
                <span class="tree-label">Labels</span>
            </div>
            <div class="tree-group-children">
                ${axis.title ? `<div class="tree-item" data-level="3">
                    <div class="tree-item-header">
                        <i class="fas fa-heading tree-icon"></i>
                        <span class="tree-label">Title: ${this.escapeHtml(axis.title)}</span>
                    </div>
                </div>` : ''}
                ${axis.xLabel ? `<div class="tree-item" data-level="3">
                    <div class="tree-item-header">
                        <i class="fas fa-long-arrow-alt-right tree-icon"></i>
                        <span class="tree-label">X: ${this.escapeHtml(axis.xLabel)}</span>
                    </div>
                </div>` : ''}
                ${axis.yLabel ? `<div class="tree-item" data-level="3">
                    <div class="tree-item-header">
                        <i class="fas fa-long-arrow-alt-up tree-icon"></i>
                        <span class="tree-label">Y: ${this.escapeHtml(axis.yLabel)}</span>
                    </div>
                </div>` : ''}
            </div>
        `;
        return section;
    }

    /**
     * Create plots group
     */
    private createPlotsGroup(plots: Plot[]): HTMLElement {
        const group = document.createElement('div');
        group.className = 'tree-group tree-plots';
        group.setAttribute('data-level', '2');

        const header = document.createElement('div');
        header.className = 'tree-group-header';
        header.innerHTML = `
            <i class="fas fa-chevron-down tree-toggle"></i>
            <i class="fas fa-chart-line tree-icon"></i>
            <span class="tree-label">Plots (${plots.length})</span>
            <button class="tree-add-btn" title="Add plot"><i class="fas fa-plus"></i></button>
        `;

        const children = document.createElement('div');
        children.className = 'tree-group-children';

        plots.forEach(plot => {
            children.appendChild(this.createPlotElement(plot));
        });

        group.appendChild(header);
        group.appendChild(children);

        return group;
    }

    /**
     * Create plot element
     */
    private createPlotElement(plot: Plot): HTMLElement {
        const plotDiv = document.createElement('div');
        plotDiv.className = 'tree-item tree-plot';
        plotDiv.setAttribute('data-level', '3');
        plotDiv.setAttribute('data-id', plot.id);

        // Determine plot icon based on type (more distinctive icons)
        const iconMap: { [key: string]: string } = {
            'line': 'fa-chart-line',
            'scatter': 'fa-circle',
            'box': 'fa-square',
            'bar': 'fa-chart-bar',
            'histogram': 'fa-chart-column'
        };

        const icon = iconMap[plot.type] || 'fa-chart-line';

        // Build label with plot details
        let label = `${plot.type.charAt(0).toUpperCase() + plot.type.slice(1)}: ${this.escapeHtml(plot.label)}`;
        if (plot.xColumn && plot.yColumn) {
            label += ` (${this.escapeHtml(plot.xColumn)} vs ${this.escapeHtml(plot.yColumn)})`;
        }

        plotDiv.innerHTML = `
            <div class="tree-item-header">
                <i class="fas ${icon} tree-icon"></i>
                <span class="tree-label">${label}</span>
                <div class="tree-item-actions">
                    <button class="tree-action-btn" title="Edit plot"><i class="fas fa-edit"></i></button>
                    <button class="tree-action-btn" title="Delete plot"><i class="fas fa-trash"></i></button>
                </div>
            </div>
        `;

        return plotDiv;
    }

    /**
     * Create guides group
     */
    private createGuidesGroup(guides: Guide[]): HTMLElement {
        const group = document.createElement('div');
        group.className = 'tree-group tree-guides';
        group.setAttribute('data-level', '2');

        const header = document.createElement('div');
        header.className = 'tree-group-header';
        header.innerHTML = `
            <i class="fas fa-chevron-down tree-toggle"></i>
            <i class="fas fa-compass tree-icon"></i>
            <span class="tree-label">Guides (${guides.length})</span>
            <button class="tree-add-btn" title="Add guide"><i class="fas fa-plus"></i></button>
        `;

        const children = document.createElement('div');
        children.className = 'tree-group-children';

        guides.forEach(guide => {
            children.appendChild(this.createGuideElement(guide));
        });

        group.appendChild(header);
        group.appendChild(children);

        return group;
    }

    /**
     * Create guide element
     */
    private createGuideElement(guide: Guide): HTMLElement {
        const guideDiv = document.createElement('div');
        guideDiv.className = 'tree-item tree-guide';
        guideDiv.setAttribute('data-level', '3');
        guideDiv.setAttribute('data-id', guide.id);

        const icon = guide.type === 'legend' ? 'fa-square-check' : 'fa-fill-drip';
        let label = `${guide.type.charAt(0).toUpperCase() + guide.type.slice(1)}: ${this.escapeHtml(guide.label)}`;

        if (guide.plots && guide.plots.length > 0) {
            label += ` (${guide.plots.length} ${guide.plots.length === 1 ? 'plot' : 'plots'})`;
        }

        guideDiv.innerHTML = `
            <div class="tree-item-header">
                <i class="fas ${icon} tree-icon"></i>
                <span class="tree-label">${label}</span>
                <div class="tree-item-actions">
                    <button class="tree-action-btn" title="Edit guide"><i class="fas fa-edit"></i></button>
                    <button class="tree-action-btn" title="Delete guide"><i class="fas fa-trash"></i></button>
                </div>
            </div>
        `;

        return guideDiv;
    }

    /**
     * Create annotations group
     */
    private createAnnotationsGroup(annotations: Annotation[]): HTMLElement {
        const group = document.createElement('div');
        group.className = 'tree-group tree-annotations';
        group.setAttribute('data-level', '2');

        const header = document.createElement('div');
        header.className = 'tree-group-header';
        header.innerHTML = `
            <i class="fas fa-chevron-down tree-toggle"></i>
            <i class="fas fa-sticky-note tree-icon"></i>
            <span class="tree-label">Annotations (${annotations.length})</span>
            <button class="tree-add-btn" title="Add annotation"><i class="fas fa-plus"></i></button>
        `;

        const children = document.createElement('div');
        children.className = 'tree-group-children';

        annotations.forEach(annotation => {
            children.appendChild(this.createAnnotationElement(annotation));
        });

        group.appendChild(header);
        group.appendChild(children);

        return group;
    }

    /**
     * Create annotation element
     */
    private createAnnotationElement(annotation: Annotation): HTMLElement {
        const annotDiv = document.createElement('div');
        annotDiv.className = 'tree-item tree-annotation';
        annotDiv.setAttribute('data-level', '3');
        annotDiv.setAttribute('data-id', annotation.id);

        const iconMap: { [key: string]: string } = {
            'text': 'fa-font',
            'scalebar': 'fa-ruler-horizontal',
            'arrow': 'fa-arrow-right'
        };

        const icon = iconMap[annotation.type] || 'fa-sticky-note';
        let label = `${annotation.type.charAt(0).toUpperCase() + annotation.type.slice(1)}`;

        if (annotation.content) {
            label += `: "${this.escapeHtml(annotation.content)}"`;
        } else {
            label += `: ${this.escapeHtml(annotation.label)}`;
        }

        annotDiv.innerHTML = `
            <div class="tree-item-header">
                <i class="fas ${icon} tree-icon"></i>
                <span class="tree-label">${label}</span>
                <div class="tree-item-actions">
                    <button class="tree-action-btn" title="Edit annotation"><i class="fas fa-edit"></i></button>
                    <button class="tree-action-btn" title="Delete annotation"><i class="fas fa-trash"></i></button>
                </div>
            </div>
        `;

        return annotDiv;
    }

    /**
     * Create "Add" button
     */
    private createAddButton(label: string, type: string): HTMLElement {
        const btn = document.createElement('button');
        btn.className = 'tree-add-btn tree-add-item';
        btn.setAttribute('data-type', type);
        btn.innerHTML = `<i class="fas fa-plus"></i> ${label}`;
        return btn;
    }

    /**
     * Escape HTML to prevent XSS
     */
    private escapeHtml(text: string): string {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Save expanded/collapsed state to localStorage
     */
    private saveExpandedState(itemId: string, isExpanded: boolean): void {
        try {
            const state = this.loadExpandedStates();
            state[itemId] = isExpanded;
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(state));
        } catch (e) {
            console.warn('[TreeManager] Failed to save expanded state:', e);
        }
    }

    /**
     * Load expanded states from localStorage
     */
    private loadExpandedStates(): { [key: string]: boolean } {
        try {
            const stored = localStorage.getItem(this.STORAGE_KEY);
            return stored ? JSON.parse(stored) : {};
        } catch (e) {
            console.warn('[TreeManager] Failed to load expanded states:', e);
            return {};
        }
    }

    /**
     * Restore expanded/collapsed states after building tree
     */
    private restoreExpandedStates(): void {
        if (!this.treeContainer) return;

        const states = this.loadExpandedStates();

        // Apply saved states to all items with IDs
        Object.entries(states).forEach(([itemId, isExpanded]) => {
            const item = this.treeContainer!.querySelector(`[data-id="${itemId}"]`) as HTMLElement;
            if (item) {
                const toggle = item.querySelector('.tree-toggle') as HTMLElement;
                const children = item.querySelector('.tree-item-children, .tree-group-children') as HTMLElement;

                if (toggle && children) {
                    if (isExpanded) {
                        // Expand
                        toggle.classList.remove('fa-chevron-right');
                        toggle.classList.add('fa-chevron-down');
                        children.style.display = 'block';
                    } else {
                        // Collapse
                        toggle.classList.remove('fa-chevron-down');
                        toggle.classList.add('fa-chevron-right');
                        children.style.display = 'none';
                    }
                }
            }
        });

        console.log('[TreeManager] Restored expanded states from localStorage');
    }

    /**
     * Clear saved tree state from localStorage
     */
    public clearSavedState(): void {
        try {
            localStorage.removeItem(this.STORAGE_KEY);
            console.log('[TreeManager] Cleared saved tree state');
        } catch (e) {
            console.warn('[TreeManager] Failed to clear saved state:', e);
        }
    }
}
