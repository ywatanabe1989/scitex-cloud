/**
 * LocalStorage utilities for state persistence
 */

export class StorageManager {
  private prefix = 'writer_app_';

  /**
   * Get item from localStorage with type safety
   */
  getItem<T>(key: string, defaultValue?: T): T | null {
    try {
      const item = localStorage.getItem(this.prefix + key);
      if (item === null) return defaultValue || null;
      return JSON.parse(item) as T;
    } catch (error) {
      console.error(`Failed to get item from storage: ${key}`, error);
      return defaultValue || null;
    }
  }

  /**
   * Set item in localStorage with type safety
   */
  setItem<T>(key: string, value: T): boolean {
    try {
      localStorage.setItem(this.prefix + key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error(`Failed to set item in storage: ${key}`, error);
      return false;
    }
  }

  /**
   * Remove item from localStorage
   */
  removeItem(key: string): boolean {
    try {
      localStorage.removeItem(this.prefix + key);
      return true;
    } catch (error) {
      console.error(`Failed to remove item from storage: ${key}`, error);
      return false;
    }
  }

  /**
   * Clear all writer app items from localStorage
   */
  clear(): boolean {
    try {
      const keysToRemove: string[] = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key?.startsWith(this.prefix)) {
          keysToRemove.push(key);
        }
      }
      keysToRemove.forEach(key => localStorage.removeItem(key));
      return true;
    } catch (error) {
      console.error('Failed to clear storage', error);
      return false;
    }
  }

  /**
   * Check if key exists in localStorage
   */
  hasItem(key: string): boolean {
    return localStorage.getItem(this.prefix + key) !== null;
  }

  /**
   * Get all keys stored for writer app
   */
  getAllKeys(): string[] {
    const keys: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith(this.prefix)) {
        keys.push(key.replace(this.prefix, ''));
      }
    }
    return keys;
  }
}

// Global storage manager instance
export const storage = new StorageManager();
