"use strict";
/**
 * Collaborator Autocomplete Handler
 * Provides user search and autocomplete for adding collaborators
 * @module projects/settings_collaborators
 */
console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/project_app/static/project_app/ts/projects/settings_collaborators.ts loaded");
class CollaboratorAutocomplete {
    elements = null;
    searchTimeout = null;
    SEARCH_DELAY_MS = 300;
    MIN_QUERY_LENGTH = 2;
    constructor() {
        this.init();
    }
    init() {
        document.addEventListener('DOMContentLoaded', () => {
            console.log('[Collaborator Autocomplete] Initializing');
            this.setupElements();
            this.attachListeners();
        });
    }
    setupElements() {
        const input = document.getElementById('collaboratorUsername');
        const dropdown = document.getElementById('collaborator-autocomplete');
        if (!input || !dropdown) {
            console.warn('[Collaborator Autocomplete] Required elements not found');
            return;
        }
        this.elements = { input, dropdown };
        console.log('[Collaborator Autocomplete] Elements found');
    }
    attachListeners() {
        if (!this.elements) {
            return;
        }
        const { input, dropdown } = this.elements;
        // Input event for search
        input.addEventListener('input', () => this.handleInput());
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            const target = e.target;
            if (!input.contains(target) && !dropdown.contains(target)) {
                this.hideDropdown();
            }
        });
        console.log('[Collaborator Autocomplete] Listeners attached');
    }
    handleInput() {
        if (!this.elements) {
            return;
        }
        // Clear previous timeout
        if (this.searchTimeout !== null) {
            window.clearTimeout(this.searchTimeout);
        }
        const query = this.elements.input.value.trim();
        if (query.length < this.MIN_QUERY_LENGTH) {
            this.hideDropdown();
            return;
        }
        // Debounce search
        this.searchTimeout = window.setTimeout(() => {
            this.performSearch(query);
        }, this.SEARCH_DELAY_MS);
    }
    async performSearch(query) {
        if (!this.elements) {
            return;
        }
        try {
            console.log('[Collaborator Autocomplete] Searching for:', query);
            const response = await fetch(`/api/users/search/?q=${encodeURIComponent(query)}`);
            console.log('[Collaborator Autocomplete] Response status:', response.status, response.ok);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            console.log('[Collaborator Autocomplete] Data received:', data);
            this.renderResults(data.users || []);
        }
        catch (error) {
            console.error('[Collaborator Autocomplete] Search error:', error);
            this.hideDropdown();
        }
    }
    renderResults(users) {
        if (!this.elements) {
            return;
        }
        const { dropdown } = this.elements;
        if (users.length === 0) {
            dropdown.innerHTML = '<div style="padding: 12px; color: var(--color-fg-muted); text-align: center; font-size: 12px;">No users found</div>';
            this.showDropdown();
            return;
        }
        dropdown.innerHTML = users.map(user => this.createUserItem(user)).join('');
        // Attach click handlers to items
        const items = dropdown.querySelectorAll('.autocomplete-item');
        items.forEach(item => {
            item.addEventListener('click', () => this.selectUser(item));
            item.addEventListener('mouseenter', () => this.highlightItem(item, true));
            item.addEventListener('mouseleave', () => this.highlightItem(item, false));
        });
        this.showDropdown();
    }
    createUserItem(user) {
        const initial = user.username.charAt(0).toUpperCase();
        const emailHtml = user.email
            ? `<div style="font-size: 11px; color: var(--color-fg-muted);">${this.escapeHtml(user.email)}</div>`
            : '';
        return `
            <div class="autocomplete-item" data-username="${this.escapeHtml(user.username)}" style="padding: 8px 12px; cursor: pointer; border-bottom: 1px solid var(--color-border-muted); display: flex; align-items: center; gap: 8px;">
                <div style="width: 24px; height: 24px; border-radius: 50%; background: var(--scitex-color-04); color: white; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600;">
                    ${initial}
                </div>
                <div>
                    <div style="font-weight: 500;">${this.escapeHtml(user.username)}</div>
                    ${emailHtml}
                </div>
            </div>
        `;
    }
    selectUser(item) {
        if (!this.elements) {
            return;
        }
        const username = item.getAttribute('data-username');
        if (username) {
            console.log('[Collaborator Autocomplete] User selected:', username);
            this.elements.input.value = username;
            this.hideDropdown();
        }
    }
    highlightItem(item, highlight) {
        item.style.background = highlight ? 'var(--color-canvas-subtle)' : 'transparent';
    }
    showDropdown() {
        if (this.elements) {
            this.elements.dropdown.style.display = 'block';
        }
    }
    hideDropdown() {
        if (this.elements) {
            this.elements.dropdown.style.display = 'none';
        }
    }
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
}
// Initialize on page load
new CollaboratorAutocomplete();
//# sourceMappingURL=settings_collaborators.js.map