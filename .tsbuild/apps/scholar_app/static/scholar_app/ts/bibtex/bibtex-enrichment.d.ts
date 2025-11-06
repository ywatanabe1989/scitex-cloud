/**

 * BibTeX Enrichment Functionality
 *
 * Handles file upload, job submission, status polling, download, URL opening, diff/comparison
 * for the BibTeX enrichment system. This file manages the complete workflow from uploading
 * a BibTeX file to downloading the enriched version with added metadata.
 *
 * @version 1.0.0
 */
declare let jobStatusInterval: number | null;
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
declare function initBibtexEnrichment(config?: BibtexEnrichmentConfig): void;
/**
 * Poll BibTeX job status
 */
declare function pollBibtexJobStatus(jobId: string, attempts?: number): void;
/**
 * Auto-download BibTeX file when enrichment completes
 */
declare function autoDownloadBibtexFile(url: string): void;
/**
 * Display the diff in a readable format (GitHub-style)
 */
declare function displayBibtexDiff(diffData: any[], stats: any): void;
//# sourceMappingURL=bibtex-enrichment.d.ts.map