# workspace_app - Authenticated Research Project & File Management Hub

## Purpose

**workspace_app** is the central hub for authenticated users to manage research projects, files, and GitHub integration within the SciTeX ecosystem. It provides the core workspace functionality including project creation, file system operations, directory management, and git/GitHub synchronization for active researchers.

## One-Line Summary

Central hub managing authenticated user projects, files, dashboards, and GitHub integration with comprehensive file system and git operations services.

## Key Responsibilities

### 1. **Project Management**
- Create, list, and delete research projects
- Copy existing projects for quick setup
- Generate example projects with full SCITEX directory structures
- Apply project templates (MNIST, Data Analysis, Research Papers, SciTeX Default)
- Project metadata and configuration management

### 2. **File System Management**
- Initialize SCITEX directory structure: `config/`, `data/`, `scripts/`, `docs/`, `results/`, `temp/`
- Browse files with React tree-based UI
- Upload and download files
- Create, delete, rename, and move files/directories
- Real-time file tree navigation via REST API
- Disk quota and storage management

### 3. **User Dashboard & Monitoring**
- Authenticated user landing page and authentication redirects
- Dashboard with integrated file manager
- User activity monitoring and statistics
- Smart recommendations based on recent activity
- Active user tracking and engagement metrics

### 4. **GitHub Integration**
- OAuth authentication flow with GitHub
- Repository creation and linking to projects
- Commit and push operations to linked repositories
- File synchronization with GitHub
- Repository status monitoring and branch management

### 5. **Email Services**
- Account activation and welcome emails
- Password reset email flow
- Project invitation and collaboration emails
- Donation confirmation and thank-you emails
- Email verification with OTP codes

### 6. **REST API Endpoints**
- Document CRUD operations (create, read, update, delete)
- Project CRUD operations
- User statistics and profile queries
- File tree navigation and content access
- GitHub repository operations
- File upload/download endpoints

## Architecture

### Directory Structure

```
workspace_app/
├── models.py                  # Model re-exports (backwards compatibility layer)
├── admin.py                   # Django admin customization
├── apps.py                    # App configuration
├── urls.py                    # URL routing
├── signals.py                 # Django signals for automatic operations
├── middleware.py              # Custom middleware
├── context_processors.py      # Template context processors
├── email_service.py           # Email handling and templates
├── directory_urls.py          # Directory-specific URL patterns
│
├── views/                     # View modules by concern
│   ├── core_views.py          # Main dashboard, project operations, examples
│   ├── directory_views.py     # File browser, file management operations
│   ├── github_views.py        # GitHub OAuth, integration, operations
│   ├── native_file_views.py   # File upload, download, operations
│   └── dashboard_views.py     # Dashboard-specific views
│
├── api/                       # REST API implementation
│   ├── viewsets.py            # Django REST Framework viewsets
│   └── permissions.py         # Permission checking and authorization
│
├── services/                  # Business logic & utilities
│   ├── directory_service.py   # User directory management (SCITEX structure)
│   ├── git_service.py         # Git operations and utilities
│   ├── ssh_service.py         # SSH key generation and management
│   ├── filesystem_utils.py    # File system utilities and helpers
│   ├── gitea_sync_service.py  # Gitea repository synchronization
│   ├── anonymous_storage.py   # Anonymous user file storage
│   └── utils/
│       └── model_imports.py   # Import utilities and compatibility
│
├── templates/core_app/        # HTML templates for views
├── migrations/                # Database migrations
└── tests.py                   # Test suite
```

### Models (Re-exported from Other Apps)

This app serves as a backwards-compatibility layer and central export point. Models are imported from:

- **profile_app:** `UserProfile`, academic domain helpers
- **organizations_app:** `Organization`, `OrganizationMembership`, `ResearchGroup`, `ResearchGroupMembership`
- **project_app:** `Project`, `ProjectMembership`, `ProjectPermission`
- **gitea_app:** `GitFileStatus`
- **writer_app:** `Manuscript`
- **auth_app:** `EmailVerification`

### Key Services

#### directory_service.py (~1,697 lines)
- SCITEX directory structure creation and management
- User workspace initialization
- File tree generation and traversal
- Directory validation and cleanup

#### git_service.py (~343 lines)
- Git configuration and operations
- Commit and push functionality
- Remote repository management
- Branch operations

#### ssh_service.py (~202 lines)
- SSH key pair generation
- Key storage and retrieval
- Git authentication via SSH

#### filesystem_utils.py (~535 lines)
- File path validation and sanitization
- File operation helpers
- Disk usage calculation
- Directory utilities

#### anonymous_storage.py (~331 lines)
- Anonymous user file storage
- Temporary file management
- Quota handling for unregistered users

## Views Overview

### core_views.py (1,309 lines)
- **User Dashboard:** Main landing for authenticated users
- **Project Operations:** Create, list, copy, delete projects
- **Example Projects:** Generate and populate example research projects
- **Project Templates:** Apply pre-configured templates

### directory_views.py (1,039 lines)
- **File Browser:** React tree-based file navigation
- **File Operations:** Upload, download, delete, rename, move files
- **Directory Operations:** Create, delete, and manage directories
- **File Content:** Serve file content and metadata

### github_views.py (549 lines)
- **OAuth Flow:** GitHub login and authorization
- **Repository Management:** Create and link repositories
- **Synchronization:** Push files to GitHub repositories
- **Status Monitoring:** Check repository and branch status

### native_file_views.py (446 lines)
- **File Upload:** Handle file uploads via web interface
- **File Download:** Serve files for download
- **Streaming:** Stream large files efficiently

## REST API Endpoints

- `GET/POST /api/projects/` - List/create projects
- `GET/PUT/DELETE /api/projects/{id}/` - Project detail operations
- `GET /api/documents/` - List documents in projects
- `GET /api/file-tree/` - Browse file tree
- `POST /api/file-operations/` - Perform file operations
- `GET/POST /api/github/` - GitHub integration endpoints
- `GET /api/user-stats/` - User statistics and metrics

## Authentication & Authorization

- **Authentication:** Required for all views except OAuth callback
- **Permissions:** User can only access their own projects and files
- **Superuser:** Admin users have elevated permissions
- **Ownership:** File/project operations check user ownership

## Email Notifications

Triggered for:
- Account activation with verification link
- Password reset with secure token
- Project invitations to collaborators
- Donation confirmations and receipts
- Project updates and notifications

## Configuration

Located in `apps.py`:
- App name: `core_app`
- Verbose name: "Core App"
- Ready signal handling for initialization

## Integration Points

- **project_app:** Projects and project memberships
- **profile_app:** User profiles and academic domain verification
- **auth_app:** User authentication and email verification
- **organizations_app:** Organization and team management
- **writer_app:** Manuscript and document management
- **gitea_app:** Git server synchronization
- **cloud_app:** User subscriptions and account settings

## Database Operations

- Minimal direct models in this app
- Primarily reads/writes through related app models
- Heavy use of Django ORM relationships
- Caching for file tree operations

## Testing

Test suite in `tests.py` covers:
- Project creation and management
- File operations and directory structure
- GitHub integration workflows
- API endpoint functionality
- Permission checking

## Future Improvements

1. Extract project-specific logic to project_app
2. Move GitHub integration to dedicated integration_app
3. Refactor large view modules into smaller, focused views
4. Improve service layer organization
5. Add caching for frequently accessed data
6. Implement better quota management system

## See Also

- `./apps/README.md` - App structure documentation
- `../accounts_app/` - User accounts, profiles, API keys, SSH keys
- `../project_app/` - Project definition and management
- `../auth_app/` - Authentication and email verification
- `../organizations_app/` - Organization and team management
- `../donations_app/` - Donations and fundraising
- `../public_app/` - Public landing pages and legal documentation
