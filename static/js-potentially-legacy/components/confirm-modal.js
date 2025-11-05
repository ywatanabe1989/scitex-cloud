/**
 * Modern Confirmation Modal Component
 * Reusable across the site for better UX than browser confirm()
 */

/**
 * Show a modern confirmation dialog
 *
 * @param {Object} options - Configuration options
 * @param {string} options.title - Modal title
 * @param {string} options.message - Main message
 * @param {string} options.confirmText - Confirm button text (default: "Confirm")
 * @param {string} options.cancelText - Cancel button text (default: "Cancel")
 * @param {Function} options.onConfirm - Callback when confirmed
 * @param {Function} options.onCancel - Callback when cancelled (optional)
 */
export function showConfirm(options) {
    const {
        title = 'Confirm',
        message,
        confirmText = 'Confirm',
        cancelText = 'Cancel',
        onConfirm,
        onCancel
    } = options;

    // Remove existing modal if present
    const existingModal = document.getElementById('scitex-confirm-modal');
    if (existingModal) {
        existingModal.remove();
    }

    // Create modal HTML
    const modal = document.createElement('div');
    modal.id = 'scitex-confirm-modal';
    modal.className = 'scitex-modal-overlay';
    modal.innerHTML = `
        <div class="scitex-modal-content">
            <div class="scitex-modal-header">
                <h3>${title}</h3>
                <button class="scitex-modal-close" aria-label="Close">&times;</button>
            </div>
            <div class="scitex-modal-body">
                <p>${message}</p>
            </div>
            <div class="scitex-modal-footer">
                <button class="scitex-btn scitex-btn-secondary" data-action="cancel">${cancelText}</button>
                <button class="scitex-btn scitex-btn-primary" data-action="confirm">${confirmText}</button>
            </div>
        </div>
    `;

    // Add to page
    document.body.appendChild(modal);

    // Add event listeners
    const closeBtn = modal.querySelector('.scitex-modal-close');
    const cancelBtn = modal.querySelector('[data-action="cancel"]');
    const confirmBtn = modal.querySelector('[data-action="confirm"]');

    const closeModal = () => {
        modal.classList.add('scitex-modal-closing');
        setTimeout(() => modal.remove(), 300);
    };

    closeBtn.addEventListener('click', () => {
        if (onCancel) onCancel();
        closeModal();
    });

    cancelBtn.addEventListener('click', () => {
        if (onCancel) onCancel();
        closeModal();
    });

    confirmBtn.addEventListener('click', () => {
        if (onConfirm) onConfirm();
        closeModal();
    });

    // Close on overlay click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            if (onCancel) onCancel();
            closeModal();
        }
    });

    // Close on Escape key
    const escapeHandler = (e) => {
        if (e.key === 'Escape') {
            if (onCancel) onCancel();
            closeModal();
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    document.addEventListener('keydown', escapeHandler);

    // Animate in
    setTimeout(() => modal.classList.add('scitex-modal-visible'), 10);

    // Focus confirm button
    confirmBtn.focus();
}

// Make it available globally
window.scitexConfirm = showConfirm;
