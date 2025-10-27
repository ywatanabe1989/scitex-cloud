#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-27 16:22:07 (ywatanabe)"
# File: ./start_dev.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

GRAY='\033[0;90m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; }
echo_header() { echo_info "=== $1 ==="; }
# ---------------------------------------

verify_env_setup() {
    echo_header "Verifying .env setup..."

    # Check if SECRET/.env.dev exists
    if [ ! -f "$GIT_ROOT"/SECRET/.env.dev ]; then
        echo_error "SECRET/.env.dev not found!"
        return 1
    fi
    echo_success "SECRET/.env.dev exists"

    # Verify symlinks are correct
    if [ ! -L "$GIT_ROOT"/.env ]; then
        echo_error ".env is not a symlink!"
        return 1
    fi
    echo_info ".env is a symlink"

    if [ ! -L "$GIT_ROOT"/containers/docker/.env ]; then
        echo_error "containers/docker/.env is not a symlink!"
        return 1
    fi
    echo_info "containers/docker/.env is a symlink"

    # Verify symlinks point to correct target
    local root_target=$(readlink "$GIT_ROOT"/.env)
    local docker_target=$(readlink "$GIT_ROOT"/containers/docker/.env)

    if [ "$root_target" != "SECRET/.env.dev" ]; then
        echo_error ".env symlink points to wrong target: $root_target"
        return 1
    fi
    echo_info ".env -> SECRET/.env.dev"

    if [ "$docker_target" != "../../SECRET/.env.dev" ]; then
        echo_error "containers/docker/.env symlink points to wrong target: $docker_target"
        return 1
    fi
    echo_info "containers/docker/.env -> ../../SECRET/.env.dev"

    # Verify critical environment variables
    source "$GIT_ROOT"/containers/docker/.env 2>/dev/null

    local critical_vars=(
        "SCITEX_CLOUD_GITEA_URL_DEV"
        "SCITEX_CLOUD_DB_HOST_DEV"
        "POSTGRES_DB"
        "POSTGRES_USER"
    )

    for var_name in "${critical_vars[@]}"; do
        if [ -z "${!var_name}" ]; then
            echo_error "Critical variable $var_name is not set!"
            return 1
        fi
    done
    echo_success "All critical variables are set"

    # Verify Gitea URL uses Docker networking
    if [[ "$SCITEX_CLOUD_GITEA_URL_DEV" == *"127.0.0.1"* ]]; then
        echo_error "SCITEX_CLOUD_GITEA_URL_DEV uses 127.0.0.1 (should use 'gitea' for Docker networking)"
        echo_info "Current value: $SCITEX_CLOUD_GITEA_URL_DEV"
        echo_info "Expected: http://gitea:3000"
        return 1
    fi
    echo_success "Gitea URL uses Docker networking: $SCITEX_CLOUD_GITEA_URL_DEV"

    return 0
}

prepare_environment_files() {
    echo_header "Preparing developmental environmental variables..."

    # Create symlinks to SECRET/.env.dev (single source of truth)
    # This ensures we always use the latest values without copying

    if [ ! -L "$GIT_ROOT"/.env ]; then
        rm -f "$GIT_ROOT"/.env
        ln -s SECRET/.env.dev "$GIT_ROOT"/.env
        echo_info "Created symlink: .env -> SECRET/.env.dev"
    fi

    if [ ! -L "$GIT_ROOT"/containers/docker/.env ]; then
        rm -f "$GIT_ROOT"/containers/docker/.env
        ln -s ../../SECRET/.env.dev "$GIT_ROOT"/containers/docker/.env
        echo_info "Created symlink: containers/docker/.env -> ../../SECRET/.env.dev"
    fi

    set -a
    source "$GIT_ROOT"/containers/docker/.env 2>/dev/null
    set +a
    echo_success "Loaded environment from SECRET/.env.dev (single source of truth via symlinks)"

    # Verify setup
    if ! verify_env_setup; then
        echo_error ".env verification failed! Please check your configuration."
        return 1
    fi
}

list_env_dev() {
    echo_header "Environment variables:"

    prepare_environment_files
    cd "$GIT_ROOT"/containers/docker
    source .env 2>/dev/null || true

    REQUIRED_ENV_VARS=(
        "SCITEX_CLOUD_ENV"
        "SCITEX_CLOUD_HTTP_PORT_DEV"
        "SCITEX_CLOUD_GITEA_HTTP_PORT_DEV"
        "POSTGRES_USER"
        "POSTGRES_DB"
        "SCITEX_CLOUD_TEST_USER_PASSWORD"
    )

    SENSITIVE_VARS=(
        "PASSWORD"
        "SECRET"
        "KEY"
        "TOKEN"
    )

    for var_name in "${REQUIRED_ENV_VARS[@]}"; do
        var_value="${!var_name}"
        is_sensitive=false
        for sensitive_pattern in "${SENSITIVE_VARS[@]}"; do
            if [[ "$var_name" == *"$sensitive_pattern"* ]]; then
                is_sensitive=true
                break
            fi
        done

        if $is_sensitive; then
            echo "  ${var_name}=***"
        else
            echo "  ${var_name}=${var_value:-[not set]}"
        fi
    done
}

detect_wsl_environment() {
    if grep -qi microsoft /proc/version 2>/dev/null; then
        export WINDOWS_HOST_IP="$(
            ip route | grep default | awk '{print $3}'
        )"
        echo_info "WSL detected. Windows host IP: ${WINDOWS_HOST_IP}"
        echo_info \
            "Access either of:\n    http://localhost:8000\n    http://127.0.0.1:8000\n    http://${WINDOWS_HOST_IP}:8000"
    fi
}

check_docker_setup() {
    echo_header "Checking Docker setup..."

    local all_good=true

    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo_error "Docker not installed. Run: sudo apt install -y docker.io"
        all_good=false
    elif docker --version &>/dev/null; then
        echo_success "Docker installed: $(docker --version)"
    fi

    # Check Docker Compose
    if ! docker compose version &>/dev/null; then
        echo_error "Docker Compose not installed. Run: sudo apt install -y docker-compose-plugin"
        all_good=false
    else
        echo_success "Docker Compose installed"
    fi

    # Check Docker daemon
    if ! docker ps &>/dev/null; then
        echo_error "Docker daemon not running. Run: sudo systemctl start docker"
        all_good=false
    else
        echo_success "Docker daemon is running"
    fi

    # Check BuildKit/Buildx
    if ! docker buildx version &>/dev/null; then
        echo_warning "Docker Buildx not installed (optional but recommended for faster builds)"
        echo_info "Install: mkdir -p ~/.docker/cli-plugins && curl -L https://github.com/docker/buildx/releases/download/v0.13.0/buildx-v0.13.0.linux-amd64 -o ~/.docker/cli-plugins/docker-buildx && chmod +x ~/.docker/cli-plugins/docker-buildx"
    else
        echo_success "Docker Buildx installed: $(docker buildx version | head -1)"
    fi

    if [ "$all_good" = false ]; then
        echo_error "Please fix the Docker setup issues above"
        return 1
    fi

    return 0
}

stop_conflicting_services() {
    pkill -f "python.*manage.py runserver" || true
    pkill -f "gunicorn" || true
    sudo systemctl stop uwsgi_dev 2>/dev/null || true
    sudo systemctl stop uwsgi_prod 2>/dev/null || true
    sudo systemctl stop nginx 2>/dev/null || true
    sudo systemctl stop gitea 2>/dev/null || true
    GITEA_PID=$(
        sudo lsof -ti :${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000} \
        2>/dev/null
    )
    if [ ! -z "$GITEA_PID" ]; then
        echo_warning \
            "Found Gitea process (PID $GITEA_PID), killing..."
        sudo kill -9 $GITEA_PID 2>/dev/null || true
    fi
}

verify_ports_free() {
    for ii in {1..3}; do
        if lsof -i :${SCITEX_CLOUD_HTTP_PORT_DEV:-8000} \
            >/dev/null 2>&1; then
            echo_warning \
                "Port ${SCITEX_CLOUD_HTTP_PORT_DEV:-8000} " \
                "still in use, waiting..."
            sleep 2
        else
            echo_success \
                "Port ${SCITEX_CLOUD_HTTP_PORT_DEV:-8000} " \
                "is free (HTTP)"
            break
        fi
    done

    for ii in {1..3}; do
        if lsof -i :${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000} \
            >/dev/null 2>&1; then
            echo_warning \
                "Port ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000} " \
                "still in use, killing..."
            fuser -k \
                ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}/tcp \
                2>/dev/null || true
            pkill -f gitea || true
            killall gitea 2>/dev/null || true
            GITEA_CONTAINER=$(
                docker ps | \
                grep \
                "0.0.0.0:${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}" | \
                awk '{print $1}'
            )
            if [ ! -z "$GITEA_CONTAINER" ]; then
                echo_warning \
                    "Found Docker container on port " \
                    "${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}, " \
                    "stopping..."
                docker stop $GITEA_CONTAINER || true
            fi
            sleep 2
        else
            echo_success \
                "Port ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000} " \
                "is free (Gitea)"
            break
        fi
    done
}

cleanup_containers() {
    echo_info "Cleaning up old containers..."
    docker compose -f docker-compose.dev.yml down
    docker rm -f \
        docker-db-1 docker-web-1 docker-redis-1 docker-gitea-1 \
        2>/dev/null || true
}


check_database_credentials() {
    if docker ps | grep -q docker-db-1; then
        echo_success "Database already running, skipping check"
        return 0
    fi

    if docker volume inspect docker_postgres_data \
        >/dev/null 2>&1; then
        echo_info \
            "Database volume exists, checking credentials..."
        docker compose -f docker-compose.dev.yml up -d db
        sleep 3
        if ! docker compose -f docker-compose.dev.yml exec -T db \
            psql -U "${POSTGRES_USER:-scitex_dev}" \
            -d "${POSTGRES_DB:-scitex_cloud_dev}" \
            -c "SELECT 1" >/dev/null 2>&1; then
            echo_warning \
                "Credentials mismatch. " \
                "Recreating database volume..."
            docker compose -f docker-compose.dev.yml down -v
        else
            echo_success \
                "Credentials valid, reusing existing database"
            docker compose -f docker-compose.dev.yml down
        fi
    fi
}

rebuild_and_nuclear_cleanup() {
    echo_info "Rebuilding web image..."
    DOCKER_BUILDKIT=1 docker compose -f docker-compose.dev.yml build web

    echo_info "Performing comprehensive Docker cleanup..."
    ALL_CONTAINERS=$(docker ps -aq)
    if [ ! -z "$ALL_CONTAINERS" ]; then
        echo_warning \
            "Stopping all Docker containers to free ports..."
        docker stop $ALL_CONTAINERS 2>/dev/null || true
    fi

    docker network prune -f || true
    docker ps -aq \
        --filter \
        "publish=${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}" | \
        xargs -r docker rm -f 2>/dev/null || true
    fuser -k \
        ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}/tcp \
        2>/dev/null || true
    docker system prune -f || true
    sleep 3

    if lsof -i :${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000} \
        >/dev/null 2>&1; then
        echo_error \
            "Port ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000} " \
            "STILL in use!"
        echo_info \
            "Manual: " \
            "sudo lsof -i :" \
            "${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}"
        return 1
    fi

    if netstat -tlnp 2>/dev/null | \
        grep ":${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}" | \
        grep -q "docker-proxy"; then
        echo_error \
            "Docker userland proxy stale binding detected"
        echo_warning "Restarting Docker daemon..."
        sudo systemctl restart docker || true
        sleep 5
    fi

    echo_success \
        "Port ${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000} " \
        "confirmed free"
}

cleanup_corrupted_containers() {
    echo_header "Cleaning up any corrupted containers..."

    # Remove any containers in a bad state (exited status)
    local bad_containers=$(docker ps -a --filter "status=exited" --format "{{.Names}}" | grep "^docker_")

    if [ -n "$bad_containers" ]; then
        echo_warning "Found corrupted containers, removing: $bad_containers"
        echo "$bad_containers" | xargs -r docker rm -f
        echo_success "Corrupted containers removed"
    fi

    # Also check for containers that docker compose can't manage
    if docker compose -f docker-compose.dev.yml ps 2>&1 | grep -q "ContainerConfig"; then
        echo_warning "Docker Compose state corrupted, forcing cleanup"
        docker compose -f docker-compose.dev.yml down --remove-orphans 2>/dev/null || true
        echo_success "Forced cleanup complete"
    fi
}

start_all_services() {
    cleanup_corrupted_containers
    echo_info "Starting all services..."
    docker compose -f docker-compose.dev.yml up -d
}

wait_for_services_healthy() {
    echo_header "Waiting for Gitea to be ready..."
    timeout 60 bash -c \
        'until docker compose -f docker-compose.dev.yml ps | \
        grep docker-gitea-1 | \
        grep -q "(healthy)"; do \
        sleep 2; \
        done' \
        && echo_success "Gitea is ready!" \
        || echo_warning \
        "Gitea taking longer, continuing anyway..."
    wait_for_web_healthy
}

verify_and_test_endpoints() {
    echo_header "Deployment status:"

    docker compose -f docker-compose.dev.yml ps

    echo_info "Testing endpoints..."
    curl -I \
        http://localhost:${SCITEX_CLOUD_HTTP_PORT_DEV:-8000}
    curl -I \
        http://localhost:${SCITEX_CLOUD_HTTP_PORT_DEV:-8000}/admin/
    curl -I \
        http://localhost:${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}

    echo ""
    echo_success "Access Information:"
    echo_success "Django:  http://localhost:${SCITEX_CLOUD_HTTP_PORT_DEV:-8000}"
    echo_success "Gitea:   http://localhost:${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}"
    echo ""
    echo_success "Gitea Admin Login:"
    echo_success "  Username: ${SCITEX_CLOUD_GITEA_ADMIN_USERNAME:-scitex_admin}"
    echo_success "  Password: ${SCITEX_CLOUD_GITEA_ADMIN_PASSWORD:-scitex_admin_2025}"
}

setup_gitea_token() {
    echo_header "Setting up Gitea API token..."

    # Use localhost for host machine access
    local GITEA_API_URL="http://127.0.0.1:${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}"

    # Check if token already exists in .env (single source of truth)
    if [ -n "$SCITEX_CLOUD_GITEA_TOKEN_DEV" ]; then
        echo_info "Token found in .env"

        # Verify token still works
        if curl -s -f -H "Authorization: token $SCITEX_CLOUD_GITEA_TOKEN_DEV" \
            "${GITEA_API_URL}/api/v1/user" >/dev/null 2>&1; then
            echo_success "Existing token is valid"
            return 0
        else
            echo_warning "Existing token in .env is invalid, generating new one..."
        fi
    fi

    # Generate new token
    echo_info "Generating new Gitea admin token..."

    # Get admin credentials from environment
    local ADMIN_USERNAME="${SCITEX_CLOUD_GITEA_ADMIN_USERNAME:-scitex_admin}"
    local ADMIN_PASSWORD="${SCITEX_CLOUD_GITEA_ADMIN_PASSWORD:-scitex_admin_2025}"
    local ADMIN_EMAIL="${SCITEX_CLOUD_GITEA_ADMIN_EMAIL:-admin@scitex.local}"

    # Check if admin user exists, create if not
    if ! docker exec -u git docker-gitea-1 gitea admin user list 2>/dev/null | grep -q "$ADMIN_USERNAME"; then
        echo_info "Creating Gitea admin user: $ADMIN_USERNAME"
        docker exec -u git docker-gitea-1 gitea admin user create \
            --username "$ADMIN_USERNAME" \
            --password "$ADMIN_PASSWORD" \
            --email "$ADMIN_EMAIL" \
            --admin \
            --must-change-password=false 2>/dev/null || true
        echo_success "Admin user created:\n    Username: $ADMIN_USERNAME\n    Password: $ADMIN_PASSWORD"
    fi

    # Generate token for admin user
    local NEW_TOKEN=$(docker exec -u git docker-gitea-1 gitea admin user generate-access-token \
        --username "$ADMIN_USERNAME" \
        --token-name "scitex-dev-$(date +%Y%m%d)" \
        --scopes "write:repository,write:user,write:admin" \
        2>/dev/null | grep -oE '[a-f0-9]{40}' | head -1)

    if [ -n "$NEW_TOKEN" ]; then
        # Update .env (single source of truth)
        mkdir -p "$GIT_ROOT/SECRET"
        if grep -q "SCITEX_CLOUD_GITEA_TOKEN_DEV=" "$GIT_ROOT/SECRET/.env.dev"; then
            sed -i "s|SCITEX_CLOUD_GITEA_TOKEN_DEV=.*|SCITEX_CLOUD_GITEA_TOKEN_DEV=$NEW_TOKEN|" "$GIT_ROOT/SECRET/.env.dev"
        else
            echo "SCITEX_CLOUD_GITEA_TOKEN_DEV=$NEW_TOKEN" >> "$GIT_ROOT/SECRET/.env.dev"
        fi
        echo_success "Token saved to SECRET/.env.dev"

        # Reload environment
        source "$GIT_ROOT/SECRET/.env.dev"
        return 0
    else
        echo_error "Failed to generate Gitea token"
        return 1
    fi
}

verify_gitea_api() {
    echo_header "Verifying Gitea API..."

    # Use localhost for host machine access
    local GITEA_URL="${SCITEX_CLOUD_GITEA_URL_IN_HOST_DEV:-http://127.0.0.1:3000}"
    GITEA_TOKEN="${SCITEX_CLOUD_GITEA_TOKEN_DEV}"

    # Test Gitea API version
    if curl -f -s "${GITEA_URL}/api/v1/version" >/dev/null 2>&1; then
        echo_success "Gitea API is accessible"
    else
        echo_error "Gitea API is not accessible at ${GITEA_URL}"
        return 1
    fi

    # Test authentication
    AUTH_RESPONSE=$(curl -s -H "Authorization: token ${GITEA_TOKEN}" \
        "${GITEA_URL}/api/v1/user" 2>/dev/null)

    if echo "$AUTH_RESPONSE" | grep -q '"login"'; then
        GITEA_USER=$(echo "$AUTH_RESPONSE" | grep -o '"login":"[^"]*"' | cut -d'"' -f4)
        echo_success "Authenticated to Gitea as: $GITEA_USER"
    else
        echo_error "Failed to authenticate to Gitea"
        echo_info "Check SCITEX_CLOUD_GITEA_TOKEN_DEV in .env"
        return 1
    fi

    return 0
}

recreate_test_user() {
    echo_header "Recreating test user to test Django-to-Gitea pipeline..."

    local USERNAME="test-user"
    local EMAIL="test@example.com"
    local PASSWORD="${SCITEX_CLOUD_TEST_USER_PASSWORD:-Test-user!}"
    local GITEA_URL="${SCITEX_CLOUD_GITEA_URL_IN_HOST_DEV:-http://127.0.0.1:3000}"
    local GITEA_TOKEN="${SCITEX_CLOUD_GITEA_TOKEN_DEV}"

    # Step 1: Delete from Django (will trigger signal to delete from Gitea)
    echo_info "Deleting test user from Django..."
    docker compose -f docker-compose.dev.yml exec -T web \
        python manage.py shell << EOH
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    user = User.objects.get(username='${USERNAME}')
    user.delete()
    print('✓ Deleted ${USERNAME} from Django')
except User.DoesNotExist:
    print('✓ User does not exist in Django')
EOH

    # Step 2: Verify deletion from Gitea (check via API)
    echo_info "Verifying deletion from Gitea..."
    sleep 2  # Give signal time to propagate

    GITEA_CHECK=$(curl -s -H "Authorization: token ${GITEA_TOKEN}" \
        "${GITEA_URL}/api/v1/users/${USERNAME}" 2>/dev/null)

    if echo "$GITEA_CHECK" | grep -q '"message"'; then
        echo_success "✓ User deleted from Gitea"
    else
        echo_warning "User may still exist in Gitea, continuing anyway..."
    fi

    # Step 3: Create user via Django (will trigger signal to create in Gitea)
    echo_info "Creating test user via Django User.objects.create_user()..."
    docker compose -f docker-compose.dev.yml exec -T web \
        python manage.py shell << EOH
import os
from django.contrib.auth import get_user_model

User = get_user_model()

user = User.objects.create_user(
    username='${USERNAME}',
    email='${EMAIL}',
    password='${PASSWORD}',
    is_active=True
)
print('✓ Created ${USERNAME} via Django')
print(f'  - Username: {user.username}')
print(f'  - Email: {user.email}')
print(f'  - Active: {user.is_active}')
EOH

    # Step 4: Wait for signal to propagate
    echo_info "Waiting for Django signal to create Gitea user..."
    sleep 3

    # Step 5: Verify user exists in both Django and Gitea
    echo ""
    verify_test_user
}

verify_test_user() {
    echo_header "Verifying test user in Django and Gitea..."

    local USERNAME="test-user"
    local EMAIL="test@example.com"
    local GITEA_URL="${SCITEX_CLOUD_GITEA_URL_IN_HOST_DEV:-http://127.0.0.1:3000}"
    local GITEA_TOKEN="${SCITEX_CLOUD_GITEA_TOKEN_DEV}"

    local django_ok=false
    local gitea_ok=false

    # Check Django
    echo_info "Checking Django..."
    local django_check=$(docker compose -f docker-compose.dev.yml exec -T web \
        python manage.py shell << EOH
import json
from django.contrib.auth import get_user_model

User = get_user_model()
try:
    user = User.objects.get(username='${USERNAME}')
    print(json.dumps({
        'exists': True,
        'username': user.username,
        'email': user.email,
        'is_active': user.is_active
    }))
except User.DoesNotExist:
    print(json.dumps({'exists': False}))
EOH
)

    if echo "$django_check" | grep -q '"exists": true'; then
        echo_success "✓ Django user exists: $USERNAME"
        local django_email=$(echo "$django_check" | grep -o '"email": "[^"]*"' | cut -d'"' -f4)
        echo_info "  Email: $django_email"
        django_ok=true
    else
        echo_error "✗ Django user not found: $USERNAME"
    fi

    # Check Gitea
    echo_info "Checking Gitea..."
    if [ -n "$GITEA_TOKEN" ]; then
        local gitea_check=$(curl -s -H "Authorization: token ${GITEA_TOKEN}" \
            "${GITEA_URL}/api/v1/users/${USERNAME}" 2>/dev/null)

        if echo "$gitea_check" | grep -q '"login"'; then
            echo_success "✓ Gitea user exists: $USERNAME"
            local gitea_email=$(echo "$gitea_check" | grep -o '"email":"[^"]*"' | cut -d'"' -f4)
            echo_info "  Email: $gitea_email"
            gitea_ok=true
        else
            echo_error "✗ Gitea user not found: $USERNAME"
        fi
    else
        echo_warning "Gitea token not set, skipping Gitea check"
    fi

    # Summary
    echo ""
    if $django_ok && $gitea_ok; then
        echo_success "Test user verified in both Django and Gitea!"
        return 0
    elif $django_ok; then
        echo_warning "Test user exists in Django but not in Gitea"
        return 1
    elif $gitea_ok; then
        echo_warning "Test user exists in Gitea but not in Django"
        return 1
    else
        echo_error "Test user not found in Django or Gitea"
        return 1
    fi
}

wait_for_web_healthy() {
    echo_header "Waiting for web container to be healthy..."
    local START_TIME=$SECONDS
    local TIMEOUT=1800

    while [ $((SECONDS - START_TIME)) -lt $TIMEOUT ]; do
        # Check if container is healthy (matches "Up ... (healthy)" format)
        if docker compose -f docker-compose.dev.yml ps | \
            grep docker-web-1 | \
            grep -q "(healthy)"; then
            echo ""
            echo_success \
                "Web container is healthy! " \
                "(took $((SECONDS - START_TIME))s)"
            return 0
        fi

        # Show progress (overwrite same line with \r)
        LAST_LINES=$(
            docker logs docker-web-1 2>&1 | \
            grep -E "Downloading|Installing|packages|Starting|Watching" | \
            tail -1 | \
            cut -c1-80
        )

        # If no relevant log line, show generic message
        if [ -z "$LAST_LINES" ]; then
            LAST_LINES="Starting up..."
        fi

        ELAPSED=$((SECONDS - START_TIME))
        printf "\033[0;37m  [%3d s] %s%-80s\033[0m\r" \
            "$ELAPSED" "" "$LAST_LINES"
        sleep 10
    done

    # Timeout reached
    echo ""
    echo_warning "Timeout after ${TIMEOUT}s"
    echo_info "Check logs: docker compose -f docker-compose.dev.yml logs web"
    return 1
}

start_dev() {
    cd "$GIT_ROOT"/containers/docker

    # Prerequisites
    detect_wsl_environment
    check_docker_setup || exit 1

    # Environment
    prepare_environment_files
    check_database_credentials

    # Stop existing services
    stop_conflicting_services
    verify_ports_free

    # Rebuild containers
    cleanup_containers
    rebuild_and_nuclear_cleanup

    # Start services
    start_all_services
    wait_for_services_healthy

    # Verification
    verify_and_test_endpoints

    # Gitea
    setup_gitea_token
    verify_gitea_api

    # Necessary setup
    recreate_test_user
}

restart_dev() {
    echo_header "Restarting web container..."

    cd "$GIT_ROOT"/containers/docker

    # Ensure all dependencies are running before restarting web
    echo_info "Checking dependencies..."

    # Check if Gitea is running
    if ! docker compose -f docker-compose.dev.yml ps | grep docker-gitea-1 | grep -q "Up"; then
        echo_warning "Gitea not running, starting all services..."
        docker compose -f docker-compose.dev.yml up -d
        wait_for_services_healthy
    else
        # Just restart web if all dependencies are up
        docker compose -f docker-compose.dev.yml restart web
        wait_for_web_healthy
    fi

    echo_info "Deployment status:"
    docker compose -f docker-compose.dev.yml ps

    echo_info "Testing endpoints..."
    curl -I \
        http://localhost:${SCITEX_CLOUD_HTTP_PORT_DEV:-8000}
    curl -I \
        http://localhost:${SCITEX_CLOUD_HTTP_PORT_DEV:-8000}/admin/
    curl -I \
        http://localhost:${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}
}


usage() {
    echo "Usage: $0 [-a|--action <start|restart|list_env>] [-l|--list-env] [-h|--help]"
    echo
    echo "Actions:"
    echo "  start      Full setup from scratch with cleanup and rebuild"
    echo "  restart    Quick restart of web container only"
    echo "  list_env   Display environment variables"
    echo
    echo "Options:"
    echo "  -a, --action     Action to perform: start, restart, or list_env"
    echo "                   (default: restart)"
    echo "  -l, --list-env   Shortcut for list_env action"
    echo "  -h, --help       Display this help message"
    echo
    echo "Example:"
    echo "  $0 -a start"
    echo "  $0 --action restart"
    echo "  $0 -l"
    exit 1
}

main() {
    sudo -v
    if [ $? -ne 0 ]; then
        echo_error "Sudo privileges required. Aborted."
        exit 1
    fi

    if ! groups | grep -q docker; then
        echo_error "User not in docker group."
        echo_info "Run setup commands:"
        echo_info "  sudo usermod -aG docker \$USER"
        echo_info "  newgrp docker"
        exit 1
    fi

    ACTION="restart"

    while [[ $# -gt 0 ]]; do
        case $1 in
            -a|--action)
                ACTION="$2"
                shift 2
                ;;
            -l|--list-env)
                ACTION="list_env"
                shift
                ;;
            -h|--help)
                usage
                ;;
            *)
                echo "Unknown option: $1"
                usage
                ;;
        esac
    done

    case $ACTION in
        start)
            start_dev
            ;;
        restart)
            restart_dev
            ;;
        list_env)
            list_env_dev
            ;;
        *)
            echo "Invalid action: $ACTION"
            usage
            ;;
    esac

}

main "$@" 2>&1 | tee "$LOG_PATH"

# EOF