/**
 * SaveService handles undo/redo and history management
 */

import { HistoryEntry, SectionName, DocumentType } from '@/types';
import { writerStorage } from '@/utils/storage';

interface HistoryState {
  [key: string]: HistoryEntry[];
}

interface HistoryIndex {
  [key: string]: number;
}

export class SaveService {
  private undoHistory: HistoryState = {};
  private currentHistoryIndex: HistoryIndex = {};
  private maxHistorySize = 30;

  constructor() {
    this.loadHistoryFromStorage();
  }

  /**
   * Add entry to history for a section
   */
  addToHistory(section: SectionName, content: string, wordCount: number): void {
    if (!this.undoHistory[section]) {
      this.undoHistory[section] = [];
      this.currentHistoryIndex[section] = -1;
    }

    const history = this.undoHistory[section];
    const currentIndex = this.currentHistoryIndex[section];

    // Remove any future history if we're not at the end
    if (currentIndex < history.length - 1) {
      history.splice(currentIndex + 1);
    }

    // Add new entry
    const entry: HistoryEntry = {
      content,
      wordCount,
      timestamp: new Date(),
      hash: this.generateHash(content),
    };

    history.push(entry);
    this.currentHistoryIndex[section] = history.length - 1;

    // Limit history size
    if (history.length > this.maxHistorySize) {
      history.shift();
      this.currentHistoryIndex[section]--;
    }

    this.saveHistoryToStorage();
  }

  /**
   * Undo to previous state
   */
  undo(section: SectionName): HistoryEntry | null {
    if (!this.undoHistory[section]) return null;

    const history = this.undoHistory[section];
    const currentIndex = this.currentHistoryIndex[section];

    if (currentIndex > 0) {
      this.currentHistoryIndex[section]--;
      this.saveHistoryToStorage();
      return history[this.currentHistoryIndex[section]];
    }

    return null;
  }

  /**
   * Redo to next state
   */
  redo(section: SectionName): HistoryEntry | null {
    if (!this.undoHistory[section]) return null;

    const history = this.undoHistory[section];
    const currentIndex = this.currentHistoryIndex[section];

    if (currentIndex < history.length - 1) {
      this.currentHistoryIndex[section]++;
      this.saveHistoryToStorage();
      return history[this.currentHistoryIndex[section]];
    }

    return null;
  }

  /**
   * Check if undo is available
   */
  canUndo(section: SectionName): boolean {
    const index = this.currentHistoryIndex[section];
    return index !== undefined && index > 0;
  }

  /**
   * Check if redo is available
   */
  canRedo(section: SectionName): boolean {
    if (!this.undoHistory[section]) return false;
    const index = this.currentHistoryIndex[section];
    return index < this.undoHistory[section].length - 1;
  }

  /**
   * Get current history entry
   */
  getCurrentEntry(section: SectionName): HistoryEntry | null {
    if (!this.undoHistory[section]) return null;

    const history = this.undoHistory[section];
    const index = this.currentHistoryIndex[section];

    if (index >= 0 && index < history.length) {
      return history[index];
    }

    return null;
  }

  /**
   * Get history for a section
   */
  getHistory(section: SectionName): HistoryEntry[] {
    return this.undoHistory[section] || [];
  }

  /**
   * Clear history for a section
   */
  clearHistory(section: SectionName): void {
    this.undoHistory[section] = [];
    this.currentHistoryIndex[section] = -1;
    this.saveHistoryToStorage();
  }

  /**
   * Clear all history
   */
  clearAllHistory(): void {
    this.undoHistory = {};
    this.currentHistoryIndex = {};
    writerStorage.remove('undoHistory');
    writerStorage.remove('currentHistoryIndex');
  }

  /**
   * Save history to localStorage
   */
  private saveHistoryToStorage(): void {
    // Only save essential data to minimize storage
    const compactHistory: { [section: string]: { content: string; wordCount: number; timestamp: string }[] } = {};

    Object.entries(this.undoHistory).forEach(([section, entries]) => {
      compactHistory[section] = entries.map(entry => ({
        content: entry.content,
        wordCount: entry.wordCount,
        timestamp: entry.timestamp.toISOString(),
      }));
    });

    writerStorage.save('undoHistory', compactHistory);
    writerStorage.save('currentHistoryIndex', this.currentHistoryIndex);
  }

  /**
   * Load history from localStorage
   */
  private loadHistoryFromStorage(): void {
    const history = writerStorage.load<any>('undoHistory');
    const indices = writerStorage.load<HistoryIndex>('currentHistoryIndex');

    if (history) {
      Object.entries(history).forEach(([section, entries]: [string, any]) => {
        this.undoHistory[section] = entries.map((entry: any) => ({
          content: entry.content,
          wordCount: entry.wordCount,
          timestamp: new Date(entry.timestamp),
          hash: this.generateHash(entry.content),
        }));
      });
    }

    if (indices) {
      this.currentHistoryIndex = indices;
    }
  }

  /**
   * Generate simple hash for content comparison
   */
  private generateHash(content: string): string {
    let hash = 0;
    for (let i = 0; i < content.length; i++) {
      const char = content.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return hash.toString(36);
  }

  /**
   * Get history statistics
   */
  getHistoryStats(): { totalEntries: number; sections: string[]; maxSize: number } {
    return {
      totalEntries: Object.values(this.undoHistory).reduce((sum, history) => sum + history.length, 0),
      sections: Object.keys(this.undoHistory),
      maxSize: this.maxHistorySize,
    };
  }

  /**
   * Set max history size
   */
  setMaxHistorySize(size: number): void {
    this.maxHistorySize = Math.max(1, Math.min(size, 100)); // Limit between 1 and 100

    // Trim existing histories if necessary
    Object.keys(this.undoHistory).forEach(section => {
      const history = this.undoHistory[section];
      if (history.length > this.maxHistorySize) {
        history.splice(0, history.length - this.maxHistorySize);
        const index = this.currentHistoryIndex[section];
        if (index >= history.length) {
          this.currentHistoryIndex[section] = history.length - 1;
        }
      }
    });

    this.saveHistoryToStorage();
  }
}

// Global SaveService instance
export const saveService = new SaveService();
