<!-- ---
!-- Timestamp: 2025-11-04
!-- File: /home/ywatanabe/proj/scitex-cloud/REFACTORING_PRIORITY_SUMMARY.md
!-- Author: Claude Code Analysis
!-- --- -->

# Project App Refactoring - Priority Summary

Quick reference for immediate refactoring work on project_app.

---

## Prioritized Work Items

### PRIORITY 1: CRITICAL - Create Forms Directory (SMALL - 3-4 hours)

**Status**: Ready to start immediately
**Impact**: Fills critical gap in FULLSTACK compliance

#### Issue
- No `forms/` directory exists
- Form handling scattered across view files
- FULLSTACK requires centralized forms layer

#### Deliverables
- [ ] Create `forms/` directory structure
- [ ] Create `forms/repository/` with file forms
- [ ] Create `forms/pull_requests/` with PR forms
- [ ] Create `forms/issues/` with issue forms
- [ ] Create `forms/shared/` with common forms
- [ ] Extract forms from `views/issues/form.py`
- [ ] Extract forms from `views/pull_requests/form.py`
- [ ] Update all view imports
- [ ] Update `forms/__init__.py` with exports

#### Work Estimate
- Directory creation: 30 min
- Extract issue forms: 1 hour
- Extract PR forms: 1 hour
- Extract other forms: 30 min
- Update imports: 1 hour
- **Total: 4 hours**

---

### PRIORITY 2: HIGH - Consolidate Legacy View Files (MEDIUM-LARGE - 6-8 hours)

**Status**: Ready after forms directory complete
**Impact**: Reduces code duplication, improves organization

#### Current Issue
12 legacy flat view files (6,186 lines total):
- `directory_views.py` (1088 lines) → `views/repository/`
- `project_views.py` (977 lines) → `views/projects/`
- `pr_views.py` (895 lines) → `views/pull_requests/`
- `issues_views.py` (595 lines) → `views/issues/`
- `api_issues_views.py` (453 lines) → `views/issues/api.py`
- `api_views.py` (559 lines) → distribute by feature
- `actions_views.py` (644 lines) → split/consolidate
- `security_views.py` (438 lines) → review
- `settings_views.py` (185 lines) → `views/projects/settings.py`
- `collaboration_views.py` (108 lines) → extract/consolidate
- `integration_views.py` (70 lines) → review
- Plus legacy view imports in `views/__init__.py`

#### Deliverables
- [ ] Move directory browsing → `views/repository/`
- [ ] Move project CRUD → `views/projects/` (merge with existing)
- [ ] Move PR views → `views/pull_requests/` (merge with existing)
- [ ] Move issue views → `views/issues/` (merge with existing)
- [ ] Move action views → `views/actions/` (or consolidate)
- [ ] Move settings → appropriate feature modules
- [ ] Consolidate API views by feature
- [ ] Delete legacy flat files
- [ ] Update `views/__init__.py` imports
- [ ] Fix `urls/__init__.py` imports

#### Work Estimate
- Analyze legacy files: 1 hour
- Consolidate directory_views.py: 2 hours
- Consolidate project/PR/issue views: 2 hours
- Update imports everywhere: 1.5 hours
- Test and fix issues: 1.5 hours
- **Total: 8 hours**

---

### PRIORITY 3: HIGH - Reorganize Services into Feature Groups (LARGE - 8-12 hours)

**Status**: Ready after view consolidation
**Impact**: Enables reusable services, FULLSTACK correspondence

#### Current Issue
Flat structure with no feature grouping (4,762 lines):
- `project_filesystem.py` (1106 lines - OVERSIZED)
- `security_scanning.py` (574 lines)
- `filesystem_utils.py` (456 lines)
- `visitor_pool.py` (455 lines)
- `email_service.py` (334 lines)
- `git_service.py` (331 lines)
- `demo_project_pool.py` (305 lines)
- `anonymous_storage.py` (266 lines)
- `repository_health_service.py` (257 lines)
- `language_detector.py` (203 lines)
- `project_utils.py` (155 lines)
- `gitea_sync_service.py` (116 lines)

#### Deliverables
- [ ] Create `services/repository/` with:
  - `file_service.py` (split from project_filesystem.py)
  - `git_service.py` (move)
  - `health_service.py` (rename from repository_health_service.py)
  - `language_detector.py` (move)

- [ ] Create `services/pull_requests/` with:
  - `pr_service.py` (new)

- [ ] Create `services/issues/` with:
  - `issue_service.py` (new)

- [ ] Create `services/workflows/` with:
  - `workflow_service.py` (new)

- [ ] Create `services/security/` with:
  - `security_service.py` (rename from security_scanning.py)

- [ ] Create `services/infrastructure/` with:
  - `email_service.py` (move)
  - `storage_service.py` (rename from anonymous_storage.py)
  - `sync_service.py` (rename from gitea_sync_service.py)
  - `filesystem_utils.py` (move)
  - `pool_managers/` subdirectory with:
    - `visitor_pool.py` (move)
    - `demo_project_pool.py` (move)

- [ ] Split `project_filesystem.py` into focused modules
- [ ] Create proper `services/__init__.py` with exports
- [ ] Update all imports in views, models, management commands

#### Work Estimate
- Create directory structure: 1 hour
- Split project_filesystem.py: 2 hours
- Move and organize services: 2 hours
- Create new service files: 2 hours
- Update imports throughout codebase: 3-4 hours
- Test and fix issues: 2 hours
- **Total: 12 hours**

---

### PRIORITY 4: MEDIUM - Refactor Models (MEDIUM - 4-5 hours)

**Status**: Ready after services reorganization
**Impact**: Perfect feature-based organization

#### Current Issue
- `core.py` is 1001 lines (exceeds 300-line limit)
- `actions.py` mixed model types (should be workflows/)
- Not truly feature-based (domain-based instead)

#### Deliverables
- [ ] Create `models/repository/` with:
  - `project.py` (extract from core.py)
  - `project_membership.py` (extract from core.py)

- [ ] Create `models/workflows/` with:
  - `workflow.py` (extract from actions.py)
  - `workflow_run.py` (extract from actions.py)
  - `workflow_job.py` (extract from actions.py)

- [ ] Create `models/shared/` with:
  - `permissions.py` (extract from core.py)
  - `visitor_allocation.py` (extract from core.py)

- [ ] Rename `models/pull_requests.py` → use existing structure
- [ ] Rename `models/issues.py` → use existing structure
- [ ] Keep `models/collaboration.py` as-is (< 300 lines)

- [ ] Update `models/__init__.py` with new export paths
- [ ] Update all imports in services, views, forms

#### Work Estimate
- Analyze and split core.py: 1.5 hours
- Split actions.py: 1 hour
- Reorganize structure: 1 hour
- Update imports: 1 hour
- Test and verify: 30 min
- **Total: 5 hours**

---

### PRIORITY 5: LOW - Update URL Imports (LOW - 1-2 hours)

**Status**: Ready after all consolidations
**Impact**: Code clarity

#### Deliverables
- [ ] Update `urls/__init__.py` to import from organized views
- [ ] Remove imports from legacy flat files
- [ ] Verify all URL patterns still work
- [ ] Test with browser/selenium

#### Work Estimate
- Update imports: 1 hour
- Test routing: 30 min
- Fix issues: 30 min
- **Total: 2 hours**

---

## SUMMARY TABLE

| Priority | Task | Effort | Status | Start After |
|----------|------|--------|--------|------------|
| P0 | Create forms/ directory | SMALL (4h) | Ready | None |
| P1 | Consolidate view files | MEDIUM-LARGE (8h) | Ready | Forms |
| P1 | Reorganize services | LARGE (12h) | Ready | Views |
| P2 | Refactor models | MEDIUM (5h) | Ready | Services |
| P2 | Update URL imports | LOW (2h) | Ready | All |

**Total Effort: ~31 hours (~1 week)**

---

## Quick Start Commands

### Phase 1: Forms (4 hours)
```bash
# Create directory structure
mkdir -p apps/project_app/forms/{repository,pull_requests,issues,shared}
touch apps/project_app/forms/__init__.py
touch apps/project_app/forms/repository/__init__.py
touch apps/project_app/forms/pull_requests/__init__.py
touch apps/project_app/forms/issues/__init__.py
touch apps/project_app/forms/shared/__init__.py

# Then extract forms from existing view files
# and update imports in views
```

### Phase 2: Views (8 hours)
```bash
# Review legacy files
wc -l apps/project_app/views/*.py | sort -rn

# Move content from legacy files to organized structure
# Update views/__init__.py to remove legacy imports
# Update urls/__init__.py imports
# Delete legacy files after verification
```

### Phase 3: Services (12 hours)
```bash
# Create service structure
mkdir -p apps/project_app/services/{repository,pull_requests,issues,workflows,security,infrastructure/pool_managers}

# Move files and split oversized ones
# Update imports everywhere: grep -r "from.*services\." apps/project_app/
```

### Phase 4: Models (5 hours)
```bash
# Create model structure
mkdir -p apps/project_app/models/{repository,workflows,shared}

# Split core.py and actions.py
# Update models/__init__.py
```

---

## Completion Criteria

After refactoring, verify:

1. **No files > 300 lines** in models, services, views
2. **Feature-based directory structure** at all layers
3. **Perfect 1:1:1:1 correspondence**:
   - View has corresponding service
   - Service has corresponding model
   - Template has corresponding CSS and TypeScript
4. **All tests passing**: `pytest apps/project_app/tests/`
5. **No import errors**: `python manage.py check`
6. **URL routing works**: Manual browser testing
7. **FULLSTACK compliance > 95%**

---

## Git Strategy

**Recommended**: Create feature branch for each phase
```bash
git checkout -b refactor/forms
# ... complete forms phase
git commit -m "feat(forms): Create forms directory structure and consolidate forms

- Create forms/ directory with feature-based organization
- Extract issue forms from views/issues/form.py
- Extract PR forms from views/pull_requests/form.py
- Update all view imports

This establishes the foundation for complete FULLSTACK compliance."

# Then merge and move to next phase
```

---

**Last Updated**: 2025-11-04
**Estimated Completion**: 1 week of focused work
**Overall Impact**: 95%+ FULLSTACK compliance

<!-- EOF -->
