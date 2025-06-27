# Bug Report: GitHub Sync Authentication Issue

## Problem Summary
GitHub sync functionality is not working properly. The backend implementation exists but fails during execution.

## Bug Details
- **Status**: Active
- **Priority**: High
- **Reporter**: User feedback: "sync github does not work yet"
- **Affected Component**: GitHub sync functionality in dashboard
- **File**: `apps/core_app/directory_views.py:552-790`

## Root Cause Analysis
The GitHub sync function `sync_with_github` exists with comprehensive implementation including:
- Git command execution via subprocess
- URL validation and security checks
- Proper error handling and timeouts
- Support for init, push, pull, status actions

However, the most likely causes of failure are:

1. **Git Authentication Issues**:
   - Server may not have Git credentials configured
   - SSH keys or personal access tokens not set up
   - Git user configuration missing

2. **Git Installation**:
   - Git may not be installed on the server
   - Git executable not in PATH

3. **File Permissions**:
   - Project directories may have permission issues
   - Web server user may not have write access to project folders

## Technical Implementation
The sync function implements:
- `subprocess.run()` with 30-second timeouts
- Proper working directory handling (`cwd=project_path`)
- Comprehensive error capture and reporting
- Support for multiple Git operations

## Testing Steps
To diagnose the issue:
1. Check if Git is installed: `git --version`
2. Verify Git global configuration: `git config --global --list`
3. Test Git authentication with GitHub
4. Check project directory permissions
5. Verify web server user can execute Git commands

## Suggested Fixes
1. **Server Configuration**:
   - Install Git if missing
   - Configure Git user credentials
   - Set up GitHub authentication (SSH keys or tokens)

2. **Permission Fixes**:
   - Ensure project directories are writable by web server user
   - Set proper ownership and permissions

3. **Authentication Setup**:
   - Configure GitHub personal access token
   - Set up SSH keys for server
   - Test authentication outside of web context

## Expected Behavior
GitHub sync should allow users to:
- Initialize Git repositories in project directories
- Push changes to GitHub with commit messages
- Pull updates from remote repositories
- Check repository status and branch information

## Current Status
- Backend implementation: ✅ Complete
- Frontend integration: ✅ Complete
- Server configuration: ❌ Needs investigation
- Authentication setup: ❌ Needs configuration

## Next Steps
1. Investigate Git installation and configuration on server
2. Set up proper GitHub authentication
3. Test Git operations in project directories
4. Verify web server permissions
5. Test end-to-end functionality

## Related Files
- `apps/core_app/directory_views.py` (lines 552-790)
- `apps/core_app/directory_urls.py` (URL routing)
- Dashboard JavaScript (frontend integration)