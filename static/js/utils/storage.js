/**
 * LocalStorage Utility Module
 * Handles persistence of application state across sessions
 */
console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/static/ts/utils/storage.ts loaded");
export class StorageManager {
    prefix;
    constructor(prefix = 'scitex_') {
        this.prefix = prefix;
    }
    /**
     * Generate storage key with prefix
     */
    getKey(key) {
        return `${this.prefix}${key}`;
    }
    /**
     * Save data to localStorage (alias for setItem)
     */
    save(key, data) {
        this.setItem(key, data);
    }
    /**
     * Load data from localStorage (alias for getItem)
     */
    load(key, defaultValue) {
        return this.getItem(key, defaultValue);
    }
    /**
     * Get item from localStorage with type safety
     */
    getItem(key, defaultValue) {
        try {
            const fullKey = this.getKey(key);
            const data = localStorage.getItem(fullKey);
            return data ? JSON.parse(data) : (defaultValue || null);
        }
        catch (error) {
            console.error(`[Storage] Failed to load ${key}:`, error);
            return defaultValue || null;
        }
    }
    /**
     * Set item in localStorage with type safety
     */
    setItem(key, value) {
        try {
            const fullKey = this.getKey(key);
            localStorage.setItem(fullKey, JSON.stringify(value));
            console.log(`[Storage] Saved: ${key}`);
            return true;
        }
        catch (error) {
            console.error(`[Storage] Failed to save ${key}:`, error);
            return false;
        }
    }
    /**
     * Check if key exists in localStorage
     */
    exists(key) {
        return localStorage.getItem(this.getKey(key)) !== null;
    }
    /**
     * Check if key exists in localStorage (alias)
     */
    hasItem(key) {
        return this.exists(key);
    }
    /**
     * Remove item from localStorage
     */
    remove(key) {
        try {
            localStorage.removeItem(this.getKey(key));
            console.log(`[Storage] Removed: ${key}`);
        }
        catch (error) {
            console.error(`[Storage] Failed to remove ${key}:`, error);
        }
    }
    /**
     * Remove item from localStorage (alias)
     */
    removeItem(key) {
        try {
            this.remove(key);
            return true;
        }
        catch (error) {
            return false;
        }
    }
    /**
     * Clear all items with this prefix
     */
    clear() {
        try {
            const keys = Object.keys(localStorage);
            keys.forEach(key => {
                if (key.startsWith(this.prefix)) {
                    localStorage.removeItem(key);
                }
            });
            console.log(`[Storage] Cleared all items with prefix: ${this.prefix}`);
        }
        catch (error) {
            console.error('[Storage] Failed to clear storage:', error);
        }
    }
    /**
     * Get all keys stored with this prefix
     */
    getAllKeys() {
        const keys = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key?.startsWith(this.prefix)) {
                keys.push(key.replace(this.prefix, ''));
            }
        }
        return keys;
    }
}
// Export singleton instances for global use
export const globalStorage = new StorageManager('scitex_');
export const writerStorage = new StorageManager('writer_app_');
//# sourceMappingURL=storage.js.map