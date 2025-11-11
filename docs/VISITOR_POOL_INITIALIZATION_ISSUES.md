# Visitor Pool Initialization Issues - Root Cause Analysis

**Date:** 2025-11-10
**Author:** Claude (Investigation)
**Status:** RESOLVED (Manual workaround applied)

## Summary

After running `reset_all_data --confirm`, the visitor pool was not automatically recreated, requiring manual intervention. This document analyzes the root causes and provides fixes for system reproducibility.

---

## Root Causes Identified

### 1. **Outdated Docker Image** ⚠️ CRITICAL

**Issue:**
- The Docker container is using an outdated `entrypoint.sh` that doesn't include visitor pool initialization
- Local file: 124 lines (includes visitor pool init at lines 109-117)
- Container file: 114 lines (missing visitor pool init)

**Evidence:**
```bash
$ wc -l deployment/docker/docker_dev/entrypoint.sh
124 deployment/docker/docker_dev/entrypoint.sh

$ docker exec scitex-cloud-dev-web-1 wc -l /entrypoint.sh
114 /entrypoint.sh

$ docker exec scitex-cloud-dev-web-1 grep "visitor pool" /entrypoint.sh
# NO OUTPUT - visitor pool code missing
```

**Impact:**
- Visitor pool is never initialized on container startup
- After `reset_all_data`, no visitor projects are created
- Anonymous users get "High Traffic" error immediately

**Fix:**
```bash
# Rebuild Docker image to include updated entrypoint.sh
make ENV=dev build
make ENV=dev restart
```

---

### 2. **VisitorPool Only Creates Directories for NEW Projects**

**Issue:**
- `VisitorPool.initialize_pool()` uses `get_or_create()`
- Directory creation only happens `if project_created:`
- If projects already exist in DB, directories are skipped

**Code Location:** `apps/project_app/services/visitor_pool.py:91-109`

```python
project, project_created = Project.objects.get_or_create(...)

if project_created:  # ⚠️ Only runs for NEW projects
    manager = get_project_filesystem_manager(user)
    success, project_path = manager.create_project_directory(project)
```

**Impact:**
- After `reset_all_data`, if visitor projects exist in DB but directories were deleted
- Running `create_visitor_pool` won't recreate directories
- Visitor users can't access their projects

**Fix:**
Update `visitor_pool.py` to always ensure directories exist:

```python
# Always ensure directory exists, not just for new projects
if project_created or not manager.get_project_root_path(project):
    success, project_path = manager.create_project_directory(project)
```

---

### 3. **Writer Workspace Initialization Depends on Gitea Success**

**Issue:**
- `_initialize_writer_structure()` is called from `create_gitea_repository` signal
- Only runs after successful Gitea repo clone
- Visitor projects fail Gitea creation (no Gitea accounts for visitors)
- Therefore, writer workspaces are never initialized

**Code Location:** `apps/project_app/signals.py:289`

```python
@receiver(post_save, sender=Project)
def create_gitea_repository(sender, instance, created, **kwargs):
    ...
    # Clone repository
    if result.returncode == 0:
        ...
        _initialize_writer_structure(project, project_dir)  # ⚠️ Never reached for visitor projects
    else:
        logger.error(f"Failed to clone repo: {result.stderr}")
```

**Gitea Errors for Visitors:**
```
ERRO: Gitea API error during user creation: user does not exist [uid: 0, name: ]
ERRO: Cannot create repository without Gitea user account
```

**Impact:**
- Visitor projects never get writer workspaces initialized
- "Create Writer Workspace" button shows even though workspace exists
- Visitor users see incomplete interface

**Fix:**
Create a separate signal for writer initialization that doesn't depend on Gitea:

```python
@receiver(post_save, sender=Project)
def initialize_writer_workspace(sender, instance, created, **kwargs):
    """Initialize writer workspace independent of Gitea status"""
    if not created:
        return

    # Wait for directory to be created
    from apps.project_app.services.project_filesystem import get_project_filesystem_manager
    manager = get_project_filesystem_manager(instance.owner)
    project_dir = manager.get_project_root_path(instance)

    if project_dir and project_dir.exists():
        _initialize_writer_structure(instance, project_dir)
```

---

## Timeline of What Happened

1. **User ran:** `./scripts/utils/reset_all_data.sh --confirm`
   - Deleted all projects and users from database
   - Deleted Gitea repositories

2. **Container restarted:** `make ENV=dev restart`
   - Used outdated Docker image (Issue #1)
   - Entrypoint.sh WITHOUT visitor pool initialization
   - No visitor projects created

3. **User accessed site:** Got "High Traffic" message
   - No visitor slots available

4. **Manual fix #1:** `docker exec ... create_visitor_pool`
   - Created 32 visitor users in DB
   - Created 32 projects in DB
   - BUT directories not created (Issue #2 - projects existed from before)

5. **Manual fix #2:** Created project directories
   - Used Python shell to create directories for each project

6. **Manual fix #3:** Initialized writer workspaces
   - Used Python shell to call WriterService for each project
   - Workspaces created successfully

---

## Complete Fix Implementation

### Step 1: Update entrypoint.sh (ALREADY DONE ✅)

The local `entrypoint.sh` already has visitor pool initialization:

```bash
# deployment/docker/docker_dev/entrypoint.sh:112-117
initialize_visitor_pool() {
    echo_info "Initializing visitor pool..."
    python manage.py create_visitor_pool --verbosity 0 2>&1 | grep -v "ERRO\|WARN" || true
    echo_success "Visitor pool ready"
}
initialize_visitor_pool
```

### Step 2: Rebuild Docker Image

```bash
make ENV=dev build
make ENV=dev restart
```

### Step 3: Improve VisitorPool.initialize_pool()

Update `apps/project_app/services/visitor_pool.py`:

```python
# Always ensure directory exists
project, project_created = Project.objects.get_or_create(...)

# Create directory if project is new OR directory doesn't exist
from apps.project_app.services.project_filesystem import get_project_filesystem_manager
manager = get_project_filesystem_manager(user)
project_root = manager.get_project_root_path(project)

if project_created or not (project_root and project_root.exists()):
    success, project_path = manager.create_project_directory(project)
    if success:
        logger.info(f"[VisitorPool] Created project: {project_slug} at {project_path}")

        # Initialize writer workspace
        _initialize_writer_workspace(project, project_path)
        created_count += 1
    else:
        logger.error(f"[VisitorPool] Failed to create directory for {project_slug}")
        if project_created:
            project.delete()
```

### Step 4: Decouple Writer Initialization from Gitea

Add new signal in `apps/project_app/signals.py`:

```python
def _initialize_writer_workspace(project, project_dir):
    """Initialize writer workspace for a project (Gitea-independent)"""
    try:
        writer_dir = project_dir / "scitex" / "writer"
        if writer_dir.exists():
            logger.info(f"Writer workspace already exists for {project.slug}")
            return

        from scitex.writer import Writer
        from django.conf import settings

        template_branch = getattr(settings, 'SCITEX_WRITER_TEMPLATE_BRANCH', None)
        template_tag = getattr(settings, 'SCITEX_WRITER_TEMPLATE_TAG', None)

        writer = Writer(
            project_dir=writer_dir,
            git_strategy='parent',
            branch=template_branch,
            tag=template_tag
        )

        # Verify creation
        manuscript_dir = writer_dir / "01_manuscript"
        if manuscript_dir.exists():
            logger.info(f"Writer workspace initialized for {project.slug}")

            # Mark manuscript as initialized
            from apps.writer_app.models import Manuscript
            manuscript, _ = Manuscript.objects.get_or_create(
                project=project,
                owner=project.owner,
                defaults={'title': f'{project.name} Manuscript'}
            )
            Manuscript.objects.filter(id=manuscript.id).update(writer_initialized=True)
        else:
            logger.error(f"Writer workspace incomplete for {project.slug}")

    except Exception as e:
        logger.error(f"Failed to initialize writer workspace for {project.slug}: {e}")
        logger.exception("Full traceback:")


@receiver(post_save, sender=Project)
def initialize_writer_on_project_create(sender, instance, created, **kwargs):
    """Initialize writer workspace when project directory is ready"""
    if not created:
        return

    # This will be called after the project is created
    # We need to wait for the directory to exist first
    # The actual initialization happens in create_gitea_repository after clone
    pass  # Keep for now, actual logic in create_gitea_repository
```

---

## Testing Checklist

After implementing fixes, test the complete flow:

- [ ] Build new Docker image: `make ENV=dev build`
- [ ] Delete all data: `./scripts/utils/reset_all_data.sh --confirm`
- [ ] Restart containers: `make ENV=dev restart`
- [ ] Check logs: `docker logs scitex-cloud-dev-web-1 | grep "visitor pool"`
  - Should see: "Initializing visitor pool..." and "Visitor pool ready"
- [ ] Check DB: `docker exec ... python manage.py create_visitor_pool --status`
  - Should show: 32 total slots, 0 allocated
- [ ] Check directories: Verify `/app/data/users/visitor-001/default-project/` exists
- [ ] Check writer workspaces: Verify `scitex/writer/01_manuscript/` exists
- [ ] Access site as anonymous user: Should NOT see "High Traffic"
- [ ] Check writer interface: Should NOT see "Create Writer Workspace" button

---

## Prevention for Future

### 1. Always Rebuild Docker Image After entrypoint.sh Changes

```bash
# After modifying deployment/docker/docker_dev/entrypoint.sh
make ENV=dev build
make ENV=dev restart
```

### 2. Add Entrypoint Version Check

Add to `entrypoint.sh`:

```bash
ENTRYPOINT_VERSION="2.0.0-beta"
echo "Entrypoint version: $ENTRYPOINT_VERSION"
```

### 3. Add Visitor Pool Health Check

Create `apps/project_app/management/commands/check_visitor_pool_health.py`:

```python
"""Check visitor pool health and fix issues"""

from django.core.management.base import BaseCommand
from apps.project_app.services.visitor_pool import VisitorPool

class Command(BaseCommand):
    help = 'Check visitor pool health and fix common issues'

    def handle(self, *args, **options):
        # Check pool status
        status = VisitorPool.get_pool_status()
        self.stdout.write(f'Pool status: {status}')

        # Check directories exist
        # Check writer workspaces exist
        # Auto-fix if needed
```

---

## Conclusion

The visitor pool initialization failure was caused by:
1. **Outdated Docker image** (missing visitor pool init in entrypoint.sh)
2. **Directory creation logic** (only for new projects, not for existing)
3. **Tight coupling** between writer initialization and Gitea success

**Immediate Action Required:**
```bash
make ENV=dev build   # Rebuild with updated entrypoint.sh
```

**Long-term Improvements:**
- Decouple writer initialization from Gitea
- Add health checks
- Improve error visibility in entrypoint.sh

<!-- EOF -->
