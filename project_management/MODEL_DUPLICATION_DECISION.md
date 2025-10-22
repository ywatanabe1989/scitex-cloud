# Model Duplication Decision Document

**Created:** 2025-10-23 04:45
**Decision Status:** RECOMMENDATION READY
**Priority:** CRITICAL 🔴

---

## Executive Summary

**RECOMMENDATION: Use `project_app` as canonical source for Project models**

**Rationale:**
1. **Codebase preference:** 25 imports use project_app vs 2 use core_app (92% consensus)
2. **Domain ownership:** Project models belong in project_app by name and purpose
3. **Lower migration effort:** Fewer files to update (only 3 files vs 22 files)

---

## Investigation Findings

### 1. Migration Analysis

Both apps have **identical creation date** in migrations:
- `core_app/migrations/0001_initial.py`: Generated 2025-10-15 14:13
- `project_app/migrations/0001_initial.py`: Generated 2025-10-15 14:13

**Models created:**
- **core_app (10 models):** GitFileStatus, Manuscript, Organization, OrganizationMembership, Project, ProjectMembership, ProjectPermission, ResearchGroup, ResearchGroupMembership, UserProfile
- **project_app (5 models):** Organization, Project, ProjectMembership, ProjectPermission, ResearchGroup

**Duplicated models (5):**
1. Project
2. ProjectMembership
3. ProjectPermission
4. Organization
5. ResearchGroup

### 2. INSTALLED_APPS Order

```python
INSTALLED_APPS = [
    # ... Django apps ...
    'apps.core_app',      # Index 13 - LOADED FIRST
    'apps.project_app',   # Index 20 - Loaded second
]
```

**Impact:** Django uses `core_app` models as canonical in the database, but the codebase mostly imports from `project_app`.

**⚠️ CRITICAL ISSUE:** This mismatch creates confusion and potential bugs!

### 3. Import Usage Analysis

#### Imports FROM project_app.models (25 occurrences in 22 files):
```
apps/code_app/project_views.py
apps/code_app/views/project_views.py
apps/core_app/context_processors.py
apps/core_app/management/commands/create_sample_data.py
apps/core_app/services/utils/model_imports.py
apps/core_app/views/core_views.py
apps/core_app/views/directory_views.py
apps/core_app/views/native_file_views.py
apps/integrations_app/services/slack_service.py
apps/integrations_app/views.py
apps/permissions_app/decorators.py
apps/project_app/management/commands/create_guest_project.py
apps/scholar_app/views/bibtex_views.py
apps/scholar_app/views/project_views.py
apps/scholar_app/views/search_views.py
apps/search_app/tests.py
apps/search_app/views.py
apps/social_app/models.py
apps/social_app/tests.py
apps/social_app/views.py
apps/viz_app/project_views.py
apps/writer_app/views.py
```

#### Imports FROM core_app.models (2 occurrences in 3 files):
```
apps/core_app/management/commands/create_sample_data.py (imports both!)
apps/profile_app/models.py
apps/project_app/views.py
```

**Key insight:** Even `core_app` itself mostly uses `project_app.models`!

---

## Decision Matrix

### Option A: Use project_app as canonical ✅ RECOMMENDED

**Pros:**
- ✅ Aligns with actual codebase usage (92% of imports)
- ✅ Clear domain ownership (Project belongs in project_app)
- ✅ Less refactoring work (update 3 files instead of 22)
- ✅ Better separation of concerns
- ✅ Follows Django best practices (specific > general)

**Cons:**
- ⚠️ Need to update INSTALLED_APPS order
- ⚠️ Database migrations required
- ⚠️ core_app models must be deprecated

**Migration effort:** LOW-MEDIUM
- Update 3 files to use project_app imports
- Reorder INSTALLED_APPS (move project_app before core_app)
- Create migration to transfer data if needed
- Remove models from core_app

### Option B: Use core_app as canonical ❌ NOT RECOMMENDED

**Pros:**
- ✅ Already first in INSTALLED_APPS
- ✅ No INSTALLED_APPS changes needed

**Cons:**
- ❌ Against codebase convention (only 8% use core_app)
- ❌ Poor domain ownership (Project in "core"?)
- ❌ Much more refactoring (22 files to update)
- ❌ Confusing for developers
- ❌ core_app already too large

**Migration effort:** HIGH
- Update 22 files across 11 different apps
- High risk of missing imports
- Perpetuates core_app bloat

### Option C: Create new dedicated app ⚠️ OVER-ENGINEERING

**Pros:**
- ✅ Clean separation
- ✅ Could split Organizations to separate app

**Cons:**
- ❌ Creates yet another app
- ❌ Most refactoring work (all files)
- ❌ Not necessary - project_app is perfect fit
- ❌ Adds complexity

**Migration effort:** VERY HIGH

---

## RECOMMENDED SOLUTION

### Phase 1: Immediate Fix (Day 1-2)

#### Step 1: Update the 3 files using core_app imports

**Files to update:**
1. `apps/profile_app/models.py`
2. `apps/project_app/views.py`
3. `apps/core_app/management/commands/create_sample_data.py`

**Change:**
```python
# OLD
from apps.core_app.models import Project, Organization

# NEW
from apps.project_app.models import Project, Organization
```

#### Step 2: Deprecate core_app models

Add deprecation notice in `apps/core_app/models.py`:
```python
import warnings

class Project(models.Model):
    """
    DEPRECATED: This model is duplicated.
    Use apps.project_app.models.Project instead.
    This model will be removed in the next version.
    """
    class Meta:
        db_table = 'project_app_project'  # Point to project_app table

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "core_app.Project is deprecated. Use project_app.Project instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)
```

#### Step 3: Update admin.py

Ensure only one app registers these models in admin.

### Phase 2: Model Reorganization (Day 3-4)

#### Step 1: Create organizations_app

The Organization and ResearchGroup models are distinct domain:
```bash
python manage.py startapp organizations_app apps/organizations_app
```

#### Step 2: Move Organization models

**From both apps to organizations_app:**
- Organization
- OrganizationMembership (from core_app)
- ResearchGroup
- ResearchGroupMembership (from core_app)

#### Step 3: Keep in project_app

- Project
- ProjectMembership
- ProjectPermission

### Phase 3: Database Migration (Day 5)

#### Option A: Django managed_models approach
```python
# In core_app/models.py
class Project(models.Model):
    class Meta:
        managed = False
        db_table = 'project_app_project'
```

#### Option B: Delete and recreate migrations
1. Backup database
2. Delete core_app model definitions
3. Create new migrations
4. Apply migrations

---

## Implementation Checklist

### Pre-flight
- [ ] Create feature branch: `refactor/resolve-model-duplication`
- [ ] Backup database
- [ ] Run full test suite to establish baseline

### Phase 1: Immediate fixes
- [ ] Update `apps/profile_app/models.py` imports
- [ ] Update `apps/project_app/views.py` imports
- [ ] Update `apps/core_app/management/commands/create_sample_data.py` imports
- [ ] Add deprecation warnings to core_app models
- [ ] Run tests
- [ ] Commit: "fix: Use project_app as canonical source for Project models"

### Phase 2: Create organizations_app
- [ ] Create `apps/organizations_app/`
- [ ] Move Organization, ResearchGroup models
- [ ] Update INSTALLED_APPS
- [ ] Create migrations
- [ ] Update all imports (Organization/ResearchGroup)
- [ ] Run tests
- [ ] Commit: "feat: Create organizations_app for Organization/ResearchGroup models"

### Phase 3: Clean up core_app
- [ ] Remove Project, ProjectMembership, ProjectPermission from core_app
- [ ] Remove Organization, ResearchGroup from core_app
- [ ] Update admin.py
- [ ] Run tests
- [ ] Commit: "refactor: Remove duplicate models from core_app"

### Phase 4: Verification
- [ ] Run full test suite
- [ ] Check database migrations
- [ ] Verify no deprecation warnings
- [ ] Update documentation
- [ ] Manual testing of key workflows

---

## Risk Assessment

### High Risk
- **Data loss** during migration
  - Mitigation: Database backup before each phase
  - Mitigation: Test on dev environment first

### Medium Risk
- **Broken imports** after changes
  - Mitigation: Use IDE refactoring tools
  - Mitigation: Comprehensive test suite

### Low Risk
- **Admin interface** confusion
  - Mitigation: Clear model verbose names
  - Mitigation: Update admin.py

---

## Success Criteria

- [ ] Zero model duplication
- [ ] All imports use correct canonical source
- [ ] All tests passing
- [ ] No deprecation warnings
- [ ] Database migrations successful
- [ ] Clear documentation of model ownership

---

## Timeline

**Week 1:**
- Day 1: Phase 1 (update imports)
- Day 2: Phase 2 (organizations_app)
- Day 3: Phase 3 (clean up core_app)
- Day 4: Testing and verification
- Day 5: Buffer for issues

**Total effort:** 3-5 days

---

## Next Steps

1. **IMMEDIATE:** Review this decision document
2. **IMMEDIATE:** Get approval to proceed
3. **START:** Create feature branch
4. **START:** Database backup
5. **EXECUTE:** Phase 1 implementation

---

**Decision made by:** Claude Code Analysis
**Decision date:** 2025-10-23
**Implementation priority:** CRITICAL

<!-- EOF -->
