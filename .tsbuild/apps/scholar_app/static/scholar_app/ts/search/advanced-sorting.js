"use strict";
/**

 * Advanced Multi-Level Sorting Controls
 *
 * Allows users to sort by multiple criteria in order (like pandas multi-column sorting).
 * Supports adding, removing, and reordering sort criteria. Includes result selection
 * and bulk export functionality.
 *
 * @version 1.0.0
 */
/**
 * Sort criterion structure
 */
console.log("[DEBUG] apps/scholar_app/static/scholar_app/ts/search/advanced-sorting.ts loaded");
// Multi-level sorting state
let sortCriteria = [];
// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function () {
    initializeAdvancedSorting();
    initializeResultSelection();
    initializeRangeFilters();
});
/**
 * Initialize advanced sorting interface
 */
function initializeAdvancedSorting() {
    const advancedSortBtn = document.getElementById('toggleAdvancedSort');
    if (!advancedSortBtn)
        return;
    advancedSortBtn.addEventListener('click', function (e) {
        e.preventDefault();
        const container = document.getElementById('advancedSortContainer');
        if (container) {
            container.style.display = container.style.display === 'none' ? 'block' : 'none';
        }
    });
    // Add event listeners to sort criterion buttons
    document.querySelectorAll('.sort-criterion-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const element = this;
            const field = element.dataset.field || '';
            const order = element.dataset.order || 'asc';
            addSortCriterionByButton(field, order, element);
        });
    });
    // Clear all button
    const clearBtn = document.getElementById('clearSortCriteria');
    if (clearBtn) {
        clearBtn.addEventListener('click', function (e) {
            e.preventDefault();
            sortCriteria = [];
            renderSortCriteria();
            updateHiddenSortInput();
            // Reset button states
            document.querySelectorAll('.sort-criterion-btn').forEach(btn => {
                btn.classList.remove('active');
                btn.classList.add('btn-outline-primary');
                btn.classList.remove('btn-primary');
                const badge = btn.querySelector('.badge');
                if (badge)
                    badge.remove();
            });
        });
    }
    // Initialize with existing sort parameters if present
    const urlParams = new URLSearchParams(window.location.search);
    const sortBy = urlParams.get('sort_by');
    if (sortBy && sortBy.includes(',')) {
        // Multi-level sort detected
        parseSortCriteria(sortBy);
        renderSortCriteria();
    }
}
/**
 * Parse sort criteria from URL parameter string
 */
function parseSortCriteria(sortByString) {
    sortCriteria = [];
    const criteria = sortByString.split(',');
    criteria.forEach(criterion => {
        const parts = criterion.split(':');
        if (parts.length === 2) {
            sortCriteria.push({
                field: parts[0].trim(),
                order: parts[1].trim()
            });
        }
    });
}
/**
 * Add or remove sort criterion when clicking button
 */
function addSortCriterionByButton(field, order, buttonElement) {
    // Check if already exists
    const existingIndex = sortCriteria.findIndex(c => c.field === field);
    if (existingIndex >= 0) {
        // Remove if clicking again
        sortCriteria.splice(existingIndex, 1);
        buttonElement.classList.remove('active', 'btn-primary');
        buttonElement.classList.add('btn-outline-primary');
        const badge = buttonElement.querySelector('.badge');
        if (badge)
            badge.remove();
    }
    else {
        // Add new criterion
        sortCriteria.push({ field, order });
        buttonElement.classList.add('active', 'btn-primary');
        buttonElement.classList.remove('btn-outline-primary');
        // Add priority badge
        const priorityBadge = document.createElement('span');
        priorityBadge.className = 'badge bg-warning text-dark ms-1';
        priorityBadge.textContent = sortCriteria.length.toString();
        buttonElement.appendChild(priorityBadge);
    }
    // Update all badges to reflect current order
    updateButtonPriorities();
    renderSortCriteria();
    updateHiddenSortInput();
}
/**
 * Update button priority badges
 */
function updateButtonPriorities() {
    // Clear all badges first
    document.querySelectorAll('.sort-criterion-btn .badge').forEach(badge => badge.remove());
    // Add badges in priority order
    sortCriteria.forEach((criterion, index) => {
        const button = document.querySelector(`.sort-criterion-btn[data-field="${criterion.field}"]`);
        if (button) {
            const badge = document.createElement('span');
            badge.className = 'badge bg-warning text-dark ms-1';
            badge.textContent = (index + 1).toString();
            button.appendChild(badge);
        }
    });
}
/**
 * Remove sort criterion by index
 */
function removeSortCriterion(index) {
    sortCriteria.splice(index, 1);
    renderSortCriteria();
    updateHiddenSortInput();
}
/**
 * Move sort criterion up or down
 */
function moveSortCriterion(index, direction) {
    if (direction === 'up' && index > 0) {
        [sortCriteria[index], sortCriteria[index - 1]] = [sortCriteria[index - 1], sortCriteria[index]];
    }
    else if (direction === 'down' && index < sortCriteria.length - 1) {
        [sortCriteria[index], sortCriteria[index + 1]] = [sortCriteria[index + 1], sortCriteria[index]];
    }
    renderSortCriteria();
    updateHiddenSortInput();
}
/**
 * Render sort criteria list
 */
function renderSortCriteria() {
    const container = document.getElementById('sortCriteriaList');
    if (!container)
        return;
    if (sortCriteria.length === 0) {
        container.innerHTML = '<p class="text-muted small">No multi-level sorting configured. Add criteria above.</p>';
        return;
    }
    let html = '<div class="list-group list-group-flush">';
    sortCriteria.forEach((criterion, index) => {
        const fieldLabel = getFieldLabel(criterion.field);
        const orderLabel = criterion.order === 'desc' ? '↓ High to Low' : '↑ Low to High';
        html += `
            <div class="list-group-item d-flex justify-content-between align-items-center p-2">
                <div>
                    <strong>${index + 1}.</strong>
                    <span class="badge bg-primary">${fieldLabel}</span>
                    <span class="badge bg-secondary">${orderLabel}</span>
                </div>
                <div class="btn-group btn-group-sm" role="group">
                    ${index > 0 ? `<button type="button" class="btn btn-outline-secondary" onclick="window.scholarSorting.moveCriterion(${index}, 'up')" title="Move up"><i class="fas fa-arrow-up"></i></button>` : ''}
                    ${index < sortCriteria.length - 1 ? `<button type="button" class="btn btn-outline-secondary" onclick="window.scholarSorting.moveCriterion(${index}, 'down')" title="Move down"><i class="fas fa-arrow-down"></i></button>` : ''}
                    <button type="button" class="btn btn-outline-danger" onclick="window.scholarSorting.removeCriterion(${index})" title="Remove"><i class="fas fa-times"></i></button>
                </div>
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}
/**
 * Get human-readable field label
 */
function getFieldLabel(field) {
    const labels = {
        citations: 'Citations',
        year: 'Year',
        title: 'Title',
        impact_factor: 'Impact Factor'
    };
    return labels[field] || field;
}
/**
 * Update hidden sort input field
 */
function updateHiddenSortInput() {
    // Update the hidden input or main sort_by field with comma-separated criteria
    const sortByInput = document.querySelector('select[name="sort_by"]');
    if (!sortByInput)
        return;
    if (sortCriteria.length === 0) {
        sortByInput.value = 'relevance';
    }
    else if (sortCriteria.length === 1) {
        sortByInput.value = sortCriteria[0].field;
        const orderSelect = document.querySelector('select[name="sort_order"]');
        if (orderSelect) {
            orderSelect.value = sortCriteria[0].order;
        }
    }
    else {
        // Multi-level: create comma-separated string
        const sortString = sortCriteria.map(c => `${c.field}:${c.order}`).join(',');
        sortByInput.value = sortString;
    }
}
/**
 * Paper selection functionality
 */
function initializeResultSelection() {
    const selectAllBtn = document.getElementById('selectAllResults');
    const deselectAllBtn = document.getElementById('deselectAllResults');
    const exportSelectedBtn = document.getElementById('exportSelectedBibtex');
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function () {
            document.querySelectorAll('.paper-select-checkbox').forEach(cb => {
                cb.checked = true;
            });
            updateSelectionCount();
        });
    }
    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', function () {
            document.querySelectorAll('.paper-select-checkbox').forEach(cb => {
                cb.checked = false;
            });
            updateSelectionCount();
        });
    }
    if (exportSelectedBtn) {
        exportSelectedBtn.addEventListener('click', exportSelectedPapers);
    }
    // Add event listeners to checkboxes
    document.querySelectorAll('.paper-select-checkbox').forEach(cb => {
        cb.addEventListener('change', updateSelectionCount);
    });
    updateSelectionCount();
}
/**
 * Update selection count display
 */
function updateSelectionCount() {
    const selectedCount = document.querySelectorAll('.paper-select-checkbox:checked').length;
    const totalCount = document.querySelectorAll('.paper-select-checkbox').length;
    const countDisplay = document.getElementById('selectedCount');
    if (countDisplay) {
        countDisplay.textContent = `${selectedCount} of ${totalCount} selected`;
    }
    const exportBtn = document.getElementById('exportSelectedBibtex');
    if (exportBtn) {
        exportBtn.disabled = selectedCount === 0;
    }
}
/**
 * Export selected papers as BibTeX
 */
function exportSelectedPapers() {
    const selectedPaperIds = Array.from(document.querySelectorAll('.paper-select-checkbox:checked'))
        .map(cb => cb.dataset.paperId)
        .filter(id => id);
    if (selectedPaperIds.length === 0) {
        alert('Please select at least one paper to export.');
        return;
    }
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
        getCookie('csrftoken');
    if (!csrfToken) {
        alert('CSRF token not found. Please refresh the page and try again.');
        return;
    }
    // Send to export endpoint via fetch
    fetch('/scholar/api/export/bibtex/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            paper_ids: selectedPaperIds,
            collection_name: 'search_results'
        })
    })
        .then(response => response.json())
        .then(data => {
        if (data.success) {
            // Create a blob and download
            const blob = new Blob([data.content], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = data.filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            alert(`Successfully exported ${data.count} papers as BibTeX!`);
        }
        else {
            alert('Export failed: ' + (data.error || 'Unknown error'));
        }
    })
        .catch((error) => {
        console.error('Export error:', error);
        alert('Failed to export papers. Please try again.');
    });
}
/**
 * Helper function to get cookie
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
/**
 * Dual-range filter synchronization with swarm plot integration
 * (Placeholder - range filter initialization would go here)
 */
function initializeRangeFilters() {
    // Range filter initialization code would go here
    // Omitted for brevity - this is a placeholder
}
// Expose functions to global scope for onclick handlers
window.scholarSorting = {
    removeCriterion: removeSortCriterion,
    moveCriterion: moveSortCriterion
};
//# sourceMappingURL=advanced-sorting.js.map