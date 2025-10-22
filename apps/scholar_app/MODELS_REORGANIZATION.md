# Scholar App Models Reorganization

**Date:** 2025-10-23
**Migration:** `0011_remove_bibtexenrichmentjob_original_filename_and_more`

---

## Summary

Successfully reorganized scholar_app models from a single 1,432-line `models.py` file into a clean modular structure with 6 domain-specific modules containing 26 models.

## Structure

### Before
```
scholar_app/
└── models.py  (1,432 lines, 26 models mixed together)
```

### After
```
scholar_app/models/
├── __init__.py          # Central export point
├── core.py             # 6 models: Author, Journal, Topic, SearchIndex, AuthorPaper, Citation
├── search.py           # 4 models: SearchQuery, SearchResult, SearchFilter, SavedSearch
├── library.py          # 4 models: Collection, UserLibrary, LibraryExport, RecommendationLog
├── collaboration.py    # 6 models: Annotation, AnnotationReply, AnnotationVote, etc.
├── bibtex.py          # 1 model: BibTeXEnrichmentJob
└── repository.py       # 6 models: Repository, Dataset, DatasetFile, etc.
```

**Total:** 1,533 lines across 7 files (including __init__.py)

## Domain Organization

### Core Models (core.py)
Core entities for academic papers and metadata:
- `Author` - Research paper authors
- `Journal` - Journal metadata
- `Topic` - Research topics/keywords
- `SearchIndex` - Main paper index
- `AuthorPaper` - Author-paper relationships
- `Citation` - Paper citations

### Search Models (search.py)
Search and discovery functionality:
- `SearchQuery` - User search queries
- `SearchResult` - Search results
- `SearchFilter` - Active filters
- `SavedSearch` - Saved searches

### Library Models (library.py)
Personal library and collections:
- `Collection` - User collections
- `UserLibrary` - Personal library
- `LibraryExport` - Export tracking
- `RecommendationLog` - AI recommendations

### Collaboration Models (collaboration.py)
Annotations and group collaboration:
- `Annotation` - Paper annotations
- `AnnotationReply` - Annotation replies
- `AnnotationVote` - Voting on annotations
- `AnnotationTag` - Annotation tags
- `CollaborationGroup` - Research groups
- `GroupMembership` - Group membership

### BibTeX Models (bibtex.py)
BibTeX enrichment:
- `BibTeXEnrichmentJob` - Job tracking

### Repository Models (repository.py)
Data repository integration:
- `Repository` - Repository configurations
- `RepositoryConnection` - User connections
- `Dataset` - Research datasets
- `DatasetFile` - Dataset files
- `DatasetVersion` - Version tracking
- `RepositorySync` - Sync operations

## Key Changes

### 1. String References for ForeignKey
All cross-module ForeignKey relationships use string references to avoid circular imports:

```python
# ✓ Good - String reference
paper = models.ForeignKey('SearchIndex', on_delete=models.CASCADE)

# ✗ Bad - Direct import (causes circular dependency)
from .core import SearchIndex
paper = models.ForeignKey(SearchIndex, on_delete=models.CASCADE)
```

### 2. Central Export Point
`models/__init__.py` exports all models for clean imports:

```python
from .core import Author, SearchIndex, ...
from .search import SearchQuery, ...

__all__ = ['Author', 'SearchIndex', 'SearchQuery', ...]
```

Usage remains the same:
```python
from apps.scholar_app.models import SearchIndex  # Still works!
```

### 3. Fixed Nullable Fields
- Added `null=True` to `BibTeXEnrichmentJob.project_name` (it was `blank=True` but not nullable)

### 4. Updated Import References
Fixed views that imported `Paper` (legacy name):
- `export_views.py`: `from ..models import SearchIndex as Paper`
- `library_views.py`: `from ..models import SearchIndex as Paper`

### 5. Fixed Service Exports
Updated `services/__init__.py` to only export functions that actually exist:
- DOI services: `auto_assign_doi_on_publish`, `validate_and_format_doi`, `get_doi_metadata`
- Repository services: `sync_dataset_with_repository`, `upload_dataset_to_repository`

## Migration

**File:** `apps/scholar_app/migrations/0011_remove_bibtexenrichmentjob_original_filename_and_more.py`

**Changes:**
- Removed `original_filename` from `BibTeXEnrichmentJob`
- Removed `processing_log` from `BibTeXEnrichmentJob`
- Made `project_name` properly nullable

## Verification

✓ Django check passes with no errors
✓ All migrations applied successfully
✓ Models import correctly: `from apps.scholar_app.models import SearchIndex`
✓ No circular import issues
✓ All 26 models accessible

## Legacy Code

Old code moved to `legacy/`:
- `legacy/models_old.py` (56,725 bytes) - Original models.py
- `legacy/bibtex_models_old.py` (3,825 bytes) - Original bibtex_models.py

## Documentation Updates

Updated `apps/README.md` with:
- When to use `models/` directory (10+ models)
- Organization pattern examples
- String reference best practices
- Reference to scholar_app implementation

## Benefits

1. **Improved Maintainability** - Each domain is self-contained
2. **Better Navigation** - Easy to find models by domain
3. **Clearer Boundaries** - Explicit separation of concerns
4. **Scalability** - Easy to add new models in appropriate modules
5. **Team Collaboration** - Reduced merge conflicts
6. **Documentation** - Module docstrings explain domain purpose

## Related Files

- `apps/README.md` - Updated architecture documentation
- `apps/scholar_app/admin.py` - Imports updated
- `apps/scholar_app/views/` - Import references fixed
- `apps/scholar_app/services/__init__.py` - Export list corrected

---

**Reference Implementation**

This reorganization establishes scholar_app as the reference implementation for SciTeX apps with complex models. Other apps should follow this pattern when they exceed 10 models or 500 lines in models.py.

<!-- EOF -->
