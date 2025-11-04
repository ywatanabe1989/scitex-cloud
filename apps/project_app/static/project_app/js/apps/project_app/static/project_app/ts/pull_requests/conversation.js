// Pull request conversation functionality
(function () {
    'use strict';
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
        if (!form) {
            console.error('Comment form not found');
            return;
        }
        const formData = new FormData(form);
        const commentUrl = form.dataset.commentUrl;
        if (!commentUrl) {
            console.error('Comment URL not found');
            return;
        }
        const csrfToken = getCookie('csrftoken');
        if (!csrfToken) {
            console.error('CSRF token not found');
            return;
        }
        fetch(commentUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            body: formData
        })
            .then(response => response.json())
            .then((data) => {
            if (data.success) {
                window.location.reload();
            }
            else {
                alert('Error: ' + data.error);
            }
        })
            .catch((error) => {
            console.error('Error submitting comment:', error);
            alert('Error submitting comment: ' + error.message);
        });
    }
    function submitReview(state) {
        const form = document.getElementById('commentForm');
        if (!form) {
            console.error('Comment form not found');
            return;
        }
        const formData = new FormData(form);
        formData.append('state', state);
        const reviewUrl = form.dataset.reviewUrl;
        if (!reviewUrl) {
            console.error('Review URL not found');
            return;
        }
        const csrfToken = getCookie('csrftoken');
        if (!csrfToken) {
            console.error('CSRF token not found');
            return;
        }
        fetch(reviewUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            body: formData
        })
            .then(response => response.json())
            .then((data) => {
            if (data.success) {
                window.location.reload();
            }
            else {
                alert('Error: ' + data.error);
            }
        })
            .catch((error) => {
            console.error('Error submitting review:', error);
            alert('Error submitting review: ' + error.message);
        });
    }
    // Expose functions to global scope for use in HTML onclick attributes
    window.submitComment = submitComment;
    window.submitReview = submitReview;
})();
//# sourceMappingURL=conversation.js.map