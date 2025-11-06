/**
 * LaTeX conversion and processing utilities
 */
export declare function convertToLatex(content: string): string;
/**
 * Convert LaTeX content to plain text preview
 */
export declare function convertFromLatex(latexContent: string): string;
/**
 * Extract text content from LaTeX for word counting
 */
export declare function extractTextFromLatex(latex: string): string;
/**
 * Check if content appears to be LaTeX
 */
export declare function isLatexContent(content: string): boolean;
/**
 * Validate LaTeX syntax (basic check)
 */
export declare function validateLatexSyntax(latex: string): {
    valid: boolean;
    errors: string[];
};
//# sourceMappingURL=latex.utils.d.ts.map