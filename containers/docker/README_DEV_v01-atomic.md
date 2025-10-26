<!-- ---
!-- Timestamp: 2025-10-26 12:37:54
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/containers/docker/README_DEV.md
!-- --- -->

# SciTeX Cloud - Local Development with Docker

**Environment:** Local Development (WSL/Linux)
**Docker:** docker-compose
**Database:** PostgreSQL (port 5433 on host)

---

## Quick Start (Tested & Working)

```bash
BLACK='\033[0;30m'
LIGHT_GRAY='\033[0;37m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${LIGHT_GRAY}INFO: $1${NC}"; }
echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; }

# Helper: Wait for web container to be healthy
wait_for_web_healthy() {
    echo_info "Waiting for web container to be healthy..."
    local START_TIME=$SECONDS
    local TIMEOUT=300  # Increased for playwright install (~3min)

    timeout $TIMEOUT bash -c '
        while ! docker-compose -f docker-compose.dev.yml ps | grep docker_web_1 | grep -q "Up (healthy)"; do
            # Show last 3 lines of pip installation
            LAST_LINES=$(docker logs docker_web_1 2>&1 | tail -3 | tr "\n" " ")
            ELAPSED=$((SECONDS - START_TIME))
            printf "\033[0;37m  [%3d s] Installing: %s\033[0m\n" "$ELAPSED" "$LAST_LINES"
            sleep 10
        done
    ' || {
        echo_warning "Timeout after ${TIMEOUT}s"
        echo_info "Check logs: docker-compose -f docker-compose.dev.yml logs web"
        return 1
    }

    if docker-compose -f docker-compose.dev.yml ps | grep docker_web_1 | grep -q "Up (healthy)"; then
        echo_success "Web container is healthy! (took $((SECONDS - START_TIME))s)"
        return 0
    fi
    return 1
}

start_dev() {
    # SUDO_PASSWORD="YOUR_PASSWORD"

    cd /home/ywatanabe/proj/scitex-cloud/containers/docker

    # 0. Detect WSL/Windows environment
    if grep -qi microsoft /proc/version 2>/dev/null; then
        export WINDOWS_HOST_IP="$(ip route | grep default | awk '{print $3}')"
        echo_info "WSL detected. Windows host IP: ${WINDOWS_HOST_IP}"
        echo_info "Access from Windows: http://localhost:8000 or http://${WINDOWS_HOST_IP}:8000"
    fi

    # 1. Prepare environment files (from gitignored SECRET directory)
    /bin/cp ~/proj/scitex-cloud/SECRET/.env.dev .env
    rm -f /home/ywatanabe/proj/scitex-cloud/.env
    cp .env /home/ywatanabe/proj/scitex-cloud/.env

    # 2. Stop any conflicting services
    pkill -f "python.*manage.py runserver" || true
    pkill -f "gunicorn" || true
    echo "$SUDO_PASSWORD" | \
        sudo -S systemctl stop uwsgi_dev 2>/dev/null || true
    echo "$SUDO_PASSWORD" | \
        sudo -S systemctl stop uwsgi_prod 2>/dev/null || true
    echo "$SUDO_PASSWORD" | \
        sudo -S systemctl stop nginx 2>/dev/null || true
    echo "$SUDO_PASSWORD" | \
        sudo -S systemctl stop gitea 2>/dev/null || true

    # 2.1. Verify ports are free (with retry)
    for i in {1..3}; do
        if lsof -i :${SCITEX_CLOUD_HTTP_PORT_DEV:-8000} >/dev/null 2>&1; then
            echo_warning "Port ${SCITEX_CLOUD_HTTP_PORT_DEV:-8000} still in use, waiting..."
            sleep 2
        else
            echo_success "Port ${SCITEX_CLOUD_HTTP_PORT_DEV:-8000} is free (HTTP)"
            break
        fi
    done

    for i in {1..3}; do
        if lsof -i :${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3001} >/dev/null 2>&1; then
            echo_warning "Port ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3001} still in use, killing..."
            # Try multiple methods to kill
            fuser -k ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3001}/tcp 2>/dev/null || true
            pkill -f gitea || true
            killall gitea 2>/dev/null || true
            # Check for docker containers on this port
            GITEA_CONTAINER=$(docker ps | grep "0.0.0.0:${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3001}" | awk '{print $1}')
            if [ ! -z "$GITEA_CONTAINER" ]; then
                echo_warning "Found Docker container on port ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3001}, stopping it..."
                docker stop $GITEA_CONTAINER || true
            fi
            sleep 2
        else
            echo_success "Port ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3001} is free (Gitea)"
            break
        fi
    done

    # 3. Clean up old containers (preserves database volumes)
    echo_info "Cleaning up old containers..."
    docker-compose -f docker-compose.dev.yml down
    echo "$SUDO_PASSWORD" | \
        sudo -S docker rm -f docker_db_1 docker_web_1 docker_redis_1 docker_gitea_1 \
        2>/dev/null || true

    # 4. Check database credentials compatibility
    if docker volume inspect docker_postgres_data >/dev/null 2>&1; then
        echo_info "Database volume exists, checking credentials..."
        docker-compose -f docker-compose.dev.yml up -d db
        sleep 3
        if ! docker-compose -f docker-compose.dev.yml exec -T db \
            psql -U "${POSTGRES_USER:-scitex_dev}" \
                 -d "${POSTGRES_DB:-scitex_cloud_dev}" \
                 -c "SELECT 1" >/dev/null 2>&1; then
            echo_warning "Credentials mismatch. Recreating database volume..."
            docker-compose -f docker-compose.dev.yml down -v
        else
            echo_success "Credentials valid, reusing existing database"
            docker-compose -f docker-compose.dev.yml down
        fi
    fi

    # 5. Rebuild web image (to include playwright in requirements.txt)
    echo_info "Rebuilding web image..."
    docker-compose -f docker-compose.dev.yml build web

    # 5.1. Nuclear cleanup for port 3001 issue
    echo_info "Performing comprehensive Docker cleanup..."

    # Stop ALL docker containers (nuclear option)
    ALL_CONTAINERS=$(docker ps -aq)
    if [ ! -z "$ALL_CONTAINERS" ]; then
        echo_warning "Stopping all Docker containers to free ports..."
        docker stop $ALL_CONTAINERS 2>/dev/null || true
    fi

    # Clean networks
    docker network prune -f || true

    # Remove any containers on port 3001 specifically
    docker ps -aq --filter "publish=${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3001}" | xargs -r docker rm -f 2>/dev/null || true

    # Force kill host processes on port
    fuser -k ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3001}/tcp 2>/dev/null || true

    # Clean Docker's internal state (fixes userland proxy issues)
    docker system prune -f || true

    # Give everything time to release
    sleep 3

    # 5.2. Verify port is truly free
    if lsof -i :${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3001} >/dev/null 2>&1; then
        echo_error "Port ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3001} STILL in use after cleanup!"
        echo_info "Manual intervention needed. Run: sudo lsof -i :${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3001}"
        return 1
    fi

    # Check if Docker daemon might need restart (WSL issue)
    if netstat -tlnp 2>/dev/null | grep ":${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3001}" | grep -q "docker-proxy"; then
        echo_error "Docker's userland proxy has stale binding on port ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3001}"
        echo_warning "This is a known WSL/Docker issue. Restarting Docker..."
        echo "$SUDO_PASSWORD" | sudo -S systemctl restart docker || true
        sleep 5
    fi

    echo_success "Port ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3001} confirmed free"

    # 5.3. Start all services
    echo_info "Starting all services..."
    docker-compose -f docker-compose.dev.yml up -d

    # 6. Wait for Gitea to be healthy
    echo_info "Waiting for Gitea to be ready..."
    timeout 60 bash -c 'until docker-compose -f docker-compose.dev.yml ps | grep docker_gitea_1 | grep -q "Up (healthy)"; do sleep 2; done' \
        && echo_success "Gitea is ready!" \
        || echo_warning "Gitea taking longer than expected, continuing anyway..."

    # 7. Wait for web container to be healthy
    wait_for_web_healthy

    # 8. Verify deployment
    echo_info "Deployment status:"
    docker-compose -f docker-compose.dev.yml ps

    # 9. Test endpoints
    echo_info "Testing endpoints..."
    curl -I http://localhost:${SCITEX_CLOUD_HTTP_PORT_DEV:-8000}
    curl -I http://localhost:${SCITEX_CLOUD_HTTP_PORT_DEV:-8000}/admin/
    curl -I http://localhost:${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3001}

    # 10. Create test users if they don't exist
    echo_info "Creating test users..."
    docker-compose -f docker-compose.dev.yml exec -T web python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()

# Test user 1: test-user
if not User.objects.filter(username='test-user').exists():
    user = User.objects.create_user(
        username='test-user',
        email='test@example.com',
        password='Test-user!',
        is_active=True
    )
    print('✓ Created test-user (password: Test-user!)')
else:
    print('✓ test-user already exists')

# Test user 2: ywatanabe
if not User.objects.filter(username='ywatanabe').exists():
    user = User.objects.create_user(
        username='ywatanabe',
        email='ywatanabe@scitex.ai',
        password='REDACTED',
        is_active=True
    )
    print('✓ Created ywatanabe (password: REDACTED)')
else:
    print('✓ ywatanabe already exists')
EOF

    echo_success "Test users ready!"
}

restart_dev() {
    cd /home/ywatanabe/proj/scitex-cloud/containers/docker

    echo_info "Restarting web container..."
    docker-compose -f docker-compose.dev.yml restart web

    # Wait for web container to be healthy
    wait_for_web_healthy

    # Show status
    echo_info "Deployment status:"
    docker-compose -f docker-compose.dev.yml ps

    # Test endpoints
    echo_info "Testing endpoints..."
    curl -I http://localhost:${SCITEX_CLOUD_HTTP_PORT_DEV:-8000}
    curl -I http://localhost:${SCITEX_CLOUD_HTTP_PORT_DEV:-8000}/admin/
    curl -I http://localhost:${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3001}
}

start_dev
```

**✅ Development environment ready!**

**Access site:**
- http://localhost:8000
- http://localhost:8000/admin/

---

## What Happens Automatically

The entrypoint script handles:

1. ✅ **Scitex package installation** - Mounts `/scitex-code` and installs editable mode
2. ✅ **Database connection wait** - Waits for PostgreSQL to be ready
3. ✅ **Database migrations** - Runs `python manage.py migrate --noinput`
4. ✅ **Static files** - Collects static files to `/app/staticfiles`
5. ✅ **Application startup** - Starts Gunicorn with auto-reload
6. ✅ **Auto-collectstatic** - Runs every 10 seconds (development only)

**No manual migrations or collectstatic needed!**

---

## Local Development Architecture

```
Host Machine (WSL/Linux)
    ↓ (localhost:8000)
docker_web_1 (Python 3.11 + Gunicorn)
  - Django application
  - Auto-reload enabled
  - Scitex package (editable from /scitex-code)
  - Port 8000 exposed
    ↓
docker_db_1 (postgres:15-alpine)
  - Database: scitex_cloud
  - User: scitex
  - Port 5433 (host) → 5432 (container)

docker_redis_1 (redis:7-alpine)
  - Cache layer
  - Port 6379
```

---

## Service Status

Check with:
```bash
docker-compose ps
```

**Expected output:**
```
NAME                  STATE            PORTS
docker_web_1          Up               0.0.0.0:8000->8000/tcp
docker_db_1           Up               0.0.0.0:5433->5432/tcp
docker_redis_1        Up               0.0.0.0:6379->6379/tcp
```

---

## Management Commands

### View Status
```bash
cd /home/ywatanabe/proj/scitex-cloud/containers/docker

docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Web only (most useful)
docker-compose logs -f web

# Last 100 lines
docker-compose logs --tail=100 web
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart web
docker-compose restart db
```

### Stop Services
```bash
# Stop (keeps data)
docker-compose down

# Stop and remove all data (DANGEROUS!)
docker-compose down -v
```

### Rebuild After Code Changes
```bash
# Rebuild web container
docker-compose build web

# Restart with new build
docker-compose up -d
```

### Database Management
```bash
# Migrations
docker-compose exec web python manage.py migrate

# Create migrations
docker-compose exec web python manage.py makemigrations

# Database shell
docker-compose exec db psql -U scitex -d scitex_cloud

# Database backup
docker-compose exec -T db pg_dump -U scitex -d scitex_cloud > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
cat backup_20251026_120000.sql | docker-compose exec -T db psql -U scitex -d scitex_cloud
```

### Django Management
```bash
# Django shell
docker-compose exec web python manage.py shell

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files (auto-runs, but manual override)
docker-compose exec web python manage.py collectstatic --noinput
```

---

## Troubleshooting

### Port 8000 Already in Use

**Symptom:** `ERROR: for web  Cannot start service web: driver failed programming external connectivity on endpoint docker_web_1... bind: address already in use`

**This is your issue!** Something is already using port 8000.

**Fix:**
```bash
# Find what's using port 8000
lsof -i :8000

# Stop all potential services using port 8000:

# 1. Django runserver
pkill -f "python.*manage.py runserver" || true

# 2. Gunicorn
pkill -f "gunicorn" || true

# 3. uWSGI systemd services
echo "$SUDO_PASSWORD" | sudo -S systemctl stop uwsgi_dev 2>/dev/null || true
echo "$SUDO_PASSWORD" | sudo -S systemctl stop uwsgi_prod 2>/dev/null || true

# 4. Nginx (may be proxying to port 8000)
echo "$SUDO_PASSWORD" | sudo -S systemctl stop nginx 2>/dev/null || true

# 5. Another Docker container
docker ps | grep 8000
# If found, stop it:
# docker stop <container_id>

# 6. Verify port is free
lsof -i :8000 || echo "✓ Port 8000 is free"

# 7. Then restart Docker services
docker-compose up -d
```

### WSL/Windows Port Binding Issues

**Symptom:** Port shows as "free" in WSL but Docker fails with "address already in use"

**Common on WSL + Windows** - Docker's userland proxy has stale state

**Fix Option 1: Restart Docker (recommended)**
```bash
sudo systemctl restart docker
sleep 5
start_dev
```

**Fix Option 2: Check Windows side**
```powershell
# In Windows PowerShell (not WSL):
netstat -ano | findstr :3001
# Then kill the process:
taskkill /PID <process_id> /F
```

**Fix Option 3: Change port**
```bash
# Edit ~/proj/scitex-cloud/SECRET/.env.dev
SCITEX_CLOUD_GITEA_HTTP_PORT_DEV=3002
# Then restart
start_dev
```

**WSL Networking Notes:**
- Services bind to `0.0.0.0` in WSL
- Access from Windows: Use `localhost`, not `127.0.0.1`
- Your WINDOWS_HOST_IP: Check with `ip route | grep default | awk '{print $3}'`
- start_dev() auto-detects WSL and shows Windows access URLs

### Port 5432 Already in Use

**Symptom:** Database connection errors

**Fix:** Already configured to use port 5433 on host
```bash
# Check docker-compose.dev.yml has:
# ports:
#   - "5433:5432"

# If you need to change it, edit docker-compose.dev.yml and restart
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d
```

### Web Container Keeps Restarting

**Check logs:**
```bash
docker-compose logs --tail=100 web
```

**Common causes:**
1. **Database not ready** - Wait 30 seconds after `docker-compose up -d`
2. **Wrong DATABASE_HOST** - Must be `db` not `localhost` in `.env`
3. **Missing environment variables** - Check `.env` file exists

**Fix:**
```bash
# Ensure .env exists
cp .env.dev .env
rm -f /home/ywatanabe/proj/scitex-cloud/.env
cp .env /home/ywatanabe/proj/scitex-cloud/.env

# Recreate containers
docker-compose down
docker-compose up -d --force-recreate
```

### ModuleNotFoundError: scitex

**Symptom:** Web container fails with "No module named 'scitex'"

**Fix:** Already handled by entrypoint script. Check logs:
```bash
docker-compose logs web | grep "Scitex package installed"
```

Should show: "Successfully installed scitex-2.1.0"

If not, check that `/home/ywatanabe/proj/scitex-code` exists and is mounted correctly.

### Database Connection Failed

**Symptom:** `could not connect to server: Connection refused`

**Fix:** Ensure using correct hostname
```bash
# In .env file, must use 'db' not 'localhost'
SCITEX_CLOUD_DB_HOST_DEV=db
SCITEX_CLOUD_DB_PORT_DEV=5432

# Restart containers
docker-compose down
docker-compose up -d
```

### Static Files Not Loading

**Symptom:** CSS/JS not loading in browser

**Fix:** Auto-collectstatic runs every 10 seconds, but you can force it:
```bash
# Manual collect
docker-compose exec web python manage.py collectstatic --noinput

# Check static files exist
docker-compose exec web ls -la /app/staticfiles/

# Restart web container
docker-compose restart web
```

---

## Key Configuration Details

### Environment Variables (.env)

**Critical settings for local development:**
```bash
# Django
DEBUG=True
SECRET_KEY=dev-secret-key-not-for-production
DJANGO_SETTINGS_MODULE=config.settings.settings_dev

# Database (must use 'db' not 'localhost')
SCITEX_CLOUD_DB_HOST_DEV=db
SCITEX_CLOUD_DB_PORT_DEV=5432
SCITEX_CLOUD_DB_NAME_DEV=scitex_cloud
SCITEX_CLOUD_DB_USER_DEV=scitex
SCITEX_CLOUD_DB_PASSWORD_DEV=scitex_dev_password

# Environment
SCITEX_CLOUD_ENV=development
```

### Docker Volumes

| Volume | Purpose | Data |
|--------|---------|------|
| postgres_data | PostgreSQL database | Persistent |
| redis_data | Redis cache | Persistent |
| static_volume | CSS/JS files | Auto-generated |
| media_volume | User uploads | Persistent |
| /scitex-code | Scitex package (editable) | Host mount |

### Ports

| Service | Internal | External | Access |
|---------|----------|----------|--------|
| web | 8000 | 8000 | http://localhost:8000 |
| db | 5432 | 5433 | localhost:5433 (from host) |
| redis | 6379 | 6379 | localhost:6379 |

**Note:** From inside containers, use internal ports. From host machine, use external ports.

---

## Development Workflow

### Typical Development Cycle

```bash
# 1. Start containers (once)
cd /home/ywatanabe/proj/scitex-cloud/containers/docker
docker-compose up -d

# 2. Make code changes in your editor
# Changes to Python code auto-reload (Gunicorn with --reload)
# Changes to templates require browser refresh

# 3. View logs to debug
docker-compose logs -f web

# 4. Run migrations if models changed
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# 5. Test in browser
# http://localhost:8000

# 6. When done, stop containers
docker-compose down
```

### Working with Scitex Package

The scitex package is mounted from `/home/ywatanabe/proj/scitex-code` in editable mode.

**Changes to scitex package:**
```bash
# Edit files in /home/ywatanabe/proj/scitex-code
# Then restart web container to reload
docker-compose restart web
```

---

## Files Reference

```
/home/ywatanabe/proj/scitex-cloud/
├── .env                                    # Django environment (copied from containers/docker/.env)
├── requirements.txt                        # Python dependencies
├── containers/docker/
│   ├── .env                                # Docker Compose environment
│   ├── .env.dev                            # Development template
│   ├── docker-compose.yml                  # Local development services
│   ├── Dockerfile                          # Web container image
│   ├── scripts/
│   │   └── entrypoint.sh                   # Auto-setup script
│   ├── README_LOCAL.md                     # This file
│   └── README_PROD.md                      # Production deployment guide
```

---

## Quick Reference Commands

```bash
# Navigate to docker directory
cd /home/ywatanabe/proj/scitex-cloud/containers/docker

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web

# Restart
docker-compose restart

# Stop
docker-compose down

# Django shell
docker-compose exec web python manage.py shell

# Database shell
docker-compose exec db psql -U scitex -d scitex_cloud

# Rebuild after code changes
docker-compose build web && docker-compose up -d
```

---

**Development environment ready! Access at http://localhost:8000** 🚀

**Production deployment:** `README_PROD.md`
**Docker setup guide:** `DOCKER_SETUP.md`

<!-- EOF -->