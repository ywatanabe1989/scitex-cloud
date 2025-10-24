/**
 * project_app.js - Consolidated JavaScript for project_app
 *
 * This file contains all JavaScript functionality previously scattered across
 * inline <script> blocks in various templates.
 *
 * Organization:
 * 1. Sidebar Management (from project_detail.html)
 * 2. File Tree Management (from project_detail.html, project_directory.html)
 * 3. Project Actions (Watch/Star/Fork from project_detail.html)
 * 4. Project Forms (from project_create.html, project_settings.html, project_delete.html)
 * 5. File Management (from project_files.html, project_file_view.html, project_file_edit.html)
 * 6. Directory Operations (from project_directory.html)
 * 7. User Profile (from user_project_list.html)
 * 8. Utility Functions
 */

// =============================================================================
// 1. SIDEBAR MANAGEMENT
// =============================================================================

const SIDEBAR_STATE_KEY = 'scitex-sidebar-state';
const SIDEBAR_SECTIONS_KEY = 'scitex-sidebar-sections';

/**
 * Initialize sidebar state from localStorage
 */
function initializeSidebar() {
    const sidebar = document.getElementById('repo-sidebar');
    const repoLayout = document.getElementById('repo-layout');
    const toggleBtn = document.getElementById('sidebar-toggle');

    if (!sidebar || !repoLayout) return;

    const savedState = localStorage.getItem(SIDEBAR_STATE_KEY);
    console.log('Initializing sidebar. Saved state:', savedState);

    // Always start collapsed by default (per GitHub style)
    sidebar.classList.add('collapsed');
    repoLayout.classList.add('sidebar-collapsed');
    if (toggleBtn) {
        toggleBtn.setAttribute('title', 'Expand sidebar');
    }
    console.log('Sidebar initialized as collapsed (default)');

    // Clear the expanded state if it was saved
    if (savedState === 'expanded') {
        localStorage.setItem(SIDEBAR_STATE_KEY, 'collapsed');
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

/**
 * Toggle entire sidebar expansion/collapse
 */
function toggleSidebar() {
    const sidebar = document.getElementById('repo-sidebar');
    const repoLayout = document.getElementById('repo-layout');
    const toggleBtn = document.getElementById('sidebar-toggle');

    if (!sidebar || !repoLayout) return;

    if (sidebar.classList.contains('collapsed')) {
        // Expand sidebar
        sidebar.classList.remove('collapsed');
        sidebar.classList.add('expanded');
        repoLayout.classList.remove('sidebar-collapsed');
        repoLayout.classList.add('sidebar-expanded');
        localStorage.setItem(SIDEBAR_STATE_KEY, 'expanded');
        if (toggleBtn) {
            toggleBtn.setAttribute('title', 'Collapse sidebar');
        }
        console.log('Sidebar expanded');
    } else {
        // Collapse sidebar
        sidebar.classList.remove('expanded');
        sidebar.classList.add('collapsed');
        repoLayout.classList.remove('sidebar-expanded');
        repoLayout.classList.add('sidebar-collapsed');
        localStorage.setItem(SIDEBAR_STATE_KEY, 'collapsed');
        if (toggleBtn) {
            toggleBtn.setAttribute('title', 'Expand sidebar');
        }
        console.log('Sidebar collapsed');
    }
}

/**
 * Toggle individual sidebar section
 */
function toggleSidebarSection(sectionId) {
    const sidebar = document.getElementById('repo-sidebar');

    if (!sidebar) return;

    // Don't toggle sections when sidebar is collapsed
    if (sidebar.classList.contains('collapsed')) {
        return;
    }

    const section = document.getElementById(sectionId);
    if (!section) return;

    section.classList.toggle('section-collapsed');
    saveSectionStates();
}

/**
 * Save all section states to localStorage
 */
function saveSectionStates() {
    const fileTreeSection = document.getElementById('file-tree-section');
    const aboutSection = document.getElementById('about-section');

    if (!fileTreeSection && !aboutSection) return;

    const sections = {};
    if (fileTreeSection) {
        sections['file-tree-section'] = fileTreeSection.classList.contains('section-collapsed') ? 'collapsed' : 'expanded';
    }
    if (aboutSection) {
        sections['about-section'] = aboutSection.classList.contains('section-collapsed') ? 'collapsed' : 'expanded';
    }

    localStorage.setItem(SIDEBAR_SECTIONS_KEY, JSON.stringify(sections));
}

// =============================================================================
// 2. FILE TREE MANAGEMENT
// =============================================================================

/**
 * Load file tree from API and render it in sidebar
 */
async function loadFileTree() {
    const treeContainer = document.getElementById('file-tree');
    if (!treeContainer) return;

    // Extract project info from page URL
    const pathParts = window.location.pathname.split('/').filter(x => x);
    if (pathParts.length < 2) return;

    const username = pathParts[0];
    const slug = pathParts[1];

    try {
        const response = await fetch(`/${username}/${slug}/api/file-tree/`);
        const data = await response.json();

        if (data.success) {
            treeContainer.innerHTML = buildTreeHTML(data.tree, username, slug);
        } else {
            treeContainer.innerHTML = '<div style="color: var(--color-fg-muted); padding: 0.5rem;">Error loading file tree</div>';
        }
    } catch (err) {
        console.error('Failed to load file tree:', err);
        treeContainer.innerHTML = '<div style="color: var(--color-fg-muted); padding: 0.5rem;">Error loading file tree</div>';
    }
}

/**
 * Build HTML for file tree recursively
 */
function buildTreeHTML(items, username, slug, level = 0) {
    let html = '';
    const indent = level * 16;
    const currentPath = window.location.pathname;

    items.forEach((item) => {
        const itemPath = `/${username}/${slug}/${item.path}${item.type === 'directory' ? '/' : ''}`;
        const isActive = currentPath.includes(item.path);
        const iconFolder = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" class="icon-folder"><path fill="currentColor" d="M1.75 1A1.75 1.75 0 0 0 0 2.75v10.5C0 14.216.784 15 1.75 15h12.5A1.75 1.75 0 0 0 16 13.25v-8.5A1.75 1.75 0 0 0 14.25 3H7.5a.25.25 0 0 1-.2-.1l-.9-1.2C6.07 1.26 5.55 1 5 1H1.75Z"></path></svg>';
        const iconFile = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" class="icon-file"><path fill="currentColor" d="M2 1.75C2 .784 2.784 0 3.75 0h6.586c.464 0 .909.184 1.237.513l2.914 2.914c.329.328.513.773.513 1.237v9.586A1.75 1.75 0 0 1 13.25 16h-9.5A1.75 1.75 0 0 1 2 14.25Zm1.75-.25a.25.25 0 0 0-.25.25v12.5c0 .138.112.25.25.25h9.5a.25.25 0 0 0 .25-.25V6h-2.75A1.75 1.75 0 0 1 9 4.25V1.5Zm6.75.062V4.25c0 .138.112.25.25.25h2.688l-.011-.013-2.914-2.914-.013-.011Z"></path></svg>';
        const icon = item.type === 'directory' ? iconFolder : iconFile;
        const hasChildren = item.children && item.children.length > 0;
        const itemId = `tree-${item.path.replace(/\//g, '-')}`;

        // Item row
        html += `<div class="file-tree-item ${isActive ? 'active' : ''}" style="padding-left: ${indent}px;">`;

        if (item.type === 'directory') {
            html += `<a href="${itemPath}" class="file-tree-folder" style="text-decoration: none; color: var(--color-fg-default);">`;

            // Chevron for folders with children
            if (hasChildren) {
                html += `<span class="file-tree-chevron ${level === 0 ? 'expanded' : ''}" onclick="toggleFolder('${itemId}'); return false;">▸</span>`;
            } else {
                html += `<span style="width: 12px; display: inline-block;"></span>`;
            }

            html += `<span class="file-tree-icon">${icon}</span><span>${item.name}</span>`;
            html += `</a>`;
        } else {
            html += `<a href="/${username}/${slug}/blob/${item.path}" class="file-tree-file" style="text-decoration: none; color: var(--color-fg-muted);">`;
            html += `<span style="width: 12px; display: inline-block;"></span>`;
            html += `<span class="file-tree-icon">${icon}</span><span>${item.name}</span>`;
            html += `</a>`;
        }

        html += `</div>`;

        // Children container - render ALL children
        if (hasChildren) {
            const isExpanded = level === 0;  // Auto-expand root level only
            html += `<div id="${itemId}" class="file-tree-children ${isExpanded ? 'expanded' : ''}">`;
            html += buildTreeHTML(item.children, username, slug, level + 1);
            html += `</div>`;
        }
    });

    return html;
}

/**
 * Toggle folder expansion in file tree
 */
function toggleFolder(folderId) {
    const folder = document.getElementById(folderId);
    if (!folder) return;

    const chevron = event.target;

    if (folder.classList.contains('expanded')) {
        folder.classList.remove('expanded');
        chevron.classList.remove('expanded');
    } else {
        folder.classList.add('expanded');
        chevron.classList.add('expanded');
    }

    event.stopPropagation();
    event.preventDefault();
}

// =============================================================================
// 3. PROJECT ACTIONS (Watch/Star/Fork)
// =============================================================================

/**
 * Load project statistics (watch/star/fork counts)
 */
async function loadProjectStats() {
    const watchCount = document.getElementById('watch-count');
    const starCount = document.getElementById('star-count');
    const forkCount = document.getElementById('fork-count');
    const sidebarStarCount = document.getElementById('sidebar-star-count');
    const sidebarForkCount = document.getElementById('sidebar-fork-count');

    if (!watchCount && !starCount && !forkCount) return;

    // Extract project info from page URL
    const pathParts = window.location.pathname.split('/').filter(x => x);
    if (pathParts.length < 2) return;

    const username = pathParts[0];
    const slug = pathParts[1];

    try {
        const response = await fetch(`/${username}/${slug}/api/stats/`);
        const data = await response.json();

        if (data.success) {
            // Update counts
            if (watchCount) watchCount.textContent = data.stats.watch_count;
            if (starCount) starCount.textContent = data.stats.star_count;
            if (forkCount) forkCount.textContent = data.stats.fork_count;

            // Update sidebar counts
            if (sidebarStarCount) {
                sidebarStarCount.textContent = `${data.stats.star_count} ${data.stats.star_count === 1 ? 'star' : 'stars'}`;
            }
            if (sidebarForkCount) {
                sidebarForkCount.textContent = `${data.stats.fork_count} ${data.stats.fork_count === 1 ? 'fork' : 'forks'}`;
            }

            // Update button states
            const watchBtn = document.getElementById('watch-btn');
            const starBtn = document.getElementById('star-btn');

            if (watchBtn && data.user_status.is_watching) {
                watchBtn.classList.add('active');
            }
            if (starBtn && data.user_status.is_starred) {
                starBtn.classList.add('active');
            }
        }
    } catch (error) {
        console.error('Failed to load project stats:', error);
    }
}

/**
 * Handle watch button click
 */
async function handleWatch(event) {
    const btn = event.currentTarget;
    const pathParts = window.location.pathname.split('/').filter(x => x);
    if (pathParts.length < 2) return;

    const username = pathParts[0];
    const slug = pathParts[1];

    try {
        const response = await fetch(`/${username}/${slug}/api/watch/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        const data = await response.json();

        if (data.success) {
            if (data.is_watching) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }

            const watchCount = document.getElementById('watch-count');
            if (watchCount) {
                watchCount.textContent = data.watch_count;
            }

            showNotification(data.message, 'success');
        } else {
            showNotification(data.error || 'Failed to update watch status', 'error');
        }
    } catch (error) {
        console.error('Error toggling watch:', error);
        showNotification('Failed to update watch status', 'error');
    }
}

/**
 * Handle star button click
 */
async function handleStar(event) {
    const btn = event.currentTarget;
    const pathParts = window.location.pathname.split('/').filter(x => x);
    if (pathParts.length < 2) return;

    const username = pathParts[0];
    const slug = pathParts[1];

    try {
        const response = await fetch(`/${username}/${slug}/api/star/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        const data = await response.json();

        if (data.success) {
            if (data.is_starred) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }

            const starCount = document.getElementById('star-count');
            if (starCount) {
                starCount.textContent = data.star_count;
            }

            showNotification(data.message, 'success');
        } else {
            showNotification(data.error || 'Failed to update star status', 'error');
        }
    } catch (error) {
        console.error('Error toggling star:', error);
        showNotification('Failed to update star status', 'error');
    }
}

/**
 * Handle fork button click
 */
async function handleFork(event) {
    if (!confirm('Fork this repository? This will create a copy under your account.')) {
        return;
    }

    const btn = event.currentTarget;
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span>Forking...</span>';

    const pathParts = window.location.pathname.split('/').filter(x => x);
    if (pathParts.length < 2) return;

    const username = pathParts[0];
    const slug = pathParts[1];

    try {
        const response = await fetch(`/${username}/${slug}/api/fork/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        const data = await response.json();

        if (data.success) {
            const forkCount = document.getElementById('fork-count');
            if (forkCount) {
                forkCount.textContent = data.fork_count;
            }

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

// =============================================================================
// 4. PROJECT FORMS (Create/Settings/Delete)
// =============================================================================

/**
 * Initialize project create form
 */
function initProjectCreateForm() {
    const nameInput = document.getElementById('name');
    const form = document.querySelector('form');
    const submitButton = document.querySelector('.btn-primary');
    const initTypeRadios = document.querySelectorAll('input[name="init_type"]');
    const githubUrlInput = document.getElementById('github_url_input');
    const githubUrlField = document.getElementById('github_url');

    if (!nameInput) return;

    let nameCheckTimeout;
    let isNameAvailable = false;

    // Real-time name availability checking
    nameInput.addEventListener('input', function() {
        const name = this.value.trim();
        const availabilityDiv = document.getElementById('name-availability');
        const availabilityIcon = document.getElementById('availability-icon');
        const availabilityMessage = document.getElementById('availability-message');

        clearTimeout(nameCheckTimeout);

        if (!name) {
            if (availabilityDiv) availabilityDiv.style.display = 'none';
            isNameAvailable = false;
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.style.opacity = '0.5';
                submitButton.style.cursor = 'not-allowed';
            }
            return;
        }

        isNameAvailable = false;
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.style.opacity = '0.5';
            submitButton.style.cursor = 'not-allowed';
        }

        if (availabilityDiv) {
            availabilityDiv.style.display = 'block';
            if (availabilityIcon) availabilityIcon.textContent = '⏳';
            if (availabilityMessage) {
                availabilityMessage.textContent = ' Checking availability...';
                availabilityMessage.style.color = '#666';
            }
        }

        nameCheckTimeout = setTimeout(async () => {
            try {
                const response = await fetch(`/project/api/check-name/?name=${encodeURIComponent(name)}`);
                const data = await response.json();

                if (data.available) {
                    isNameAvailable = true;
                    if (availabilityIcon) availabilityIcon.textContent = '✓';
                    if (availabilityMessage) {
                        availabilityMessage.textContent = ' ' + data.message;
                        availabilityMessage.style.color = '#28a745';
                    }
                    if (submitButton) {
                        submitButton.disabled = false;
                        submitButton.style.opacity = '1';
                        submitButton.style.cursor = 'pointer';
                    }
                } else {
                    isNameAvailable = false;
                    if (availabilityIcon) availabilityIcon.textContent = '✗';
                    if (availabilityMessage) {
                        availabilityMessage.textContent = ' ' + data.message;
                        availabilityMessage.style.color = '#dc3545';
                    }
                    if (submitButton) {
                        submitButton.disabled = true;
                        submitButton.style.opacity = '0.5';
                        submitButton.style.cursor = 'not-allowed';
                    }
                }
            } catch (error) {
                console.error('Error checking name availability:', error);
                if (availabilityDiv) availabilityDiv.style.display = 'none';
            }
        }, 500);
    });

    // Prevent form submission if name is not available
    if (form) {
        form.addEventListener('submit', function(e) {
            const name = nameInput.value.trim();
            if (!name) {
                e.preventDefault();
                alert('Please enter a project name');
                return false;
            }
            if (!isNameAvailable) {
                e.preventDefault();
                alert('Please choose an available project name. The current name is already taken or invalid.');
                return false;
            }
        });
    }

    // Handle initialization type selection
    initTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (githubUrlInput) githubUrlInput.style.display = 'none';

            if (this.value === 'github') {
                if (githubUrlInput && githubUrlField) {
                    githubUrlInput.style.display = 'block';
                    githubUrlField.setAttribute('required', 'required');
                }
            } else {
                if (githubUrlField) githubUrlField.removeAttribute('required');
            }
        });
    });

    // Auto-fill name from Git URL
    if (githubUrlField) {
        githubUrlField.addEventListener('blur', function() {
            const url = this.value.trim();
            if (url && !nameInput.value.trim()) {
                const repoName = extractRepoNameFromUrl(url);
                if (repoName) {
                    nameInput.value = repoName;
                    nameInput.dispatchEvent(new Event('input'));
                }
            }
        });
    }

    // Aggressive autofill prevention
    nameInput.setAttribute('readonly', 'readonly');

    const clearAutofill = function() {
        if (nameInput.value && nameInput.matches(':-webkit-autofill')) {
            nameInput.value = '';
        }
    };

    setTimeout(clearAutofill, 50);
    setTimeout(clearAutofill, 100);
    setTimeout(clearAutofill, 200);

    nameInput.addEventListener('focus', function() {
        nameInput.removeAttribute('readonly');
    }, { once: true });

    nameInput.addEventListener('click', function() {
        nameInput.removeAttribute('readonly');
    }, { once: true });

    setTimeout(function() {
        nameInput.removeAttribute('readonly');
    }, 500);
}

/**
 * Extract repository name from URL
 */
function extractRepoNameFromUrl(url) {
    if (!url) return '';
    url = url.trim();
    if (url.endsWith('.git')) {
        url = url.slice(0, -4);
    }
    const parts = url.replace(/\/$/, '').split('/');
    return parts[parts.length - 1] || '';
}

/**
 * Initialize project settings form
 */
function initProjectSettingsForm() {
    // Radio button selection visual feedback
    document.querySelectorAll('.radio-option input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', function() {
            document.querySelectorAll('.radio-option').forEach(opt => opt.classList.remove('selected'));
            this.closest('.radio-option').classList.add('selected');
        });
    });

    // Delete modal functions
    const deleteModal = document.getElementById('deleteModal');
    const deleteConfirmInput = document.getElementById('deleteConfirmInput');
    const deleteConfirmButton = document.getElementById('deleteConfirmButton');

    if (deleteModal && deleteConfirmInput && deleteConfirmButton) {
        // Check delete input
        deleteConfirmInput.addEventListener('input', function() {
            const expectedValue = this.getAttribute('data-expected-value') || '';
            if (this.value === expectedValue) {
                deleteConfirmButton.disabled = false;
                deleteConfirmButton.style.opacity = '1';
            } else {
                deleteConfirmButton.disabled = true;
                deleteConfirmButton.style.opacity = '0.5';
            }
        });
    }

    // Close modal on ESC key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && deleteModal) {
            hideDeleteModal();
        }
    });

    // Add collaborator button feedback
    const addCollaboratorBtn = document.getElementById('addCollaboratorBtn');
    const collaboratorUsername = document.getElementById('collaboratorUsername');
    const addBtnText = document.getElementById('addBtnText');

    if (addCollaboratorBtn && collaboratorUsername && addBtnText) {
        addCollaboratorBtn.addEventListener('click', function(e) {
            const username = collaboratorUsername.value.trim();
            if (username) {
                addBtnText.textContent = 'Adding...';
                addCollaboratorBtn.disabled = true;
                addCollaboratorBtn.style.opacity = '0.7';
                console.log('Adding collaborator:', username);
            } else {
                e.preventDefault();
                alert('Please enter a username');
            }
        });

        collaboratorUsername.addEventListener('input', function() {
            if (addCollaboratorBtn.disabled) {
                addBtnText.textContent = 'Add collaborator';
                addCollaboratorBtn.disabled = false;
                addCollaboratorBtn.style.opacity = '1';
            }
        });
    }
}

/**
 * Show delete modal
 */
function showDeleteModal() {
    const modal = document.getElementById('deleteModal');
    if (modal) {
        modal.style.display = 'flex';
        const deleteConfirmInput = document.getElementById('deleteConfirmInput');
        const deleteConfirmButton = document.getElementById('deleteConfirmButton');
        if (deleteConfirmInput) deleteConfirmInput.value = '';
        if (deleteConfirmButton) deleteConfirmButton.disabled = true;
    }
}

/**
 * Hide delete modal
 */
function hideDeleteModal() {
    const modal = document.getElementById('deleteModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * Submit delete form
 */
function submitDelete() {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = window.location.href;

    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const actionInput = document.createElement('input');
    actionInput.type = 'hidden';
    actionInput.name = 'action';
    actionInput.value = 'delete_repository';

    form.appendChild(csrfInput);
    form.appendChild(actionInput);
    document.body.appendChild(form);
    form.submit();
}

/**
 * Initialize project delete form
 */
function initProjectDeleteForm() {
    const confirmText = document.getElementById('confirmText');
    const deleteBtn = document.getElementById('deleteBtn');

    if (!confirmText || !deleteBtn) return;

    const expectedText = deleteBtn.getAttribute('data-expected-text') || '';

    confirmText.addEventListener('input', function() {
        if (this.value === expectedText) {
            deleteBtn.disabled = false;
            deleteBtn.style.opacity = '1';
            deleteBtn.style.cursor = 'pointer';
        } else {
            deleteBtn.disabled = true;
            deleteBtn.style.opacity = '0.5';
            deleteBtn.style.cursor = 'not-allowed';
        }
    });
}

// =============================================================================
// 5. FILE MANAGEMENT
// =============================================================================

/**
 * Handle file upload
 */
function handleFileUpload(event) {
    const files = event.target.files;
    if (files.length > 0) {
        alert(`Selected ${files.length} file(s) for upload. Upload functionality to be implemented.`);
    }
}

/**
 * Create new folder
 */
function createFolder() {
    const folderName = prompt('Enter folder name:');
    if (folderName && folderName.trim()) {
        alert(`Creating folder: ${folderName}`);
    }
}

/**
 * Refresh files list
 */
function refreshFiles() {
    location.reload();
}

/**
 * Open file or folder
 */
function openFile(fileName) {
    alert(`Opening: ${fileName}`);
}

/**
 * Copy file content to clipboard
 */
function copyToClipboard() {
    const content = document.querySelector('.file-content')?.innerText ||
                   document.querySelector('.markdown-body')?.innerText || '';

    navigator.clipboard.writeText(content).then(() => {
        const btn = event.target;
        const originalText = btn.innerHTML;
        btn.innerHTML = '✓ Copied!';
        setTimeout(() => { btn.innerHTML = originalText; }, 2000);
    }).catch(err => {
        alert('Failed to copy: ' + err);
    });
}

/**
 * Show markdown code view
 */
function showCode() {
    const preview = document.getElementById('markdownPreview');
    const code = document.getElementById('markdownCode');
    const codeBtn = document.getElementById('codeBtn');
    const previewBtn = document.getElementById('previewBtn');

    if (preview && code && codeBtn && previewBtn) {
        preview.style.display = 'none';
        code.style.display = 'block';
        codeBtn.classList.add('active');
        previewBtn.classList.remove('active');
    }
}

/**
 * Show markdown preview
 */
function showPreview() {
    const preview = document.getElementById('markdownPreview');
    const code = document.getElementById('markdownCode');
    const codeBtn = document.getElementById('codeBtn');
    const previewBtn = document.getElementById('previewBtn');

    if (preview && code && codeBtn && previewBtn) {
        preview.style.display = 'block';
        code.style.display = 'none';
        codeBtn.classList.remove('active');
        previewBtn.classList.add('active');
    }
}

/**
 * Show markdown edit view (for file editor)
 */
function showEdit() {
    const textarea = document.getElementById('editorTextarea');
    const previewContainer = document.getElementById('previewContainer');
    const editBtn = document.getElementById('editBtn');
    const previewBtn = document.getElementById('previewBtn');

    if (textarea && previewContainer && editBtn && previewBtn) {
        textarea.style.display = 'block';
        previewContainer.style.display = 'none';
        editBtn.classList.add('active');
        previewBtn.classList.remove('active');
    }
}

// =============================================================================
// 6. DIRECTORY OPERATIONS
// =============================================================================

/**
 * Copy entire project/directory content to clipboard
 */
async function copyProjectToClipboard() {
    console.log('copyProjectToClipboard() called');
    const btn = document.getElementById('copy-project-btn');
    if (!btn) return;

    const originalText = btn.innerHTML;
    btn.innerHTML = '⏳ Loading...';
    btn.disabled = true;

    const pathParts = window.location.pathname.split('/').filter(x => x);
    if (pathParts.length < 2) return;

    const username = pathParts[0];
    const slug = pathParts[1];
    const subpath = pathParts.slice(2).join('/');

    try {
        console.log('Fetching concatenated content...');
        const response = await fetch(`/${username}/${slug}/api/concatenate/${subpath}`);
        const data = await response.json();
        console.log('API response:', data);

        if (data.success) {
            await navigator.clipboard.writeText(data.content);
            btn.innerHTML = `✓ Copied ${data.file_count} files!`;
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

/**
 * Download project/directory content as file
 */
async function downloadProjectAsFile() {
    const btn = event.target;
    const originalText = btn.innerHTML;
    btn.innerHTML = '⏳ Preparing download...';

    const pathParts = window.location.pathname.split('/').filter(x => x);
    if (pathParts.length < 2) return;

    const username = pathParts[0];
    const slug = pathParts[1];
    const subpath = pathParts.slice(2).join('/');

    try {
        const response = await fetch(`/${username}/${slug}/api/concatenate/${subpath}`);
        const data = await response.json();

        if (data.success) {
            const blob = new Blob([data.content], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;

            const dirName = subpath.split('/').filter(x => x).pop() || slug;
            a.download = `${dirName}_all_files.txt`;

            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            btn.innerHTML = `✓ Downloaded ${data.file_count} files!`;
            setTimeout(() => {
                btn.innerHTML = originalText;
            }, 3000);
        } else {
            alert('Error: ' + data.error);
            btn.innerHTML = originalText;
        }
    } catch (err) {
        alert('Failed to download: ' + err);
        btn.innerHTML = originalText;
    }
}

/**
 * Toggle branch dropdown
 */
function toggleBranchDropdown(event) {
    if (event) event.stopPropagation();
    const dropdown = document.getElementById('branchDropdown');
    if (dropdown) {
        dropdown.classList.toggle('show');
    }
}

/**
 * Switch to different Git branch
 */
async function switchBranch(branch) {
    console.log('Switching to branch:', branch);

    const pathParts = window.location.pathname.split('/').filter(x => x);
    if (pathParts.length < 2) return;

    const username = pathParts[0];
    const slug = pathParts[1];

    try {
        const response = await fetch(`/${username}/${slug}/api/switch-branch/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ branch: branch })
        });

        const data = await response.json();

        if (data.success) {
            window.location.reload();
        } else {
            alert('Failed to switch branch: ' + data.error);
        }
    } catch (error) {
        console.error('Error switching branch:', error);
        alert('Failed to switch branch: ' + error.message);
    }
}

/**
 * Toggle dropdown menus
 */
function toggleAddFileDropdown() {
    const dropdown = document.getElementById('add-file-dropdown');
    if (dropdown) {
        const isVisible = dropdown.style.display === 'block';
        closeAllDropdowns();
        dropdown.style.display = isVisible ? 'none' : 'block';
    }
}

function toggleCopyDropdown() {
    const dropdown = document.getElementById('copy-dropdown');
    if (dropdown) {
        const isVisible = dropdown.style.display === 'block';
        closeAllDropdowns();
        dropdown.style.display = isVisible ? 'none' : 'block';
    }
}

function toggleCodeDropdown() {
    const dropdown = document.getElementById('code-dropdown');
    if (dropdown) {
        const isVisible = dropdown.style.display === 'block';
        closeAllDropdowns();
        dropdown.style.display = isVisible ? 'none' : 'block';
    }
}

function toggleMoreDropdown() {
    const dropdown = document.getElementById('more-dropdown');
    if (dropdown) {
        const isVisible = dropdown.style.display === 'block';
        closeAllDropdowns();
        dropdown.style.display = isVisible ? 'none' : 'block';
    }
}

function closeAllDropdowns() {
    document.querySelectorAll('.dropdown-menu, .file-browser-toolbar .dropdown-menu').forEach(dropdown => {
        dropdown.style.display = 'none';
    });
}

// =============================================================================
// 7. USER PROFILE
// =============================================================================

/**
 * Repository search in user profile
 */
function initRepoSearch() {
    const searchInput = document.getElementById('repo-search');
    if (!searchInput) return;

    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const repoItems = document.querySelectorAll('.repo-item');

        repoItems.forEach(item => {
            const repoName = item.querySelector('.repo-name')?.textContent.toLowerCase() || '';
            const repoDesc = item.querySelector('.repo-description')?.textContent.toLowerCase() || '';

            if (repoName.includes(searchTerm) || repoDesc.includes(searchTerm)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    });
}

/**
 * Toggle follow/unfollow for user
 */
async function toggleFollow() {
    const btn = document.getElementById('follow-btn');
    if (!btn) return;

    const isFollowing = btn.innerHTML.includes('Following');
    const username = btn.getAttribute('data-username');
    if (!username) return;

    const endpoint = isFollowing
        ? `/social/api/unfollow/${username}/`
        : `/social/api/follow/${username}/`;

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            if (isFollowing) {
                btn.innerHTML = '<i class="fas fa-user-plus"></i> Follow';
            } else {
                btn.innerHTML = '<i class="fas fa-user-check"></i> Following';
            }

            const followerCount = document.querySelector('.profile-stat strong');
            if (followerCount) {
                followerCount.textContent = data.followers_count;
            }
        } else {
            alert(data.error || 'Failed to update follow status');
        }
    } catch (err) {
        console.error('Follow error:', err);
        alert('Failed to update follow status');
    }
}

/**
 * Toggle star/unstar for repository
 */
async function toggleStar(btn) {
    const isStarred = btn.innerHTML.includes('Unstar');
    const username = btn.dataset.username;
    const slug = btn.dataset.slug;

    if (!username || !slug) return;

    const endpoint = isStarred
        ? `/social/api/unstar/${username}/${slug}/`
        : `/social/api/star/${username}/${slug}/`;

    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '⏳ ...';

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            if (isStarred) {
                btn.innerHTML = '⭐ Star';
            } else {
                btn.innerHTML = '⭐ Unstar';
            }
        } else {
            alert(data.error || 'Failed to update star status');
            btn.innerHTML = originalHTML;
        }
    } catch (err) {
        console.error('Star error:', err);
        alert('Failed to update star status');
        btn.innerHTML = originalHTML;
    } finally {
        btn.disabled = false;
    }
}

// =============================================================================
// 8. UTILITY FUNCTIONS
// =============================================================================

/**
 * Get CSRF token from cookies
 */
function getCookie(name) {
    let cookieValue = null;
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

/**
 * Show notification message
 */
function showNotification(message, type = 'info') {
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

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Make table rows clickable
 */
function initClickableRows() {
    const clickableRows = document.querySelectorAll('.clickable-row');
    clickableRows.forEach(row => {
        row.addEventListener('click', function(e) {
            if (e.target.tagName === 'A' || e.target.closest('a')) {
                return;
            }
            const href = this.getAttribute('data-href');
            if (href) {
                window.location.href = href;
            }
        });
    });
}

/**
 * Initialize drag and drop for file upload
 */
function initDragAndDrop() {
    const uploadZone = document.getElementById('upload-zone');
    if (!uploadZone) return;

    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            alert(`Dropped ${files.length} file(s). Upload functionality to be implemented.`);
        }
    });

    uploadZone.addEventListener('click', () => {
        const fileInput = document.getElementById('file-upload');
        if (fileInput) fileInput.click();
    });
}

// =============================================================================
// INITIALIZATION ON PAGE LOAD
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('project_app.js: Initializing...');

    // Initialize sidebar if present
    if (document.getElementById('repo-sidebar')) {
        initializeSidebar();
        loadFileTree();
    }

    // Load project stats if on project detail page
    if (document.getElementById('watch-count') || document.getElementById('star-count')) {
        loadProjectStats();
    }

    // Initialize forms based on page context
    if (document.getElementById('name') && document.getElementById('name-availability')) {
        initProjectCreateForm();
    }

    if (document.querySelector('.radio-option input[type="radio"]')) {
        initProjectSettingsForm();
    }

    if (document.getElementById('confirmText') && document.getElementById('deleteBtn')) {
        initProjectDeleteForm();
    }

    // Initialize clickable rows
    initClickableRows();

    // Initialize drag and drop
    initDragAndDrop();

    // Initialize repository search
    initRepoSearch();

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.btn-group') && !e.target.closest('.file-browser-toolbar .btn-group')) {
            closeAllDropdowns();
        }

        // Close branch dropdown
        const branchDropdown = document.getElementById('branchDropdown');
        const branchSelector = document.querySelector('.branch-selector');
        if (branchDropdown && branchSelector && !branchSelector.contains(e.target)) {
            branchDropdown.classList.remove('show');
        }
    });

    console.log('project_app.js: Initialization complete');
});

// =============================================================================
// EXPOSE FUNCTIONS TO GLOBAL SCOPE (for onclick handlers in templates)
// =============================================================================

// Make key functions available globally for inline onclick handlers
window.toggleSidebar = toggleSidebar;
window.toggleSidebarSection = toggleSidebarSection;
window.toggleFolder = toggleFolder;
window.handleWatch = handleWatch;
window.handleStar = handleStar;
window.handleFork = handleFork;
window.showDeleteModal = showDeleteModal;
window.hideDeleteModal = hideDeleteModal;
window.submitDelete = submitDelete;
window.copyToClipboard = copyToClipboard;
window.showCode = showCode;
window.showPreview = showPreview;
window.showEdit = showEdit;
window.copyProjectToClipboard = copyProjectToClipboard;
window.downloadProjectAsFile = downloadProjectAsFile;
window.toggleBranchDropdown = toggleBranchDropdown;
window.switchBranch = switchBranch;
window.toggleAddFileDropdown = toggleAddFileDropdown;
window.toggleCopyDropdown = toggleCopyDropdown;
window.toggleCodeDropdown = toggleCodeDropdown;
window.toggleMoreDropdown = toggleMoreDropdown;
window.toggleFollow = toggleFollow;
window.toggleStar = toggleStar;
window.handleFileUpload = handleFileUpload;
window.createFolder = createFolder;
window.refreshFiles = refreshFiles;
window.openFile = openFile;
