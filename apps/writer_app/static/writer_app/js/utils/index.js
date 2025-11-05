/**
 * Writer-specific utility modules
 * These utilities are shared across writer components
 */
// DOM utilities
console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/utils/index.ts loaded");
export { querySelector, querySelectorAll, setVisibility, toggleClass, addClass, removeClass, hasClass, getComputedStyle, setAttributes, removeElement, clearElement, createElement, scrollIntoView, getScrollPosition, setScrollPosition, } from './dom.utils.js';
// Keyboard utilities
export { matchesShortcut, registerShortcut, formatShortcut, isInputElement, } from './keyboard.utils.js';
// LaTeX utilities
export { convertToLatex, convertFromLatex, extractTextFromLatex, isLatexContent, validateLatexSyntax, } from './latex.utils.js';
// Timer and timing utilities
export { debounce, throttle, formatElapsedTime, SimpleTimer, wait, createTimeout, } from './timer.utils.js';
//# sourceMappingURL=index.js.map