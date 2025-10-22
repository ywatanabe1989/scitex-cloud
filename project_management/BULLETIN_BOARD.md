# SciTeX Development Bulletin Board

**Last Updated:** 2025-10-23 06:10
**Status:** ✅ Model Duplication Resolved - Continuing with Architecture Refactoring

---

## ✅ COMPLETED: Model Duplication Resolution

### Phase 1 Complete (2025-10-23 06:10)
1. **✅ Fixed Migration Errors**
   - Resolved FieldDoesNotExist error during migrations
   - Fixed constraint ordering in migration 0007
   - All migrations now apply successfully

2. **✅ Removed Duplicate Models from core_app**
   - Deleted: Project, ProjectMembership, ProjectPermission, Manuscript, GitFileStatus
   - Added backward-compatible imports from canonical locations
   - Updated admin registrations and inline classes

3. **✅ Created sustainability_app Initial Migration**
   - Donation and DonationTier models migrated successfully
   - Database schema updated

**Commit:** 0c5665a on `refactor/resolve-model-duplication` branch

---

## 🚨 REMAINING: Architecture Issues

### Critical Problems
1. ~~**Model Duplication**: core_app and project_app have DUPLICATE models~~ ✅ RESOLVED
   - ✅ Project, ProjectMembership models moved to project_app
   - ⚠️ Organization, ResearchGroup still duplicated - needs organizations_app extraction

2. **core_app Overloaded** (9 models, 7 services, 5 view modules)
   - Organizations, Projects, Git, Files, Email, Manuscripts
   - Mixes too many concerns

3. **cloud_app Overloaded** (8 models)
   - Auth, Billing, Landing, Resources, Integrations
   - Overlaps with auth_app, sustainability_app, integrations_app

### Immediate Impact
- ✅ Fixed: URL namespace error (core_app now registered)
- ⚠️ Risk: Model conflicts if both apps are active
- ⚠️ Maintainability: Hard to understand which app owns what

---

## Current Phase

🔴 **PHASE 1: CRITICAL REFACTORING REQUIRED**
- Resolve model duplication between core_app and project_app
- Extract Git/GitHub functionality to integrations_app
- Move donations to sustainability_app
- Consolidate auth functionality in auth_app

---

## Completed Tasks

### 1. Scholar App Reorganization ✅
- **Commit:** 735d56d on `refactor/standardize-core-app` branch
- **Changes:** 1,432 → 6 modules, 159 files
- **Status:** Pushed to GitHub, ready for PR
- **Documentation:**
  - `apps/README.md` (Standard architecture)
  - `apps/scholar_app/MODELS_REORGANIZATION.md` (Details)
  - `apps/REORGANIZATION_RECOMMENDATIONS.md` (Other apps)

### 2. Critical Fixes ✅
- Fixed EmailService import in auth_app
- Django check: No errors
- All apps loading correctly

---

## Quick Wins (High Priority)

### Performance Improvements
1. **Add Query Optimization** (5 apps missing select_related/prefetch_related)
   - code_app, integrations_app, profile_app, search_app, social_app
   - Low effort, high impact

2. **Background Task Migration** (Writer app)
   - Move LaTeX compilation to task queue
   - 5 TODO items identified
   - Improves response time significantly

### Test Coverage
1. **Add Missing Tests** (5 apps)
   - code_app, integrations_app, profile_app, search_app, social_app
   - Critical for reliability

---

## Refactoring Plan: core_app & cloud_app

### Phase 1: Resolve Model Duplication (CRITICAL) 🔴
**Problem:** core_app and project_app both define same models
**Decision needed:** Which app should own these models?
   - Option A: Keep in project_app (more specific), deprecate core_app models
   - Option B: Keep in core_app (more general), migrate project_app to use them
   - Option C: Create new org_app for Organization/ResearchGroup models

**Affected models:**
- Project, ProjectMembership, ProjectPermission
- Organization, ResearchGroup (membership)

**Action required:** Check database migrations to see which is canonical

### Phase 2: Extract Git/GitHub to integrations_app 🟡
**Move from core_app:**
- GitFileStatus model
- views/github_views.py (OAuth, repo management)
- services/git_service.py
- services/gitea_sync_service.py

**Benefits:** Clean separation, integrations_app is proper home

### Phase 3: Move Donations to sustainability_app 🟡
**Move from cloud_app:**
- Donation, DonationTier models
- Related donation views

**Note:** sustainability_app already exists - this is clearly its domain!

### Phase 4: Consolidate Auth 🟢
**Move from cloud_app to auth_app:**
- EmailVerification model
- Auth-related views (signup, login, logout)

**Move from cloud_app to integrations_app:**
- ServiceIntegration, APIKey models

### Phase 5: Manuscript Model 🟢
**Move from core_app to writer_app:**
- Manuscript model
- writer_app already handles papers/documents

---

## Next Architecture Tasks (Updated Priority)

### CRITICAL (Do First)
1. ⚠️ **Resolve Model Duplication** - core_app vs project_app
   - Investigate which is canonical source
   - Create migration plan
   - Update all imports across codebase
   - Estimated: 6-8 hours

### High Priority
2. **Extract Git/GitHub** - core_app → integrations_app
   - Clean separation of concerns
   - Estimated: 3-4 hours

3. **Move Donations** - cloud_app → sustainability_app
   - Already has proper app
   - Estimated: 2-3 hours

### Medium Priority
4. **Consolidate Auth** - cloud_app → auth_app
   - Estimated: 2-3 hours

5. **Core App Internal Reorganization**
   - After extractions, organize remaining code
   - Follow scholar_app pattern
   - Estimated: 4-6 hours

6. **Writer App Reorganization**
   - Largest (1,503 lines, 20 models)
   - Estimated: 6-8 hours

---

## Technical Debt Summary

### TODOs by App
- **writer_app:** 5 TODOs (async/task queue)
- **scholar_app:** 2 TODOs (author creation, citation API)

### Missing Optimizations
- Query optimization (5 apps)
- Test coverage (5 apps)
- Celery/task queue integration (1 app)

### Production Readiness
- Security settings need tuning (DEBUG, SECURE_*, etc.)
- Deploy checklist: See `--deploy` warnings

---

## Repository Status

**Branch:** `refactor/standardize-auth-app` (develop)
**Remote:** `refactor/standardize-core-app` (pushed)
**PR Ready:** Yes, open at GitHub for review

**Recent Changes:**
- Scholar app models/views/services organized
- Core app services layer created
- Documentation comprehensive

---

## Recommendations

### For Next Session
1. ✅ Fix remaining bugs (EmailService - done)
2. 📝 Add query optimizations to 5 apps (quick win)
3. 🧪 Implement missing test suites
4. 📊 Consider core_app reorganization
5. 🚀 Prepare for V1.1 feature release

### Build Schedule
- **This week:** Polish & test
- **Next week:** Core app reorganization
- **Following:** Writer app reorganization
- **Before launch:** Full test coverage + performance tuning

---

## Key Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Apps | 17 | ✅ All loaded |
| Models | 73 | 28 organized (scholar_app) |
| Lines of Code | ~50K | Clean & organized |
| Test Coverage | Partial | 10/17 apps have tests |
| Performance Issues | Identified | Ready to fix |
| Documentation | Complete | Architecture documented |

---

**Ready for:** Critical refactoring of core_app and cloud_app

---

## Detailed Analysis: Model Duplication Investigation

### Models in BOTH core_app AND project_app:
1. **Project** - Full project model with metadata
2. **ProjectMembership** - User membership in projects
3. **ProjectPermission** - Permission management
4. **Organization** - Institution/organization model
5. **ResearchGroup** - Research group model

### Additional models:
- **core_app only:** GitFileStatus, Manuscript, ResearchGroupMembership, OrganizationMembership
- **project_app only:** (Need to verify if truly unique)

### Investigation needed:
```bash
# Check which app's migrations were created first
ls -la apps/core_app/migrations/ | grep -E "000[0-9]_"
ls -la apps/project_app/migrations/ | grep -E "000[0-9]_"

# Check which models are actually being used in INSTALLED_APPS
# Check settings for app order
```

### Recommendation:
Based on Django best practices and SciTeX architecture:
- **Keep in project_app**: Project, ProjectMembership, ProjectPermission (project-specific)
- **Keep in core_app**: Organization, ResearchGroup, OrganizationMembership, ResearchGroupMembership (broader scope)
- **OR** Consider creating dedicated apps:
  - `organizations_app` for Organization/ResearchGroup models
  - Keep Project models in `project_app`

---

## Session Summary (2025-10-23 04:30)

### ✅ Completed
1. Fixed `'core_app' is not a registered namespace` error
   - Updated 10 import statements across core_app
   - Fixed views package structure
   - Namespace now successfully registered at `/core/`

2. Analyzed core_app and cloud_app responsibilities
   - Identified critical model duplication
   - Mapped overlapping concerns
   - Created 5-phase refactoring plan

3. Updated BULLETIN_BOARD.md with findings
   - Elevated priority to CRITICAL
   - Documented all issues
   - Created actionable migration plan

### ⚠️ Critical Issues Identified
1. **Model duplication** between core_app and project_app
2. **core_app too large** - mixing 6+ different domains
3. **cloud_app overlaps** with auth_app, sustainability_app, integrations_app

### 📋 Next Actions Required

**DECISION MADE:** Use `project_app` as canonical source for Project models

1. ✅ **COMPLETED:** Investigation complete - See MODEL_DUPLICATION_DECISION.md
   - 92% of imports use project_app (25 vs 2)
   - project_app is better domain owner
   - Only 3 files need updating (vs 22 if we used core_app)

2. **READY TO EXECUTE:** Phase 1 - Update 3 files to use project_app
   - apps/profile_app/models.py
   - apps/project_app/views.py
   - apps/core_app/management/commands/create_sample_data.py
   - Estimated: 2-3 hours

3. **NEXT:** Create organizations_app for Organization/ResearchGroup models
   - Extract from both core_app and project_app
   - Clean separation of concerns
   - Estimated: 4-6 hours

4. **THEN:** Extract Git/GitHub to integrations_app
5. **THEN:** Move donations to sustainability_app
6. **THEN:** Consolidate auth in auth_app

---

## Investigation Summary (2025-10-23 04:45)

### Model Duplication Analysis ✅

**Finding:** core_app and project_app both have 5 duplicate models
- Both migrations created same day (2025-10-15 14:13)
- core_app loads first in INSTALLED_APPS (index 13 vs 20)
- BUT 92% of codebase uses project_app.models

**Evidence:**
```
Imports from project_app: 25 occurrences across 22 files
Imports from core_app:     2 occurrences across 3 files
```

**Decision:** Use project_app as canonical source ✅
- See `MODEL_DUPLICATION_DECISION.md` for full analysis
- Migration plan ready
- Implementation checklist prepared

---

<!-- EOF -->
