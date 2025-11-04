// Workflow Detail Page JavaScript
// Functions for triggering and toggling workflows

function triggerWorkflow() {
    if (!confirm('Run this workflow now?')) {
        return;
    }

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const triggerUrl = document.body.dataset.workflowTriggerUrl;

    fetch(triggerUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = data.run_url;
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        alert('Error triggering workflow: ' + error);
    });
}

function toggleWorkflow() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const toggleUrl = document.body.dataset.workflowToggleUrl;

    fetch(toggleUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.reload();
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        alert('Error toggling workflow: ' + error);
    });
}
