// Security Scan Button Handler
// Triggers a security scan via AJAX and displays results

document.addEventListener('DOMContentLoaded', function() {
    const runScanBtn = document.getElementById('runScanBtn');

    if (runScanBtn) {
        // Get CSRF token and API URL from data attributes
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const apiUrl = runScanBtn.dataset.scanUrl;

        runScanBtn.addEventListener('click', function() {
            const btn = this;
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Scanning...';

            fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`Scan completed!\nCritical: ${data.alerts.critical}\nHigh: ${data.alerts.high}\nMedium: ${data.alerts.medium}\nLow: ${data.alerts.low}`);
                    location.reload();
                } else {
                    alert('Scan failed: ' + (data.error || 'Unknown error'));
                    btn.disabled = false;
                    btn.innerHTML = 'Run security scan';
                }
            })
            .catch(error => {
                alert('Error running scan: ' + error);
                btn.disabled = false;
                btn.innerHTML = 'Run security scan';
            });
        });
    }
});
