/**

 * BibTeX Enrichment Functionality
 *
 * Handles file upload, job submission, status polling, download, URL opening, diff/comparison
 * for the BibTeX enrichment system. This file manages the complete workflow from uploading
 * a BibTeX file to downloading the enriched version with added metadata.
 *
 * @version 1.0.0
 */

import { showConfirm } from '../../../shared/ts/components/confirm-modal.js';

// Global state

console.log("[DEBUG] apps/scholar_app/static/scholar_app/ts/bibtex/bibtex-enrichment.ts loaded");
let jobStatusInterval: number | null = null;

// Window interface extensions
declare global {
    interface Window {
        currentBibtexJobId: string | null;
        SCHOLAR_CONFIG?: {
            urls?: {
                bibtexUpload?: string;
                resourceStatus?: string;
            };
        };
    }
}

window.currentBibtexJobId = null;

/**
 * Job status response interface
 */
interface JobStatusResponse {
    status: string;
    progress_percentage?: number;
    processed_papers?: number;
    total_papers?: number;
    failed_papers?: number;
    log?: string;
    error_message?: string;
}

/**
 * BibTeX enrichment configuration
 */
interface BibtexEnrichmentConfig {
    formId?: string;
    fileInputId?: string;
    dropZoneId?: string;
    statusPollInterval?: number;
}

/**
 * Initialize BibTeX enrichment system
 */
function initBibtexEnrichment(config: BibtexEnrichmentConfig = {}): void {
    const {
        formId = 'bibtexEnrichmentForm',
        fileInputId = 'bibtexFileInput',
        dropZoneId = 'dropZone',
        statusPollInterval = 2000
    } = config;

    const form = document.getElementById(formId) as HTMLFormElement | null;
    const fileInput = document.getElementById(fileInputId) as HTMLInputElement | null;
    const dropZone = document.getElementById(dropZoneId) as HTMLElement | null;

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

    function preventDefaults(e: Event): void {
        e.preventDefault();
        e.stopPropagation();
    }

    // Dragenter: increment counter and apply styles
    dropZone.addEventListener('dragenter', (e: DragEvent) => {
        dragCounter++;
        if (e.dataTransfer) e.dataTransfer.dropEffect = 'copy';
        dropZone.style.borderColor = '#6B8FB3';
        dropZone.style.borderStyle = 'solid';
        dropZone.style.background = 'rgba(107, 143, 179, 0.15)';
        dropZone.style.transform = 'scale(1.01)';
        dropZone.style.boxShadow = '0 4px 16px rgba(107, 143, 179, 0.3)';
    });

    // Dragover: maintain styles
    dropZone.addEventListener('dragover', (e: DragEvent) => {
        if (e.dataTransfer) e.dataTransfer.dropEffect = 'copy';
    });

    // Dragleave: decrement counter, remove styles only when truly leaving
    dropZone.addEventListener('dragleave', () => {
        dragCounter--;
        if (dragCounter === 0) {
            resetDropZoneStyle();
        }
    });

    // Drop: reset counter and remove styles
    dropZone.addEventListener('drop', (e: DragEvent) => {
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
            } else {
                alert('Please drop a .bib file');
            }
        }
    });

    // Handle file input change (click to upload)
    fileInput.addEventListener('change', function() {
        if (this.files && this.files.length > 0) {
            showFileName(this.files[0].name);
        }
    });

    // Function to display file name and auto-submit
    function showFileName(fileName: string): void {
        const uploadMessage = document.getElementById('uploadMessage') as HTMLElement | null;
        const fileNameDisplay = document.getElementById('fileNameDisplay') as HTMLElement | null;
        const fileNameEl = document.getElementById('fileName') as HTMLElement | null;

        if (uploadMessage) uploadMessage.style.display = 'none';
        if (fileNameDisplay) fileNameDisplay.style.display = 'block';
        if (fileNameEl) fileNameEl.textContent = fileName;

        // Add success visual feedback to drop zone
        dropZone.style.borderColor = 'var(--info-color)';
        dropZone.style.background = 'rgba(107, 143, 179, 0.1)';

        // Auto-submit after short delay
        setTimeout(() => {
            autoSubmitBibtexForm();
        }, 300);
    }

    // Auto-submit function
    function autoSubmitBibtexForm(): void {
        const formData = new FormData(form);

        // Get CSRF token
        const csrfToken = (document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement)?.value;

        if (!csrfToken) {
            alert('CSRF token not found. Please refresh the page.');
            return;
        }

        // Show processing state
        dropZone.style.borderColor = 'var(--info-color)';
        dropZone.style.background = 'rgba(107, 143, 179, 0.15)';

        // Show progress area
        const progressArea = document.getElementById('bibtexProgressArea') as HTMLElement | null;
        if (progressArea) progressArea.style.display = 'block';

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
                return response.json().then((data: any) => {
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
                        } else {
                            // User declined, start monitoring existing job
                            if (data.existing_job.id) {
                                pollBibtexJobStatus(data.existing_job.id);
                            }
                            throw new Error('User declined to cancel existing job');
                        }
                    } else {
                        alert(data.message || 'You already have a job in progress. Please wait for it to complete.');
                        resetBibtexForm();
                        throw new Error('Job already running');
                    }
                });
            }
            return response.json();
        })
        .then((data: any) => {
            if (data.success && data.job_id) {
                // Start polling for job status
                pollBibtexJobStatus(data.job_id);
            } else {
                alert('Error: ' + (data.error || 'Failed to start enrichment'));
                resetBibtexForm();
            }
        })
        .catch((error: Error) => {
            const ignoredErrors = ['Job already running', 'User declined to cancel existing job'];
            if (!ignoredErrors.includes(error.message)) {
                console.error('Error:', error);
                alert('Failed to upload BibTeX file: ' + error.message);
                resetBibtexForm();
            }
        });
    }

    // Prevent manual form submission (auto-processing only)
    form.addEventListener('submit', function(e: Event) {
        e.preventDefault();
    });

    function resetDropZoneStyle(): void {
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
function resetBibtexForm(): void {
    const formArea = document.getElementById('bibtexFormArea') as HTMLElement | null;
    const progressArea = document.getElementById('bibtexProgressArea') as HTMLElement | null;
    const form = document.getElementById('bibtexEnrichmentForm') as HTMLFormElement | null;

    if (formArea) formArea.style.display = 'block';
    if (progressArea) progressArea.style.display = 'none';
    if (form) form.reset();
}

/**
 * Poll BibTeX job status
 */
function pollBibtexJobStatus(jobId: string, attempts: number = 0): void {
    // Store job ID globally for "Open All URLs" button
    window.currentBibtexJobId = jobId;

    // Show enrichment running indicator on first call
    if (attempts === 0) {
        const runningIndicator = document.getElementById('enrichmentRunningIndicator') as HTMLElement | null;
        if (runningIndicator) runningIndicator.style.display = 'block';
    }

    if (attempts > 180) {
        console.error('[BibTeX] Polling timeout after 180 attempts');
        const log = document.getElementById('processingLog') as HTMLElement | null;
        const enrichmentLog = document.getElementById('enrichmentProcessingLog') as HTMLElement | null;
        if (log) log.textContent += '\n\n✗ Polling timeout. Please refresh the page.';
        if (enrichmentLog) enrichmentLog.textContent += '\n\n✗ Polling timeout. Please refresh the page.';
        return;
    }

    fetch(`/scholar/api/bibtex/job/${jobId}/status/`)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        })
        .then((data: JobStatusResponse) => {
            // Update progress in running indicator
            if (data.progress_percentage !== undefined) {
                const progressBar = document.getElementById('enrichmentProgressBar') as HTMLElement | null;
                const progressPercent = document.getElementById('progressPercent') as HTMLElement | null;
                if (progressBar) progressBar.style.width = `${data.progress_percentage}%`;
                if (progressPercent) progressPercent.textContent = `${data.progress_percentage}%`;
            }

            // Update status text in running indicator
            if (data.total_papers !== undefined) {
                let statusText = `Processing ${data.processed_papers}/${data.total_papers} papers`;
                if (data.failed_papers && data.failed_papers > 0) statusText += ` (${data.failed_papers} failed)`;
                const progressStatus = document.getElementById('progressStatus') as HTMLElement | null;
                if (progressStatus) progressStatus.textContent = statusText;
            }

            // Update logs (both running indicator and sidebar)
            if (data.log) {
                const processingLog = document.getElementById('processingLog') as HTMLElement | null;
                const enrichmentLog = document.getElementById('enrichmentProcessingLog') as HTMLElement | null;

                if (processingLog) {
                    processingLog.textContent = data.log;
                    processingLog.scrollTop = processingLog.scrollHeight;
                }

                if (enrichmentLog) {
                    enrichmentLog.textContent = data.log;
                    enrichmentLog.scrollTop = enrichmentLog.scrollHeight;
                }
            }

            // Check if done
            if (data.status === 'completed') {
                console.log('[BibTeX] Job completed! Setting up download...');
                const downloadUrl = `/scholar/api/bibtex/job/${jobId}/download/`;

                // Hide running indicator
                const runningIndicator = document.getElementById('enrichmentRunningIndicator') as HTMLElement | null;
                if (runningIndicator) runningIndicator.style.display = 'none';

                // Enable download button
                const downloadBtn = document.getElementById('downloadBtn') as HTMLButtonElement | null;
                if (downloadBtn) {
                    downloadBtn.disabled = false;
                    downloadBtn.classList.remove('disabled');
                    downloadBtn.style.opacity = '1';
                    downloadBtn.onclick = () => autoDownloadBibtexFile(downloadUrl);
                }

                // Enable save to project button
                const saveBtn = document.getElementById('saveToProjectBtn') as HTMLButtonElement | null;
                if (saveBtn) {
                    saveBtn.disabled = false;
                    saveBtn.style.opacity = '1';
                }

                // Enable view changes button (main area)
                const viewChangesBtn = document.getElementById('viewChangesBtn') as HTMLButtonElement | null;
                if (viewChangesBtn) {
                    viewChangesBtn.disabled = false;
                    viewChangesBtn.style.opacity = '1';
                }

                // Enable other buttons
                const showDiffBtn = document.getElementById('showDiffBtn') as HTMLButtonElement | null;
                const openUrlsBtn = document.getElementById('openUrlsBtn') as HTMLButtonElement | null;
                const openUrlsMainBtn = document.getElementById('openUrlsMainBtn') as HTMLButtonElement | null;

                if (showDiffBtn) {
                    showDiffBtn.disabled = false;
                    showDiffBtn.style.opacity = '1';
                }

                if (openUrlsBtn) {
                    openUrlsBtn.disabled = false;
                    openUrlsBtn.style.opacity = '1';
                    openUrlsBtn.style.cursor = 'pointer';
                }

                if (openUrlsMainBtn) {
                    openUrlsMainBtn.disabled = false;
                    openUrlsMainBtn.style.opacity = '1';
                    openUrlsMainBtn.style.cursor = 'pointer';
                }

                // Fetch URL count for "Open All URLs" buttons
                fetch(`/scholar/api/bibtex/job/${jobId}/urls/`)
                    .then(response => response.json())
                    .then((urlData: any) => {
                        const count = urlData.total_urls || 0;

                        // Update sidebar button count
                        const urlCount = document.getElementById('urlCount') as HTMLElement | null;
                        if (urlCount) urlCount.textContent = count.toString();

                        // Update main button text
                        const urlButtonText = document.getElementById('urlButtonText') as HTMLElement | null;
                        if (urlButtonText && count > 0) {
                            urlButtonText.textContent = `Open All ${count} URLs`;
                        }
                    })
                    .catch((error: Error) => {
                        console.error('[BibTeX] Failed to fetch URL count:', error);
                        const urlCount = document.getElementById('urlCount') as HTMLElement | null;
                        if (urlCount) urlCount.textContent = '?';
                    });

                // Auto-download the enriched file
                autoDownloadBibtexFile(downloadUrl).catch((error: Error) => {
                    console.error('[Auto-Download on Complete] Failed:', error);
                    // Error alert already shown in autoDownloadBibtexFile
                });
            } else if (data.status === 'failed') {
                console.log('[BibTeX] Job failed:', data.error_message);
                const log = document.getElementById('processingLog') as HTMLElement | null;
                const enrichmentLog = document.getElementById('enrichmentProcessingLog') as HTMLElement | null;
                const errorMsg = '\n\n✗ ERROR: ' + (data.error_message || 'Unknown error');
                if (log) log.textContent += errorMsg;
                if (enrichmentLog) enrichmentLog.textContent += errorMsg;

                // Hide running indicator after delay
                setTimeout(() => {
                    const runningIndicator = document.getElementById('enrichmentRunningIndicator') as HTMLElement | null;
                    if (runningIndicator) runningIndicator.style.display = 'none';
                    resetBibtexForm();
                }, 5000);
            } else {
                setTimeout(() => pollBibtexJobStatus(jobId, attempts + 1), 2000);
            }
        })
        .catch((error: Error) => {
            console.error('Polling error:', error);
            setTimeout(() => pollBibtexJobStatus(jobId, attempts + 1), 5000);
        });
}

/**
 * Handle download button click
 */
(window as any).handleDownload = async function(): Promise<void> {
    const downloadBtn = document.getElementById('downloadBtn') as HTMLButtonElement;
    if (!downloadBtn) return;

    // Get download URL from button's onclick that was set during enrichment
    const jobId = window.currentBibtexJobId;
    if (!jobId) {
        showAlert('⚠ No enriched file available yet. Please wait for enrichment to complete.', 'warning');
        return;
    }

    const downloadUrl = `/scholar/api/bibtex/job/${jobId}/download/`;

    // Add loading state
    const originalHTML = downloadBtn.innerHTML;
    downloadBtn.disabled = true;
    downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Downloading...';
    downloadBtn.style.opacity = '0.7';

    try {
        await autoDownloadBibtexFile(downloadUrl);
        // Success alert is shown in autoDownloadBibtexFile
    } catch (error) {
        console.error('[Handle Download] Error:', error);
        showAlert('❌ Failed to download enriched BibTeX file. Please try again.', 'error');
    } finally {
        // Restore button state
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = originalHTML;
        downloadBtn.style.opacity = '1';
    }
};

/**
 * Auto-download BibTeX file when enrichment completes
 */
async function autoDownloadBibtexFile(url: string): Promise<void> {
    console.log('[Auto-Download] Starting download for:', url);

    try {
        const response = await fetch(url);
        console.log('[Auto-Download] Response status:', response.status);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        // Extract filename from headers
        let filename = 'enriched_bibliography.bib';
        const contentDisposition = response.headers.get('Content-Disposition');
        if (contentDisposition) {
            const match = contentDisposition.match(/filename="?(.+?)"?$/);
            if (match) filename = match[1];
        }
        console.log('[Auto-Download] Filename:', filename);

        const blob = await response.blob();
        const fileSizeMB = (blob.size / (1024 * 1024)).toFixed(2);

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

        // Show success alert with filename and size
        showAlert(
            `✅ <strong>Download started!</strong><br><br>` +
            `📄 File: <code>${filename}</code><br>` +
            `📦 Size: ${fileSizeMB} MB<br><br>` +
            `Check your browser's download folder.`,
            'success'
        );

    } catch (error: any) {
        console.error('[Auto-Download] ✗ Failed:', error);

        // Show error alert with details
        showAlert(
            `❌ <strong>Download failed</strong><br><br>` +
            `${error.message || 'Unknown error occurred'}<br><br>` +
            `Please try again or contact support if the problem persists.`,
            'error'
        );

        throw error; // Re-throw so handleDownload can catch it
    }
}

/**
 * Open all paper URLs from enriched BibTeX file in a new window
 */
(window as any).openAllPaperUrls = function(): void {
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
        .then((data: any) => {
            console.log('[Open URLs] Received data:', data);

            if (data.urls && data.urls.length > 0) {
                showConfirm({
                    title: `Open ${data.total_urls} paper URL(s) in new tabs?`,
                    message: `This feature is useful when you want to download PDF files.\n\nWhat will happen:\n• Papers will open in background tabs\n• You can download PDF files efficiently\n\nPlease note:\n• Opening many tabs may clutter your browser\n• Your browser may block pop-ups - please allow them if needed`,
                    confirmText: 'Open All URLs',
                    cancelText: 'Cancel',
                    onConfirm: () => {
                        console.log(`[Open URLs] Opening ${data.urls.length} URLs as tabs...`);

                        // Open all URLs in background tabs
                        let openedCount = 0;
                        data.urls.forEach((paper: any, index: number) => {
                            console.log(`[Open URLs] Opening: ${paper.title.substring(0, 50)}... (${paper.type})`);
                            // Use a unique target name for each tab so they all stay separate
                            const targetName = `scitex_paper_${jobId}_${index}`;
                            const tab = window.open(paper.url, targetName);
                            if (tab) {
                                // Immediately blur the new tab to keep focus on current page
                                tab.blur();
                                openedCount++;
                            }
                        });

                        // Refocus on current window to stay here
                        window.focus();

                        // Show message about result
                        if (openedCount === data.urls.length) {
                            // All opened successfully
                            console.log(`[Open URLs] Successfully opened all ${openedCount} URLs`);
                        } else if (openedCount > 0) {
                            // Some were blocked
                            alert(`⚠️ Opened ${openedCount} out of ${data.urls.length} URLs.\n\nSome tabs were blocked by your browser's popup blocker.\nPlease allow popups for this site in your browser settings.`);
                        } else {
                            // All were blocked
                            alert(`❌ Could not open URLs.\n\nYour browser blocked the popups.\nPlease allow popups for this site:\n1. Click the blocked popup icon in your address bar\n2. Allow popups from this site\n3. Try again`);
                        }
                    }
                });
            } else {
                alert('No URLs found in the enriched BibTeX file.\n\nThis could mean:\n- Papers don\'t have DOI or URL fields\n- Enrichment didn\'t add URLs\n- Try downloading the file to check');
            }
        })
        .catch((error: Error) => {
            console.error('[Open URLs] Error:', error);
            alert(`Failed to fetch URLs: ${error.message}\n\nPlease try downloading the BibTeX file manually.`);
        });
};

/**
 * Show BibTeX diff
 */
(window as any).showBibtexDiff = function(): void {
    const jobId = window.currentBibtexJobId;
    if (!jobId) {
        alert('No job ID available. Please wait for enrichment to complete.');
        return;
    }

    // Show modal
    const modal = document.getElementById('bibtexDiffModal') as HTMLElement | null;
    const content = document.getElementById('bibtexDiffContent') as HTMLElement | null;
    if (modal) modal.style.display = 'block';
    if (content) content.innerHTML = 'Loading comparison...';

    // Fetch diff data
    fetch(`/scholar/api/bibtex/job/${jobId}/diff/`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then((data: any) => {
            if (data.success) {
                displayBibtexDiff(data.diff, data.stats, data.files);
            } else {
                if (content) {
                    content.innerHTML = `<div style="color: var(--error-color);">Error: ${data.error || 'Failed to generate diff'}</div>`;
                }
            }
        })
        .catch((error: Error) => {
            console.error('Error fetching diff:', error);
            if (content) {
                content.innerHTML = `<div style="color: var(--error-color);">Failed to load comparison: ${error.message}</div>`;
            }
        });
};

/**
 * Display the diff in a readable format (GitHub-style)
 */
function displayBibtexDiff(diffData: any[], stats: any, files?: any): void {
    let html = '';

    // Show file comparison info at the top
    if (files && files.original && files.enhanced) {
        html += `<div style="background: #f6f8fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #0366d6;">`;
        html += `<div style="display: flex; gap: 1rem; align-items: center; font-size: 0.9rem;">`;
        html += `<div style="flex: 1;">`;
        html += `<div style="color: #586069; font-size: 0.75rem; font-weight: 600; margin-bottom: 0.25rem;">ORIGINAL</div>`;
        if (files.original_url) {
            // Check if URL is a download endpoint or filer URL
            const isDownloadUrl = files.original_url.includes('/download/');
            const linkAttrs = isDownloadUrl ? 'download' : 'target="_blank"';
            const icon = isDownloadUrl ? 'fa-download' : 'fa-folder-open';
            const tooltip = isDownloadUrl ? 'Download original file' : 'View in file browser';
            html += `<a href="${files.original_url}" ${linkAttrs} style="color: #0366d6; font-family: monospace; font-size: 0.85rem; text-decoration: none; display: inline-flex; align-items: center; gap: 0.3rem;" title="${tooltip}">`;
            html += `<i class="fas ${icon}" style="font-size: 0.75rem;"></i>${files.original}`;
            html += `</a>`;
        } else {
            html += `<div style="color: #24292e; font-family: monospace; font-size: 0.85rem;">${files.original}</div>`;
        }
        html += `</div>`;
        html += `<div style="color: #586069; font-size: 1.2rem;"><i class="fas fa-arrow-right"></i></div>`;
        html += `<div style="flex: 1;">`;
        html += `<div style="color: #586069; font-size: 0.75rem; font-weight: 600; margin-bottom: 0.25rem;">ENHANCED</div>`;
        if (files.enhanced_url) {
            // Check if URL is a download endpoint or filer URL
            const isDownloadUrl = files.enhanced_url.includes('/download/');
            const linkAttrs = isDownloadUrl ? 'download' : 'target="_blank"';
            const icon = isDownloadUrl ? 'fa-download' : 'fa-folder-open';
            const tooltip = isDownloadUrl ? 'Download enhanced file' : 'View in file browser';
            html += `<a href="${files.enhanced_url}" ${linkAttrs} style="color: #0366d6; font-family: monospace; font-size: 0.85rem; text-decoration: none; display: inline-flex; align-items: center; gap: 0.3rem;" title="${tooltip}">`;
            html += `<i class="fas ${icon}" style="font-size: 0.75rem;"></i>${files.enhanced}`;
            html += `</a>`;
        } else {
            html += `<div style="color: #24292e; font-family: monospace; font-size: 0.85rem;">${files.enhanced}</div>`;
        }
        html += `</div>`;
        html += `</div></div>`;
    }

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

        // Show major metadata fields success rates
        if (stats.major_fields) {
            html += `<div style="background: #fff5e6; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; border-left: 4px solid #e67700;">`;
            html += `<h3 style="color: #24292e; margin-bottom: 1rem; font-size: 1.1rem;">
                <i class="fas fa-clipboard-check"></i> Major Metadata Success Rates
            </h3>`;
            html += `<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">`;

            // Abstract (most important)
            const abstractRate = stats.major_fields.abstract ?
                Math.round((stats.major_fields.abstract.acquired / stats.total_entries) * 100) : 0;
            const abstractColor = abstractRate >= 70 ? '#28a745' : abstractRate >= 40 ? '#e67700' : '#d73a49';
            html += `<div style="text-align: center; padding: 0.75rem; background: white; border-radius: 6px; border: 1px solid #e1e4e8;">
                <div style="color: #586069; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.25rem;">ABSTRACT</div>
                <div style="color: ${abstractColor}; font-size: 1.6rem; font-weight: 700;">${abstractRate}%</div>
                <div style="color: #586069; font-size: 0.75rem;">${stats.major_fields.abstract?.acquired || 0}/${stats.total_entries}</div>
            </div>`;

            // DOI
            const doiRate = stats.major_fields.doi ?
                Math.round((stats.major_fields.doi.acquired / stats.total_entries) * 100) : 0;
            const doiColor = doiRate >= 70 ? '#28a745' : doiRate >= 40 ? '#e67700' : '#d73a49';
            html += `<div style="text-align: center; padding: 0.75rem; background: white; border-radius: 6px; border: 1px solid #e1e4e8;">
                <div style="color: #586069; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.25rem;">DOI</div>
                <div style="color: ${doiColor}; font-size: 1.6rem; font-weight: 700;">${doiRate}%</div>
                <div style="color: #586069; font-size: 0.75rem;">${stats.major_fields.doi?.acquired || 0}/${stats.total_entries}</div>
            </div>`;

            // Citation Count
            const citationsRate = stats.major_fields.citation_count ?
                Math.round((stats.major_fields.citation_count.acquired / stats.total_entries) * 100) : 0;
            const citationsColor = citationsRate >= 70 ? '#28a745' : citationsRate >= 40 ? '#e67700' : '#d73a49';
            html += `<div style="text-align: center; padding: 0.75rem; background: white; border-radius: 6px; border: 1px solid #e1e4e8;">
                <div style="color: #586069; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.25rem;">CITATION COUNT</div>
                <div style="color: ${citationsColor}; font-size: 1.6rem; font-weight: 700;">${citationsRate}%</div>
                <div style="color: #586069; font-size: 0.75rem;">${stats.major_fields.citation_count?.acquired || 0}/${stats.total_entries}</div>
            </div>`;

            // Impact Factor
            const ifRate = stats.major_fields.impact_factor ?
                Math.round((stats.major_fields.impact_factor.acquired / stats.total_entries) * 100) : 0;
            const ifColor = ifRate >= 70 ? '#28a745' : ifRate >= 40 ? '#e67700' : '#d73a49';
            html += `<div style="text-align: center; padding: 0.75rem; background: white; border-radius: 6px; border: 1px solid #e1e4e8;">
                <div style="color: #586069; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.25rem;">IMPACT FACTOR</div>
                <div style="color: ${ifColor}; font-size: 1.6rem; font-weight: 700;">${ifRate}%</div>
                <div style="color: #586069; font-size: 0.75rem;">${stats.major_fields.impact_factor?.acquired || 0}/${stats.total_entries}</div>
            </div>`;

            html += `</div></div>`;
        }
    }

    if (!diffData || diffData.length === 0) {
        html += '<div style="text-align: center; padding: 3rem; color: #586069; background: #ffffff;">';
        html += '<i class="fas fa-check-circle" style="font-size: 3rem; margin-bottom: 1rem; display: block; color: #28a745;"></i>';
        html += '<p style="font-size: 1.1rem;">All entries are already complete!</p>';
        html += '<p style="font-size: 0.9rem;">No new fields were added during enrichment.</p>';
        html += '</div>';
        const content = document.getElementById('bibtexDiffContent') as HTMLElement | null;
        if (content) content.innerHTML = html;
        return;
    }

    // Display entries in GitHub-style diff format
    diffData.forEach((entry: any) => {
        html += `<div style="margin-bottom: 1.5rem; border: 1px solid #d1d5da; border-radius: 6px; overflow: hidden;">`;
        html += `<div style="background: #f6f8fa; padding: 0.5rem 1rem; font-family: monospace; font-weight: 600; color: #24292e;">@${entry.type}{${entry.key}}</div>`;

        // Show added fields
        if (entry.added_fields && entry.added_fields.length > 0) {
            html += `<div style="background: #e6ffed; padding: 1rem;">`;
            entry.added_fields.forEach((field: any) => {
                const fieldValue = field.value.length > 100 ? field.value.substring(0, 100) + '...' : field.value;
                html += `<div style="margin-bottom: 0.5rem; font-family: monospace; font-size: 0.9rem;">`;
                html += `<span style="color: #22863a; font-weight: 600;">+ ${field.name}</span> = `;
                html += `<span style="color: #032f62;">{${fieldValue}}</span>`;
                html += `</div>`;
            });
            html += `</div>`;
        }

        // Show changed fields
        if (entry.changed_fields && entry.changed_fields.length > 0) {
            html += `<div style="background: #fff5b1; padding: 1rem;">`;
            entry.changed_fields.forEach((field: any) => {
                const oldValue = field.old_value.length > 80 ? field.old_value.substring(0, 80) + '...' : field.old_value;
                const newValue = field.new_value.length > 80 ? field.new_value.substring(0, 80) + '...' : field.new_value;
                html += `<div style="margin-bottom: 0.75rem; font-family: monospace; font-size: 0.9rem;">`;
                html += `<div style="color: #b31d28; margin-bottom: 0.25rem;">- ${field.name} = {${oldValue}}</div>`;
                html += `<div style="color: #22863a;">+ ${field.name} = {${newValue}}</div>`;
                html += `</div>`;
            });
            html += `</div>`;
        }

        // Show unchanged fields (optional, grayed out)
        if (entry.unchanged_fields && entry.unchanged_fields.length > 0) {
            html += `<div style="background: #fafbfc; padding: 1rem; border-top: 1px solid #e1e4e8;">`;
            html += `<div style="color: #6a737d; font-size: 0.85rem; margin-bottom: 0.5rem; font-weight: 600;">Unchanged fields (${entry.unchanged_fields.length})</div>`;
            entry.unchanged_fields.forEach((field: any) => {
                const fieldValue = field.value.length > 80 ? field.value.substring(0, 80) + '...' : field.value;
                html += `<div style="margin-bottom: 0.35rem; font-family: monospace; font-size: 0.85rem; color: #6a737d;">`;
                html += `  ${field.name} = {${fieldValue}}`;
                html += `</div>`;
            });
            html += `</div>`;
        }

        html += `</div>`;
    });

    const content = document.getElementById('bibtexDiffContent') as HTMLElement | null;
    if (content) content.innerHTML = html;
}

/**
 * Close BibTeX diff modal
 */
(window as any).closeBibtexDiff = function(): void {
    const modal = document.getElementById('bibtexDiffModal') as HTMLElement | null;
    if (modal) modal.style.display = 'none';
};

/**
 * Toggle processing log visibility in the running indicator
 */
(window as any).toggleProcessingLogVisibility = function(): void {
    const log = document.getElementById('enrichmentProcessingLog') as HTMLElement | null;
    const icon = document.getElementById('logToggleIcon') as HTMLElement | null;

    if (log && icon) {
        if (log.style.display === 'none') {
            log.style.display = 'block';
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-up');
        } else {
            log.style.display = 'none';
            icon.classList.remove('fa-chevron-up');
            icon.classList.add('fa-chevron-down');
        }
    }
};

/**
 * Recent job interface
 */
interface RecentJob {
    id: string;
    original_filename: string;
    status: string;
    total_papers: number;
    processed_papers: number;
    failed_papers: number;
    created_at: string | null;
    completed_at: string | null;
    progress_percentage: number;
    project_name: string | null;
}

/**
 * Recent jobs API response
 */
interface RecentJobsResponse {
    success: boolean;
    jobs: RecentJob[];
    total: number;
}

/**
 * Load and display recent jobs
 */
async function loadRecentJobs(): Promise<void> {
    try {
        const response = await fetch('/scholar/api/bibtex/recent-jobs/');
        if (!response.ok) {
            console.warn('[BibTeX] Failed to load recent jobs:', response.status);
            return;
        }

        const data: RecentJobsResponse = await response.json();

        if (!data.success || !data.jobs || data.jobs.length === 0) {
            // Show "no jobs" message
            const noJobsMsg = document.getElementById('noRecentJobsMessage');
            const jobsContainer = document.getElementById('recentJobsContainer');
            if (noJobsMsg) noJobsMsg.style.display = 'block';
            if (jobsContainer) jobsContainer.style.display = 'none';
            return;
        }

        // Hide "no jobs" message and show container
        const noJobsMsg = document.getElementById('noRecentJobsMessage');
        const jobsContainer = document.getElementById('recentJobsContainer');
        if (noJobsMsg) noJobsMsg.style.display = 'none';
        if (jobsContainer) {
            jobsContainer.style.display = 'flex';
            renderRecentJobs(data.jobs, jobsContainer);
        }

    } catch (error) {
        console.error('[BibTeX] Error loading recent jobs:', error);
    }
}

/**
 * Render recent jobs as compact cards
 */
function renderRecentJobs(jobs: RecentJob[], container: HTMLElement): void {
    container.innerHTML = jobs.map(job => {
        const statusBadgeData = getStatusBadgeData(job.status);
        const jobUrl = `/scholar/bibtex/job/${job.id}/`;
        const downloadUrl = `/scholar/api/bibtex/job/${job.id}/download/`;

        return `
            <div class="recent-job-card" style="position: relative; min-width: 180px; max-width: 200px; padding: 0.75rem; border: 1px solid var(--color-border-default); border-radius: 6px; background: var(--color-canvas-subtle); transition: all 0.2s ease; box-shadow: 0 1px 3px rgba(0,0,0,0.12); display: flex; flex-direction: column; gap: 0.6rem;">

                <!-- Close button -->
                <button onclick="event.stopPropagation(); deleteJob('${job.id}')"
                        style="position: absolute; top: 0.4rem; right: 0.4rem; background: none; border: none; color: var(--color-fg-muted); cursor: pointer; padding: 3px; border-radius: 3px; font-size: 0.75rem; line-height: 1; transition: all 0.2s; z-index: 10;"
                        onmouseover="this.style.background='var(--color-danger-subtle)'; this.style.color='var(--color-danger-fg)';"
                        onmouseout="this.style.background='none'; this.style.color='var(--color-fg-muted)';"
                        title="Delete job">
                    <i class="fas fa-times"></i>
                </button>

                <!-- Filename with icon -->
                <div style="display: flex; align-items: center; gap: 0.4rem; padding-right: 1.2rem; cursor: pointer;" onclick="window.location.href='${jobUrl}'">
                    <i class="fas fa-check-circle" style="color: var(--scitex-color-03); font-size: 0.85rem;"></i>
                    <div style="font-weight: 500; color: var(--color-fg-default); font-size: 0.8rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1;" title="${job.original_filename}">
                        ${job.original_filename}
                    </div>
                </div>

                <!-- Paper count -->
                <div style="font-size: 0.7rem; color: var(--color-fg-muted); cursor: pointer;" onclick="window.location.href='${jobUrl}'">
                    ${job.total_papers || 0} papers
                </div>

                <!-- Progress bar (if processing) -->
                ${job.status === 'processing' && job.progress_percentage !== undefined ? `
                    <div style="background: var(--color-border-default); height: 3px; border-radius: 2px; overflow: hidden;">
                        <div style="height: 100%; background: var(--scitex-color-03); width: ${job.progress_percentage}%; transition: width 0.3s ease;"></div>
                    </div>
                ` : ''}

                <!-- Action buttons -->
                ${job.status === 'completed' ? `
                    <div style="display: flex; gap: 0.4rem; margin-top: auto;">
                        <button onclick="event.stopPropagation(); saveJobToProject('${job.id}')"
                                class="btn btn-warning"
                                style="flex: 1; padding: 0.4rem; font-size: 0.7rem; display: flex; align-items: center; justify-content: center; gap: 0.3rem; border: none;"
                                title="Save to project">
                            <i class="fas fa-save" style="font-size: 0.7rem;"></i>
                        </button>

                        <button onclick="event.stopPropagation(); window.location.href='${downloadUrl}'"
                                class="btn btn-success"
                                style="flex: 1; padding: 0.4rem; font-size: 0.7rem; display: flex; align-items: center; justify-content: center; gap: 0.3rem; border: none;"
                                title="Download enriched BibTeX">
                            <i class="fas fa-download" style="font-size: 0.7rem;"></i>
                        </button>

                        <button onclick="event.stopPropagation(); window.currentBibtexJobId='${job.id}'; showBibtexDiff();"
                                class="btn btn-secondary"
                                style="flex: 1; padding: 0.4rem; font-size: 0.7rem; display: flex; align-items: center; justify-content: center; gap: 0.3rem; border: none;"
                                title="Show what was enhanced">
                            <i class="fas fa-code-branch" style="font-size: 0.7rem;"></i>
                        </button>

                        <button onclick="event.stopPropagation(); window.currentBibtexJobId='${job.id}'; openAllPaperUrls();"
                                class="btn btn-info"
                                style="flex: 1; padding: 0.4rem; font-size: 0.7rem; display: flex; align-items: center; justify-content: center; gap: 0.3rem; border: none;"
                                title="Open all URLs">
                            <i class="fas fa-external-link-alt" style="font-size: 0.7rem;"></i>
                        </button>
                    </div>
                ` : ''}

                <!-- Disabled buttons for non-completed jobs -->
                ${job.status !== 'completed' ? `
                    <div style="display: flex; gap: 0.4rem; margin-top: auto;">
                        <button disabled
                                style="flex: 1; padding: 0.4rem; background: var(--color-neutral-muted); border: none; border-radius: 4px; color: var(--color-fg-muted); font-size: 0.7rem; cursor: not-allowed; display: flex; align-items: center; justify-content: center; gap: 0.3rem; opacity: 0.5;">
                            <i class="fas fa-save" style="font-size: 0.7rem;"></i>
                        </button>
                        <button disabled
                                style="flex: 1; padding: 0.4rem; background: var(--color-neutral-muted); border: none; border-radius: 4px; color: var(--color-fg-muted); font-size: 0.7rem; cursor: not-allowed; display: flex; align-items: center; justify-content: center; gap: 0.3rem; opacity: 0.5;">
                            <i class="fas fa-download" style="font-size: 0.7rem;"></i>
                        </button>
                        <button disabled
                                style="flex: 1; padding: 0.4rem; background: var(--color-neutral-muted); border: none; border-radius: 4px; color: var(--color-fg-muted); font-size: 0.7rem; cursor: not-allowed; display: flex; align-items: center; justify-content: center; gap: 0.3rem; opacity: 0.5;">
                            <i class="fas fa-external-link-alt" style="font-size: 0.7rem;"></i>
                        </button>
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

/**
 * Get status badge styling data
 */
function getStatusBadgeData(status: string): { text: string; bgColor: string; textColor: string } {
    const badges: { [key: string]: { text: string; bgColor: string; textColor: string } } = {
        'completed': {
            text: 'Completed',
            bgColor: 'var(--scitex-color-03)',
            textColor: 'white'
        },
        'processing': {
            text: 'Processing',
            bgColor: 'var(--scitex-color-04)',
            textColor: 'var(--color-fg-default)'
        },
        'failed': {
            text: 'Failed',
            bgColor: 'var(--color-danger-emphasis)',
            textColor: 'white'
        },
        'pending': {
            text: 'Pending',
            bgColor: 'var(--color-neutral-muted)',
            textColor: 'var(--color-fg-default)'
        },
        'cancelled': {
            text: 'Cancelled',
            bgColor: 'var(--color-danger-subtle)',
            textColor: 'var(--color-danger-fg)'
        }
    };

    return badges[status] || badges['pending'];
}

/**
 * Delete a job (placeholder function - implement with API call)
 */
(window as any).deleteJob = async function(jobId: string): Promise<void> {
    try {
        const csrfToken = (document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement)?.value;
        const response = await fetch(`/scholar/api/bibtex/job/${jobId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            // Reload recent jobs
            await loadRecentJobs();
        } else {
            alert('Failed to delete job');
        }
    } catch (error) {
        console.error('Error deleting job:', error);
        alert('Failed to delete job');
    }
};

/**
 * Show alert banner at top of page
 */
function showAlert(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'success'): void {
    // Remove any existing alerts
    const existingAlerts = document.querySelectorAll('.scholar-alert');
    existingAlerts.forEach(alert => alert.remove());

    // Create alert element
    const alert = document.createElement('div');
    alert.className = `scholar-alert scholar-alert-${type}`;
    alert.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 10000;
        background: ${type === 'success' ? 'var(--success-color)' : type === 'error' ? 'var(--error-color)' : type === 'warning' ? 'var(--warning-color)' : 'var(--info-color)'};
        color: white;
        padding: 1rem 2rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        gap: 1rem;
        min-width: 300px;
        max-width: 600px;
        animation: slideDown 0.3s ease-out;
    `;

    const icon = type === 'success' ? 'check-circle' :
                 type === 'error' ? 'times-circle' :
                 type === 'warning' ? 'exclamation-triangle' : 'info-circle';

    alert.innerHTML = `
        <i class="fas fa-${icon}" style="font-size: 1.5rem; flex-shrink: 0;"></i>
        <div style="flex: 1; line-height: 1.6;">${message}</div>
        <button onclick="this.parentElement.remove()" style="background: none; border: none; color: white; font-size: 1.5rem; cursor: pointer; padding: 0; line-height: 1; flex-shrink: 0;">
            <i class="fas fa-times"></i>
        </button>
    `;

    // Add animation keyframes if not already added
    if (!document.getElementById('alert-animation-styles')) {
        const style = document.createElement('style');
        style.id = 'alert-animation-styles';
        style.textContent = `
            @keyframes slideDown {
                from {
                    transform: translateX(-50%) translateY(-100px);
                    opacity: 0;
                }
                to {
                    transform: translateX(-50%) translateY(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(style);
    }

    document.body.appendChild(alert);

    // Don't auto-remove - let user close it manually
}

/**
 * Handle save to project button click
 */
(window as any).handleSaveToProject = async function(): Promise<void> {
    // Get the button and add loading state
    const saveBtn = document.getElementById('saveToProjectBtn') as HTMLButtonElement;
    if (!saveBtn) return;

    // Store original button content
    const originalHTML = saveBtn.innerHTML;

    // Set loading state
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    saveBtn.style.opacity = '0.7';

    try {
        // Get current job ID from the global state
        const jobId = window.currentBibtexJobId;
        if (!jobId) {
            throw new Error('No job ID found');
        }

        await saveJobToProject(jobId);
    } catch (error) {
        console.error('[Handle Save] Error:', error);
        showAlert('Failed to save to project. Please try again.', 'error');
    } finally {
        // Restore button state
        saveBtn.disabled = false;
        saveBtn.innerHTML = originalHTML;
        saveBtn.style.opacity = '1';
    }
};

/**
 * Save a job to the current/default project
 */
(window as any).saveJobToProject = async function(jobId: string): Promise<void> {
    console.log('[Save to Project] Job ID:', jobId);

    // Get current project ID from hidden input or use default
    const projectInput = document.getElementById('projectSelector') as HTMLInputElement;
    const projectId = projectInput?.value;

    console.log('[Save to Project] Project ID:', projectId);

    if (!projectId) {
        showAlert('⚠ No project selected. Please select a project first.', 'warning');
        return;
    }

    const csrfToken = (document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement)?.value;
    console.log('[Save to Project] CSRF Token:', csrfToken ? 'Present' : 'Missing');

    const response = await fetch(`/scholar/api/bibtex/job/${jobId}/save-to-project/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `project_id=${encodeURIComponent(projectId)}`
    });

    console.log('[Save to Project] Response status:', response.status);

    const data = await response.json();
    console.log('[Save to Project] Response data:', data);

    if (response.ok && data.success) {
        const projectName = data.project || 'project';

        // Build detailed success message with file paths
        let message = `✓ Successfully saved to <strong>${projectName}</strong>`;

        if (data.paths) {
            message += '<br><br><strong>Files saved:</strong><br>';
            if (data.paths.enriched) {
                message += `📄 <code>${data.paths.enriched}</code><br>`;
            }
            if (data.paths.merged && data.committed) {
                message += `📚 <code>${data.paths.merged}</code> (merged bibliography)`;
            }
        }

        if (data.committed) {
            message += '<br><br>✅ Auto-committed to Git repository';
        }

        showAlert(message, 'success');
    } else {
        showAlert(`❌ Failed to save to project: ${data.error || 'Unknown error'}`, 'error');
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    initBibtexEnrichment();
    loadRecentJobs();
});
