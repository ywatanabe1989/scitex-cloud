/**
 * Code Block Copy Button Handler
 * Adds copy-to-clipboard functionality to all code blocks
 * Also applies syntax highlighting and line numbers
 *
 * Note: Suppresses highlight.js warnings about unescaped HTML in code blocks.
 * These are false positives that occur when markdown table syntax is displayed
 * as examples in documentation. The HTML is properly escaped by the markdown renderer.
 */
interface CodeBlockConfig {
    showLineNumbers: boolean;
    enableCopyButton: boolean;
}
declare class CodeBlockManager {
    private config;
    private originalWarn;
    private warningKeywords;
    constructor(config?: Partial<CodeBlockConfig>);
    /**
     * Install global filter to suppress false positive warnings from highlight.js
     * This is installed immediately to catch warnings from all sources
     */
    private installGlobalWarningFilter;
    /**
     * Suppress highlight.js warnings during callback execution
     */
    private suppressHighlightWarnings;
    /**
     * Initialize code block handling
     */
    init(): void;
    /**
     * Process all code blocks on the page
     */
    private processCodeBlocks;
    /**
     * Process a single code block
     */
    private processCodeBlock;
    /**
     * Add copy button to code block
     */
    private addCopyButton;
    /**
     * Copy code to clipboard
     */
    private copyToClipboard;
    /**
     * Setup Ctrl+A handler to select only code content
     */
    private setupSelectAllHandler;
}
//# sourceMappingURL=code-blocks.d.ts.map