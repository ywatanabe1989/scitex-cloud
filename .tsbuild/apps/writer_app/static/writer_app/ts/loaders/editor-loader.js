/**
 * Editor Loader Module
 * Handles sequential loading of CodeMirror and Monaco Editor
 * Prevents AMD/RequireJS conflicts between the two editors
 *
 * @version 1.0.0 (TypeScript)
 * @author SciTeX Development Team
 */
// ============================================================================
// Type Definitions
// ============================================================================
console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/loaders/editor-loader.ts loaded");
// ============================================================================
// Editor Loader Class
// ============================================================================
export class EditorLoader {
    CODEMIRROR_VERSION = '5.65.16';
    MONACO_VERSION = '0.45.0';
    originalDefine = null;
    originalRequire = null;
    /**
     * Initialize and load both CodeMirror and Monaco editors
     */
    async initialize() {
        console.log('[EditorLoader] Starting editor initialization');
        try {
            await this.loadCodeMirror();
            await this.loadMonaco();
            console.log('[EditorLoader] All editors loaded successfully');
        }
        catch (error) {
            console.error('[EditorLoader] Failed to load editors:', error);
            throw error;
        }
    }
    /**
     * Load CodeMirror scripts without AMD conflicts
     */
    async loadCodeMirror() {
        console.log('[EditorLoader] Loading CodeMirror...');
        // CodeMirror scripts to load in order
        const scripts = [
            `https://cdnjs.cloudflare.com/ajax/libs/codemirror/${this.CODEMIRROR_VERSION}/codemirror.min.js`,
            `https://cdnjs.cloudflare.com/ajax/libs/codemirror/${this.CODEMIRROR_VERSION}/mode/stex/stex.min.js`,
            `https://cdnjs.cloudflare.com/ajax/libs/codemirror/${this.CODEMIRROR_VERSION}/addon/dialog/dialog.min.js`,
            `https://cdnjs.cloudflare.com/ajax/libs/codemirror/${this.CODEMIRROR_VERSION}/addon/search/searchcursor.min.js`,
            `https://cdnjs.cloudflare.com/ajax/libs/codemirror/${this.CODEMIRROR_VERSION}/addon/search/search.min.js`,
            `https://cdnjs.cloudflare.com/ajax/libs/codemirror/${this.CODEMIRROR_VERSION}/keymap/vim.min.js`,
            `https://cdnjs.cloudflare.com/ajax/libs/codemirror/${this.CODEMIRROR_VERSION}/keymap/emacs.min.js`
        ];
        // Save original AMD globals
        this.originalDefine = window.define;
        this.originalRequire = window.require;
        // Temporarily disable AMD to prevent conflicts
        // CodeMirror UMD modules detect AMD and try to register, causing conflicts with Monaco's RequireJS
        window.define = undefined;
        window.require = undefined;
        try {
            // Load all CodeMirror scripts sequentially
            await this.loadScriptsSequentially(scripts);
            console.log('[EditorLoader] CodeMirror loaded successfully');
        }
        finally {
            // Always restore AMD globals, even if loading fails
            window.define = this.originalDefine;
            window.require = this.originalRequire;
        }
    }
    /**
     * Load Monaco Editor with fake worker to avoid CORS issues
     */
    async loadMonaco() {
        console.log('[EditorLoader] Loading Monaco Editor...');
        // Configure Monaco environment with main-thread worker fallback
        // This prevents CORS issues when loading from CDN
        window.MonacoEnvironment = {
            getWorker: (_moduleId, _label) => {
                return Promise.resolve(this.createFakeWorker());
            }
        };
        // Load Monaco loader script
        const loaderUrl = `https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/${this.MONACO_VERSION}/min/vs/loader.min.js`;
        await this.loadScript(loaderUrl);
        // Configure and load Monaco
        return new Promise((resolve, reject) => {
            // Wait for RequireJS to be available
            const checkRequire = () => {
                if (typeof window.require !== 'undefined' && window.require.config) {
                    // Configure RequireJS paths for Monaco
                    const requireConfig = {
                        paths: { 'vs': `https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/${this.MONACO_VERSION}/min/vs` },
                        'vs/nls': { availableLanguages: {} }
                    };
                    window.require.config(requireConfig);
                    // Load Monaco editor main module
                    window.require(['vs/editor/editor.main'], () => {
                        console.log('[EditorLoader] Monaco Editor loaded successfully');
                        window.monacoLoaded = true;
                        window.monaco = window.monaco;
                        resolve();
                    }, (error) => {
                        console.error('[EditorLoader] Failed to load Monaco:', error);
                        reject(error);
                    });
                }
                else {
                    // Retry after a short delay
                    setTimeout(checkRequire, 50);
                }
            };
            checkRequire();
        });
    }
    /**
     * Create a fake Worker that runs in the main thread
     * Used to prevent CORS issues with Monaco's web workers
     */
    createFakeWorker() {
        return {
            postMessage: () => { },
            terminate: () => { },
            addEventListener: () => { },
            removeEventListener: () => { }
        };
    }
    /**
     * Load a single script asynchronously
     */
    loadScript(url) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = url;
            script.onload = () => {
                console.log('[EditorLoader] Loaded:', url);
                resolve();
            };
            script.onerror = () => {
                const error = new Error(`Failed to load script: ${url}`);
                console.error('[EditorLoader]', error);
                reject(error);
            };
            document.head.appendChild(script);
        });
    }
    /**
     * Load multiple scripts in sequential order
     */
    async loadScriptsSequentially(urls) {
        for (const url of urls) {
            try {
                await this.loadScript(url);
            }
            catch (error) {
                console.warn('[EditorLoader] Failed to load script, continuing:', url, error);
                // Continue loading other scripts even if one fails
            }
        }
    }
}
// ============================================================================
// Auto-initialization
// ============================================================================
/**
 * Auto-initialize editors when this module is loaded
 * Can be imported and used directly in templates
 */
export async function initializeEditors() {
    const loader = new EditorLoader();
    await loader.initialize();
}
// Export singleton instance for direct use
export const editorLoader = new EditorLoader();
//# sourceMappingURL=editor-loader.js.map