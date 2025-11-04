// Pull request form functionality

(function() {
    'use strict';

    function updateComparison(): void {
        const baseSelect = document.getElementById('baseSelect') as HTMLSelectElement | null;
        const headSelect = document.getElementById('headSelect') as HTMLSelectElement | null;

        if (!baseSelect || !headSelect) {
            console.error('Base or head select element not found');
            return;
        }

        const base = baseSelect.value;
        const head = headSelect.value;

        if (base && head) {
            window.location.href = `?base=${base}&head=${head}`;
        }
    }

    // Expose function to global scope for use in HTML onchange attributes
    (window as any).updateComparison = updateComparison;
})();
