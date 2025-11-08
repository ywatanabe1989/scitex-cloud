/**
 * Repository Maintenance Admin Tool
 * Manages repository health monitoring, orphan detection, and sync operations
 * @module repository/admin_maintenance
 */

console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/project_app/static/project_app/ts/repository/admin_maintenance.ts loaded");
interface HealthStats {
    healthy_count: number;
    warnings: number;
    critical_issues: number;
    total_django_projects: number;
}

interface RepositoryIssue {
    is_healthy: boolean;
    is_critical: boolean;
    project_slug?: string;
    gitea_name?: string;
    issue_type: string;
    message: string;
}

interface HealthData {
    success: boolean;
    stats: HealthStats;
    issues: RepositoryIssue[];
    error?: string;
}

interface PendingAction {
    type: 'restore' | 'delete' | 'sync';
    name: string;
    projectName?: string;
}

class RepositoryMaintenance {
    private username: string = '';
    private healthData: HealthData | null = null;
    private pendingAction: PendingAction | null = null;
    private currentFilter: 'all' | 'healthy' | 'warnings' | 'critical' = 'all';

    constructor() {
        this.init();
    }

    private init(): void {
        document.addEventListener('DOMContentLoaded', () => {
            console.log('[Repository Maintenance] Initializing');
            this.loadUsername();
            this.setupDialogBackdropClose();
            this.loadRepositoryHealth();
        });
    }

    private loadUsername(): void {
        const usernameEl = document.querySelector('[data-username]');
        if (usernameEl) {
            this.username = usernameEl.getAttribute('data-username') || '';
            console.log('[Repository Maintenance] Username:', this.username);
        } else {
            console.error('[Repository Maintenance] Username not found');
        }
    }

    private setupDialogBackdropClose(): void {
        const dialog = document.getElementById('confirmation-dialog');
        if (dialog) {
            dialog.addEventListener('click', (e: MouseEvent) => {
                if (e.target === dialog) {
                    this.closeDialog();
                }
            });
        }

        // Expose dialog functions to window
        (window as any).closeDialog = () => this.closeDialog();
        (window as any).executeAction = () => this.executeAction();
        (window as any).confirmRestore = (name: string) => this.confirmRestore(name);
        (window as any).confirmDelete = (name: string) => this.confirmDelete(name);
        (window as any).confirmSync = (name: string) => this.confirmSync(name);
    }

    private async loadRepositoryHealth(): Promise<void> {
        console.log('[Repository Maintenance] Loading repository health');

        try {
            const response = await fetch(`/${this.username}/api/repository-health/`);
            const data: HealthData = await response.json();

            if (data.success) {
                this.healthData = data;
                this.renderHealthStatus(data);
                this.renderIssues(data);
            } else {
                this.showError(data.error || 'Failed to load repository health');
            }
        } catch (error) {
            console.error('[Repository Maintenance] Error:', error);
            this.showError('Failed to connect to server');
        }
    }

    private renderHealthStatus(data: HealthData): void {
        const stats = data.stats;
        const html = `
            <div class="health-card success ${this.currentFilter === 'healthy' ? 'active' : ''}" data-filter="healthy" title="Click to show only healthy repositories">
                <div class="health-card-value">${stats.healthy_count}</div>
                <div class="health-card-label">Healthy</div>
            </div>
            <div class="health-card warning ${this.currentFilter === 'warnings' ? 'active' : ''}" data-filter="warnings" title="Click to show only warnings">
                <div class="health-card-value">${stats.warnings}</div>
                <div class="health-card-label">Warnings</div>
            </div>
            <div class="health-card ${stats.critical_issues > 0 ? 'critical' : ''} ${this.currentFilter === 'critical' ? 'active' : ''}" data-filter="critical" title="Click to show only critical issues">
                <div class="health-card-value">${stats.critical_issues}</div>
                <div class="health-card-label">Critical</div>
            </div>
            <div class="health-card ${this.currentFilter === 'all' ? 'active' : ''}" data-filter="all" title="Click to show all repositories">
                <div class="health-card-value">${stats.total_django_projects}</div>
                <div class="health-card-label">Total Projects</div>
            </div>
        `;
        const statusEl = document.getElementById('health-status');
        if (statusEl) {
            statusEl.innerHTML = html;

            // Add click handlers to cards
            statusEl.querySelectorAll('.health-card').forEach((card) => {
                card.addEventListener('click', () => {
                    const filter = card.getAttribute('data-filter') as 'all' | 'healthy' | 'warnings' | 'critical';
                    this.applyFilter(filter);
                });
            });
        }
    }

    private renderIssues(data: HealthData): void {
        const issues = data.issues;
        const issuesListEl = document.getElementById('issues-list');

        if (!issuesListEl) {
            return;
        }

        if (issues.length === 0) {
            issuesListEl.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">✓</div>
                    <div class="empty-state-title">All repositories are healthy!</div>
                    <div class="empty-state-message">No synchronization issues detected</div>
                </div>
            `;
            return;
        }

        const html = issues.map(issue => this.renderIssue(issue)).join('');
        issuesListEl.innerHTML = html;

        // Apply current filter
        this.applyCurrentFilter();
    }

    private applyFilter(filter: 'all' | 'healthy' | 'warnings' | 'critical'): void {
        this.currentFilter = filter;
        console.log('[Repository Maintenance] Applying filter:', filter);

        // Update health cards to show active state
        if (this.healthData) {
            this.renderHealthStatus(this.healthData);
        }

        // Filter the repository cards
        this.applyCurrentFilter();
    }

    private applyCurrentFilter(): void {
        const issueCards = document.querySelectorAll('.issue-card');

        let visibleCount = 0;

        issueCards.forEach((card) => {
            const htmlCard = card as HTMLElement;
            let shouldShow = false;

            if (this.currentFilter === 'all') {
                shouldShow = true;
            } else if (this.currentFilter === 'healthy') {
                shouldShow = card.getAttribute('data-status') === 'healthy';
            } else if (this.currentFilter === 'warnings') {
                shouldShow = card.getAttribute('data-status') === 'warning';
            } else if (this.currentFilter === 'critical') {
                shouldShow = card.getAttribute('data-status') === 'critical';
            }

            if (shouldShow) {
                htmlCard.style.display = '';
                visibleCount++;
            } else {
                htmlCard.style.display = 'none';
            }
        });

        console.log(`[Repository Maintenance] Showing ${visibleCount}/${issueCards.length} repositories`);
    }

    private renderIssue(issue: RepositoryIssue): string {
        const icon = issue.is_healthy ? '✓' : (issue.is_critical ? '✗' : '⚠');
        const iconClass = issue.is_healthy ? 'healthy' : (issue.is_critical ? 'critical' : 'warning');
        const name = issue.project_slug || issue.gitea_name || 'Unknown';

        let localStatus = '—';
        let djangoStatus = '—';
        let giteaStatus = '—';
        let issueTypeDisplay = '';

        if (issue.issue_type === 'healthy') {
            localStatus = '✓ Local';
            djangoStatus = '✓ Project';
            giteaStatus = '✓ Repository';
            issueTypeDisplay = 'In sync';
        } else if (issue.issue_type === 'orphaned_in_gitea') {
            localStatus = '—';
            djangoStatus = '—';
            giteaStatus = '✓ Repository';
            issueTypeDisplay = 'Orphaned in Gitea';
        } else if (issue.issue_type === 'missing_in_gitea') {
            localStatus = '?';
            djangoStatus = '✓ Project';
            giteaStatus = '✗ Missing';
            issueTypeDisplay = 'Repository missing';
        } else if (issue.issue_type === 'missing_directory') {
            localStatus = '✗ Missing';
            djangoStatus = '✓ Project';
            giteaStatus = '✓ Repository';
            issueTypeDisplay = 'Local directory missing';
        }

        let actions = '';
        if (issue.issue_type === 'orphaned_in_gitea') {
            actions = `
                <button class="issue-button sync" onclick="confirmRestore('${this.escapeHtml(name)}')">
                    ↺ Restore Project
                </button>
            `;
        } else if (issue.issue_type === 'missing_in_gitea' || issue.issue_type === 'missing_directory') {
            actions = `
                <button class="issue-button sync" onclick="confirmSync('${this.escapeHtml(name)}')">
                    🔄 Sync Repository
                </button>
            `;
        }

        // Determine status for filtering
        const status = issue.is_healthy ? 'healthy' : (issue.is_critical ? 'critical' : 'warning');

        return `
            <div class="issue-item issue-card" data-status="${status}">
                <div class="issue-header">
                    <div class="issue-icon ${iconClass}">${icon}</div>
                    <div class="issue-content" style="flex: 1;">
                        <div class="issue-title">
                            <span class="issue-name">${this.escapeHtml(name)}</span>
                            <span style="margin-left: 0.5rem; color: var(--color-fg-muted);">${issueTypeDisplay}</span>
                        </div>
                        <div style="font-size: 0.875rem; color: var(--color-fg-muted); margin-top: 0.25rem;">
                            ${issue.message}
                        </div>
                    </div>
                </div>
                <div class="issue-status-columns">
                    <div class="status-column">
                        <div class="status-label">Local</div>
                        <div class="status-value">${localStatus}</div>
                    </div>
                    <div class="status-column">
                        <div class="status-label">Django Project</div>
                        <div class="status-value">${djangoStatus}</div>
                    </div>
                    <div class="status-column">
                        <div class="status-label">Gitea Repository</div>
                        <div class="status-value">${giteaStatus}</div>
                    </div>
                </div>
                <div class="issue-actions">
                    ${actions}
                </div>
            </div>
        `;
    }

    private confirmRestore(repositoryName: string): void {
        this.pendingAction = {
            type: 'restore',
            name: repositoryName,
            projectName: repositoryName
        };

        const projectNameId = 'restore-project-name-input';
        const dialogMessageEl = document.getElementById('dialog-message');

        if (dialogMessageEl) {
            dialogMessageEl.innerHTML = `
                <p>Restore this orphaned repository by creating a new project?</p>
                <p style="margin: 1rem 0; font-family: monospace; background: var(--color-canvas-subtle); padding: 0.5rem; border-radius: 0.25rem; word-break: break-all;">
                    ${this.escapeHtml(repositoryName)}
                </p>
                <div style="margin: 1rem 0;">
                    <label for="${projectNameId}" style="display: block; margin-bottom: 0.5rem; font-weight: 500;">
                        Project name for restored repository:
                    </label>
                    <input type="text" id="${projectNameId}" value="${this.escapeHtml(repositoryName)}"
                           style="width: 100%; padding: 0.5rem; border: 1px solid var(--color-border-default);
                           border-radius: 0.25rem; background: var(--color-canvas-subtle); color: var(--color-fg-default);">
                </div>
                <p><strong>Note:</strong> This will create a new Django project linked to the existing Gitea repository and clone it to your local filesystem.</p>
            `;
        }

        this.showDialog();

        // Focus input and setup enter key handler
        setTimeout(() => {
            const input = document.getElementById(projectNameId) as HTMLInputElement;
            if (input) {
                input.focus();
                input.addEventListener('keypress', (e: KeyboardEvent) => {
                    if (e.key === 'Enter') {
                        this.executeAction();
                    }
                });
            }
        }, 100);
    }

    private confirmDelete(repositoryName: string): void {
        this.pendingAction = {
            type: 'delete',
            name: repositoryName
        };

        const dialogMessageEl = document.getElementById('dialog-message');
        if (dialogMessageEl) {
            dialogMessageEl.innerHTML = `
                <p>Are you sure you want to delete this orphaned repository?</p>
                <p style="margin: 1rem 0; font-family: monospace; background: var(--color-canvas-subtle); padding: 0.5rem; border-radius: 0.25rem; word-break: break-all;">
                    ${this.escapeHtml(repositoryName)}
                </p>
                <p><strong>Warning:</strong> This action cannot be undone. The repository will be permanently deleted from Gitea.</p>
            `;
        }

        this.showDialog();
    }

    private confirmSync(projectSlug: string): void {
        this.pendingAction = {
            type: 'sync',
            name: projectSlug
        };

        const dialogMessageEl = document.getElementById('dialog-message');
        if (dialogMessageEl) {
            dialogMessageEl.innerHTML = `
                <p>Sync this repository with Gitea?</p>
                <p style="margin: 1rem 0; font-family: monospace; background: var(--color-canvas-subtle); padding: 0.5rem; border-radius: 0.25rem; word-break: break-all;">
                    ${this.escapeHtml(projectSlug)}
                </p>
                <p>This will re-clone the repository from Gitea if the local directory is missing.</p>
            `;
        }

        this.showDialog();
    }

    private executeAction(): void {
        if (!this.pendingAction) {
            return;
        }

        const { type, name } = this.pendingAction;
        let projectName = this.pendingAction.projectName || name;

        if (type === 'restore') {
            const input = document.getElementById('restore-project-name-input') as HTMLInputElement;
            if (input) {
                projectName = input.value.trim();
            }
        }

        this.closeDialog();

        if (type === 'restore') {
            this.restoreRepository(name, projectName);
        } else if (type === 'delete') {
            this.deleteRepository(name);
        } else if (type === 'sync') {
            this.syncRepository(name);
        }
    }

    private async deleteRepository(repositoryName: string): Promise<void> {
        console.log('[Repository Maintenance] Deleting repository:', repositoryName);

        try {
            const response = await fetch(`/${this.username}/api/repository-cleanup/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ gitea_name: repositoryName })
            });

            const data = await response.json();

            if (data.success) {
                setTimeout(() => this.loadRepositoryHealth(), 500);
            } else {
                this.showError(data.message || data.error);
            }
        } catch (error) {
            console.error('[Repository Maintenance] Error:', error);
            this.showError('Failed to delete repository');
        }
    }

    private async syncRepository(projectSlug: string): Promise<void> {
        console.log('[Repository Maintenance] Syncing repository:', projectSlug);

        try {
            const response = await fetch(`/${this.username}/api/repository-sync/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ project_slug: projectSlug })
            });

            const data = await response.json();

            if (data.success) {
                setTimeout(() => this.loadRepositoryHealth(), 500);
            } else {
                this.showError(data.message || data.error);
            }
        } catch (error) {
            console.error('[Repository Maintenance] Error:', error);
            this.showError('Failed to sync repository');
        }
    }

    private async restoreRepository(repositoryName: string, projectName: string): Promise<void> {
        console.log('[Repository Maintenance] Restoring repository:', repositoryName, 'as project:', projectName);

        try {
            const response = await fetch(`/${this.username}/api/repository-restore/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    gitea_name: repositoryName,
                    project_name: projectName
                })
            });

            console.log('[Repository Maintenance] Response status:', response.status);
            const data = await response.json();
            console.log('[Repository Maintenance] Response data:', data);

            if (data.success) {
                if (data.project_id) {
                    const slugifiedName = projectName
                        .toLowerCase()
                        .replace(/\s+/g, '-')
                        .replace(/[^\w\-]/g, '');

                    console.log('[Repository Maintenance] Redirecting to:', `/${this.username}/${slugifiedName}/`);
                    setTimeout(() => {
                        window.location.href = `/${this.username}/${slugifiedName}/`;
                    }, 500);
                } else {
                    console.log('[Repository Maintenance] Reloading health page');
                    setTimeout(() => this.loadRepositoryHealth(), 500);
                }
            } else {
                console.error('[Repository Maintenance] API Error:', data);
                this.showError(data.message || data.error);
            }
        } catch (error) {
            console.error('[Repository Maintenance] Error:', error);
            this.showError('Failed to restore repository');
        }
    }

    private showDialog(): void {
        const dialog = document.getElementById('confirmation-dialog');
        if (dialog) {
            dialog.classList.add('show');
        }
    }

    private closeDialog(): void {
        const dialog = document.getElementById('confirmation-dialog');
        if (dialog) {
            dialog.classList.remove('show');
        }
        this.pendingAction = null;
    }

    private showError(message: string): void {
        const errorEl = document.getElementById('error-message');
        const errorTextEl = document.getElementById('error-text');

        if (errorEl && errorTextEl) {
            errorTextEl.textContent = message;
            errorEl.style.display = 'block';

            setTimeout(() => {
                errorEl.style.display = 'none';
            }, 5000);
        }
    }

    private getCSRFToken(): string {
        const tokenEl = document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement;
        return tokenEl?.value || '';
    }

    private escapeHtml(text: string): string {
        const map: Record<string, string> = {
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
new RepositoryMaintenance();
