// Account Settings JavaScript

// Debug: Log when script loads
console.log('Account settings JS loaded');

// Add form submission debugging
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const action = this.querySelector('input[name="action"]');
            console.log('Form submitted, action:', action ? action.value : 'none');
        });
    });
});

// Password Validation (same as signup page)
document.addEventListener('DOMContentLoaded', function() {
    const newPasswordInput = document.getElementById('new_password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const changePasswordForm = document.querySelector('form[action*="change_password"], form input[name="action"][value="change_password"]').closest('form');

    if (newPasswordInput && changePasswordForm) {
        // Add password requirements display
        const requirementsDiv = document.createElement('div');
        requirementsDiv.className = 'password-rules';
        requirementsDiv.style.cssText = 'background-color: var(--color-canvas-subtle); border: 1px solid var(--color-border-default); border-radius: 8px; padding: 1rem; font-size: 0.9rem; margin-top: 0.5rem;';
        requirementsDiv.innerHTML = `
            <div style="font-weight: 600; color: var(--color-fg-default); margin-bottom: 0.5rem; font-size: 0.95rem;">Password Requirements:</div>
            <div class="password-rule" id="rule-length" style="margin-bottom: 0.4rem; color: #dc3545; display: flex; align-items: center; transition: color 0.3s ease;">
                <i class="fas fa-circle" style="margin-right: 0.5rem; width: 16px; font-size: 0.75rem;"></i> At least 8 characters
            </div>
            <div class="password-rule" id="rule-lowercase" style="margin-bottom: 0.4rem; color: #dc3545; display: flex; align-items: center; transition: color 0.3s ease;">
                <i class="fas fa-circle" style="margin-right: 0.5rem; width: 16px; font-size: 0.75rem;"></i> At least one lowercase letter
            </div>
            <div class="password-rule" id="rule-uppercase" style="margin-bottom: 0.4rem; color: #dc3545; display: flex; align-items: center; transition: color 0.3s ease;">
                <i class="fas fa-circle" style="margin-right: 0.5rem; width: 16px; font-size: 0.75rem;"></i> At least one uppercase letter
            </div>
            <div class="password-rule" id="rule-number" style="margin-bottom: 0.4rem; color: #dc3545; display: flex; align-items: center; transition: color 0.3s ease;">
                <i class="fas fa-circle" style="margin-right: 0.5rem; width: 16px; font-size: 0.75rem;"></i> At least one number
            </div>
            <div class="password-rule" id="rule-special" style="margin-bottom: 0.4rem; color: #dc3545; display: flex; align-items: center; transition: color 0.3s ease;">
                <i class="fas fa-circle" style="margin-right: 0.5rem; width: 16px; font-size: 0.75rem;"></i> At least one special character (!@#$%^&*)
            </div>
        `;

        // Insert after new password input
        newPasswordInput.parentElement.appendChild(requirementsDiv);

        // Real-time validation
        newPasswordInput.addEventListener('input', function() {
            const password = this.value;

            const ruleLength = document.getElementById('rule-length');
            const ruleLowercase = document.getElementById('rule-lowercase');
            const ruleUppercase = document.getElementById('rule-uppercase');
            const ruleNumber = document.getElementById('rule-number');
            const ruleSpecial = document.getElementById('rule-special');

            // Check length
            updateRule(ruleLength, password.length >= 8, password.length > 0);

            // Check lowercase
            updateRule(ruleLowercase, /[a-z]/.test(password), password.length > 0);

            // Check uppercase
            updateRule(ruleUppercase, /[A-Z]/.test(password), password.length > 0);

            // Check number
            updateRule(ruleNumber, /\d/.test(password), password.length > 0);

            // Check special character
            updateRule(ruleSpecial, /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password), password.length > 0);
        });
    }
});

function updateRule(element, isValid, hasInput) {
    if (isValid) {
        element.style.color = '#28a745';  // Green
        element.classList.add('valid');
        element.querySelector('i').className = 'fas fa-check';
    } else {
        element.style.color = '#dc3545';  // Red
        element.classList.remove('valid');
        element.querySelector('i').className = hasInput ? 'fas fa-times' : 'fas fa-circle';
    }
}

// Delete Account Modal Functions

function showDeleteAccountModal() {
    console.log('showDeleteAccountModal called');
    const modal = document.getElementById('deleteAccountModal');
    console.log('Modal element:', modal);
    if (modal) {
        modal.style.display = 'flex';
        document.getElementById('deleteAccountConfirmInput').value = '';
        document.getElementById('deleteAccountConfirmButton').disabled = true;
        console.log('Modal displayed');
    } else {
        console.error('Delete account modal not found!');
    }
}

function hideDeleteAccountModal() {
    document.getElementById('deleteAccountModal').style.display = 'none';
}

function checkDeleteAccountInput() {
    const input = document.getElementById('deleteAccountConfirmInput');
    const button = document.getElementById('deleteAccountConfirmButton');
    const expectedValue = input.getAttribute('data-username');

    if (input.value === expectedValue) {
        button.disabled = false;
        button.style.opacity = '1';
    } else {
        button.disabled = true;
        button.style.opacity = '0.5';
    }
}

function submitDeleteAccount() {
    const deleteUrl = document.getElementById('deleteAccountConfirmButton').getAttribute('data-delete-url');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const username = document.getElementById('deleteAccountConfirmInput').getAttribute('data-username');

    const form = document.createElement('form');
    form.method = 'POST';
    form.action = deleteUrl;

    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;

    const confirmInput = document.createElement('input');
    confirmInput.type = 'hidden';
    confirmInput.name = 'confirm_text';
    confirmInput.value = `delete ${username}`;

    form.appendChild(csrfInput);
    form.appendChild(confirmInput);
    document.body.appendChild(form);
    form.submit();
}

// Close modal on ESC key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        hideDeleteAccountModal();
    }
});
