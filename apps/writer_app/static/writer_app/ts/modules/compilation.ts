/**
 * Writer Compilation Module
 * Handles LaTeX compilation and PDF generation
 */

import { ApiClient } from '@/utils/api';
import { getCsrfToken } from '@/utils/csrf';
import { CompilationJob } from '@/types';

console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/modules/compilation.ts loaded");
export interface CompilationOptions {
    projectId: number;
    docType: string;
    content?: string;  // Optional: only for preview
    format?: 'pdf' | 'dvi';
    colorMode?: 'light' | 'dark';
    sectionName?: string;  // For section-specific preview files
}

export class CompilationManager {
    private apiClient: ApiClient;
    private currentJob: CompilationJob | null = null;
    private isCompiling: boolean = false;
    private onProgressCallback?: (progress: number, status: string) => void;
    private onCompleteCallback?: (jobId: string, pdfUrl: string) => void;
    private onErrorCallback?: (error: string) => void;

    constructor(apiBaseUrl: string = '') {
        this.apiClient = new ApiClient(apiBaseUrl);
    }

    /**
     * Compile preview (live editing with content)
     */
    async compilePreview(options: CompilationOptions): Promise<CompilationJob | null> {
        if (!options.content) {
            console.error('[CompilationPreview] Content is required for preview compilation');
            return null;
        }

        if (this.isCompiling) {
            console.warn('[CompilationPreview] Compilation already in progress');
            return null;
        }

        this.isCompiling = true;
        this.notifyProgress(0, 'Preparing preview...');

        try {
            const timeoutMs = 60000; // 60 seconds for preview
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

            const response = await fetch(
                `/writer/api/project/${options.projectId}/compile_preview/`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({
                        content: options.content,
                        timeout: 60,
                        color_mode: options.colorMode || 'light',
                        section_name: options.sectionName || 'preview'
                    }),
                    signal: controller.signal
                }
            );

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const result = await response.json() as any;

            console.log('[CompilationPreview] Result:', result.success);
            this.notifyProgress(50, 'Compiling preview...');

            if (result?.success === true) {
                this.notifyProgress(100, 'Preview ready');
                this.currentJob = { id: 'preview', status: 'completed', progress: 100 };

                const pdfPath = result.output_pdf || result.pdf_path;
                if (this.onCompleteCallback && pdfPath) {
                    this.onCompleteCallback('preview', pdfPath);
                }

                return this.currentJob;
            } else {
                throw new Error(result?.error || 'Preview compilation failed');
            }
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Preview compilation failed';
            this.notifyError(message);
            this.currentJob = null;
            return null;
        } finally {
            this.isCompiling = false;
        }
    }

    /**
     * Compile full manuscript from workspace (no content)
     */
    async compileFull(options: CompilationOptions): Promise<CompilationJob | null> {
        if (this.isCompiling) {
            console.warn('[CompilationFull] Compilation already in progress');
            return null;
        }

        this.isCompiling = true;
        this.notifyProgress(0, 'Preparing full compilation...');

        try {
            const timeoutMs = 300000; // 5 minutes for full compilation
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

            console.log('[CompilationFull] Starting:', options.docType);

            const response = await fetch(
                `/writer/api/project/${options.projectId}/compile_full/`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({
                        doc_type: options.docType,
                        timeout: 300
                    }),
                    signal: controller.signal
                }
            );

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const result = await response.json() as any;

            console.log('[CompilationFull] Result:', result);
            this.notifyProgress(50, 'Compiling manuscript...');

            if (result?.success === true) {
                this.notifyProgress(100, 'Manuscript compiled');
                this.currentJob = { id: 'full', status: 'completed', progress: 100 };

                const pdfPath = result.output_pdf || result.pdf_path;
                console.log('[CompilationFull] PDF path:', pdfPath);

                if (this.onCompleteCallback && pdfPath) {
                    this.onCompleteCallback('full', pdfPath);
                }

                return this.currentJob;
            } else {
                const errorMsg = result?.error || result?.log || 'Full compilation failed';
                console.error('[CompilationFull] Error:', errorMsg);
                throw new Error(errorMsg);
            }
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Full compilation failed';
            this.notifyError(message);
            this.currentJob = null;
            return null;
        } finally {
            this.isCompiling = false;
        }
    }

    /**
     * @deprecated Use compilePreview() or compileFull() instead
     */
    async compile(options: CompilationOptions): Promise<CompilationJob | null> {
        console.warn('[Compilation] DEPRECATED: Use compilePreview() or compileFull() instead');
        if (options.content) {
            return this.compilePreview(options);
        } else {
            return this.compileFull(options);
        }
    }

    /**
     * Get current job status
     */
    async getStatus(jobId: string): Promise<CompilationJob | null> {
        try {
            if (jobId === 'local') {
                // Local synchronous job
                return this.currentJob;
            }

            // This would be for async job polling (not currently used)
            return null;
        } catch (error) {
            console.error('[Compilation] Failed to get status:', error);
            return null;
        }
    }

    /**
     * Cancel compilation
     */
    async cancel(jobId: string): Promise<boolean> {
        try {
            const response = await this.apiClient.post<any>(
                `/writer/api/cancel-compilation/${jobId}/`,
                {}
            );

            return response.success;
        } catch (error) {
            console.error('[Compilation] Failed to cancel:', error);
            return false;
        }
    }

    /**
     * Check if currently compiling
     */
    getIsCompiling(): boolean {
        return this.isCompiling;
    }

    /**
     * Set progress callback
     */
    onProgress(callback: (progress: number, status: string) => void): void {
        this.onProgressCallback = callback;
    }

    /**
     * Set completion callback
     */
    onComplete(callback: (jobId: string, pdfUrl: string) => void): void {
        this.onCompleteCallback = callback;
    }

    /**
     * Set error callback
     */
    onError(callback: (error: string) => void): void {
        this.onErrorCallback = callback;
    }

    /**
     * Notify progress
     */
    private notifyProgress(progress: number, status: string): void {
        console.log(`[Compilation] ${progress}% - ${status}`);
        if (this.onProgressCallback) {
            this.onProgressCallback(progress, status);
        }
    }

    /**
     * Notify error
     */
    private notifyError(error: string): void {
        console.error('[Compilation] Error:', error);
        if (this.onErrorCallback) {
            this.onErrorCallback(error);
        }
    }

    /**
     * Check for existing PDF
     */
    async checkExistingPDF(projectSlug: string, docType: string = 'manuscript'): Promise<string | null> {
        try {
            const response = await this.apiClient.get<any>(
                `/writer/api/pdf/${projectSlug}/${docType}/`
            );

            if (response.success && response.data?.url) {
                return response.data.url;
            }

            return null;
        } catch (error) {
            console.error('[Compilation] Failed to check existing PDF:', error);
            return null;
        }
    }
}
