/**
 * Repository Maintenance Admin Tool
 * Manages repository health monitoring, orphan detection, and sync operations
 * @module repository/admin_maintenance
 */
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
declare class RepositoryMaintenance {
    private username;
    private healthData;
    private pendingAction;
    constructor();
    private init;
    private loadUsername;
    private setupDialogBackdropClose;
    private loadRepositoryHealth;
    private renderHealthStatus;
    private renderIssues;
    private renderIssue;
    private confirmRestore;
    private confirmDelete;
    private confirmSync;
    private executeAction;
    private deleteRepository;
    private syncRepository;
    private restoreRepository;
    private showDialog;
    private closeDialog;
    private showError;
    private getCSRFToken;
    private escapeHtml;
}
//# sourceMappingURL=admin_maintenance.d.ts.map