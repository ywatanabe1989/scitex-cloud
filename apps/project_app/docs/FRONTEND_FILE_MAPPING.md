# Project App Frontend File Mapping

**Purpose:** Track old → new file paths during refactoring
**Date:** 2025-11-04

---

## Templates Mapping

### Core Pages (Already Top-Level)

| Old Path | New Path | Status |
|----------|----------|--------|
| `list.html` | `list.html` | ✓ No change |
| `create.html` | `create.html` | ✓ No change |
| `edit.html` | `edit.html` | ✓ No change |
| `delete.html` | `delete.html` | ✓ No change |
| `settings.html` | `settings.html` | ✓ No change |

### Browse → Browse (Flatten)

| Old Path | New Path | Status |
|----------|----------|--------|
| `browse/project_root.html` | `browse.html` | ⏳ Rename |
| `browse/subdirectory.html` | `directory_browser.html` | ⏳ Rename |

### Filer → File_* (Flatten + Rename)

| Old Path | New Path | Status |
|----------|----------|--------|
| `filer/view.html` | `file_view.html` | ⏳ Move + Rename |
| `filer/edit.html` | `file_edit.html` | ⏳ Move + Rename |
| `filer/history.html` | `file_history.html` | ⏳ Move + Rename |
| `filer/browser.html` | `file_browser.html` | ⏳ Move + Rename |
| `filer/directory.html` | `file_directory.html` | ⏳ Move + Rename |

### Issues (Flatten)

| Old Path | New Path | Status |
|----------|----------|--------|
| `issues/issues_list.html` | `issues_list.html` | ⏳ Move |
| `issues/issue_detail.html` | `issues_detail.html` | ⏳ Move |
| `issues/issue_form.html` | `issues_form.html` | ⏳ Move |
| `issues/label_manage.html` | `issues_label_manage.html` | ⏳ Move |
| `issues/milestone_manage.html` | `issues_milestone_manage.html` | ⏳ Move |

### Pull Requests (Flatten)

| Old Path | New Path | Status |
|----------|----------|--------|
| `pull_requests/pr_list.html` | `pr_list.html` | ⏳ Move |
| `pull_requests/pr_detail.html` | `pr_detail.html` | ⏳ Move |
| `pull_requests/pr_form.html` | `pr_form.html` | ⏳ Move |

### Actions (Flatten)

| Old Path | New Path | Status |
|----------|----------|--------|
| `actions/actions_list.html` | `actions_list.html` | ⏳ Move |
| `actions/workflow_detail.html` | `workflow_detail.html` | ⏳ Move |
| `actions/workflow_editor.html` | `workflow_editor.html` | ⏳ Move |
| `actions/workflow_run_detail.html` | `workflow_run_detail.html` | ⏳ Move |
| `actions/workflow_delete_confirm.html` | `workflow_delete_confirm.html` | ⏳ Move |

### Security (Flatten)

| Old Path | New Path | Status |
|----------|----------|--------|
| `security/security_overview.html` | `security_overview.html` | ⏳ Move |
| `security/security_alerts.html` | `security_alerts.html` | ⏳ Move |
| `security/security_alert_detail.html` | `security_alert_detail.html` | ⏳ Move |
| `security/security_advisories.html` | `security_advisories.html` | ⏳ Move |
| `security/scan_history.html` | `security_scan_history.html` | ⏳ Move |
| `security/security_policy.html` | `security_policy.html` | ⏳ Move |
| `security/dependency_graph.html` | `security_dependency_graph.html` | ⏳ Move |

### Commits (Flatten)

| Old Path | New Path | Status |
|----------|----------|--------|
| `commits/detail.html` | `commit_detail.html` | ⏳ Move |

### Users (Flatten)

| Old Path | New Path | Status |
|----------|----------|--------|
| `users/bio.html` | `user_bio.html` | ⏳ Move |
| `users/projects.html` | `user_projects.html` | ⏳ Move |
| `users/board.html` | `user_board.html` | ⏳ Move |
| `users/overview.html` | `user_overview.html` | ⏳ Move |
| `users/stars.html` | `user_stars.html` | ⏳ Move |

### Admin (Add Prefix)

| Old Path | New Path | Status |
|----------|----------|--------|
| `repository_maintenance.html` | `admin_repository_maintenance.html` | ⏳ Rename |

---

## Partials Directories Mapping

### Create New Directories

| Directory | Purpose | Status |
|-----------|---------|--------|
| `list_partials/` | For list.html | ⏳ Create |
| `create_partials/` | For create.html | ⏳ Create |
| `edit_partials/` | For edit.html | ⏳ Create |
| `delete_partials/` | For delete.html | ⏳ Create |
| `settings_partials/` | For settings.html | ⏳ Create |
| `browse_partials/` | For browse.html | ⏳ Create |
| `file_view_partials/` | For file_view.html | ⏳ Create |
| `file_edit_partials/` | For file_edit.html | ⏳ Create |
| `file_history_partials/` | For file_history.html | ⏳ Create |
| `issues_list_partials/` | For issues_list.html | ⏳ Create |
| `issues_detail_partials/` | For issues_detail.html | ⏳ Create |
| `issues_form_partials/` | For issues_form.html | ⏳ Create |
| `pr_list_partials/` | For pr_list.html | ⏳ Create |
| `pr_detail_partials/` | For pr_detail.html | ⏳ Create |
| `pr_form_partials/` | For pr_form.html | ⏳ Create |
| `actions_list_partials/` | For actions_list.html | ⏳ Create |
| `workflow_detail_partials/` | For workflow_detail.html | ⏳ Create |
| `workflow_editor_partials/` | For workflow_editor.html | ⏳ Create |
| `workflow_run_detail_partials/` | For workflow_run_detail.html | ⏳ Create |
| `security_overview_partials/` | For security_overview.html | ⏳ Create |
| `security_alerts_partials/` | For security_alerts.html | ⏳ Create |
| `security_alert_detail_partials/` | For security_alert_detail.html | ⏳ Create |
| `commit_detail_partials/` | For commit_detail.html | ⏳ Create |
| `user_profile_partials/` | For user_profile.html | ⏳ Create |
| `user_bio_partials/` | For user_bio.html | ⏳ Create |
| `admin_repository_maintenance_partials/` | For admin_repository_maintenance.html | ⏳ Create |

### Remove Old Directories

| Directory | Action | Status |
|-----------|--------|--------|
| `browse/partials/` | Merge into browse_partials/ | ⏳ Delete |
| `issues/partials/` | Merge into issues_*_partials/ | ⏳ Delete |
| `pull_requests/partials/` | Merge into pr_*_partials/ | ⏳ Delete |
| `actions/partials/` | Merge into workflow_*_partials/ | ⏳ Delete |
| `security/partials/` | Merge into security_*_partials/ | ⏳ Delete |
| `partials/` | Distribute to specific _partials/ | ⏳ Delete |

---

## CSS Mapping

### Top-Level CSS Files

| Old Path | New Path | Status |
|----------|----------|--------|
| `common.css` | `common.css` | ✓ No change |
| `variables.css` | `variables.css` | ✓ No change |
| `project_app.css` | `project_app.css` | ✓ No change |

### Pages Directory → Top Level

| Old Path | New Path | Status |
|----------|----------|--------|
| `pages/create.css` | `create.css` | ⏳ Move |
| `pages/delete.css` | `delete.css` | ⏳ Move |
| `pages/detail.css` | `browse.css` | ⏳ Move + Rename |
| `pages/edit.css` | `edit.css` | ⏳ Move |
| `pages/list.css` | `list.css` | ⏳ Move |
| `pages/settings.css` | `settings.css` | ⏳ Move |

### Feature Directories → Top Level (Hyphenate)

| Old Path | New Path | Status |
|----------|----------|--------|
| `actions/list.css` | `actions-list.css` | ⏳ Move + Hyphenate |
| `actions/workflow-detail.css` | `workflow-detail.css` | ⏳ Move |
| `actions/workflow-editor.css` | `workflow-editor.css` | ⏳ Move |
| `actions/workflow-run-detail.css` | `workflow-run-detail.css` | ⏳ Move |
| `commits/detail.css` | `commit-detail.css` | ⏳ Move + Hyphenate |
| `filer/browser.css` | `file-browser.css` | ⏳ Move + Hyphenate |
| `filer/edit.css` | `file-edit.css` | ⏳ Move + Hyphenate |
| `filer/history.css` | `file-history.css` | ⏳ Move + Hyphenate |
| `filer/view.css` | `file-view.css` | ⏳ Move + Hyphenate |
| `issues/detail.css` | `issues-detail.css` | ⏳ Move + Hyphenate |
| `issues/list.css` | `issues-list.css` | ⏳ Move + Hyphenate |
| `pull_requests/pr-detail.css` | `pr-detail.css` | ⏳ Move |
| `pull_requests/pr-list.css` | `pr-list.css` | ⏳ Move |
| `security/security.css` | `security-overview.css` | ⏳ Move + Rename |
| `users/bio.css` | `user-bio.css` | ⏳ Move + Hyphenate |
| `users/profile.css` | `user-profile.css` | ⏳ Move + Hyphenate |

### Components (Keep as-is)

| Old Path | New Path | Status |
|----------|----------|--------|
| `components/badges.css` | `components/badges.css` | ✓ No change |
| `components/buttons.css` | `components/buttons.css` | ✓ No change |
| `components/cards.css` | `components/cards.css` | ✓ No change |
| `components/file-tree.css` | `components/file-tree.css` | ✓ No change |
| `components/forms.css` | `components/forms.css` | ✓ No change |
| `components/icons.css` | `components/icons.css` | ✓ No change |
| `components/sidebar.css` | `components/sidebar.css` | ✓ No change |
| `components/tables.css` | `components/tables.css` | ✓ No change |

---

## JavaScript Mapping

### Rename (Underscore → Hyphen)

| Old Path | New Path | Status |
|----------|----------|--------|
| `file_browser.js` | `file-browser.js` | ⏳ Rename |
| `file_edit.js` | `file-edit.js` | ⏳ Rename |
| `file_history.js` | `file-history.js` | ⏳ Rename |
| `issue_detail.js` | `issues-detail.js` | ⏳ Rename |
| `pr_conversation.js` | `pr-conversation.js` | ⏳ Rename |
| `pr_detail.js` | `pr-detail.js` | ⏳ Rename |
| `pr_form.js` | `pr-form.js` | ⏳ Rename |
| `security_alert_detail.js` | `security-alert-detail.js` | ⏳ Rename |
| `security_scan.js` | `security-scan.js` | ⏳ Rename |
| `sidebar_improvements.js` | `sidebar-improvements.js` | ⏳ Rename |
| `workflow_detail.js` | `workflow-detail.js` | ⏳ Rename |
| `workflow_editor.js` | `workflow-editor.js` | ⏳ Rename |
| `workflow_run_detail.js` | `workflow-run-detail.js` | ⏳ Rename |

### Keep (Already Correct)

| Old Path | New Path | Status |
|----------|----------|--------|
| `project-create.js` | `project-create.js` | ✓ No change |
| `project-detail.js` | `project-detail.js` | ✓ No change |
| `file-view.js` | `file-view.js` | ✓ No change |
| `pdf-viewer.js` | `pdf-viewer.js` | ✓ No change |
| `icons.js` | `icons.js` | ✓ No change |
| `settings.js` | `settings.js` | ✓ No change |
| `profile.js` | `profile.js` | ✓ No change |
| `project_app.js` | `project_app.js` | ✓ No change |

---

## Status Legend

- ✓ No change needed
- ⏳ Pending migration
- ✅ Completed
- ❌ Issue/blocked

---

## Progress Tracking

### Templates
- [ ] Core pages (5 files)
- [ ] Browse/filer (6 files)
- [ ] Issues (5 files)
- [ ] Pull requests (3 files)
- [ ] Actions (5 files)
- [ ] Security (7 files)
- [ ] Commits (1 file)
- [ ] Users (5 files)
- [ ] Admin (1 file)
- [ ] Partials directories (25+ directories)

### CSS
- [ ] Pages (6 files)
- [ ] Actions (4 files)
- [ ] Commits (1 file)
- [ ] Filer (4 files)
- [ ] Issues (2 files)
- [ ] Pull requests (2 files)
- [ ] Security (1 file)
- [ ] Users (2 files)

### JavaScript
- [ ] Rename 13 files
- [ ] Update template references (13 files)

---

**Total Files to Process:**
- Templates: ~40 main files + ~100 partials = 140 files
- CSS: ~25 files
- JavaScript: ~13 files
- **Total: ~180 files**

<!-- EOF -->
