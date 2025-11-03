/**
 * Writer Sections Management Module
 * Handles section switching, loading, and UI updates
 */
import { getWriterConfig } from './helpers.js';
import { render_pdf, updatePDFPreviewTitle } from './writer-pdf.js';

// Shared timeout for auto-compile (needs to be accessible across modules)
let compileTimeout;

/**
 * Get the compile timeout for clearing
 */
export function getCompileTimeout() {
    return compileTimeout;
}

/**
 * Set the compile timeout
 */
export function setCompileTimeout(timeout) {
    compileTimeout = timeout;
}

/**
 * Clear the compile timeout
 */
export function clearCompileTimeout() {
    clearTimeout(compileTimeout);
}

/**
 * Load section content from API
 */
export async function loadSectionContent(editor, sectionsManager, _state, sectionId) {
    const config = getWriterConfig();
    if (!config.projectId) {
        console.warn('[Writer] Cannot load section content: no project ID');
        return;
    }

    try {
        // Extract section name and doc type from sectionId (e.g., "manuscript/abstract" -> doc_type="manuscript", section_name="abstract")
        const parts = sectionId.split('/');
        if (parts.length !== 2) {
            console.warn('[Writer] Invalid section ID format:', sectionId);
            return;
        }

        const docType = parts[0];
        const sectionName = parts[1];

        console.log('[Writer] Loading section content:', sectionId, 'docType:', docType, 'sectionName:', sectionName);

        const response = await fetch(`/writer/api/project/${config.projectId}/section/${sectionName}/?doc_type=${docType}`);
        if (!response.ok) {
            const error = await response.text();
            console.error('[Writer] Failed to load section:', response.status, error);
            return;
        }

        const data = await response.json();
        console.log('[Writer] API Response for', sectionId, ':', data);

        if (data.success && data.content !== undefined) {
            console.log('[Writer] ✓ Content loaded for:', sectionId, 'length:', data.content.length);
            console.log('[Writer] First 100 chars:', data.content.substring(0, 100));
            sectionsManager.setContent(sectionId, data.content);
            editor.setContent(data.content);
        }
        else {
            const errorMsg = data.error || 'Unknown error loading section';
            console.error('[Writer] ✗ API Error:', errorMsg);
            throw new Error(errorMsg);
        }
    }
    catch (error) {
        console.error('[Writer] Error loading section content:', error);
        throw error; // Re-throw to let caller handle it
    }
}

/**
 * Switch to a section
 */
export async function switchSection(editor, sectionsManager, state, sectionId, pdfPreviewManager) {
    // FIRST: Cancel any pending auto-compile from previous section
    clearTimeout(compileTimeout);

    // Save current section
    const currentContent = editor.getContent();
    sectionsManager.setContent(state.currentSection, currentContent);

    // Update current section
    state.currentSection = sectionId;
    console.log('[Writer] Switching to section:', sectionId);

    updateSectionUI(sectionId);
    syncDropdownToSection(sectionId);

    // Render appropriate PDF (compiled or preview)
    render_pdf(sectionId, pdfPreviewManager);

    // For compiled_pdf sections, load the compiled TeX in editor (read-only)
    if (sectionId.endsWith('/compiled_pdf')) {
        console.log('[Writer] Compiled PDF section - loading compiled TeX');
        // Set editor to read-only
        if (typeof editor.setReadOnly === 'function') {
            editor.setReadOnly(true);
        }

        // Load compiled_tex content
        const compiledTexId = sectionId.replace('/compiled_pdf', '/compiled_tex');
        try {
            await loadSectionContent(editor, sectionsManager, state, compiledTexId);
        }
        catch (error) {
            const errorMsg = `Failed to load compiled TeX: ${error}`;
            console.error('[Writer]', errorMsg);
            editor.setContent(`% ERROR: ${errorMsg}\n% Please check browser console for details`);
        }
        return;
    }

    // For regular editable sections
    if (typeof editor.setReadOnly === 'function') {
        editor.setReadOnly(false);
    }

    // Load fresh content from API
    try {
        await loadSectionContent(editor, sectionsManager, state, sectionId);
    }
    catch (error) {
        const errorMsg = `Failed to load section ${sectionId}: ${error}`;
        console.error('[Writer]', errorMsg);
        editor.setContent(`% ERROR: ${errorMsg}\n% Please check browser console for details`);
    }
}

/**
 * Update section UI
 */
export function updateSectionUI(sectionId) {
    document.querySelectorAll('.section-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.section === sectionId);
    });

    // Update the section title label in the editor header
    updateSectionTitleLabel(sectionId);

    // Update PDF preview title as well
    updatePDFPreviewTitle(sectionId);

    // Show/hide commit button based on section type (hide for read-only sections)
    updateCommitButtonVisibility(sectionId);
}

/**
 * Sync dropdown selection with current section
 */
export function syncDropdownToSection(sectionId) {
    const dropdown = document.getElementById('texfile-selector');
    if (dropdown) {
        dropdown.value = sectionId;
    }
}

/**
 * Update the section title label to show current section name with file link
 */
export function updateSectionTitleLabel(sectionId) {
    const titleElement = document.getElementById('editor-section-title');
    if (!titleElement)
        return;

    const config = getWriterConfig();

    // Extract section info from sectionId (e.g., "manuscript/abstract")
    const parts = sectionId.split('/');
    const docType = parts[0];
    const sectionName = parts[parts.length - 1];

    // Capitalize and format the section name
    const formattedName = sectionName
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');

    // Build file path for link
    const docDirMap = {
        'manuscript': '01_manuscript',
        'supplementary': '02_supplementary',
        'revision': '03_revision',
        'shared': 'shared'
    };

    let filePath = '';
    if (sectionName === 'compiled_pdf' || sectionName === 'compiled_tex') {
        // For compiled_pdf, link to the TEX file (since that's what shows in editor)
        // Compiled files are in the root of doc directory
        filePath = `scitex/writer/${docDirMap[docType]}/${docType}.tex`;
    }
    else {
        // Regular sections are in contents/
        const ext = sectionName === 'bibliography' || sectionName === 'references' ? 'bib' : 'tex';
        if (docType === 'shared') {
            filePath = `scitex/writer/shared/${sectionName}.${ext}`;
        }
        else {
            filePath = `scitex/writer/${docDirMap[docType]}/contents/${sectionName}.${ext}`;
        }
    }

    // Create link to project browser
    const fileLink = config.username && config.projectSlug
        ? `/${config.username}/${config.projectSlug}/blob/${filePath}`
        : '';

    if (fileLink) {
        titleElement.innerHTML = `${formattedName} Source <a href="${fileLink}" target="_blank" style="font-size: 0.8em; opacity: 0.7;">📁</a>`;
    }
    else {
        titleElement.textContent = `${formattedName} Source`;
    }
}

/**
 * Update commit button state based on section type and user authentication
 * - Hides button for guest users (Visitor Mode)
 * - Disables button for read-only sections (keeps it visible to reduce surprise)
 */
export function updateCommitButtonVisibility(sectionId) {
    const commitBtn = document.getElementById('git-commit-btn');
    if (!commitBtn)
        return;

    const config = window.WRITER_CONFIG;

    // Hide for guest users (projectId === 0 means demo/guest project)
    if (!config || config.projectId === 0) {
        commitBtn.style.display = 'none';
        return;
    }

    // Always show button for authenticated users
    commitBtn.style.display = '';

    // Extract section name from sectionId (e.g., "manuscript/compiled_pdf" -> "compiled_pdf")
    const parts = sectionId.split('/');
    const sectionName = parts[parts.length - 1];

    // Disable button for read-only sections (but keep it visible)
    // compiled_pdf is the merged/compiled document
    // figures, tables, references are directories or view-only sections
    const readOnlySections = ['compiled_pdf', 'figures', 'tables', 'references'];
    const isReadOnly = readOnlySections.includes(sectionName);

    if (isReadOnly) {
        commitBtn.disabled = true;
        commitBtn.title = 'Cannot commit read-only sections';
    }
    else {
        commitBtn.disabled = false;
        commitBtn.title = 'Create git commit for current changes';
    }
}

/**
 * Handle document type switch
 */
export function handleDocTypeSwitch(editor, sectionsManager, state, newDocType, pdfPreviewManager) {
    // Map of first section for each document type
    const firstSectionByDocType = {
        'manuscript': 'abstract',
        'supplementary': 'content',
        'revision': 'response',
        'shared': '' // No sections for shared type
    };

    const firstSection = firstSectionByDocType[newDocType] || 'abstract';

    if (!firstSection) {
        console.warn('[Writer] No sections available for document type:', newDocType);
        console.log('[Writer] Keeping current section:', state.currentSection);
        // Don't switch sections if document type has no sections
        return;
    }

    // Switch to the first section of the new document type
    console.log('[Writer] Switching to', firstSection, 'for', newDocType);
    switchSection(editor, sectionsManager, state, firstSection, pdfPreviewManager);
}
