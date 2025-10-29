/**
 * History Timeline Component for Writer App
 *
 * Displays manuscript version history as an interactive timeline
 * with version details, diffs, and rollback functionality.
 */

class HistoryTimeline {
    constructor(manuscriptId, containerId = 'history-timeline-container') {
        this.manuscriptId = manuscriptId;
        this.container = document.getElementById(containerId);
        this.versions = [];
        this.isExpanded = false;
        this.currentDiffView = null;

        if (!this.container) {
            console.error('[HistoryTimeline] Container not found:', containerId);
            return;
        }

        this.init();
    }

    async init() {
        console.log('[HistoryTimeline] Initializing timeline for manuscript:', this.manuscriptId);
        this.renderSkeleton();
        await this.loadVersionHistory();
        this.renderTimeline();
        this.attachEventListeners();
    }

    renderSkeleton() {
        // Show loading skeleton while fetching data
        this.container.innerHTML = `
            <div class="history-timeline-loading">
                <i class="fas fa-spinner fa-spin"></i>
                <span>Loading version history...</span>
            </div>
        `;
    }

    async loadVersionHistory() {
        try {
            const response = await fetch(`/writer/api/version/${this.manuscriptId}/history/`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.success) {
                this.versions = data.versions || [];
                console.log('[HistoryTimeline] Loaded versions:', this.versions.length);
            } else {
                throw new Error(data.error || 'Failed to load version history');
            }
        } catch (error) {
            console.error('[HistoryTimeline] Error loading versions:', error);
            this.renderError(error.message);
        }
    }

    renderTimeline() {
        if (this.versions.length === 0) {
            this.renderEmptyState();
            return;
        }

        const html = `
            <div class="history-timeline-header">
                <div class="timeline-header-left">
                    <button id="history-toggle-btn" class="btn-icon" title="Toggle history panel">
                        <i class="fas fa-${this.isExpanded ? 'chevron-right' : 'history'}"></i>
                    </button>
                    <h3 class="timeline-title">Version History</h3>
                    <span class="timeline-count">${this.versions.length} version${this.versions.length !== 1 ? 's' : ''}</span>
                </div>
                <div class="timeline-header-right">
                    <button id="create-version-btn" class="btn-sm btn-primary" title="Create new version">
                        <i class="fas fa-tag me-1"></i>New Version
                    </button>
                    <button id="view-full-history-btn" class="btn-sm btn-outline" title="View full history dashboard">
                        <i class="fas fa-external-link-alt"></i>
                    </button>
                </div>
            </div>

            <div class="history-timeline-content ${this.isExpanded ? 'expanded' : 'collapsed'}">
                <div class="timeline-entries">
                    ${this.versions.map((version, index) => this.renderVersionEntry(version, index)).join('')}
                </div>
            </div>

            <div id="diff-modal" class="diff-modal" style="display: none;">
                <div class="diff-modal-content">
                    <div class="diff-modal-header">
                        <h4>Version Comparison</h4>
                        <div class="diff-modal-controls">
                            <select id="diff-type-selector" class="form-select-sm">
                                <option value="unified">Unified Diff</option>
                                <option value="side_by_side">Side by Side</option>
                                <option value="word_level">Word Level</option>
                                <option value="semantic">Semantic</option>
                            </select>
                            <button id="close-diff-modal" class="btn-icon">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                    <div class="diff-modal-body" id="diff-modal-body">
                        <div class="diff-loading">
                            <i class="fas fa-spinner fa-spin"></i>
                            <span>Loading diff...</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.container.innerHTML = html;
    }

    renderVersionEntry(version, index) {
        const isLatest = index === 0;
        const isMajor = version.is_major_version;
        const hasTag = version.version_tag && version.version_tag.trim() !== '';

        // Calculate time ago
        const timeAgo = this.getTimeAgo(version.created_at);

        // Determine stats colors
        const deltaClass = version.word_count_delta > 0 ? 'stat-positive' :
                          version.word_count_delta < 0 ? 'stat-negative' : 'stat-neutral';

        return `
            <div class="timeline-entry ${isLatest ? 'latest' : ''} ${isMajor ? 'major' : ''}" data-version-id="${version.id}">
                <div class="timeline-marker">
                    <div class="timeline-dot ${isMajor ? 'major' : ''}">
                        <i class="fas fa-${isMajor ? 'code-branch' : 'circle'}"></i>
                    </div>
                    ${index < this.versions.length - 1 ? '<div class="timeline-line"></div>' : ''}
                </div>

                <div class="timeline-card">
                    <div class="timeline-card-header">
                        <div class="version-badge ${isMajor ? 'major' : 'minor'}">
                            v${version.version_number}
                        </div>
                        ${isLatest ? '<span class="latest-badge">Latest</span>' : ''}
                        ${hasTag ? `<span class="tag-badge" title="${version.version_tag}"><i class="fas fa-tag me-1"></i>${this.truncateText(version.version_tag, 20)}</span>` : ''}
                        <span class="branch-badge">${version.branch_name}</span>
                    </div>

                    <div class="timeline-card-body">
                        <div class="version-meta">
                            <span class="version-author" title="${version.created_by}">
                                <i class="fas fa-user me-1"></i>${version.created_by}
                            </span>
                            <span class="version-time" title="${new Date(version.created_at).toLocaleString()}">
                                <i class="fas fa-clock me-1"></i>${timeAgo}
                            </span>
                        </div>

                        ${version.commit_message ? `
                            <div class="version-message">
                                ${this.escapeHtml(version.commit_message)}
                            </div>
                        ` : ''}

                        <div class="version-stats">
                            <span class="stat-item">
                                <i class="fas fa-edit"></i>
                                <span>${version.total_changes} change${version.total_changes !== 1 ? 's' : ''}</span>
                            </span>
                            ${version.word_count_delta !== 0 ? `
                                <span class="stat-item ${deltaClass}">
                                    <i class="fas fa-${version.word_count_delta > 0 ? 'plus' : 'minus'}"></i>
                                    <span>${Math.abs(version.word_count_delta)} word${Math.abs(version.word_count_delta) !== 1 ? 's' : ''}</span>
                                </span>
                            ` : ''}
                            ${version.lines_added > 0 ? `
                                <span class="stat-item stat-positive">
                                    <i class="fas fa-plus"></i>
                                    <span>${version.lines_added}</span>
                                </span>
                            ` : ''}
                            ${version.lines_removed > 0 ? `
                                <span class="stat-item stat-negative">
                                    <i class="fas fa-minus"></i>
                                    <span>${version.lines_removed}</span>
                                </span>
                            ` : ''}
                        </div>
                    </div>

                    <div class="timeline-card-actions">
                        <button class="btn-xs btn-outline view-diff-btn" data-version-index="${index}" title="View changes">
                            <i class="fas fa-eye me-1"></i>Diff
                        </button>
                        ${!isLatest ? `
                            <button class="btn-xs btn-outline rollback-btn" data-version-id="${version.id}" title="Restore this version">
                                <i class="fas fa-undo me-1"></i>Rollback
                            </button>
                        ` : ''}
                        <button class="btn-xs btn-outline download-btn" data-version-id="${version.id}" title="Download this version">
                            <i class="fas fa-download"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    renderEmptyState() {
        this.container.innerHTML = `
            <div class="history-timeline-empty">
                <div class="empty-icon">
                    <i class="fas fa-history"></i>
                </div>
                <div class="empty-message">No version history yet</div>
                <div class="empty-hint">Versions will appear here as you create them</div>
                <button id="create-first-version-btn" class="btn-sm btn-primary mt-3">
                    <i class="fas fa-tag me-2"></i>Create First Version
                </button>
            </div>
        `;
    }

    renderError(message) {
        this.container.innerHTML = `
            <div class="history-timeline-error">
                <div class="error-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <div class="error-message">Failed to load version history</div>
                <div class="error-detail">${this.escapeHtml(message)}</div>
                <button id="retry-load-btn" class="btn-sm btn-outline mt-3">
                    <i class="fas fa-redo me-2"></i>Retry
                </button>
            </div>
        `;
    }

    attachEventListeners() {
        // Toggle panel
        const toggleBtn = document.getElementById('history-toggle-btn');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.togglePanel());
        }

        // Create version
        const createBtn = document.getElementById('create-version-btn');
        if (createBtn) {
            createBtn.addEventListener('click', () => this.showCreateVersionModal());
        }

        // View full history
        const viewFullBtn = document.getElementById('view-full-history-btn');
        if (viewFullBtn) {
            viewFullBtn.addEventListener('click', () => {
                window.location.href = `/writer/version-control/${this.manuscriptId}/`;
            });
        }

        // View diff buttons
        document.querySelectorAll('.view-diff-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = parseInt(e.currentTarget.dataset.versionIndex);
                this.showDiff(index);
            });
        });

        // Rollback buttons
        document.querySelectorAll('.rollback-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const versionId = e.currentTarget.dataset.versionId;
                this.rollbackToVersion(versionId);
            });
        });

        // Download buttons
        document.querySelectorAll('.download-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const versionId = e.currentTarget.dataset.versionId;
                this.downloadVersion(versionId);
            });
        });

        // Close diff modal
        const closeDiffBtn = document.getElementById('close-diff-modal');
        if (closeDiffBtn) {
            closeDiffBtn.addEventListener('click', () => this.closeDiffModal());
        }

        // Diff type selector
        const diffTypeSelector = document.getElementById('diff-type-selector');
        if (diffTypeSelector) {
            diffTypeSelector.addEventListener('change', () => {
                if (this.currentDiffView) {
                    this.loadDiff(this.currentDiffView.fromVersionId, this.currentDiffView.toVersionId);
                }
            });
        }

        // Retry button (for error state)
        const retryBtn = document.getElementById('retry-load-btn');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => this.init());
        }

        // Create first version (empty state)
        const createFirstBtn = document.getElementById('create-first-version-btn');
        if (createFirstBtn) {
            createFirstBtn.addEventListener('click', () => this.showCreateVersionModal());
        }
    }

    togglePanel() {
        this.isExpanded = !this.isExpanded;
        const content = this.container.querySelector('.history-timeline-content');
        const toggleBtn = document.getElementById('history-toggle-btn');

        if (content) {
            content.classList.toggle('expanded', this.isExpanded);
            content.classList.toggle('collapsed', !this.isExpanded);
        }

        if (toggleBtn) {
            const icon = toggleBtn.querySelector('i');
            icon.className = `fas fa-${this.isExpanded ? 'chevron-right' : 'history'}`;
        }
    }

    async showDiff(versionIndex) {
        if (versionIndex >= this.versions.length - 1) {
            alert('No previous version to compare with');
            return;
        }

        const toVersion = this.versions[versionIndex];
        const fromVersion = this.versions[versionIndex + 1];

        await this.loadDiff(fromVersion.id, toVersion.id);
    }

    async loadDiff(fromVersionId, toVersionId) {
        const modal = document.getElementById('diff-modal');
        const modalBody = document.getElementById('diff-modal-body');
        const diffTypeSelector = document.getElementById('diff-type-selector');
        const diffType = diffTypeSelector ? diffTypeSelector.value : 'unified';

        // Show modal with loading state
        modal.style.display = 'flex';
        modalBody.innerHTML = `
            <div class="diff-loading">
                <i class="fas fa-spinner fa-spin"></i>
                <span>Loading diff...</span>
            </div>
        `;

        // Store current diff view
        this.currentDiffView = { fromVersionId, toVersionId };

        try {
            const response = await fetch(
                `/writer/api/version/${this.manuscriptId}/diff/${fromVersionId}/${toVersionId}/?type=${diffType}`
            );

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.success) {
                modalBody.innerHTML = `
                    <div class="diff-view">
                        ${data.diff.html || this.renderDiffFallback(data.diff)}
                    </div>
                `;
            } else {
                throw new Error(data.error || 'Failed to load diff');
            }
        } catch (error) {
            console.error('[HistoryTimeline] Error loading diff:', error);
            modalBody.innerHTML = `
                <div class="diff-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Failed to load diff: ${this.escapeHtml(error.message)}</p>
                </div>
            `;
        }
    }

    renderDiffFallback(diff) {
        // Fallback renderer if HTML is not provided by backend
        return `
            <pre class="diff-text">${this.escapeHtml(JSON.stringify(diff, null, 2))}</pre>
        `;
    }

    closeDiffModal() {
        const modal = document.getElementById('diff-modal');
        if (modal) {
            modal.style.display = 'none';
        }
        this.currentDiffView = null;
    }

    async rollbackToVersion(versionId) {
        const version = this.versions.find(v => v.id === versionId);
        if (!version) {
            alert('Version not found');
            return;
        }

        const confirmed = confirm(
            `Are you sure you want to rollback to version ${version.version_number}?\n\n` +
            `This will create a new version with the content from v${version.version_number}.`
        );

        if (!confirmed) return;

        try {
            const response = await fetch(`/writer/api/version/${this.manuscriptId}/rollback/${versionId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.success) {
                alert(`Rollback successful! New version created: v${data.rollback_version.version_number}`);
                // Reload timeline
                await this.loadVersionHistory();
                this.renderTimeline();
                this.attachEventListeners();
            } else {
                throw new Error(data.error || 'Rollback failed');
            }
        } catch (error) {
            console.error('[HistoryTimeline] Rollback error:', error);
            alert(`Rollback failed: ${error.message}`);
        }
    }

    async downloadVersion(versionId) {
        // Download version as .tex file
        window.location.href = `/writer/api/version/${this.manuscriptId}/download/${versionId}/`;
    }

    showCreateVersionModal() {
        // This should trigger the main app's create version modal
        // You can emit a custom event that the main app listens to
        const event = new CustomEvent('create-version-requested', {
            detail: { manuscriptId: this.manuscriptId }
        });
        document.dispatchEvent(event);
    }

    // Utility methods
    getTimeAgo(timestamp) {
        const now = new Date();
        const then = new Date(timestamp);
        const seconds = Math.floor((now - then) / 1000);

        const intervals = {
            year: 31536000,
            month: 2592000,
            week: 604800,
            day: 86400,
            hour: 3600,
            minute: 60
        };

        for (const [unit, secondsInUnit] of Object.entries(intervals)) {
            const interval = Math.floor(seconds / secondsInUnit);
            if (interval >= 1) {
                return `${interval} ${unit}${interval !== 1 ? 's' : ''} ago`;
            }
        }

        return 'just now';
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    getCsrfToken() {
        // Get CSRF token from config or cookie
        if (window.WRITER_CONFIG?.csrfToken) {
            return window.WRITER_CONFIG.csrfToken;
        }

        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (tokenElement) {
            return tokenElement.value;
        }

        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return decodeURIComponent(value);
            }
        }

        return '';
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HistoryTimeline;
}
