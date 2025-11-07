<!-- ---
!-- Timestamp: 2025-11-04
!-- Author: Claude Code
!-- Purpose: Comprehensive refactoring plan to follow FULLSTACK.md guidelines
!-- --- -->

# Project App Refactoring Plan - FULLSTACK.md Compliance

## Current Status

**Current Structure:** Flat organization with mixed layers
```
views/               → 14 Python files (flat)
templates/           → 39 HTML files (flat)
static/css/          → CSS files (flat)
static/ts/           → TS files (flat)
models/              → Some feature organization (actions.py, issues.py, pull_requests.py)
services/            → Mostly utility files, needs organization
```

**Target Structure:** Nested feature-based with perfect correspondence
```
views/repository/, views/pull_requests/, views/issues/, views/security/,
views/workflows/, views/projects/, views/users/, views/actions/

templates/project_app/repository/, templates/project_app/pull_requests/, etc.
static/project_app/css/repository/, static/project_app/css/pull_requests/, etc.
static/project_app/ts/repository/, static/project_app/ts/pull_requests/, etc.
```

---

## Features Identified

### 1. Repository Feature
**Handles:** File browsing, viewing, editing, history, commits
**Current Files:**
- Views: project_views.py (project_directory_dynamic, project_directory, project_file_view, file_history_view, commit_detail)
- Templates: browse.html, file_view.html, file_edit.html, file_history.html, commit_detail.html, directory_browser.html, file_browser.html, file_directory.html
- CSS: browse.css, file_view.css, file_edit.css, file_history.css, commit_detail.css, etc.
- TS: browse.ts, file_view.ts, file_edit.ts, file_history.ts, etc.

**New Structure:**
```
views/repository/
├── __init__.py
├── browse.py          (project_directory_dynamic, project_directory)
├── file_view.py       (project_file_view)
├── file_edit.py       (file edit operations)
├── file_history.py    (file_history_view)
└── commit_detail.py   (commit_detail)

templates/project_app/repository/
├── browse.html
├── file_view.html
├── file_edit.html
├── file_history.html
└── commit_detail.html

static/project_app/css/repository/
├── browse.css
├── file_view.css
├── file_edit.css
├── file_history.css
└── commit_detail.css

static/project_app/ts/repository/
├── browse.ts
├── file_view.ts
├── file_edit.ts
├── file_history.ts
└── commit_detail.ts
```

### 2. Pull Requests Feature
**Handles:** PR listing, detail view, form for creating/editing PRs
**Current Files:**
- Views: pr_views.py (pr_list, pr_detail, pr_form, pr_conversation, pr_compare)
- Templates: pr_list.html, pr_detail.html, pr_form.html
- CSS: pr_list.css, pr_detail.css, pr_form.css
- TS: pr_list.ts, pr_detail.ts, pr_form.ts

**New Structure:**
```
views/pull_requests/
├── __init__.py
├── list.py           (pr_list)
├── detail.py         (pr_detail, pr_conversation)
└── form.py           (pr_form, pr_compare)

templates/project_app/pull_requests/
├── list.html
├── detail.html
└── form.html

static/project_app/css/pull_requests/
├── list.css
├── detail.css
└── form.css

static/project_app/ts/pull_requests/
├── list.ts
├── detail.ts
└── form.ts
```

### 3. Issues Feature
**Handles:** Issue tracking, labels, milestones
**Current Files:**
- Views: issues_views.py (issues_list, issues_detail, issues_form, issues_label_manage, issues_milestone_manage)
- Templates: issues_list.html, issues_detail.html, issues_form.html, issues_label_manage.html, issues_milestone_manage.html
- CSS: issues_list.css, issues_detail.css, issues_form.css, etc.
- TS: issues_list.ts, issues_detail.ts, etc.

**New Structure:**
```
views/issues/
├── __init__.py
├── list.py
├── detail.py
├── form.py
└── management.py     (labels, milestones)

templates/project_app/issues/
├── list.html
├── detail.html
├── form.html
└── management.html   (labels/milestones)

static/project_app/css/issues/
├── list.css
├── detail.css
├── form.css
└── management.css

static/project_app/ts/issues/
├── list.ts
├── detail.ts
├── form.ts
└── management.ts
```

### 4. Security Feature
**Handles:** Security scanning, alerts, advisories, dependencies
**Current Files:**
- Views: security_views.py (security_overview, security_alerts, security_scan_history, security_advisory, etc.)
- Templates: security_overview.html, security_alerts.html, security_advisories.html, security_scan_history.html, security_dependency_graph.html, security_alert_detail.html, security_policy.html
- CSS, TS: corresponding files

**New Structure:**
```
views/security/
├── __init__.py
├── overview.py
├── alerts.py
├── scan.py
├── advisories.py
├── dependency.py
└── policy.py

templates/project_app/security/
├── overview.html
├── alerts.html
├── scan_history.html
├── advisories.html
├── dependency_graph.html
├── alert_detail.html
└── policy.html

static/project_app/css/security/
├── overview.css
├── alerts.css
├── scan.css
├── advisories.css
├── dependency.css
└── policy.css

static/project_app/ts/security/
├── overview.ts
├── alerts.ts
├── scan.ts
├── advisories.ts
├── dependency.ts
└── policy.ts
```

### 5. Workflows Feature
**Handles:** Workflow editor, execution details, runs
**Current Files:**
- Views: (in project_views.py or separate)
- Templates: workflow_detail.html, workflow_editor.html, workflow_run_detail.html, workflow_delete_confirm.html

**New Structure:**
```
views/workflows/
├── __init__.py
├── detail.py
├── editor.py
├── runs.py
└── delete.py

templates/project_app/workflows/
├── detail.html
├── editor.html
├── run_detail.html
└── delete_confirm.html

static/project_app/css/workflows/
├── detail.css
├── editor.css
├── run_detail.css
└── delete_confirm.css

static/project_app/ts/workflows/
├── detail.ts
├── editor.ts
├── run_detail.ts
└── delete_confirm.ts
```

### 6. Projects Feature
**Handles:** Project CRUD, settings, deletion
**Current Files:**
- Views: project_views.py (project_list, project_detail, project_create, project_edit, project_delete, project_settings)
- Templates: list.html, browse.html, create.html, edit.html, delete.html, settings.html
- CSS, TS: corresponding files

**New Structure:**
```
views/projects/
├── __init__.py
├── list.py           (project_list)
├── detail.py         (project_detail)
├── create.py         (project_create, project_create_from_template)
├── edit.py           (project_edit)
├── delete.py         (project_delete)
└── settings.py       (project_settings)

templates/project_app/projects/
├── list.html
├── detail.html
├── create.html
├── edit.html
├── delete.html
└── settings.html

static/project_app/css/projects/
├── list.css
├── detail.css
├── create.css
├── edit.css
├── delete.css
└── settings.css

static/project_app/ts/projects/
├── list.ts
├── detail.ts
├── create.ts
├── edit.ts
├── delete.ts
└── settings.ts
```

### 7. Users Feature
**Handles:** User profiles, bio, board, projects list, stars
**Current Files:**
- Views: project_views.py (user_profile, user_bio_page, user_overview, user_projects_board, user_stars)
- Templates: user_bio.html, user_overview.html, user_projects.html, user_stars.html, user_board.html

**New Structure:**
```
views/users/
├── __init__.py
├── profile.py        (user_profile, user_bio_page)
├── overview.py       (user_overview)
├── board.py          (user_projects_board)
├── projects.py       (user_projects)
└── stars.py          (user_stars)

templates/project_app/users/
├── profile.html
├── overview.html
├── board.html
├── projects.html
└── stars.html

static/project_app/css/users/
├── profile.css
├── overview.css
├── board.css
├── projects.css
└── stars.css

static/project_app/ts/users/
├── profile.ts
├── overview.ts
├── board.ts
├── projects.ts
└── stars.ts
```

### 8. Actions Feature
**Handles:** Action execution history
**Current Files:**
- Views: actions_views.py
- Templates: actions_list.html

**New Structure:**
```
views/actions/
├── __init__.py
└── list.py

templates/project_app/actions/
└── list.html

static/project_app/css/actions/
└── list.css

static/project_app/ts/actions/
└── list.ts
```

### 9. Shared/Common
**Handles:** Shared utilities, sidebar, partials, base templates
**Structure:**
```
templates/project_app/
├── base/
│   └── app_base.html
├── shared/
│   ├── _sidebar.html
│   ├── _tabs.html
│   └── _navigation.html

static/project_app/css/shared/
├── sidebar.css
├── tabs.css
└── navigation.css

static/project_app/ts/shared/
├── Sidebar.ts
├── Tabs.ts
└── Navigation.ts

views/shared/
├── __init__.py
└── utils.py          (shared utilities and helpers)
```

### 10. API Layer (Optional)
For API endpoints, create parallel structure:
```
api/
├── __init__.py
├── repository/
│   ├── __init__.py
│   └── serializers.py / viewsets.py
├── pull_requests/
├── issues/
├── security/
├── workflows/
├── projects/
├── users/
└── actions/
```

---

## Migration Strategy

### Phase 1: Templates (Straightforward)
**Task:** Move flat HTML files into feature subdirectories
- Move browse.html → repository/browse.html
- Move pr_list.html → pull_requests/list.html
- Move issues_list.html → issues/list.html
- etc.
- Preserve partials structure (browse_partials/ → repository/browse/)

### Phase 2: Static CSS
**Task:** Move flat CSS files into feature subdirectories (mirrors templates)
- Same structure as templates

### Phase 3: Static TypeScript
**Task:** Move flat TS files into feature subdirectories (mirrors templates)
- Same structure as templates
- Update imports in TS files to use relative paths

### Phase 4: Views
**Task:** Reorganize Python view files into feature subdirectories
- Extract functions from large files (project_views.py, etc.)
- Create feature-specific view modules
- Update __init__.py to export all views
- Update urls.py to reference new locations

### Phase 5: URLs
**Task:** Reorganize URL configuration
```
urls/
├── __init__.py       (main)
├── repository.py
├── pull_requests.py
├── issues.py
├── security.py
├── workflows.py
├── projects.py
├── users.py
└── actions.py
```

### Phase 6: Models and Services
**Task:** Organize into feature subdirectories
```
models/
├── __init__.py
├── repository/
├── pull_requests/
├── issues/
├── security/
├── workflows/
├── projects/
├── users/
├── actions/
└── shared/

services/
├── __init__.py
├── repository/
├── pull_requests/
├── issues/
├── security/
├── workflows/
├── projects/
├── users/
├── actions/
└── shared/
```

---

## Execution Plan (Parallel Agents)

### Agent 1: Refactor Templates Structure
- Create feature subdirectories in templates/project_app/
- Move HTML files and their partials
- Update all template paths in views

### Agent 2: Refactor CSS Structure
- Create feature subdirectories in static/project_app/css/
- Move CSS files to match template structure
- Ensure imports work correctly

### Agent 3: Refactor TypeScript Structure
- Create feature subdirectories in static/project_app/ts/
- Move TS files to match template structure
- Update relative import paths

### Agent 4: Refactor Views - Part 1 (Repository & Pull Requests)
- Create views/repository/ with browse.py, file_view.py, file_edit.py, file_history.py, commit_detail.py
- Create views/pull_requests/ with list.py, detail.py, form.py
- Extract functions from monolithic files
- Update imports

### Agent 5: Refactor Views - Part 2 (Issues & Security)
- Create views/issues/ with list.py, detail.py, form.py, management.py
- Create views/security/ with overview.py, alerts.py, scan.py, advisories.py, dependency.py, policy.py
- Extract functions from security_views.py and issues_views.py
- Update imports

### Agent 6: Refactor Views - Part 3 (Workflows, Projects, Users, Actions)
- Create views/workflows/ with detail.py, editor.py, runs.py, delete.py
- Create views/projects/ with list.py, detail.py, create.py, edit.py, delete.py, settings.py
- Create views/users/ with profile.py, overview.py, board.py, projects.py, stars.py
- Create views/actions/ with list.py
- Extract functions and organize

### Agent 7: Reorganize URL Configuration
- Create urls/ subdirectory structure matching features
- Update config/urls.py to include all feature URLs
- Verify all URL names work correctly

### Agent 8: Final Verification
- Run TypeScript compilation
- Run Django check command
- Test key views in browser
- Verify no import errors
- Document any remaining issues

---

## Import Patterns After Refactoring

```python
# Views importing models
from apps.project_app.models import Project, File  # or feature-specific

# Views importing services
from apps.project_app.services.repository import FileService

# Services importing models
from apps.project_app.models import Project

# Templates linking CSS/JS
<link rel="stylesheet" href="{% static 'project_app/css/repository/browse.css' %}">
<script src="{% static 'project_app/js/repository/browse.js' %}"></script>
```

---

## Potential Issues & Solutions

### Issue 1: Circular Imports
**Solution:** Use string references in models, import only at function level if needed

### Issue 2: Large Files with Mixed Concerns
**Solution:** Split carefully, ensure each feature file < 200 lines, extract utilities to shared/

### Issue 3: URL Namespace Conflicts
**Solution:** Use proper namespace organization in urls/__init__.py

### Issue 4: Static File Path Changes
**Solution:** Use Django {% static %} tag, compile TypeScript after restructuring

### Issue 5: Third-party integrations (GitHub, Gitea)
**Solution:** Place in shared/ or appropriate feature directory

---

## Validation Checklist

- [ ] All templates moved to feature subdirectories
- [ ] All CSS files moved to matching structure
- [ ] All TS files moved and imports updated
- [ ] All views reorganized into features
- [ ] All URLs reorganized and working
- [ ] No import errors
- [ ] TypeScript compiles
- [ ] Django checks pass
- [ ] All key views tested in browser
- [ ] CSS applies correctly
- [ ] JavaScript executes correctly
- [ ] No console errors

---

## Completion Criteria

✅ Perfect 1:1:1:1 correspondence across all layers
✅ All files in feature-based subdirectories
✅ Imports follow strict hierarchy (Models ← Services ← Views)
✅ No global scope pollution in TS files (use IIFEs)
✅ All functionality preserved
✅ No breaking changes for end users

---

<!-- EOF -->
