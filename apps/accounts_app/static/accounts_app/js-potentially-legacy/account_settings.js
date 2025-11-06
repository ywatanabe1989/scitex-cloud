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

// Password Toggle Functionality (matching signup page)
document.addEventListener('DOMContentLoaded', function() {
    const toggleButtons = document.querySelectorAll('.toggle-password');

    toggleButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const passwordInput = document.getElementById(targetId);
            const icon = this.querySelector('i');

            if (passwordInput) {
                const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
                passwordInput.setAttribute('type', type);

                // Toggle the eye icon
                if (type === 'password') {
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

// Password Validation (same as signup page)
document.addEventListener('DOMContentLoaded', function() {
    const newPasswordInput = document.getElementById('new_password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const changePasswordForm = document.querySelector('form[action*="change_password"], form input[name="action"][value="change_password"]').closest('form');

    if (newPasswordInput && changePasswordForm) {
        // Add password requirements display
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

        // Insert after new password input group (parent is .input-group, parent.parent is .form-group)
        newPasswordInput.parentElement.parentElement.appendChild(requirementsDiv);

        // Real-time validation
        newPasswordInput.addEventListener('input', function() {
            const password = this.value;
            const hasInput = password.length > 0;

            const ruleLength = document.getElementById('rule-length');
            const ruleLowercase = document.getElementById('rule-lowercase');
            const ruleUppercase = document.getElementById('rule-uppercase');
            const ruleNumber = document.getElementById('rule-number');
            const ruleSpecial = document.getElementById('rule-special');

            // Check length
            updatePasswordRule(ruleLength, password.length >= 8, hasInput);

            // Check lowercase
            updatePasswordRule(ruleLowercase, /[a-z]/.test(password), hasInput);

            // Check uppercase
            updatePasswordRule(ruleUppercase, /[A-Z]/.test(password), hasInput);

            // Check number
            updatePasswordRule(ruleNumber, /\d/.test(password), hasInput);

            // Check special character
            updatePasswordRule(ruleSpecial, /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password), hasInput);
        });
    }
});

// Helper function to update password rule state (matching signup page)
function updatePasswordRule(element, isValid, hasInput) {
    element.classList.remove('valid', 'invalid');
    if (isValid) {
        element.style.color = '#28a745';  // Green
        element.classList.add('valid');
        element.querySelector('i').className = 'fas fa-check';
    } else if (hasInput) {
        element.style.color = '#dc3545';  // Red
        element.classList.add('invalid');
        element.querySelector('i').className = 'fas fa-times';
    } else {
        element.style.color = '#6c757d';  // Gray
        element.querySelector('i').className = 'fas fa-circle';
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
