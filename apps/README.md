# SciTeX Apps Architecture

**Version:** 1.0
**Reference Implementation:** `scholar_app`
**Last Updated:** 2025-10-23

---

## Overview

This document defines the standard directory structure for all SciTeX Django apps. Following this structure ensures consistency, maintainability, and scalability across the entire ecosystem.

## Standard App Structure

```
{app_name}/
├── 📁 api/                     # API layer (REST endpoints)
│   ├── __init__.py
│   ├── serializers.py         # DRF serializers
│   ├── viewsets.py            # DRF ViewSets
│   └── permissions.py         # API permissions
│
├── 📁 views/                   # View layer (web pages)
│   ├── __init__.py
│   ├── {feature}_views.py     # Feature views
│   └── workspace_views.py     # Workspace views
│
├── 📁 services/                # Business logic layer
│   ├── __init__.py
│   ├── {domain}_service.py    # Domain services
│   └── utils.py               # Shared utilities
│
├── 📁 integrations/            # External service integrations
│   ├── __init__.py
│   └── {service}_client.py    # API clients
│
├── 📁 models/                  # Data models (for complex apps with 10+ models)
│   ├── __init__.py            # Central export point for all models
│   ├── core.py                # Core entities
│   ├── {domain}.py            # Domain-specific models
│   └── {feature}.py           # Feature-specific models
│
├── 📁 tests/                   # Test suite
│   ├── __init__.py
│   ├── test_models.py
│   └── test_views.py
│
├── 📁 static/                  # Static files (CSS, JS, images)
│   └── {app_name}/
│       ├── css/
│       ├── js/
│       └── images/
│
├── 📁 templates/               # HTML templates
│   └── {app_name}/
│       ├── base.html
│       └── {feature}.html
│
├── 📁 legacy/                  # Archived code
│
├── 📄 models.py                # Models (if simple)
├── 📄 admin.py                 # Django admin
├── 📄 urls.py                  # URL routing
└── 📄 apps.py                  # App config
```

## When to Use `models/` Directory

**Use a `models/` directory when:**
- You have 10+ models in your app
- Models naturally group by domain/feature
- The models.py file exceeds ~500 lines

**Organization Pattern (see scholar_app as reference):**

```python
models/
├── __init__.py          # Export all models
├── core.py             # Core entities (User, Organization, etc.)
├── search.py           # Search-related models
├── library.py          # Library/Collection models
├── collaboration.py    # Collaboration/Sharing models
└── integration.py      # External integrations
```

**Important Rules:**
1. **Use string references** for ForeignKey to avoid circular imports:
   ```python
   paper = models.ForeignKey('SearchIndex', on_delete=models.CASCADE)  # ✓ Good
   paper = models.ForeignKey(SearchIndex, on_delete=models.CASCADE)     # ✗ Bad
   ```

2. **Export everything** from `__init__.py`:
   ```python
   from .core import Author, Journal, SearchIndex
   from .search import SearchQuery, SavedSearch

   __all__ = ['Author', 'Journal', 'SearchIndex', 'SearchQuery', 'SavedSearch']
   ```

3. **Order models** within each file to minimize forward references
4. **Document domain** organization in module docstrings

**Reference Implementation:** `scholar_app/models/` (26 models across 6 files)

<!-- EOF -->