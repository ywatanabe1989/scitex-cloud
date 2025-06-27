# Feature Request: Enhanced GitHub Integration

## Summary
Enhanced GitHub connectivity for seamless version control integration within the SciTeX Cloud platform's file-centric dashboard.

## Current Status
- Basic GitHub sync functionality exists with manual commands
- Repository initialization and syncing available via project settings
- Command-line style GitHub operations supported

## Requested Enhancements

### 1. **One-Click GitHub Integration**
- **GitHub Connect Button**: Direct connection from project header
- **Repository Creation**: Create new GitHub repositories from within SciTeX
- **Automatic Authentication**: OAuth-based GitHub authentication flow
- **Repository Linking**: Link existing GitHub repositories to projects

### 2. **Visual Git Status Integration**
- **File Status Indicators**: Show git status (modified, untracked, staged) in file tree
- **Branch Visualization**: Display current branch in project header
- **Commit History**: Inline commit history for files in preview panel
- **Diff Visualization**: Side-by-side diff view for modified files

### 3. **Streamlined Git Operations**
- **Quick Actions**: Stage, unstage, commit buttons in file context menus
- **Commit Dialog**: Rich commit interface with message templates
- **Push/Pull Indicators**: Visual indicators for sync status
- **Branch Management**: Create, switch, merge branches from UI

### 4. **Collaborative Features**
- **Pull Request Integration**: View and create PRs from within SciTeX
- **Issue Tracking**: Link research tasks to GitHub issues
- **Contributor Activity**: Show team member contributions in dashboard
- **Code Review**: Inline commenting and review capabilities

### 5. **Research-Specific Features**
- **Research Templates**: Pre-configured .gitignore for scientific projects
- **Data Versioning**: Special handling for large data files (LFS integration)
- **Publication Releases**: Tag and release research milestones
- **Citation Integration**: Automatic DOI and citation generation for releases

## Technical Implementation

### Frontend Components
```javascript
// GitHub Integration Widget
<GitHubWidget 
  projectId={project.id}
  repository={project.github_url}
  onConnect={handleGitHubConnect}
  onSync={handleGitHubSync}
/>

// File Status Indicators
<FileItem 
  file={file}
  gitStatus={file.git_status}
  onStage={handleStageFile}
  onCommit={handleCommitFile}
/>
```

### Backend API Endpoints
```python
# GitHub Integration APIs
POST /core/api/projects/{id}/github/connect/
POST /core/api/projects/{id}/github/sync/
GET  /core/api/projects/{id}/github/status/
POST /core/api/projects/{id}/github/commit/
GET  /core/api/projects/{id}/github/history/
```

### Database Schema Extensions
```sql
-- Enhanced project model
ALTER TABLE core_project ADD COLUMN github_token VARCHAR(255);
ALTER TABLE core_project ADD COLUMN github_repo_id INTEGER;
ALTER TABLE core_project ADD COLUMN current_branch VARCHAR(100);
ALTER TABLE core_project ADD COLUMN last_sync_at TIMESTAMP;

-- Git file status tracking
CREATE TABLE core_git_file_status (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES core_project(id),
    file_path VARCHAR(500),
    git_status VARCHAR(20), -- 'modified', 'added', 'deleted', 'untracked'
    last_commit_hash VARCHAR(40),
    updated_at TIMESTAMP
);
```

## User Experience Flow

### 1. **Initial Setup**
1. User creates new project in SciTeX dashboard
2. Clicks "Connect to GitHub" button in project header
3. OAuth flow redirects to GitHub for authorization
4. User selects existing repository or creates new one
5. SciTeX automatically clones/initializes repository
6. File tree shows git-enabled project structure

### 2. **Daily Workflow**
1. User edits files in SciTeX Writer/Code modules
2. File tree shows modified files with status indicators
3. User stages changes using file context menu
4. Quick commit dialog with research-focused templates
5. One-click push to GitHub with progress indicators
6. Collaboration features update team members

### 3. **Advanced Operations**
1. Branch creation for experimental analysis
2. Pull request creation for peer review
3. Issue linking for research task tracking
4. Release tagging for publication milestones

## Benefits for Research Workflow

### **Version Control Best Practices**
- Automated backup of research work
- Collaborative editing with conflict resolution
- Reproducible research through version tracking
- Publication-ready code repositories

### **Team Collaboration**
- Seamless sharing of research code and data
- Peer review process for research methodologies
- Distributed team coordination
- Knowledge transfer and documentation

### **Publication Integration**
- DOI generation for code repositories
- Citation-ready software releases
- Supplementary material organization
- Open science compliance

## Priority Level
**HIGH** - This feature significantly enhances the research workflow and positions SciTeX as a comprehensive research platform.

## Estimated Implementation Time
- **Phase 1** (Basic Integration): 2-3 weeks
- **Phase 2** (Visual Git Status): 2-3 weeks  
- **Phase 3** (Advanced Features): 3-4 weeks
- **Phase 4** (Research-Specific): 2-3 weeks

**Total**: 9-13 weeks for complete implementation

## Dependencies
- GitHub API integration and OAuth setup
- Git command-line tools on server
- File system monitoring for git status updates
- WebSocket connections for real-time status updates

## Success Metrics
- **Adoption Rate**: 70%+ of projects connected to GitHub
- **Commit Frequency**: Increase in research code versioning
- **Collaboration**: More multi-author projects
- **Publication Integration**: Research code citing and DOI usage

---

**Created**: 2025-06-27  
**Requestor**: Dashboard Enhancement Initiative  
**Status**: Open for Development  
**Related Features**: File-Centric Dashboard, Project Management