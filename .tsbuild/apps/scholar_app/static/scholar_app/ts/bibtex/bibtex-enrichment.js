"use strict";
/**

 * BibTeX Enrichment Functionality
 *
 * Handles file upload, job submission, status polling, download, URL opening, diff/comparison
 * for the BibTeX enrichment system. This file manages the complete workflow from uploading
 * a BibTeX file to downloading the enriched version with added metadata.
 *
 * @version 1.0.0
 */
// Global state
console.log("[DEBUG] apps/scholar_app/static/scholar_app/ts/bibtex/bibtex-enrichment.ts loaded");
let jobStatusInterval = null;
window.currentBibtexJobId = null;
/**
 * Initialize BibTeX enrichment system
 */
function initBibtexEnrichment(config = {}) {
    const { formId = 'bibtexEnrichmentForm', fileInputId = 'bibtexFileInput', dropZoneId = 'dropZone', statusPollInterval = 2000 } = config;
    const form = document.getElementById(formId);
    const fileInput = document.getElementById(fileInputId);
    const dropZone = document.getElementById(dropZoneId);
    if (!form || !fileInput || !dropZone) {
        console.warn('[BibTeX Enrichment] Form elements not found');
        return;
    }
    // Drag counter for proper drag/drop handling
    let dragCounter = 0;
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    // Dragenter: increment counter and apply styles
    dropZone.addEventListener('dragenter', (e) => {
        dragCounter++;
        if (e.dataTransfer)
            e.dataTransfer.dropEffect = 'copy';
        dropZone.style.borderColor = '#6B8FB3';
        dropZone.style.borderStyle = 'solid';
        dropZone.style.background = 'rgba(107, 143, 179, 0.15)';
        dropZone.style.transform = 'scale(1.01)';
        dropZone.style.boxShadow = '0 4px 16px rgba(107, 143, 179, 0.3)';
    });
    // Dragover: maintain styles
    dropZone.addEventListener('dragover', (e) => {
        if (e.dataTransfer)
            e.dataTransfer.dropEffect = 'copy';
    });
    // Dragleave: decrement counter, remove styles only when truly leaving
    dropZone.addEventListener('dragleave', () => {
        dragCounter--;
        if (dragCounter === 0) {
            resetDropZoneStyle();
        }
    });
    // Drop: reset counter and remove styles
    dropZone.addEventListener('drop', (e) => {
        dragCounter = 0;
        resetDropZoneStyle();
        const dt = e.dataTransfer;
        const files = dt?.files;
        if (files && files.length > 0) {
            const file = files[0];
            if (file.name.endsWith('.bib')) {
                // Assign the dropped file to the input
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                fileInput.files = dataTransfer.files;
                // Update visual feedback
                showFileName(file.name);
            }
            else {
                alert('Please drop a .bib file');
            }
        }
    });
    // Handle file input change (click to upload)
    fileInput.addEventListener('change', function () {
        if (this.files && this.files.length > 0) {
            showFileName(this.files[0].name);
        }
    });
    // Function to display file name and auto-submit
    function showFileName(fileName) {
        const uploadMessage = document.getElementById('uploadMessage');
        const fileNameDisplay = document.getElementById('fileNameDisplay');
        const fileNameEl = document.getElementById('fileName');
        if (uploadMessage)
            uploadMessage.style.display = 'none';
        if (fileNameDisplay)
            fileNameDisplay.style.display = 'block';
        if (fileNameEl)
            fileNameEl.textContent = fileName;
        // Add success visual feedback to drop zone
        dropZone.style.borderColor = 'var(--info-color)';
        dropZone.style.background = 'rgba(107, 143, 179, 0.1)';
        // Auto-submit after short delay
        setTimeout(() => {
            autoSubmitBibtexForm();
        }, 300);
    }
    // Auto-submit function
    function autoSubmitBibtexForm() {
        const formData = new FormData(form);
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (!csrfToken) {
            alert('CSRF token not found. Please refresh the page.');
            return;
        }
        // Show processing state
        dropZone.style.borderColor = 'var(--info-color)';
        dropZone.style.background = 'rgba(107, 143, 179, 0.15)';
        // Show progress area
        const progressArea = document.getElementById('bibtexProgressArea');
        if (progressArea)
            progressArea.style.display = 'block';
        // Submit form via AJAX
        const uploadUrl = window.SCHOLAR_CONFIG?.urls?.bibtexUpload || '/scholar/api/bibtex/upload/';
        fetch(uploadUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        })
            .then(response => {
            if (response.status === 409) {
                // Conflict - user already has a job in progress
                return response.json().then((data) => {
                    if (data.requires_confirmation && data.existing_job) {
                        // Ask user if they want to cancel the existing job
                        const msg = `You already have a job in progress: "${data.existing_job.filename}" (${data.existing_job.progress}% complete).\n\nCancel it and start a new job?`;
                        if (confirm(msg)) {
                            // Resubmit with force flag
                            formData.append('force', 'true');
                            return fetch(uploadUrl, {
                                method: 'POST',
                                body: formData,
                                headers: {
                                    'X-Requested-With': 'XMLHttpRequest',
                                    'X-CSRFToken': csrfToken
                                }
                            }).then(r => r.json());
                        }
                        else {
                            // User declined, start monitoring existing job
                            if (data.existing_job.id) {
                                pollBibtexJobStatus(data.existing_job.id);
                            }
                            throw new Error('User declined to cancel existing job');
                        }
                    }
                    else {
                        alert(data.message || 'You already have a job in progress. Please wait for it to complete.');
                        resetBibtexForm();
                        throw new Error('Job already running');
                    }
                });
            }
            return response.json();
        })
            .then((data) => {
            if (data.success && data.job_id) {
                // Start polling for job status
                pollBibtexJobStatus(data.job_id);
            }
            else {
                alert('Error: ' + (data.error || 'Failed to start enrichment'));
                resetBibtexForm();
            }
        })
            .catch((error) => {
            const ignoredErrors = ['Job already running', 'User declined to cancel existing job'];
            if (!ignoredErrors.includes(error.message)) {
                console.error('Error:', error);
                alert('Failed to upload BibTeX file: ' + error.message);
                resetBibtexForm();
            }
        });
    }
    // Prevent manual form submission (auto-processing only)
    form.addEventListener('submit', function (e) {
        e.preventDefault();
    });
    function resetDropZoneStyle() {
        dropZone.style.borderColor = 'var(--scitex-color-03)';
        dropZone.style.borderStyle = 'dashed';
        dropZone.style.background = 'var(--color-canvas-subtle)';
        dropZone.style.transform = 'scale(1)';
        dropZone.style.boxShadow = 'none';
    }
    console.log('[BibTeX Enrichment] Initialization complete');
}
/**
 * Reset BibTeX form to initial state
 */
function resetBibtexForm() {
    const formArea = document.getElementById('bibtexFormArea');
    const progressArea = document.getElementById('bibtexProgressArea');
    const form = document.getElementById('bibtexEnrichmentForm');
    if (formArea)
        formArea.style.display = 'block';
    if (progressArea)
        progressArea.style.display = 'none';
    if (form)
        form.reset();
}
/**
 * Poll BibTeX job status
 */
function pollBibtexJobStatus(jobId, attempts = 0) {
    // Store job ID globally for "Open All URLs" button
    window.currentBibtexJobId = jobId;
    if (attempts > 180) {
        console.error('[BibTeX] Polling timeout after 180 attempts');
        const log = document.getElementById('processingLog');
        if (log)
            log.textContent += '\n\n✗ Polling timeout. Please refresh the page.';
        return;
    }
    fetch(`/scholar/api/bibtex/job/${jobId}/status/`)
        .then(response => {
        if (!response.ok)
            throw new Error(`HTTP ${response.status}`);
        return response.json();
    })
        .then((data) => {
        // Update progress
        if (data.progress_percentage !== undefined) {
            const progressBar = document.getElementById('progressBar');
            const progressPercentage = document.getElementById('progressPercentage');
            if (progressBar)
                progressBar.style.width = `${data.progress_percentage}%`;
            if (progressPercentage)
                progressPercentage.textContent = `${data.progress_percentage}%`;
        }
        // Update paper counts
        if (data.total_papers !== undefined) {
            let text = `${data.processed_papers} / ${data.total_papers} papers processed`;
            if (data.failed_papers && data.failed_papers > 0)
                text += ` (${data.failed_papers} failed)`;
            const progressDetails = document.getElementById('progressDetails');
            if (progressDetails)
                progressDetails.textContent = text;
        }
        // Update log
        if (data.log) {
            const processingLog = document.getElementById('processingLog');
            if (processingLog) {
                processingLog.textContent = data.log;
                processingLog.scrollTop = processingLog.scrollHeight;
            }
        }
        // Check if done
        if (data.status === 'completed') {
            console.log('[BibTeX] Job completed! Setting up download...');
            const downloadUrl = `/scholar/api/bibtex/job/${jobId}/download/`;
            // Enable download button
            const downloadBtn = document.getElementById('downloadBtn');
            if (downloadBtn) {
                downloadBtn.href = downloadUrl;
                downloadBtn.classList.remove('disabled');
                downloadBtn.style.opacity = '1';
            }
            // Enable other buttons
            const showDiffBtn = document.getElementById('showDiffBtn');
            const openUrlsBtn = document.getElementById('openUrlsBtn');
            if (showDiffBtn) {
                showDiffBtn.disabled = false;
                showDiffBtn.style.opacity = '1';
            }
            if (openUrlsBtn) {
                openUrlsBtn.disabled = false;
                openUrlsBtn.style.opacity = '1';
                openUrlsBtn.style.cursor = 'pointer';
            }
            // Fetch URL count for "Open All URLs" button
            fetch(`/scholar/api/bibtex/job/${jobId}/urls/`)
                .then(response => response.json())
                .then((urlData) => {
                const count = urlData.total_urls || 0;
                const urlCount = document.getElementById('urlCount');
                if (urlCount)
                    urlCount.textContent = count.toString();
            })
                .catch((error) => {
                console.error('[BibTeX] Failed to fetch URL count:', error);
                const urlCount = document.getElementById('urlCount');
                if (urlCount)
                    urlCount.textContent = '?';
            });
            // Auto-download the enriched file
            autoDownloadBibtexFile(downloadUrl);
        }
        else if (data.status === 'failed') {
            console.log('[BibTeX] Job failed:', data.error_message);
            const log = document.getElementById('processingLog');
            if (log)
                log.textContent += '\n\n✗ ERROR: ' + (data.error_message || 'Unknown error');
            setTimeout(() => resetBibtexForm(), 5000);
        }
        else {
            setTimeout(() => pollBibtexJobStatus(jobId, attempts + 1), 2000);
        }
    })
        .catch((error) => {
        console.error('Polling error:', error);
        setTimeout(() => pollBibtexJobStatus(jobId, attempts + 1), 5000);
    });
}
/**
 * Auto-download BibTeX file when enrichment completes
 */
function autoDownloadBibtexFile(url) {
    console.log('[Auto-Download] Starting download for:', url);
    fetch(url)
        .then(response => {
        console.log('[Auto-Download] Response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        // Extract filename from headers
        let filename = 'enriched_bibliography.bib';
        const contentDisposition = response.headers.get('Content-Disposition');
        if (contentDisposition) {
            const match = contentDisposition.match(/filename="?(.+?)"?$/);
            if (match)
                filename = match[1];
        }
        console.log('[Auto-Download] Filename:', filename);
        return response.blob().then(blob => ({ blob, filename }));
    })
        .then(({ blob, filename }) => {
        console.log('[Auto-Download] Creating download link...');
        const blobUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = filename;
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        setTimeout(() => {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(blobUrl);
            console.log('[Auto-Download] ✓ Download completed');
        }, 100);
    })
        .catch((error) => {
        console.error('[Auto-Download] ✗ Failed:', error);
        console.log('[Auto-Download] Trying fallback method...');
        // Fallback: direct link
        const a = document.createElement('a');
        a.href = url;
        a.download = 'enriched_bibliography.bib';
        document.body.appendChild(a);
        a.click();
        setTimeout(() => document.body.removeChild(a), 100);
    });
}
/**
 * Open all paper URLs from enriched BibTeX file
 */
window.openAllPaperUrls = function () {
    const jobId = window.currentBibtexJobId;
    if (!jobId) {
        alert('No job ID available. Please wait for enrichment to complete.');
        return;
    }
    console.log('[Open URLs] Fetching URLs for job:', jobId);
    const urlsEndpoint = `/scholar/api/bibtex/job/${jobId}/urls/`;
    fetch(urlsEndpoint)
        .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
    })
        .then((data) => {
        console.log('[Open URLs] Received data:', data);
        if (data.urls && data.urls.length > 0) {
            const confirmMsg = `Open ${data.total_urls} paper URL(s) in new tabs?\n\n` +
                `Note: Your browser may block some pop-ups. Please allow pop-ups for this site if needed.`;
            if (confirm(confirmMsg)) {
                console.log(`[Open URLs] Opening ${data.urls.length} URLs...`);
                // Open all URLs immediately (no setTimeout to avoid popup blocker)
                let openedCount = 0;
                data.urls.forEach((paper) => {
                    console.log(`[Open URLs] Opening: ${paper.title.substring(0, 50)}... (${paper.type})`);
                    const newWindow = window.open(paper.url, '_blank');
                    if (newWindow) {
                        openedCount++;
                    }
                });
                // Only show message if some tabs were blocked
                if (openedCount < data.urls.length) {
                    alert(`⚠️ Opened ${openedCount} out of ${data.urls.length} URLs.\n\nSome tabs were blocked by your browser's popup blocker.\nPlease allow popups for this site and try again.`);
                }
            }
        }
        else {
            alert('No URLs found in the enriched BibTeX file.\n\nThis could mean:\n- Papers don\'t have DOI or URL fields\n- Enrichment didn\'t add URLs\n- Try downloading the file to check');
        }
    })
        .catch((error) => {
        console.error('[Open URLs] Error:', error);
        alert(`Failed to fetch URLs: ${error.message}\n\nPlease try downloading the BibTeX file manually.`);
    });
};
/**
 * Show BibTeX diff
 */
window.showBibtexDiff = function () {
    const jobId = window.currentBibtexJobId;
    if (!jobId) {
        alert('No job ID available. Please wait for enrichment to complete.');
        return;
    }
    // Show modal
    const modal = document.getElementById('bibtexDiffModal');
    const content = document.getElementById('bibtexDiffContent');
    if (modal)
        modal.style.display = 'block';
    if (content)
        content.innerHTML = 'Loading comparison...';
    // Fetch diff data
    fetch(`/scholar/api/bibtex/job/${jobId}/diff/`)
        .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
    })
        .then((data) => {
        if (data.success) {
            displayBibtexDiff(data.diff, data.stats);
        }
        else {
            if (content) {
                content.innerHTML = `<div style="color: var(--error-color);">Error: ${data.error || 'Failed to generate diff'}</div>`;
            }
        }
    })
        .catch((error) => {
        console.error('Error fetching diff:', error);
        if (content) {
            content.innerHTML = `<div style="color: var(--error-color);">Failed to load comparison: ${error.message}</div>`;
        }
    });
};
/**
 * Display the diff in a readable format (GitHub-style)
 */
function displayBibtexDiff(diffData, stats) {
    let html = '';
    // Show statistics at the top
    if (stats) {
        html += `<div style="background: #f6f8fa; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; border-left: 4px solid #28a745;">`;
        html += `<h3 style="color: #24292e; margin-bottom: 1rem; font-size: 1.2rem;">
            <i class="fas fa-chart-bar"></i> Enhancement Statistics
        </h3>`;
        html += `<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">`;
        html += `<div style="text-align: center;">
            <div style="color: #586069; font-size: 0.85rem;">Total Entries</div>
            <div style="color: #0366d6; font-size: 1.8rem; font-weight: 700;">${stats.total_entries}</div>
        </div>`;
        html += `<div style="text-align: center;">
            <div style="color: #586069; font-size: 0.85rem;">Entries Enhanced</div>
            <div style="color: #28a745; font-size: 1.8rem; font-weight: 700;">${stats.entries_enhanced}</div>
        </div>`;
        html += `<div style="text-align: center;">
            <div style="color: #586069; font-size: 0.85rem;">Fields Added</div>
            <div style="color: #28a745; font-size: 1.8rem; font-weight: 700;">${stats.total_fields_added}</div>
        </div>`;
        html += `<div style="text-align: center;">
            <div style="color: #586069; font-size: 0.85rem;">Enhancement Rate</div>
            <div style="color: #0366d6; font-size: 1.8rem; font-weight: 700;">${stats.enhancement_rate}%</div>
        </div>`;
        html += `</div></div>`;
    }
    if (!diffData || diffData.length === 0) {
        html += '<div style="text-align: center; padding: 3rem; color: #586069; background: #ffffff;">';
        html += '<i class="fas fa-check-circle" style="font-size: 3rem; margin-bottom: 1rem; display: block; color: #28a745;"></i>';
        html += '<p style="font-size: 1.1rem;">All entries are already complete!</p>';
        html += '<p style="font-size: 0.9rem;">No new fields were added during enrichment.</p>';
        html += '</div>';
        const content = document.getElementById('bibtexDiffContent');
        if (content)
            content.innerHTML = html;
        return;
    }
    // Display entries in GitHub-style diff format (abbreviated for token efficiency)
    diffData.forEach((entry) => {
        html += `<div style="margin-bottom: 1.5rem; border: 1px solid #d1d5da; border-radius: 6px; overflow: hidden;">`;
        html += `<div style="background: #f6f8fa; padding: 0.5rem 1rem; font-family: monospace;">@${entry.type}{${entry.key}}</div>`;
        html += `</div>`;
    });
    const content = document.getElementById('bibtexDiffContent');
    if (content)
        content.innerHTML = html;
}
/**
 * Close BibTeX diff modal
 */
window.closeBibtexDiff = function () {
    const modal = document.getElementById('bibtexDiffModal');
    if (modal)
        modal.style.display = 'none';
};
// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function () {
    initBibtexEnrichment();
});
//# sourceMappingURL=bibtex-enrichment.js.map