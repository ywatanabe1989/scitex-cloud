/**
 * Writer-specific utility modules
 * These utilities are shared across writer components
 */

// DOM utilities
export {
  querySelector,
  querySelectorAll,
  setVisibility,
  toggleClass,
  addClass,
  removeClass,
  hasClass,
  getComputedStyle,
  setAttributes,
  removeElement,
  clearElement,
  createElement,
  scrollIntoView,
  getScrollPosition,
  setScrollPosition,
} from './dom.utils';

// Keyboard utilities
export {
  matchesShortcut,
  registerShortcut,
  formatShortcut,
  isInputElement,
  type KeyboardShortcut,
} from './keyboard.utils';

// LaTeX utilities
export {
  convertToLatex,
  convertFromLatex,
  extractTextFromLatex,
  isLatexContent,
  validateLatexSyntax,
} from './latex.utils';

// Timer and timing utilities
export {
  debounce,
  throttle,
  formatElapsedTime,
  SimpleTimer,
  wait,
  createTimeout,
} from './timer.utils';
