/**
 * Writer Storage Module
 * Handles saving sections to server and auto-save scheduling
 */
import { getCsrfToken } from '@/utils/csrf.js';
import { getWriterConfig } from './helpers.js';

/**
 * Show toast notification (utility)
 */
function showToast(message, _type = 'info') {
    const fn = window.showToast || ((msg) => console.log(msg));
    fn(message);
}

// Shared timeout for auto-save
let saveTimeout;

/**
 * Schedule auto-save
 */
export function scheduleSave(_editor, sectionsManager, state) {
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(() => {
        saveSections(sectionsManager, state);
    }, 5000); // Auto-save after 5 seconds of inactivity
}

/**
 * Save sections to server
 */
export async function saveSections(sectionsManager, state) {
    try {
        // Get project ID from page config
        const config = getWriterConfig();
        if (!config.projectId) {
            console.warn('[Writer] Cannot save sections: no project ID');
            return;
        }

        const allSections = sectionsManager.getAll();

        // Filter out empty sections to avoid unnecessary writes
        const sections = {};
        for (const [name, contentValue] of Object.entries(allSections)) {
            const content = String(contentValue || '');
            if (content.trim().length > 0) {
                sections[name] = content;
            }
        }

        if (Object.keys(sections).length === 0) {
            console.log('[Writer] No non-empty sections to save');
            return;
        }

        console.log(`[Writer] Saving ${Object.keys(sections).length} sections for ${state.currentDocType || 'manuscript'}`);

        const response = await fetch(`/writer/api/project/${config.projectId}/save-sections/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                sections,
                doc_type: state.currentDocType || 'manuscript'
            })
        });

        const data = await response.json();

        if (data.success) {
            state.unsavedSections.clear();
            console.log(`[Writer] Sections saved: ${data.sections_saved} saved, ${data.sections_skipped || 0} skipped`);
            showToast('Sections saved', 'success');
        }
        else {
            const errorMsg = data.error || 'Unknown error';
            console.error('[Writer] Save failed:', errorMsg);
            if (data.traceback) {
                console.error('[Writer] Server traceback:', data.traceback);
            }
            showToast(`Failed to save sections: ${errorMsg}`, 'error');
        }
    }
    catch (error) {
        console.error('[Writer] Error saving sections:', error);
        showToast('Error saving sections', 'error');
    }
}
