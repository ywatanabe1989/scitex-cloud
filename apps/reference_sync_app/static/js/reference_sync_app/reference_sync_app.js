/**
 * Reference Sync App JavaScript
 * Handles OAuth flows, sync operations, conflict resolution, and real-time updates
 */

// Main application object
const ReferenceSyncApp = {
    // Configuration
    config: {
        syncStatusCheckInterval: 5000, // 5 seconds
        maxRetries: 3,
        retryDelay: 1000,
    },

    // State management
    state: {
        activeSyncSessions: new Set(),
        syncStatusTimers: new Map(),
        retryCount: new Map(),
    },

    // Initialize the application
    init() {
        this.bindEvents();
        this.checkActiveSyncs();
        this.initializeTooltips();
        this.setupCSRFToken();
    },

    // Bind event listeners
    bindEvents() {
        // OAuth connection buttons
        document.querySelectorAll('[data-action="connect-oauth"]').forEach(button => {
            button.addEventListener('click', this.handleOAuthConnect.bind(this));
        });

        // Sync action buttons
        document.querySelectorAll('[data-action="start-sync"]').forEach(button => {
            button.addEventListener('click', this.handleStartSync.bind(this));
        });

        // Conflict resolution forms
        document.querySelectorAll('[data-action="resolve-conflict"]').forEach(form => {
            form.addEventListener('submit', this.handleConflictResolution.bind(this));
        });

        // Auto-refresh checkboxes
        document.querySelectorAll('[data-action="toggle-auto-refresh"]').forEach(checkbox => {
            checkbox.addEventListener('change', this.handleAutoRefreshToggle.bind(this));
        });

        // File upload handlers
        document.querySelectorAll('[data-action="bulk-import"]').forEach(form => {
            form.addEventListener('submit', this.handleBulkImport.bind(this));
        });

        // Export handlers
        document.querySelectorAll('[data-action="bulk-export"]').forEach(form => {
            form.addEventListener('submit', this.handleBulkExport.bind(this));
        });
    },

    // Setup CSRF token for all AJAX requests
    setupCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (csrfToken) {
            // Set default headers for fetch requests
            this.defaultHeaders = {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            };
        }
    },

    // Initialize Bootstrap tooltips
    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    // Handle OAuth connection
    async handleOAuthConnect(event) {
        event.preventDefault();
        const button = event.target.closest('button');
        const service = button.dataset.service;
        
        if (!service) {
            this.showError('Service not specified');
            return;
        }

        try {
            this.setButtonLoading(button, true);
            
            const response = await fetch(`/reference-sync/accounts/connect/${service}/`, {
                method: 'POST',
                headers: this.defaultHeaders,
            });

            const data = await response.json();

            if (data.oauth_url) {
                // Redirect to OAuth provider
                window.location.href = data.oauth_url;
            } else {
                throw new Error(data.error || 'Failed to get OAuth URL');
            }

        } catch (error) {
            this.showError(`Failed to connect to ${service}: ${error.message}`);
            this.setButtonLoading(button, false);
        }
    },

    // Handle sync start
    async handleStartSync(event) {
        event.preventDefault();
        const button = event.target.closest('button');
        const profileId = button.dataset.profileId;

        if (!profileId) {
            this.showError('Profile ID not found');
            return;
        }

        if (!confirm('Start synchronization for this profile?')) {
            return;
        }

        try {
            this.setButtonLoading(button, true);

            const response = await fetch(`/reference-sync/profiles/${profileId}/sync/`, {
                method: 'POST',
                headers: this.defaultHeaders,
            });

            const data = await response.json();

            if (data.success) {
                this.showSuccess('Sync started successfully');
                
                // Add to active syncs and start monitoring
                this.state.activeSyncSessions.add(data.session_id);
                this.startSyncStatusMonitoring(data.session_id);
                
                // Redirect to session detail page
                setTimeout(() => {
                    window.location.href = `/reference-sync/sessions/${data.session_id}/`;
                }, 1000);

            } else {
                throw new Error(data.error || 'Sync failed to start');
            }

        } catch (error) {
            this.showError(`Failed to start sync: ${error.message}`);
            this.setButtonLoading(button, false);
        }
    },

    // Start monitoring sync status
    startSyncStatusMonitoring(sessionId) {
        const timer = setInterval(async () => {
            try {
                const response = await fetch(`/reference-sync/api/sync-status/${sessionId}/`);
                const data = await response.json();

                this.updateSyncStatus(sessionId, data);

                // Stop monitoring if sync is complete
                if (['completed', 'failed', 'cancelled'].includes(data.status)) {
                    this.stopSyncStatusMonitoring(sessionId);
                }

            } catch (error) {
                console.error('Failed to check sync status:', error);
                
                // Increment retry count
                const retries = this.state.retryCount.get(sessionId) || 0;
                if (retries >= this.config.maxRetries) {
                    this.stopSyncStatusMonitoring(sessionId);
                } else {
                    this.state.retryCount.set(sessionId, retries + 1);
                }
            }
        }, this.config.syncStatusCheckInterval);

        this.state.syncStatusTimers.set(sessionId, timer);
    },

    // Stop monitoring sync status
    stopSyncStatusMonitoring(sessionId) {
        const timer = this.state.syncStatusTimers.get(sessionId);
        if (timer) {
            clearInterval(timer);
            this.state.syncStatusTimers.delete(sessionId);
        }
        this.state.activeSyncSessions.delete(sessionId);
        this.state.retryCount.delete(sessionId);
    },

    // Update sync status in UI
    updateSyncStatus(sessionId, data) {
        // Update progress bars
        const progressBars = document.querySelectorAll(`[data-session-id="${sessionId}"] .progress-bar`);
        progressBars.forEach(bar => {
            bar.style.width = `${data.progress}%`;
            bar.setAttribute('aria-valuenow', data.progress);
        });

        // Update status badges
        const statusBadges = document.querySelectorAll(`[data-session-id="${sessionId}"] .sync-status`);
        statusBadges.forEach(badge => {
            badge.textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);
            badge.className = `sync-status ${data.status}`;
        });

        // Update counters
        this.updateCounter(`[data-session-id="${sessionId}"] .items-processed`, data.items_processed);
        this.updateCounter(`[data-session-id="${sessionId}"] .total-items`, data.total_items);
        this.updateCounter(`[data-session-id="${sessionId}"] .conflicts-found`, data.conflicts_found);
        this.updateCounter(`[data-session-id="${sessionId}"] .errors-count`, data.errors_count);

        // Show notifications for status changes
        if (data.status === 'completed') {
            this.showSuccess(`Sync completed: ${data.items_processed} items processed`);
        } else if (data.status === 'failed') {
            this.showError('Sync failed. Check the session details for more information.');
        }
    },

    // Update counter element
    updateCounter(selector, value) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            element.textContent = value;
        });
    },

    // Handle conflict resolution
    async handleConflictResolution(event) {
        event.preventDefault();
        const form = event.target;
        const conflictId = form.dataset.conflictId;
        const formData = new FormData(form);

        try {
            const response = await fetch(`/reference-sync/conflicts/${conflictId}/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.defaultHeaders['X-CSRFToken'],
                },
            });

            const data = await response.json();

            if (data.success) {
                this.showSuccess('Conflict resolved successfully');
                
                // Update UI to show resolved state
                const conflictElement = form.closest('.conflict-item');
                if (conflictElement) {
                    conflictElement.classList.add('resolved');
                    conflictElement.querySelector('.resolution-status').textContent = 'Resolved';
                }

                // Disable form
                const inputs = form.querySelectorAll('input, select, textarea, button');
                inputs.forEach(input => input.disabled = true);

            } else {
                throw new Error(data.error || 'Failed to resolve conflict');
            }

        } catch (error) {
            this.showError(`Failed to resolve conflict: ${error.message}`);
        }
    },

    // Handle auto-refresh toggle
    handleAutoRefreshToggle(event) {
        const checkbox = event.target;
        const interval = parseInt(checkbox.dataset.interval) || 30000;

        if (checkbox.checked) {
            this.startAutoRefresh(interval);
        } else {
            this.stopAutoRefresh();
        }
    },

    // Start auto-refresh
    startAutoRefresh(interval) {
        this.stopAutoRefresh(); // Clear any existing timer
        
        this.autoRefreshTimer = setInterval(() => {
            window.location.reload();
        }, interval);
    },

    // Stop auto-refresh
    stopAutoRefresh() {
        if (this.autoRefreshTimer) {
            clearInterval(this.autoRefreshTimer);
            this.autoRefreshTimer = null;
        }
    },

    // Handle bulk import
    async handleBulkImport(event) {
        event.preventDefault();
        const form = event.target;
        const fileInput = form.querySelector('input[type="file"]');
        
        if (!fileInput.files.length) {
            this.showError('Please select a file to import');
            return;
        }

        const file = fileInput.files[0];
        const maxSize = 10 * 1024 * 1024; // 10MB

        if (file.size > maxSize) {
            this.showError('File size cannot exceed 10MB');
            return;
        }

        try {
            const submitButton = form.querySelector('button[type="submit"]');
            this.setButtonLoading(submitButton, true);

            const formData = new FormData(form);
            
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.defaultHeaders['X-CSRFToken'],
                },
            });

            if (response.redirected) {
                window.location.href = response.url;
            } else {
                const data = await response.json();
                if (data.success) {
                    this.showSuccess(`Successfully imported ${data.count} references`);
                    form.reset();
                } else {
                    throw new Error(data.error || 'Import failed');
                }
            }

        } catch (error) {
            this.showError(`Import failed: ${error.message}`);
        } finally {
            const submitButton = form.querySelector('button[type="submit"]');
            this.setButtonLoading(submitButton, false);
        }
    },

    // Handle bulk export
    async handleBulkExport(event) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);

        try {
            const submitButton = form.querySelector('button[type="submit"]');
            this.setButtonLoading(submitButton, true);

            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.defaultHeaders['X-CSRFToken'],
                },
            });

            if (response.ok) {
                // Handle file download
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = this.getFilenameFromResponse(response) || 'export.zip';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);

                this.showSuccess('Export completed successfully');
            } else {
                const data = await response.json();
                throw new Error(data.error || 'Export failed');
            }

        } catch (error) {
            this.showError(`Export failed: ${error.message}`);
        } finally {
            const submitButton = form.querySelector('button[type="submit"]');
            this.setButtonLoading(submitButton, false);
        }
    },

    // Get filename from response headers
    getFilenameFromResponse(response) {
        const contentDisposition = response.headers.get('Content-Disposition');
        if (contentDisposition) {
            const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (match) {
                return match[1].replace(/['"]/g, '');
            }
        }
        return null;
    },

    // Check for active sync sessions on page load
    checkActiveSyncs() {
        const activeSyncElements = document.querySelectorAll('[data-session-status="running"]');
        activeSyncElements.forEach(element => {
            const sessionId = element.dataset.sessionId;
            if (sessionId) {
                this.state.activeSyncSessions.add(sessionId);
                this.startSyncStatusMonitoring(sessionId);
            }
        });
    },

    // Set button loading state
    setButtonLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || button.innerHTML;
        }
    },

    // Show success message
    showSuccess(message) {
        this.showToast(message, 'success');
    },

    // Show error message
    showError(message) {
        this.showToast(message, 'danger');
    },

    // Show toast notification
    showToast(message, type = 'info') {
        // Remove existing toasts
        const existingToasts = document.querySelectorAll('.toast');
        existingToasts.forEach(toast => toast.remove());

        // Create new toast
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;

        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '1055';
            document.body.appendChild(toastContainer);
        }

        // Add toast to container
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        // Initialize and show toast
        const toastElement = toastContainer.lastElementChild;
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: type === 'danger' ? 8000 : 5000,
        });
        toast.show();

        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    },

    // Utility: Format bytes
    formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    },

    // Utility: Format duration
    formatDuration(seconds) {
        if (seconds < 60) {
            return `${Math.round(seconds)}s`;
        } else if (seconds < 3600) {
            return `${Math.round(seconds / 60)}m`;
        } else {
            return `${Math.round(seconds / 3600)}h`;
        }
    },

    // Cleanup when page unloads
    cleanup() {
        // Clear all timers
        this.state.syncStatusTimers.forEach(timer => clearInterval(timer));
        this.state.syncStatusTimers.clear();
        
        if (this.autoRefreshTimer) {
            clearInterval(this.autoRefreshTimer);
        }
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    ReferenceSyncApp.init();
});

// Cleanup when page unloads
window.addEventListener('beforeunload', () => {
    ReferenceSyncApp.cleanup();
});

// Export for use in other scripts
window.ReferenceSyncApp = ReferenceSyncApp;