/**
 * CompilationService handles LaTeX compilation and PDF management
 */

import {
  DocumentType,
  SectionName,
} from '@/types';
import { wait, SimpleTimer, formatElapsedTime } from '@/writer/utils/timer.utils';

declare const pdfjsLib: any;

export interface CompilationOptions {
  projectId: string;
  docType: DocumentType;
  maxAttempts?: number;
  pollInterval?: number;
}

export class CompilationService {
  private currentlyCompiling = false;
  private compilationTimer: SimpleTimer = new SimpleTimer();
  private liveCompileTimeout: NodeJS.Timeout | null = null;
  private liveCompilationEnabled = true;
  private mainPdfDoc: any = null;
  private diffPdfDoc: any = null;
  private hasDiffPdf = false;

  /**
   * Trigger LaTeX compilation
   */
  async compile(options: CompilationOptions): Promise<CompilationResult> {
    if (this.currentlyCompiling) {
      return {
        success: false,
        jobId: '',
        status: 'processing',
        message: 'Compilation already in progress',
        timestamp: new Date(),
      };
    }

    this.currentlyCompiling = true;
    this.compilationTimer.start();

    try {
      const response = await this.sendCompileRequest(options.projectId, options.docType);

      if (!response.success || !response.data?.job_id) {
        throw new Error(response.data?.message || 'Failed to start compilation');
      }

      const jobId = response.data.job_id;

      // Poll for completion
      const result = await this.pollCompilationStatus(
        jobId,
        options.projectId,
        options.maxAttempts ?? 60,
        options.pollInterval ?? 1000
      );

      return result;
    } catch (error) {
      console.error('Compilation error:', error);
      return {
        success: false,
        jobId: '',
        status: 'failed',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date(),
      };
    } finally {
      this.currentlyCompiling = false;
      this.compilationTimer.stop();
    }
  }

  /**
   * Poll compilation status until completion
   */
  private async pollCompilationStatus(
    jobId: string,
    projectId: string,
    maxAttempts: number,
    pollInterval: number,
    onProgress?: (attempt: number, total: number, elapsed: string) => void
  ): Promise<CompilationResult> {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      await wait(pollInterval);

      const response = await this.sendStatusRequest(jobId, projectId);

      if (!response.success) {
        continue;
      }

      const status = response.data?.status;
      const elapsed = formatElapsedTime(this.compilationTimer.getElapsed());

      if (onProgress) {
        onProgress(attempt + 1, maxAttempts, elapsed);
      }

      if (status === 'completed') {
        return {
          success: true,
          jobId,
          status: 'completed',
          pdfPath: response.data?.pdf_path,
          timestamp: new Date(),
        };
      } else if (status === 'failed') {
        return {
          success: false,
          jobId,
          status: 'failed',
          message: response.data?.error || 'Compilation failed',
          output: response.data?.output,
          timestamp: new Date(),
        };
      }
    }

    return {
      success: false,
      jobId,
      status: 'failed',
      message: 'Compilation timeout - exceeded maximum polling attempts',
      timestamp: new Date(),
    };
  }

  /**
   * Get elapsed compilation time
   */
  getCompilationTime(): string {
    return formatElapsedTime(this.compilationTimer.getElapsed());
  }

  /**
   * Check if currently compiling
   */
  isCompiling(): boolean {
    return this.currentlyCompiling;
  }

  /**
   * Enable/disable live compilation
   */
  setLiveCompilation(enabled: boolean): void {
    this.liveCompilationEnabled = enabled;
    if (!enabled && this.liveCompileTimeout) {
      clearTimeout(this.liveCompileTimeout);
      this.liveCompileTimeout = null;
    }
  }

  /**
   * Check if live compilation is enabled
   */
  isLiveCompilationEnabled(): boolean {
    return this.liveCompilationEnabled;
  }

  /**
   * Schedule live compilation with debounce
   */
  scheduleLiveCompile(
    callback: () => Promise<void>,
    delay: number = 3000
  ): void {
    if (!this.liveCompilationEnabled) {
      return;
    }

    if (this.liveCompileTimeout) {
      clearTimeout(this.liveCompileTimeout);
    }

    this.liveCompileTimeout = setTimeout(() => {
      callback().catch(error => console.error('Live compilation error:', error));
    }, delay);
  }

  /**
   * Load PDF document
   */
  async loadPdf(pdfPath: string): Promise<any> {
    if (typeof pdfjsLib === 'undefined') {
      console.error('PDF.js not loaded');
      return null;
    }

    try {
      const pdf = await pdfjsLib.getDocument(pdfPath).promise;
      this.mainPdfDoc = pdf;
      return pdf;
    } catch (error) {
      console.error('Failed to load PDF:', error);
      return null;
    }
  }

  /**
   * Load diff PDF
   */
  async loadDiffPdf(pdfPath: string): Promise<any> {
    if (typeof pdfjsLib === 'undefined') {
      console.error('PDF.js not loaded');
      return null;
    }

    try {
      const pdf = await pdfjsLib.getDocument(pdfPath).promise;
      this.diffPdfDoc = pdf;
      this.hasDiffPdf = true;
      return pdf;
    } catch (error) {
      console.error('Failed to load diff PDF:', error);
      return null;
    }
  }

  /**
   * Get main PDF document
   */
  getMainPdf(): any {
    return this.mainPdfDoc;
  }

  /**
   * Get diff PDF document
   */
  getDiffPdf(): any {
    return this.diffPdfDoc;
  }

  /**
   * Check if diff PDF is available
   */
  hasDiff(): boolean {
    return this.hasDiffPdf;
  }

  /**
   * Render PDF page
   */
  async renderPdfPage(
    pdf: any,
    pageNum: number,
    canvas: HTMLCanvasElement,
    scale: number = 1.5
  ): Promise<void> {
    try {
      const page = await pdf.getPage(pageNum);
      const viewport = page.getViewport({ scale });

      canvas.width = viewport.width;
      canvas.height = viewport.height;

      const context = canvas.getContext('2d');
      if (!context) throw new Error('Failed to get canvas context');

      await page.render({
        canvasContext: context,
        viewport,
      }).promise;
    } catch (error) {
      console.error(`Failed to render PDF page ${pageNum}:`, error);
      throw error;
    }
  }

  /**
   * Get PDF outline/bookmarks
   */
  async getPdfOutline(pdf: any): Promise<any[]> {
    try {
      return await pdf.getOutline();
    } catch (error) {
      console.error('Failed to get PDF outline:', error);
      return [];
    }
  }

  /**
   * Clean up resources
   */
  cleanup(): void {
    if (this.liveCompileTimeout) {
      clearTimeout(this.liveCompileTimeout);
    }
    if (this.compilationTimer.isActive()) {
      this.compilationTimer.stop();
    }
    this.mainPdfDoc = null;
    this.diffPdfDoc = null;
  }

  /**
   * Send compilation request to backend
   */
  private async sendCompileRequest(
    projectId: string,
    docType: DocumentType
  ): Promise<any> {
    // This will be implemented in WriterAPI service
    // For now, return a placeholder
    return { success: false };
  }

  /**
   * Send status check request to backend
   */
  private async sendStatusRequest(jobId: string, projectId: string): Promise<any> {
    // This will be implemented in WriterAPI service
    // For now, return a placeholder
    return { success: false };
  }
}

// Global CompilationService instance
export const compilationService = new CompilationService();
