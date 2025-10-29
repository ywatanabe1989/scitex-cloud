/**
 * API-related type definitions
 */

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface CompilationResponse extends ApiResponse {
  data?: {
    job_id: string;
    status: string;
    message: string;
  };
}

export interface PdfResponse extends ApiResponse {
  data?: {
    pdf_path: string;
    exists: boolean;
  };
}

export interface SectionResponse extends ApiResponse {
  data?: {
    content: string;
    wordCount: number;
    lastModified: string;
  };
}

export interface HistoryResponse extends ApiResponse {
  data?: {
    entries: HistoryEntry[];
    totalCount: number;
  };
}

export interface TexFilesResponse extends ApiResponse {
  data?: TexFile[];
}

export interface InitializeResponse extends ApiResponse {
  data?: {
    projectId: string;
    sections: SectionData;
    wordCounts: DocumentStats;
  };
}

export interface HistoryEntry {
  hash: string;
  message: string;
  author: string;
  timestamp: string;
  content?: string;
}

export interface SectionData {
  [docType: string]: {
    [sectionName: string]: string;
  };
}

export interface DocumentStats {
  [docType: string]: {
    [sectionName: string]: number;
  };
}

export interface TexFile {
  path: string;
  name: string;
  section: string;
  docType: string;
}

export interface RequestConfig {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  url: string;
  data?: any;
  headers?: Record<string, string>;
  timeout?: number;
}

export interface DiffResponse extends ApiResponse {
  data?: {
    diff: string;
    pdfPath?: string;
  };
}
