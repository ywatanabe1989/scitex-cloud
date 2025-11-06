/**

 * Advanced Multi-Level Sorting Controls
 *
 * Allows users to sort by multiple criteria in order (like pandas multi-column sorting).
 * Supports adding, removing, and reordering sort criteria. Includes result selection
 * and bulk export functionality.
 *
 * @version 1.0.0
 */
interface SortCriterion {
    field: string;
    order: 'asc' | 'desc';
}
declare let sortCriteria: SortCriterion[];
/**
 * Initialize advanced sorting interface
 */
declare function initializeAdvancedSorting(): void;
/**
 * Parse sort criteria from URL parameter string
 */
declare function parseSortCriteria(sortByString: string): void;
/**
 * Add or remove sort criterion when clicking button
 */
declare function addSortCriterionByButton(field: string, order: 'asc' | 'desc', buttonElement: HTMLElement): void;
/**
 * Update button priority badges
 */
declare function updateButtonPriorities(): void;
/**
 * Remove sort criterion by index
 */
declare function removeSortCriterion(index: number): void;
/**
 * Move sort criterion up or down
 */
declare function moveSortCriterion(index: number, direction: 'up' | 'down'): void;
/**
 * Render sort criteria list
 */
declare function renderSortCriteria(): void;
/**
 * Get human-readable field label
 */
declare function getFieldLabel(field: string): string;
/**
 * Update hidden sort input field
 */
declare function updateHiddenSortInput(): void;
/**
 * Paper selection functionality
 */
declare function initializeResultSelection(): void;
/**
 * Update selection count display
 */
declare function updateSelectionCount(): void;
/**
 * Export selected papers as BibTeX
 */
declare function exportSelectedPapers(): void;
/**
 * Dual-range filter synchronization with swarm plot integration
 * (Placeholder - range filter initialization would go here)
 */
declare function initializeRangeFilters(): void;
//# sourceMappingURL=advanced-sorting.d.ts.map