/**
 * API Client Utility Module
 * Provides reusable fetch wrapper with CSRF token handling
 */
export interface ApiRequestInit extends Omit<RequestInit, 'body'> {
    body?: BodyInit | object | null;
}
export interface ApiResponse<T = any> {
    success: boolean;
    data?: T;
    error?: string;
    message?: string;
}
/**
 * API Client class for making requests with automatic CSRF token handling
 */
export declare class ApiClient {
    private baseUrl;
    private csrfTokenFn;
    constructor(baseUrl?: string, csrfTokenFn?: () => string);
    /**
     * Prepare request headers with CSRF token
     */
    private getHeaders;
    /**
     * Make GET request
     */
    get<T = any>(url: string, options?: ApiRequestInit): Promise<ApiResponse<T>>;
    /**
     * Make POST request
     */
    post<T = any>(url: string, body?: any, options?: ApiRequestInit): Promise<ApiResponse<T>>;
    /**
     * Make PUT request
     */
    put<T = any>(url: string, body?: any, options?: ApiRequestInit): Promise<ApiResponse<T>>;
    /**
     * Make PATCH request
     */
    patch<T = any>(url: string, body?: any, options?: ApiRequestInit): Promise<ApiResponse<T>>;
    /**
     * Make DELETE request
     */
    delete<T = any>(url: string, options?: ApiRequestInit): Promise<ApiResponse<T>>;
    /**
     * Core request method
     */
    private request;
}
export declare const apiClient: ApiClient;
//# sourceMappingURL=api.d.ts.map