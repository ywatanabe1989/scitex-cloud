# Legacy Code Archive

**Date Archived:** 2025-11-04
**Reason:** Refactoring to follow Django organization best practices

## Archived Files

### Models (Archived from monolithic structure)

1. **models_old.py** (45K, 1,230 lines)
   - Original monolithic models file
   - **Replaced by:** `models/` directory structure
   - **Contains:** Project, ProjectMembership, ProjectPermission, VisitorAllocation, ProjectWatch, ProjectStar, ProjectFork, ProjectInvitation

2. **models_issues_old.py** (12K, 400 lines)
   - Original issues models file
   - **Replaced by:** `models/issues.py`
   - **Contains:** Issue, IssueComment, IssueLabel, IssueMilestone, IssueAssignment, IssueEvent

3. **models_pull_requests_old.py** (18K, 600 lines)
   - Original pull request models file
   - **Replaced by:** `models/pull_requests.py`
   - **Contains:** PullRequest, PullRequestReview, PullRequestComment, PullRequestCommit, PullRequestLabel, PullRequestEvent

### Views (Archived from monolithic structure)

4. **base_views_old.py** (105K, 2,872 lines)
   - Original monolithic views file
   - **Replaced by:** `views/` directory structure with:
     - `views/project_views.py` - CRUD operations, user profiles
     - `views/directory_views.py` - File browser, directory listing
     - `views/api_views.py` - REST API endpoints
     - `views/integration_views.py` - GitHub/Gitea integration
     - `views/collaboration_views.py` - Invitations, members (already existed)
     - `views/settings_views.py` - Project settings (already existed)

## New Structure

### Models (Organized by domain)

```
models/
├── __init__.py              # Central export point
├── core.py                  # Project, ProjectMembership, ProjectPermission, VisitorAllocation
├── collaboration.py         # ProjectWatch, ProjectStar, ProjectFork, ProjectInvitation
├── issues.py                # Issue tracking models
├── pull_requests.py         # Pull request models
└── actions.py               # Workflow/CI models
```

### Views (Organized by feature)

```
views/
├── __init__.py              # Central export point
├── project_views.py         # Project CRUD, user profiles (~1,000 lines)
├── directory_views.py       # File browser, directory listing (~800 lines)
├── api_views.py             # REST API endpoints (~600 lines)
├── integration_views.py     # GitHub/Gitea integration (~200 lines)
├── collaboration_views.py   # Invitations, members (~400 lines)
├── settings_views.py        # Project settings (~600 lines)
├── issues_views.py          # Issue management
├── pr_views.py              # Pull request management
├── security_views.py        # Security features
└── actions_views.py         # CI/CD workflows
```

## Why These Files Were Archived

### Benefits of Refactoring

1. **Code Organization**
   - Models split by domain (core, collaboration, issues, PRs)
   - Views split by feature (project, directory, API, integration)
   - Each file focused on specific functionality

2. **Maintainability**
   - Smaller files (200-1,000 lines vs 1,230-2,872 lines)
   - Clear separation of concerns
   - Easier code review and navigation

3. **Performance**
   - Faster file loading
   - Better IDE performance
   - Easier parallel development

4. **Django Best Practices**
   - Follows `/RULES/00_DJANGO_ORGANIZATION_BACKEND.md`
   - Uses string references for model relationships
   - Central export via `__init__.py`

### Backward Compatibility

All existing imports continue to work:

```python
# ✓ Still works
from apps.project_app.models import Project
from apps.project_app.views import project_list

# ✓ Also works (new way)
from apps.project_app.models.core import Project
from apps.project_app.views.project_views import project_list
```

## Migration Guide

If you need to reference old code:

1. **For models:** Look in `models_old.py`, `models_issues_old.py`, or `models_pull_requests_old.py`
2. **For views:** Look in `base_views_old.py`

**Important:** Do NOT import from these legacy files. They are kept for reference only.

## Refactoring Documentation

- **Execution Plan:** `../REFACTORING_EXECUTION_PLAN.md`
- **Summary:** `../REFACTORING_SUMMARY.md`
- **Organization Rules:** `/RULES/00_DJANGO_ORGANIZATION_BACKEND.md`

## Notes

- All functionality preserved - no features removed
- All tests should pass without modification
- URLs and templates unchanged
- Database migrations unaffected (models only reorganized, not changed)

---

**Do not edit files in this directory.** They are kept for historical reference only.

<!-- EOF -->
