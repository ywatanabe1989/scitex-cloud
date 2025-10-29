/**
 * LocalStorage Utility Module
 * Handles persistence of application state across sessions
 */
export declare class StorageManager {
    private prefix;
    constructor(prefix?: string);
    /**
     * Generate storage key with prefix
     */
    private getKey;
    /**
     * Save data to localStorage (alias for setItem)
     */
    save<T>(key: string, data: T): void;
    /**
     * Load data from localStorage (alias for getItem)
     */
    load<T>(key: string, defaultValue?: T): T | null;
    /**
     * Get item from localStorage with type safety
     */
    getItem<T>(key: string, defaultValue?: T): T | null;
    /**
     * Set item in localStorage with type safety
     */
    setItem<T>(key: string, value: T): boolean;
    /**
     * Check if key exists in localStorage
     */
    exists(key: string): boolean;
    /**
     * Check if key exists in localStorage (alias)
     */
    hasItem(key: string): boolean;
    /**
     * Remove item from localStorage
     */
    remove(key: string): void;
    /**
     * Remove item from localStorage (alias)
     */
    removeItem(key: string): boolean;
    /**
     * Clear all items with this prefix
     */
    clear(): void;
    /**
     * Get all keys stored with this prefix
     */
    getAllKeys(): string[];
}
export declare const globalStorage: StorageManager;
export declare const writerStorage: StorageManager;
//# sourceMappingURL=storage.d.ts.map