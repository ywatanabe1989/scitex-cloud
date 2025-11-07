# Project App Refactoring Execution Plan

**Date:** 2025-11-04
**Based on:** `/RULES/00_DJANGO_ORGANIZATION_BACKEND.md`

## Current Structure Analysis

### Models (Need Refactoring)
- `models.py` (1,300+ lines) - Contains 8 models
- `models_issues.py` (400+ lines) - Contains 6 models
- `models_pull_requests.py` (600+ lines) - Contains 6 models
- `models/actions.py` ✓ (Already organized)

### Views (Partial Refactoring Done)
- `base_views.py` (2,872 lines) - **NEEDS SPLITTING**
- `views/collaboration_views.py` ✓ (Created)
- `views/settings_views.py` ✓ (Created)
- `views/__init__.py` ✓ (Central export point exists)

---

## Target Structure

```
apps/project_app/
├── models/
│   ├── __init__.py              # Central export point for all models
│   ├── core.py                  # Project, ProjectMembership, ProjectPermission, VisitorAllocation
│   ├── collaboration.py         # ProjectInvitation, ProjectWatch, ProjectStar, ProjectFork
│   ├── issues.py                # Issue, IssueComment, IssueLabel, IssueMilestone, IssueAssignment, IssueEvent
│   ├── pull_requests.py         # PullRequest, PullRequestReview, PullRequestComment, etc.
│   └── actions.py               # Workflow, WorkflowRun, WorkflowJob, WorkflowStep ✓
│
├── views/
│   ├── __init__.py              # Central export point ✓
│   ├── collaboration_views.py   # ✓ project_collaborate, project_members, invitations
│   ├── settings_views.py        # ✓ project_settings
│   ├── project_views.py         # NEW: CRUD, user profile, list views
│   ├── directory_views.py       # NEW: File browser, commits, history
│   ├── api_views.py             # NEW: All REST API endpoints
│   ├── integration_views.py     # NEW: GitHub integration, repository maintenance
│   ├── issues_views.py          # ✓ (Already exists)
│   ├── pr_views.py              # ✓ (Already exists)
│   ├── security_views.py        # ✓ (Already exists)
│   └── actions_views.py         # ✓ (Already exists)
│
├── legacy/
│   ├── models_old.py            # Original models.py
│   ├── models_issues_old.py     # Original models_issues.py
│   ├── models_pull_requests_old.py  # Original models_pull_requests.py
│   ├── base_views_old.py        # Original base_views.py
│   └── README.md                # Documentation of what was archived
│
├── services/                    # ✓ Already well organized
├── templates/                   # ✓ Already well organized
├── static/                      # ✓ Already well organized
├── admin.py
├── apps.py
├── forms.py
├── signals.py
├── urls.py
└── tests.py
```

---

## Refactoring Steps

### Phase 1: Models Reorganization

#### Step 1.1: Create models/core.py
Extract from `models.py`:
- `ProjectMembership`
- `Project`
- `ProjectPermission`
- `VisitorAllocation`

#### Step 1.2: Create models/collaboration.py
Extract from `models.py`:
- `ProjectInvitation`
- `ProjectWatch`
- `ProjectStar`
- `ProjectFork`

#### Step 1.3: Move models_issues.py → models/issues.py
Move entire file content with minimal changes

#### Step 1.4: Move models_pull_requests.py → models/pull_requests.py
Move entire file content with minimal changes

#### Step 1.5: Create models/__init__.py
```python
# Export all models from submodules
from .core import Project, ProjectMembership, ProjectPermission, VisitorAllocation
from .collaboration import ProjectInvitation, ProjectWatch, ProjectStar, ProjectFork
from .issues import Issue, IssueComment, IssueLabel, IssueMilestone, IssueAssignment, IssueEvent
from .pull_requests import PullRequest, PullRequestReview, PullRequestComment, PullRequestCommit, PullRequestLabel, PullRequestEvent
from .actions import Workflow, WorkflowRun, WorkflowJob, WorkflowStep

__all__ = [
    # Core models
    'Project', 'ProjectMembership', 'ProjectPermission', 'VisitorAllocation',
    # Collaboration models
    'ProjectInvitation', 'ProjectWatch', 'ProjectStar', 'ProjectFork',
    # Issue models
    'Issue', 'IssueComment', 'IssueLabel', 'IssueMilestone', 'IssueAssignment', 'IssueEvent',
    # Pull Request models
    'PullRequest', 'PullRequestReview', 'PullRequestComment', 'PullRequestCommit', 'PullRequestLabel', 'PullRequestEvent',
    # Actions models
    'Workflow', 'WorkflowRun', 'WorkflowJob', 'WorkflowStep',
]
```

#### Step 1.6: Move old files to legacy/
- `models.py` → `legacy/models_old.py`
- `models_issues.py` → `legacy/models_issues_old.py`
- `models_pull_requests.py` → `legacy/models_pull_requests_old.py`

---

### Phase 2: Views Reorganization

#### Step 2.1: Create views/project_views.py
Extract from `base_views.py`:
- `project_list` (L37)
- `user_profile` (L42)
- `user_project_list` (L76)
- `user_bio_page` (L130)
- `project_detail` (L159)
- `project_create` (L366)
- `project_create_from_template` (L742)
- `project_edit` (L779)
- `project_delete` (L982)
- `user_overview` (L2374)
- `user_projects_board` (L2408)
- `user_stars` (L2435)
- `project_detail_redirect` (L1616)

#### Step 2.2: Create views/directory_views.py
Extract from `base_views.py`:
- `project_directory_dynamic` (L1640)
- `project_directory` (L2201)
- `project_file_view` (L1843)
- `file_history_view` (L2475)
- `commit_detail` (L2642)
- `_detect_language` (L1776) - helper function

#### Step 2.3: Create views/api_views.py
Extract from `base_views.py`:
- `api_file_tree` (L1096)
- `api_check_name_availability` (L1177)
- `api_project_list` (L1256)
- `api_project_create` (L1266)
- `api_concatenate_directory` (L1300)
- `api_project_detail` (L1425)
- `api_repository_health` (L1443)
- `api_repository_cleanup` (L1478)
- `api_repository_sync` (L1521)
- `api_repository_restore` (L1564)

#### Step 2.4: Create views/integration_views.py
Extract from `base_views.py`:
- `github_integration` (L1075)
- `repository_maintenance` (L1050)

#### Step 2.5: Update views/__init__.py
Import from new modular files instead of base_views.py

#### Step 2.6: Move base_views.py to legacy/
- `base_views.py` → `legacy/base_views_old.py`

---

### Phase 3: Testing & Verification

#### Step 3.1: Run migrations
```bash
python manage.py makemigrations project_app
python manage.py migrate project_app
```

#### Step 3.2: Test imports
```bash
python manage.py shell
>>> from apps.project_app.models import Project, Issue, PullRequest
>>> from apps.project_app.views import project_list, project_settings
```

#### Step 3.3: Start development server
```bash
./start_dev.sh
```

#### Step 3.4: Manual testing
- [ ] Visit project list page
- [ ] Visit project detail page
- [ ] Test file browser
- [ ] Test project settings
- [ ] Test collaboration features
- [ ] Test API endpoints

---

## Import Changes Required

### Before (current)
```python
from apps.project_app.models import Project
from .models import Issue
```

### After (no change needed!)
```python
from apps.project_app.models import Project  # Works the same!
from .models import Issue                     # Works the same!
```

The central `models/__init__.py` exports everything, so existing imports continue to work.

---

## Migration Strategy

### Use String References
All models already use string references for ForeignKey/ManyToManyField to avoid circular imports:

```python
# ✅ Good - will continue working
class ProjectMembership(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
```

This is already the pattern in the codebase, so no changes needed.

---

## Success Criteria

- [ ] All models organized into domain-specific modules
- [ ] All views split into feature-specific modules
- [ ] No import errors when starting Django
- [ ] All migrations apply successfully
- [ ] All views accessible via browser
- [ ] No broken URLs
- [ ] Legacy code moved to `legacy/` directory
- [ ] Documentation updated

---

## Notes

- Keep commits atomic (one phase/step per commit)
- Test after each major change
- Use string references for model relationships
- Maintain backward compatibility through `__init__.py` exports
- Document what was archived in `legacy/README.md`

<!-- EOF -->
