/**
 * Writer Compilation Module
 * Handles LaTeX compilation, auto-compile scheduling, and compilation listeners
 */
import { clearCompileTimeout, setCompileTimeout } from './writer-shared.js';

/**
 * Show toast notification (utility)
 */
function showToast(message, _type = 'info') {
    const fn = window.showToast || ((msg) => console.log(msg));
    fn(message);
}

/**
 * Schedule auto-compile for live PDF preview
 */
export function scheduleAutoCompile(pdfPreviewManager, content, sectionId) {
    if (!pdfPreviewManager)
        return;

    // Clear existing timeout
    clearCompileTimeout();

    // Schedule compilation after user stops typing
    const timeout = setTimeout(() => {
        console.log('[Writer] Auto-compiling for live preview, section:', sectionId);
        // Pass section ID for section-specific preview
        pdfPreviewManager.compileQuick(content, sectionId);
    }, 2000); // Wait 2 seconds after user stops typing

    // Store timeout so it can be cancelled
    setCompileTimeout(timeout);
}

/**
 * Handle full manuscript compilation (no content sent - uses workspace)
 */
export async function handleCompileFull(compilationManager, state) {
    if (compilationManager.getIsCompiling()) {
        showToast('Compilation already in progress', 'warning');
        return;
    }

    try {
        const projectId = state.projectId;
        if (!projectId) {
            showToast('No project ID found', 'error');
            return;
        }

        showToast('Compiling full manuscript from workspace...', 'info');
        console.log('[Writer] Starting full compilation for project:', projectId);

        const result = await compilationManager.compileFull({
            projectId: projectId,
            docType: 'manuscript'
        });

        if (result && result.status === 'completed') {
            showToast('Manuscript compiled successfully', 'success');
        }
        else {
            showToast('Compilation failed', 'error');
        }
    }
    catch (error) {
        showToast('Compilation error: ' + (error instanceof Error ? error.message : 'Unknown error'), 'error');
    }
}

/**
 * @deprecated Use handleCompileFull instead for compile button
 * Handle preview compilation (sends content - for auto-preview)
 */
export async function handleCompile(_editor, sectionsManager, _compilationManager, _state, pdfPreviewManager) {
    if (!pdfPreviewManager) {
        showToast('PDF preview not initialized', 'error');
        return;
    }

    if (pdfPreviewManager.isCompiling()) {
        showToast('Compilation already in progress', 'warning');
        return;
    }

    try {
        const sections = sectionsManager.getAll();
        const sectionArray = Object.entries(sections).map(([name, content]) => ({
            name: name.charAt(0).toUpperCase() + name.slice(1),
            content: content
        }));

        showToast('Starting preview compilation...', 'info');
        await pdfPreviewManager.compile(sectionArray);
    }
    catch (error) {
        showToast('Compilation error: ' + (error instanceof Error ? error.message : 'Unknown error'), 'error');
    }
}

/**
 * Setup compilation listeners
 */
export function setupCompilationListeners(compilationManager, _config) {
    compilationManager.onProgress((progress, status) => {
        const progressBar = document.getElementById('compilation-progress');
        if (progressBar) {
            progressBar.value = String(progress);
        }

        const statusText = document.getElementById('compilation-status');
        if (statusText) {
            statusText.textContent = status;
        }
    });

    compilationManager.onComplete((_jobId, pdfUrl) => {
        const showToast = window.showToast || ((msg) => console.log(msg));
        showToast('Compilation completed successfully');

        if (pdfUrl) {
            // Dynamic import to avoid circular dependency
            import('./writer-pdf.js').then(module => {
                module.openPDF(pdfUrl);
            });
        }
    });

    compilationManager.onError((error) => {
        const showToast = window.showToast || ((msg) => console.error(msg));
        showToast('Compilation error: ' + error);
    });
}
