/**
 * Modern Confirmation Modal Component
 * Reusable across the site for better UX than browser confirm()
 */
/**
 * Configuration options for confirmation modal
 */
console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/static/ts/components/confirm-modal.ts loaded");
/**
 * Show a modern confirmation dialog
 *
 * @param options - Configuration options for the modal
 */
export function showConfirm(options) {
    const { title = 'Confirm', message, confirmText = 'Confirm', cancelText = 'Cancel', onConfirm, onCancel } = options;
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
        <h3>${escapeHtml(title)}</h3>
        <button class="scitex-modal-close" aria-label="Close">&times;</button>
      </div>
      <div class="scitex-modal-body">
        <p>${escapeHtml(message)}</p>
      </div>
      <div class="scitex-modal-footer">
        <button class="scitex-btn scitex-btn-secondary" data-action="cancel">${escapeHtml(cancelText)}</button>
        <button class="scitex-btn scitex-btn-primary" data-action="confirm">${escapeHtml(confirmText)}</button>
      </div>
    </div>
  `;
    // Add to page
    document.body.appendChild(modal);
    // Get button elements
    const closeBtn = modal.querySelector('.scitex-modal-close');
    const cancelBtn = modal.querySelector('[data-action="cancel"]');
    const confirmBtn = modal.querySelector('[data-action="confirm"]');
    /**
     * Close modal with animation
     */
    const closeModal = () => {
        modal.classList.add('scitex-modal-closing');
        setTimeout(() => modal.remove(), 300);
    };
    // Event listeners
    closeBtn?.addEventListener('click', () => {
        if (onCancel)
            onCancel();
        closeModal();
    });
    cancelBtn?.addEventListener('click', () => {
        if (onCancel)
            onCancel();
        closeModal();
    });
    confirmBtn?.addEventListener('click', () => {
        if (onConfirm)
            onConfirm();
        closeModal();
    });
    // Close on overlay click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            if (onCancel)
                onCancel();
            closeModal();
        }
    });
    // Close on Escape key
    const escapeHandler = (e) => {
        if (e.key === 'Escape') {
            if (onCancel)
                onCancel();
            closeModal();
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    document.addEventListener('keydown', escapeHandler);
    // Animate in
    setTimeout(() => modal.classList.add('scitex-modal-visible'), 10);
    // Focus confirm button
    confirmBtn?.focus();
}
/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
window.scitexConfirm = showConfirm;
//# sourceMappingURL=confirm-modal.js.map