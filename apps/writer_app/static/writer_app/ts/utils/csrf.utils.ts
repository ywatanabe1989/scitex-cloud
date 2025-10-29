/**
 * CSRF token utilities for Django security
 */

/**
 * Get CSRF token from DOM or cookies
 */
export function getCsrfToken(): string {
  // Try to get from DOM first (Django renders it in template)
  const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement;
  if (tokenElement?.value) {
    return tokenElement.value;
  }

  // Try to get from cookie
  const name = 'csrftoken';
  let cookieValue = '';
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }

  return cookieValue;
}

/**
 * Create headers object with CSRF token
 */
export function createHeadersWithCsrf(additionalHeaders: Record<string, string> = {}): Record<string, string> {
  const csrfToken = getCsrfToken();
  return {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken,
    ...additionalHeaders,
  };
}
