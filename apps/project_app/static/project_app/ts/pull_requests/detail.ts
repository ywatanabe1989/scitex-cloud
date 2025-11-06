// Pull Request Detail Page JavaScript
// Functions for merging, closing, and reopening pull requests
<<<<<<<< HEAD:apps/project_app/static/project_app/js-potentially-legacy/pull_requests/detail.js
console.log("[DEBUG] apps/project_app/static/project_app/ts/pull_requests/detail.ts loaded");
========


console.log("[DEBUG] apps/project_app/static/project_app/ts/pull_requests/detail.ts loaded");

>>>>>>>> feat/writer-visitor-access-and-optimizations:apps/project_app/static/project_app/ts/pull_requests/detail.ts
function submitMerge() {
    const form = document.getElementById('mergeForm') as HTMLFormElement;
    const formData = new FormData(form);
    // Get CSRF token
<<<<<<<< HEAD:apps/project_app/static/project_app/js-potentially-legacy/pull_requests/detail.js
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    // Get URL from data attribute (set in template)
    const mergeUrl = document.getElementById('mergeModal').dataset.mergeUrl;
========
    const csrfToken = (document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement).value;

    // Get URL from data attribute (set in template)
    const mergeModal = document.getElementById('mergeModal') as HTMLElement | null;
    const mergeUrl = mergeModal?.dataset.mergeUrl;

    if (!mergeUrl) {
        alert('Error: Merge URL not found');
        return;
    }

>>>>>>>> feat/writer-visitor-access-and-optimizations:apps/project_app/static/project_app/ts/pull_requests/detail.ts
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
        }
        else {
            alert('Error: ' + data.error);
        }
    })
        .catch(error => {
        alert('Error: ' + error);
    });
}
function closePR() {
    if (!confirm('Are you sure you want to close this pull request?'))
        return;
    // Get CSRF token
<<<<<<<< HEAD:apps/project_app/static/project_app/js-potentially-legacy/pull_requests/detail.js
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    // Get URL from data attribute (set in template)
    const closeUrl = document.body.dataset.prCloseUrl;
========
    const csrfToken = (document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement).value;

    // Get URL from data attribute (set in template)
    const closeUrl = document.body.dataset.prCloseUrl;

    if (!closeUrl) {
        alert('Error: Close URL not found');
        return;
    }

>>>>>>>> feat/writer-visitor-access-and-optimizations:apps/project_app/static/project_app/ts/pull_requests/detail.ts
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
        }
        else {
            alert('Error: ' + data.error);
        }
    });
}
function reopenPR() {
    // Get CSRF token
<<<<<<<< HEAD:apps/project_app/static/project_app/js-potentially-legacy/pull_requests/detail.js
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    // Get URL from data attribute (set in template)
    const reopenUrl = document.body.dataset.prReopenUrl;
========
    const csrfToken = (document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement).value;

    // Get URL from data attribute (set in template)
    const reopenUrl = document.body.dataset.prReopenUrl;

    if (!reopenUrl) {
        alert('Error: Reopen URL not found');
        return;
    }

>>>>>>>> feat/writer-visitor-access-and-optimizations:apps/project_app/static/project_app/ts/pull_requests/detail.ts
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
        }
        else {
            alert('Error: ' + data.error);
        }
    });
}
//# sourceMappingURL=detail.js.map