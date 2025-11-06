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

    if (attempts > 180) {
        console.error('[BibTeX] Polling timeout after 180 attempts');
        const log = document.getElementById('processingLog') as HTMLElement | null;
        if (log) log.textContent += '\n\n✗ Polling timeout. Please refresh the page.';
        return;
    }

    fetch(`/scholar/api/bibtex/job/${jobId}/status/`)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        })
        .then((data: JobStatusResponse) => {
            // Update progress
            if (data.progress_percentage !== undefined) {
                const progressBar = document.getElementById('progressBar') as HTMLElement | null;
                const progressPercentage = document.getElementById('progressPercentage') as HTMLElement | null;
                if (progressBar) progressBar.style.width = `${data.progress_percentage}%`;
                if (progressPercentage) progressPercentage.textContent = `${data.progress_percentage}%`;
            }

            // Update paper counts
            if (data.total_papers !== undefined) {
                let text = `${data.processed_papers} / ${data.total_papers} papers processed`;
                if (data.failed_papers && data.failed_papers > 0) text += ` (${data.failed_papers} failed)`;
                const progressDetails = document.getElementById('progressDetails') as HTMLElement | null;
                if (progressDetails) progressDetails.textContent = text;
            }

            // Update log
            if (data.log) {
                const processingLog = document.getElementById('processingLog') as HTMLElement | null;
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
                const downloadBtn = document.getElementById('downloadBtn') as HTMLAnchorElement | null;
                if (downloadBtn) {
                    downloadBtn.href = downloadUrl;
                    downloadBtn.classList.remove('disabled');
                    downloadBtn.style.opacity = '1';
                }

                // Enable other buttons
                const showDiffBtn = document.getElementById('showDiffBtn') as HTMLButtonElement | null;
                const openUrlsBtn = document.getElementById('openUrlsBtn') as HTMLButtonElement | null;

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
                    .then((urlData: any) => {
                        const count = urlData.total_urls || 0;
                        const urlCount = document.getElementById('urlCount') as HTMLElement | null;
                        if (urlCount) urlCount.textContent = count.toString();
                    })
                    .catch((error: Error) => {
                        console.error('[BibTeX] Failed to fetch URL count:', error);
                        const urlCount = document.getElementById('urlCount') as HTMLElement | null;
                        if (urlCount) urlCount.textContent = '?';
                    });

                // Auto-download the enriched file
                autoDownloadBibtexFile(downloadUrl);
            } else if (data.status === 'failed') {
                console.log('[BibTeX] Job failed:', data.error_message);
                const log = document.getElementById('processingLog') as HTMLElement | null;
                if (log) log.textContent += '\n\n✗ ERROR: ' + (data.error_message || 'Unknown error');
                setTimeout(() => resetBibtexForm(), 5000);
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
 * Auto-download BibTeX file when enrichment completes
 */
function autoDownloadBibtexFile(url: string): void {
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
                if (match) filename = match[1];
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
        .catch((error: Error) => {
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
                const confirmMsg = `Open ${data.total_urls} paper URL(s) in new tabs?\n\n` +
                    `Note: Your browser may block some pop-ups. Please allow pop-ups for this site if needed.`;

                if (confirm(confirmMsg)) {
                    console.log(`[Open URLs] Opening ${data.urls.length} URLs...`);

                    // Open all URLs immediately (no setTimeout to avoid popup blocker)
                    let openedCount = 0;
                    data.urls.forEach((paper: any) => {
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
                displayBibtexDiff(data.diff, data.stats);
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
function displayBibtexDiff(diffData: any[], stats: any): void {
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
        const content = document.getElementById('bibtexDiffContent') as HTMLElement | null;
        if (content) content.innerHTML = html;
        return;
    }

    // Display entries in GitHub-style diff format (abbreviated for token efficiency)
    diffData.forEach((entry: any) => {
        html += `<div style="margin-bottom: 1.5rem; border: 1px solid #d1d5da; border-radius: 6px; overflow: hidden;">`;
        html += `<div style="background: #f6f8fa; padding: 0.5rem 1rem; font-family: monospace;">@${entry.type}{${entry.key}}</div>`;
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
        const statusBadge = getStatusBadge(job.status);
        const createdDate = job.created_at ? new Date(job.created_at).toLocaleDateString() : 'Unknown';
        const jobUrl = `/scholar/bibtex/job/${job.id}/`;

        return `
            <div class="recent-job-card" style="min-width: 200px; padding: 1rem; border: 1px solid var(--color-border-default); border-radius: 6px; background: var(--color-canvas-subtle); cursor: pointer; transition: all 0.2s ease;" onclick="window.location.href='${jobUrl}'">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                    <div style="font-weight: 600; color: var(--color-fg-default); font-size: 0.9rem; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${job.original_filename}">
                        ${job.original_filename}
                    </div>
                    ${statusBadge}
                </div>
                <div style="font-size: 0.75rem; color: var(--color-fg-muted); margin-bottom: 0.5rem;">
                    ${job.total_papers || 0} papers
                </div>
                <div style="font-size: 0.7rem; color: var(--color-fg-muted);">
                    ${createdDate}
                </div>
                ${job.progress_percentage !== undefined && job.status === 'processing' ? `
                    <div style="margin-top: 0.5rem; background: var(--color-border-default); height: 4px; border-radius: 2px; overflow: hidden;">
                        <div style="height: 100%; background: var(--scitex-color-03); width: ${job.progress_percentage}%; transition: width 0.3s ease;"></div>
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

/**
 * Get status badge HTML
 */
function getStatusBadge(status: string): string {
    const badges: { [key: string]: { text: string; color: string } } = {
        'completed': { text: '✓', color: 'var(--scitex-color-03)' },
        'processing': { text: '⋯', color: 'var(--scitex-color-04)' },
        'failed': { text: '✗', color: 'var(--color-danger-fg)' },
        'pending': { text: '○', color: 'var(--color-fg-muted)' },
        'cancelled': { text: '✗', color: 'var(--color-fg-muted)' }
    };

    const badge = badges[status] || badges['pending'];
    return `<div style="font-size: 1.2rem; color: ${badge.color}; font-weight: bold;">${badge.text}</div>`;
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    initBibtexEnrichment();
    loadRecentJobs();
});
