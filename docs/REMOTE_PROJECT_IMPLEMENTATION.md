# Remote Project Support - Implementation Summary

## Overview

SciTeX Cloud now supports **remote projects** with TRAMP-like filesystem access via SSHFS. This allows users to work with files on remote servers without creating local copies, preserving privacy and security.

## Key Features

### 1. Project Types

- **Local Projects**: Git-enabled, stored on SciTeX Cloud, full version control
- **Remote Projects**: SSHFS mount, no local copy, SSH access to remote servers

### 2. Remote Credentials Management

Users manage SSH credentials for remote systems through the SSH Keys settings page.

**URL**: `http://127.0.0.1:8000/accounts/settings/ssh-keys/#remote-credentials`

Features:
- Add remote credentials (name, host, port, username, public key)
- Test SSH connections before use
- View SSH key fingerprints
- Track last used time
- Delete credentials
- Setup instructions and documentation

### 3. Project Creation

Users can create remote projects through the standard project creation flow.

**URL**: `http://127.0.0.1:8000/projects/create/`

Steps:
1. Select "Remote Filesystem" as project type
2. Choose a remote credential
3. Enter the remote path (absolute path on remote server)
4. System validates SSH connection before creating project

### 4. File Operations

All file operations work transparently for both local and remote projects:

- **Read files**: `GET /{username}/{slug}/blob/<file-path>`
- **File tree**: `GET /{username}/{slug}/api/file-tree/`
- **Save files**: `POST /code/api/save/`
- **Create files**: `POST /code/api/create-file/`
- **Delete files**: `POST /code/api/delete/`

### 5. SciTeX Structure Initialization

Initialize SciTeX directory structure in any project (local or remote).

**Endpoint**: `POST /{username}/{slug}/api/initialize-scitex/`

Features:
- Non-destructive: Won't overwrite existing files
- Works via rsync for remote projects
- Returns statistics (files created, skipped, bytes transferred)

### 6. Auto-Mount/Unmount

Remote filesystems are automatically managed:

- **Auto-mount**: On first access when needed
- **Auto-unmount**: After 30 minutes of inactivity
- **Periodic cleanup**: Celery tasks run every 10 minutes
- **Stale mount cleanup**: Every hour

## Architecture

### Database Models

**RemoteCredential** (apps/project_app/models/remote.py):
- `user`: Owner
- `name`: Friendly name
- `ssh_host`, `ssh_port`, `ssh_username`
- `ssh_public_key`, `ssh_key_fingerprint`
- `private_key_path`: Auto-generated on server
- `last_used_at`: Track usage

**RemoteProjectConfig** (apps/project_app/models/remote.py):
- `project`: One-to-one with Project
- `remote_credential`: Foreign key to RemoteCredential
- `remote_path`: Absolute path on remote server
- `is_mounted`, `mount_point`, `mounted_at`, `last_accessed`

**Project.project_type** (apps/project_app/models/repository/project.py):
- Added field: `project_type` ('local' or 'remote', default 'local')

### Services

**RemoteProjectManager** (apps/project_app/services/remote_project_manager.py):
- SSHFS mount/unmount operations
- File CRUD operations (read, write, delete, list)
- Connection testing
- Auto-reconnect on failure

**ProjectServiceManager** (apps/project_app/services/project_service_manager.py):
- Unified API for local and remote projects
- `get_project_path()`: Returns local or mount path
- `initialize_scitex_structure()`: Works for both types

### Celery Tasks

**auto_unmount_inactive_remote_projects** (apps/project_app/tasks.py):
- Runs every 10 minutes
- Unmounts projects inactive for >30 minutes
- Privacy-preserving design

**cleanup_stale_mounts** (apps/project_app/tasks.py):
- Runs every hour
- Cleans up orphaned mount points
- Handles server crash recovery

### Updated Endpoints

All workspace file operation endpoints now support both project types:

1. **apps/code_app/workspace_api_views.py**:
   - `api_get_file_content()`
   - `api_save_file()`
   - `api_create_file()`
   - `api_delete_file()`

2. **apps/project_app/views/repository/api.py**:
   - `api_file_tree()`
   - `api_initialize_scitex_structure()` (new)

3. **apps/accounts_app/views.py**:
   - `ssh_keys()` - Handles remote credential actions

## Security

### SSH Key Management

- Public keys stored in database
- Private keys auto-generated on server (not user-uploaded)
- SSH fingerprints verified
- Keys stored in secure location with proper permissions (600)

### Path Security

- Absolute path validation on remote servers
- Path traversal prevention
- Mount points isolated per user/project

### Access Control

- Only project owners/collaborators can access remote projects
- SSH connection tested before project creation
- Credentials tied to specific users

## Privacy

### Data Residency

- Files never stored on SciTeX Cloud for remote projects
- All edits happen directly on remote filesystem
- Automatic unmount ensures no data retention

### Audit Trail

- Last access time tracking
- Last used credential tracking
- Mount/unmount logging

## Configuration

### Settings

Required settings (config/settings/settings_shared.py):

```python
# Remote project mount directory
SCITEX_REMOTE_MOUNT_BASE = Path(BASE_DIR) / '.remote-mounts'

# Celery beat schedule
CELERY_BEAT_SCHEDULE = {
    'auto-unmount-remote-projects': {
        'task': 'apps.project_app.tasks.auto_unmount_inactive_remote_projects',
        'schedule': 600.0,  # 10 minutes
    },
    'cleanup-stale-mounts': {
        'task': 'apps.project_app.tasks.cleanup_stale_mounts',
        'schedule': 3600.0,  # 1 hour
    },
}
```

### System Requirements

- `sshfs` package installed
- `fusermount` available
- Celery worker running
- Celery beat scheduler running

## Usage Flow

### Adding a Remote Credential

1. Navigate to: `http://127.0.0.1:8000/accounts/settings/ssh-keys/#remote-credentials`
2. Click "Add Remote Credential"
3. Fill in:
   - Credential name (e.g., "Lab Server")
   - SSH host (e.g., "remote.university.edu")
   - SSH port (default: 22)
   - SSH username (e.g., "jdoe")
   - SSH public key (paste the public key that's already in remote ~/.ssh/authorized_keys)
4. Click "Add Credential"
5. (Optional) Click "Test" to verify connection

### Creating a Remote Project

1. Navigate to: `http://127.0.0.1:8000/projects/create/`
2. Enter project name and description
3. Select "Remote Filesystem" as project type
4. Choose a remote credential from dropdown
5. Enter remote path (e.g., "/home/jdoe/research/my-project")
6. Click "Create Repository"
7. System validates SSH connection
8. Project created (no Git repository)

### Working with Remote Files

1. Navigate to project: `http://127.0.0.1:8000/{username}/{slug}/`
2. File tree automatically shows remote files
3. Click on any file to view/edit
4. Save works transparently (no Git commits for remote projects)
5. All file operations work the same as local projects

### Initializing SciTeX Structure

Via API:
```bash
curl -X POST \
  http://127.0.0.1:8000/{username}/{slug}/api/initialize-scitex/ \
  -H "Cookie: sessionid=..." \
  -H "X-CSRFToken: ..."
```

Response:
```json
{
  "success": true,
  "message": "SciTeX structure initialized successfully",
  "stats": {
    "files_created": 42,
    "files_skipped": 5,
    "bytes_transferred": 123456
  },
  "project_type": "remote"
}
```

## Limitations

### Remote Projects

- **No Git operations**: No commits, branches, or version control
- **No Git integrations**: No GitHub/GitLab sync
- **Network dependent**: Requires stable SSH connection
- **Slower performance**: Network latency vs local filesystem
- **No offline access**: Requires network connectivity

### SSHFS Caching

- 20-second cache timeout (configurable)
- May cause brief stale reads
- Auto-reconnect on connection loss

## Troubleshooting

### "Failed to mount remote project"

**Causes**:
- SSH connection failed
- Remote path doesn't exist
- Permission denied on remote server
- Mount point already in use

**Solutions**:
1. Test SSH connection from terminal: `ssh user@host -p port`
2. Verify remote path exists: `ssh user@host ls /path/to/project`
3. Check SSH key is in remote `~/.ssh/authorized_keys`
4. Check mount point permissions

### "Connection refused"

**Causes**:
- Remote server down
- Firewall blocking SSH port
- Incorrect host/port

**Solutions**:
1. Verify server is running
2. Test connection: `telnet host port`
3. Check firewall rules

### Stale Mounts

If mounts become stale after server restart:

```bash
# Manually unmount
fusermount -u /path/to/mount/point

# Or wait for hourly cleanup task to run
```

## Development

### Running Celery

Required for auto-unmount functionality:

```bash
# Worker
celery -A config.celery_app worker -l info

# Beat scheduler
celery -A config.celery_app beat -l info

# Both (development)
celery -A config.celery_app worker --beat -l info
```

### Testing Remote Projects

1. Set up a test remote server with SSH access
2. Add test credential via UI
3. Create test remote project
4. Verify file operations work
5. Wait 30+ minutes to verify auto-unmount
6. Check logs for Celery task execution

## Future Enhancements

Potential improvements:

1. **Connection pooling**: Reuse SSH connections for better performance
2. **Bandwidth monitoring**: Track data transferred
3. **Quota management**: Limit remote project access per user
4. **Multi-hop SSH**: Support jump hosts/bastion servers
5. **SFTP fallback**: If SSHFS unavailable
6. **Real-time sync**: Optional local cache with bidirectional sync
7. **Conflict detection**: Detect when remote files change externally

## References

- SSHFS documentation: https://github.com/libfuse/sshfs
- Emacs TRAMP: https://www.gnu.org/software/tramp/
- Django Celery Beat: https://django-celery-beat.readthedocs.io/

---

**Implementation Date**: 2025-11-26
**Status**: ✅ Complete and Ready for Testing
