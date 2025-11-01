# Centralized Logging System

## Overview
All logs are centralized in `./logs/` directory at the project root for easy access and debugging.

---

## Log Locations

### Primary Logs (Always in ./logs/)
```
./logs/
├── start.sh.log          # Main startup script
├── docker-compose.log    # Docker Compose operations
├── web.log              # Django application logs
├── db.log               # PostgreSQL logs
├── gitea.log            # Gitea logs
├── redis.log            # Redis logs
└── build.log            # Docker build output
```

### Symlinks (Point to ./logs/)
Scripts create local symlinks for convenience:
- `deployment/docker/docker_dev/.start.sh.log` → `../../../logs/start.sh.log`
- Container logs in `./logs/` are also accessible via `docker compose logs`

---

## How It Works

### 1. Startup Script (start.sh)
```bash
# Centralized log
LOG_PATH="$GIT_ROOT/logs/start.sh.log"
LOCAL_LOG="$THIS_DIR/.start.sh.log"

# Symlink: local → centralized
ln -sf "$LOG_PATH" "$LOCAL_LOG"

# All output goes to centralized log
{ main "$@" } 2>&1 | tee -a "$LOG_PATH"
```

### 2. Docker Containers
Container logs write to host `./logs/` via volume mount:
```yaml
volumes:
  - ../../../logs:/app/logs
```

Django/application logs:
```python
# In Django settings
LOGGING = {
    'handlers': {
        'file': {
            'filename': '/app/logs/web.log',
        }
    }
}
```

### 3. Docker Compose Logs
Save compose operations:
```bash
docker compose up 2>&1 | tee -a logs/docker-compose.log
docker compose build 2>&1 | tee -a logs/build.log
```

---

## Usage

### View All Logs
```bash
# Real-time monitoring
tail -f logs/*.log

# View specific log
tail -f logs/start.sh.log
tail -f logs/web.log
```

### View Container Logs
```bash
cd deployment/docker/docker_dev

# All containers
docker compose logs -f

# Specific service
docker compose logs -f web
docker compose logs -f db
```

### Clean Logs
```bash
# Clear all logs
rm -f logs/*.log

# Or in Makefile
make clean-logs
```

---

## Benefits

✅ **Single Location**: All logs in one place (`./logs/`)
✅ **Easy Debugging**: No hunting for log files
✅ **Symlinks**: Scripts can still reference "local" logs
✅ **Persistent**: Logs survive container restarts
✅ **Centralized**: Easy to grep/search across all logs
✅ **Version Control**: `logs/` directory gitignored

---

## Integration with .gitignore

Ensure `logs/` is ignored:
```gitignore
# Logs
logs/
*.log
```

---

## Example: Finding Errors

```bash
# Search all logs for errors
grep -r "ERROR\|Error\|error" logs/

# Find build failures
grep -A 10 "failed" logs/build.log

# Check Django errors
grep "Traceback" logs/web.log
```

---

*All logs centralized for systematic debugging*
