// Pull request conversation functionality

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

function submitComment() {
    const form = document.getElementById('commentForm');
    const formData = new FormData(form);
    const commentUrl = form.dataset.commentUrl;
    const csrfToken = getCookie('csrftoken');

    fetch(commentUrl, {
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
        alert('Error submitting comment: ' + error.message);
    });
}

function submitReview(state) {
    const form = document.getElementById('commentForm');
    const formData = new FormData(form);
    formData.append('state', state);
    const reviewUrl = form.dataset.reviewUrl;
    const csrfToken = getCookie('csrftoken');

    fetch(reviewUrl, {
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
        alert('Error submitting review: ' + error.message);
    });
}
