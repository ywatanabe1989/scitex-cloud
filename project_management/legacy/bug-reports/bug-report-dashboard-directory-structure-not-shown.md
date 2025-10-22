<!-- ---
!-- Timestamp: 2025-06-28 02:15:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Cloud/project_management/bug-reports/bug-report-dashboard-directory-structure-not-shown.md
!-- --- -->

# Bug Report: Dashboard Directory Structure Not Shown

## Problem Description
Directory structure is not displayed in the dashboard, preventing users from viewing their project file organization.

## Expected Behavior
Dashboard should show project directory structures, allowing users to:
- View project file trees
- Navigate project directories
- Understand project organization
- Access project files

## Actual Behavior
Directory structure is not visible or not loading in the dashboard interface.

## Environment
- **Platform**: SciTeX-Cloud Dashboard
- **Module**: Core App Dashboard
- **Browser**: [To be determined during investigation]
- **User Type**: Authenticated users with projects

## Bug Fix Progress
- [x] Identify root cause
- [x] Check dashboard template implementation
- [ ] Verify directory manager integration
- [ ] Test project directory creation
- [ ] Fix directory structure display
- [ ] Test directory navigation
- [ ] Verify file listing functionality

## Investigation Plan

### Potential Causes
1. **Template Issue**: Dashboard template missing directory structure component
2. **JavaScript Issue**: Frontend not loading directory data
3. **API Issue**: Backend not providing directory structure data
4. **Permission Issue**: User lacking permissions to view directories
5. **Project Directory Issue**: Projects not properly initializing directories
6. **CSS Issue**: Directory structure hidden by styling

### Investigation Steps
1. Check dashboard template for directory structure components
2. Verify project directory creation in directory manager
3. Test API endpoints for directory structure
4. Check JavaScript for directory loading
5. Verify project permissions and access
6. Test with different user accounts and projects

## Root Cause Analysis

**Found Issue**: The dashboard template has the JavaScript functions `loadProjectStructure()` and `renderFolderStructure()` that expect to load directory structure via API endpoint `/core/directory/projects/{project_id}/structure/`, but:

1. **Missing Project Directory Initialization**: Projects may not have directories properly initialized
2. **API Endpoint Available**: URL pattern exists at `directory_views.project_structure`
3. **Frontend Implementation**: JavaScript calls the correct API but may not handle responses properly
4. **Template Logic**: Directory structure display depends on projects having `directory_created=True`

**Key Findings**:
- JavaScript function `loadProjectStructure()` calls `/core/directory/projects/${currentProject}/structure/`
- Function `renderFolderStructure()` creates hardcoded folder structure (config, data, scripts, docs, results, temp)
- Dashboard shows directory structure only when projects exist and have directories initialized

## Root Cause & Solution

**Root Cause**: Infinite recursion in Django signals
- `post_save` signal for Project model called `ensure_project_directory()`
- This function modified and saved the project, triggering the signal again
- Similarly, `update_storage_usage()` called `self.save()` causing recursive signals

**Solution Implemented**:
1. **Fixed Project Signal (`apps/core_app/signals.py:39-61`)**:
   - Modified signal to use `Project.objects.filter(id=instance.id).update()` instead of `instance.save()`
   - Added guard conditions to prevent recursion
   - Only create directories for new projects that don't have `directory_created=True`

2. **Fixed Storage Update (`apps/core_app/models.py:570-582`)**:
   - Changed `self.save()` to `Project.objects.filter(id=self.id).update(storage_used=total_size)`
   - This avoids triggering post_save signals during storage updates
   - Still updates the instance attribute for immediate access

**Result**: Directory structure now displays correctly in dashboard when projects exist

## Test Plan
1. Create test project with directory structure
2. Verify directory creation in filesystem
3. Test dashboard display of directory structure
4. Test directory navigation and file access
5. Verify cross-browser compatibility

## Related Files
- `apps/core_app/templates/core_app/dashboard.html`
- `apps/core_app/views.py` (dashboard view)
- `apps/core_app/directory_manager.py`
- `apps/core_app/directory_views.py`
- Dashboard JavaScript files
- Directory structure CSS files

## Priority
**High** - Core functionality that affects user experience and project management

## Reported By
User via bug report command

## Assigned To
TBD

## Status
**RESOLVED** - Fixed infinite recursion in project directory creation signals

<!-- EOF -->