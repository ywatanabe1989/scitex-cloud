/**

 * BibTeX Job Detail UI Module
 *
 * Handles UI interactions for the BibTeX job detail page including:
 * - Copy log to clipboard with visual feedback
 * - Expand/collapse log viewer
 * - Keyboard shortcuts for log selection
 * - Elapsed time tracking
 * - Real-time job status polling
 *
 * @module bibtex/job-detail-ui
 */
/**
 * Copy log content to clipboard with visual feedback
 *
 * @param {HTMLButtonElement} button - The copy button element
 * @param {HTMLPreElement} logElement - The log content element
 */
declare function copyLogToClipboard(button: HTMLButtonElement, logElement: HTMLPreElement): Promise<void>;
/**
 * Toggle log viewer size between compact and expanded
 *
 * @param {HTMLButtonElement} button - The toggle button element
 * @param {HTMLPreElement} logElement - The log content element
 * @param {boolean} expanded - Current expanded state
 * @returns {boolean} New expanded state
 */
declare function toggleLogSize(button: HTMLButtonElement, logElement: HTMLPreElement, expanded: boolean): boolean;
/**
 * Handle Ctrl+A keyboard shortcut to select only log content
 *
 * @param {KeyboardEvent} event - The keyboard event
 * @param {HTMLPreElement} logElement - The log content element
 */
declare function handleLogKeyboardShortcut(event: KeyboardEvent, logElement: HTMLPreElement): void;
/**
 * Update elapsed time display
 *
 * @param {Date | null} startedAt - Job start timestamp
 * @param {HTMLElement} elapsedTimeEl - Element to update with elapsed time
 */
declare function updateElapsedTime(startedAt: Date | null, elapsedTimeEl: HTMLElement): void;
/**
 * Poll job status and update UI in real-time
 *
 * @param {string} jobId - The job ID to poll
 * @param {string} jobStatus - Current job status
 * @param {HTMLPreElement | null} logElement - Log content element
 * @param {number} attempts - Current polling attempt number
 * @param {number} maxAttempts - Maximum polling attempts (default: 90)
 */
declare function pollJobStatus(jobId: string, jobStatus: string, logElement: HTMLPreElement | null, attempts?: number, maxAttempts?: number): void;
/**
 * Initialize job detail UI
 * Should be called from template with data-job-id attribute
 */
declare function initJobDetailUI(): void;
export { initJobDetailUI, copyLogToClipboard, toggleLogSize, handleLogKeyboardShortcut, updateElapsedTime, pollJobStatus, };
//# sourceMappingURL=job-detail-ui.d.ts.map