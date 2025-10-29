/**
 * CSRF Token Utility Module
 * Handles retrieval of Django CSRF token from multiple sources
 */

export function getCsrfToken(): string {
    // First, try to get from WRITER_CONFIG (set in template)
    if ((window as any).WRITER_CONFIG?.csrfToken) {
        return (window as any).WRITER_CONFIG.csrfToken;
    }

    // Try to get CSRF token from form input
    const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement;
    if (tokenElement) {
        return tokenElement.value;
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
    console.warn('[Writer] CSRF token not found in form, config, or cookies');
    return '';
}
