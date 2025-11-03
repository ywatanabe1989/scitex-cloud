/**
 * Writer PDF Management Module
 * Handles PDF rendering, loading, and zoom controls
 */
import { getWriterConfig } from './helpers.js';

/**
 * Render PDF - Central function for PDF display logic
 * Determines whether to show compiled PDF or trigger preview compilation
 *
 * @param {string} sectionId - Section ID (e.g., 'manuscript/compiled_pdf')
 * @param {object} pdfPreviewManager - PDF preview manager instance (unused for compiled_pdf)
 */
export function render_pdf(sectionId, pdfPreviewManager) {
    // For compiled_pdf sections: show full manuscript PDF (NO preview compilation)
    if (sectionId.endsWith('/compiled_pdf')) {
        console.log('[Writer] render_pdf: Showing compiled PDF (no preview compilation)');
        loadCompiledPDF(sectionId);
        return;
    }

    // For other sections: preview will be managed by auto-compile on content change
    console.log('[Writer] render_pdf: Editable section, preview managed by auto-compile');
}

/**
 * Load compiled PDF for display (not quick preview)
 */
export function loadCompiledPDF(sectionId) {
    const config = getWriterConfig();
    if (!config.projectId)
        return;

    // Extract doc type from sectionId (e.g., "manuscript/compiled_pdf" -> "manuscript")
    const parts = sectionId.split('/');
    const docType = parts[0];

    // Use API endpoint for PDF (avoids X-Frame-Options issues)
    const pdfUrl = `/writer/api/project/${config.projectId}/pdf/?doc_type=${docType}`;
    console.log('[Writer] Loading compiled PDF for section:', sectionId, 'URL:', pdfUrl);

    // Display the PDF directly (bypass quick preview compilation)
    const textPreview = document.getElementById('text-preview');
    if (textPreview) {
        textPreview.innerHTML = `
            <div class="pdf-preview-container">
                <div class="pdf-preview-viewer" id="pdf-viewer-pane">
                    <iframe
                        src="${pdfUrl}#toolbar=0&navpanes=0&scrollbar=1&view=FitW"
                        type="application/pdf"
                        width="100%"
                        height="100%"
                        title="Compiled PDF"
                        frameborder="0">
                    </iframe>
                </div>
            </div>
        `;
    }
}

/**
 * Update the PDF preview panel title to show current section with link
 */
export function updatePDFPreviewTitle(sectionId) {
    const titleElement = document.getElementById('preview-title');
    if (!titleElement)
        return;

    const config = getWriterConfig();

    // Extract section name from sectionId
    const parts = sectionId.split('/');
    const docType = parts[0];
    const sectionName = parts[parts.length - 1];

    // Capitalize and format
    const docTypeLabel = docType.charAt(0).toUpperCase() + docType.slice(1);
    const formattedName = sectionName
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');

    // Build PDF file link
    let pdfLink = '';
    if (sectionName === 'compiled_pdf' && config.username && config.projectSlug) {
        // Link to compiled PDF
        const docDirMap = {
            'manuscript': '01_manuscript',
            'supplementary': '02_supplementary',
            'revision': '03_revision'
        };
        pdfLink = `/${config.username}/${config.projectSlug}/blob/scitex/writer/${docDirMap[docType]}/${docType}.pdf`;
    }
    else if (config.username && config.projectSlug) {
        // Link to preview PDF
        pdfLink = `/${config.username}/${config.projectSlug}/blob/scitex/writer/preview_output/preview-${sectionName}.pdf`;
    }

    // Special case for compiled_pdf - don't add "PDF" twice
    let titleText = '';
    if (sectionName === 'compiled_pdf') {
        titleText = `${docTypeLabel} PDF`;
    }
    else {
        titleText = `${docTypeLabel} ${formattedName} PDF`;
    }

    // Add link if available
    if (pdfLink) {
        titleElement.innerHTML = `${titleText} <a href="${pdfLink}" target="_blank" style="font-size: 0.8em; opacity: 0.7;">📁</a>`;
    }
    else {
        titleElement.textContent = titleText;
    }
}

/**
 * Open PDF in new window
 */
export function openPDF(url) {
    const pdfWindow = window.open(url, '_blank');
    if (!pdfWindow) {
        const showToast = window.showToast || ((msg) => console.warn(msg));
        showToast('Failed to open PDF. Please check popup blocker settings.');
    }
}

/**
 * Setup PDF zoom control buttons
 */
export function setupPDFZoomControls(pdfScrollZoomHandler) {
    const zoomInBtn = document.getElementById('pdf-zoom-in-btn');
    const zoomOutBtn = document.getElementById('pdf-zoom-out-btn');
    const fitWidthBtn = document.getElementById('pdf-fit-width-btn');
    const resetZoomBtn = document.getElementById('pdf-reset-zoom-btn');
    const colorModeBtn = document.getElementById('pdf-color-mode-btn');
    const zoomControls = document.querySelector('.pdf-zoom-controls');

    if (zoomInBtn) {
        zoomInBtn.addEventListener('click', () => {
            pdfScrollZoomHandler.zoomIn();
        });
    }

    if (zoomOutBtn) {
        zoomOutBtn.addEventListener('click', () => {
            pdfScrollZoomHandler.zoomOut();
        });
    }

    if (fitWidthBtn) {
        fitWidthBtn.addEventListener('click', () => {
            pdfScrollZoomHandler.fitToWidth();
        });
    }

    if (resetZoomBtn) {
        resetZoomBtn.addEventListener('click', () => {
            pdfScrollZoomHandler.resetZoom();
        });
    }

    if (colorModeBtn) {
        colorModeBtn.addEventListener('click', () => {
            pdfScrollZoomHandler.toggleColorMode();
        });
    }

    // Show/hide zoom controls based on PDF presence
    const observer = new MutationObserver(() => {
        const hasPDF = document.querySelector('.pdf-preview-container') !== null;
        if (zoomControls) {
            zoomControls.style.display = hasPDF ? 'flex' : 'none';
        }
    });

    const previewPanel = document.querySelector('.preview-panel');
    if (previewPanel) {
        observer.observe(previewPanel, { childList: true, subtree: true });
    }

    console.log('[Writer] PDF zoom controls initialized');
}
