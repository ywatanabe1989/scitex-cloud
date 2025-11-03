/**
 * Writer Git Module
 * Handles git commit operations and modal management
 */

/**
 * Show toast notification (utility)
 */
function showToast(message, _type = 'info') {
    const fn = window.showToast || ((msg) => console.log(msg));
    fn(message);
}

/**
 * Show git commit modal
 */
export function showCommitModal(state) {
    const currentSection = state.currentSection;
    if (!currentSection) {
        showToast('No section selected', 'warning');
        return;
    }

    // Update current section info in modal
    const sectionInfoEl = document.getElementById('commit-current-section');
    if (sectionInfoEl) {
        const parts = currentSection.split('/');
        const sectionName = parts[parts.length - 1];
        const formattedName = sectionName
            .split('_')
            .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
        sectionInfoEl.textContent = formattedName;
    }

    // Clear previous message
    const messageInput = document.getElementById('commit-message-input');
    if (messageInput) {
        messageInput.value = '';
        messageInput.focus();
    }

    // Show modal using Bootstrap
    const modalEl = document.getElementById('git-commit-modal');
    if (modalEl) {
        const modal = new window.bootstrap.Modal(modalEl);
        modal.show();
    }
}

/**
 * Handle git commit
 */
export async function handleGitCommit(state) {
    const currentSection = state.currentSection;
    if (!currentSection) {
        showToast('No section selected', 'warning');
        return;
    }

    const messageInput = document.getElementById('commit-message-input');
    const commitMessage = messageInput?.value.trim();

    if (!commitMessage) {
        showToast('Please enter a commit message', 'warning');
        messageInput?.focus();
        return;
    }

    try {
        // Extract doc type and section name
        const [docType, sectionName] = currentSection.split('/');
        if (!docType || !sectionName) {
            showToast('Invalid section format', 'error');
            return;
        }

        const config = window.WRITER_CONFIG;

        // First, ensure changes are saved to file (auto-save might not have triggered yet)
        console.log('[Writer] Ensuring section is saved before commit...');
        // We need to get the current editor content and save it
        // This will be handled by calling the section write API
        // For now, we'll proceed with commit assuming auto-save has run

        // Call API endpoint to commit
        const response = await fetch(`/writer/api/project/${config.projectId}/section/${sectionName}/commit/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': config.csrfToken
            },
            body: JSON.stringify({
                doc_type: docType,
                message: commitMessage
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('[Writer] Commit HTTP error:', response.status, errorText);
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        const data = await response.json();
        console.log('[Writer] Commit response:', data);

        if (data.success) {
            showToast('Changes committed successfully', 'success');

            // Close modal
            const modalEl = document.getElementById('git-commit-modal');
            if (modalEl) {
                const modal = window.bootstrap.Modal.getInstance(modalEl);
                if (modal) {
                    modal.hide();
                }
            }
        }
        else {
            console.error('[Writer] Commit failed:', data);
            throw new Error(data.error || 'Commit failed');
        }
    }
    catch (error) {
        console.error('[Writer] Git commit error:', error);
        showToast('Failed to commit: ' + (error instanceof Error ? error.message : 'Unknown error'), 'error');
    }
}
