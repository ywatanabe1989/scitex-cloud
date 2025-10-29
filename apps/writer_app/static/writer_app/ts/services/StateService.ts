/**
 * StateService manages editor and application state persistence
 */

import { SectionName, DocumentType, EditorState, PreviewState } from '@/types';
import { writerStorage } from '@/utils/storage';

export interface AppState {
  currentSection: SectionName;
  currentDocType: DocumentType;
  editorState: EditorState;
  previewState: PreviewState;
  hasUnsavedChanges: boolean;
  liveCompilationEnabled: boolean;
  sidebarCollapsed: boolean;
  compilationPanelVisible: boolean;
  timestamp: number;
}

export class StateService {
  private state: Partial<AppState> = {};

  constructor() {
    this.loadFromStorage();
  }

  /**
   * Set a state value
   */
  setState<K extends keyof AppState>(key: K, value: AppState[K]): void {
    this.state[key] = value;
    this.saveToStorage();
  }

  /**
   * Get a state value
   */
  getState<K extends keyof AppState>(key: K): AppState[K] | undefined {
    return this.state[key];
  }

  /**
   * Update multiple state values
   */
  updateState(updates: Partial<AppState>): void {
    this.state = { ...this.state, ...updates };
    this.saveToStorage();
  }

  /**
   * Get entire state
   */
  getAllState(): Partial<AppState> {
    return { ...this.state };
  }

  /**
   * Reset state to defaults
   */
  resetState(): void {
    this.state = {
      currentSection: 'abstract' as SectionName,
      currentDocType: 'manuscript' as DocumentType,
      hasUnsavedChanges: false,
      liveCompilationEnabled: true,
      sidebarCollapsed: false,
      compilationPanelVisible: false,
    };
    this.saveToStorage();
  }

  /**
   * Clear all state
   */
  clearState(): void {
    this.state = {};
    writerStorage.remove('editorState');
  }

  /**
   * Check if state exists in storage
   */
  hasState(): boolean {
    return writerStorage.exists('editorState');
  }

  /**
   * Save state to localStorage
   */
  private saveToStorage(): void {
    const stateToSave = {
      ...this.state,
      timestamp: Date.now(),
    };
    writerStorage.save('editorState', stateToSave);
  }

  /**
   * Load state from localStorage
   */
  private loadFromStorage(): void {
    const saved = writerStorage.load<AppState>('editorState');
    if (saved) {
      // Only load if it's not too old (24 hours)
      const maxAge = 24 * 60 * 60 * 1000;
      if (Date.now() - (saved.timestamp || 0) < maxAge) {
        this.state = saved;
      } else {
        this.resetState();
      }
    }
  }

  /**
   * Export state as JSON for debugging
   */
  exportState(): string {
    return JSON.stringify(this.state, null, 2);
  }

  /**
   * Import state from JSON
   */
  importState(json: string): boolean {
    try {
      const imported = JSON.parse(json);
      this.state = imported;
      this.saveToStorage();
      return true;
    } catch (error) {
      console.error('Failed to import state', error);
      return false;
    }
  }
}

// Global StateService instance
export const stateService = new StateService();
