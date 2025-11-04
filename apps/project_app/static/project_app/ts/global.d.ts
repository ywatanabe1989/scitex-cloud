/**
 * Global Type Declarations for project_app
 * Declares types for third-party libraries and global variables
 */

// Highlight.js
interface HLJSApi {
    highlightElement(element: HTMLElement): void;
    lineNumbersBlock?(element: HTMLElement): void;
    configure(options: any): void;
    highlightAll(): void;
}

// Marked (Markdown parser)
interface MarkedStatic {
    parse(markdown: string, options?: any): string;
    setOptions(options: any): void;
}

// Icon utilities
interface IconOptions {
    size?: number;
    classes?: string;
    color?: string;
    title?: string;
}

interface IconUtilsInterface {
    loadIcon(iconName: string, options?: IconOptions): Promise<string>;
    createIcon(iconName: string, options?: IconOptions): Promise<HTMLElement | null>;
    getInlineIcon(iconName: string, options?: IconOptions): string;
    emojiToIcon(emoji: string): string;
    ICON_BASE_PATH: string;
}

// PDF.js
interface PDFJSLib {
    GlobalWorkerOptions: {
        workerSrc: string;
    };
    getDocument(params: any): any;
}

// Global variables
interface Window {
    hljs: HLJSApi;
    marked: MarkedStatic;
    IconUtils: IconUtilsInterface;
    pdfjsLib: PDFJSLib;
    SCITEX_PROJECT_DATA: {
        owner: string;
        repo: string;
        slug?: string;
        path: string;
        branch: string;
        [key: string]: any;
    };
    SCITEX_FILE_PATH?: string;
    SCITEX_PROFILE_DATA?: {
        [key: string]: any;
    };
    // Functions exposed by file_view.ts
    copyToClipboard: () => void;
    showCode: () => void;
    showPreview: () => void;
    toggleBranchDropdown: (event: Event) => void;
    switchBranch: (branch: string) => Promise<void>;
    // Functions exposed by file_edit.ts
    showEdit?: () => void;
}
