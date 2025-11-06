/**
 * Compilation view page functionality
 * Corresponds to: templates/writer_app/compilation/compilation_view.html
 */
interface CompilationLog {
    timestamp: string;
    level: string;
    message: string;
}
declare class CompilationViewPage {
    private logViewer;
    private progressBar;
    private _pdfViewer;
    constructor();
    private init;
    private setupLogViewer;
    private setupProgressMonitoring;
    updateProgress(percentage: number): void;
    addLogEntry(log: CompilationLog): void;
}
//# sourceMappingURL=compilation_view.d.ts.map