/**
 * Editor Loader Module
 * Handles sequential loading of CodeMirror and Monaco Editor
 * Prevents AMD/RequireJS conflicts between the two editors
 *
 * @version 1.0.0 (TypeScript)
 * @author SciTeX Development Team
 */
interface FakeWorker {
    postMessage: () => void;
    terminate: () => void;
    addEventListener: () => void;
    removeEventListener: () => void;
}
interface MonacoEnvironment {
    getWorker: (moduleId: string, label: string) => Promise<FakeWorker>;
}
declare global {
    interface Window {
        define: any;
        require: any;
        MonacoEnvironment: MonacoEnvironment;
        monaco: any;
        monacoLoaded: boolean;
        CodeMirror: any;
    }
}
export declare class EditorLoader {
    private readonly CODEMIRROR_VERSION;
    private readonly MONACO_VERSION;
    private originalDefine;
    private originalRequire;
    /**
     * Initialize and load both CodeMirror and Monaco editors
     */
    initialize(): Promise<void>;
    /**
     * Load CodeMirror scripts without AMD conflicts
     */
    private loadCodeMirror;
    /**
     * Load Monaco Editor with fake worker to avoid CORS issues
     */
    private loadMonaco;
    /**
     * Create a fake Worker that runs in the main thread
     * Used to prevent CORS issues with Monaco's web workers
     */
    private createFakeWorker;
    /**
     * Load a single script asynchronously
     */
    private loadScript;
    /**
     * Load multiple scripts in sequential order
     */
    private loadScriptsSequentially;
}
/**
 * Auto-initialize editors when this module is loaded
 * Can be imported and used directly in templates
 */
export declare function initializeEditors(): Promise<void>;
export declare const editorLoader: EditorLoader;
export {};
//# sourceMappingURL=editor-loader.d.ts.map