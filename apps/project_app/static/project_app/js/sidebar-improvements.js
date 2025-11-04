/* =============================================================================
   SIDEBAR IMPROVEMENTS - JavaScript Updates
   Apply these changes to the <script> section in project_detail.html
   ============================================================================= */

// ===========================================================================
// 1. UPDATE: initializeSidebar() function
// Replace the existing function with this enhanced version
// ===========================================================================
function initializeSidebar() {
    const sidebar = document.getElementById('repo-sidebar');
    const repoLayout = document.getElementById('repo-layout');
    const toggleBtn = document.getElementById('sidebar-toggle');
    const savedState = localStorage.getItem(SIDEBAR_STATE_KEY);

    console.log('Initializing sidebar. Saved state:', savedState);

    // Always start collapsed by default (per GitHub style)
    sidebar.classList.add('collapsed');
    repoLayout.classList.add('sidebar-collapsed');
    toggleBtn.setAttribute('title', 'Expand sidebar');  // ADDED
    console.log('Sidebar initialized as collapsed (default)');

    // Restore section states
    const savedSections = localStorage.getItem(SIDEBAR_SECTIONS_KEY);
    if (savedSections) {
        try {
            const sections = JSON.parse(savedSections);
            Object.keys(sections).forEach(sectionId => {
                const section = document.getElementById(sectionId);
                if (section && sections[sectionId] === 'collapsed') {
                    section.classList.add('section-collapsed');
                }
            });
        } catch (e) {
            console.error('Error restoring section states:', e);
        }
    }
}

// ===========================================================================
// 2. UPDATE: toggleSidebar() function
// Replace the existing function with this enhanced version
// ===========================================================================
function toggleSidebar() {
    const sidebar = document.getElementById('repo-sidebar');
    const repoLayout = document.getElementById('repo-layout');
    const toggleBtn = document.getElementById('sidebar-toggle');  // ADDED

    if (sidebar.classList.contains('collapsed')) {
        // Expand sidebar
        sidebar.classList.remove('collapsed');
        sidebar.classList.add('expanded');
        repoLayout.classList.remove('sidebar-collapsed');
        repoLayout.classList.add('sidebar-expanded');
        localStorage.setItem(SIDEBAR_STATE_KEY, 'expanded');
        toggleBtn.setAttribute('title', 'Collapse sidebar');  // ADDED
        console.log('Sidebar expanded');
    } else {
        // Collapse sidebar
        sidebar.classList.remove('expanded');
        sidebar.classList.add('collapsed');
        repoLayout.classList.remove('sidebar-expanded');
        repoLayout.classList.add('sidebar-collapsed');
        localStorage.setItem(SIDEBAR_STATE_KEY, 'collapsed');
        toggleBtn.setAttribute('title', 'Expand sidebar');  // ADDED
        console.log('Sidebar collapsed');
    }
}

// ===========================================================================
// 3. UPDATE: loadProjectStats() function
// Replace the existing function with this enhanced version
// ===========================================================================
async function loadProjectStats() {
    try {
        const response = await fetch('/{{ project.owner.username }}/{{ project.slug }}/api/stats/');
        const data = await response.json();

        if (data.success) {
            // Update counts
            document.getElementById('watch-count').textContent = data.stats.watch_count;
            document.getElementById('star-count').textContent = data.stats.star_count;
            document.getElementById('fork-count').textContent = data.stats.fork_count;

            // UPDATE SIDEBAR COUNTS (ADDED SECTION)
            const sidebarStarCount = document.getElementById('sidebar-star-count');
            const sidebarForkCount = document.getElementById('sidebar-fork-count');
            if (sidebarStarCount) {
                sidebarStarCount.textContent = `${data.stats.star_count} ${data.stats.star_count === 1 ? 'star' : 'stars'}`;
            }
            if (sidebarForkCount) {
                sidebarForkCount.textContent = `${data.stats.fork_count} ${data.stats.fork_count === 1 ? 'fork' : 'forks'}`;
            }

            // Update button states
            if (data.user_status.is_watching) {
                document.getElementById('watch-btn').classList.add('active');
            }
            if (data.user_status.is_starred) {
                document.getElementById('star-btn').classList.add('active');
            }
        }
    } catch (error) {
        console.error('Failed to load project stats:', error);
    }
}

/* =============================================================================
   END OF JAVASCRIPT IMPROVEMENTS
   ============================================================================= */
