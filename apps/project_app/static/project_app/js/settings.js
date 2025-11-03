// Project Settings JavaScript

// ===== DEBUG LOGGING =====
const DEBUG = true;
const log = (msg, data) => DEBUG && console.log(`[Settings] ${msg}`, data || '');
const logError = (msg, err) => console.error(`[Settings ERROR] ${msg}`, err || '');
const logWarn = (msg, data) => console.warn(`[Settings WARN] ${msg}`, data || '');

log('Settings.js loaded');

// Section navigation - show only one section at a time
function switchSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.settings-section-wrapper').forEach(wrapper => {
        wrapper.style.display = 'none';
    });

    // Show the selected section
    const selectedSection = document.getElementById(`section-${sectionId}`);
    if (selectedSection) {
        selectedSection.style.display = 'block';
    }

    // Update active nav button
    document.querySelectorAll('.settings-nav-item').forEach(item => {
        item.classList.remove('active');
    });
    const activeBtn = document.querySelector(`[data-section="${sectionId}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
}

// Add click handlers to nav buttons and radio button feedback
document.addEventListener('DOMContentLoaded', function() {
    // Section navigation click handlers
    document.querySelectorAll('.settings-nav-item').forEach(button => {
        if (!button.disabled) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const sectionId = this.getAttribute('data-section');
                switchSection(sectionId);
            });
        }
    });

    // Radio button selection visual feedback
    document.querySelectorAll('.radio-option input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', function() {
            document.querySelectorAll('.radio-option').forEach(opt => opt.classList.remove('selected'));
            this.closest('.radio-option').classList.add('selected');
        });
    });
});

// Handle section-specific form submissions
// This prevents HTML5 validation errors from other sections when submitting one section
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('settingsForm');
    if (!form) return;

    // Get all submit buttons with name="action"
    const submitButtons = form.querySelectorAll('button[type="submit"][name="action"]');

    submitButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const actionValue = this.value;

            // Temporarily disable validation on non-active fields
            const nameInput = document.getElementById('name');
            const collaboratorInput = document.getElementById('collaboratorUsername');

            // Remove required from all fields first
            if (nameInput) nameInput.removeAttribute('required');
            if (collaboratorInput) collaboratorInput.removeAttribute('required');

            // Add required back only to the field needed for this action
            if (actionValue === 'update_general' && nameInput) {
                nameInput.setAttribute('required', 'required');
            } else if (actionValue === 'add_collaborator' && collaboratorInput) {
                collaboratorInput.setAttribute('required', 'required');
            }

            // Re-add required attributes after submission
            setTimeout(() => {
                if (nameInput) nameInput.setAttribute('required', 'required');
                if (collaboratorInput) collaboratorInput.setAttribute('required', 'required');
            }, 100);
        });
    });
});

// GitHub-style Delete Modal
function showDeleteModal() {
    console.log('showDeleteModal called');
    const modal = document.getElementById('deleteModal');
    console.log('Modal element:', modal);
    if (modal) {
        modal.style.display = 'flex';
        document.getElementById('deleteConfirmInput').value = '';
        document.getElementById('deleteConfirmButton').disabled = true;
        console.log('Modal displayed');
    } else {
        console.error('Delete modal not found!');
    }
}

function hideDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
}

function checkDeleteInput() {
    const input = document.getElementById('deleteConfirmInput');
    const button = document.getElementById('deleteConfirmButton');
    const expectedValue = input.getAttribute('data-confirm-text');

    if (input.value === expectedValue) {
        button.disabled = false;
        button.style.opacity = '1';
    } else {
        button.disabled = true;
        button.style.opacity = '0.5';
    }
}

function submitDelete() {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = window.location.href;

    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const actionInput = document.createElement('input');
    actionInput.type = 'hidden';
    actionInput.name = 'action';
    actionInput.value = 'delete_repository';

    form.appendChild(csrfInput);
    form.appendChild(actionInput);
    document.body.appendChild(form);
    form.submit();
}

// Close modal on ESC key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        hideDeleteModal();
    }
});

// Add collaborator button feedback
document.addEventListener('DOMContentLoaded', function() {
    // Handle hash navigation (e.g., #collaborators)
    if (window.location.hash) {
        const hash = window.location.hash.substring(1); // Remove #
        const navLink = document.querySelector(`[data-section="${hash}"]`);
        if (navLink) {
            navLink.click(); // Trigger section switch
        }
    }

    // Add form submit listener for debugging
    const settingsForm = document.getElementById('settingsForm');
    if (settingsForm) {
        settingsForm.addEventListener('submit', function(e) {
            const formData = new FormData(this);
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            log('FORM SUBMIT EVENT', {
                action: this.action,
                method: this.method,
                data: data,
                validity: this.checkValidity(),
                reportValidity: this.reportValidity()
            });

            // Check if form is valid
            if (!this.checkValidity()) {
                logError('FORM VALIDATION FAILED', {
                    invalidFields: Array.from(this.querySelectorAll(':invalid')).map(el => el.name)
                });
                e.preventDefault();
                return false;
            }

            log('FORM IS SUBMITTING NOW - Watch Network tab for POST request');
        });
    }

    const addCollaboratorBtn = document.getElementById('addCollaboratorBtn');
    const collaboratorUsername = document.getElementById('collaboratorUsername');
    const addBtnText = document.getElementById('addBtnText');

    if (addCollaboratorBtn && collaboratorUsername) {
        log('Collaborator button initialized');

        // Show loading state when form submits via this button
        addCollaboratorBtn.addEventListener('click', function(e) {
            const username = collaboratorUsername.value.trim();
            const role = document.getElementById('collaboratorRole')?.value;
            const form = document.getElementById('settingsForm');

            log('Add collaborator button clicked', { username, role, hasForm: !!form });

            if (username) {
                // CRITICAL: Ensure action value is set before disabling button
                // Browsers may not submit disabled button values
                let actionInput = form.querySelector('input[name="action"][type="hidden"]');
                if (!actionInput) {
                    actionInput = document.createElement('input');
                    actionInput.type = 'hidden';
                    actionInput.name = 'action';
                    form.appendChild(actionInput);
                }
                actionInput.value = 'add_collaborator';
                log('Set hidden action input', { value: actionInput.value });

                addBtnText.textContent = 'Adding...';
                addCollaboratorBtn.disabled = true;
                addCollaboratorBtn.style.opacity = '0.7';

                // Get form data for debugging
                const formData = new FormData(form);
                const formDataObj = {};
                for (let [key, value] of formData.entries()) {
                    formDataObj[key] = value;
                }

                log('Submitting form', {
                    action: form?.action,
                    method: form?.method,
                    currentURL: window.location.href,
                    formFields: formDataObj
                });
            } else {
                e.preventDefault();
                logWarn('Empty username, preventing submission');
                alert('Please enter a username');
            }
        });

        // Reset button when username input changes
        collaboratorUsername.addEventListener('input', function() {
            if (addCollaboratorBtn.disabled) {
                addBtnText.textContent = 'Add collaborator';
                addCollaboratorBtn.disabled = false;
                addCollaboratorBtn.style.opacity = '1';
            }
        });
    }
});
