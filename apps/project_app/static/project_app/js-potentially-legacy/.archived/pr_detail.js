"use strict";
// Pull Request Detail Page JavaScript
// Functions for merging, closing, and reopening pull requests
<<<<<<<< HEAD:.tsbuild/apps/project_app/static/project_app/ts/pull_requests/detail.js
console.log("[DEBUG] apps/project_app/static/project_app/ts/pull_requests/detail.ts loaded");
========
>>>>>>>> feat/writer-visitor-access-and-optimizations:apps/project_app/static/project_app/js-potentially-legacy/.archived/pr_detail.js
function submitMerge() {
    const form = document.getElementById('mergeForm');
    const formData = new FormData(form);
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    // Get URL from data attribute (set in template)
<<<<<<<< HEAD:.tsbuild/apps/project_app/static/project_app/ts/pull_requests/detail.js
    const mergeModal = document.getElementById('mergeModal');
    const mergeUrl = mergeModal?.dataset.mergeUrl;
    if (!mergeUrl) {
        alert('Error: Merge URL not found');
        return;
    }
========
    const mergeUrl = document.getElementById('mergeModal').dataset.mergeUrl;
>>>>>>>> feat/writer-visitor-access-and-optimizations:apps/project_app/static/project_app/js-potentially-legacy/.archived/pr_detail.js
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
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    // Get URL from data attribute (set in template)
    const closeUrl = document.body.dataset.prCloseUrl;
<<<<<<<< HEAD:.tsbuild/apps/project_app/static/project_app/ts/pull_requests/detail.js
    if (!closeUrl) {
        alert('Error: Close URL not found');
        return;
    }
========
>>>>>>>> feat/writer-visitor-access-and-optimizations:apps/project_app/static/project_app/js-potentially-legacy/.archived/pr_detail.js
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
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    // Get URL from data attribute (set in template)
    const reopenUrl = document.body.dataset.prReopenUrl;
<<<<<<<< HEAD:.tsbuild/apps/project_app/static/project_app/ts/pull_requests/detail.js
    if (!reopenUrl) {
        alert('Error: Reopen URL not found');
        return;
    }
========
>>>>>>>> feat/writer-visitor-access-and-optimizations:apps/project_app/static/project_app/js-potentially-legacy/.archived/pr_detail.js
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
<<<<<<<< HEAD:.tsbuild/apps/project_app/static/project_app/ts/pull_requests/detail.js
//# sourceMappingURL=detail.js.map
========
//# sourceMappingURL=pr_detail.js.map
>>>>>>>> feat/writer-visitor-access-and-optimizations:apps/project_app/static/project_app/js-potentially-legacy/.archived/pr_detail.js
