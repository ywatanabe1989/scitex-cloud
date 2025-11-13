/**
 * Global Type Declarations for root static TypeScript
 * Declares types for third-party libraries and global variables
 */

// Highlight.js
interface HLJSApi {
  highlightElement(element: HTMLElement): void;
  lineNumbersBlock?(element: HTMLElement): void;
  configure(options: any): void;
  highlightAll(): void;
  registerLanguage(name: string, definition: (hljs: any) => any): void;
  COMMENT(begin: string, end: string): any;
  QUOTE_STRING_MODE: any;
  C_NUMBER_MODE: any;
}

// Extend Window interface
declare global {
  interface Window {
    hljs: HLJSApi;
  }
}

export {};
