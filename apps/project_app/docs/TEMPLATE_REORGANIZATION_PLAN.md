# Template Reorganization Plan (Final)

**Approach:** Separate **ACTIVE PAGES** from **PLANNED FEATURES**

---

## Current Problem

Templates are mixed together without clear indication of:
- ✅ What's actively used (views exist, users see them)
- ⏳ What's planned (designs exist, but no views/services yet)
- ❓ What's experimental/abandoned

This creates confusion about what's "real" vs. "placeholder".

---

## New Structure: Clear Separation

### Rationale:
- **Active templates** stay in root and organized subdirectories
- **Planned feature templates** move to `planned/` to indicate "not yet implemented"
- **Shared partials** stay accessible to both
- **Legacy/experimental** clearly marked

---

## Proposed Directory Structure

```
templates/project_app/

├── 📁 pages/                          ← ACTIVE PAGES (what users see now)
│   ├── project_base.html              ← App-prefixed base template
│   ├── project_create.html            ← rename: create.html
│   ├── project_edit.html              ← rename: edit.html
│   ├── project_delete.html            ← rename: delete.html
│   ├── project_index.html             ← rename: index.html
│   ├── project_settings.html          ← rename: settings.html
│   ├── github_integration.html        ✅ keep as-is
│   ├── repository_maintenance.html    ✅ keep as-is
│   │
│   ├── 📁 users/                      ✅ keep all 5
│   │   ├── profile.html               ← rename: bio.html
│   │   ├── overview.html
│   │   ├── projects.html
│   │   ├── board.html
│   │   └── stars.html
│   │
│   └── 📁 files/                      ← NEW: consolidated file management
│       ├── browser_root.html          ← from: browse/project_root.html
│       ├── browser_subdirectory.html  ← from: browse/subdirectory.html
│       ├── view.html                  ← from: filer/view.html
│       ├── edit.html                  ← from: filer/edit.html
│       └── history.html               ← from: filer/history.html
│
├── 📁 partials/                       ← SHARED COMPONENTS (all 57 used)
│   ├── _breadcrumb.html
│   ├── _file_list.html
│   ├── _sidebar.html
│   ├── _toolbar.html
│   ├── _scripts.html
│   ├── _tab_navigation.html
│   │
│   ├── 📁 forms/
│   │   ├── _project_form.html
│   │   ├── _file_form.html
│   │   └── ...
│   │
│   ├── 📁 settings/
│   │   ├── _general.html
│   │   ├── _collaborators.html
│   │   ├── _visibility.html
│   │   └── _danger_zone.html
│   │
│   ├── 📁 files/
│   │   ├── _file_view_*.html (11)
│   │   ├── _file_header.html
│   │   └── history_*.html (4)
│   │
│   ├── 📁 project/
│   │   ├── _header.html
│   │   ├── _tabs.html
│   │   ├── _readme.html
│   │   └── _empty_state.html
│   │
│   └── [other active partials organized by purpose]
│
├── 📁 planned/                        ← FUTURE FEATURES (not yet in views)
│   │                                   Templates exist but no views render them
│   │
│   ├── 📁 actions/                    ⏳ GitHub Actions/Workflows
│   │   ├── actions_list.html
│   │   ├── workflow_detail.html
│   │   ├── workflow_editor.html
│   │   ├── workflow_delete_confirm.html
│   │   ├── workflow_run_detail.html
│   │   └── partials/
│   │       ├── _workflow_breadcrumb.html
│   │       ├── _workflow_editor_form.html
│   │       └── _workflow_templates_sidebar.html
│   │
│   ├── 📁 issues/                     ⏳ Issue Tracking
│   │   ├── issues_list.html
│   │   ├── issue_detail.html
│   │   ├── issue_form.html
│   │   ├── label_manage.html
│   │   └── milestone_manage.html
│   │
│   ├── 📁 pull_requests/              ⏳ Pull Request Management
│   │   ├── pr_list.html
│   │   ├── pr_detail.html
│   │   ├── pr_form.html
│   │   ├── pr_compare.html
│   │   └── partials/
│   │       ├── _pr_breadcrumb.html
│   │       ├── _pr_header.html
│   │       ├── _pr_list_*.html (8)
│   │       ├── _pr_tabs.html
│   │       ├── pr_*.html (5)
│   │       └── _pr_merge_modal.html
│   │
│   ├── 📁 security/                   ⏳ Security & Dependency Scanning
│   │   ├── security_overview.html
│   │   ├── security_alerts.html
│   │   ├── security_alert_detail.html
│   │   ├── security_advisories.html
│   │   ├── security_policy.html
│   │   ├── dependency_graph.html
│   │   ├── scan_history.html
│   │   └── partials/
│   │       ├── _security_header.html
│   │       ├── _security_tabs.html
│   │       ├── _security_alerts_card.html
│   │       ├── _security_scans_card.html
│   │       └── _security_stats.html
│   │
│   ├── 📁 commits/                    ⏳ Commit History Display
│   │   └── detail.html
│   │
│   └── 📁 partials/                   (Reusable for planned features)
│       └── [components shared by planned features]
│
└── 📁 legacy/                         ← OBSOLETE/EXPERIMENTAL
    ├── extracted_styles/              (Old CSS extraction approach)
    ├── sidebar.html      (Incomplete experiment)
    ├── list.html                      (Superseded by other functionality)
    ├── filer/                         (If not fully migrated to browse→files/)
    ├── browse/                        (If migrating from this)
    └── README.md                      (Explain what's here & why)
```

---

## Key Changes Explained

### 1. **New `pages/` Directory**
- **Why:** Clearly separates what users see NOW from everything else
- **What goes there:** All actively rendered templates
- **Benefits:**
  - Easy to find what's in production
  - Clear that these have corresponding views/services
  - Easier for new developers to understand the site

### 2. **New `planned/` Directory**
- **Why:** Templates for future features that don't have views yet
- **What goes there:** actions/, issues/, pull_requests/, security/, commits/
- **Benefits:**
  - Indicates "this is not live yet"
  - Preserves work for future implementation
  - Prevents confusion with active code
  - Easy to move to `pages/` when service/view are created

### 3. **New `files/` Subdirectory under Pages**
- **Why:** Consolidates file management (currently split between filer/ and browse/)
- **What goes there:** File browser, editor, viewer, history
- **Benefits:**
  - Resolves filer/browse confusion
  - Groups related functionality
  - Clear naming (browser_root, browser_subdirectory, not project_root)

### 4. **Organized Partials Structure**
- **Why:** Currently flat with 57 files, hard to navigate
- **What:** Group by purpose (forms/, settings/, files/, project/)
- **Benefits:**
  - Easier to find components
  - Shows relationship between partials and pages
  - Scalable as more features are added

### 5. **Legacy Directory**
- **Why:** Keep experimental/old code without cluttering active areas
- **What:** Old CSS extraction attempts, incomplete experiments
- **Benefits:**
  - Clear separation of "don't touch this"
  - Can be deleted in future without affecting current code

---

## Implementation Steps

### Phase 1: Directory Setup (5 minutes)
```bash
# Create new directories
mkdir -p apps/project_app/templates/project_app/pages
mkdir -p apps/project_app/templates/project_app/pages/users
mkdir -p apps/project_app/templates/project_app/pages/files
mkdir -p apps/project_app/templates/project_app/partials/forms
mkdir -p apps/project_app/templates/project_app/partials/settings
mkdir -p apps/project_app/templates/project_app/partials/files
mkdir -p apps/project_app/templates/project_app/partials/project
mkdir -p apps/project_app/templates/project_app/planned
mkdir -p apps/project_app/templates/project_app/legacy
```

### Phase 2: Move & Rename Active Templates (10 minutes)
```bash
# Move root templates to pages/
mv apps/project_app/templates/project_app/create.html \
   apps/project_app/templates/project_app/pages/project_create.html
mv apps/project_app/templates/project_app/edit.html \
   apps/project_app/templates/project_app/pages/project_edit.html
mv apps/project_app/templates/project_app/delete.html \
   apps/project_app/templates/project_app/pages/project_delete.html
mv apps/project_app/templates/project_app/index.html \
   apps/project_app/templates/project_app/pages/project_index.html
mv apps/project_app/templates/project_app/settings.html \
   apps/project_app/templates/project_app/pages/project_settings.html

# Move users/ to pages/users/
mv apps/project_app/templates/project_app/users/* \
   apps/project_app/templates/project_app/pages/users/
# Rename bio.html to profile.html
mv apps/project_app/templates/project_app/pages/users/bio.html \
   apps/project_app/templates/project_app/pages/users/profile.html

# Move github & repo maintenance (can stay at root or move to pages/)
# Option A: Keep at root (if they're global)
# Option B: Move to pages/ (if they're project-specific) - recommended

# Consolidate file management: browse/ + filer/ → pages/files/
mv apps/project_app/templates/project_app/browse/project_root.html \
   apps/project_app/templates/project_app/pages/files/browser_root.html
mv apps/project_app/templates/project_app/browse/subdirectory.html \
   apps/project_app/templates/project_app/pages/files/browser_subdirectory.html
mv apps/project_app/templates/project_app/filer/view.html \
   apps/project_app/templates/project_app/pages/files/
mv apps/project_app/templates/project_app/filer/edit.html \
   apps/project_app/templates/project_app/pages/files/
mv apps/project_app/templates/project_app/filer/history.html \
   apps/project_app/templates/project_app/pages/files/
```

### Phase 3: Move Planned Features (5 minutes)
```bash
# Move entire feature directories to planned/
mv apps/project_app/templates/project_app/actions \
   apps/project_app/templates/project_app/planned/
mv apps/project_app/templates/project_app/issues \
   apps/project_app/templates/project_app/planned/
mv apps/project_app/templates/project_app/pull_requests \
   apps/project_app/templates/project_app/planned/
mv apps/project_app/templates/project_app/security \
   apps/project_app/templates/project_app/planned/
mv apps/project_app/templates/project_app/commits \
   apps/project_app/templates/project_app/planned/
```

### Phase 4: Organize Partials (10 minutes)
```bash
# Create helper script to analyze which partials go where
# Then move them to appropriate subdirectories

# Example - move settings partials
mv apps/project_app/templates/project_app/partials/settings_*.html \
   apps/project_app/templates/project_app/partials/settings/

# Move file-related partials
mv apps/project_app/templates/project_app/partials/_file_*.html \
   apps/project_app/templates/project_app/partials/files/
mv apps/project_app/templates/project_app/partials/history_*.html \
   apps/project_app/templates/project_app/partials/files/
mv apps/project_app/templates/project_app/partials/commit_*.html \
   apps/project_app/templates/project_app/partials/files/

# Move project-related partials
mv apps/project_app/templates/project_app/partials/_project_*.html \
   apps/project_app/templates/project_app/partials/project/
mv apps/project_app/templates/project_app/partials/_repo_tabs.html \
   apps/project_app/templates/project_app/partials/project/

# Move form partials
mv apps/project_app/templates/project_app/partials/create_*.html \
   apps/project_app/templates/project_app/partials/forms/
mv apps/project_app/templates/project_app/partials/edit_*.html \
   apps/project_app/templates/project_app/partials/forms/
mv apps/project_app/templates/project_app/partials/*form*.html \
   apps/project_app/templates/project_app/partials/forms/ 2>/dev/null || true

# Move user-related partials
mkdir -p apps/project_app/templates/project_app/partials/users/
mv apps/project_app/templates/project_app/partials/user_*.html \
   apps/project_app/templates/project_app/partials/users/
mv apps/project_app/templates/project_app/partials/profile_*.html \
   apps/project_app/templates/project_app/partials/users/
```

### Phase 5: Archive Legacy Files (5 minutes)
```bash
# Move old/experimental files to legacy/
mv apps/project_app/templates/project_app/legacy/extracted_styles \
   apps/project_app/templates/project_app/legacy/
mv apps/project_app/templates/project_app/sidebar.html \
   apps/project_app/templates/project_app/legacy/
mv apps/project_app/templates/project_app/list.html \
   apps/project_app/templates/project_app/legacy/

# If filer/ still has old files after consolidation:
mv apps/project_app/templates/project_app/filer \
   apps/project_app/templates/project_app/legacy/filer_old_backup/

# If browse/ exists as duplicate:
mv apps/project_app/templates/project_app/browse \
   apps/project_app/templates/project_app/legacy/browse_old_backup/
```

### Phase 6: Update All Template References (20 minutes)
```bash
# Find all render() calls that need updating
grep -r "render.*create.html\|render.*edit.html" \
  apps/project_app/views apps/project_app/*.py

# Update view files to use new paths
# Example: "project_app/create.html" → "project_app/pages/project_create.html"
```

### Phase 7: Update Include Paths (10 minutes)
```bash
# Update all {% include %} statements in templates
grep -r "{% include.*partials" \
  apps/project_app/templates/project_app/pages

# Update to new paths:
# {% include "project_app/partials/settings_general.html" %}
# becomes:
# {% include "project_app/partials/settings/_general.html" %}
```

### Phase 8: Test Everything (15 minutes)
```bash
# Run tests
python manage.py test project_app

# Manually test key pages:
# - http://127.0.0.1:8000/test-user/proj-001/ (project index)
# - http://127.0.0.1:8000/project/new/ (project create)
# - http://127.0.0.1:8000/test-user/proj-001/settings (project settings)
# - http://127.0.0.1:8000/test-user/proj-001/.git (file browser)
# - http://127.0.0.1:8000/test-user/ (user profile)
```

---

## Summary of Changes

### Files Moved (Active Pages): 18 files
```
Root templates → pages/
Users templates → pages/users/
File management → pages/files/ (consolidates filer/ + browse/)
```

### Directories Moved (Planned Features): ~55 files
```
actions/ → planned/actions/
issues/ → planned/issues/
pull_requests/ → planned/pull_requests/
security/ → planned/security/
commits/ → planned/commits/
```

### Partials Organized: 57 files into subdirectories
```
partials/forms/
partials/settings/
partials/files/
partials/project/
partials/users/
```

### Result:
```
BEFORE:                 AFTER:
173 files              173 files (same count)
├─ 24 active           ├─ 24 in pages/ (clear they're active)
├─ 55 planned          ├─ 55 in planned/ (clear they're future)
├─ 57 partials         ├─ 57 in partials/ (organized)
└─ 37 legacy           └─ 37 in legacy/ (don't touch)

Key Benefit: CLEAR SEPARATION of what's live vs. planned vs. obsolete
```

---

## Benefits of This Structure

✅ **Clarity**
   - Anyone looking at `/pages/` knows those are live features
   - Anyone looking at `/planned/` knows those are in development
   - Clear architectural intent

✅ **Scalability**
   - Easy to add new pages (just add to pages/)
   - Easy to move planned feature to active (move planned/X → pages/)
   - Partials organized by domain makes them easier to find

✅ **Maintenance**
   - When implementing actions/issues/PRs, you know exactly where the templates are
   - No confusion about what's being used vs. what's sitting around
   - Can run tests specifically on active templates

✅ **Developer Onboarding**
   - New developers immediately understand: pages = live, planned = future, legacy = don't touch
   - Less cognitive load when exploring codebase

✅ **Documentation**
   - Structure itself documents the product roadmap
   - Templates for future features serve as design documentation

---

## Next: Service Architecture

Once templates are organized, the next step is ensuring each active page has:

```
✅ pages/project_create.html
✅ views/project_views.py (with project_create() function)
✅ services/project_service.py (with create_project() method)
✅ urls.py entry point
```

And planned features have templates but wait for service/view implementation.

---

## Checklist

- [ ] Create new directories (Phase 1)
- [ ] Move active templates (Phase 2)
- [ ] Move users templates (Phase 2)
- [ ] Consolidate file management (Phase 2)
- [ ] Move planned features (Phase 3)
- [ ] Organize partials (Phase 4)
- [ ] Archive legacy files (Phase 5)
- [ ] Update all render() calls (Phase 6)
- [ ] Update all include paths (Phase 7)
- [ ] Run tests (Phase 8)
- [ ] Commit changes with clear message
