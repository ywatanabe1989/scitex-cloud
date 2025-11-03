# Visitor Project Selector Implementation

**Date**: 2025-11-03
**Status**: ✅ Complete

## Overview
Implemented project selector in the global header for all users, including visitors. Visitors are now allocated a project from a pre-created pool and can use the Writer app without authentication.

## Changes Made

### 1. Global Header Template
**File**: `templates/global_base_partials/global_header.html`

- Removed `{% if user.is_authenticated %}` guard around project selector
- Project selector now visible to all users (authenticated + visitors)
- Shows allocated project name (e.g., "Default Project 001")
- Visitor-specific dropdown with:
  - Current project display with checkmark
  - Visitor mode warning message
  - "Sign up to save your work" call-to-action

### 2. Context Processor
**File**: `apps/project_app/context_processors.py`

- Modified `project_context()` to check visitor projects FIRST
- Loads visitor project from session: `VisitorPool.SESSION_KEY_PROJECT_ID`
- Makes visitor project available globally in templates
- Ensures context processor doesn't override view context

### 3. Visitor Pool Service
**File**: `apps/project_app/services/visitor_pool.py`

**Fixes**:
- Fixed method name: `create_empty_project_directory` → `create_project_directory`
- Added `data_location` field to project defaults
- Set `data_location` during project creation and reset

**Pool Setup**:
- 32 visitor accounts: `visitor-001` to `visitor-032`
- 32 default projects: `default-project-001` to `default-project-032`
- Each project has proper directory structure
- Session-based allocation with 24-hour expiry

### 4. Database Setup
**Manual Fixes** (one-time):
```python
# Set data_location for all visitor projects
for project in visitor_projects:
    project.data_location = f"{visitor.username}/{project.slug}"
    project.save()

# Create project directories
for project in visitor_projects:
    manager.create_project_directory(project)
```

## How It Works

### For Visitors
1. Anonymous user visits `/writer/`
2. `VisitorPool.allocate_visitor()` assigns a free slot
3. Project stored in session: `visitor_project_id`
4. Context processor loads project for templates
5. View passes project to JavaScript via `WRITER_CONFIG`
6. Header shows "Default Project 001" (or 002, 003, etc.)
7. Writer app works with valid `projectId`

### For Authenticated Users
1. User visits `/writer/`
2. Context processor checks for user's projects
3. Uses `last_active_repository` or first project
4. Header shows user's project name
5. Can switch between projects via dropdown

## Testing Results

✅ **Header**: Shows "Default Project 001"
✅ **JavaScript**: `projectId: 6` (valid ID)
✅ **API Calls**: No more 401/500 errors
✅ **Section Loading**: Content loads successfully
✅ **Compilation**: Auto-compilation works
✅ **PDF Preview**: Displays correctly

## Pool Management

### Check Status
```bash
docker exec scitex-cloud-dev-web-1 python manage.py create_visitor_pool --status
```

### Clean Up Expired Slots
```python
from apps.project_app.services.visitor_pool import VisitorPool
freed = VisitorPool.cleanup_expired_allocations()
```

### Reset All Allocations (Dev Only)
```bash
docker exec scitex-cloud-dev-web-1 python manage.py shell -c "
from apps.project_app.models import VisitorAllocation
VisitorAllocation.objects.all().delete()
"
```

## Future Enhancements

- [ ] Add visitor → user migration on signup
- [ ] Implement pool auto-expansion if exhausted
- [ ] Add metrics/analytics for pool usage
- [ ] Periodic cleanup of expired allocations (cron job)
- [ ] Visitor workspace reset after signup

## Related Files

- `templates/global_base_partials/global_header.html`
- `apps/project_app/context_processors.py`
- `apps/project_app/services/visitor_pool.py`
- `apps/writer_app/views/main_views.py`
- `apps/project_app/management/commands/create_visitor_pool.py`
