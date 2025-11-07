/**
 * Sidebar improvements functionality
 * Corresponds to: templates/project_app/shared/sidebar.html
 */
console.log("[DEBUG] apps/project_app/static/project_app/ts/shared/sidebar_improvements.ts loaded");
class SidebarImprovements {
    constructor() {
        this.sidebar = document.querySelector('.sidebar');
        this.init();
    }
    init() {
        console.log('[SidebarImprovements] Initializing sidebar improvements');
        this.setupCollapsible();
    }
    setupCollapsible() {
        const toggleButtons = document.querySelectorAll('.sidebar-toggle');
        toggleButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.sidebar?.classList.toggle('collapsed');
            });
        });
    }
}
document.addEventListener('DOMContentLoaded', () => {
    new SidebarImprovements();
});
//# sourceMappingURL=sidebar_improvements.js.map