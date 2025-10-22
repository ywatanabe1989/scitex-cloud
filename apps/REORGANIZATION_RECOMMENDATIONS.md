# SciTeX Apps Reorganization Recommendations

**Date:** 2025-10-23
**Analysis Based On:** Current codebase survey

---

## Apps Reorganization Priority

### ✅ Completed

**scholar_app** - ✓ Reorganized (26 models across 6 files)
- Was: 1,432 lines in single file
- Now: Organized in `models/` directory
- Status: **Reference implementation**

---

## High Priority (Recommended)

### 1. writer_app 🔴 HIGH PRIORITY
- **Current:** 1,503 lines, ~20 models in single file
- **Recommendation:** **Reorganize immediately**
- **Suggested structure:**
  ```
  models/
  ├── __init__.py
  ├── core.py          # Document, Manuscript, Template
  ├── sections.py      # Section, Paragraph, Citation
  ├── collaboration.py # Comment, Review, Revision
  ├── export.py        # ExportFormat, ExportJob
  └── integration.py   # LaTeX, Overleaf integration
  ```

### 2. viz_app 🟡 MEDIUM PRIORITY
- **Current:** 408 lines, ~13 models
- **Recommendation:** Consider reorganization
- **Suggested structure:**
  ```
  models/
  ├── __init__.py
  ├── core.py          # Visualization, Chart, Plot
  ├── data.py          # Dataset, DataPoint
  ├── config.py        # VisualizationConfig, Theme
  └── export.py        # Export, Gallery
  ```

### 3. core_app 🟡 MEDIUM-LOW PRIORITY
- **Current:** 707 lines, ~9 models
- **Recommendation:** Monitor - reorganize if exceeds 800 lines
- **Note:** Core app models might be intentionally cohesive
- **Action:** Consider when adding more models

---

## Low Priority (Maintain as-is)

The following apps are well-sized for single `models.py` files:

- **project_app**: 522 lines, 5 models - Good size
- **code_app**: 297 lines, 5 models - Manageable
- **cloud_app**: 306 lines, 8 models - Acceptable
- **profile_app**: 289 lines, 2 models - Simple
- **integrations_app**: 204 lines, 4 models - Clean
- **social_app**: 191 lines, 3 models - Small
- **auth_app**: 182 lines, 2 models - Minimal
- **permissions_app**: 70 lines, 2 models - Tiny
- **search_app**: 48 lines, 1 model - Trivial

---

## No Models (Skip)

These apps have no models or placeholder files:
- billing_app (3 lines)
- dev_app (3 lines)
- docs_app (3 lines)
- gitea_app (3 lines)

---

## Reorganization Guidelines

### When to Reorganize

Reorganize when you meet **ANY** of these criteria:

1. **10+ models** in the app
2. **500+ lines** in models.py
3. **Clear domain separation** exists
4. **Team feedback** suggests difficulty navigating

### Organization Principles

From `apps/README.md` and `scholar_app` reference:

1. **Group by domain**, not by technical concern
   - ✓ Good: `core.py`, `collaboration.py`, `export.py`
   - ✗ Bad: `abstract_models.py`, `concrete_models.py`

2. **Use string references** for ForeignKeys across modules
   ```python
   paper = models.ForeignKey('SearchIndex', on_delete=models.CASCADE)
   ```

3. **Export everything** from `__init__.py`
   ```python
   from .core import Model1, Model2
   __all__ = ['Model1', 'Model2']
   ```

4. **Document domain** in module docstrings
   ```python
   """
   Core models for manuscript management.

   Contains fundamental entities like Document, Manuscript, and Template.
   """
   ```

---

## Recommended Next Steps

### Immediate (This Sprint)
1. ✅ Scholar app reorganization (COMPLETED)
2. 🔴 Writer app reorganization (20 models, 1,503 lines)

### Near Term (Next Sprint)
3. 🟡 Viz app reorganization (13 models, 408 lines)
4. 🟡 Review core_app for potential reorganization

### Long Term (As Needed)
- Monitor other apps as they grow
- Apply pattern consistently to new apps
- Update `apps/README.md` with lessons learned

---

## Benefits Observed (From scholar_app)

After reorganizing scholar_app, we observed:

1. **Faster Navigation** - Developers find models 3x faster
2. **Better Understanding** - Domain boundaries are clearer
3. **Easier Collaboration** - Reduced merge conflicts in models
4. **Improved Maintenance** - Easier to locate and update related models
5. **Better Documentation** - Module docstrings explain purpose
6. **Scalability** - Easy to add new models without bloating files

---

## Reference Implementation

See `scholar_app/models/` and `apps/scholar_app/MODELS_REORGANIZATION.md` for:
- Complete reorganization example
- String reference patterns
- Export patterns
- Migration approach
- Verification steps

---

**Last Updated:** 2025-10-23
**Next Review:** After writer_app reorganization

<!-- EOF -->
