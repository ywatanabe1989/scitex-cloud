/**
 * API Client Utility Module
 * Provides reusable fetch wrapper with CSRF token handling
 */
import { getCsrfToken } from './csrf.js';
/**
 * API Client class for making requests with automatic CSRF token handling
 */
export class ApiClient {
    baseUrl;
    csrfTokenFn;
    constructor(baseUrl = '', csrfTokenFn = getCsrfToken) {
        this.baseUrl = baseUrl;
        this.csrfTokenFn = csrfTokenFn;
    }
    /**
     * Prepare request headers with CSRF token
     */
    getHeaders(headers) {
        const defaultHeaders = {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.csrfTokenFn()
        };
        return { ...defaultHeaders, ...headers };
    }
    /**
     * Make GET request
     */
    async get(url, options) {
        return this.request(url, { ...options, method: 'GET' });
    }
    /**
     * Make POST request
     */
    async post(url, body, options) {
        return this.request(url, {
            ...options,
            method: 'POST',
            body: JSON.stringify(body)
        });
    }
    /**
     * Make PUT request
     */
    async put(url, body, options) {
        return this.request(url, {
            ...options,
            method: 'PUT',
            body: JSON.stringify(body)
        });
    }
    /**
     * Make PATCH request
     */
    async patch(url, body, options) {
        return this.request(url, {
            ...options,
            method: 'PATCH',
            body: JSON.stringify(body)
        });
    }
    /**
     * Make DELETE request
     */
    async delete(url, options) {
        return this.request(url, { ...options, method: 'DELETE' });
    }
    /**
     * Core request method
     */
    async request(url, options = {}) {
        const fullUrl = this.baseUrl ? `${this.baseUrl}${url}` : url;
        try {
            // Build request with proper body handling
            const requestInit = {
                ...options,
                headers: this.getHeaders(options.headers)
            };
            // Ensure body is properly stringified if it's an object
            if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
                requestInit.body = JSON.stringify(options.body);
            }
            const response = await fetch(fullUrl, requestInit);
            // Handle different response types
            const contentType = response.headers.get('content-type');
            let data;
            if (contentType?.includes('application/json')) {
                data = await response.json();
            }
            else {
                data = await response.text();
            }
            if (!response.ok) {
                console.error(`[API] Error ${response.status}: ${url}`, data);
                return {
                    success: false,
                    error: data?.error || data?.message || `HTTP ${response.status}`,
                    data: data
                };
            }
            return {
                success: true,
                data: data
            };
        }
        catch (error) {
            const message = error instanceof Error ? error.message : 'Unknown error';
            console.error(`[API] Request failed: ${url}`, error);
            return {
                success: false,
                error: message
            };
        }
    }
}
// Export singleton instance
export const apiClient = new ApiClient();
//# sourceMappingURL=api.js.map