/**
 * LaTeX Wrapper Module
 * Wraps section content with proper LaTeX document structure
 */
<<<<<<<< HEAD:.tsbuild/apps/writer_app/static/writer_app/ts/editor/modules/latex-wrapper.js
console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/editor/modules/latex-wrapper.ts loaded");
export class LatexWrapper {
    documentClass;
    packages;
    preamble;
    title;
    author;
    includeTableOfContents;
    constructor(options) {
========

console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/editor/modules/latex-wrapper.ts loaded");
export interface LatexWrapperOptions {
    documentClass?: string;
    packages?: string[];
    preamble?: string;
    title?: string;
    author?: string;
    includeTableOfContents?: boolean;
}

export class LatexWrapper {
    private documentClass: string;
    private packages: string[];
    private preamble: string;
    private title: string;
    private author: string;
    private includeTableOfContents: boolean;

    constructor(options?: LatexWrapperOptions) {
>>>>>>>> feat/writer-visitor-access-and-optimizations:apps/writer_app/static/writer_app/ts/editor/modules/latex-wrapper.ts
        this.documentClass = options?.documentClass || 'article';
        this.packages = options?.packages || this.getDefaultPackages();
        this.preamble = options?.preamble || '';
        this.title = options?.title || 'Untitled Manuscript';
        this.author = options?.author || '';
        this.includeTableOfContents = options?.includeTableOfContents ?? true;
    }

    /**
     * Get default LaTeX packages
     */
    private getDefaultPackages(): string[] {
        return [
            'geometry{margin=1in}',
            'graphicx',
            'amsmath',
            'amssymb',
            'hyperref',
            'setspace',
            'natbib'
        ];
    }

    /**
     * Get LaTeX preamble
     */
    getPreamble(): string {
        let preamble = `\\documentclass{${this.documentClass}}\n\n`;

        // Add packages
        this.packages.forEach(pkg => {
            if (pkg.includes('{')) {
                preamble += `\\usepackage[${pkg}]\n`;
            } else {
                preamble += `\\usepackage{${pkg}}\n`;
            }
        });

        preamble += '\n';

        // Add title and author
        preamble += `\\title{${this.escapeLatexSpecial(this.title)}}\n`;
        if (this.author) {
            preamble += `\\author{${this.escapeLatexSpecial(this.author)}}\n`;
        }

        preamble += '\\date{\\today}\n\n';

        // Add custom preamble
        if (this.preamble) {
            preamble += this.preamble + '\n\n';
        }

        return preamble;
    }

    /**
     * Get LaTeX document begin
     */
    getDocumentBegin(): string {
        let doc = '\\begin{document}\n\n';
        doc += '\\maketitle\n';

        if (this.includeTableOfContents) {
            doc += '\\tableofcontents\n\\newpage\n\n';
        }

        return doc;
    }

    /**
     * Wrap section content with LaTeX structure
     */
    wrapSection(
        sectionName: string,
        content: string,
        level: number = 1
    ): string {
        const sectionCommands = ['section', 'subsection', 'subsubsection'];
        const command = sectionCommands[Math.min(level, 2)];

        let wrapped = `\\${command}{${this.escapeLatexSpecial(sectionName)}}\n\n`;
        wrapped += content + '\n\n';

        return wrapped;
    }

    /**
     * Wrap multiple sections
     */
    wrapSections(sections: { name: string; content: string }[]): string {
        let content = '';
        sections.forEach(section => {
            content += this.wrapSection(section.name, section.content, 1);
        });
        return content;
    }

    /**
     * Get LaTeX document end
     */
    getDocumentEnd(): string {
        return '\n\\end{document}\n';
    }

    /**
     * Create complete LaTeX document
     */
    createDocument(sections: { name: string; content: string }[]): string {
        let doc = this.getPreamble();
        doc += this.getDocumentBegin();
        doc += this.wrapSections(sections);
        doc += this.getDocumentEnd();
        return doc;
    }

    /**
     * Escape LaTeX special characters
     */
    private escapeLatexSpecial(text: string): string {
        return text
            .replace(/\\/g, '\\textbackslash{}')
            .replace(/[&%$#_{}]/g, '\\$&')
            .replace(/\^/g, '\\textasciicircum{}')
            .replace(/~/g, '\\textasciitilde{}');
    }

    /**
     * Create minimal LaTeX document for preview
     */
    createMinimalDocument(content: string, fontSize: number = 11): string {
        // Map editor font size (10-20px) to LaTeX font size (10pt-14pt)
        // 10px -> 10pt, 14px -> 11pt (default), 20px -> 14pt
        const latexFontSize = Math.max(10, Math.min(14, Math.round(10 + (fontSize - 10) / 2.5)));
        const fontSizeOption = `${latexFontSize}pt`;

        let doc = `\\documentclass[${fontSizeOption}]{article}\n`;
        doc += `\\usepackage{geometry}\n`;
        doc += `\\usepackage[utf8]{inputenc}\n`;
        doc += `\\geometry{margin=1in}\n`;
        doc += `\\usepackage{hyperref}\n\n`;
        doc += `\\begin{document}\n\n`;
        doc += content;
        doc += `\n\n\\end{document}\n`;
        return doc;
    }

    /**
     * Set document title
     */
    setTitle(title: string): void {
        this.title = title;
    }

    /**
     * Set document author
     */
    setAuthor(author: string): void {
        this.author = author;
    }

    /**
     * Add package to preamble
     */
    addPackage(packageName: string): void {
        if (!this.packages.includes(packageName)) {
            this.packages.push(packageName);
        }
    }

    /**
     * Remove package from preamble
     */
    removePackage(packageName: string): void {
        const index = this.packages.indexOf(packageName);
        if (index > -1) {
            this.packages.splice(index, 1);
        }
    }
}
