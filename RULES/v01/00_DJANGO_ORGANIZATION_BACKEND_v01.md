<!-- ---
!-- Timestamp: 2025-11-03 23:20:38
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/RULES/00_DJANGO_ORGANIZATION_APP.md
!-- --- -->

## Standard App Structure

Each app should follow this modular organization:

```
{app_name}_app/
├── 📁 models/                  # Database models (split by domain)
│   ├── __init__.py            # Central export point for all models
│   ├── core.py                # Core domain models
│   ├── search.py              # Search/query models
│   ├── library.py             # User library/collection models
│   ├── collaboration.py       # Collaboration/sharing models
│   ├── integration.py         # Integration-specific models
│   └── repository.py          # Repository/data management models
│
├── 📁 views/                  # View logic organized by feature
│   ├── __init__.py            # Central export point
│   ├── search_views.py        # Search/discovery features
│   ├── library_views.py       # Library management
│   ├── export_views.py        # Export/download features
│   ├── collaboration_views.py # Sharing/collaboration
│   ├── annotation_views.py    # Annotations/comments
│   ├── workspace_views.py     # Workspace management
│   ├── project_views.py       # Project-specific views
│   ├── api_views.py           # API endpoints
│   └── trending_views.py      # Analytics/trending
│
├── 📁 services/               # Business logic (domain services)
│   ├── __init__.py            # Central export point
│   ├── service_name.py        # Domain-specific service
│   └── utils.py               # Shared utilities
│
├── 📁 integrations/           # External integrations
│   ├── __init__.py
│   ├── external_api.py        # Integration with external services
│   └── sync_service.py        # Data synchronization
│
├── 📁 templates/              # HTML templates
│   └── {app_name}/
│       ├── {app_name}_base.html      # Base template with {app_name} prefix
│       ├── {feature}.html            # Feature-specific templates
│       └── partials/
│           └── {component}.html      # Reusable components
│
├── 📁 static/                 # Static assets
│   └── {app_name}/
│       ├── css/
│       │   └── {app_name}.css        # Styles with {app_name} prefix
│       ├── js/
│       │   └── {app_name}.js         # Scripts with {app_name} prefix
│       └── images/
│           └── {icon_name}.svg       # Icons/images
│
├── 📁 legacy/                 # Archived code (old implementations)
│   ├── models_old.py          # Previous models.py
│   ├── simple_views.py        # Monolithic views
│   └── {archived_file}.py     # Other archived files
│
├── admin.py                   # Django admin configuration
├── apps.py                    # App configuration
├── forms.py                   # Django forms
├── signals.py                 # Django signals
├── urls.py                    # URL routing
├── tests.py                   # Unit tests
├── MODELS_REORGANIZATION.md   # (optional) Documentation of model organization
└── README.md                  # (optional) App-specific documentation
```

# Key Principles

## 1. Models Organization

**Split models.py into domain modules:**
- **core.py**: Entity definitions (e.g., Author, Journal, SearchIndex)
- **search.py**: Search/query-related models
- **library.py**: User library, collections, organization
- **collaboration.py**: Annotations, sharing, group models
- **integration.py**: Integration-specific models
- **repository.py**: Data repository, datasets, syncing

**Use string references to avoid circular imports:**
```python
# Instead of: ForeignKey(SearchIndex, ...)
# Use: ForeignKey('SearchIndex', ...)
related_papers = models.ManyToManyField('SearchIndex', related_name='associated_datasets')
external_model = models.ForeignKey('other_app.Model', on_delete=models.CASCADE)
```

**Central export in models/__init__.py:**
```python
from .core import Author, Journal, SearchIndex
from .search import SearchQuery, SearchResult
from .library import Collection, UserLibrary
# ... import all models

__all__ = [
    'Author', 'Journal', 'SearchIndex',
    'SearchQuery', 'SearchResult',
    'Collection', 'UserLibrary',
    # ... all models
]
```

Then import anywhere as:
```python
from apps.{app_name}.models import SearchIndex, Collection
```

## 2. Views Organization

**Organize views by feature, not by pattern:**
- Each view module handles a complete feature (search, library, export, etc.)
- Keep related views together
- Each module should be ~1000-2000 lines maximum
- Use `views/__init__.py` to export common views

**View module structure:**
```python
# apps/scholar_app/views/search_views.py
from django.shortcuts import render
from ..models import SearchIndex, SearchQuery
from ..services import search_service

def search(request):
    """Main search view"""
    pass

def search_filters(request):
    """Search filters sub-view"""
    pass

def search_results(request):
    """Results display sub-view"""
    pass
```

## 3. Services Organization

**Business logic should go in services, not views:**
- Views handle HTTP request/response
- Services handle business logic
- Services can be imported by other services, views, or management commands
- Keep services stateless (dependency injection preferred)

**Example service structure:**
```python
# apps/scholar_app/services/search_service.py
class SearchService:
    @staticmethod
    def search_papers(query, filters=None):
        """Business logic for searching papers"""
        pass

    @staticmethod
    def rank_results(papers):
        """Rank search results by relevance"""
        pass
```

## 4. Templates Naming Convention

## 5. Static Files Naming Convention

## 6. Legacy Code Handling

**When reorganizing an app:**
1. Create a `legacy/` directory
2. Move old files there (models_old.py, simple_views.py, etc.)
3. Keep legacy code for reference but don't import from it
4. Document what was archived and why

**Example legacy structure:**
```
legacy/
├── models_old.py        # Original 1432-line models.py
├── simple_views.py      # Monolithic views
├── views_advanced.py    # Complex view logic
└── README.md           # What was archived and when
```

## 7. Testing

**Each app should have a tests.py (or tests/ directory):**
- Unit tests for models
- View tests for HTTP endpoints
- Service tests for business logic
- Aim for 80%+ coverage on critical paths

## 8. Forward References in Django Models

**Use string references to avoid import-time issues:**

```python
# ✅ Good - avoids circular imports
class SearchResult(models.Model):
    search_index = models.ForeignKey('SearchIndex', on_delete=models.CASCADE)
    search_query = models.ForeignKey('SearchQuery', on_delete=models.CASCADE)
    collection = models.ForeignKey('Collection', on_delete=models.SET_NULL, null=True)

# ❌ Avoid - can cause circular import issues
from .core import SearchIndex  # May fail if SearchIndex imports SearchResult
class SearchResult(models.Model):
    search_index = models.ForeignKey(SearchIndex, on_delete=models.CASCADE)
```

<!-- EOF -->