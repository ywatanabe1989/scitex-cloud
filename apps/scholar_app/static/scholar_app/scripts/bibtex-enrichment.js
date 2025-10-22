/**
 * BibTeX Enrichment Functionality
 *
 * Handles:
 * - File upload and job submission
 * - Job status polling
 * - Download functionality
 * - URL opening
 * - Diff/comparison display
 *
 * @requires CSRF token in page
 * @requires URL endpoints configured
 */

// Global state
let jobStatusInterval = null;
window.currentBibtexJobId = null;

/**
 * Initialize BibTeX enrichment system
 * @param {Object} config - Configuration
 */
function initBibtexEnrichment(config = {}) {
    const {
        formId = 'bibtexEnrichmentForm',
        fileInputId = 'bibtexFileInput',
        uploadUrl = '/scholar/bibtex/upload/',
    } = config;

    const form = document.getElementById(formId);
    const fileInput = document.getElementById(fileInputId);

    if (!form || !fileInput) {
        console.warn('BibTeX enrichment form not found');
        return;
    }

    // File input change handler
    fileInput.addEventListener('change', handleFileSelect);

    // Form submit handler
    form.addEventListener('submit', handleFormSubmit);

    // Drag and drop support
    setupDragAndDrop();
}

/**
 * Handle file selection
 */
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.name.endsWith('.bib')) {
        alert('Please select a .bib file');
        e.target.value = '';
        return;
    }

    // Show file name in UI
    const fileName = file.name;
    console.log('Selected file:', fileName);
}

/**
 * Handle form submission
 */
function handleFormSubmit(e, forceCancel = false) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Add force_cancel flag if user confirmed cancellation
    if (forceCancel) {
        formData.append('force_cancel', 'true');
    }

    // Show loading state
    showLoadingState();

    fetch(e.target.action, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken,
        },
        body: formData
    })
    .then(response => {
        if (response.status === 409) {
            // Conflict - existing job found, requires confirmation
            return response.json().then(data => {
                handleJobConflict(e.target, data);
                throw new Error('Conflict handled');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            window.currentBibtexJobId = data.job_id;
            startJobPolling(data.job_id);
        } else {
            showError(data.error || 'Upload failed');
            resetForm();
        }
    })
    .catch(error => {
        if (error.message === 'Conflict handled') {
            // This is expected, don't show error
            resetForm();
            return;
        }
        console.error('Upload error:', error);
        showError('Failed to upload file. Please try again.');
        resetForm();
    });
}

/**
 * Handle job conflict - ask user to cancel old job
 */
function handleJobConflict(form, data) {
    const existingJob = data.existing_job;
    const message = `You already have a job in progress:\n"${existingJob.filename}"\nProgress: ${existingJob.progress}%\n\nCancel it and start new job?`;

    if (confirm(message)) {
        // User confirmed - resubmit with force_cancel flag
        const event = new Event('submit', { bubbles: true, cancelable: true });
        handleFormSubmit.call(form, event, true);
    }
}

/**
 * Setup drag and drop
 */
function setupDragAndDrop() {
    const dropZone = document.getElementById('dropZone');
    if (!dropZone) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.style.borderColor = 'var(--scitex-color-03)';
            dropZone.style.background = 'var(--color-canvas-subtle)';
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.style.borderColor = 'var(--scitex-color-03)';
            dropZone.style.background = 'var(--color-canvas-default)';
        });
    });

    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            document.getElementById('bibtexFileInput').files = files;
            handleFileSelect({ target: { files } });
        }
    });
}

/**
 * Start polling job status
 * @param {string} jobId - Job UUID
 */
function startJobPolling(jobId) {
    // Clear any existing interval
    if (jobStatusInterval) {
        clearInterval(jobStatusInterval);
    }

    // Show progress area
    const progressArea = document.getElementById('progressArea');
    if (progressArea) {
        progressArea.style.display = 'block';
    }

    // Poll immediately, then every 2 seconds
    updateJobStatus(jobId);
    jobStatusInterval = setInterval(() => updateJobStatus(jobId), 2000);
}

/**
 * Update job status
 * @param {string} jobId - Job UUID
 */
function updateJobStatus(jobId) {
    fetch(`/scholar/api/bibtex/job/${jobId}/status/`)
        .then(response => response.json())
        .then(data => {
            updateProgressUI(data);

            // If completed or failed, stop polling
            if (data.status === 'completed' || data.status === 'failed') {
                stopJobPolling();
                handleJobComplete(data);
            }
        })
        .catch(error => {
            console.error('Status check error:', error);
        });
}

/**
 * Stop job polling
 */
function stopJobPolling() {
    if (jobStatusInterval) {
        clearInterval(jobStatusInterval);
        jobStatusInterval = null;
    }
}

/**
 * Update progress UI
 * @param {Object} data - Job status data
 */
function updateProgressUI(data) {
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const progressLog = document.getElementById('progressLog');

    if (progressBar) {
        progressBar.style.width = `${data.progress_percentage}%`;
    }

    if (progressText) {
        progressText.textContent = `${data.progress_percentage}% (${data.processed_papers}/${data.total_papers} papers)`;
    }

    if (progressLog && data.log) {
        progressLog.textContent = data.log;
        // Auto-scroll to bottom
        progressLog.scrollTop = progressLog.scrollHeight;
    }
}

/**
 * Handle job completion
 * @param {Object} data - Job status data
 */
function handleJobComplete(data) {
    if (data.status === 'completed' && data.has_output) {
        showDownloadArea(window.currentBibtexJobId);
    } else if (data.status === 'failed') {
        showError(data.error_message || 'Enrichment failed');
    }
}

/**
 * Show download area
 * @param {string} jobId - Job UUID
 */
function showDownloadArea(jobId) {
    const downloadArea = document.getElementById('downloadArea');
    const downloadBtn = document.getElementById('downloadBtn');
    const showDiffBtn = document.getElementById('showDiffBtn');
    const openUrlsBtn = document.getElementById('openUrlsBtn');

    if (downloadArea) {
        downloadArea.style.display = 'flex';
    }

    if (downloadBtn) {
        downloadBtn.href = `/scholar/api/bibtex/job/${jobId}/download/`;
    }

    // Fetch URL count for "Open All URLs" button
    if (openUrlsBtn) {
        fetch(`/scholar/api/bibtex/job/${jobId}/urls/`)
            .then(response => response.json())
            .then(data => {
                if (data.total_urls > 0) {
                    document.getElementById('urlCount').textContent = data.total_urls;
                }
            });
    }
}

/**
 * Open all paper URLs
 */
window.openAllPaperUrls = function() {
    const jobId = window.currentBibtexJobId;
    if (!jobId) {
        alert('No job ID available.');
        return;
    }

    fetch(`/scholar/api/bibtex/job/${jobId}/urls/`)
        .then(response => response.json())
        .then(data => {
            if (!data.urls || data.urls.length === 0) {
                alert('No URLs found in the enriched BibTeX file.');
                return;
            }

            if (!confirm(`Open ${data.total_urls} URLs in new tabs?\n\nNote: Your browser may block some tabs.`)) {
                return;
            }

            // Open URLs with staggered delay
            data.urls.forEach((item, index) => {
                setTimeout(() => {
                    window.open(item.url, '_blank');
                }, index * 100);
            });
        })
        .catch(error => {
            console.error('Error fetching URLs:', error);
            alert('Failed to fetch URLs.');
        });
};

/**
 * Show BibTeX diff
 */
window.showBibtexDiff = function() {
    const jobId = window.currentBibtexJobId;
    if (!jobId) {
        alert('No job ID available.');
        return;
    }

    // Show modal
    const modal = document.getElementById('bibtexDiffModal');
    const content = document.getElementById('bibtexDiffContent');

    if (modal) modal.style.display = 'block';
    if (content) content.innerHTML = 'Loading comparison...';

    // Fetch diff
    fetch(`/scholar/api/bibtex/job/${jobId}/diff/`)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (data.success) {
                displayBibtexDiff(data.diff, data.stats);
            } else {
                if (content) {
                    content.innerHTML = `<div style="color: var(--error-color);">Error: ${data.error || 'Failed to generate diff'}</div>`;
                }
            }
        })
        .catch(error => {
            console.error('Diff error:', error);
            if (content) {
                content.innerHTML = `<div style="color: var(--error-color);">Failed to load comparison: ${error.message}</div>`;
            }
        });
};

/**
 * Close BibTeX diff modal
 */
window.closeBibtexDiff = function() {
    const modal = document.getElementById('bibtexDiffModal');
    if (modal) modal.style.display = 'none';
};

/**
 * Display BibTeX diff
 * @param {Array} diffData - Diff entries
 * @param {Object} stats - Statistics
 */
function displayBibtexDiff(diffData, stats) {
    let html = '';

    // Statistics dashboard
    if (stats) {
        html += `
            <div style="background: var(--color-canvas-subtle); padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; border-left: 4px solid var(--success-color);">
                <h3 style="color: var(--color-fg-default); margin-bottom: 1rem; font-size: 1.2rem;">
                    <i class="fas fa-chart-bar"></i> Enhancement Statistics
                </h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                    <div style="text-align: center;">
                        <div style="color: var(--color-fg-muted); font-size: 0.85rem;">Total Entries</div>
                        <div style="color: var(--scitex-color-03); font-size: 1.8rem; font-weight: 700;">${stats.total_entries}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="color: var(--color-fg-muted); font-size: 0.85rem;">Entries Enhanced</div>
                        <div style="color: var(--success-color); font-size: 1.8rem; font-weight: 700;">${stats.entries_enhanced}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="color: var(--color-fg-muted); font-size: 0.85rem;">Fields Added</div>
                        <div style="color: var(--success-color); font-size: 1.8rem; font-weight: 700;">${stats.total_fields_added}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="color: var(--color-fg-muted); font-size: 0.85rem;">Fields Modified</div>
                        <div style="color: var(--warning-color); font-size: 1.8rem; font-weight: 700;">${stats.total_fields_modified}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="color: var(--color-fg-muted); font-size: 0.85rem;">Enhancement Rate</div>
                        <div style="color: var(--scitex-color-02); font-size: 1.8rem; font-weight: 700;">${stats.enhancement_rate}%</div>
                    </div>
                </div>
            </div>
        `;
    }

    // No changes case
    if (!diffData || diffData.length === 0) {
        html += `
            <div style="text-align: center; padding: 3rem; color: var(--color-fg-muted);">
                <i class="fas fa-check-circle" style="font-size: 3rem; margin-bottom: 1rem; display: block;"></i>
                <p style="font-size: 1.1rem;">All entries are already complete!</p>
                <p style="font-size: 0.9rem;">No new fields were added during enrichment.</p>
            </div>
        `;
        document.getElementById('bibtexDiffContent').innerHTML = html;
        return;
    }

    // Display each entry with changes
    diffData.forEach(entry => {
        html += renderDiffEntry(entry);
    });

    document.getElementById('bibtexDiffContent').innerHTML = html;
}

/**
 * Render a single diff entry
 * @param {Object} entry - Diff entry
 * @returns {string} HTML
 */
function renderDiffEntry(entry) {
    let html = `
        <div style="margin-bottom: 2rem; border: 1px solid var(--color-border-default); border-radius: 6px; padding: 1rem; background: var(--color-canvas-default);">
            <div style="font-weight: 700; font-size: 1.1rem; color: var(--color-fg-default); margin-bottom: 0.75rem;">
                <i class="fas fa-file-alt"></i> @${entry.type}{${entry.key}}
            </div>
    `;

    // Title
    if (entry.title) {
        const shortTitle = entry.title.length > 100 ? entry.title.substring(0, 100) + '...' : entry.title;
        html += `
            <div style="color: var(--color-fg-muted); font-size: 0.9rem; margin-bottom: 0.75rem; font-style: italic;">
                "${escapeHtml(shortTitle)}"
            </div>
        `;
    }

    // Added fields
    if (entry.added_fields && Object.keys(entry.added_fields).length > 0) {
        html += `
            <div style="margin-top: 0.75rem; margin-bottom: 0.5rem; color: var(--success-color); font-weight: 600;">
                <i class="fas fa-plus-circle"></i> Added fields (${Object.keys(entry.added_fields).length}):
            </div>
        `;
        for (const [key, value] of Object.entries(entry.added_fields)) {
            const displayValue = value.length > 100 ? value.substring(0, 100) + '...' : value;
            html += `
                <div style="padding-left: 1.5rem; color: var(--success-color); margin-bottom: 0.25rem;">
                    <span style="font-weight: 600; background: var(--color-canvas-subtle); padding: 0.15rem 0.4rem; border-radius: 3px;">${escapeHtml(key)}</span> =
                    <span style="font-family: monospace;">{${escapeHtml(displayValue)}}</span>
                </div>
            `;
        }
    }

    // Modified fields
    if (entry.modified_fields && Object.keys(entry.modified_fields).length > 0) {
        html += `
            <div style="margin-top: 0.75rem; margin-bottom: 0.5rem; color: var(--warning-color); font-weight: 600;">
                <i class="fas fa-edit"></i> Modified fields (${Object.keys(entry.modified_fields).length}):
            </div>
        `;
        for (const [key, change] of Object.entries(entry.modified_fields)) {
            const oldValue = change.old.length > 50 ? change.old.substring(0, 50) + '...' : change.old;
            const newValue = change.new.length > 50 ? change.new.substring(0, 50) + '...' : change.new;
            html += `
                <div style="padding-left: 1.5rem; margin-bottom: 0.5rem;">
                    <div style="font-weight: 600; background: var(--color-canvas-subtle); padding: 0.15rem 0.4rem; border-radius: 3px; display: inline-block; margin-bottom: 0.25rem;">
                        ${escapeHtml(key)}
                    </div>
                    <div style="padding-left: 0.5rem; color: var(--error-color); text-decoration: line-through; font-family: monospace; font-size: 0.85rem;">
                        - {${escapeHtml(oldValue)}}
                    </div>
                    <div style="padding-left: 0.5rem; color: var(--success-color); font-family: monospace; font-size: 0.85rem;">
                        + {${escapeHtml(newValue)}}
                    </div>
                </div>
            `;
        }
    }

    html += `</div>`;
    return html;
}

/**
 * Show loading state
 */
function showLoadingState() {
    const progressArea = document.getElementById('progressArea');
    if (progressArea) {
        progressArea.style.display = 'block';
    }
}

/**
 * Reset form
 */
function resetForm() {
    const progressArea = document.getElementById('progressArea');
    if (progressArea) {
        progressArea.style.display = 'none';
    }
}

/**
 * Show error
 * @param {string} message - Error message
 */
function showError(message) {
    alert(message);
}

/**
 * Escape HTML
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopJobPolling();
});

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => initBibtexEnrichment());
} else {
    initBibtexEnrichment();
}
