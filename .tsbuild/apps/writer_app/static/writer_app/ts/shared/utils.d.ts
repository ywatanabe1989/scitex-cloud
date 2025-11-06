/**
 * Shared utility functions for writer_app
 */
export declare function getCsrfToken(): string;
/**
 * Make API request with CSRF token
 */
export declare function apiRequest(url: string, options?: RequestInit): Promise<Response>;
/**
 * Format date to human-readable string
 */
export declare function formatDate(date: Date | string): string;
/**
 * Debounce function calls
 */
export declare function debounce<T extends (...args: any[]) => any>(func: T, wait: number): (...args: Parameters<T>) => void;
/**
 * Show toast notification
 */
export declare function showToast(message: string, type?: 'success' | 'error' | 'info'): void;
/**
 * Format file size to human-readable string
 */
export declare function formatFileSize(bytes: number): string;
//# sourceMappingURL=utils.d.ts.map