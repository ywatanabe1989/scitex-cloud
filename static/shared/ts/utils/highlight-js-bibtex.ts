/**
 * BibTeX Language Definition for Highlight.js
 *
 * Registers a custom BibTeX language definition with Highlight.js
 * for proper syntax highlighting of .bib files.
 *
 * This script can be included in any page that uses highlight.js
 * and needs BibTeX syntax highlighting support.
 *
 * Usage:
 *   <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
 *   <script src="/static/js/utils/highlight-js-bibtex.js"></script>
 */

// Note: hljs types are declared in global.d.ts

console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/static/ts/utils/highlight-js-bibtex.ts loaded");
interface HljsApi {
    COMMENT: (begin: string, end: string) => CommentRule;
    QUOTE_STRING_MODE: QuoteStringMode;
    C_NUMBER_MODE: NumberMode;
}

interface CommentRule {
    scope?: string;
    begin: string;
    end: string;
}

interface QuoteStringMode {
    scope?: string;
    begin?: string;
    end?: string;
}

interface NumberMode {
    scope?: string;
    variants?: any[];
}

interface LanguageRule {
    className?: string;
    scope?: string;
    begin: string | RegExp;
    end?: string | RegExp;
    returnBegin?: boolean;
    contains?: LanguageRule[];
    relevance?: number;
}

interface LanguageDefinition {
    name: string;
    aliases?: string[];
    case_insensitive?: boolean;
    contains: (CommentRule | LanguageRule | QuoteStringMode | NumberMode)[];
}

(function registerBibTeXLanguage(): void {
    'use strict';

    // Wait for hljs to be available
    if (typeof window.hljs === 'undefined') {
        console.warn('[BibTeX] hljs not available yet, retrying...');
        setTimeout(registerBibTeXLanguage, 100);
        return;
    }

    try {
        window.hljs.registerLanguage('bibtex', function(hljs: HljsApi): LanguageDefinition {
            return {
                name: 'BibTeX',
                aliases: ['bib'],
                case_insensitive: true,
                contains: [
                    // Comments: % to end of line
                    hljs.COMMENT('%', '$'),

                    // Entry types: @article, @book, @inproceedings, etc.
                    {
                        className: 'meta',
                        begin: '@[a-zA-Z]+',
                        relevance: 10
                    },

                    // Field names: author=, title=, year=, etc.
                    {
                        className: 'attr',
                        begin: '[a-zA-Z_]+\\s*=',
                        returnBegin: true,
                        contains: [
                            {
                                className: 'attr',
                                begin: '[a-zA-Z_]+'
                            }
                        ]
                    },

                    // Quoted strings: "value" or {value}
                    hljs.QUOTE_STRING_MODE,

                    // Numbers
                    hljs.C_NUMBER_MODE
                ]
            };
        });

        console.log('[BibTeX] ✓ Language successfully registered with Highlight.js');
    } catch (err) {
        console.error('[BibTeX] ✗ Failed to register language:', err);
    }
})();

// Export empty object to make this a valid module
export {};
