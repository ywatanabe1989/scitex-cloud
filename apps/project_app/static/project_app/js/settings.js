// Project Settings JavaScript
// Radio button selection visual feedback
document.querySelectorAll('.radio-option input[type="radio"]').forEach(radio => {
    radio.addEventListener('change', function() {
        document.querySelectorAll('.radio-option').forEach(opt => opt.classList.remove('selected'));
        this.closest('.radio-option').classList.add('selected');
    });
});

// Handle section-specific form submissions
// This prevents HTML5 validation errors from other sections when submitting one section
document.addEventListener('DOMContentLoaded', function() {
    // Get all submit buttons with name="action"
    const submitButtons = document.querySelectorAll('button[type="submit"][name="action"]');

    submitButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const actionValue = this.value;

            // For visibility and general updates, disable validation on collaborator field
            if (actionValue === 'update_visibility' || actionValue === 'update_general') {
                const collaboratorInput = document.getElementById('collaboratorUsername');
                if (collaboratorInput) {
                    // Temporarily remove required attribute
                    collaboratorInput.removeAttribute('required');

                    // Re-add it after a short delay (after form submission)
                    setTimeout(() => {
                        collaboratorInput.setAttribute('required', 'required');
                    }, 100);
                }
            }

            // For add_collaborator, make sure the field is required
            if (actionValue === 'add_collaborator') {
                const collaboratorInput = document.getElementById('collaboratorUsername');
                if (collaboratorInput) {
                    collaboratorInput.setAttribute('required', 'required');
                }
            }
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
    const addCollaboratorBtn = document.getElementById('addCollaboratorBtn');
    const collaboratorUsername = document.getElementById('collaboratorUsername');
    const addBtnText = document.getElementById('addBtnText');

    if (addCollaboratorBtn && collaboratorUsername) {
        // Show loading state when form submits via this button
        addCollaboratorBtn.addEventListener('click', function(e) {
            const username = collaboratorUsername.value.trim();
            if (username) {
                addBtnText.textContent = 'Adding...';
                addCollaboratorBtn.disabled = true;
                addCollaboratorBtn.style.opacity = '0.7';
                console.log('Adding collaborator:', username);
            } else {
                e.preventDefault();
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
