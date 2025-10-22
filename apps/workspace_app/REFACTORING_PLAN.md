# Core App Refactoring Plan

## File Classification & Organization

### Views Layer (`views/`)
- `views.py` → `views/core_views.py`
- `dashboard_views.py` → `views/dashboard_views.py`
- `directory_views.py` → `views/directory_views.py`
- `github_views.py` → `views/github_views.py`
- `native_file_views.py` → `views/native_file_views.py`

### API Layer (`api/`)
- `api_views.py` → `api/viewsets.py`
- `permissions.py` → `api/permissions.py`

### Services Layer (`services/`)
- `git_operations.py` → `services/git_service.py`
- `ssh_manager.py` → `services/ssh_service.py`
- `directory_manager.py` → `services/directory_service.py`
- `filesystem_utils.py` → `services/filesystem_utils.py`
- `gitea_sync.py` → `services/gitea_sync_service.py`
- `anonymous_storage.py` → `services/anonymous_storage.py`
- `services.py` → `services/core_service.py`

### Utilities (`services/utils/`)
- `context_processors.py` → Keep at root (Django convention)
- `middleware.py` → Keep at root (Django convention)
- `model_imports.py` → `services/utils/model_imports.py`

### Root Level (Keep at root - Django conventions)
- `__init__.py`
- `admin.py`
- `apps.py`
- `models.py`
- `signals.py`
- `urls.py`
- `urls.py` → `directory_urls.py` (routing specific)

## Import Update Strategy

1. Update `urls.py` to import from new locations
2. Update view imports in `__init__.py`
3. Update service imports in `__init__.py`
4. Test all import paths
