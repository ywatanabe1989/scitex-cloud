/**
 * CSRF Token Utility Module
 * Handles retrieval of Django CSRF token from multiple sources
 */
console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/static/ts/utils/csrf.ts loaded");
export function getCsrfToken() {
    // First, try to get from window config objects
    if (window.WRITER_CONFIG?.csrfToken) {
        return window.WRITER_CONFIG.csrfToken;
    }
    if (window.SCHOLAR_CONFIG?.csrfToken) {
        return window.SCHOLAR_CONFIG.csrfToken;
    }
    // Try to get CSRF token from form input
    const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    if (tokenElement) {
        return tokenElement.value;
    }
    // Fallback: try to get from meta tag
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        return metaTag.getAttribute('content') || '';
    }
    // Fallback: try to get from cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return decodeURIComponent(value);
        }
    }
    // If no CSRF token found, return empty string and let Django handle it
    console.warn('[CSRF] Token not found in config, form, meta, or cookies');
    return '';
}
/**
 * Create headers object with CSRF token for API requests
 */
export function createHeadersWithCsrf(additionalHeaders = {}) {
    const csrfToken = getCsrfToken();
    return {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
        ...additionalHeaders,
    };
}
//# sourceMappingURL=csrf.js.map