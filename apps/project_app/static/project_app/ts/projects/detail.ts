// =============================================================================
// Sidebar State Management
// =============================================================================

import { loadFileTree as loadFileTreeShared, toggleFolder as toggleFolderShared } from '../shared/file-tree.js';
import { getCsrfToken } from '../utils/csrf.js';

console.log("[DEBUG] apps/project_app/static/project_app/ts/projects/detail.ts loaded");

(function() {
    'use strict';

const SIDEBAR_STATE_KEY = 'scitex-sidebar-state';
const SIDEBAR_SECTIONS_KEY = 'scitex-sidebar-sections';

// Initialize sidebar state from localStorage
function initializeSidebar(): void {
    const sidebar = document.getElementById('repo-sidebar');
    const repoLayout = document.getElementById('repo-layout');
    const toggleBtn = document.getElementById('sidebar-toggle');
    const savedState = localStorage.getItem(SIDEBAR_STATE_KEY);

    console.log('Initializing sidebar. Saved state:', savedState);

    // Check if sidebar element exists before trying to manipulate it
    if (!sidebar) {
        console.log('Sidebar element not found on this page, skipping sidebar initialization');
        return;
    }

    // Start collapsed by default, but respect localStorage if user explicitly expanded it
    if (savedState === 'expanded') {
        sidebar.classList.remove('collapsed');
        sidebar.classList.add('expanded');
        if (repoLayout) {
            repoLayout.classList.remove('sidebar-collapsed');
            repoLayout.classList.add('sidebar-expanded');
        }
        if (toggleBtn) {
            toggleBtn.setAttribute('title', 'Collapse sidebar');
        }
        console.log('Sidebar initialized as expanded (from localStorage)');
    } else {
        sidebar.classList.add('collapsed');
        if (repoLayout) {
            repoLayout.classList.add('sidebar-collapsed');
        }
        if (toggleBtn) {
            toggleBtn.setAttribute('title', 'Expand sidebar');
        }
        console.log('Sidebar initialized as collapsed (default)');
    }

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

// Toggle entire sidebar
function toggleSidebar(): void {
    const sidebar = document.getElementById('repo-sidebar');
    const repoLayout = document.getElementById('repo-layout');
    const toggleBtn = document.getElementById('sidebar-toggle');

    if (!sidebar) return;

    if (sidebar.classList.contains('collapsed')) {
        // Expand sidebar
        sidebar.classList.remove('collapsed');
        sidebar.classList.add('expanded');
        if (repoLayout) {
            repoLayout.classList.remove('sidebar-collapsed');
            repoLayout.classList.add('sidebar-expanded');
        }
        localStorage.setItem(SIDEBAR_STATE_KEY, 'expanded');
        if (toggleBtn) {
            toggleBtn.setAttribute('title', 'Collapse sidebar');
        }
        console.log('Sidebar expanded');
    } else {
        // Collapse sidebar
        sidebar.classList.remove('expanded');
        sidebar.classList.add('collapsed');
        if (repoLayout) {
            repoLayout.classList.remove('sidebar-expanded');
            repoLayout.classList.add('sidebar-collapsed');
        }
        localStorage.setItem(SIDEBAR_STATE_KEY, 'collapsed');
        if (toggleBtn) {
            toggleBtn.setAttribute('title', 'Expand sidebar');
        }
        console.log('Sidebar collapsed');
    }
}

// Toggle individual sidebar section
function toggleSidebarSection(sectionId: string): void {
    const sidebar = document.getElementById('repo-sidebar');

    // Don't toggle sections when sidebar is collapsed
    if (!sidebar || sidebar.classList.contains('collapsed')) {
        return;
    }

    const section = document.getElementById(sectionId);
    if (!section) return;

    section.classList.toggle('section-collapsed');

    // Save section states
    saveSectionStates();
}

// Save all section states to localStorage
function saveSectionStates(): void {
    const fileTreeSection = document.getElementById('file-tree-section');
    const aboutSection = document.getElementById('about-section');

    const sections: Record<string, string> = {};
    if (fileTreeSection) {
        sections['file-tree-section'] = fileTreeSection.classList.contains('section-collapsed') ? 'collapsed' : 'expanded';
    }
    if (aboutSection) {
        sections['about-section'] = aboutSection.classList.contains('section-collapsed') ? 'collapsed' : 'expanded';
    }
    localStorage.setItem(SIDEBAR_SECTIONS_KEY, JSON.stringify(sections));
}

// =============================================================================
// File Tree
// =============================================================================

// Build file tree for sidebar using shared module
async function loadFileTree(): Promise<void> {
    const projectData = (window as any).SCITEX_PROJECT_DATA;
    if (!projectData) {
        console.error('Project data not available');
        return;
    }

    await loadFileTreeShared(projectData.owner, projectData.slug, 'file-tree');
}

// Use shared toggle function
function toggleFolder(folderId: string, event?: Event): void {
    toggleFolderShared(folderId, event);
}

// =============================================================================
// Project Concatenation
// =============================================================================

async function copyProjectToClipboard(event: Event): Promise<void> {
    const projectData = (window as any).SCITEX_PROJECT_DATA;
    if (!projectData) return;

    const btn = event.currentTarget as HTMLButtonElement;
    const originalText = btn.innerHTML;
    btn.innerHTML = '⏳ Loading...';
    btn.disabled = true;

    try {
        const response = await fetch(`/${projectData.owner}/${projectData.slug}/api/concatenate/`);
        const data = await response.json();

        if (data.success) {
            await navigator.clipboard.writeText(data.content);
            const checkIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" class="octicon octicon-16" style="vertical-align: text-bottom; margin-right: 4px;"><path fill="currentColor" d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"></path></svg>';
            btn.innerHTML = `${checkIcon} Copied ${data.file_count} files!`;
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }, 3000);
        } else {
            alert('Error: ' + data.error);
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    } catch (err) {
        alert('Failed to copy: ' + err);
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function downloadProjectAsFile(event: Event): Promise<void> {
    const projectData = (window as any).SCITEX_PROJECT_DATA;
    if (!projectData) return;

    const btn = event.currentTarget as HTMLButtonElement;
    const originalText = btn.innerHTML;
    btn.innerHTML = '⏳ Preparing download...';
    btn.disabled = true;

    try {
        const response = await fetch(`/${projectData.owner}/${projectData.slug}/api/concatenate/`);
        const data = await response.json();

        if (data.success) {
            // Create a blob and download it
            const blob = new Blob([data.content], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${projectData.slug}_all_files.txt`;

            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            const checkIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" class="octicon octicon-16" style="vertical-align: text-bottom; margin-right: 4px;"><path fill="currentColor" d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"></path></svg>';
            btn.innerHTML = `${checkIcon} Downloaded ${data.file_count} files!`;
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }, 3000);
        } else {
            alert('Error: ' + data.error);
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    } catch (err) {
        alert('Failed to download: ' + err);
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// =============================================================================
// Watch/Star/Fork Action Handlers
// =============================================================================

async function loadProjectStats(): Promise<void> {
    const projectData = (window as any).SCITEX_PROJECT_DATA;
    if (!projectData) return;

    try {
        const response = await fetch(`/${projectData.owner}/${projectData.slug}/api/stats/`);
        const data = await response.json();

        if (data.success) {
            // Update counts
            const watchCount = document.getElementById('watch-count');
            const starCount = document.getElementById('star-count');
            const forkCount = document.getElementById('fork-count');

            if (watchCount) watchCount.textContent = data.stats.watch_count;
            if (starCount) starCount.textContent = data.stats.star_count;
            if (forkCount) forkCount.textContent = data.stats.fork_count;

            // Update button states
            const watchBtn = document.getElementById('watch-btn');
            const starBtn = document.getElementById('star-btn');

            if (data.user_status.is_watching && watchBtn) {
                watchBtn.classList.add('active');
            }
            if (data.user_status.is_starred && starBtn) {
                starBtn.classList.add('active');
            }
        }
    } catch (error) {
        console.error('Failed to load project stats:', error);
    }
}

async function handleWatch(event: Event): Promise<void> {
    const projectData = (window as any).SCITEX_PROJECT_DATA;
    if (!projectData) return;

    const btn = event.currentTarget as HTMLElement;

    try {
        const response = await fetch(`/${projectData.owner}/${projectData.slug}/api/watch/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        });

        const data = await response.json();

        if (data.success) {
            // Toggle active state
            if (data.is_watching) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }

            // Update count
            const watchCount = document.getElementById('watch-count');
            if (watchCount) watchCount.textContent = data.watch_count;

            // Show notification
            showNotification(data.message, 'success');
        } else {
            showNotification(data.error || 'Failed to update watch status', 'error');
        }
    } catch (error) {
        console.error('Error toggling watch:', error);
        showNotification('Failed to update watch status', 'error');
    }
}

async function handleStar(event: Event): Promise<void> {
    const projectData = (window as any).SCITEX_PROJECT_DATA;
    if (!projectData) return;

    const btn = event.currentTarget as HTMLElement;

    try {
        const response = await fetch(`/${projectData.owner}/${projectData.slug}/api/star/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        });

        const data = await response.json();

        if (data.success) {
            // Toggle active state
            if (data.is_starred) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }

            // Update count
            const starCount = document.getElementById('star-count');
            if (starCount) starCount.textContent = data.star_count;

            // Show notification
            showNotification(data.message, 'success');
        } else {
            showNotification(data.error || 'Failed to update star status', 'error');
        }
    } catch (error) {
        console.error('Error toggling star:', error);
        showNotification('Failed to update star status', 'error');
    }
}

async function handleFork(event: Event): Promise<void> {
    if (!confirm('Fork this repository? This will create a copy under your account.')) {
        return;
    }

    const projectData = (window as any).SCITEX_PROJECT_DATA;
    if (!projectData) return;

    const btn = event.currentTarget as HTMLButtonElement;
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span>Forking...</span>';

    try {
        const response = await fetch(`/${projectData.owner}/${projectData.slug}/api/fork/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        });

        const data = await response.json();

        if (data.success) {
            // Update count
            const forkCount = document.getElementById('fork-count');
            if (forkCount) forkCount.textContent = data.fork_count;

            // Show success message and redirect
            showNotification(data.message, 'success');
            setTimeout(() => {
                window.location.href = data.forked_project.url;
            }, 1500);
        } else {
            showNotification(data.error || 'Failed to fork repository', 'error');
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    } catch (error) {
        console.error('Error forking project:', error);
        showNotification('Failed to fork repository', 'error');
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Helper function to show notifications
function showNotification(message: string, type: string = 'info'): void {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 24px;
        background: ${type === 'success' ? 'var(--color-success-emphasis)' : type === 'error' ? 'var(--color-danger-emphasis)' : 'var(--color-accent-emphasis)'};
        color: white;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// =============================================================================
// Toolbar Dropdown Functions
// =============================================================================

function toggleBranchDropdown(): void {
    const dropdown = document.getElementById('branch-dropdown') as HTMLElement | null;
    const isVisible = dropdown && dropdown.style.display === 'block';

    // Close all other dropdowns
    closeAllDropdowns();

    if (dropdown) {
        dropdown.style.display = isVisible ? 'none' : 'block';
        console.log('Branch dropdown toggled:', dropdown.style.display);
    }
}

function switchBranch(branchName: string): void {
    console.log('Switching to branch:', branchName);
    const currentBranch = document.getElementById('current-branch');
    if (currentBranch) currentBranch.textContent = branchName;

    // Update active state in dropdown
    document.querySelectorAll('.branch-item').forEach((item: Element) => {
        const htmlItem = item as HTMLElement;
        if (htmlItem.dataset.branch === branchName) {
            htmlItem.classList.add('active');
            const svg = htmlItem.querySelector('svg') as SVGElement | null;
            if (svg) svg.style.opacity = '1';
        } else {
            htmlItem.classList.remove('active');
            const svg = htmlItem.querySelector('svg') as SVGElement | null;
            if (svg) svg.style.opacity = '0';
        }
    });

    // Close dropdown
    const branchDropdown = document.getElementById('branch-dropdown') as HTMLElement | null;
    if (branchDropdown) branchDropdown.style.display = 'none';

    // TODO: Reload page with selected branch
    // const projectData = window.SCITEX_PROJECT_DATA;
    // window.location.href = `/${projectData.owner}/${projectData.slug}/?branch=${branchName}`;
}

// Simple wrapper functions for toolbar buttons
function toggleWatch(): void {
    const btn = document.getElementById('watch-btn');
    if (btn) {
        // Create a proper event object
        const event = new MouseEvent('click', {
            bubbles: true,
            cancelable: true,
            view: window
        });
        // Set currentTarget manually after creation
        Object.defineProperty(event, 'currentTarget', {
            writable: false,
            value: btn
        });
        handleWatch(event);
    }
}

function toggleStar(): void {
    const btn = document.getElementById('star-btn');
    if (btn) {
        // Create a proper event object
        const event = new MouseEvent('click', {
            bubbles: true,
            cancelable: true,
            view: window
        });
        // Set currentTarget manually after creation
        Object.defineProperty(event, 'currentTarget', {
            writable: false,
            value: btn
        });
        handleStar(event);
    }
}

function forkProject(): void {
    const btn = document.getElementById('fork-btn');
    if (btn) {
        // Create a proper event object
        const event = new MouseEvent('click', {
            bubbles: true,
            cancelable: true,
            view: window
        });
        // Set currentTarget manually after creation
        Object.defineProperty(event, 'currentTarget', {
            writable: false,
            value: btn
        });
        handleFork(event);
    }
}

function toggleAddFileDropdown(): void {
    const dropdown = document.getElementById('add-file-dropdown') as HTMLElement | null;
    if (!dropdown) return;

    const isVisible = dropdown.style.display === 'block';

    // Close all other dropdowns
    closeAllDropdowns();

    dropdown.style.display = isVisible ? 'none' : 'block';
    console.log('Add file dropdown toggled:', dropdown.style.display);
}

function toggleCodeDropdown(): void {
    const dropdown = document.getElementById('code-dropdown') as HTMLElement | null;
    if (!dropdown) return;

    const isVisible = dropdown.style.display === 'block';

    // Close all other dropdowns
    closeAllDropdowns();

    dropdown.style.display = isVisible ? 'none' : 'block';
    console.log('Code dropdown toggled:', dropdown.style.display);
}

function toggleCopyDropdown(): void {
    const dropdown = document.getElementById('copy-dropdown') as HTMLElement | null;
    if (!dropdown) return;

    const isVisible = dropdown.style.display === 'block';

    // Close all other dropdowns
    closeAllDropdowns();

    dropdown.style.display = isVisible ? 'none' : 'block';
    console.log('Copy dropdown toggled:', dropdown.style.display);
}

function closeAllDropdowns(): void {
    const dropdowns = ['branch-dropdown-menu', 'add-file-dropdown', 'code-dropdown', 'copy-dropdown'];
    dropdowns.forEach(id => {
        const dropdown = document.getElementById(id) as HTMLElement | null;
        if (dropdown && dropdown.style.display === 'block') {
            dropdown.style.display = 'none';
        }
    });
}

function copyCloneUrl(event: Event): void {
    const input = document.getElementById('clone-url') as HTMLInputElement;
    if (!input) return;

    navigator.clipboard.writeText(input.value).then(() => {
        const btn = (event.target as HTMLElement).closest('button');
        if (!btn) return;

        const originalHTML = btn.innerHTML;
        btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z"/></svg>';
        setTimeout(() => {
            btn.innerHTML = originalHTML;
        }, 2000);
    }).catch((err: Error) => {
        console.error('Failed to copy:', err);
    });
}

function downloadProjectZip(): void {
    // Placeholder for ZIP download functionality
    alert('ZIP download functionality coming soon!');
}

// =============================================================================
// Event Listeners
// =============================================================================

// Load file tree on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded - initializing sidebar, file tree and dropdown');

    // Initialize sidebar state
    initializeSidebar();

    // Load file tree
    loadFileTree();

    // Load initial stats
    loadProjectStats();

    // Make table rows clickable
    const fileBrowserRows = document.querySelectorAll('.file-browser-row');
    fileBrowserRows.forEach((row: Element) => {
        row.addEventListener('click', function(this: HTMLElement, e: Event) {
            // Don't navigate if clicking on a link directly
            const target = e.target as HTMLElement;
            if (target.tagName === 'A' || target.closest('a')) {
                return;
            }
            const href = this.getAttribute('data-href');
            if (href) {
                window.location.href = href;
            }
        });
    });

    // Manual dropdown toggle for split button
    const dropdownToggle = document.querySelector('.dropdown-toggle-split');
    const dropdownMenu = document.querySelector('.dropdown-menu') as HTMLElement | null;

    if (dropdownToggle && dropdownMenu) {
        console.log('Dropdown elements found - setting up manual toggle');

        dropdownToggle.addEventListener('click', function(e) {
            console.log('Dropdown toggle clicked!');
            e.preventDefault();
            e.stopPropagation();

            const isVisible = dropdownMenu.style.display === 'block';
            dropdownMenu.style.display = isVisible ? 'none' : 'block';
            console.log('Dropdown visibility toggled to:', dropdownMenu.style.display);
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            const target = e.target as Node;
            if (!dropdownToggle.contains(target) && !dropdownMenu.contains(target)) {
                dropdownMenu.style.display = 'none';
            }
        });
    } else {
        console.warn('Dropdown elements not found:', {dropdownToggle, dropdownMenu});
    }
});

// Close dropdowns when clicking outside
document.addEventListener('click', function(e: Event) {
    // Check if click is on any dropdown button or within dropdown content
    const target = e.target as HTMLElement;
    const clickedButton = target.closest('button');
    const isDropdownButton = clickedButton && (
        clickedButton.id === 'branch-dropdown-btn-header' ||
        clickedButton.id === 'add-file-btn' ||
        clickedButton.classList.contains('dropdown-toggle-split')
    );
    const isDropdownContent = target.closest('.dropdown-menu');

    if (!isDropdownButton && !isDropdownContent) {
        closeAllDropdowns();
    }
});

// Expose functions to global scope for onclick handlers
(window as any).toggleSidebar = toggleSidebar;
(window as any).toggleSidebarSection = toggleSidebarSection;
(window as any).toggleFolder = toggleFolder;
(window as any).copyProjectToClipboard = copyProjectToClipboard;
(window as any).downloadProjectAsFile = downloadProjectAsFile;
(window as any).handleWatch = handleWatch;
(window as any).handleStar = handleStar;
(window as any).handleFork = handleFork;
(window as any).toggleBranchDropdown = toggleBranchDropdown;
(window as any).switchBranch = switchBranch;
(window as any).toggleWatch = toggleWatch;
(window as any).toggleStar = toggleStar;
(window as any).forkProject = forkProject;
(window as any).toggleAddFileDropdown = toggleAddFileDropdown;
(window as any).toggleCodeDropdown = toggleCodeDropdown;
(window as any).toggleCopyDropdown = toggleCopyDropdown;
(window as any).copyCloneUrl = copyCloneUrl;
(window as any).downloadProjectZip = downloadProjectZip;

})(); // End of IIFE
