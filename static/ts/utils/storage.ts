/**
 * LocalStorage Utility Module
 * Handles persistence of application state across sessions
 */

export class StorageManager {
    private prefix: string;

    constructor(prefix: string = 'scitex_') {
        this.prefix = prefix;
    }

    /**
     * Generate storage key with prefix
     */
    private getKey(key: string): string {
        return `${this.prefix}${key}`;
    }

    /**
     * Save data to localStorage
     */
    save<T>(key: string, data: T): void {
        try {
            const fullKey = this.getKey(key);
            localStorage.setItem(fullKey, JSON.stringify(data));
            console.log(`[Storage] Saved: ${key}`);
        } catch (error) {
            console.error(`[Storage] Failed to save ${key}:`, error);
        }
    }

    /**
     * Load data from localStorage
     */
    load<T>(key: string, defaultValue?: T): T | null {
        try {
            const fullKey = this.getKey(key);
            const data = localStorage.getItem(fullKey);
            return data ? JSON.parse(data) : (defaultValue || null);
        } catch (error) {
            console.error(`[Storage] Failed to load ${key}:`, error);
            return defaultValue || null;
        }
    }

    /**
     * Check if key exists in localStorage
     */
    exists(key: string): boolean {
        return localStorage.getItem(this.getKey(key)) !== null;
    }

    /**
     * Remove item from localStorage
     */
    remove(key: string): void {
        try {
            localStorage.removeItem(this.getKey(key));
            console.log(`[Storage] Removed: ${key}`);
        } catch (error) {
            console.error(`[Storage] Failed to remove ${key}:`, error);
        }
    }

    /**
     * Clear all items with this prefix
     */
    clear(): void {
        try {
            const keys = Object.keys(localStorage);
            keys.forEach(key => {
                if (key.startsWith(this.prefix)) {
                    localStorage.removeItem(key);
                }
            });
            console.log(`[Storage] Cleared all items with prefix: ${this.prefix}`);
        } catch (error) {
            console.error('[Storage] Failed to clear storage:', error);
        }
    }
}

// Export singleton instance for global use
export const globalStorage = new StorageManager('scitex_');
