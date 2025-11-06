/**
 * DOM manipulation and query utilities
 */
export declare function querySelector<T extends Element = Element>(selector: string): T | null;
/**
 * Safely query all elements matching selector
 */
export declare function querySelectorAll<T extends Element = Element>(selector: string): T[];
/**
 * Set element's visibility
 */
export declare function setVisibility(element: HTMLElement | null, visible: boolean): void;
/**
 * Toggle class on element
 */
export declare function toggleClass(element: HTMLElement | null, className: string, force?: boolean): void;
/**
 * Add class to element
 */
export declare function addClass(element: HTMLElement | null, className: string): void;
/**
 * Remove class from element
 */
export declare function removeClass(element: HTMLElement | null, className: string): void;
/**
 * Check if element has class
 */
export declare function hasClass(element: HTMLElement | null, className: string): boolean;
/**
 * Get computed style value
 */
export declare function getComputedStyle(element: HTMLElement): CSSStyleDeclaration;
/**
 * Set multiple attributes on element
 */
export declare function setAttributes(element: HTMLElement | null, attributes: Record<string, string>): void;
/**
 * Remove element from DOM
 */
export declare function removeElement(element: HTMLElement | null): void;
/**
 * Clear element's content
 */
export declare function clearElement(element: HTMLElement | null): void;
/**
 * Create element with options
 */
export declare function createElement(tag: string, options?: {
    className?: string | string[];
    id?: string;
    attributes?: Record<string, string>;
    textContent?: string;
    innerHTML?: string;
}): HTMLElement;
/**
 * Scroll element into view smoothly
 */
export declare function scrollIntoView(element: HTMLElement | null, behavior?: 'smooth' | 'auto'): void;
/**
 * Get scroll position
 */
export declare function getScrollPosition(): {
    x: number;
    y: number;
};
/**
 * Set scroll position
 */
export declare function setScrollPosition(x: number, y: number): void;
//# sourceMappingURL=dom.utils.d.ts.map