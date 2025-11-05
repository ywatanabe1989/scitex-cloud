# Project App Frontend Refactoring Plan

**Date:** 2025-11-04
**Goal:** Refactor project_app frontend to follow `/RULES/00_DJANGO_ORGANIZATION_FRONTEND.md`
**Reference:** writer_app structure (successful implementation)

---

## Current State Analysis

### Templates (170 files)

```
templates/project_app/
├── actions/                   # Nested ❌
│   └── partials/              # Generic name ❌
├── browse/                    # Nested ❌
│   └── partials/              # Generic name ❌
├── issues/                    # Nested ❌
├── pull_requests/             # Nested ❌
├── security/                  # Nested ❌
├── commits/
├── users/
├── filer/
├── partials/                  # 66 files, many duplicates ❌
├── create.html                # Good ✓
├── delete.html                # Good ✓
├── edit.html                  # Good ✓
├── settings.html              # Good ✓
└── list.html                  # Good ✓
```

**Problems:**
- ❌ Nested feature directories (browse/, issues/, etc.)
- ❌ Generic "partials/" directories (which page?)
- ❌ 26 duplicate partials in browse/partials/ and partials/
- ❌ Ambiguous filenames (header.html appears multiple times)
- ❌ Hard to search and navigate

### CSS (84 files)

```
static/project_app/css/
├── actions/
├── commits/
├── filer/
├── issues/
├── pull_requests/
├── security/
├── users/
├── pages/
├── components/
└── Many files use underscores ❌
```

### JavaScript (21 files)

```
static/project_app/js/
├── file_browser.js            # Underscore ❌
├── file_edit.js               # Underscore ❌
├── project-create.js          # Hyphen ✓
├── project-detail.js          # Hyphen ✓
└── Mixed naming conventions ❌
```

---

## Target Structure

### Templates (Flat, Explicit)

```
templates/project_app/
├── # ━━━ Core User Pages ━━━
├── browse.html
├── browse_partials/
│   ├── browse_header.html
│   ├── browse_header_partials/
│   │   ├── browse_header_toolbar.html
│   │   └── browse_header_breadcrumb.html
│   ├── browse_file_browser.html
│   ├── browse_sidebar.html
│   ├── browse_readme.html
│   └── browse_empty_state.html
│
├── list.html                  # Already at top ✓
├── list_partials/
│   ├── list_project_card.html
│   ├── list_create_form.html
│   ├── list_pagination.html
│   └── list_empty_state.html
│
├── create.html                # Already at top ✓
├── create_partials/
│   ├── create_breadcrumb.html
│   ├── create_name_field.html
│   ├── create_description_field.html
│   ├── create_init_options.html
│   ├── create_form_actions.html
│   └── create_scripts.html
│
├── edit.html                  # Already at top ✓
├── edit_partials/
│   ├── edit_breadcrumb.html
│   ├── edit_name_field.html
│   ├── edit_description_field.html
│   ├── edit_source_url_field.html
│   └── edit_form_actions.html
│
├── delete.html                # Already at top ✓
├── delete_partials/
│   ├── delete_breadcrumb.html
│   ├── delete_warning_box.html
│   ├── delete_project_info.html
│   ├── delete_consequences_list.html
│   ├── delete_confirmation_form.html
│   └── delete_confirmation_script.html
│
├── settings.html              # Already at top ✓
├── settings_partials/
│   ├── settings_navigation.html
│   ├── settings_general.html
│   ├── settings_visibility.html
│   ├── settings_collaborators.html
│   ├── settings_danger_zone.html
│   └── settings_delete_modal.html
│
├── # ━━━ File Operations ━━━
├── file_view.html
├── file_view_partials/
│   ├── file_view_header.html
│   ├── file_view_breadcrumb.html
│   ├── file_view_tabs.html
│   ├── file_view_commit_info.html
│   ├── file_view_content_code.html
│   ├── file_view_content_text.html
│   ├── file_view_content_markdown.html
│   ├── file_view_content_pdf.html
│   ├── file_view_content_image.html
│   ├── file_view_content_binary.html
│   ├── file_view_scripts.html
│   └── file_view_pdf_scripts.html
│
├── file_edit.html
├── file_edit_partials/
│
├── file_history.html
├── file_history_partials/
│   ├── file_history_header.html
│   ├── file_history_filter_bar.html
│   └── file_history_pagination.html
│
├── directory_browser.html
├── directory_browser_partials/
│
├── # ━━━ Issues (Flattened) ━━━
├── issues_list.html
├── issues_list_partials/
│
├── issues_detail.html
├── issues_detail_partials/
│
├── issues_form.html
├── issues_form_partials/
│
├── issues_label_manage.html
├── issues_milestone_manage.html
│
├── # ━━━ Pull Requests (Flattened) ━━━
├── pr_list.html
├── pr_list_partials/
│   ├── pr_list_header.html
│   ├── pr_list_search.html
│   ├── pr_list_filters.html
│   ├── pr_list_items.html
│   ├── pr_list_pagination.html
│   └── pr_list_empty.html
│
├── pr_detail.html
├── pr_detail_partials/
│   ├── pr_detail_header.html
│   ├── pr_detail_tabs.html
│   ├── pr_detail_conversation.html
│   ├── pr_detail_commits.html
│   ├── pr_detail_diff.html
│   ├── pr_detail_checks.html
│   ├── pr_detail_sidebar.html
│   └── pr_detail_merge_modal.html
│
├── pr_form.html
├── pr_form_partials/
│
├── # ━━━ Actions/Workflows (Flattened) ━━━
├── actions_list.html
├── actions_list_partials/
│
├── workflow_detail.html
├── workflow_detail_partials/
│
├── workflow_editor.html
├── workflow_editor_partials/
│   ├── workflow_editor_breadcrumb.html
│   ├── workflow_editor_form.html
│   └── workflow_editor_templates_sidebar.html
│
├── workflow_run_detail.html
├── workflow_run_detail_partials/
│
├── workflow_delete_confirm.html
│
├── # ━━━ Security (Flattened) ━━━
├── security_overview.html
├── security_overview_partials/
│   ├── security_overview_header.html
│   ├── security_overview_tabs.html
│   ├── security_overview_stats.html
│   ├── security_overview_alerts_card.html
│   └── security_overview_scans_card.html
│
├── security_alerts.html
├── security_alerts_partials/
│
├── security_alert_detail.html
├── security_alert_detail_partials/
│
├── security_advisories.html
├── security_scan_history.html
├── security_policy.html
├── security_dependency_graph.html
│
├── # ━━━ Commits ━━━
├── commit_detail.html
├── commit_detail_partials/
│   ├── commit_detail_header.html
│   └── commit_detail_file_diff.html
│
├── # ━━━ Users ━━━
├── user_profile.html
├── user_profile_partials/
│   ├── user_profile_navigation.html
│   ├── user_profile_sidebar.html
│   └── user_profile_scripts.html
│
├── user_bio.html
├── user_bio_partials/
│   ├── user_bio_header.html
│   └── user_bio_projects.html
│
├── user_projects.html
├── user_board.html
├── user_overview.html
├── user_stars.html
│
└── # ━━━ Admin/Maintenance ━━━
    ├── admin_repository_maintenance.html
    └── admin_repository_maintenance_partials/
```

### CSS (Hyphens, Flat)

```
static/project_app/css/
├── browse.css
├── list.css
├── create.css
├── edit.css
├── delete.css
├── settings.css
├── file-view.css              # Hyphen ✓
├── file-edit.css
├── file-history.css
├── directory-browser.css
├── issues-list.css            # Hyphen ✓
├── issues-detail.css
├── issues-form.css
├── pr-list.css                # Hyphen ✓
├── pr-detail.css
├── pr-form.css
├── actions-list.css
├── workflow-detail.css
├── workflow-editor.css
├── workflow-run-detail.css
├── security-overview.css
├── security-alerts.css
├── security-alert-detail.css
├── commit-detail.css
├── user-profile.css
├── user-bio.css
├── admin-repository-maintenance.css
├── common.css                 # Keep ✓
├── variables.css              # Keep ✓
└── components/                # Keep ✓
    ├── badges.css
    ├── buttons.css
    ├── cards.css
    ├── file-tree.css
    ├── forms.css
    ├── icons.css
    ├── sidebar.css
    └── tables.css
```

### JavaScript (Hyphens, Flat)

```
static/project_app/js/
├── browse.js
├── file-view.js               # Hyphen ✓
├── file-edit.js               # Hyphen ✓
├── file-history.js            # Hyphen ✓
├── project-create.js          # Already correct ✓
├── project-detail.js          # Already correct ✓
├── settings.js
├── profile.js
├── issues-detail.js           # Hyphen ✓
├── pr-detail.js               # Hyphen ✓
├── pr-conversation.js         # Hyphen ✓
├── pr-form.js                 # Hyphen ✓
├── workflow-detail.js         # Hyphen ✓
├── workflow-editor.js         # Hyphen ✓
├── workflow-run-detail.js     # Hyphen ✓
├── security-alert-detail.js   # Hyphen ✓
├── security-scan.js           # Hyphen ✓
├── icons.js                   # Keep ✓
└── pdf-viewer.js              # Keep ✓
```

---

## Migration Steps

### Phase 1: Templates Restructuring

#### Step 1.1: Flatten Feature Directories

```bash
# Move issues templates
mv templates/project_app/issues/issues_list.html templates/project_app/issues_list.html
mv templates/project_app/issues/issue_detail.html templates/project_app/issues_detail.html
mv templates/project_app/issues/issue_form.html templates/project_app/issues_form.html
mv templates/project_app/issues/label_manage.html templates/project_app/issues_label_manage.html
mv templates/project_app/issues/milestone_manage.html templates/project_app/issues_milestone_manage.html

# Move PR templates
mv templates/project_app/pull_requests/pr_list.html templates/project_app/pr_list.html
mv templates/project_app/pull_requests/pr_detail.html templates/project_app/pr_detail.html
mv templates/project_app/pull_requests/pr_form.html templates/project_app/pr_form.html

# Move actions templates
mv templates/project_app/actions/actions_list.html templates/project_app/actions_list.html
mv templates/project_app/actions/workflow_detail.html templates/project_app/workflow_detail.html
mv templates/project_app/actions/workflow_editor.html templates/project_app/workflow_editor.html
mv templates/project_app/actions/workflow_run_detail.html templates/project_app/workflow_run_detail.html
mv templates/project_app/actions/workflow_delete_confirm.html templates/project_app/workflow_delete_confirm.html

# Move security templates
mv templates/project_app/security/security_overview.html templates/project_app/security_overview.html
mv templates/project_app/security/security_alerts.html templates/project_app/security_alerts.html
mv templates/project_app/security/security_alert_detail.html templates/project_app/security_alert_detail.html
mv templates/project_app/security/security_advisories.html templates/project_app/security_advisories.html
mv templates/project_app/security/scan_history.html templates/project_app/security_scan_history.html
mv templates/project_app/security/security_policy.html templates/project_app/security_policy.html
mv templates/project_app/security/dependency_graph.html templates/project_app/security_dependency_graph.html

# Move browse templates
mv templates/project_app/browse/project_root.html templates/project_app/browse.html
mv templates/project_app/browse/subdirectory.html templates/project_app/directory_browser.html

# Move filer templates
mv templates/project_app/filer/view.html templates/project_app/file_view.html
mv templates/project_app/filer/edit.html templates/project_app/file_edit.html
mv templates/project_app/filer/history.html templates/project_app/file_history.html
mv templates/project_app/filer/browser.html templates/project_app/file_browser.html
mv templates/project_app/filer/directory.html templates/project_app/file_directory.html

# Move commits templates
mv templates/project_app/commits/detail.html templates/project_app/commit_detail.html

# Move user templates
mv templates/project_app/users/bio.html templates/project_app/user_bio.html
mv templates/project_app/users/projects.html templates/project_app/user_projects.html
mv templates/project_app/users/board.html templates/project_app/user_board.html
mv templates/project_app/users/overview.html templates/project_app/user_overview.html
mv templates/project_app/users/stars.html templates/project_app/user_stars.html

# Rename admin pages
mv templates/project_app/repository_maintenance.html templates/project_app/admin_repository_maintenance.html
```

#### Step 1.2: Rename Partials Directories

```bash
# Rename feature partials to xxx_partials
mv templates/project_app/issues/partials templates/project_app/issues_list_partials  # temporary
mv templates/project_app/pull_requests/partials templates/project_app/pr_list_partials  # temporary
mv templates/project_app/actions/partials templates/project_app/actions_list_partials  # temporary
mv templates/project_app/security/partials templates/project_app/security_overview_partials  # temporary
mv templates/project_app/browse/partials templates/project_app/browse_partials

# Create partials directories for existing top-level pages
mkdir templates/project_app/list_partials
mkdir templates/project_app/create_partials
mkdir templates/project_app/edit_partials
mkdir templates/project_app/delete_partials
mkdir templates/project_app/settings_partials
```

#### Step 1.3: Move Partials and Add Prefixes

This requires a systematic approach. For each partial:
1. Move to correct `xxx_partials/` directory
2. Rename with `xxx_` prefix

Example for browse partials:
```bash
# browse_partials/
mv partials/_file_list.html browse_partials/browse_file_list.html
mv partials/_file_view_breadcrumb.html browse_partials/browse_file_view_breadcrumb.html
# ... continue for all browse partials
```

#### Step 1.4: Remove Duplicates

Delete duplicate partials that exist in both locations:
```bash
# After moving to browse_partials/, delete from partials/
rm partials/_file_list.html
rm partials/_project_header.html
# ... etc for all 26 duplicates
```

### Phase 2: CSS Restructuring

#### Step 2.1: Flatten CSS Directories

```bash
# Move from feature directories to top level
mv static/project_app/css/actions/list.css static/project_app/css/actions-list.css
mv static/project_app/css/actions/workflow-detail.css static/project_app/css/workflow-detail.css
mv static/project_app/css/actions/workflow-editor.css static/project_app/css/workflow-editor.css
mv static/project_app/css/actions/workflow-run-detail.css static/project_app/css/workflow-run-detail.css

mv static/project_app/css/commits/detail.css static/project_app/css/commit-detail.css

mv static/project_app/css/filer/browser.css static/project_app/css/file-browser.css
mv static/project_app/css/filer/edit.css static/project_app/css/file-edit.css
mv static/project_app/css/filer/history.css static/project_app/css/file-history.css
mv static/project_app/css/filer/view.css static/project_app/css/file-view.css

mv static/project_app/css/issues/list.css static/project_app/css/issues-list.css
mv static/project_app/css/issues/detail.css static/project_app/css/issues-detail.css

mv static/project_app/css/pull_requests/pr-list.css static/project_app/css/pr-list.css
mv static/project_app/css/pull_requests/pr-detail.css static/project_app/css/pr-detail.css

mv static/project_app/css/security/security.css static/project_app/css/security-overview.css

mv static/project_app/css/users/bio.css static/project_app/css/user-bio.css
mv static/project_app/css/users/profile.css static/project_app/css/user-profile.css

mv static/project_app/css/pages/create.css static/project_app/css/create.css
mv static/project_app/css/pages/delete.css static/project_app/css/delete.css
mv static/project_app/css/pages/detail.css static/project_app/css/browse.css
mv static/project_app/css/pages/edit.css static/project_app/css/edit.css
mv static/project_app/css/pages/list.css static/project_app/css/list.css
mv static/project_app/css/pages/settings.css static/project_app/css/settings.css
```

#### Step 2.2: Remove Empty Directories

```bash
rmdir static/project_app/css/actions
rmdir static/project_app/css/commits
rmdir static/project_app/css/filer
rmdir static/project_app/css/issues
rmdir static/project_app/css/pull_requests
rmdir static/project_app/css/security
rmdir static/project_app/css/users
rmdir static/project_app/css/pages
```

### Phase 3: JavaScript Restructuring

#### Step 3.1: Rename JS Files (Underscore → Hyphen)

```bash
# Rename files with underscores to hyphens
mv static/project_app/js/file_browser.js static/project_app/js/file-browser.js
mv static/project_app/js/file_edit.js static/project_app/js/file-edit.js
mv static/project_app/js/file_history.js static/project_app/js/file-history.js
mv static/project_app/js/issue_detail.js static/project_app/js/issues-detail.js
mv static/project_app/js/pr_conversation.js static/project_app/js/pr-conversation.js
mv static/project_app/js/pr_detail.js static/project_app/js/pr-detail.js
mv static/project_app/js/pr_form.js static/project_app/js/pr-form.js
mv static/project_app/js/security_alert_detail.js static/project_app/js/security-alert-detail.js
mv static/project_app/js/security_scan.js static/project_app/js/security-scan.js
mv static/project_app/js/sidebar.js static/project_app/js/sidebar-improvements.js
mv static/project_app/js/workflow_detail.js static/project_app/js/workflow-detail.js
mv static/project_app/js/workflow_editor.js static/project_app/js/workflow-editor.js
mv static/project_app/js/workflow_run_detail.js static/project_app/js/workflow-run-detail.js

# Keep these (already correct)
# project-create.js ✓
# project-detail.js ✓
# file-view.js ✓
# pdf-viewer.js ✓
```

### Phase 4: Update Template References

This is the most critical step - update all `{% include %}` statements:

```django
<!-- Before -->
{% include "project_app/issues/partials/header.html" %}

<!-- After -->
{% include "project_app/issues_list_partials/issues_list_header.html" %}
```

Use find and replace systematically:
```bash
# Find all includes
grep -r "{% include" templates/project_app/*.html

# Update each one following the new naming pattern
```

### Phase 5: Update Static References

Update CSS/JS references in templates:

```django
<!-- Before -->
{% static 'project_app/css/issues/detail.css' %}
{% static 'project_app/js/issue_detail.js' %}

<!-- After -->
{% static 'project_app/css/issues-detail.css' %}
{% static 'project_app/js/issues-detail.js' %}
```

### Phase 6: Cleanup

```bash
# Move backup files to legacy
mkdir templates/project_app/.old
mv templates/project_app/index.html.backup templates/project_app/.old/
mv templates/project_app/legacy/* templates/project_app/.old/
rmdir templates/project_app/legacy

# Remove backup CSS
mv static/project_app/css/project_app.css.backup static/project_app/css/.old/
mv static/project_app/css/pages/detail.css.backup static/project_app/css/.old/

# Remove empty directories
rmdir templates/project_app/browse
rmdir templates/project_app/issues
rmdir templates/project_app/pull_requests
rmdir templates/project_app/actions
rmdir templates/project_app/security
rmdir templates/project_app/commits
rmdir templates/project_app/users
rmdir templates/project_app/filer
```

---

## Testing Checklist

After refactoring, test each page:

### Core Pages
- [ ] `/projects/` - List page
- [ ] `/projects/create/` - Create page
- [ ] `/{username}/{project}/` - Browse page
- [ ] `/{username}/{project}/edit/` - Edit page
- [ ] `/{username}/{project}/delete/` - Delete page
- [ ] `/{username}/{project}/settings/` - Settings page

### File Operations
- [ ] `/{username}/{project}/file/{path}` - File view
- [ ] `/{username}/{project}/file/{path}/edit` - File edit
- [ ] `/{username}/{project}/file/{path}/history` - File history

### Features
- [ ] `/{username}/{project}/issues/` - Issues list
- [ ] `/{username}/{project}/issues/{id}` - Issue detail
- [ ] `/{username}/{project}/pulls/` - PR list
- [ ] `/{username}/{project}/pulls/{id}` - PR detail
- [ ] `/{username}/{project}/actions/` - Actions list
- [ ] `/{username}/{project}/security/` - Security overview
- [ ] `/{username}/{project}/commit/{hash}` - Commit detail

### User Pages
- [ ] `/{username}/` - User profile
- [ ] `/{username}/bio` - User bio
- [ ] `/{username}/projects` - User projects
- [ ] `/{username}/stars` - User stars

### Admin
- [ ] `/admin/repository-maintenance/` - Repository maintenance

### Assets
- [ ] Check browser console for 404s
- [ ] Verify all CSS loads
- [ ] Verify all JS loads
- [ ] Check no broken images/icons

---

## Rollback Plan

If issues arise:

1. **Keep old files during migration**
   ```bash
   # Don't delete, rename to .old
   mv templates/project_app/issues templates/project_app/.old/issues
   ```

2. **Git commit after each phase**
   ```bash
   git add .
   git commit -m "Phase 1: Flatten templates"
   ```

3. **Can revert specific commits**
   ```bash
   git revert <commit-hash>
   ```

---

## Expected Results

### Before (Current)
- 170 template files in nested directories
- 26 duplicate partials
- Mixed naming conventions
- Hard to search/navigate

### After (Target)
- ~150 template files (removed duplicates)
- All at top level or in `xxx_partials/`
- Consistent explicit naming
- Easy to search: `ls *issues*` shows all issue templates
- Clear ownership: `issues_list_partials/` belongs to `issues_list.html`

---

## Estimated Time

- Phase 1 (Templates): 3-4 hours
- Phase 2 (CSS): 1 hour
- Phase 3 (JavaScript): 30 minutes
- Phase 4 (Update includes): 2-3 hours
- Phase 5 (Update static refs): 1 hour
- Phase 6 (Cleanup): 30 minutes
- Testing: 2 hours

**Total: ~10-12 hours**

---

## Next Steps

1. Review and approve this plan
2. Create file mapping spreadsheet for tracking
3. Execute phase by phase with git commits
4. Test thoroughly after each phase
5. Document any issues encountered

<!-- EOF -->
