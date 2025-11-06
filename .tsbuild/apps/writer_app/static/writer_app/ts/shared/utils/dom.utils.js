/**
 * DOM manipulation and query utilities
 */
/**
 * Safely query element from DOM
 */
console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/shared/utils/dom.utils.ts loaded");
export function querySelector(selector) {
    try {
        return document.querySelector(selector);
    }
    catch (error) {
        console.error(`Failed to query selector: ${selector}`, error);
        return null;
    }
}
/**
 * Safely query all elements matching selector
 */
export function querySelectorAll(selector) {
    try {
        return Array.from(document.querySelectorAll(selector));
    }
    catch (error) {
        console.error(`Failed to query selector: ${selector}`, error);
        return [];
    }
}
/**
 * Set element's visibility
 */
export function setVisibility(element, visible) {
    if (!element)
        return;
    element.style.display = visible ? '' : 'none';
}
/**
 * Toggle class on element
 */
export function toggleClass(element, className, force) {
    if (!element)
        return;
    if (force === undefined) {
        element.classList.toggle(className);
    }
    else {
        element.classList.toggle(className, force);
    }
}
/**
 * Add class to element
 */
export function addClass(element, className) {
    if (!element)
        return;
    element.classList.add(className);
}
/**
 * Remove class from element
 */
export function removeClass(element, className) {
    if (!element)
        return;
    element.classList.remove(className);
}
/**
 * Check if element has class
 */
export function hasClass(element, className) {
    if (!element)
        return false;
    return element.classList.contains(className);
}
/**
 * Get computed style value
 */
export function getComputedStyle(element) {
    return window.getComputedStyle(element);
}
/**
 * Set multiple attributes on element
 */
export function setAttributes(element, attributes) {
    if (!element)
        return;
    Object.entries(attributes).forEach(([key, value]) => {
        element.setAttribute(key, value);
    });
}
/**
 * Remove element from DOM
 */
export function removeElement(element) {
    if (element?.parentNode) {
        element.parentNode.removeChild(element);
    }
}
/**
 * Clear element's content
 */
export function clearElement(element) {
    if (!element)
        return;
    element.innerHTML = '';
}
/**
 * Create element with options
 */
export function createElement(tag, options) {
    const element = document.createElement(tag);
    if (options?.className) {
        if (Array.isArray(options.className)) {
            element.classList.add(...options.className);
        }
        else {
            element.className = options.className;
        }
    }
    if (options?.id) {
        element.id = options.id;
    }
    if (options?.attributes) {
        setAttributes(element, options.attributes);
    }
    if (options?.textContent) {
        element.textContent = options.textContent;
    }
    if (options?.innerHTML) {
        element.innerHTML = options.innerHTML;
    }
    return element;
}
/**
 * Scroll element into view smoothly
 */
export function scrollIntoView(element, behavior = 'smooth') {
    if (element) {
        element.scrollIntoView({ behavior, block: 'nearest' });
    }
}
/**
 * Get scroll position
 */
export function getScrollPosition() {
    return {
        x: window.scrollX || document.documentElement.scrollLeft,
        y: window.scrollY || document.documentElement.scrollTop,
    };
}
/**
 * Set scroll position
 */
export function setScrollPosition(x, y) {
    window.scrollTo(x, y);
}
//# sourceMappingURL=dom.utils.js.map