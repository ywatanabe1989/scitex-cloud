/**
 * LaTeX Wrapper Module
 * Wraps section content with proper LaTeX document structure
 */
export interface LatexWrapperOptions {
    documentClass?: string;
    packages?: string[];
    preamble?: string;
    title?: string;
    author?: string;
    includeTableOfContents?: boolean;
}
export declare class LatexWrapper {
    private documentClass;
    private packages;
    private preamble;
    private title;
    private author;
    private includeTableOfContents;
    constructor(options?: LatexWrapperOptions);
    /**
     * Get default LaTeX packages
     */
    private getDefaultPackages;
    /**
     * Get LaTeX preamble
     */
    getPreamble(): string;
    /**
     * Get LaTeX document begin
     */
    getDocumentBegin(): string;
    /**
     * Wrap section content with LaTeX structure
     */
    wrapSection(sectionName: string, content: string, level?: number): string;
    /**
     * Wrap multiple sections
     */
    wrapSections(sections: {
        name: string;
        content: string;
    }[]): string;
    /**
     * Get LaTeX document end
     */
    getDocumentEnd(): string;
    /**
     * Create complete LaTeX document
     */
    createDocument(sections: {
        name: string;
        content: string;
    }[]): string;
    /**
     * Escape LaTeX special characters
     */
    private escapeLatexSpecial;
    /**
     * Create minimal LaTeX document for preview
     */
    createMinimalDocument(content: string): string;
    /**
     * Set document title
     */
    setTitle(title: string): void;
    /**
     * Set document author
     */
    setAuthor(author: string): void;
    /**
     * Add package to preamble
     */
    addPackage(packageName: string): void;
    /**
     * Remove package from preamble
     */
    removePackage(packageName: string): void;
}
//# sourceMappingURL=latex-wrapper.d.ts.map