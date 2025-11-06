"use strict";
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
    const forms = document.querySelectorAll('form');
    forms.forEach((form) => {
        form.addEventListener('submit', function () {
            const action = this.querySelector('input[name="action"]');
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
    const toggleButtons = document.querySelectorAll('.toggle-password');
    toggleButtons.forEach((button) => {
        button.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            if (!targetId)
                return;
            const passwordInput = document.getElementById(targetId);
            const icon = this.querySelector('i');
            if (passwordInput && icon) {
                const currentType = passwordInput.getAttribute('type');
                const newType = currentType === 'password' ? 'text' : 'password';
                passwordInput.setAttribute('type', newType);
                // Toggle the eye icon
                if (newType === 'password') {
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
                else {
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
function updatePasswordRule(element, isValid, hasInput) {
    element.classList.remove('valid', 'invalid');
    const icon = element.querySelector('i');
    if (!icon)
        return;
    if (isValid) {
        element.classList.add('valid');
        icon.className = 'fas fa-check';
    }
    else {
        // Invalid state: red X (default)
        element.classList.add('invalid');
        icon.className = 'fas fa-times';
    }
}
/**
 * Validate password requirements
 */
function validatePasswordRequirements(password) {
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
    const newPasswordInput = document.getElementById('new_password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    // Find the change password form
    const actionInput = document.querySelector('form input[name="action"][value="change_password"]');
    const changePasswordForm = actionInput?.closest('form');
    if (newPasswordInput && changePasswordForm) {
        // Create password requirements display
        const requirementsDiv = document.createElement('div');
        requirementsDiv.className = 'password-rules';
        requirementsDiv.innerHTML = `
            <div class="password-rules-title">Password Requirements:</div>
            <div class="password-rule invalid" id="rule-length"><i class="fas fa-times"></i> At least 8 characters</div>
            <div class="password-rule invalid" id="rule-lowercase"><i class="fas fa-times"></i> At least one lowercase letter</div>
            <div class="password-rule invalid" id="rule-uppercase"><i class="fas fa-times"></i> At least one uppercase letter</div>
            <div class="password-rule invalid" id="rule-number"><i class="fas fa-times"></i> At least one number</div>
            <div class="password-rule invalid" id="rule-special"><i class="fas fa-times"></i> At least one special character (!@#$%^&*)</div>
        `;
        // Insert after new password input group
        const inputGroup = newPasswordInput.parentElement;
        const formGroup = inputGroup?.parentElement;
        if (formGroup) {
            formGroup.appendChild(requirementsDiv);
        }
        // Real-time validation
        newPasswordInput.addEventListener('input', function () {
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
function showDeleteAccountModal() {
    console.log('showDeleteAccountModal called');
    const modal = document.getElementById('deleteAccountModal');
    console.log('Modal element:', modal);
    if (modal) {
        modal.style.display = 'flex';
        const confirmInput = document.getElementById('deleteAccountConfirmInput');
        const confirmButton = document.getElementById('deleteAccountConfirmButton');
        if (confirmInput) {
            confirmInput.value = '';
        }
        if (confirmButton) {
            confirmButton.disabled = true;
        }
        console.log('Modal displayed');
    }
    else {
        console.error('Delete account modal not found!');
    }
}
/**
 * Hide delete account confirmation modal
 */
function hideDeleteAccountModal() {
    const modal = document.getElementById('deleteAccountModal');
    if (modal) {
        modal.style.display = 'none';
    }
}
/**
 * Check delete account confirmation input
 */
function checkDeleteAccountInput() {
    const input = document.getElementById('deleteAccountConfirmInput');
    const button = document.getElementById('deleteAccountConfirmButton');
    if (!input || !button)
        return;
    const expectedValue = input.getAttribute('data-username');
    if (input.value === expectedValue) {
        button.disabled = false;
        button.style.opacity = '1';
    }
    else {
        button.disabled = true;
        button.style.opacity = '0.5';
    }
}
/**
 * Submit delete account form
 */
function submitDeleteAccount() {
    const confirmButton = document.getElementById('deleteAccountConfirmButton');
    const confirmInput = document.getElementById('deleteAccountConfirmInput');
    const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
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
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        hideDeleteAccountModal();
    }
});
// Export functions to global scope for HTML onclick handlers
if (typeof window !== 'undefined') {
    window.showDeleteAccountModal = showDeleteAccountModal;
    window.hideDeleteAccountModal = hideDeleteAccountModal;
    window.checkDeleteAccountInput = checkDeleteAccountInput;
    window.submitDeleteAccount = submitDeleteAccount;
}
//# sourceMappingURL=account-settings.js.map