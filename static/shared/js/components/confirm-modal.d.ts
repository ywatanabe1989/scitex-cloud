/**
 * Modern Confirmation Modal Component
 * Reusable across the site for better UX than browser confirm()
 */
export interface ConfirmModalOptions {
    /** Modal title */
    title?: string;
    /** Main message content */
    message: string;
    /** Confirm button text */
    confirmText?: string;
    /** Cancel button text */
    cancelText?: string;
    /** Callback when confirmed */
    onConfirm?: () => void;
    /** Callback when cancelled */
    onCancel?: () => void;
}
/**
 * Show a modern confirmation dialog
 *
 * @param options - Configuration options for the modal
 */
export declare function showConfirm(options: ConfirmModalOptions): void;
declare global {
    interface Window {
        scitexConfirm: typeof showConfirm;
    }
}
//# sourceMappingURL=confirm-modal.d.ts.map