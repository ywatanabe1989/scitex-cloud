/**
 * WordCountService tracks word counts for sections
 */

import { SectionName, DocumentType, DocumentStats } from '@/types';
import { extractTextFromLatex } from '@/writer/utils/latex.utils';
import { writerStorage } from '@/utils/storage';

export class WordCountService {
  private wordCounts: DocumentStats = {};
  private serverWordCounts: DocumentStats = {};

  constructor() {
    this.loadFromStorage();
  }

  /**
   * Initialize word counts from server data
   */
  initializeFromServer(serverCounts: DocumentStats): void {
    this.serverWordCounts = JSON.parse(JSON.stringify(serverCounts)); // Deep copy
    this.wordCounts = JSON.parse(JSON.stringify(serverCounts));
    this.saveToStorage();
  }

  /**
   * Count words in content
   */
  countWords(content: string): number {
    if (!content) return 0;

    // Extract text from LaTeX
    const text = extractTextFromLatex(content);

    // Count words (split by whitespace)
    const words = text.trim().split(/\s+/);

    return words.filter(word => word.length > 0).length;
  }

  /**
   * Update word count for a section
   */
  updateSectionWordCount(docType: DocumentType, section: SectionName, content: string): number {
    const count = this.countWords(content);

    if (!this.wordCounts[docType]) {
      this.wordCounts[docType] = {};
    }

    this.wordCounts[docType][section] = count;
    this.saveToStorage();

    return count;
  }

  /**
   * Get word count for a section
   */
  getWordCount(docType: DocumentType, section: SectionName): number {
    return this.wordCounts[docType]?.[section] ?? 0;
  }

  /**
   * Get total word count for a document type
   */
  getTotalWordCount(docType: DocumentType): number {
    const sections = this.wordCounts[docType] || {};
    return Object.values(sections).reduce((sum, count) => sum + (count ?? 0), 0);
  }

  /**
   * Get all word counts
   */
  getAllWordCounts(): DocumentStats {
    return JSON.parse(JSON.stringify(this.wordCounts));
  }

  /**
   * Get word count statistics
   */
  getStats(): {
    docType: DocumentType;
    total: number;
    sections: { [section: string]: number };
  }[] {
    return Object.entries(this.wordCounts).map(([docType, sections]) => ({
      docType: docType as DocumentType,
      total: Object.values(sections).reduce((sum, count) => sum + (count ?? 0), 0),
      sections,
    }));
  }

  /**
   * Check if section has unsaved word count changes
   */
  hasChanges(docType: DocumentType, section: SectionName, currentCount: number): boolean {
    const savedCount = this.wordCounts[docType]?.[section] ?? 0;
    return currentCount !== savedCount;
  }

  /**
   * Save to localStorage
   */
  private saveToStorage(): void {
    writerStorage.save('wordCounts', this.wordCounts);
  }

  /**
   * Load from localStorage
   */
  private loadFromStorage(): void {
    const saved = writerStorage.load<DocumentStats>('wordCounts');
    if (saved) {
      this.wordCounts = saved;
    }
  }

  /**
   * Reset to server values
   */
  resetToServer(): void {
    this.wordCounts = JSON.parse(JSON.stringify(this.serverWordCounts));
    this.saveToStorage();
  }

  /**
   * Clear all word counts
   */
  clear(): void {
    this.wordCounts = {};
    writerStorage.remove('wordCounts');
  }
}

// Global WordCountService instance
export const wordCountService = new WordCountService();
