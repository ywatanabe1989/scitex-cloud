// Issue Detail Page JavaScript
// Functions for closing and reopening issues

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function closeIssue() {
    if (!confirm('Are you sure you want to close this issue?')) return;

    const closeUrl = document.body.dataset.issueCloseUrl;

    const response = await fetch(closeUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    });

    const data = await response.json();
    if (data.success) {
        location.reload();
    } else {
        alert(data.error || 'Failed to close issue');
    }
}

async function reopenIssue() {
    const reopenUrl = document.body.dataset.issueReopenUrl;

    const response = await fetch(reopenUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    });

    const data = await response.json();
    if (data.success) {
        location.reload();
    } else {
        alert(data.error || 'Failed to reopen issue');
    }
}
