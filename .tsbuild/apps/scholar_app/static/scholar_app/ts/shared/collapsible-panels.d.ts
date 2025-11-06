/**

 * Collapsible Panels Module
 *
 * Generic module for handling collapsible panel UI interactions:
 * - Click to expand/collapse panels
 * - Icon rotation animation
 * - Dynamic height calculation with MutationObserver
 * - Smooth transitions
 *
 * @module shared/collapsible-panels
 */
/**
 * Recalculate height of collapsible content
 * Useful when content changes dynamically
 *
 * @param {HTMLElement} content - The collapsible content element
 */
declare function recalculateHeight(content: HTMLElement): void;
/**
 * Expand a collapsible panel
 *
 * @param {HTMLElement} header - The header element
 * @param {HTMLElement} content - The content element to expand
 * @param {HTMLElement} icon - The icon element to rotate
 */
declare function expandPanel(header: HTMLElement, content: HTMLElement, icon: HTMLElement): void;
/**
 * Collapse a collapsible panel
 *
 * @param {HTMLElement} header - The header element
 * @param {HTMLElement} content - The content element to collapse
 * @param {HTMLElement} icon - The icon element to rotate
 */
declare function collapsePanel(header: HTMLElement, content: HTMLElement, icon: HTMLElement): void;
/**
 * Toggle a collapsible panel between expanded and collapsed states
 *
 * @param {HTMLElement} header - The header element
 * @param {HTMLElement} content - The content element
 * @param {HTMLElement} icon - The icon element
 */
declare function togglePanel(header: HTMLElement, content: HTMLElement, icon: HTMLElement): void;
/**
 * Initialize a single collapsible panel
 *
 * @param {HTMLElement} header - The collapsible header element
 */
declare function initializePanel(header: HTMLElement): void;
/**
 * Initialize all collapsible panels on the page
 * Should be called after DOM is loaded
 *
 * @param {string} headerSelector - CSS selector for collapsible headers (default: '.collapsible-header')
 */
declare function initializeCollapsiblePanels(headerSelector?: string): void;
/**
 * Expand all collapsible panels
 *
 * @param {string} headerSelector - CSS selector for collapsible headers (default: '.collapsible-header')
 */
declare function expandAllPanels(headerSelector?: string): void;
/**
 * Collapse all collapsible panels
 *
 * @param {string} headerSelector - CSS selector for collapsible headers (default: '.collapsible-header')
 */
declare function collapseAllPanels(headerSelector?: string): void;
export { initializeCollapsiblePanels, initializePanel, togglePanel, expandPanel, collapsePanel, expandAllPanels, collapseAllPanels, recalculateHeight, };
//# sourceMappingURL=collapsible-panels.d.ts.map