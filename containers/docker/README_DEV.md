<!-- ---
!-- Timestamp: 2025-10-26 13:22:12
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

# ========================================
# Helper Functions
# ========================================

detect_wsl_environment() {
    if grep -qi microsoft /proc/version 2>/dev/null; then
        export WINDOWS_HOST_IP="$(ip route | grep default | awk '{print $3}')"
        echo_info "WSL detected. Windows host IP: ${WINDOWS_HOST_IP}"
        echo_info "Access from Windows: http://localhost:8000 or http://${WINDOWS_HOST_IP}:8000"
    fi
}

prepare_environment_files() {
    /bin/cp ~/proj/scitex-cloud/SECRET/.env.dev .env
    rm -f /home/ywatanabe/proj/scitex-cloud/.env
    cp .env /home/ywatanabe/proj/scitex-cloud/.env

    # Source .env to make variables available to bash functions
    set -a  # Export all variables
    source .env 2>/dev/null || source .env  # Suppress "command not found" errors from comma-separated values
    set +a  # Stop exporting
    echo_info "Loaded environment from .env"
}

stop_conflicting_services() {
    pkill -f "python.*manage.py runserver" || true
    pkill -f "gunicorn" || true
    echo "$SUDO_PASSWORD" | sudo -S systemctl stop uwsgi_dev 2>/dev/null || true
    echo "$SUDO_PASSWORD" | sudo -S systemctl stop uwsgi_prod 2>/dev/null || true
    echo "$SUDO_PASSWORD" | sudo -S systemctl stop nginx 2>/dev/null || true
    echo "$SUDO_PASSWORD" | sudo -S systemctl stop gitea 2>/dev/null || true

    # Force kill gitea process if systemctl didn't work
    GITEA_PID=$(sudo lsof -ti :${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000} 2>/dev/null)
    if [ ! -z "$GITEA_PID" ]; then
        echo_warning "Found Gitea process (PID $GITEA_PID) still running, killing..."
        echo "$SUDO_PASSWORD" | sudo -S kill -9 $GITEA_PID 2>/dev/null || true
    fi
}

verify_ports_free() {
    # Check port 8000
    for i in {1..3}; do
        if lsof -i :${SCITEX_CLOUD_HTTP_PORT_DEV:-8000} >/dev/null 2>&1; then
            echo_warning "Port ${SCITEX_CLOUD_HTTP_PORT_DEV:-8000} still in use, waiting..."
            sleep 2
        else
            echo_success "Port ${SCITEX_CLOUD_HTTP_PORT_DEV:-8000} is free (HTTP)"
            break
        fi
    done

    # Check port 3001 (Gitea)
    for i in {1..3}; do
        if lsof -i :${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000} >/dev/null 2>&1; then
            echo_warning "Port ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000} still in use, killing..."
            fuser -k ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}/tcp 2>/dev/null || true
            pkill -f gitea || true
            killall gitea 2>/dev/null || true
            GITEA_CONTAINER=$(docker ps | grep "0.0.0.0:${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}" | awk '{print $1}')
            if [ ! -z "$GITEA_CONTAINER" ]; then
                echo_warning "Found Docker container on port ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}, stopping..."
                docker stop $GITEA_CONTAINER || true
            fi
            sleep 2
        else
            echo_success "Port ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000} is free (Gitea)"
            break
        fi
    done
}

cleanup_containers() {
    echo_info "Cleaning up old containers..."
    docker-compose -f docker-compose.dev.yml down
    echo "$SUDO_PASSWORD" | \
        sudo -S docker rm -f docker_db_1 docker_web_1 docker_redis_1 docker_gitea_1 \
        2>/dev/null || true
}

check_database_credentials() {
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
}

rebuild_and_nuclear_cleanup() {
    # Rebuild web image
    echo_info "Rebuilding web image..."
    docker-compose -f docker-compose.dev.yml build web

    # Nuclear cleanup for persistent port issues
    echo_info "Performing comprehensive Docker cleanup..."

    ALL_CONTAINERS=$(docker ps -aq)
    if [ ! -z "$ALL_CONTAINERS" ]; then
        echo_warning "Stopping all Docker containers to free ports..."
        docker stop $ALL_CONTAINERS 2>/dev/null || true
    fi

    docker network prune -f || true
    docker ps -aq --filter "publish=${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}" | xargs -r docker rm -f 2>/dev/null || true
    fuser -k ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}/tcp 2>/dev/null || true
    docker system prune -f || true
    sleep 3

    # Final verification
    if lsof -i :${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000} >/dev/null 2>&1; then
        echo_error "Port ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000} STILL in use!"
        echo_info "Manual: sudo lsof -i :${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}"
        return 1
    fi

    # Check for Docker userland proxy issue (WSL)
    if netstat -tlnp 2>/dev/null | grep ":${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}" | grep -q "docker-proxy"; then
        echo_error "Docker userland proxy stale binding detected"
        echo_warning "Restarting Docker daemon..."
        echo "$SUDO_PASSWORD" | sudo -S systemctl restart docker || true
        sleep 5
    fi

    echo_success "Port ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000} confirmed free"
}

start_all_services() {
    echo_info "Starting all services..."
    docker-compose -f docker-compose.dev.yml up -d
}

wait_for_services_healthy() {
    # Wait for Gitea
    echo_info "Waiting for Gitea to be ready..."
    timeout 60 bash -c 'until docker-compose -f docker-compose.dev.yml ps | grep docker_gitea_1 | grep -q "Up (healthy)"; do sleep 2; done' \
        && echo_success "Gitea is ready!" \
        || echo_warning "Gitea taking longer, continuing anyway..."

    # Wait for Web
    wait_for_web_healthy
}

verify_and_test_endpoints() {
    echo_info "Deployment status:"
    docker-compose -f docker-compose.dev.yml ps

    echo_info "Testing endpoints..."
    curl -I http://localhost:${SCITEX_CLOUD_HTTP_PORT_DEV:-8000}
    curl -I http://localhost:${SCITEX_CLOUD_HTTP_PORT_DEV:-8000}/admin/
    curl -I http://localhost:${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}
}

create_test_users() {
    echo_info "Creating test users..."
    # Passwords from CLAUDE.md: test-user / Test-user!, ywatanabe / Yusuke8939.
    docker-compose -f docker-compose.dev.yml exec -T web python manage.py shell << EOF
import os
from django.contrib.auth import get_user_model
User = get_user_model()

# Test user 1
if not User.objects.filter(username='test-user').exists():
    user = User.objects.create_user(
        username='test-user',
        email='test@example.com',
        password=os.getenv('SCITEX_TEST_USER_PASSWORD', 'Test-user!'),
        is_active=True
    )
    print('✓ Created test-user')
else:
    print('✓ test-user already exists')

# Test user 2
if not User.objects.filter(username='ywatanabe').exists():
    user = User.objects.create_user(
        username='ywatanabe',
        email='ywatanabe@scitex.ai',
        password=os.getenv('SCITEX_YWATANABE_PASSWORD', 'Yusuke8939.'),
        is_active=True
    )
    print('✓ Created ywatanabe')
else:
    print('✓ ywatanabe already exists')
EOF

    echo_success "Test users ready!"
}

wait_for_web_healthy() {
    echo_info "Waiting for web container to be healthy..."
    local START_TIME=$SECONDS
    local TIMEOUT=300

    timeout $TIMEOUT bash -c '
        while ! docker-compose -f docker-compose.dev.yml ps | grep docker_web_1 | grep -q "Up (healthy)"; do
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

# ========================================
# Main Functions
# ========================================

start_dev() {
    # SUDO_PASSWORD="YOUR_PASSWORD"

    cd /home/ywatanabe/proj/scitex-cloud/containers/docker

    # Execute setup steps
    detect_wsl_environment
    prepare_environment_files
    stop_conflicting_services
    verify_ports_free
    cleanup_containers
    check_database_credentials
    rebuild_and_nuclear_cleanup
    start_all_services
    wait_for_services_healthy
    verify_and_test_endpoints
    create_test_users
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
    curl -I http://localhost:${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}
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


**Development environment ready! Access at http://localhost:8000** 🚀

**Production deployment:** `README_PROD.md`
**Docker setup guide:** `DOCKER_SETUP.md`

<!-- EOF -->