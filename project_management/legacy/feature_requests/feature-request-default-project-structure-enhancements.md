<!-- ---
!-- Timestamp: 2025-06-28 02:25:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Cloud/project_management/feature_requests/feature-request-default-project-structure-enhancements.md
!-- --- -->

# Feature Request: Default Project Structure Enhancements

## Summary
Enhance project creation with standardized default structure, copy functionality, directory uploads, and GitHub sync fixes.

## Feature Request Details

### 1. Default Directory Structure
- **Source Template**: Use `~/proj/scitex-cloud/docs/to_claude/examples/example-python-project-scitex/` as the standard template
- **Implementation**: When no projects exist yet, automatically copy this project structure
- **Benefit**: Provides users with immediate working example following SCITEX framework

### 2. Copy Project Functionality in Dashboard
- **Requirement**: Implement copy project button/functionality directly in the dashboard interface
- **Location**: Dashboard project cards should have "Copy Project" action
- **Functionality**: Allow users to duplicate existing projects with their structure and files
- **Use Case**: Users can create variations of successful projects

### 3. Directory Upload Functionality
- **Current State**: Only file upload is available
- **Enhancement**: Add ability to upload entire directories/folders
- **Implementation**: Support drag-and-drop or browse for folder uploads
- **Benefit**: Easier migration of existing project structures

### 4. GitHub Sync Issues
- **Problem**: GitHub sync functionality is not working properly
- **Investigation Needed**: Determine root cause of GitHub integration failures
- **Fix Required**: Restore proper GitHub synchronization functionality

## Technical Implementation

### Priority: High
These features are essential for proper project management and user workflow.

### Implementation Areas:

#### 1. Default Project Structure
- **Files to Modify**:
  - `apps/core_app/views.py` (project creation logic)
  - `apps/core_app/directory_manager.py` (template copying)
  - Dashboard templates

- **Implementation**:
  - Create function to copy example project structure
  - Integrate with project creation workflow
  - Ensure proper file permissions and ownership

#### 2. Dashboard Copy Project
- **Files to Modify**:
  - `apps/core_app/templates/core_app/dashboard.html`
  - Dashboard JavaScript
  - Existing `copy_project` view (already implemented)

- **Implementation**:
  - Add copy button to project cards
  - Connect to existing API endpoint
  - Add confirmation dialog and progress feedback

#### 3. Directory Upload
- **Files to Modify**:
  - `apps/core_app/directory_views.py`
  - Upload templates and JavaScript
  - File handling backend

- **Implementation**:
  - Extend upload_file function to handle directories
  - Add frontend directory selection
  - Handle nested directory structures

#### 4. GitHub Sync Fix
- **Files to Investigate**:
  - `apps/core_app/github_views.py`
  - GitHub integration endpoints
  - Authentication and token management

- **Investigation**:
  - Test GitHub API endpoints
  - Verify authentication flow
  - Check error logs and responses

## User Stories

### Default Structure
As a new researcher, I want to start with a proven project structure so that I can focus on my research rather than project organization.

### Copy Project
As a researcher, I want to copy successful projects so that I can reuse proven workflows for similar research.

### Directory Upload
As a researcher, I want to upload entire project folders so that I can quickly migrate existing work to SciTeX Cloud.

### GitHub Sync
As a developer-researcher, I want reliable GitHub synchronization so that I can maintain version control of my research code.

## Acceptance Criteria

### Default Structure
- [ ] New projects automatically include example SCITEX structure
- [ ] Example files demonstrate proper framework usage
- [ ] Structure is customizable after creation

### Copy Project
- [ ] Copy button appears in dashboard project cards
- [ ] Copy functionality preserves file structure
- [ ] Copied projects get unique names
- [ ] User can modify copy during creation

### Directory Upload
- [ ] Interface supports folder/directory selection
- [ ] Nested directory structures are preserved
- [ ] Progress indication for large uploads
- [ ] Error handling for failed uploads

### GitHub Sync
- [ ] GitHub authentication works properly
- [ ] Repository creation functions correctly
- [ ] File synchronization maintains integrity
- [ ] Error messages are clear and actionable

## Related Issues
- Dashboard directory structure not shown (related bug)
- Project initialization and directory creation
- File management and organization

## Implementation Dependencies
- Directory manager functionality
- GitHub API integration
- Dashboard UI components
- File upload infrastructure

## Request Status
- **Status**: Open
- **Priority**: High
- **Assigned To**: TBD
- **Created By**: User via /home/ywatanabe/proj/scitex-cloud/docs/from_user/default_project_structure.md
- **Created Date**: 2025-06-28

## Notes
This request builds on existing example project functionality and addresses multiple user workflow improvements simultaneously.

<!-- EOF -->