// Security alert detail page functionality
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
    function dismissAlert() {
        const reason = prompt('Reason for dismissing this alert (optional):');
        if (reason !== null) {
            const container = document.querySelector('.container-fluid');
            if (!container) {
                alert('Error: Container element not found');
                return;
            }
            const dismissUrl = container.dataset.alertDismissUrl;
            if (!dismissUrl) {
                alert('Error: Dismiss URL not found');
                return;
            }
            const csrfToken = getCookie('csrftoken');
            if (!csrfToken) {
                alert('Error: CSRF token not found');
                return;
            }
            fetch(dismissUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'reason=' + encodeURIComponent(reason)
            })
                .then((response) => response.json())
                .then((data) => {
                if (data.success) {
                    location.reload();
                }
                else {
                    alert('Failed to dismiss alert: ' + (data.error || 'Unknown error'));
                }
            })
                .catch((error) => {
                console.error('Error dismissing alert:', error);
                alert('Error dismissing alert: ' + error.message);
            });
        }
    }
    function reopenAlert() {
        const container = document.querySelector('.container-fluid');
        if (!container) {
            alert('Error: Container element not found');
            return;
        }
        const reopenUrl = container.dataset.alertReopenUrl;
        if (!reopenUrl) {
            alert('Error: Reopen URL not found');
            return;
        }
        const csrfToken = getCookie('csrftoken');
        if (!csrfToken) {
            alert('Error: CSRF token not found');
            return;
        }
        fetch(reopenUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
        })
            .then((response) => response.json())
            .then((data) => {
            if (data.success) {
                location.reload();
            }
            else {
                alert('Failed to reopen alert: ' + (data.error || 'Unknown error'));
            }
        })
            .catch((error) => {
            console.error('Error reopening alert:', error);
            alert('Error reopening alert: ' + error.message);
        });
    }
    function createFixPR() {
        alert('Automatic fix PR creation is not yet implemented');
    }
    // Expose functions to global scope for HTML onclick handlers
    window.dismissAlert = dismissAlert;
    window.reopenAlert = reopenAlert;
    window.createFixPR = createFixPR;
})();
//# sourceMappingURL=security_alert_detail.js.map