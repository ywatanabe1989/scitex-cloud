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

// ============================================================================
// Type Definitions
// ============================================================================

/** Password validation rule state */

console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/accounts_app/static/accounts_app/ts/account-settings.ts loaded");
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

// ============================================================================
// Initialization
// ============================================================================

console.log('Account settings JS loaded');

// ============================================================================
// Form Submission Debugging
// ============================================================================

/**
 * Add form submission debugging
 */
document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll<HTMLFormElement>('form');
    forms.forEach((form) => {
        form.addEventListener('submit', function() {
            const action = this.querySelector<HTMLInputElement>('input[name="action"]');
            console.log('Form submitted, action:', action ? action.value : 'none');
        });
    });
});

// ============================================================================
// Password Toggle Functionality
// ============================================================================

/**
 * Initialize password toggle buttons
 */
document.addEventListener('DOMContentLoaded', () => {
    const toggleButtons = document.querySelectorAll<HTMLButtonElement>('.toggle-password');

    toggleButtons.forEach((button) => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            if (!targetId) return;

            const passwordInput = document.getElementById(targetId) as HTMLInputElement | null;
            const icon = this.querySelector<HTMLElement>('i');

            if (passwordInput && icon) {
                const currentType = passwordInput.getAttribute('type');
                const newType = currentType === 'password' ? 'text' : 'password';
                passwordInput.setAttribute('type', newType);

                // Toggle the eye icon
                if (newType === 'password') {
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                } else {
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                }
            }
        });
    });
});

// ============================================================================
// Password Validation
// ============================================================================

/**
 * Helper function to update password rule state
 */
function updatePasswordRule(element: HTMLElement, isValid: boolean, hasInput: boolean): void {
    element.classList.remove('valid', 'invalid');
    const icon = element.querySelector<HTMLElement>('i');
    if (!icon) return;

    if (isValid) {
        element.style.color = '#28a745';  // Green
        element.classList.add('valid');
        icon.className = 'fas fa-check';
    } else if (hasInput) {
        element.style.color = '#dc3545';  // Red
        element.classList.add('invalid');
        icon.className = 'fas fa-times';
    } else {
        element.style.color = '#6c757d';  // Gray
        icon.className = 'fas fa-circle';
    }
}

/**
 * Validate password requirements
 */
function validatePasswordRequirements(password: string): PasswordRequirements {
    return {
        length: password.length >= 8,
        lowercase: /[a-z]/.test(password),
        uppercase: /[A-Z]/.test(password),
        number: /\d/.test(password),
        special: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)
    };
}

/**
 * Initialize password validation
 */
document.addEventListener('DOMContentLoaded', () => {
    const newPasswordInput = document.getElementById('new_password') as HTMLInputElement | null;
    const confirmPasswordInput = document.getElementById('confirm_password') as HTMLInputElement | null;

    // Find the change password form
    const actionInput = document.querySelector<HTMLInputElement>('form input[name="action"][value="change_password"]');
    const changePasswordForm = actionInput?.closest('form');

    if (newPasswordInput && changePasswordForm) {
        // Create password requirements display
        const requirementsDiv = document.createElement('div');
        requirementsDiv.className = 'password-rules';
        requirementsDiv.innerHTML = `
            <div class="password-rules-title">Password Requirements:</div>
            <div class="password-rule" id="rule-length"><i class="fas fa-circle"></i> At least 8 characters</div>
            <div class="password-rule" id="rule-lowercase"><i class="fas fa-circle"></i> At least one lowercase letter</div>
            <div class="password-rule" id="rule-uppercase"><i class="fas fa-circle"></i> At least one uppercase letter</div>
            <div class="password-rule" id="rule-number"><i class="fas fa-circle"></i> At least one number</div>
            <div class="password-rule" id="rule-special"><i class="fas fa-circle"></i> At least one special character (!@#$%^&*)</div>
        `;

        // Insert after new password input group
        const inputGroup = newPasswordInput.parentElement;
        const formGroup = inputGroup?.parentElement;
        if (formGroup) {
            formGroup.appendChild(requirementsDiv);
        }

        // Real-time validation
        newPasswordInput.addEventListener('input', function() {
            const password = this.value;
            const hasInput = password.length > 0;

            // Get rule elements
            const ruleLength = document.getElementById('rule-length');
            const ruleLowercase = document.getElementById('rule-lowercase');
            const ruleUppercase = document.getElementById('rule-uppercase');
            const ruleNumber = document.getElementById('rule-number');
            const ruleSpecial = document.getElementById('rule-special');

            if (!ruleLength || !ruleLowercase || !ruleUppercase || !ruleNumber || !ruleSpecial) {
                return;
            }

            // Validate requirements
            const requirements = validatePasswordRequirements(password);

            // Update each rule
            updatePasswordRule(ruleLength, requirements.length, hasInput);
            updatePasswordRule(ruleLowercase, requirements.lowercase, hasInput);
            updatePasswordRule(ruleUppercase, requirements.uppercase, hasInput);
            updatePasswordRule(ruleNumber, requirements.number, hasInput);
            updatePasswordRule(ruleSpecial, requirements.special, hasInput);
        });
    }
});

// ============================================================================
// Delete Account Modal
// ============================================================================

/**
 * Show delete account confirmation modal
 */
function showDeleteAccountModal(): void {
    console.log('showDeleteAccountModal called');
    const modal = document.getElementById('deleteAccountModal') as HTMLElement | null;
    console.log('Modal element:', modal);

    if (modal) {
        modal.style.display = 'flex';

        const confirmInput = document.getElementById('deleteAccountConfirmInput') as HTMLInputElement | null;
        const confirmButton = document.getElementById('deleteAccountConfirmButton') as HTMLButtonElement | null;

        if (confirmInput) {
            confirmInput.value = '';
        }
        if (confirmButton) {
            confirmButton.disabled = true;
        }

        console.log('Modal displayed');
    } else {
        console.error('Delete account modal not found!');
    }
}

/**
 * Hide delete account confirmation modal
 */
function hideDeleteAccountModal(): void {
    const modal = document.getElementById('deleteAccountModal') as HTMLElement | null;
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * Check delete account confirmation input
 */
function checkDeleteAccountInput(): void {
    const input = document.getElementById('deleteAccountConfirmInput') as HTMLInputElement | null;
    const button = document.getElementById('deleteAccountConfirmButton') as HTMLButtonElement | null;

    if (!input || !button) return;

    const expectedValue = input.getAttribute('data-username');

    if (input.value === expectedValue) {
        button.disabled = false;
        button.style.opacity = '1';
    } else {
        button.disabled = true;
        button.style.opacity = '0.5';
    }
}

/**
 * Submit delete account form
 */
function submitDeleteAccount(): void {
    const confirmButton = document.getElementById('deleteAccountConfirmButton') as HTMLElement | null;
    const confirmInput = document.getElementById('deleteAccountConfirmInput') as HTMLInputElement | null;
    const csrfTokenElement = document.querySelector<HTMLInputElement>('[name=csrfmiddlewaretoken]');

    if (!confirmButton || !confirmInput || !csrfTokenElement) {
        console.error('Required elements not found for delete account');
        return;
    }

    const deleteUrl = confirmButton.getAttribute('data-delete-url');
    const username = confirmInput.getAttribute('data-username');
    const csrfToken = csrfTokenElement.value;

    if (!deleteUrl || !username) {
        console.error('Missing delete URL or username');
        return;
    }

    // Create and submit form
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = deleteUrl;

    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;

    const confirmTextInput = document.createElement('input');
    confirmTextInput.type = 'hidden';
    confirmTextInput.name = 'confirm_text';
    confirmTextInput.value = `delete ${username}`;

    form.appendChild(csrfInput);
    form.appendChild(confirmTextInput);
    document.body.appendChild(form);
    form.submit();
}

// ============================================================================
// Global Event Handlers
// ============================================================================

/**
 * Close modal on ESC key
 */
document.addEventListener('keydown', (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
        hideDeleteAccountModal();
    }
});

// ============================================================================
// Global Exports
// ============================================================================

declare global {
    interface Window {
        showDeleteAccountModal: typeof showDeleteAccountModal;
        hideDeleteAccountModal: typeof hideDeleteAccountModal;
        checkDeleteAccountInput: typeof checkDeleteAccountInput;
        submitDeleteAccount: typeof submitDeleteAccount;
    }
}

// Export functions to global scope for HTML onclick handlers
if (typeof window !== 'undefined') {
    window.showDeleteAccountModal = showDeleteAccountModal;
    window.hideDeleteAccountModal = hideDeleteAccountModal;
    window.checkDeleteAccountInput = checkDeleteAccountInput;
    window.submitDeleteAccount = submitDeleteAccount;
}

// Make this file a module to allow global augmentation
export {};
