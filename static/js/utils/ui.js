/**
 * UI Utility Module
 * Common UI interaction helpers
 */
/**
 * Show a toast notification
 */
export function showToast(message, type = 'info', duration = 5000) {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    toast.setAttribute('role', 'alert');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    `;
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(toast);
    if (duration > 0) {
        setTimeout(() => {
            toast.remove();
        }, duration);
    }
}
/**
 * Show a status message in a specific container
 */
export function showStatus(message, type, containerId) {
    const container = containerId ? document.getElementById(containerId) : document.body;
    if (!container)
        return;
    const status = document.createElement('div');
    status.className = `alert alert-${type === 'error' ? 'danger' : type}`;
    status.textContent = message;
    status.style.margin = '10px 0';
    if (containerId) {
        const existing = container.querySelector('.alert');
        if (existing)
            existing.remove();
        container.appendChild(status);
    }
    else {
        document.body.insertBefore(status, document.body.firstChild);
    }
    setTimeout(() => status.remove(), 5000);
}
/**
 * Disable/enable button with loading state
 */
export function setButtonLoading(button, isLoading, loadingText = 'Loading...') {
    const originalText = button.textContent;
    const originalHTML = button.innerHTML;
    if (isLoading) {
        button.setAttribute('disabled', 'true');
        button.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${loadingText}`;
    }
    else {
        button.removeAttribute('disabled');
        button.textContent = originalText;
        button.innerHTML = originalHTML;
    }
}
/**
 * Show/hide loading spinner
 */
export function showSpinner(containerId, show = true) {
    const container = document.getElementById(containerId);
    if (!container)
        return;
    if (show) {
        const spinner = document.createElement('div');
        spinner.className = 'spinner-container';
        spinner.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        `;
        container.appendChild(spinner);
    }
    else {
        const spinner = container.querySelector('.spinner-container');
        if (spinner)
            spinner.remove();
    }
}
/**
 * Modal helper to show/hide modals
 */
export class Modal {
    element;
    bootstrap;
    constructor(elementId) {
        const el = document.getElementById(elementId);
        if (!el) {
            throw new Error(`Modal element with id "${elementId}" not found`);
        }
        this.element = el;
        // Try to get Bootstrap modal instance
        if (window.bootstrap) {
            this.bootstrap = new window.bootstrap.Modal(el);
        }
    }
    show() {
        if (this.bootstrap) {
            this.bootstrap.show();
        }
        else {
            this.element.setAttribute('style', 'display: flex;');
        }
    }
    hide() {
        if (this.bootstrap) {
            this.bootstrap.hide();
        }
        else {
            this.element.setAttribute('style', 'display: none;');
        }
    }
    toggle() {
        if (this.bootstrap) {
            this.bootstrap.toggle();
        }
        else {
            const isHidden = this.element.style.display === 'none';
            this.element.style.display = isHidden ? 'flex' : 'none';
        }
    }
}
/**
 * Confirm dialog helper
 */
export function confirm(message) {
    return Promise.resolve(window.confirm(message));
}
/**
 * Debounce function calls
 */
export function debounce(func, wait) {
    let timeout = null;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            func(...args);
        };
        if (timeout) {
            clearTimeout(timeout);
        }
        timeout = setTimeout(later, wait);
    };
}
/**
 * Throttle function calls
 */
export function throttle(func, limit) {
    let inThrottle = false;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => (inThrottle = false), limit);
        }
    };
}
//# sourceMappingURL=ui.js.map