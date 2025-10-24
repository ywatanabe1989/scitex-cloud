# Writer App Refactoring Guide

## Overview

The writer_app has been refactored to follow the standard SciTeX app architecture (as defined in `apps/README.md`). This document outlines the changes made.

## Date: 2025-10-24

## Changes Made

### 1. Models Reorganization

**Before:** Single `models.py` file (1503 lines, 20 models)

**After:** Modular structure in `models/` directory

```
models/
├── __init__.py           # Central export point for all models
├── core.py              # DocumentTemplate, Manuscript, ManuscriptSection, Figure, Table, Citation
├── compilation.py       # CompilationJob, AIAssistanceLog
├── collaboration.py     # CollaborativeSession, DocumentChange
├── version_control.py   # ManuscriptVersion, ManuscriptBranch, DiffResult, MergeRequest
└── arxiv.py            # ArxivAccount, ArxivCategory, ArxivSubmission, etc.
```

### 2. Critical Fix: Directory Structure

**Updated project directory structure to match `scitex.project` module:**

- **Before:** `project_path / 'paper'`
- **After:** `project_path / 'scitex' / 'writer'`

This aligns with the standalone `scitex.project` package structure where SciTeX features use `scitex/{feature}/` subdirectories.

**Files changed:**
- `models/core.py`: `get_project_paper_path()` method
- `legacy/models_old.py`: For historical reference

### 3. Legacy Files

Old files moved to `legacy/` directory:
- `legacy/models_old.py` - Original monolithic models file (kept for reference)

## Migration Guide

### For Developers

**Model imports remain the same:**

```python
# This still works
from apps.writer_app.models import Manuscript, CompilationJob, ArxivSubmission

# All models are exported from models/__init__.py
```

**No changes needed in:**
- Views (imports work the same)
- Admin (imports work the same)
- Tests (imports work the same)
- URL patterns (no changes)

### For Database

**No database migrations needed** - this is purely a code reorganization. The Django ORM sees the same models.

## Benefits

### 1. Better Organization
- Models grouped by domain (core, compilation, collaboration, version_control, arxiv)
- Each file is ~100-300 lines (more maintainable)
- Easier to find specific models

### 2. Matches SciTeX Standards
- Follows pattern established in `scholar_app`
- Consistent with `apps/README.md` architecture guidelines
- Uses forward references (string model names) to avoid circular imports

### 3. Correct Directory Structure
- Now uses `scitex/writer/` as per `scitex.project` module
- Compatible with standalone project management
- Proper integration with Django's project system

## File Organization

### Core Models (`models/core.py`)
Main manuscript and document models:
- `DocumentTemplate` - Journal templates
- `Manuscript` - Main document model
- `ManuscriptSection` - Document sections
- `Figure` - Image figures
- `Table` - Data tables
- `Citation` - Bibliography entries

### Compilation Models (`models/compilation.py`)
LaTeX compilation and AI assistance:
- `CompilationJob` - LaTeX compilation tracking
- `AIAssistanceLog` - AI usage logging

### Collaboration Models (`models/collaboration.py`)
Real-time collaborative editing:
- `CollaborativeSession` - Active editing sessions
- `DocumentChange` - Operational transform tracking

### Version Control Models (`models/version_control.py`)
Git-style version management:
- `ManuscriptVersion` - Version snapshots
- `ManuscriptBranch` - Branch management
- `DiffResult` - Diff computation cache
- `MergeRequest` - Branch merging

### arXiv Models (`models/arxiv.py`)
arXiv submission integration:
- `ArxivAccount` - User arXiv credentials
- `ArxivCategory` - Subject categories
- `ArxivSubmission` - Submission tracking
- `ArxivSubmissionHistory` - Status history
- `ArxivValidationResult` - Validation checks
- `ArxivApiResponse` - API logging

## Next Steps

### Recommended Future Improvements

1. **Views Refactoring** (Future)
   - Split `views.py` (3165 lines) into feature modules
   - Create `views/` directory similar to models structure

2. **Services Layer** (Future)
   - Extract business logic from views
   - Create `services/` directory for reusable logic

3. **Template Organization** (Future)
   - Organize templates by feature
   - Move duplicates to `legacy/`

## References

- [SciTeX Apps Architecture](../README.md)
- [Scholar App Refactoring](../../scholar_app/REFACTORING_GUIDE.md)
- [SciTeX Project Module](~/proj/scitex-code/src/scitex/project/README.md)

---

**Refactored by:** Claude Code
**Date:** 2025-10-24
**Architecture Version:** 1.0
