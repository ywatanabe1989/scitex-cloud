/**
 * Drag-and-Drop Sorting Interface
 * Allows users to:
 * - Drag sort items to reorder priority (left = higher priority)
 * - Click items to cycle through states: None → Ascending → Descending → None
 */

(function() {
    'use strict';

    let draggedElement = null;

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeDragSort();
    });

    function initializeDragSort() {
        const container = document.getElementById('dragSortContainer');
        if (!container) {
            console.warn('[Drag Sort] Container not found');
            return;
        }

        const sortItems = container.querySelectorAll('.sort-item');

        sortItems.forEach(item => {
            // Click to cycle through states
            item.addEventListener('click', function(e) {
                // Don't trigger if clicking the drag handle
                if (e.target.closest('.drag-handle')) return;

                cycleSortState(this);
            });

            // Drag start
            item.addEventListener('dragstart', function(e) {
                draggedElement = this;
                this.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', this.innerHTML);
            });

            // Drag end
            item.addEventListener('dragend', function(e) {
                this.classList.remove('dragging');
                // Remove all drag-over classes
                sortItems.forEach(item => item.classList.remove('drag-over'));
            });

            // Drag over
            item.addEventListener('dragover', function(e) {
                if (e.preventDefault) {
                    e.preventDefault();
                }
                e.dataTransfer.dropEffect = 'move';

                const afterElement = getDragAfterElement(container, e.clientX);
                if (afterElement == null) {
                    container.appendChild(draggedElement);
                } else {
                    container.insertBefore(draggedElement, afterElement);
                }

                return false;
            });

            // Drag enter
            item.addEventListener('dragenter', function(e) {
                if (this !== draggedElement) {
                    this.classList.add('drag-over');
                }
            });

            // Drag leave
            item.addEventListener('dragleave', function(e) {
                this.classList.remove('drag-over');
            });

            // Drop
            item.addEventListener('drop', function(e) {
                if (e.stopPropagation) {
                    e.stopPropagation();
                }
                this.classList.remove('drag-over');
                return false;
            });
        });

        console.log('[Drag Sort] Initialized with', sortItems.length, 'items');
    }

    /**
     * Cycle through sort states: none → asc → desc → none
     */
    function cycleSortState(element) {
        const currentState = element.getAttribute('data-state');
        let newState;

        switch(currentState) {
            case 'none':
                newState = 'asc';
                break;
            case 'asc':
                newState = 'desc';
                break;
            case 'desc':
                newState = 'none';
                break;
            default:
                newState = 'none';
        }

        element.setAttribute('data-state', newState);

        // Update the indicator
        const indicator = element.querySelector('.sort-indicator');
        if (indicator) {
            // CSS will handle the content via ::before pseudo-element
            indicator.setAttribute('data-state', newState);
        }

        console.log('[Drag Sort] Changed', element.getAttribute('data-field'), 'to', newState);

        // Trigger sort update
        updateSort();
    }

    /**
     * Get the element that should be after the dragged element
     */
    function getDragAfterElement(container, x) {
        const draggableElements = [...container.querySelectorAll('.sort-item:not(.dragging)')];

        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = x - box.left - box.width / 2;

            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }

    /**
     * Update the sort based on current state and order
     */
    function updateSort() {
        const container = document.getElementById('dragSortContainer');
        if (!container) return;

        const sortItems = container.querySelectorAll('.sort-item');
        const sortCriteria = [];

        // Build sort criteria array based on order (left to right = priority)
        sortItems.forEach((item, index) => {
            const field = item.getAttribute('data-field');
            const state = item.getAttribute('data-state');

            if (state !== 'none') {
                sortCriteria.push({
                    field: field,
                    order: state,
                    priority: index + 1
                });
            }
        });

        console.log('[Drag Sort] Sort criteria:', sortCriteria);

        // Apply sorting to results
        if (sortCriteria.length > 0) {
            applySortToResults(sortCriteria);
        } else {
            console.log('[Drag Sort] No active sort criteria');
        }
    }

    /**
     * Apply multi-level sorting to search results
     */
    function applySortToResults(criteria) {
        const resultsContainer = document.querySelector('.search-results-container');
        if (!resultsContainer) {
            console.warn('[Drag Sort] No results container found');
            return;
        }

        const cards = Array.from(resultsContainer.querySelectorAll('.result-card'));
        if (cards.length === 0) {
            console.warn('[Drag Sort] No result cards found');
            return;
        }

        // Sort cards using multi-level criteria
        cards.sort((a, b) => {
            for (let criterion of criteria) {
                const valueA = getCardValue(a, criterion.field);
                const valueB = getCardValue(b, criterion.field);

                let comparison = 0;
                if (valueA < valueB) comparison = -1;
                if (valueA > valueB) comparison = 1;

                if (comparison !== 0) {
                    return criterion.order === 'asc' ? comparison : -comparison;
                }
            }
            return 0;
        });

        // Re-append cards in sorted order
        cards.forEach(card => resultsContainer.appendChild(card));

        console.log('[Drag Sort] Sorted', cards.length, 'results by', criteria.length, 'criteria');
    }

    /**
     * Extract sort value from a result card
     */
    function getCardValue(card, field) {
        switch(field) {
            case 'year':
                const year = card.getAttribute('data-year');
                return year ? parseInt(year) : 0;

            case 'citations':
                const citationText = card.textContent.match(/(\d+)\s+citations?/i);
                return citationText ? parseInt(citationText[1]) : 0;

            case 'impact_factor':
                const ifText = card.textContent.match(/IF:\s*([\d.]+)/i);
                return ifText ? parseFloat(ifText[1]) : 0;

            default:
                return 0;
        }
    }

    // Expose updateSort for external use
    window.dragSort = {
        update: updateSort
    };

})();
