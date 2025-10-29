/**
 * WriterAPI - REST API client for scitex.writer.Writer
 * 
 * Provides a clean interface for the new /api/project/<id>/ endpoints.
 * All manuscript operations delegate to scitex.writer.Writer.
 */

class WriterAPI {
    constructor(projectId, csrfToken) {
        this.projectId = projectId;
        this.csrfToken = csrfToken;
        this.baseUrl = `/writer/api/project/${projectId}`;
    }

    /**
     * Read a section from the manuscript
     * @param {string} sectionName - Section name (e.g., 'abstract', 'introduction')
     * @param {string} docType - Document type: 'manuscript', 'supplementary', or 'revision'
     * @returns {Promise<string>} Section content
     */
    async readSection(sectionName, docType = 'manuscript') {
        const url = `${this.baseUrl}/section/${sectionName}/?doc_type=${docType}`;
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to read section: ${response.status}`);
        }

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Failed to read section');
        }

        return data.content;
    }

    /**
     * Write content to a section
     * @param {string} sectionName - Section name
     * @param {string} content - Section content
     * @param {string} docType - Document type (default: 'manuscript')
     * @param {string} commitMessage - Optional commit message (if provided, auto-commits)
     * @returns {Promise<object>} Response with success status
     */
    async writeSection(sectionName, content, docType = 'manuscript', commitMessage = null) {
        const url = `${this.baseUrl}/section/${sectionName}/`;
        const body = {
            content: content,
            doc_type: docType
        };

        if (commitMessage) {
            body.commit_message = commitMessage;
        }

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken
            },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            throw new Error(`Failed to write section: ${response.status}`);
        }

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Failed to write section');
        }

        return data;
    }

    /**
     * Get git history for a section
     * @param {string} sectionName - Section name
     * @param {string} docType - Document type (default: 'manuscript')
     * @returns {Promise<array>} Array of commit messages
     */
    async getSectionHistory(sectionName, docType = 'manuscript') {
        const url = `${this.baseUrl}/section/${sectionName}/history/?doc_type=${docType}`;
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to get history: ${response.status}`);
        }

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Failed to get history');
        }

        return data.history || [];
    }

    /**
     * Get git diff for a section
     * @param {string} sectionName - Section name
     * @param {string} ref - Git reference to compare against (default: 'HEAD')
     * @param {string} docType - Document type (default: 'manuscript')
     * @returns {Promise<object>} Diff data with has_changes flag
     */
    async getSectionDiff(sectionName, ref = 'HEAD', docType = 'manuscript') {
        const url = `${this.baseUrl}/section/${sectionName}/diff/?ref=${ref}&doc_type=${docType}`;
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to get diff: ${response.status}`);
        }

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Failed to get diff');
        }

        return data;
    }

    /**
     * Restore a section from git history
     * @param {string} sectionName - Section name
     * @param {string} ref - Git reference (commit, branch, tag)
     * @param {string} docType - Document type (default: 'manuscript')
     * @returns {Promise<object>} Response with success status
     */
    async checkoutSection(sectionName, ref = 'HEAD', docType = 'manuscript') {
        const url = `${this.baseUrl}/section/${sectionName}/checkout/`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken
            },
            body: JSON.stringify({
                ref: ref,
                doc_type: docType
            })
        });

        if (!response.ok) {
            throw new Error(`Failed to checkout section: ${response.status}`);
        }

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Failed to checkout section');
        }

        return data;
    }

    /**
     * Compile a document
     * @param {string} docType - Document type: 'manuscript', 'supplementary', or 'revision'
     * @param {number} timeout - Compilation timeout in seconds (default: 300)
     * @returns {Promise<object>} Compilation result with success, output_pdf, log, error
     */
    async compile(docType = 'manuscript', timeout = 300) {
        const url = `${this.baseUrl}/compile/`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken
            },
            body: JSON.stringify({
                doc_type: docType,
                timeout: timeout
            })
        });

        if (!response.ok) {
            throw new Error(`Compilation failed: ${response.status}`);
        }

        const data = await response.json();
        return data;
    }

    /**
     * Get path to compiled PDF
     * @param {string} docType - Document type (default: 'manuscript')
     * @returns {Promise<string|null>} Path to PDF or null if not compiled
     */
    async getPDF(docType = 'manuscript') {
        const url = `${this.baseUrl}/pdf/?doc_type=${docType}`;
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to get PDF: ${response.status}`);
        }

        const data = await response.json();
        if (!data.success) {
            return null;
        }

        return data.pdf_path;
    }

    /**
     * Get list of available sections for each document type
     * @returns {Promise<object>} Object with sections for manuscript, supplementary, revision
     */
    async getAvailableSections() {
        const url = `${this.baseUrl}/sections/`;
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to get sections: ${response.status}`);
        }

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Failed to get sections');
        }

        return data.sections;
    }
}

// Export for use in other scripts
window.WriterAPI = WriterAPI;
