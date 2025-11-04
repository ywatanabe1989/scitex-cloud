// Pull Request Detail Page JavaScript
// Functions for merging, closing, and reopening pull requests

function submitMerge() {
    const form = document.getElementById('mergeForm');
    const formData = new FormData(form);

    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Get URL from data attribute (set in template)
    const mergeUrl = document.getElementById('mergeModal').dataset.mergeUrl;

    fetch(mergeUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
        },
        body: formData
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
        alert('Error: ' + error);
    });
}

function closePR() {
    if (!confirm('Are you sure you want to close this pull request?')) return;

    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Get URL from data attribute (set in template)
    const closeUrl = document.body.dataset.prCloseUrl;

    fetch(closeUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.reload();
        } else {
            alert('Error: ' + data.error);
        }
    });
}

function reopenPR() {
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Get URL from data attribute (set in template)
    const reopenUrl = document.body.dataset.prReopenUrl;

    fetch(reopenUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.reload();
        } else {
            alert('Error: ' + data.error);
        }
    });
}
