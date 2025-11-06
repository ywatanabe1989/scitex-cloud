"use strict";
/**
 * Browse Toolbar Handler
 * Manages file browser toolbar interactions: dropdowns, copy, download, branch switching
 * @module repository/browse_toolbar
 */
console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/project_app/static/project_app/ts/repository/browse_toolbar.ts loaded");
class BrowseToolbar {
    projectData = null;
    constructor() {
        this.init();
    }
    init() {
        document.addEventListener('DOMContentLoaded', () => {
            console.log('[Browse Toolbar] Initializing');
            this.loadProjectData();
            this.setupClickableRows();
            this.setupDropdowns();
            this.setupDropdownHoverEffects();
        });
    }
    loadProjectData() {
        // Project data should be set by template
        const ownerEl = document.querySelector('[data-project-owner]');
        const slugEl = document.querySelector('[data-project-slug]');
        const pathEl = document.querySelector('[data-breadcrumb-path]');
        if (ownerEl && slugEl) {
            this.projectData = {
                owner: ownerEl.getAttribute('data-project-owner') || '',
                slug: slugEl.getAttribute('data-project-slug') || '',
                breadcrumbPath: pathEl?.getAttribute('data-breadcrumb-path') || ''
            };
            console.log('[Browse Toolbar] Project data loaded:', this.projectData);
        }
        else {
            console.warn('[Browse Toolbar] Project data not found in DOM');
        }
    }
    setupClickableRows() {
        const clickableRows = document.querySelectorAll('.clickable-row');
        console.log('[Browse Toolbar] Found', clickableRows.length, 'clickable rows');
        clickableRows.forEach(row => {
            row.addEventListener('click', (e) => {
                const target = e.target;
                // Don't navigate if clicking on a link directly
                if (target.tagName === 'A' || target.closest('a')) {
                    return;
                }
                const href = row.getAttribute('data-href');
                if (href) {
                    window.location.href = href;
                }
            });
        });
    }
    setupDropdowns() {
        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            const target = e.target;
            if (!target.closest('.file-browser-toolbar .btn-group')) {
                this.closeAllDropdowns();
            }
        });
        // Expose toggle functions to window for onclick handlers
        window.toggleBranchDropdown = () => this.toggleDropdown('branch-dropdown');
        window.toggleAddFileDropdown = () => this.toggleDropdown('add-file-dropdown');
        window.toggleCopyDropdown = () => this.toggleDropdown('copy-dropdown');
        window.toggleCodeDropdown = () => this.toggleDropdown('code-dropdown');
        window.toggleMoreDropdown = () => this.toggleDropdown('more-dropdown');
        // Expose action functions
        window.switchBranch = (branch) => this.switchBranch(branch);
        window.copyProjectToClipboard = () => this.copyProjectToClipboard();
        window.downloadProjectAsFile = () => this.downloadProjectAsFile();
        window.copyDirToClipboard = () => this.copyDirToClipboard();
        window.downloadDirAsFile = () => this.downloadDirAsFile();
        console.log('[Browse Toolbar] Dropdown functions exposed to window');
    }
    toggleDropdown(dropdownId) {
        const dropdown = document.getElementById(dropdownId);
        if (!dropdown) {
            return;
        }
        const isVisible = dropdown.style.display === 'block';
        this.closeAllDropdowns();
        dropdown.style.display = isVisible ? 'none' : 'block';
    }
    closeAllDropdowns() {
        const dropdowns = document.querySelectorAll('.file-browser-toolbar .dropdown-menu');
        dropdowns.forEach(dropdown => {
            dropdown.style.display = 'none';
        });
    }
    setupDropdownHoverEffects() {
        const dropdownItems = document.querySelectorAll('.file-browser-toolbar .dropdown-item');
        dropdownItems.forEach(item => {
            item.addEventListener('mouseenter', () => {
                item.style.background = 'var(--color-canvas-subtle)';
            });
            item.addEventListener('mouseleave', () => {
                item.style.background = 'transparent';
            });
        });
    }
    async switchBranch(branch) {
        if (!this.projectData) {
            console.error('[Browse Toolbar] Project data not available');
            return;
        }
        console.log('[Browse Toolbar] Switching to branch:', branch);
        try {
            const response = await fetch(`/${this.projectData.owner}/${this.projectData.slug}/api/switch-branch/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({ branch })
            });
            const data = await response.json();
            if (data.success) {
                window.location.reload();
            }
            else {
                alert('Failed to switch branch: ' + data.error);
            }
        }
        catch (error) {
            console.error('[Browse Toolbar] Error switching branch:', error);
            alert('Failed to switch branch: ' + error.message);
        }
    }
    async copyProjectToClipboard() {
        await this.copyToClipboardGeneric('copy-project-btn');
    }
    async copyDirToClipboard() {
        await this.copyToClipboardGeneric('copy-dir-btn');
    }
    async copyToClipboardGeneric(btnId) {
        if (!this.projectData) {
            console.error('[Browse Toolbar] Project data not available');
            return;
        }
        const btn = document.getElementById(btnId);
        if (!btn) {
            return;
        }
        const originalText = btn.innerHTML;
        btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" style="vertical-align: text-bottom; margin-right: 4px;"><path fill="#6c8ba0" d="M2.75 0a.75.75 0 0 0 0 1.5h.75v1.25a4.75 4.75 0 0 0 1.9 3.8l.333.25c.134.1.134.3 0 .4l-.333.25a4.75 4.75 0 0 0-1.9 3.8v1.25h-.75a.75.75 0 0 0 0 1.5h10.5a.75.75 0 0 0 0-1.5h-.75v-1.25a4.75 4.75 0 0 0-1.9-3.8l-.333-.25a.25.25 0 0 1 0-.4l.333-.25a4.75 4.75 0 0 0 1.9-3.8V1.5h.75a.75.75 0 0 0 0-1.5H2.75Zm7.25 9v3.25h-4V9a3.25 3.25 0 0 1 1.3-2.6l.333-.25a1.75 1.75 0 0 0 0-2.8l-.333-.25A3.25 3.25 0 0 1 6 1.5V0h4v1.5a3.25 3.25 0 0 1-1.3 2.6l-.333.25a1.75 1.75 0 0 0 0 2.8l.333.25A3.25 3.25 0 0 1 10 9.75Z"/></svg> Loading...';
        btn.disabled = true;
        try {
            console.log('[Browse Toolbar] Fetching concatenated content...');
            const response = await fetch(`/${this.projectData.owner}/${this.projectData.slug}/api/concatenate/${this.projectData.breadcrumbPath}`);
            const data = await response.json();
            console.log('[Browse Toolbar] API response:', data);
            if (data.success) {
                await navigator.clipboard.writeText(data.content);
                btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" style="vertical-align: text-bottom; margin-right: 4px;"><path fill="#6c8ba0" fill-rule="evenodd" d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"/></svg> Copied ${data.file_count} files!`;
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                }, 3000);
            }
            else {
                alert('Error: ' + data.error);
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        }
        catch (err) {
            alert('Failed to copy: ' + err);
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    }
    async downloadProjectAsFile() {
        await this.downloadAsFileGeneric('download-project-btn');
    }
    async downloadDirAsFile() {
        await this.downloadAsFileGeneric('download-dir-btn');
    }
    async downloadAsFileGeneric(btnId) {
        if (!this.projectData) {
            console.error('[Browse Toolbar] Project data not available');
            return;
        }
        const btn = document.getElementById(btnId);
        if (!btn) {
            return;
        }
        const originalText = btn.innerHTML;
        btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" style="vertical-align: text-bottom; margin-right: 4px;"><path fill="#6c8ba0" d="M2.75 0a.75.75 0 0 0 0 1.5h.75v1.25a4.75 4.75 0 0 0 1.9 3.8l.333.25c.134.1.134.3 0 .4l-.333.25a4.75 4.75 0 0 0-1.9 3.8v1.25h-.75a.75.75 0 0 0 0 1.5h10.5a.75.75 0 0 0 0-1.5h-.75v-1.25a4.75 4.75 0 0 0-1.9-3.8l-.333-.25a.25.25 0 0 1 0-.4l.333-.25a4.75 4.75 0 0 0 1.9-3.8V1.5h.75a.75.75 0 0 0 0-1.5H2.75Zm7.25 9v3.25h-4V9a3.25 3.25 0 0 1 1.3-2.6l.333-.25a1.75 1.75 0 0 0 0-2.8l-.333-.25A3.25 3.25 0 0 1 6 1.5V0h4v1.5a3.25 3.25 0 0 1-1.3 2.6l-.333.25a1.75 1.75 0 0 0 0 2.8l.333.25A3.25 3.25 0 0 1 10 9.75Z"/></svg> Preparing download...';
        try {
            const response = await fetch(`/${this.projectData.owner}/${this.projectData.slug}/api/concatenate/${this.projectData.breadcrumbPath}`);
            const data = await response.json();
            if (data.success) {
                const blob = new Blob([data.content], { type: 'text/plain' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                // Generate filename
                const dirName = this.projectData.breadcrumbPath.split('/').filter(x => x).pop() || this.projectData.slug;
                a.download = `${dirName}_all_files.txt`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" style="vertical-align: text-bottom; margin-right: 4px;"><path fill="#6c8ba0" fill-rule="evenodd" d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"/></svg> Downloaded ${data.file_count} files!`;
                setTimeout(() => {
                    btn.innerHTML = originalText;
                }, 3000);
            }
            else {
                alert('Error: ' + data.error);
                btn.innerHTML = originalText;
            }
        }
        catch (err) {
            alert('Failed to download: ' + err);
            btn.innerHTML = originalText;
        }
    }
    getCookie(name) {
        let cookieValue = '';
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}
// Initialize on page load
new BrowseToolbar();
//# sourceMappingURL=browse_toolbar.js.map