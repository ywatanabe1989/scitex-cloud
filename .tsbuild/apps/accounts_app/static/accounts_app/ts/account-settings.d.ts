/**
 * Account Settings - TypeScript Implementation
 * Handles account settings page interactions
 *
 * Features:
 * - Form submission debugging
 * - Password toggle visibility
 * - Password validation with real-time feedback
 * - Account deletion confirmation modal
 *
 * @version 2.0.0 (TypeScript)
 * @author SciTeX Development Team
 */
interface PasswordRule {
    element: HTMLElement;
    isValid: boolean;
    hasInput: boolean;
}
/** Password validation requirements */
interface PasswordRequirements {
    length: boolean;
    lowercase: boolean;
    uppercase: boolean;
    number: boolean;
    special: boolean;
}
/**
 * Helper function to update password rule state
 */
declare function updatePasswordRule(element: HTMLElement, isValid: boolean, hasInput: boolean): void;
/**
 * Validate password requirements
 */
declare function validatePasswordRequirements(password: string): PasswordRequirements;
/**
 * Show delete account confirmation modal
 */
declare function showDeleteAccountModal(): void;
/**
 * Hide delete account confirmation modal
 */
declare function hideDeleteAccountModal(): void;
/**
 * Check delete account confirmation input
 */
declare function checkDeleteAccountInput(): void;
/**
 * Submit delete account form
 */
declare function submitDeleteAccount(): void;
declare global {
    interface Window {
        showDeleteAccountModal: typeof showDeleteAccountModal;
        hideDeleteAccountModal: typeof hideDeleteAccountModal;
        checkDeleteAccountInput: typeof checkDeleteAccountInput;
        submitDeleteAccount: typeof submitDeleteAccount;
    }
}
//# sourceMappingURL=account-settings.d.ts.map