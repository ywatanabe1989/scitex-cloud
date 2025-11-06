"use strict";
/**
 * Delete Confirmation Handler
 * Enables delete button only when user types exact project path
 * @module projects/delete_confirmation
 */
console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/project_app/static/project_app/ts/projects/delete_confirmation.ts loaded");
class DeleteConfirmation {
    elements = null;
    constructor() {
        this.init();
    }
    init() {
        document.addEventListener('DOMContentLoaded', () => {
            console.log('[Delete Confirmation] Initializing');
            this.setupElements();
            this.attachListeners();
        });
    }
    setupElements() {
        const confirmInput = document.getElementById('confirmText');
        const deleteButton = document.getElementById('deleteBtn');
        if (!confirmInput || !deleteButton) {
            console.warn('[Delete Confirmation] Required elements not found');
            return;
        }
        const expectedText = confirmInput.getAttribute('data-expected-text') || '';
        if (!expectedText) {
            console.error('[Delete Confirmation] Expected text not provided');
            return;
        }
        this.elements = {
            confirmInput,
            deleteButton,
            expectedText
        };
        console.log('[Delete Confirmation] Expected text:', expectedText);
    }
    attachListeners() {
        if (!this.elements) {
            return;
        }
        const { confirmInput, deleteButton, expectedText } = this.elements;
        confirmInput.addEventListener('input', () => {
            const currentValue = confirmInput.value;
            const isMatch = currentValue === expectedText;
            this.updateButtonState(deleteButton, isMatch);
            console.log('[Delete Confirmation] Input:', currentValue, '| Match:', isMatch);
        });
    }
    updateButtonState(button, enabled) {
        button.disabled = !enabled;
        button.style.opacity = enabled ? '1' : '0.5';
        button.style.cursor = enabled ? 'pointer' : 'not-allowed';
    }
}
// Initialize on page load
new DeleteConfirmation();
//# sourceMappingURL=delete_confirmation.js.map