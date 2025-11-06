/**

 * BibTeX Enrichment Queue Management System
 *
 * Handles:
 * - Resource monitoring and display
 * - Queue position visualization
 * - Job cancellation
 * - Privacy/security (only show user's own jobs)
 *
 * @requires Django CSRF token in page
 * @requires URL endpoints configured
 *
 * @version 1.0.0
 */
interface JobData {
    id: string;
    filename: string;
    progress: number;
    processed: number;
    total: number;
    can_cancel: boolean;
    position?: number;
}
/**
 * Jobs response interface
 */
interface JobsData {
    active: JobData[];
    queued: JobData[];
    active_count: number;
    queued_count: number;
}
/**
 * System stats interface
 */
interface SystemStats {
    cpu_percent: string;
    memory_percent: string;
}
/**
 * Resource status response interface
 */
interface ResourceStatusResponse {
    system: SystemStats;
    jobs: JobsData;
    timestamp: string;
}
/**
 * Queue management configuration
 */
interface QueueConfig {
    resourceStatusUrl?: string;
    pollInterval?: number;
}
declare let resourceMonitorInterval: number | null;
/**
 * Initialize queue management system
 */
declare function initQueueManagement(config?: QueueConfig): void;
/**
 * Stop queue management monitoring
 */
declare function stopQueueManagement(): void;
/**
 * Update resource monitor display
 */
declare function updateResourceMonitor(resourceStatusUrl: string): void;
/**
 * Update system statistics display
 */
declare function updateSystemStats(system: SystemStats): void;
/**
 * Update active jobs display
 */
declare function updateActiveJobs(jobs: JobsData): void;
/**
 * Render a single active job card
 */
declare function renderActiveJob(job: JobData): string;
/**
 * Update queued jobs display
 */
declare function updateQueuedJobs(jobs: JobsData): void;
/**
 * Render a single queued job card with position indicator
 */
declare function renderQueuedJob(job: JobData): string;
/**
 * Render privacy message when other users have jobs
 */
declare function renderPrivacyMessage(count: number, status: string): string;
/**
 * Update refresh time display
 */
declare function updateRefreshTime(timestamp: string): void;
/**
 * Escape HTML to prevent XSS
 */
declare function escapeHtml(text: string): string;
/**
 * Check if queue management should be active
 */
declare function shouldRunQueueManagement(): boolean;
//# sourceMappingURL=queue-management.d.ts.map