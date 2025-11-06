/**
 * Index main page functionality
 * Corresponds to: templates/writer_app/index/main.html
 */
interface Manuscript {
    id: number;
    title: string;
    project: string;
    word_count: number;
    updated_at: string;
}
declare class IndexPage {
    private btnNewManuscript;
    constructor();
    private init;
    private setupEventListeners;
    private createNewManuscript;
}
//# sourceMappingURL=main.d.ts.map