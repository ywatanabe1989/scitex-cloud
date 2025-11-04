/**
 * UI Utility Module
 * Common UI interaction helpers
 */
export type ToastType = 'success' | 'error' | 'warning' | 'info';
/**
 * Show a toast notification
 */
export declare function showToast(message: string, type?: ToastType, duration?: number): void;
/**
 * Show a status message in a specific container
 */
export declare function showStatus(message: string, type: ToastType, containerId?: string): void;
/**
 * Disable/enable button with loading state
 */
export declare function setButtonLoading(button: HTMLElement, isLoading: boolean, loadingText?: string): void;
/**
 * Show/hide loading spinner
 */
export declare function showSpinner(containerId: string, show?: boolean): void;
/**
 * Modal helper to show/hide modals
 */
export declare class Modal {
    private element;
    private bootstrap?;
    constructor(elementId: string);
    show(): void;
    hide(): void;
    toggle(): void;
}
/**
 * Confirm dialog helper
 */
export declare function confirm(message: string): Promise<boolean>;
/**
 * Debounce function calls
 */
export declare function debounce<T extends (...args: any[]) => any>(func: T, wait: number): (...args: Parameters<T>) => void;
/**
 * Throttle function calls
 */
export declare function throttle<T extends (...args: any[]) => any>(func: T, limit: number): (...args: Parameters<T>) => void;
//# sourceMappingURL=ui.d.ts.map