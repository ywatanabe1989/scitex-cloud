/**

 * Drag-and-Drop Result Sorting
 *
 * Allows users to manually reorder search results by dragging and dropping result cards.
 * Useful for creating custom reading lists or ordering papers by personal preference.
 *
 * @version 1.0.0
 */
declare let draggedItem: HTMLElement | null;
declare let dragStartIndex: number;
declare let dragPlaceholder: HTMLElement | null;
/**
 * Initialize drag and drop functionality
 */
declare function initializeDragSort(): void;
/**
 * Update all result cards to be draggable
 */
declare function updateDraggableCards(): void;
/**
 * Drag start handler
 */
declare function handleDragStart(this: HTMLElement, e: DragEvent): void;
/**
 * Drag end handler
 */
declare function handleDragEnd(this: HTMLElement, e: DragEvent): void;
/**
 * Drag over handler
 */
declare function handleDragOver(this: HTMLElement, e: DragEvent): void;
/**
 * Drag enter handler
 */
declare function handleDragEnter(this: HTMLElement, e: DragEvent): void;
/**
 * Drag leave handler
 */
declare function handleDragLeave(this: HTMLElement, e: DragEvent): void;
/**
 * Drop handler
 */
declare function handleDrop(this: HTMLElement, e: DragEvent): void;
//# sourceMappingURL=drag-sort.d.ts.map