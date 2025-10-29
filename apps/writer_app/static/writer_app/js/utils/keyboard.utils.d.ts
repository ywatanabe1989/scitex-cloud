/**
 * Keyboard event utilities
 */
export interface KeyboardShortcut {
    key: string;
    ctrl?: boolean;
    shift?: boolean;
    alt?: boolean;
    meta?: boolean;
    callback: (event: KeyboardEvent) => void;
}
/**
 * Check if keyboard event matches a shortcut
 */
export declare function matchesShortcut(event: KeyboardEvent, key: string, options?: {
    ctrl?: boolean;
    shift?: boolean;
    alt?: boolean;
    meta?: boolean;
}): boolean;
/**
 * Register keyboard shortcut
 */
export declare function registerShortcut(shortcut: KeyboardShortcut): () => void;
/**
 * Get human-readable shortcut string
 */
export declare function formatShortcut(shortcut: KeyboardShortcut): string;
/**
 * Check if event is from input element
 */
export declare function isInputElement(element: Element): boolean;
//# sourceMappingURL=keyboard.utils.d.ts.map