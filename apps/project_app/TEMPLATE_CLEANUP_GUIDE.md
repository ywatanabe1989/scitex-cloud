# Template Directory Cleanup Guide

Quick reference for understanding and reorganizing the template structure.

---

## 📊 Current State Summary

```
Total Files:        173
├─ Used:            75 files (43%)
│  ├─ Page templates:    18
│  └─ Partials:          57
├─ Unused:         98 files (57%)
│  ├─ Orphaned:          45
│  ├─ Legacy:             7
│  └─ Duplicate dirs:     46
└─ Status:         Critical organizational debt
```

---

## ✅ KEEP: 18 Active Page Templates

These are being rendered by views - **DO NOT DELETE**:

```
✅ Root Level
   create.html                    (Project creation)
   delete.html                    (Deletion confirmation)
   edit.html                      (Project editing)
   index.html                     (Project index/home)
   settings.html                  (Project settings)
   github_integration.html        (GitHub integration)
   repository_maintenance.html    (Maintenance page)

✅ Users Directory
   users/bio.html                 (User profile)
   users/board.html               (User board)
   users/overview.html            (User overview)
   users/projects.html            (User's projects)
   users/stars.html               (User's stars)

✅ Filer (File Management)
   filer/directory.html           (File browser)
   filer/edit.html                (File editor)
   filer/history.html             (File history)
   filer/view.html                (File viewer)

⚠️ Note: project_collaborate.html & project_members.html may be missing files
```

---

## ✅ KEEP: 57 Active Partials

Used by the page templates above:

```
✅ File Viewer (11)
   _file_view_breadcrumb.html
   _file_view_content_binary.html
   _file_view_content_code.html
   _file_view_content_image.html
   _file_view_content_markdown.html
   _file_view_content_pdf.html
   _file_view_content_text.html
   _file_view_header.html
   _file_view_pdf_scripts.html
   _file_view_scripts.html
   _file_view_tabs.html

✅ Project Display (7)
   _project_empty_state.html
   _project_file_browser.html
   _project_header.html
   _project_readme.html
   _project_scripts.html
   _project_toolbar.html
   _repo_tabs.html

✅ Settings (6)
   settings_collaborators.html
   settings_danger_zone.html
   settings_delete_modal.html
   settings_general.html
   settings_navigation.html
   settings_visibility.html

✅ Create/Edit Forms (11)
   create_breadcrumb.html
   create_description_field.html
   create_form_actions.html
   create_name_field.html
   edit_breadcrumb.html
   edit_description_field.html
   edit_form_actions.html
   edit_name_field.html
   edit_source_url_field.html
   project_create_init_options.html
   project_create_scripts.html

✅ Delete Confirmation (6)
   delete_breadcrumb.html
   delete_confirmation_form.html
   delete_confirmation_script.html
   delete_consequences_list.html
   delete_project_info.html
   delete_warning_box.html

✅ User Profile (2)
   user_bio_header.html
   user_bio_projects.html

✅ File History (4)
   commit_list_item.html
   history_filter_bar.html
   history_header.html
   history_pagination.html

✅ Navigation (6)
   _breadcrumb.html
   _file_list.html
   _scripts.html
   _sidebar.html
   _tab_navigation.html
   _toolbar.html

✅ User Pages (4)
   profile_navigation.html
   profile_scripts.html
   profile_sidebar.html
   repository_list_item.html
```

---

## ❌ DELETE: Completely Unused Feature Directories

These directories have **zero** active views rendering them:

### Actions Workflows (8 files)
```
❌ DELETE: actions/
   └─ actions_list.html
   └─ workflow_delete_confirm.html
   └─ workflow_detail.html
   └─ workflow_editor.html
   └─ workflow_run_detail.html
   └─ partials/_workflow_breadcrumb.html
   └─ partials/_workflow_editor_form.html
   └─ partials/_workflow_templates_sidebar.html
```
**Status:** Not implemented. No views in `views/actions_views.py` render these.

### Pull Requests (16 files)
```
❌ DELETE: pull_requests/
   └─ pr_detail.html
   └─ pr_form.html
   └─ pr_list.html
   └─ partials/ (13 files)
```
**Status:** Not implemented. No views render these.

### Issues Management (5 files)
```
❌ DELETE: issues/
   └─ issue_detail.html
   └─ issue_form.html
   └─ issues_list.html
   └─ label_manage.html
   └─ milestone_manage.html
```
**Status:** Not implemented. No views render these.

### Security Features (11 files)
```
❌ DELETE: security/
   └─ dependency_graph.html
   └─ scan_history.html
   └─ security_advisories.html
   └─ security_alert_detail.html
   └─ security_alerts.html
   └─ security_overview.html
   └─ security_policy.html
   └─ partials/ (5 files)
```
**Status:** Not implemented. No views render these.

### Commits Display (1 file)
```
❌ DELETE: commits/
   └─ detail.html
```
**Status:** Not used. File history is displayed by `filer/history.html` instead.

### Duplicate/Experimental Directories (46 files)
```
❌ DELETE: browse/
   └─ (exact duplicate of filer/ partials)
```
**Status:** Completely redundant. Use filer/ instead.

---

## ❌ DELETE: Legacy & Orphaned Files

### Legacy Directory (7 files)
```
❌ DELETE: legacy/extracted_styles/
   └─ _styles.html
   └─ commit_detail_styles.html
   └─ history_styles.html
   └─ profile_styles.html
   └─ project_create_styles.html
   └─ settings_styles.html
   └─ user_bio_styles.html
```
**Status:** Not how Django CSS works. Delete entirely.

### Experimental Files (2 files)
```
❌ DELETE: sidebar_improvements.html    (Incomplete feature)
❌ DELETE: list.html                    (Superseded by other functionality)
❌ DELETE: filer/browser.html           (Superseded by filer/directory.html)
```

---

## 🎯 Cleanup Tasks (Priority Order)

### Phase 1: High-Impact Deletions (5 minutes)
```bash
# Delete completely unused feature directories
rm -rf apps/project_app/templates/project_app/actions/
rm -rf apps/project_app/templates/project_app/issues/
rm -rf apps/project_app/templates/project_app/pull_requests/
rm -rf apps/project_app/templates/project_app/security/
rm -rf apps/project_app/templates/project_app/commits/
rm -rf apps/project_app/templates/project_app/browse/

# Delete legacy files
rm -rf apps/project_app/templates/project_app/legacy/extracted_styles/
rm apps/project_app/templates/project_app/sidebar_improvements.html
rm apps/project_app/templates/project_app/list.html
rm apps/project_app/templates/project_app/filer/browser.html
```

**Result:** Removes 78 files, reduces directory from 173 → 95 files

### Phase 2: Remove Unused Partials (10 minutes)

After Phase 1, audit remaining partials:
```bash
# Check for any remaining unused partials
grep -r "{% include" apps/project_app/templates/project_app/*.html \
  apps/project_app/templates/project_app/{users,filer}/*.html
```

Then delete any partials not found in the includes.

**Result:** Potential to remove 30-40 more files

### Phase 3: Rename Templates (15 minutes - optional)

For consistency with README.md guidelines:
```
create.html         → project_create.html
edit.html           → project_edit.html
delete.html         → project_delete.html
index.html          → project_index.html
settings.html       → project_settings.html
```

Update all `render()` calls in views to match.

### Phase 4: Add Base Template (5 minutes - optional)

Create `project_app_base.html` with common structure used by all templates.

---

## ✏️ Verification Checklist

Before & After each phase:

```
□ Run tests: python manage.py test project_app
□ Check homepage: http://127.0.0.1:8000/test-user/proj-001/
□ Check project creation: http://127.0.0.1:8000/project/new/
□ Check project settings: http://127.0.0.1:8000/test-user/proj-001/settings/
□ Check file browser: http://127.0.0.1:8000/test-user/proj-001/.git
□ Check user profile: http://127.0.0.1:8000/test-user/
□ Confirm no 404 template errors in console
```

---

## 📋 File Organization After Cleanup

```
templates/project_app/
├── project_app_base.html          (New: Base template)
│
├── create.html                    ✅ Keep
├── edit.html                      ✅ Keep
├── delete.html                    ✅ Keep
├── index.html                     ✅ Keep
├── settings.html                  ✅ Keep
├── github_integration.html        ✅ Keep
├── repository_maintenance.html    ✅ Keep
│
├── users/                         ✅ Keep all 5
│   ├── bio.html
│   ├── board.html
│   ├── overview.html
│   ├── projects.html
│   └── stars.html
│
├── filer/                         ✅ Keep 4, delete 1
│   ├── directory.html
│   ├── edit.html
│   ├── history.html
│   └── view.html
│
├── partials/                      ✅ Keep used, delete unused
│   ├── _breadcrumb.html
│   ├── _file_list.html
│   ├── _file_view_*.html (11)
│   ├── _project_*.html (7)
│   ├── _scripts.html
│   ├── _sidebar.html
│   ├── _tab_navigation.html
│   ├── _toolbar.html
│   ├── create_*.html (6)
│   ├── delete_*.html (6)
│   ├── edit_*.html (5)
│   ├── history_*.html (4)
│   ├── profile_*.html (3)
│   ├── settings_*.html (6)
│   └── user_bio_*.html (2)
│
└── legacy/                        (Optional: Archive instead of delete)
    └── archived_features/
        ├── actions_backup/
        ├── issues_backup/
        ├── pull_requests_backup/
        ├── security_backup/
        └── commits_backup/

[DELETED]
❌ actions/
❌ issues/
❌ pull_requests/
❌ security/
❌ commits/
❌ browse/
❌ legacy/extracted_styles/
❌ sidebar_improvements.html
❌ list.html
❌ filer/browser.html
```

**Final result:** 95 files (down from 173) - 45% reduction

---

## 🔍 Root Cause Analysis

Why did this happen?
1. **Multiple refactoring waves** - Different people moved/created features
2. **Planned but unimplemented features** - Actions, Issues, PRs, Security
3. **Duplicate directories** - `browse/` is exact copy of filer partials
4. **No cleanup process** - Old files never deleted, just replaced
5. **Lack of organization** - No app-prefixed base template or naming standard

**Prevention:**
- Follow README.md naming conventions strictly
- Delete unused files during refactoring
- Document which features are planned vs. active
- Add linting to catch orphaned templates

---

## Questions to Answer First

Before executing cleanup, confirm:
1. ❓ Are Actions/Issues/PRs/Security **planned features** or **abandoned**?
2. ❓ Should we archive them to `legacy/` or delete completely?
3. ❓ Is `project_collaborate.html` or `project_members.html` being rendered from somewhere else?
4. ❓ Should we rename templates with `project_` prefix or keep current names?

---

## Time Estimate

| Task | Time | Impact |
|------|------|--------|
| Phase 1 (Delete unused dirs) | 5 min | High (50 files removed) |
| Phase 2 (Remove orphaned partials) | 10 min | Medium (30 files removed) |
| Phase 3 (Rename templates) | 15 min | Low (consistency only) |
| Phase 4 (Add base template) | 5 min | Low (best practice) |
| **Testing** | 10 min | Critical |
| **TOTAL** | **45 min** | **95 files cleaned up** |
