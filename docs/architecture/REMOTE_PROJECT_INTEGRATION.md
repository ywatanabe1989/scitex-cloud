# Remote Project Integration Architecture

**Status**: Planning
**Created**: 2025-11-26
**Author**: ywatanabe (with Claude)

## Executive Summary

This document outlines the architecture for accessing remote filesystems (HPC clusters, cloud instances, personal servers) through SciTeX Cloud using a **TRAMP-like approach**.

**Key Concept**: Treat remote access as a **special project type** with:
- ✅ Dynamic on-demand mounting (like Emacs TRAMP)
- ✅ No local data storage (privacy-preserving)
- ✅ No Git handling (avoids confusion)
- ✅ On-the-fly file rendering
- ✅ Slow but secure

---

## Architecture: Remote as Special Project Type

### Terminology Clarity

**To avoid confusion:**

| Term | Means | Example |
|------|-------|---------|
| **Local Project** | Git repository on SciTeX Cloud | Gitea repo, fast, version control |
| **Remote Project** | SSHFS mount to external server | HPC home dir, slow, no Git |
| **Import from Git URL** | `git clone` into local project | GitHub/GitLab → Local Gitea |
| **Clone** | ❌ Avoid this term | Use "Import" instead |

**Clear Separation:**
- 📁 **Local Project** + "Import from Git URL" = Git development (fast, full Git)
- 🌐 **Remote Project** = File browsing only (slow, no Git)

### Concept: TRAMP-Like Access

Inspired by Emacs TRAMP (Transparent Remote Access, Multiple Protocol), remote filesystems are accessed **dynamically** without persistent local copies.

**Protocol Comparison for CRUD Operations:**

| Operation | SSHFS (Mount) | SSH Commands | SCP | Rsync |
|-----------|---------------|--------------|-----|-------|
| **Read** | ✅ Best (read from mount) | ✅ `ssh "cat file"` | ⚠️ Works but copies | ❌ Overkill |
| **Write** | ✅ Best (write to mount) | ✅ `ssh "cat > file"` | ⚠️ Needs temp file | ❌ Overkill |
| **Delete** | ✅ Best (rm on mount) | ✅ `ssh "rm file"` | ❌ Can't delete | ❌ Not designed |
| **List** | ✅ Best (ls on mount) | ✅ `ssh "ls -la"` | ❌ Can't list | ⚠️ Verbose |
| **Performance** | 🚀 Fast (cached) | 🐌 Network per op | 🐌 Network per op | 🐌 Slow startup |
| **Complexity** | ⚠️ Requires FUSE | ✅ Simple | ✅ Simple | ⚠️ Complex |

**Recommended Strategy:**

```
┌─────────────────────────────────────────────────┐
│ SSHFS Mount (Primary Method) ✅                 │
│ - All CRUD through mount point                  │
│ - Fast, cached, transparent                     │
│ - Most TRAMP-like experience                    │
└─────────────────────────────────────────────────┘
         │
         │ (if mount fails or not available)
         ↓
┌─────────────────────────────────────────────────┐
│ Direct SSH Commands (Fallback) ⚠️              │
│ - Read: ssh "cat file"                          │
│ - Write: ssh "cat > file" < content             │
│ - Delete: ssh "rm file"                         │
│ - List: ssh "ls -la"                            │
└─────────────────────────────────────────────────┘
         │
         │ (bulk operations only)
         ↓
┌─────────────────────────────────────────────────┐
│ Rsync (Template Sync Only) 🔧                  │
│ - Initialize SciTeX structure                   │
│ - Bulk file synchronization                    │
│ - NOT for individual file operations           │
└─────────────────────────────────────────────────┘
```

**Avoid SCP**: Deprecated, less flexible than SSH/SSHFS.

---

### Caching Strategy (Like TRAMP)

**Goal**: Balance performance with reliability and freshness.

**Multi-Level Cache:**

```
┌─────────────────────────────────────────────────────────┐
│ Level 1: SSHFS Kernel Cache (Fastest)                   │
│ - Metadata caching: 20 seconds                          │
│ - Directory entries: 20 seconds                         │
│ - Automatic invalidation on writes                      │
│ - Configured via SSHFS options                          │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ Level 2: Django Cache (Medium-term)                     │
│ - File tree structure: 5 minutes                        │
│ - File metadata: 2 minutes                              │
│ - Read-only data (size, mtime)                          │
│ - Invalidate on write operations                        │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ Level 3: Browser/UI Cache (Short-term)                  │
│ - File list UI: 30 seconds                              │
│ - File content preview: 1 minute                        │
│ - Manual refresh available                              │
└─────────────────────────────────────────────────────────┘
```

**SSHFS Cache Configuration:**

```python
# apps/project_app/services/remote_project_manager.py

def _mount(self):
    """Mount with TRAMP-like caching."""

    cmd = [
        "sshfs",
        remote_target,
        str(self.mount_point),

        # Cache configuration (like TRAMP)
        "-o", "cache_timeout=20",          # Metadata cache: 20 sec
        "-o", "entry_timeout=20",          # Directory entry cache: 20 sec
        "-o", "attr_timeout=20",           # Attribute cache: 20 sec
        "-o", "kernel_cache",              # Use kernel page cache
        "-o", "auto_cache",                # Automatic cache based on mtime

        # Reliability
        "-o", "reconnect",                 # Auto-reconnect on disconnect
        "-o", "ServerAliveInterval=15",    # Keepalive every 15 sec
        "-o", "ServerAliveCountMax=3",     # Disconnect after 3 failed keepalives

        # Performance vs Consistency trade-off
        "-o", "direct_io",                 # Bypass cache for writes (consistency)
        # OR
        # "-o", "writeback_cache",         # Cache writes (performance, less reliable)

        # Other options
        "-o", "Compression=yes",           # Compress traffic
        "-o", "allow_other",               # Allow other users
        "-o", f"IdentityFile={ssh_key_path}",
    ]
```

**Cache Trade-offs:**

| Configuration | Performance | Reliability | Use Case |
|---------------|-------------|-------------|----------|
| `cache_timeout=20` | ✅ Good | ✅ Good | **Recommended** - Balance |
| `cache_timeout=60` | ✅✅ Better | ⚠️ Stale data | Read-heavy workloads |
| `cache_timeout=5` | ⚠️ Slower | ✅✅ Fresh | Write-heavy, multi-user |
| `direct_io` | ⚠️ Slower writes | ✅✅ Consistent | **Recommended** for reliability |
| `writeback_cache` | ✅✅ Fast writes | ⚠️ Data loss risk | Use with caution |

**Django-Level Cache:**

```python
# apps/project_app/services/remote_project_manager.py

from django.core.cache import cache
from django.utils import timezone

class RemoteProjectManager:

    def list_directory(self, relative_path: str = ".") -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """List directory with Django cache."""

        # Cache key
        cache_key = f"remote_dir:{self.project.id}:{relative_path}"

        # Check cache (5 minutes TTL)
        cached = cache.get(cache_key)
        if cached:
            cached_data, cached_time = cached
            age = (timezone.now() - cached_time).total_seconds()

            # Use cache if < 5 minutes old
            if age < 300:  # 5 minutes
                logger.debug(f"Cache hit for {relative_path} (age: {age:.1f}s)")
                return True, cached_data, None

        # Ensure mounted
        success, error = self.ensure_mounted()
        if not success:
            return False, None, error

        # Read from filesystem
        dir_path = self.mount_point / relative_path

        try:
            entries = []
            for item in dir_path.iterdir():
                stat = item.stat()
                entries.append({
                    'name': item.name,
                    'path': str(item.relative_to(self.mount_point)),
                    'type': 'directory' if item.is_dir() else 'file',
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                })

            # Sort
            entries.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))

            # Cache result
            cache.set(
                cache_key,
                (entries, timezone.now()),
                timeout=300  # 5 minutes
            )

            self._update_last_accessed()
            return True, entries, None

        except Exception as e:
            return False, None, str(e)

    def invalidate_cache(self, relative_path: str = None):
        """Invalidate cache after writes."""
        if relative_path:
            # Invalidate specific path
            cache_key = f"remote_dir:{self.project.id}:{relative_path}"
            cache.delete(cache_key)

            # Also invalidate parent directory
            parent = str(Path(relative_path).parent)
            if parent != '.':
                self.invalidate_cache(parent)
        else:
            # Invalidate all cache for this project
            # (Use cache prefix pattern matching if available)
            cache.delete_pattern(f"remote_dir:{self.project.id}:*")

    def write_file(self, relative_path: str, content: str) -> Tuple[bool, Optional[str]]:
        """Write file and invalidate cache."""

        # ... write file ...

        # Invalidate cache on success
        if success:
            self.invalidate_cache(str(Path(relative_path).parent))

        return success, error
```

**Cache Invalidation Events:**

```python
# When to invalidate cache

# 1. File written
write_file() → invalidate parent directory cache

# 2. File deleted
delete_file() → invalidate parent directory cache

# 3. File renamed/moved
move_file() → invalidate both old and new parent caches

# 4. Manual refresh (user clicks refresh button)
refresh_button_click() → invalidate all cache

# 5. After unmount
unmount() → clear all cache for this project
```

**UI Cache Invalidation:**

```typescript
// apps/project_app/static/project_app/ts/remote_file_tree.ts

class RemoteFileTree {
    private cacheTimeout = 30000; // 30 seconds
    private lastFetch: Map<string, number> = new Map();

    async loadDirectory(path: string, forceRefresh = false): Promise<void> {
        const cacheKey = path;
        const now = Date.now();
        const lastFetchTime = this.lastFetch.get(cacheKey) || 0;
        const age = now - lastFetchTime;

        // Use cache if fresh and not forced
        if (!forceRefresh && age < this.cacheTimeout) {
            console.log(`UI cache hit: ${path} (age: ${age}ms)`);
            return; // Use cached UI
        }

        // Fetch from server
        console.log(`Fetching: ${path}`);
        const response = await fetch(`/api/projects/${username}/${slug}/files/?path=${path}`);
        const data = await response.json();

        // Update UI
        this.renderFileTree(data.files);

        // Update cache timestamp
        this.lastFetch.set(cacheKey, now);
    }

    // Manual refresh button
    async refreshDirectory(path: string): Promise<void> {
        await this.loadDirectory(path, true); // Force refresh
    }

    // Auto-invalidate on writes
    async saveFile(path: string, content: string): Promise<void> {
        await fetch(`/api/projects/${username}/${slug}/file/save/`, {
            method: 'POST',
            body: JSON.stringify({ path, content })
        });

        // Invalidate parent directory cache
        const parentPath = path.split('/').slice(0, -1).join('/');
        this.lastFetch.delete(parentPath); // Clear cache

        // Reload to show changes
        await this.loadDirectory(parentPath, true);
    }
}
```

**Reliability Features:**

```python
# apps/project_app/services/remote_project_manager.py

class RemoteProjectManager:

    def ensure_mounted(self) -> Tuple[bool, Optional[str]]:
        """Ensure mounted with connection health check."""

        # Check if already mounted
        if self._is_mounted():
            # Health check: Can we actually access it?
            try:
                # Try to stat mount point
                self.mount_point.stat()
                self._update_last_accessed()
                return True, None
            except OSError:
                # Mount is stale, remount
                logger.warning(f"Stale mount detected, remounting: {self.project.slug}")
                self.unmount()
                # Fall through to mount

        # Mount
        return self._mount()

    def read_file_with_retry(self, relative_path: str, max_retries=3) -> Tuple[bool, Optional[str], Optional[str]]:
        """Read file with automatic retry on network errors."""

        for attempt in range(max_retries):
            try:
                success, content, error = self.read_file(relative_path)

                if success:
                    return True, content, None

                # If mount issue, try remounting
                if "Input/output error" in str(error) or "Transport endpoint" in str(error):
                    logger.warning(f"Mount error on attempt {attempt+1}, remounting...")
                    self.unmount()
                    self.ensure_mounted()
                    continue

                # Other error, don't retry
                return False, None, error

            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Read failed on attempt {attempt+1}: {e}, retrying...")
                    time.sleep(1)  # Wait before retry
                    continue
                else:
                    return False, None, f"Failed after {max_retries} attempts: {str(e)}"

        return False, None, "Max retries exceeded"
```

**UI Loading States:**

```typescript
// Show cache status in UI
class RemoteFileIndicator {
    showCacheStatus(path: string, cached: boolean): void {
        const indicator = document.querySelector('.file-tree-status');

        if (cached) {
            indicator.innerHTML = `
                <span class="cache-indicator">
                    📦 Cached (${this.getCacheAge(path)})
                    <button onclick="refresh()">🔄 Refresh</button>
                </span>
            `;
        } else {
            indicator.innerHTML = `
                <span class="loading-indicator">
                    ⏳ Loading from remote...
                </span>
            `;
        }
    }
}
```

---

**Recommended Configuration (Production):**

```python
# Balance between performance and reliability

SSHFS_OPTIONS = {
    # Cache (performance)
    'cache_timeout': 20,        # 20 seconds (TRAMP-like)
    'entry_timeout': 20,
    'attr_timeout': 20,
    'kernel_cache': True,
    'auto_cache': True,

    # Reliability (stability)
    'reconnect': True,          # Auto-reconnect
    'ServerAliveInterval': 15,  # Keepalive
    'direct_io': True,          # Consistent writes (no write cache)

    # Performance
    'Compression': 'yes',
}

DJANGO_CACHE_TTL = {
    'file_tree': 300,   # 5 minutes
    'file_meta': 120,   # 2 minutes
}

UI_CACHE_TTL = 30  # 30 seconds
```

```
┌─────────────────────────────────────────────────┐
│ SciTeX Cloud Project Types                      │
├─────────────────────────────────────────────────┤
│                                                  │
│ 1. Standard Project (Local)                     │
│    - Gitea repository                           │
│    - Full Git support                           │
│    - Fast file operations                       │
│    - Data stored locally                        │
│                                                  │
│ 2. Remote Project ⭐ NEW                         │
│    - SSH connection                             │
│    - NO Git support                             │
│    - Slow file operations (network latency)     │
│    - NO local data storage (privacy)            │
│    - SSHFS mount on-demand                      │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## Database Schema

### Remote Project Type

```python
# apps/project_app/models.py

class Project(models.Model):
    """Existing Project model - add project_type field."""

    PROJECT_TYPES = [
        ('local', 'Local Repository'),    # Existing: Gitea
        ('remote', 'Remote Filesystem'),  # NEW: SSH mount
    ]

    project_type = models.CharField(
        max_length=20,
        choices=PROJECT_TYPES,
        default='local'
    )

    # Existing fields...
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)

    # Remote-specific fields (null for local projects)
    remote_config = models.OneToOneField(
        'RemoteProjectConfig',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='project'
    )


class RemoteProjectConfig(models.Model):
    """Configuration for remote filesystem access."""

    # SSH Connection
    ssh_host = models.CharField(max_length=255, help_text="e.g., spartan.hpc.unimelb.edu.au")
    ssh_port = models.IntegerField(default=22)
    ssh_username = models.CharField(max_length=100, help_text="Username on remote system")

    # SSH Key (reference to user's remote credential)
    remote_credential = models.ForeignKey(
        'RemoteCredential',
        on_delete=models.CASCADE,
        help_text="SSH key for authentication"
    )

    # Remote Path
    remote_path = models.CharField(
        max_length=500,
        help_text="Path on remote system (e.g., /home/username/project)"
    )

    # Mount State
    is_mounted = models.BooleanField(default=False)
    mount_point = models.CharField(max_length=500, blank=True, null=True)
    mounted_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Connection Test
    last_test_at = models.DateTimeField(null=True, blank=True)
    last_test_success = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.ssh_username}@{self.ssh_host}:{self.remote_path}"


class RemoteCredential(models.Model):
    """SSH credentials for remote systems."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='remote_credentials')

    # Remote System Info
    name = models.CharField(max_length=100, help_text="e.g., 'Spartan HPC', 'AWS Server'")
    ssh_host = models.CharField(max_length=255)
    ssh_port = models.IntegerField(default=22)
    ssh_username = models.CharField(max_length=100)

    # SSH Key
    ssh_public_key = models.TextField()
    ssh_key_fingerprint = models.CharField(max_length=100)
    private_key_path = models.CharField(max_length=500)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [['user', 'name']]

    def __str__(self):
        return f"{self.user.username} → {self.name}"
```

---

## Core Implementation: RemoteProjectManager

```python
# apps/project_app/services/remote_project_manager.py

import subprocess
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict, List
from django.utils import timezone
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class RemoteProjectManager:
    """
    Manage remote filesystem projects with TRAMP-like on-demand access.

    Key Features:
    - SSHFS mounting on-demand (lazy loading)
    - Auto-unmount after timeout (privacy)
    - No local data storage
    - No Git support (prevents confusion)
    """

    def __init__(self, project):
        """
        Initialize remote project manager.

        Args:
            project: Project instance (must be project_type='remote')
        """
        if project.project_type != 'remote':
            raise ValueError("Project must be type 'remote'")

        self.project = project
        self.config = project.remote_config

        # Mount point: /tmp/scitex_remote/{user_id}/{project_slug}
        self.mount_base = Path("/tmp/scitex_remote")
        self.mount_point = self.mount_base / str(project.owner.id) / project.slug

    def ensure_mounted(self) -> Tuple[bool, Optional[str]]:
        """
        Ensure remote filesystem is mounted (mount if not already).

        Returns:
            (success, error_message)
        """
        # Check if already mounted
        if self._is_mounted():
            logger.debug(f"Remote project {self.project.slug} already mounted")
            self._update_last_accessed()
            return True, None

        # Mount
        return self._mount()

    def _is_mounted(self) -> bool:
        """Check if filesystem is currently mounted."""
        if not self.mount_point.exists():
            return False

        # Check if mount point has FUSE filesystem
        cmd = ["mountpoint", "-q", str(self.mount_point)]
        result = subprocess.run(cmd, capture_output=True)

        is_mounted = result.returncode == 0

        # Update database state
        if is_mounted != self.config.is_mounted:
            self.config.is_mounted = is_mounted
            self.config.save(update_fields=['is_mounted'])

        return is_mounted

    def _mount(self) -> Tuple[bool, Optional[str]]:
        """
        Mount remote filesystem via SSHFS.

        Returns:
            (success, error_message)
        """
        # Create mount point
        self.mount_point.mkdir(parents=True, exist_ok=True)

        # Get SSH key
        ssh_key_path = self.config.remote_credential.private_key_path

        if not Path(ssh_key_path).exists():
            return False, f"SSH key not found: {ssh_key_path}"

        # SSHFS mount command
        remote_target = f"{self.config.ssh_username}@{self.config.ssh_host}:{self.config.remote_path}"

        cmd = [
            "sshfs",
            remote_target,
            str(self.mount_point),
            "-p", str(self.config.ssh_port),
            "-o", f"IdentityFile={ssh_key_path}",
            "-o", "StrictHostKeyChecking=accept-new",
            "-o", "ServerAliveInterval=15",
            "-o", "reconnect",
            "-o", "cache_timeout=20",
            "-o", "allow_other",
            "-o", "default_permissions",
            # Privacy: No caching to disk
            "-o", "kernel_cache",
            "-o", "entry_timeout=1",
            "-o", "attr_timeout=1",
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )

            # Update database
            self.config.is_mounted = True
            self.config.mount_point = str(self.mount_point)
            self.config.mounted_at = timezone.now()
            self.config.last_accessed = timezone.now()
            self.config.save()

            logger.info(
                f"Mounted remote project: {self.project.owner.username}/{self.project.slug} "
                f"→ {remote_target}"
            )

            return True, None

        except subprocess.CalledProcessError as e:
            error_msg = f"SSHFS mount failed: {e.stderr}"
            logger.error(error_msg)
            return False, error_msg

        except subprocess.TimeoutExpired:
            return False, "SSH connection timeout"

    def unmount(self) -> Tuple[bool, Optional[str]]:
        """
        Unmount remote filesystem.

        Returns:
            (success, error_message)
        """
        if not self._is_mounted():
            return True, None

        cmd = ["fusermount", "-u", str(self.mount_point)]

        try:
            subprocess.run(cmd, check=True, timeout=10, capture_output=True)

            # Update database
            self.config.is_mounted = False
            self.config.mount_point = None
            self.config.save()

            # Remove mount point directory
            try:
                self.mount_point.rmdir()
            except OSError:
                pass  # Directory not empty or doesn't exist

            logger.info(f"Unmounted remote project: {self.project.slug}")
            return True, None

        except subprocess.CalledProcessError as e:
            error_msg = f"Unmount failed: {e.stderr.decode()}"
            logger.error(error_msg)
            return False, error_msg

    def read_file(self, relative_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Read a file from remote filesystem (mounts if needed).

        Args:
            relative_path: Path relative to remote_path

        Returns:
            (success, content, error_message)
        """
        # Ensure mounted
        success, error = self.ensure_mounted()
        if not success:
            return False, None, error

        # Read file
        file_path = self.mount_point / relative_path

        try:
            content = file_path.read_text()
            self._update_last_accessed()
            return True, content, None

        except FileNotFoundError:
            return False, None, f"File not found: {relative_path}"
        except PermissionError:
            return False, None, f"Permission denied: {relative_path}"
        except Exception as e:
            return False, None, str(e)

    def write_file(self, relative_path: str, content: str) -> Tuple[bool, Optional[str]]:
        """
        Write a file to remote filesystem.

        Args:
            relative_path: Path relative to remote_path
            content: File content

        Returns:
            (success, error_message)
        """
        # Ensure mounted
        success, error = self.ensure_mounted()
        if not success:
            return False, error

        file_path = self.mount_point / relative_path

        try:
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            file_path.write_text(content)

            self._update_last_accessed()
            return True, None

        except PermissionError:
            return False, f"Permission denied: {relative_path}"
        except Exception as e:
            return False, str(e)

    def list_directory(self, relative_path: str = ".") -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """
        List directory contents from remote filesystem.

        Args:
            relative_path: Path relative to remote_path

        Returns:
            (success, file_list, error_message)
        """
        # Ensure mounted
        success, error = self.ensure_mounted()
        if not success:
            return False, None, error

        dir_path = self.mount_point / relative_path

        try:
            entries = []

            for item in dir_path.iterdir():
                stat = item.stat()

                entries.append({
                    'name': item.name,
                    'path': str(item.relative_to(self.mount_point)),
                    'type': 'directory' if item.is_dir() else 'file',
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                })

            # Sort: directories first, then alphabetically
            entries.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))

            self._update_last_accessed()
            return True, entries, None

        except FileNotFoundError:
            return False, None, f"Directory not found: {relative_path}"
        except PermissionError:
            return False, None, f"Permission denied: {relative_path}"
        except Exception as e:
            return False, None, str(e)

    def _update_last_accessed(self):
        """Update last accessed timestamp."""
        self.config.last_accessed = timezone.now()
        self.config.save(update_fields=['last_accessed'])

    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """
        Test SSH connection to remote system.

        Returns:
            (success, error_message)
        """
        ssh_key_path = self.config.remote_credential.private_key_path

        cmd = [
            "ssh",
            "-p", str(self.config.ssh_port),
            "-i", ssh_key_path,
            "-o", "StrictHostKeyChecking=accept-new",
            "-o", "ConnectTimeout=10",
            f"{self.config.ssh_username}@{self.config.ssh_host}",
            "echo 'OK'"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15,
                check=True
            )

            # Update database
            self.config.last_test_at = timezone.now()
            self.config.last_test_success = True
            self.config.save()

            return True, None

        except subprocess.CalledProcessError as e:
            error_msg = f"SSH connection failed: {e.stderr}"

            self.config.last_test_at = timezone.now()
            self.config.last_test_success = False
            self.config.save()

            return False, error_msg

        except subprocess.TimeoutExpired:
            return False, "Connection timeout"
```

---

## Project Creation Flow

### 1. Create Remote Project UI

**Location**: `/new/` (project creation page)

```html
<!-- apps/project_app/templates/project_app/new.html -->

<form method="post">
  <h2>Create New Project</h2>

  <!-- Project Type Selection -->
  <div class="form-group">
    <label>Project Type</label>
    <div class="radio-group">
      <input type="radio" name="project_type" value="local" id="type_local" checked>
      <label for="type_local">
        📁 Local Repository
        <small>Git-enabled, fast, stored on SciTeX Cloud</small>
      </label>

      <input type="radio" name="project_type" value="remote" id="type_remote">
      <label for="type_remote">
        🌐 Remote Filesystem
        <small>TRAMP-like access, SSH mount, no Git, slow but private</small>
      </label>
    </div>
  </div>

  <!-- Local Project Fields (shown when type_local selected) -->
  <div id="local_fields" class="project-type-fields">
    <div class="form-group">
      <label>Project Name</label>
      <input type="text" name="name" required>
    </div>

    <div class="form-group">
      <label>Initialize From</label>
      <select name="init_from">
        <option value="template">SciTeX Template</option>
        <option value="empty">Empty Repository</option>
        <option value="import-git">Import from Git URL</option>
      </select>
    </div>
  </div>

  <!-- Remote Project Fields (shown when type_remote selected) -->
  <div id="remote_fields" class="project-type-fields" style="display: none;">
    <div class="form-group">
      <label>Project Name</label>
      <input type="text" name="name" required>
      <small>Display name for this remote connection</small>
    </div>

    <div class="form-group">
      <label>Remote System</label>
      <select name="remote_credential_id" required>
        <option value="">-- Select Remote System --</option>
        {% for cred in user.remote_credentials.all %}
        <option value="{{ cred.id }}">
          {{ cred.name }} ({{ cred.ssh_username }}@{{ cred.ssh_host }})
        </option>
        {% endfor %}
      </select>
      <a href="/accounts/settings/remote/">+ Add Remote System</a>
    </div>

    <div class="form-group">
      <label>Remote Path</label>
      <input type="text" name="remote_path" placeholder="/home/username/project" required>
      <small>Absolute path on remote system</small>
    </div>

    <button type="button" onclick="testRemoteConnection()">
      🔍 Test Connection
    </button>

    <div class="alert alert-warning">
      ⚠️ Remote projects:
      <ul>
        <li>No Git support (no commits/branches/history)</li>
        <li>Slower file operations (network latency)</li>
        <li>No local data storage (privacy-preserving)</li>
        <li>Requires stable network connection</li>
      </ul>
    </div>
  </div>

  <button type="submit">Create Project</button>
</form>

<script>
// Toggle fields based on project type
document.querySelectorAll('input[name="project_type"]').forEach(radio => {
  radio.addEventListener('change', (e) => {
    if (e.target.value === 'local') {
      document.getElementById('local_fields').style.display = 'block';
      document.getElementById('remote_fields').style.display = 'none';
    } else {
      document.getElementById('local_fields').style.display = 'none';
      document.getElementById('remote_fields').style.display = 'block';
    }
  });
});
</script>
```

### 2. View: Create Remote Project

```python
# apps/project_app/views/project_views.py

@login_required
def create_project(request):
    """Create new project (local or remote)."""

    if request.method == 'POST':
        project_type = request.POST.get('project_type')

        if project_type == 'remote':
            return _create_remote_project(request)
        else:
            return _create_local_project(request)  # Existing logic

    # GET: Show form
    context = {
        'remote_credentials': request.user.remote_credentials.filter(is_active=True)
    }
    return render(request, 'project_app/new.html', context)


def _create_remote_project(request):
    """Create remote project."""
    from apps.project_app.services.remote_project_manager import RemoteProjectManager

    name = request.POST.get('name')
    slug = slugify(name)
    remote_credential_id = request.POST.get('remote_credential_id')
    remote_path = request.POST.get('remote_path')

    # Validate
    if Project.objects.filter(owner=request.user, slug=slug).exists():
        messages.error(request, f"Project '{slug}' already exists")
        return redirect('project_app:new')

    try:
        remote_credential = RemoteCredential.objects.get(
            id=remote_credential_id,
            user=request.user
        )
    except RemoteCredential.DoesNotExist:
        messages.error(request, "Invalid remote credential")
        return redirect('project_app:new')

    # Create project
    project = Project.objects.create(
        owner=request.user,
        name=name,
        slug=slug,
        project_type='remote'
    )

    # Create remote config
    remote_config = RemoteProjectConfig.objects.create(
        ssh_host=remote_credential.ssh_host,
        ssh_port=remote_credential.ssh_port,
        ssh_username=remote_credential.ssh_username,
        remote_credential=remote_credential,
        remote_path=remote_path
    )

    project.remote_config = remote_config
    project.save()

    # Test connection
    manager = RemoteProjectManager(project)
    success, error = manager.test_connection()

    if success:
        messages.success(request, f"Remote project '{name}' created successfully!")
        return redirect('project_app:detail', username=request.user.username, slug=slug)
    else:
        messages.warning(
            request,
            f"Project created but connection test failed: {error}. "
            f"Please check your remote system configuration."
        )
        return redirect('project_app:detail', username=request.user.username, slug=slug)
```

---

## File Tree API for Remote Projects

```python
# apps/project_app/views/api_views.py

@login_required
def api_file_tree(request, username, project_slug):
    """Get file tree (local or remote)."""

    project = get_object_or_404(
        Project,
        owner__username=username,
        slug=project_slug
    )

    # Check permissions
    if not project.can_access(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    if project.project_type == 'remote':
        return _api_remote_file_tree(request, project)
    else:
        return _api_local_file_tree(request, project)  # Existing logic


def _api_remote_file_tree(request, project):
    """Get file tree from remote filesystem."""
    from apps.project_app.services.remote_project_manager import RemoteProjectManager

    manager = RemoteProjectManager(project)

    # Get requested path
    path = request.GET.get('path', '.')

    # List directory
    success, entries, error = manager.list_directory(path)

    if not success:
        return JsonResponse({
            'error': error,
            'is_mounted': manager._is_mounted()
        }, status=500)

    # Build tree structure
    tree = []
    for entry in entries:
        tree.append({
            'name': entry['name'],
            'path': entry['path'],
            'type': entry['type'],
            'size': entry['size'],
            'modified': entry['modified'],
        })

    return JsonResponse({
        'tree': tree,
        'is_remote': True,
        'is_mounted': manager.config.is_mounted,
        'remote_host': f"{manager.config.ssh_username}@{manager.config.ssh_host}",
        'remote_path': manager.config.remote_path,
    })
```

---

## Monaco Editor Integration for Remote Files

```typescript
// apps/code_app/static/code_app/ts/workspace/editor/MonacoManager.ts

class MonacoManager {

  async openFile(filePath: string, projectType: 'local' | 'remote'): Promise<void> {

    if (projectType === 'remote') {
      return this.openRemoteFile(filePath);
    } else {
      return this.openLocalFile(filePath);  // Existing logic
    }
  }

  async openRemoteFile(filePath: string): Promise<void> {
    // Show loading indicator
    this.showLoading(`Loading remote file: ${filePath}`);

    try {
      // Fetch file content via API
      const response = await fetch(`/api/projects/${username}/${slug}/file/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: filePath })
      });

      if (!response.ok) {
        throw new Error(`Failed to load file: ${response.statusText}`);
      }

      const data = await response.json();

      // Create or update model
      const model = monaco.editor.createModel(
        data.content,
        this.detectLanguage(filePath),
        monaco.Uri.file(filePath)
      );

      // Set model to editor
      this.editor.setModel(model);

      // Mark as remote (read-only warning banner)
      this.showRemoteWarning(
        `Remote file: ${data.remote_host}:${filePath}. ` +
        `Changes will be saved directly to remote system.`
      );

      this.hideLoading();

    } catch (error) {
      this.hideLoading();
      this.showError(`Failed to open remote file: ${error.message}`);
    }
  }

  async saveRemoteFile(filePath: string, content: string): Promise<void> {
    // Show saving indicator
    this.showSaving(`Saving to remote: ${filePath}`);

    try {
      const response = await fetch(`/api/projects/${username}/${slug}/file/save/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          path: filePath,
          content: content
        })
      });

      if (!response.ok) {
        throw new Error(`Save failed: ${response.statusText}`);
      }

      this.showSuccess(`Saved to remote: ${filePath}`);

    } catch (error) {
      this.showError(`Failed to save remote file: ${error.message}`);
    }
  }

  showRemoteWarning(message: string): void {
    // Display warning banner above editor
    const banner = document.createElement('div');
    banner.className = 'remote-file-banner';
    banner.innerHTML = `
      <div class="alert alert-warning">
        ⚠️ ${message}
        <button onclick="this.parentElement.remove()">×</button>
      </div>
    `;
    this.editorContainer.prepend(banner);
  }
}
```

---

## User Workflows

### Workflow 0: Power User - Git Clone from Remote ⭐ **Recommended for Git Work**

**Use Case**: User has code on remote HPC/server and wants full Git functionality.

**Solution**: Clone to **local project** (don't use remote project type).

```bash
# Option A: Clone via SSH from remote system
# 1. Create new LOCAL project in SciTeX Cloud
# 2. In workspace terminal:
cd /home/scitex/projects/my-research
git clone ssh://user@hpc.edu:/home/user/research-code .

# Option B: If remote code is already on GitHub/GitLab
git clone git@github.com:user/research-code .

# Now you have full Git functionality:
git status
git commit -m "Update analysis"
git push

# Can still submit jobs to HPC via SLURM API
# (code is local, execution is remote)
```

**Why this is better than remote projects for Git work:**
- ✅ Full Git support (commits, branches, history)
- ✅ Fast file operations (local storage)
- ✅ Offline work possible
- ✅ SciTeX Cloud Gitea collaboration features
- ✅ Best of both worlds: develop locally, compute remotely

### Workflow 1: Browse Remote Files (Use Remote Project)

**Use Case**: Browse HPC results, edit config files, view logs (no Git needed).

**Solution**: Create **remote project**.

```
1. User creates remote project:
   - Type: Remote Filesystem
   - System: "Spartan HPC" (from saved credentials)
   - Path: /home/username/results/

2. User opens project in workspace
   - First access: System auto-mounts via SSHFS
   - File tree shows remote files (read from mount point)

3. User browses and downloads results
   - Click file → Opens in Monaco editor (via mount)
   - Download specific files to local workspace
   - No local storage of remote files

4. Auto-unmount after 30 minutes inactivity
```

**When to use remote projects:**
- ✅ Browse large result directories on HPC
- ✅ Edit config files (`.bashrc`, SLURM scripts)
- ✅ View logs without downloading
- ✅ Quick one-off file access
- ❌ NOT for Git development (use Workflow 0 instead)

### Workflow 2: Edit Remote Config File

**Use Case**: Edit `.bashrc` on HPC without cloning entire home directory.

```
1. Remote project already created (points to /home/username/)
2. Navigate to file in tree: .bashrc
3. Click to open → System mounts if needed
4. Edit in Monaco editor
5. Save → Writes directly to HPC via mount
6. No local copy stored
```

### Workflow 3: Submit Job to HPC with Local Code

**Use Case**: Develop locally, execute on HPC.

```
1. Develop in LOCAL Git project (fast, full Git)
2. Submit job via SLURM API:
   - Code is rsynced to HPC temporarily
   - Job runs on HPC compute nodes
   - Results fetched back when complete
3. No need for remote project type
```

**This combines:**
- Local Git development (fast)
- Remote execution (powerful)
- No mounted filesystems needed

---

## Initialize SciTeX Structure (Universal Feature)

### Use Case

User has existing project (local OR remote) and wants to add SciTeX directory structure to it from the web UI.

**Examples:**
- Local project: Empty or imported from GitHub, missing SciTeX structure
- Remote project: Existing HPC project, want to add SciTeX modules

**Button**: "Initialize SciTeX Structure" (works for both local and remote)

**What it does:**
1. **Always syncs from master template**: `templates/research-master/scitex/`
2. Creates: `scitex/vis/`, `scitex/writer/`, `scitex/scholar/`, `scitex/code/`, etc.
3. **Non-destructive**: Won't override existing files
4. **Consistent**: Same structure for all projects (local and remote)

**Source of Truth**:
- **Master template**: `templates/research-master/scitex/` ✅
- All projects sync from this **single source**
- Ensures **consistency** across all projects (local and remote)
- Re-clicking button syncs **new files** from updated template (non-destructive)

**Example Workflow**:
```bash
# Admin updates master template
templates/research-master/scitex/vis/new-feature.py  # Added

# User clicks "Initialize SciTeX Structure"
# → New files copied to project
# → Existing files untouched (non-destructive)
# → User gets latest template additions
```

### Implementation (Universal - Local + Remote)

```python
# apps/project_app/services/project_manager.py (NEW unified manager)

class ProjectManager:
    """
    Unified project manager for local and remote projects.

    Handles common operations that work across both project types.
    """

    def __init__(self, project):
        self.project = project

    def initialize_scitex_structure(self) -> Tuple[bool, Dict, Optional[str]]:
        """
        Sync SciTeX template structure to project (local or remote).

        Dispatches to appropriate implementation based on project type.

        Returns:
            (success, stats, error_message)
        """
        if self.project.project_type == 'local':
            return self._initialize_local()
        elif self.project.project_type == 'remote':
            return self._initialize_remote()
        else:
            return False, {}, f"Unknown project type: {self.project.project_type}"

    def _initialize_local(self) -> Tuple[bool, Dict, Optional[str]]:
        """Initialize SciTeX structure on LOCAL project."""
        from django.conf import settings
        import shutil

        # Get template directory
        template_dir = Path(settings.BASE_DIR) / 'templates' / 'research-master' / 'scitex'

        if not template_dir.exists():
            return False, {}, f"Template not found: {template_dir}"

        # Get project directory (from Gitea)
        from apps.project_app.services.directory_manager import DirectoryManager
        dir_manager = DirectoryManager(self.project.owner)
        project_path = dir_manager.get_project_path(self.project)

        if not project_path or not project_path.exists():
            return False, {}, "Project directory not found"

        # Target: {project_path}/scitex/
        target_dir = project_path / 'scitex'

        try:
            stats = {
                'files_created': 0,
                'files_skipped': 0,
                'bytes_transferred': 0,
            }

            # Walk through template and copy files (non-destructive)
            for src_file in template_dir.rglob('*'):
                if src_file.is_file():
                    # Relative path within scitex/
                    rel_path = src_file.relative_to(template_dir)
                    dest_file = target_dir / rel_path

                    # Skip if exists (non-destructive)
                    if dest_file.exists():
                        stats['files_skipped'] += 1
                        continue

                    # Create parent directories
                    dest_file.parent.mkdir(parents=True, exist_ok=True)

                    # Copy file
                    shutil.copy2(src_file, dest_file)

                    stats['files_created'] += 1
                    stats['bytes_transferred'] += src_file.stat().st_size

            logger.info(
                f"SciTeX structure initialized (local): "
                f"{self.project.owner.username}/{self.project.slug} - "
                f"{stats['files_created']} files created"
            )

            return True, stats, None

        except Exception as e:
            logger.error(f"Failed to initialize local structure: {e}")
            return False, {}, str(e)

    def _initialize_remote(self) -> Tuple[bool, Dict, Optional[str]]:
        """
        Sync SciTeX template structure to remote filesystem.

        Creates scitex/ directory on remote with standard structure:
        - scitex/vis/
        - scitex/writer/
        - scitex/scholar/
        - scitex/code/
        - etc.

        Non-destructive: Won't override existing files.

        Returns:
            (success, stats, error_message)
            stats: {
                'files_created': int,
                'files_skipped': int,
                'bytes_transferred': int,
            }
        """
        # Get template directory
        from django.conf import settings
        template_dir = Path(settings.BASE_DIR) / 'templates' / 'research-master' / 'scitex'

        if not template_dir.exists():
            return False, {}, f"Template not found: {template_dir}"

        # Get SSH key
        ssh_key_path = self.config.remote_credential.private_key_path

        # Remote target
        remote_target = (
            f"{self.config.ssh_username}@{self.config.ssh_host}:"
            f"{self.config.remote_path}/scitex/"
        )

        # Rsync command - NON-DESTRUCTIVE
        cmd = [
            "rsync",
            "-avz",
            "--progress",
            "--ignore-existing",    # Don't override existing files ✅
            "--stats",              # Get statistics
            "-e", f"ssh -p {self.config.ssh_port} -i {ssh_key_path} -o StrictHostKeyChecking=accept-new",
            f"{template_dir}/",     # Source: SciTeX template
            remote_target,          # Target: remote/scitex/
        ]

        try:
            logger.info(
                f"Initializing SciTeX structure on remote: "
                f"{self.config.ssh_username}@{self.config.ssh_host}:{self.config.remote_path}"
            )

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
                check=True
            )

            # Parse rsync stats from output
            stats = self._parse_rsync_stats(result.stdout)

            logger.info(
                f"SciTeX structure initialized: "
                f"{stats['files_created']} files created, "
                f"{stats['files_skipped']} files skipped"
            )

            return True, stats, None

        except subprocess.CalledProcessError as e:
            error_msg = f"Rsync failed: {e.stderr}"
            logger.error(error_msg)
            return False, {}, error_msg

        except subprocess.TimeoutExpired:
            return False, {}, "Rsync timeout (5 minutes)"

    def _parse_rsync_stats(self, output: str) -> Dict:
        """Parse rsync --stats output."""
        import re

        stats = {
            'files_created': 0,
            'files_skipped': 0,
            'bytes_transferred': 0,
        }

        # Extract statistics from rsync output
        # "Number of created files: 42"
        match = re.search(r'Number of created files:\s*(\d+)', output)
        if match:
            stats['files_created'] = int(match.group(1))

        # "Number of regular files transferred: 15"
        match = re.search(r'Number of regular files transferred:\s*(\d+)', output)
        if match:
            stats['files_created'] = int(match.group(1))

        # "Total transferred file size: 123456 bytes"
        match = re.search(r'Total transferred file size:\s*([\d,]+)', output)
        if match:
            stats['bytes_transferred'] = int(match.group(1).replace(',', ''))

        return stats
```

### API Endpoint

```python
# apps/project_app/views/api_views.py

@login_required
@require_http_methods(["POST"])
def api_initialize_scitex_structure(request, username, project_slug):
    """
    Initialize SciTeX directory structure on remote filesystem.

    POST /{username}/{project_slug}/api/initialize-scitex/

    Returns:
        {
            "success": true,
            "stats": {
                "files_created": 42,
                "files_skipped": 5,
                "bytes_transferred": 123456
            },
            "message": "SciTeX structure initialized successfully"
        }
    """
    from apps.project_app.services.remote_project_manager import RemoteProjectManager

    # Get project
    project = get_object_or_404(
        Project,
        owner__username=username,
        slug=project_slug
    )

    # Check permissions
    if not project.can_write(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    # Initialize structure (works for both local and remote)
    from apps.project_app.services.project_manager import ProjectManager

    manager = ProjectManager(project)
    success, stats, error = manager.initialize_scitex_structure()

    if success:
        return JsonResponse({
            'success': True,
            'stats': stats,
            'message': (
                f"SciTeX structure initialized: "
                f"{stats['files_created']} files created, "
                f"{stats['files_skipped']} files skipped"
            )
        })
    else:
        return JsonResponse({
            'success': False,
            'error': error
        }, status=500)
```

### Frontend JavaScript

```javascript
// apps/project_app/static/project_app/js/remote_project.js

async function initializeSciTeXStructure(projectSlug) {
  // Confirm with user
  const confirmed = confirm(
    'This will create scitex/ directory structure in your project.\n\n' +
    'Existing files will NOT be overwritten.\n\n' +
    'Continue?'
  );

  if (!confirmed) return;

  // Show progress
  const button = event.target;
  button.disabled = true;
  button.textContent = '⏳ Syncing...';

  try {
    const response = await fetch(
      `/${username}/${projectSlug}/api/initialize-scitex/`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        }
      }
    );

    const data = await response.json();

    if (data.success) {
      // Show success
      alert(
        `✅ SciTeX structure initialized!\n\n` +
        `Files created: ${data.stats.files_created}\n` +
        `Files skipped: ${data.stats.files_skipped}\n` +
        `Size: ${formatBytes(data.stats.bytes_transferred)}`
      );

      // Refresh file tree
      window.location.reload();
    } else {
      alert(`❌ Failed: ${data.error}`);
    }
  } catch (error) {
    alert(`❌ Error: ${error.message}`);
  } finally {
    button.disabled = false;
    button.textContent = '📁 Initialize SciTeX Structure on Remote';
  }
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
```

---

## Auto-Unmount for Privacy

```python
# apps/project_app/tasks.py (Celery task)

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from apps.project_app.models import RemoteProjectConfig
from apps.project_app.services.remote_project_manager import RemoteProjectManager


@shared_task
def auto_unmount_inactive_remote_projects():
    """
    Auto-unmount remote projects that haven't been accessed in X minutes.

    Run every 5 minutes via Celery beat.
    """
    # Unmount projects inactive for > 30 minutes
    timeout = timezone.now() - timedelta(minutes=30)

    inactive_configs = RemoteProjectConfig.objects.filter(
        is_mounted=True,
        last_accessed__lt=timeout
    )

    for config in inactive_configs:
        project = config.project

        try:
            manager = RemoteProjectManager(project)
            success, error = manager.unmount()

            if success:
                logger.info(
                    f"Auto-unmounted inactive remote project: "
                    f"{project.owner.username}/{project.slug}"
                )
            else:
                logger.warning(
                    f"Failed to auto-unmount {project.slug}: {error}"
                )

        except Exception as e:
            logger.error(f"Error auto-unmounting {project.slug}: {e}")
```

```python
# config/celery.py

from celery.schedules import crontab

app.conf.beat_schedule = {
    'auto-unmount-remote-projects': {
        'task': 'apps.project_app.tasks.auto_unmount_inactive_remote_projects',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
}
```

---

## Benefits of Remote Project Approach

### ✅ Advantages

1. **No Git Confusion**: Remote projects explicitly have no Git support
2. **Privacy-Preserving**: No local data storage, auto-unmount after inactivity
3. **Simple Mental Model**: "Remote = TRAMP-like, Local = Git"
4. **Consistent UI**: Same interface for local and remote projects
5. **Generic**: Works with HPC, cloud instances, personal servers, etc.
6. **Lazy Loading**: Mount only when accessed (saves resources)

### ⚠️ Trade-offs

1. **Slower**: Network latency for every file operation
2. **No Offline**: Requires active network connection
3. **No Git**: Cannot commit, branch, or view history
4. **No Full-Text Search**: Cannot grep across all files efficiently
5. **Mount Dependencies**: Requires FUSE/SSHFS support

---

## UI/UX Indicators

### Remote Project Badge

```html
<!-- Project header -->
<div class="project-header">
  <h1>
    {{ project.name }}

    {% if project.project_type == 'remote' %}
    <span class="badge badge-remote" title="Remote filesystem via SSH">
      🌐 Remote
    </span>
    {% endif %}
  </h1>

  {% if project.project_type == 'remote' %}
  <div class="remote-status">
    {% if project.remote_config.is_mounted %}
    <span class="status-mounted">
      ✅ Mounted: {{ project.remote_config.ssh_username }}@{{ project.remote_config.ssh_host }}
    </span>
    {% else %}
    <span class="status-unmounted">
      ⏸️ Not mounted (will mount on first access)
    </span>
    {% endif %}
  </div>
  {% endif %}
</div>
```

### Project Settings - SciTeX Structure (All Projects)

**Location**: `/{username}/{project_slug}/settings/` or project overview

**This button appears for ALL projects (local and remote):**

```html
<!-- apps/project_app/templates/project_app/detail.html -->

<!-- For ALL projects: Show SciTeX structure button -->
<div class="project-settings">
  <h3>⚙️ Project Settings</h3>

  <table class="details-table">
    <tr>
      <th>SciTeX Structure</th>
      <td>
        <button
          onclick="initializeSciTeXStructure('{{ project.slug }}')"
          class="btn btn-primary">
          📁 Initialize SciTeX Structure
        </button>
        <br>
        <small class="text-muted">
          {% if project.project_type == 'local' %}
            Syncs scitex/ template to local project (won't override existing files)
          {% else %}
            Syncs scitex/ template to remote filesystem (won't override existing files)
          {% endif %}
        </small>
      </td>
    </tr>
  </table>
</div>

<!-- For REMOTE projects: Show additional remote-specific settings -->
{% if project.project_type == 'remote' %}
<div class="remote-project-details">
  <h3>🌐 Remote Connection Details</h3>

  <table class="details-table">
    <tr>
      <th>Remote System</th>
      <td>
        {{ project.remote_config.remote_credential.name }}
        <span class="text-muted">
          ({{ project.remote_config.ssh_username }}@{{ project.remote_config.ssh_host }}:{{ project.remote_config.ssh_port }})
        </span>
      </td>
    </tr>

    <tr>
      <th>Remote Path</th>
      <td><code>{{ project.remote_config.remote_path }}</code></td>
    </tr>

    <tr>
      <th>SSH Key</th>
      <td>
        {{ project.remote_config.remote_credential.name }}
        <br>
        <small class="text-muted">
          Fingerprint: <code>{{ project.remote_config.remote_credential.ssh_key_fingerprint }}</code>
        </small>
        <br>
        <a href="/accounts/settings/remote/">Manage SSH Keys</a>
      </td>
    </tr>

    <tr>
      <th>Mount Status</th>
      <td>
        {% if project.remote_config.is_mounted %}
          <span class="badge badge-success">✅ Currently Mounted</span>
          <br>
          <small>Mounted at: {{ project.remote_config.mounted_at|timesince }} ago</small>
          <br>
          <small>Last accessed: {{ project.remote_config.last_accessed|timesince }} ago</small>
          <br>
          <button onclick="unmountRemote('{{ project.slug }}')">Unmount Now</button>
        {% else %}
          <span class="badge badge-secondary">⏸️ Not Mounted</span>
          <br>
          <small>Will mount automatically on first access</small>
        {% endif %}
      </td>
    </tr>

    <tr>
      <th>Connection Test</th>
      <td>
        {% if project.remote_config.last_test_success %}
          <span class="badge badge-success">✅ Connected</span>
          <small>(tested {{ project.remote_config.last_test_at|timesince }} ago)</small>
        {% else %}
          <span class="badge badge-danger">❌ Failed</span>
          <small>(last attempt {{ project.remote_config.last_test_at|timesince }} ago)</small>
        {% endif %}
        <br>
        <button onclick="testRemoteConnection('{{ project.slug }}')">Test Connection Now</button>
      </td>
    </tr>
  </table>

  <div class="alert alert-info mt-3">
    ℹ️ <strong>About Remote Projects:</strong>
    <ul>
      <li>Files are accessed on-demand via SSH (no local copies)</li>
      <li>Auto-unmounts after 30 minutes of inactivity for privacy</li>
      <li>Git operations are not available (clone to local project if needed)</li>
      <li>Network latency affects file operation speed</li>
    </ul>
  </div>
</div>
{% endif %}
```

### Disabled Git Features

```html
<!-- For remote projects, hide/disable Git UI elements -->
{% if project.project_type == 'remote' %}
  <!-- No commit button -->
  <!-- No branch selector -->
  <!-- No Git history -->
  <!-- No pull/push buttons -->

  <div class="alert alert-info">
    ℹ️ This is a remote project. Git operations are not available.
    Changes are saved directly to {{ project.remote_config.ssh_host }}.
  </div>
{% endif %}
```

---

## Implementation Phases

### Phase 1: Core Remote Project (1 week)

- [ ] Database models (`RemoteProjectConfig`, `RemoteCredential`)
- [ ] `RemoteProjectManager` class (mount/unmount/read/write/list)
- [ ] Project creation UI (remote type selection)
- [ ] File tree API for remote projects
- [ ] Monaco editor integration (open/save remote files)

### Phase 2: Remote Credentials Management (3 days)

- [ ] UI: `/accounts/settings/remote/` (manage remote systems)
- [ ] SSH key generation for remote access
- [ ] Connection testing
- [ ] Credential validation

### Phase 3: Auto-Unmount & Privacy (2 days)

- [ ] Celery task for auto-unmount
- [ ] Last accessed tracking
- [ ] Manual unmount API endpoint
- [ ] Mount status indicators in UI

### Phase 4: Polish & Documentation (2 days)

- [ ] User guide: "Working with Remote Projects"
- [ ] Performance tuning (SSHFS options)
- [ ] Error handling (connection loss, permission issues)
- [ ] Integration tests

---

## Comparison: Remote vs Local Projects

| Feature | Local Project | Remote Project |
|---------|---------------|----------------|
| **Storage** | SciTeX Cloud | Remote system |
| **Git Support** | ✅ Full | ❌ None |
| **File Operations** | 🚀 Fast | 🐌 Slow (network) |
| **Offline Work** | ✅ Yes | ❌ No |
| **Privacy** | ⚠️ Data stored locally | ✅ No local storage |
| **Full-Text Search** | ✅ Fast | ❌ Slow/limited |
| **Collaboration** | ✅ Gitea features | ❌ SSH-based only |
| **Use Case** | Development, version control | Browse remote data, edit configs |

---

## Concerns and Mitigations

### 1. **FUSE/SSHFS Availability** ⚠️

**Concern**: Not all environments support FUSE (Docker containers, restrictive systems)

**Mitigation**:
```python
# Fallback to SSH commands if SSHFS unavailable
def ensure_file_access(self):
    if self._can_use_sshfs():
        return self.ensure_mounted()  # SSHFS
    else:
        return self._use_ssh_commands()  # Fallback
```

### 2. **UID/GID Mapping** ⚠️

**Concern**: Container UID (e.g., 1000) ≠ Remote UID (e.g., 12345)

**Mitigation**:
```bash
# SSHFS with UID mapping
sshfs -o uid=$(id -u) -o gid=$(id -g) \
      -o allow_other \
      user@host:/path /mount
```

### 3. **Network Reliability** ⚠️

**Concern**: Connection loss during file operations

**Mitigation**:
- Auto-reconnect: `sshfs -o reconnect`
- Keepalive: `ServerAliveInterval=15`
- Graceful degradation: Fall back to SSH commands
- User notification: Show connection status in UI

### 4. **Concurrent Access** ⚠️

**Concern**: Multiple users/sessions accessing same remote project

**Mitigation**:
- Per-user mount points: `/tmp/scitex_remote/{user_id}/{project_slug}/`
- Each user gets own SSHFS mount
- No conflict between users

### 5. **Container Restarts** ⚠️

**Concern**: SSHFS mounts don't persist across container restarts

**Mitigation**:
- Auto-remount on first access (lazy loading)
- Database tracks mount state
- User notification: "Remounting remote project..."

### 6. **Disk Space (Local Mount Point)** ⚠️

**Concern**: SSHFS mount metadata uses some local space

**Mitigation**:
- Minimal space: Only metadata cached, not file contents
- Auto-cleanup on unmount
- `/tmp` location (cleared on reboot)

### 7. **Performance Degradation** ⚠️

**Concern**: Network latency makes file operations slow

**Expectation**:
- UI shows "🌐 Remote" badge (sets expectation)
- Warning: "Remote projects are slower due to network latency"
- Recommend local clone for heavy development

---

## Module Integration (Universal Access)

### Remote Projects Work in ALL Modules ✅

**The same mount point is accessible from all SciTeX modules:**

```
Remote Project Mount: /tmp/scitex_remote/{user_id}/{project_slug}/
                               ↓
    ┌──────────────────────┬────────────┬─────────────┬──────────────┐
    ↓                      ↓            ↓             ↓              ↓
📁 Files            📚 Scholar     📊 Vis        ✍️ Writer      💻 Code
/code/              /scholar/      /vis/         /writer/       /code/
workspace           BibTeX mgmt    figures       LaTeX editor   workspace
```

### 1. **Files Tab** (Code Workspace) ✅

**Location**: `/code/` workspace → Files tab

**Access**:
```typescript
// File tree reads from mount point
const files = await fetch(`/api/projects/${username}/${slug}/files/`);
// → Lists files from SSHFS mount
```

**Features**:
- Browse remote files
- Open in Monaco editor
- Save changes to remote
- Delete remote files

### 2. **Scholar Module** ✅

**Location**: `/scholar/`

**Access**:
```python
# Read BibTeX from remote project
project_path = get_project_path(project)  # Returns mount point if remote
bib_file = project_path / "scitex/scholar/references.bib"
content = bib_file.read_text()  # Works via SSHFS
```

**Features**:
- Manage BibTeX files on remote
- Edit entries (saved to remote)
- Import/export

### 3. **Vis Module** ✅

**Location**: `/vis/`

**Access**:
```python
# Read/write figures from remote project
project_path = get_project_path(project)  # Mount point
figures_dir = project_path / "scitex/vis/figures"
for fig in figures_dir.glob("*.png"):
    # Display in gallery
```

**Features**:
- View figures from remote
- Edit figure metadata
- Generate new figures (saved to remote)

### 4. **Writer Module** ✅

**Location**: `/writer/`

**Access**:
```python
# Edit LaTeX on remote project
project_path = get_project_path(project)
tex_file = project_path / "scitex/writer/01_manuscript/main.tex"
content = tex_file.read_text()  # Via SSHFS
```

**Features**:
- Edit LaTeX files remotely
- Compile PDF (fetch from remote)
- Manage bibliography

### 5. **Code Workspace** ✅

**Location**: `/code/` workspace

**Same as Files tab** (already implemented in architecture)

---

## Unified Project Path Resolution

**Key Implementation**: All modules use the same path resolution

```python
# apps/project_app/services/project_manager.py

class ProjectManager:
    """Unified manager for local and remote projects."""

    def get_project_path(self, project) -> Path:
        """
        Get project filesystem path (local or remote mount point).

        Returns:
            Path - Local Gitea path or SSHFS mount point
        """
        if project.project_type == 'local':
            # Return Gitea repository path
            from apps.project_app.services.directory_manager import DirectoryManager
            dir_mgr = DirectoryManager(project.owner)
            return dir_mgr.get_project_path(project)

        elif project.project_type == 'remote':
            # Return SSHFS mount point (auto-mount if needed)
            from apps.project_app.services.remote_project_manager import RemoteProjectManager
            remote_mgr = RemoteProjectManager(project)

            # Ensure mounted
            remote_mgr.ensure_mounted()

            # Return mount point
            return remote_mgr.mount_point

        else:
            raise ValueError(f"Unknown project type: {project.project_type}")
```

**All modules use this**:
```python
# In any module (scholar, vis, writer, code)
from apps.project_app.services.project_manager import ProjectManager

manager = ProjectManager()
project_path = manager.get_project_path(project)

# Now work with files (local or remote - transparent!)
files = list(project_path.rglob("*.tex"))
```

---

## Security Considerations

1. **SSH Key Security**
   - Separate keys for remote access (not reused for Git)
   - 0600 permissions on private keys
   - Key rotation support

2. **Mount Isolation**
   - Per-user mount points: `/tmp/scitex_remote/{user_id}/{project_slug}`
   - Auto-unmount after 30 minutes inactivity
   - No disk caching (privacy)

3. **Access Control**
   - Project permissions apply to remote projects
   - Only project owner/collaborators can access
   - SSH authentication required

4. **Network Security**
   - All traffic over SSH (encrypted)
   - Known_hosts verification
   - Connection timeouts

---

## Future Enhancements

### Phase 5: Advanced Features (Future)

- [ ] **Read-only mode**: Option to mount remote projects as read-only
- [ ] **Bookmark paths**: Save frequently accessed remote directories
- [ ] **Bandwidth optimization**: Compression, caching strategies
- [ ] **Multiple protocols**: Support SFTP, WebDAV, S3, etc.
- [ ] **Collaborative cursors**: Show when others access same remote files
- [ ] **Sync to local**: Option to create local copy of remote project

---

## Conclusion

**Remote Projects** provide a TRAMP-like experience for accessing remote filesystems:

✅ **Privacy**: No local data storage
✅ **Simplicity**: No Git confusion (Git disabled by design)
✅ **Flexibility**: Works with any SSH-accessible system
✅ **Consistency**: Same UI as local projects

**Trade-off**: Slower file operations due to network latency, but acceptable for browsing remote data and editing configuration files.

---

## References

- **Emacs TRAMP**: https://www.gnu.org/software/tramp/
- **SSHFS**: https://github.com/libfuse/sshfs
- **Django Projects**: `apps/project_app/models.py`
- **Existing SSH Gateway**: `apps/workspace_app/SSH_GATEWAY_GUIDE.md`

---

**Next Steps**:
1. Review architecture with stakeholders
2. Create database migrations
3. Implement Phase 1 (core functionality)
4. User testing with real remote systems

<!-- EOF -->
