/**
 * Document and file-related type definitions
 */

export interface Document {
  id: string;
  title: string;
  docType: 'manuscript' | 'supplementary' | 'revision';
  createdAt: Date;
  updatedAt: Date;
  isDirty: boolean;
}

export interface TexFile {
  path: string;
  name: string;
  section: string;
  docType: string;
  size?: number;
  lastModified?: Date;
}

export interface CompilationResult {
  success: boolean;
  jobId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message?: string;
  output?: string;
  pdfPath?: string;
  timestamp: Date;
}

export interface WordCountStats {
  [sectionName: string]: number;
  total: number;
}

export interface DocumentStats {
  [docType: string]: WordCountStats;
}

export interface HistoryEntry {
  content: string;
  timestamp: Date;
  wordCount: number;
  hash?: string;
}

export interface HistoryState {
  [section: string]: HistoryEntry[];
}

export interface HistoryIndex {
  [section: string]: number;
}
