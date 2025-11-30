<!-- ---
!-- Timestamp: 2025-11-20 19:59:11
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/docs/DOCKER_DJANGO_DAPHNE_TYPESCRIPT_COMMUNICATION.md
!-- --- -->

# Docker + Django + Daphne + TypeScript Hot Reload System

## Overview

This document describes the development environment hot reload architecture for SciTeX Cloud, which combines Docker, Django, Daphne (ASGI server), django-browser-reload, and TypeScript compilation with automatic browser refresh.

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Docker Container                      │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Django Development Server                 │  │
│  │                                                        │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │   Django runserver (with Daphne integration)     │  │  │
│  │  │   - Command: python manage.py runserver          │  │  │
│  │  │   - ASGI Application: config.asgi:application    │  │  │
│  │  │   - Port: 0.0.0.0:8000                           │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  │                                                        │  │
│  │  ┌──────────────────┐  ┌───────────────────────────┐   │  │
│  │  │  StatReloader    │  │  django-browser-reload    │   │  │
│  │  │  (Django core)   │  │  (Browser refresh)        │   │  │
│  │  │                  │  │                           │   │  │
│  │  │  Watches:        │  │  Watches:                 │   │  │
│  │  │  - Python files  │  │  - Templates (*.html)     │   │  │
│  │  │                  │  │  - CSS files              │   │  │
│  │  │  Action:         │  │  - JS files               │   │  │
│  │  │  Django restart  │  │                           │   │  │
│  │  │                  │  │  Action:                  │   │  │
│  │  │                  │  │  Browser refresh (SSE)    │   │  │
│  │  └──────────────────┘  └───────────────────────────┘   │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │           TypeScript Watch Process (PID: 32)           │  │
│  │                                                        │  │
│  │  Watches: static/ts/**, apps/*/static/*/ts/**          │  │
│  │  Action: .ts → .js compilation                         │  │
│  │  Log: /app/logs/tsc-watch-all.log                      │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                  Volume Mounts                         │  │
│  │                                                        │  │
│  │  Host → Container (Live Sync):                         │  │
│  │  - /home/user/proj/scitex-cloud:/app:cached            │  │
│  │  - /home/user/proj/scitex-code:/scitex-code:cached     │  │
│  │                                                        │  │
│  │  Persistent Volumes:                                   │  │
│  │  - /app/logs (migration sentinel file)                 │  │
│  │  - /app/staticfiles                                    │  │
│  │  - /app/media                                          │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
         │                                    │
         │ HTTP/WebSocket                     │ SSE
         ↓                                    ↓
┌──────────────────────────────────────────────────────────────┐
│                         Browser                              │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  django-browser-reload client (reload-listener.js)     │  │
│  │  - Listens for SSE events from server                  │  │
│  │  - Triggers location.reload() on file change           │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## Hot Reload Flow by File Type

### 1. HTML Template Changes (.html)

**File**: `/app/templates/**/*.html` or `/app/apps/*/templates/**/*.html`

**Flow**:
1. Developer edits template file on host
2. WSL2 → Docker volume sync (subsecond)
3. `django-browser-reload` detects file change via `DJANGO_BROWSER_RELOAD_EXTRA_FILES`
4. Server sends SSE (Server-Sent Event) to connected browsers
5. Browser receives event and executes `location.reload()`
6. **No Django restart**

**Speed**: < 1 second (instant browser refresh)

**Log Signature**:
```
# No special log - just HTTP GET requests for page reload
2025-11-20 08:47:49,416 [INFO] django.channels.server: HTTP GET /vis/vis/ 200
```

### 2. TypeScript Changes (.ts)

**File**: `/app/static/ts/**/*.ts` or `/app/apps/*/static/*/ts/**/*.ts`

**Flow**:
1. Developer edits TypeScript file on host
2. WSL2 → Docker volume sync
3. TypeScript watch process (PID 32) detects change
4. `tsc` compiles `.ts` → `.js`
5. `django-browser-reload` detects compiled `.js` file change
6. Browser refresh via SSE
7. **No Django restart**

**Speed**: 1-2 seconds (compilation + browser refresh)

**Log Signature**:
```
# Check TypeScript watch log
tail -f /app/logs/tsc-watch-all.log
```

### 3. Python Code Changes (.py)

**File**: `/app/**/*.py`, `/scitex-code/src/**/*.py`

**Flow**:
1. Developer edits Python file on host
2. WSL2 → Docker volume sync
3. Django's `StatReloader` detects file modification (via mtime polling)
4. Django triggers autoreload (subprocess restart)
5. **Optimizations kick in**:
   - Migrations skipped (sentinel file: `/app/logs/.migrations_done` exists)
   - Visitor pool skipped (fast-path check: all visitors already exist)
   - Background services skipped (already running)
6. Django process restarts with new code
7. Browser may auto-refresh if watching page

**Speed**: 5-10 seconds (Django restart)

**Log Signature**:
```
2025-11-20 08:44:40,373 [INFO] django.utils.autoreload: Watching for file changes with StatReloader
# ... file change detected ...
Initial Args for manage.py: ['manage.py', 'runserver', '0.0.0.0:8000', 'from_docker']
Performing system checks...
Django version 5.2.7, using settings 'config.settings.settings_dev'
Starting ASGI/Daphne version 4.1.2 development server at http://0.0.0.0:8000/
```

### 4. CSS Changes (.css)

**File**: `/app/static/**/*.css` or `/app/apps/*/static/**/*.css`

**Flow**: Same as HTML templates (browser refresh only, no Django restart)

**Speed**: < 1 second

## Key Components

### Django Settings (settings_dev.py)

```python
# Daphne must be first in INSTALLED_APPS for runserver integration
DEVELOPMENT_APPS = [
    "daphne",  # Must be first for runserver integration
    "django_browser_reload",
    "django_extensions",
]

INSTALLED_APPS = DEVELOPMENT_APPS + INSTALLED_APPS

# ASGI Application
ASGI_APPLICATION = "config.asgi.application"

# Browser reload middleware
MIDDLEWARE += [
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

# Files to watch for browser reload
def _get_extra_watch_files():
    """Dynamically get files to watch for browser reload."""
    import glob
    files = []
    files.extend(glob.glob(str(BASE_DIR / "apps/*/templates/**/*.html"), recursive=True))
    files.extend(glob.glob(str(BASE_DIR / "templates/**/*.html"), recursive=True))
    files.extend(glob.glob(str(BASE_DIR / "static/**/*.css"), recursive=True))
    files.extend(glob.glob(str(BASE_DIR / "apps/*/static/**/*.css"), recursive=True))
    files.extend(glob.glob(str(BASE_DIR / "static/**/*.js"), recursive=True))
    files.extend(glob.glob(str(BASE_DIR / "apps/*/static/**/*.js"), recursive=True))
    return files

DJANGO_BROWSER_RELOAD_EXTRA_FILES = _get_extra_watch_files()
```

### Docker Compose Configuration

```yaml
services:
  web:
    # Use Django's runserver with Daphne integration (see settings_dev.py)
    # Daphne in INSTALLED_APPS makes runserver use ASGI automatically
    # Hot reload works natively with Django's autoreload + django-browser-reload
    # "from_docker" argument bypasses the manage.py wrapper safety check
    command: ["python", "manage.py", "runserver", "0.0.0.0:8000", "from_docker"]

    volumes:
      # Main application code (hot reload with cached mode for performance)
      - ../../..:/app:cached

      # scitex-code package (editable mode)
      - ../../../../scitex-code:/scitex-code:cached

      # Persistent logs (includes migration sentinel file)
      - ../../../logs:/app/logs
```

### Entrypoint Script Optimizations

```bash
MIGRATION_SENTINEL="/app/logs/.migrations_done"

if [ -f "$MIGRATION_SENTINEL" ]; then
    echo "🔄 Hot-Reload Restart (fast path)"
    # Skip migrations on hot-reload
    echo_info "Hot-reload restart detected - skipping migrations"
else
    echo "🔧 Development Environment (first start)"
    # First container start - run full setup
    run_migrations
    # Mark migrations as done (persists in /app/logs volume)
    touch "$MIGRATION_SENTINEL"
fi
```

### Visitor Pool Fast-Path Optimization

```python
# /app/apps/project_app/services/visitor_pool.py

@classmethod
def initialize_pool(cls, pool_size: int = None) -> int:
    """
    Create visitor pool (visitor-001 to visitor-004 by default).
    """
    if pool_size is None:
        pool_size = cls.POOL_SIZE

    # Fast-path: Check if pool is already fully initialized
    # This avoids expensive writer workspace checks on every restart
    all_ready = True
    for i in range(1, pool_size + 1):
        visitor_num = f"{i:03d}"
        username = f"{cls.VISITOR_USER_PREFIX}{visitor_num}"

        # Quick database check
        try:
            user = User.objects.get(username=username)
            project = Project.objects.get(slug="default-project", owner=user)
            # Verify directory exists
            manager = get_project_filesystem_manager(user)
            project_root = manager.get_project_root_path(project)
            if not (project_root and project_root.exists()):
                all_ready = False
                break
        except (User.DoesNotExist, Project.DoesNotExist):
            all_ready = False
            break

    if all_ready:
        logger.info(f"[VisitorPool] Pool already initialized: {pool_size}/{pool_size} ready")
        return 0  # Exit early - no work needed

    # ... rest of initialization for first-time setup
```

## Communication Protocols

### Server-Sent Events (SSE) for Browser Reload

**Endpoint**: Provided by `django-browser-reload` middleware

**Client Code**: `/static/django-browser-reload/reload-listener.js`

```javascript
// Browser establishes SSE connection to Django
const eventSource = new EventSource('/__reload__/events/');

eventSource.onmessage = function(event) {
    // Server detected file change
    if (event.data === 'reload') {
        location.reload();
    }
};
```

**Server Behavior**:
- Middleware watches `DJANGO_BROWSER_RELOAD_EXTRA_FILES`
- On file modification (detected via mtime), sends SSE message
- All connected browsers receive event and reload

### Django StatReloader (Python File Watching)

**Implementation**: Django's `django.utils.autoreload.StatReloader`

**Mechanism**:
- Polls file modification times (mtime) at regular intervals
- Detects changes in:
  - Python modules (`*.py`)
  - Settings files
  - Imported packages (including editable scitex-code)

**Process Restart**:
1. Main process spawns child process with Django app
2. Main process monitors files
3. On change detected:
   - Sends SIGTERM to child process
   - Spawns new child process with updated code
4. Browser reconnects to new process

## Performance Optimizations

### 1. Migration Sentinel File

**Problem**: Migrations ran on every hot reload (17 seconds)

**Solution**:
- First start: Run migrations, create `/app/logs/.migrations_done`
- Hot reload: Skip migrations if sentinel exists
- Persistent volume ensures sentinel survives container restarts

**Impact**: Reduced hot reload from 30+ seconds to 5-10 seconds

### 2. Visitor Pool Fast-Path

**Problem**: Visitor pool initialization checked writer workspaces (20+ seconds)

**Solution**:
- Quick database query to verify all 4 visitors exist
- Directory existence check
- Early return if all ready
- Full initialization only on first start

**Impact**: Reduced visitor pool init from 20 seconds to < 1 second

### 3. Docker Volume Cache Mode

**Configuration**: `:cached` suffix on volume mounts

**Effect**:
- Host writes are batched before syncing to container
- Container reads are cached
- Improves file sync performance on WSL2

### 4. TypeScript Background Watch

**Implementation**: Separate process (PID 32) runs `tsc --watch`

**Benefits**:
- Compilation happens immediately on file save
- No blocking of Django process
- Compiled output triggers browser reload automatically

## Troubleshooting

### Hot Reload Not Working

**Check 1: Volume mounts**
```bash
docker exec scitex-cloud-dev-django-1 ls /app/templates/
# Should show your templates
```

**Check 2: Django autoreload enabled**
```bash
docker logs scitex-cloud-dev-django-1 | grep StatReloader
# Should show: "Watching for file changes with StatReloader"
```

**Check 3: Browser reload client loaded**
```bash
# In browser console, check for:
<script src="/static/django-browser-reload/reload-listener.js"></script>
```

**Check 4: Container using new docker-compose command**
```bash
docker exec scitex-cloud-dev-django-1 ps aux | grep python
# Should show: python manage.py runserver 0.0.0.0:8000 from_docker
```

### Template Changes Not Reflecting

**Issue**: Browser not refreshing on template edit

**Diagnosis**:
```bash
# Check if django-browser-reload is installed
docker exec scitex-cloud-dev-django-1 python -c "import django_browser_reload; print('OK')"

# Verify DJANGO_BROWSER_RELOAD_EXTRA_FILES contains templates
docker exec scitex-cloud-dev-django-1 python -c \
  "from django.conf import settings; \
   print(len([f for f in settings.DJANGO_BROWSER_RELOAD_EXTRA_FILES if 'templates' in f]))"
```

### Slow Django Restart

**Issue**: Python file changes take > 30 seconds to reload

**Check**:
```bash
# Verify migration sentinel exists
docker exec scitex-cloud-dev-django-1 ls -la /app/logs/.migrations_done

# Check visitor pool fast-path
docker logs scitex-cloud-dev-django-1 | grep "visitor pool already initialized"
```

## Migration from Old System

### Before (Custom Wrapper)

**Command**: `python /app/deployment/docker/docker_dev/run_daphne_with_autoreload.py`

**Issues**:
- Custom autoreload logic
- Container restarts instead of process restarts
- Migrations ran every time
- Visitor pool re-initialized every time
- 30+ second reload time

### After (Official Django + Daphne)

**Command**: `python manage.py runserver 0.0.0.0:8000 from_docker`

**Benefits**:
- Official Django runserver with Daphne integration
- Native StatReloader (process restart only)
- Migration sentinel skips redundant migrations
- Visitor pool fast-path optimization
- 5-10 second Python reload, < 1 second template reload

### Key Changes

1. **settings_dev.py**:
   - Added `"daphne"` to `INSTALLED_APPS` (first position)
   - Set `ASGI_APPLICATION = "config.asgi.application"`

2. **docker-compose.yml**:
   - Changed command to `["python", "manage.py", "runserver", "0.0.0.0:8000", "from_docker"]`

3. **entrypoint.sh**:
   - Added migration sentinel file logic

4. **visitor_pool.py**:
   - Added fast-path check at start of `initialize_pool()`

## References

- [Django Daphne Integration](https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/daphne/#integration-with-runserver)
- [django-browser-reload Documentation](https://github.com/adamchainz/django-browser-reload)
- [Django Autoreload](https://docs.djangoproject.com/en/5.2/ref/utils/#module-django.utils.autoreload)
- [Daphne 4.0 Release Notes](https://github.com/django/daphne/blob/main/CHANGELOG.txt)

## Version Information

- Django: 5.2.7
- Daphne: 4.1.2
- django-browser-reload: (installed)
- Python: 3.11.14
- TypeScript: (tsc watch mode)
- Docker: (WSL2 backend)

