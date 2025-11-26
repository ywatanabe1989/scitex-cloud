/**
 * CanvasTabManager - Manages tabs for canvas/figures
 *
 * Responsibilities:
 * - Figure tab creation and management
 * - Tab switching between figures
 * - Tab close functionality
 * - Inline rename on double-click
 * - 1 tab = 1 figure
 */

export interface CanvasTab {
    id: string;
    figureName: string;
    isActive: boolean;
    canvasData?: any;
}

export class CanvasTabManager {
    private tabs: CanvasTab[] = [];
    private activeTabId: string | null = null;
    private onTabChange: ((tabId: string) => void) | null = null;
    private onTabClose: ((tabId: string) => void) | null = null;
    private onTabRename: ((tabId: string, newName: string) => void) | null = null;

    constructor() {
        this.initializeDefaultTab();
    }

    /**
     * Initialize with a default tab (Figure 1)
     */
    private initializeDefaultTab(): void {
        const defaultTab: CanvasTab = {
            id: 'default',
            figureName: 'Figure 1',
            isActive: true
        };
        this.tabs.push(defaultTab);
        this.activeTabId = 'default';
    }

    /**
     * Set callbacks
     */
    public setCallbacks(
        onTabChange: (tabId: string) => void,
        onTabClose: (tabId: string) => void,
        onTabRename: (tabId: string, newName: string) => void
    ): void {
        this.onTabChange = onTabChange;
        this.onTabClose = onTabClose;
        this.onTabRename = onTabRename;
    }

    /**
     * Create a new figure tab
     */
    public createTab(figureName?: string): string {
        const id = `canvas-tab-${Date.now()}`;

        // Auto-generate figure name if not provided
        const figName = figureName || `Figure ${this.tabs.length + 1}`;

        const newTab: CanvasTab = {
            id,
            figureName: figName,
            isActive: false
        };
        this.tabs.push(newTab);
        this.renderTabs();
        return id;
    }

    /**
     * Switch to a tab
     */
    public switchToTab(tabId: string): void {
        const tab = this.tabs.find(t => t.id === tabId);
        if (!tab) return;

        this.tabs.forEach(t => t.isActive = false);
        tab.isActive = true;
        this.activeTabId = tabId;
        this.renderTabs();

        if (this.onTabChange) {
            this.onTabChange(tabId);
        }
    }

    /**
     * Close a tab
     */
    public closeTab(tabId: string): void {
        const index = this.tabs.findIndex(t => t.id === tabId);
        if (index === -1) return;

        // Don't close if it's the only tab
        if (this.tabs.length === 1) return;

        this.tabs.splice(index, 1);

        // If closing active tab, switch to another
        if (this.activeTabId === tabId) {
            const newActiveIndex = Math.min(index, this.tabs.length - 1);
            this.switchToTab(this.tabs[newActiveIndex].id);
        } else {
            this.renderTabs();
        }

        if (this.onTabClose) {
            this.onTabClose(tabId);
        }
    }

    /**
     * Rename a tab
     */
    public renameTab(tabId: string, newName: string): void {
        const tab = this.tabs.find(t => t.id === tabId);
        if (!tab) return;

        tab.figureName = newName;
        this.renderTabs();

        if (this.onTabRename) {
            this.onTabRename(tabId, newName);
        }
    }

    /**
     * Render tabs in the container
     */
    public renderTabs(): void {
        const container = document.getElementById('canvas-tabs-container');
        if (!container) return;

        // Save the + button element before clearing
        const plusBtn = container.querySelector('.data-tab-new');

        container.innerHTML = '';

        this.tabs.forEach(tab => {
            const tabElement = this.createTabElement(tab);
            container.appendChild(tabElement);
        });

        // Re-append the + button at the end
        if (plusBtn) {
            container.appendChild(plusBtn);
        }
    }

    /**
     * Create a tab element
     */
    private createTabElement(tab: CanvasTab): HTMLElement {
        const tabDiv = document.createElement('div');
        tabDiv.className = `data-tab${tab.isActive ? ' active' : ''}`;
        tabDiv.dataset.tabId = tab.id;
        tabDiv.title = tab.figureName;
        tabDiv.draggable = true;

        // Icon
        const icon = document.createElement('i');
        icon.className = 'fas fa-paint-brush';
        tabDiv.appendChild(icon);

        // Label
        const label = document.createElement('span');
        label.className = 'data-tab-label';
        label.textContent = tab.figureName;
        tabDiv.appendChild(label);

        // Close button
        const closeBtn = document.createElement('button');
        closeBtn.className = 'data-tab-close';
        closeBtn.title = 'Close tab';
        closeBtn.innerHTML = '&times;';
        closeBtn.onclick = (e) => {
            e.stopPropagation();
            this.closeTab(tab.id);
        };
        tabDiv.appendChild(closeBtn);

        // Click to switch
        tabDiv.onclick = () => {
            this.switchToTab(tab.id);
        };

        // Double-click to rename
        tabDiv.ondblclick = (e) => {
            e.preventDefault();
            this.startInlineRename(tabDiv, tab.id, label);
        };

        // Drag and drop handlers
        this.setupDragHandlers(tabDiv, tab.id);

        return tabDiv;
    }

    /**
     * Start inline rename
     */
    private startInlineRename(tabElement: HTMLElement, tabId: string, labelElement: HTMLElement): void {
        const currentName = labelElement.textContent || '';

        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'data-tab-rename-input';
        input.value = currentName;
        input.style.cssText = `
            width: 100px;
            padding: 2px 4px;
            font-size: 12px;
            border: 1px solid var(--workspace-icon-primary);
            border-radius: 3px;
            background: var(--workspace-bg-primary);
            color: var(--text-primary);
            outline: none;
        `;

        labelElement.style.display = 'none';
        tabElement.insertBefore(input, labelElement.nextSibling);
        input.focus();
        input.select();

        const finishRename = () => {
            const newName = input.value.trim() || currentName;
            this.renameTab(tabId, newName);
            input.remove();
            labelElement.style.display = '';
        };

        input.onblur = finishRename;
        input.onkeydown = (e) => {
            if (e.key === 'Enter') {
                finishRename();
            } else if (e.key === 'Escape') {
                input.value = currentName;
                finishRename();
            }
        };
    }

    /**
     * Get active tab
     */
    public getActiveTab(): CanvasTab | null {
        return this.tabs.find(t => t.id === this.activeTabId) || null;
    }

    /**
     * Get all tabs
     */
    public getTabs(): CanvasTab[] {
        return [...this.tabs];
    }

    /**
     * Initialize event listeners for the new tab button
     */
    public initializeEventListeners(): void {
        const newTabBtn = document.getElementById('canvas-tab-new');
        if (newTabBtn) {
            newTabBtn.onclick = () => {
                this.showInlineNewTabInput();
            };
        }
    }

    /**
     * Show inline input for creating a new tab
     */
    private showInlineNewTabInput(): void {
        const container = document.getElementById('canvas-tabs-container');
        const newTabBtn = document.getElementById('canvas-tab-new');
        if (!container || !newTabBtn) return;

        // Check if input already exists
        const existingInput = container.querySelector('.inline-new-tab-input');
        if (existingInput) {
            (existingInput as HTMLInputElement).focus();
            return;
        }

        // Create inline input container
        const inputWrapper = document.createElement('div');
        inputWrapper.className = 'data-tab inline-new-tab-wrapper';
        inputWrapper.style.cssText = `
            display: inline-flex;
            align-items: center;
            padding: 4px 8px;
        `;

        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'inline-new-tab-input';
        input.placeholder = 'Figure 2';
        const defaultFigureName = `Figure ${this.tabs.length + 1}`;
        input.value = defaultFigureName;
        input.style.cssText = `
            width: 100px;
            padding: 4px 6px;
            font-size: 12px;
            border: 1px solid var(--workspace-icon-primary);
            border-radius: 3px;
            background: var(--workspace-bg-primary);
            color: var(--text-primary);
            outline: none;
        `;

        inputWrapper.appendChild(input);

        // Insert before the + button (not after)
        if (newTabBtn && newTabBtn.parentNode === container) {
            container.insertBefore(inputWrapper, newTabBtn);
        } else {
            container.appendChild(inputWrapper);
        }

        input.focus();
        input.select();

        const finishCreate = () => {
            const figureName = input.value.trim() || defaultFigureName;
            inputWrapper.remove();
            const newTabId = this.createTab(figureName);
            this.switchToTab(newTabId);
        };

        const cancelCreate = () => {
            inputWrapper.remove();
        };

        input.onblur = () => {
            setTimeout(() => {
                if (document.activeElement !== input) {
                    finishCreate();
                }
            }, 100);
        };

        input.onkeydown = (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                finishCreate();
            } else if (e.key === 'Escape') {
                e.preventDefault();
                cancelCreate();
            }
        };
    }

    /**
     * Setup drag and drop handlers for tab reordering
     */
    private setupDragHandlers(tabElement: HTMLElement, tabId: string): void {
        tabElement.addEventListener('dragstart', (e: DragEvent) => {
            if (e.dataTransfer) {
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/plain', tabId);
            }
            tabElement.classList.add('dragging');
        });

        tabElement.addEventListener('dragend', () => {
            tabElement.classList.remove('dragging');
            // Remove all drag-over indicators
            document.querySelectorAll('.data-tab').forEach(el => {
                el.classList.remove('drag-over');
            });
        });

        tabElement.addEventListener('dragover', (e: DragEvent) => {
            e.preventDefault();
            if (e.dataTransfer) {
                e.dataTransfer.dropEffect = 'move';
            }
            tabElement.classList.add('drag-over');
        });

        tabElement.addEventListener('dragleave', () => {
            tabElement.classList.remove('drag-over');
        });

        tabElement.addEventListener('drop', (e: DragEvent) => {
            e.preventDefault();
            tabElement.classList.remove('drag-over');

            if (e.dataTransfer) {
                const draggedId = e.dataTransfer.getData('text/plain');
                this.reorderTabs(draggedId, tabId);
            }
        });
    }

    /**
     * Reorder tabs by moving draggedId before targetId
     */
    private reorderTabs(draggedId: string, targetId: string): void {
        if (draggedId === targetId) return;

        const draggedIndex = this.tabs.findIndex(t => t.id === draggedId);
        const targetIndex = this.tabs.findIndex(t => t.id === targetId);

        if (draggedIndex === -1 || targetIndex === -1) return;

        // Remove dragged tab and insert before target
        const [draggedTab] = this.tabs.splice(draggedIndex, 1);
        this.tabs.splice(targetIndex, 0, draggedTab);

        this.renderTabs();
    }
}
