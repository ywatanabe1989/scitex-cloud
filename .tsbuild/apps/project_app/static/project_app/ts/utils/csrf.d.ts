/**
 * CSRF Token Utility Module
 * Handles retrieval of Django CSRF token from multiple sources
 */
export declare function getCsrfToken(): string;
/**
 * Create headers object with CSRF token for API requests
 */
export declare function createHeadersWithCsrf(additionalHeaders?: Record<string, string>): Record<string, string>;
//# sourceMappingURL=csrf.d.ts.map