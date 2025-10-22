<!-- ---
!-- Timestamp: 2025-10-23 03:15:00
!-- Author: claude-code
!-- File: /home/ywatanabe/proj/scitex-cloud/project_management/BULLETIN_BOARD.md
!-- --- -->

# SciTeX Apps Refactoring - Bulletin Board

## Current Status: Analysis Complete, Refactoring Planning Phase

**Last Updated:** 2025-10-23 03:15:00

---

## Executive Summary

The SciTeX ecosystem consists of 18 Django apps across multiple functional domains. Currently, **only `scholar_app` follows the standard architectural structure** defined in `apps/README.md`. A comprehensive refactoring is needed to align all apps with the standardized architecture for consistency, maintainability, and scalability.

---

## Standard Architecture Reference

See: `./apps/README.md` and `./apps/scholar_app/` (reference implementation)

**Standard Structure:**
```
{app_name}/
├── 📁 api/                     # API layer (REST endpoints)
├── 📁 views/                   # View layer (web pages)
├── 📁 services/                # Business logic layer
├── 📁 integrations/            # External service integrations
├── 📁 models/                  # Data models (if complex)
├── 📁 tests/                   # Test suite
├── 📁 legacy/                  # Archived code
├── 📄 models.py                # Models (if simple)
├── 📄 admin.py                 # Django admin
├── 📄 urls.py                  # URL routing
└── 📄 apps.py                  # App config
```

---

## Apps Status Assessment

### ✅ COMPLIANT (1 app)

#### `scholar_app`
- **Status:** Already follows standard architecture
- **Structure:** Properly organized with api/, views/, services/, integrations/, models/, tests/, legacy/
- **Reference:** Use as template for other apps
- **Priority:** No changes needed

### 🔴 NON-COMPLIANT - REQUIRES MAJOR REFACTORING (10 apps)

These apps have views, api_views, and business logic scattered across the root directory and need comprehensive restructuring.

#### `auth_app`
- **Current Files:** api_views.py, views.py, forms.py, validators.py
- **Issues:** 
  - API and views mixed at root level
  - Forms and validators at root instead of organized modules
  - No services layer
- **Refactoring Needed:**
  - Create `views/` directory and move views.py
  - Create `api/` directory and move api_views.py
  - Create `services/` directory for business logic
  - Move forms.py → services/ or create forms/ subdirectory
  - Move validators.py → services/

#### `code_app`
- **Current Files:** api_views.py, views.py, project_views.py, default_workspace_views.py, jupyter_utils.py, environment_manager.py, repository_integration.py, visualization_pipeline.py
- **Issues:**
  - Views scattered across multiple files at root
  - Complex business logic (jupyter_utils, environment_manager, repository_integration, visualization_pipeline) at root
  - No clear separation of concerns
- **Refactoring Needed:**
  - Create `views/` with organized feature files
  - Create `services/` for business logic
  - Move jupyter_utils.py → services/jupyter_service.py
  - Move environment_manager.py → services/
  - Move repository_integration.py → services/ or integrations/
  - Move visualization_pipeline.py → services/
  - Create `api/` for api_views.py

#### `core_app`
- **Current Files:** api_views.py, views.py, dashboard_views.py, github_views.py, directory_views.py, native_file_views.py, multiple utility files
- **Issues:**
  - 8+ view files at root level
  - Complex utilities (git_operations, ssh_manager, directory_manager, etc.) scattered
  - No clear service layer
  - Middleware at root level
- **Refactoring Needed:**
  - Create `views/` with organized feature files
  - Create `services/` for business logic
  - Move git_operations.py → services/
  - Move ssh_manager.py → services/
  - Move directory_manager.py → services/
  - Move middleware.py → appropriate location
  - Create `api/` for api_views.py

#### `profile_app`
- **Current Files:** views.py, signals.py only
- **Issues:**
  - Minimal structure but should still follow standard
  - No API layer exposed yet
  - No services layer for business logic
- **Refactoring Needed:**
  - Create `views/` directory
  - Create `api/` directory (prepare for future API)
  - Create `services/` directory if needed

#### `project_app`
- **Current Files:** views.py, user_urls.py, decorators.py, signals.py only
- **Issues:**
  - Root-level views.py
  - Decorators at root level
  - Potential future API endpoints not organized
- **Refactoring Needed:**
  - Create `views/` directory
  - Create `services/` directory for decorators and helper logic
  - Prepare `api/` structure

#### `viz_app`
- **Current Files:** api_views.py, views.py, project_views.py, default_workspace_views.py, code_integration.py
- **Issues:**
  - Views scattered across multiple files at root
  - code_integration.py at root instead of integrations/
  - No services layer
- **Refactoring Needed:**
  - Create `views/` with organized feature files
  - Create `integrations/` and move code_integration.py
  - Create `services/` for business logic
  - Create `api/` for api_views.py

#### `writer_app`
- **Current Files:** arxiv_services.py, arxiv_views.py, simple_views.py, views.py, default_workspace_views.py, utils.py, version_control.py, ai_assistant.py, operational_transform.py, consumers.py, repository_integration.py
- **Issues:**
  - 10+ files at root level
  - Views scattered across multiple files
  - Services not properly organized (arxiv_services, ai_assistant, version_control at root)
  - Utils and operational logic at root
  - No clear integrations folder
- **Refactoring Needed:**
  - Create `views/` with organized feature files
  - Create `services/` for business logic
  - Move arxiv_services.py, ai_assistant.py, version_control.py → services/
  - Move operational_transform.py, operational_transforms.py → services/
  - Move utils.py → services/utils.py
  - Move repository_integration.py → integrations/
  - Create `api/` if needed
  - Create `consumers.py` → services/websocket/ or integrations/

#### `gitea_app`
- **Current Files:** api_client.py, views.py, models.py only
- **Issues:**
  - api_client.py at root instead of integrations/
  - Minimal structure but needs to follow standard
- **Refactoring Needed:**
  - Create `integrations/` and move api_client.py
  - Create `views/` directory
  - Create `services/` directory if needed
  - Create `api/` directory

#### `integrations_app`
- **Current Files:** views.py, services.py only (plus README.md)
- **Issues:**
  - services.py at root instead of organized within services/ directory
  - Minimal views support
- **Refactoring Needed:**
  - Create `views/` directory
  - Create `services/` directory and move services.py logic
  - Create `integrations/` for external service clients
  - Create `api/` directory

#### `search_app`
- **Current Files:** README.md only (empty app)
- **Status:** Stub/placeholder app
- **Refactoring Needed:**
  - Create basic structure when functionality is added
  - Follow standard architecture from the start

### 🟡 PLACEHOLDER APPS (7 apps)

These apps only contain `__init__.py` and `README.md`, indicating they are placeholders for future development.

- **billing_app** - Placeholder for billing/subscription features
- **cloud_app** - Placeholder for cloud integration features
- **dev_app** - Placeholder for development tools
- **docs_app** - Placeholder for documentation features
- **permissions_app** - Placeholder for permission management
- **search_app** - Placeholder for search functionality
- **social_app** - Placeholder for social features

**Action:** When developing these apps, follow the standard architecture from `apps/README.md` from day one.

---

## Refactoring Priorities

### Phase 1: Foundation (Scholar & Core)
1. **scholar_app** - Already compliant, maintain standard
2. **core_app** - Most complex, critical functionality

### Phase 2: Major Features (Code, Writer, Viz)
3. **code_app** - Data-heavy app with complex logic
4. **writer_app** - Most files to reorganize, critical feature
5. **viz_app** - Medium complexity

### Phase 3: Authentication & Profile
6. **auth_app** - Important but simpler
7. **profile_app** - Simpler structure
8. **project_app** - Central to project-centric architecture

### Phase 4: Infrastructure
9. **gitea_app** - Integration-focused
10. **integrations_app** - Integration hub
11. **search_app** - Prepare structure for future
12. Remaining placeholders - Create basic structure

---

## Refactoring Strategy

### Git Workflow
- Create feature branch: `refactor/standardize-{app_name}`
- Atomic commits per structural change
- One commit per directory creation/file move
- Descriptive commit messages following: `refactor({app}): organize {layer}`

### Per-App Process
1. **Backup current state** in git (feature branch)
2. **Create directory structure** (api/, views/, services/, etc.)
3. **Move files** with appropriate reorganization:
   - Root `views.py` → `views/{feature}_views.py`
   - Root `api_views.py` → `api/viewsets.py`
   - Root utilities → `services/{domain}_service.py`
4. **Update imports** in `__init__.py` files
5. **Update URL imports** in main `urls.py`
6. **Test** locally before committing
7. **Merge** to develop after validation

### File Organization Rules

**api/ directory:**
- `__init__.py`
- `viewsets.py` (or `serializers.py` for complex)
- `permissions.py` (if needed)

**views/ directory:**
- `__init__.py`
- `{feature}_views.py` (e.g., `auth_views.py`, `profile_views.py`)
- Keep feature grouping logical

**services/ directory:**
- `__init__.py`
- `{domain}_service.py` (e.g., `git_service.py`, `auth_service.py`)
- `utils.py` (for shared utilities)

**integrations/ directory:**
- `__init__.py`
- `{service}_client.py` (e.g., `github_client.py`, `arxiv_client.py`)

---

## Implementation Notes

### Import Considerations
- Update all relative imports when moving files
- Use explicit imports in `__init__.py` for public APIs
- Document package structure for new developers

### Django Admin
- Keep `admin.py` at root level as per Django convention

### URL Routing
- Keep `urls.py` at root level as per Django convention
- Consider creating feature-specific url patterns if routes are complex
- Update imports to reference moved views

### Testing
- Move `tests.py` → `tests/` directory with `__init__.py`
- Create `tests/test_{layer}_{feature}.py` files
- Ensure test imports are updated

### Backwards Compatibility
- Maintain public APIs through `__init__.py` exports
- Don't break existing import paths if external apps depend on them

---

## Success Metrics

1. ✅ All non-placeholder apps follow standard architecture
2. ✅ Clear separation of concerns (api, views, services, integrations)
3. ✅ Consistent file naming conventions across all apps
4. ✅ Tests pass after each refactoring phase
5. ✅ No broken imports or URL routing
6. ✅ Documentation updated to reflect new structure

---

## Collaboration Notes

### Using This Board for Coordination

**For Multiple Agents:**
1. Claim a specific app or phase before starting
2. Update the "Current Work" section below
3. Report blockers and decisions made
4. Link to relevant commits/PRs

### Current Work (To be updated during refactoring)
- **Agent:** None assigned yet
- **App:** None
- **Phase:** Planning

### Decision Log
- **2025-10-23**: Initial assessment completed. Standard architecture documented in apps/README.md. Scholar_app is reference implementation.

---

## Related Documents

- Reference: `./apps/README.md`
- Reference Implementation: `./apps/scholar_app/`
- Architecture Details: `./apps/ARCHITECTURE.md` (if exists)

<!-- EOF -->
