#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-27 04:56:24 (ywatanabe)"
# File: ./containers/docker/start_dev.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

GRAY='\033[0;90m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; }
# ---------------------------------------

REQUIRED_ENV_VARS=(
    "SCITEX_CLOUD_HTTP_PORT_DEV"
    "SCITEX_CLOUD_GITEA_HTTP_PORT_DEV"
    "POSTGRES_USER"
    "POSTGRES_DB"
    "SCITEX_TEST_USER_PASSWORD"
)

SENSITIVE_VARS=(
    "PASSWORD"
    "SECRET"
    "KEY"
    "TOKEN"
)

list_env_dev() {
    cd /home/ywatanabe/proj/scitex-cloud/containers/docker
    source .env 2>/dev/null || true

    echo_info "Environment variables:"
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
            "Access: http://localhost:8000 or " \
            "http://${WINDOWS_HOST_IP}:8000"
    fi
}

prepare_environment_files() {
    /bin/cp ~/proj/scitex-cloud/SECRET/.env.dev .env
    rm -f /home/ywatanabe/proj/scitex-cloud/.env
    cp .env /home/ywatanabe/proj/scitex-cloud/.env
    set -a
    source .env 2>/dev/null || source .env
    set +a
    echo_info "Loaded environment from .env"
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
    docker-compose -f docker-compose.dev.yml down
    docker rm -f \
        docker_db_1 docker_web_1 docker_redis_1 docker_gitea_1 \
        2>/dev/null || true
}


check_database_credentials() {
    if docker ps | grep -q docker_db_1; then
        echo_success "Database already running, skipping check"
        return 0
    fi

    if docker volume inspect docker_postgres_data \
        >/dev/null 2>&1; then
        echo_info \
            "Database volume exists, checking credentials..."
        docker-compose -f docker-compose.dev.yml up -d db
        sleep 3
        if ! docker-compose -f docker-compose.dev.yml exec -T db \
            psql -U "${POSTGRES_USER:-scitex_dev}" \
            -d "${POSTGRES_DB:-scitex_cloud_dev}" \
            -c "SELECT 1" >/dev/null 2>&1; then
            echo_warning \
                "Credentials mismatch. " \
                "Recreating database volume..."
            docker-compose -f docker-compose.dev.yml down -v
        else
            echo_success \
                "Credentials valid, reusing existing database"
            docker-compose -f docker-compose.dev.yml down
        fi
    fi
}


rebuild_and_nuclear_cleanup() {
    if docker images | grep -q "docker_web.*latest"; then
        echo_info "Web image exists, checking if rebuild needed..."
        if [ -f .last_build ] && [ -z "$(find ../../scitex_cloud ../../config -newer .last_build -type f 2>/dev/null)" ]; then
            echo_success "No changes detected, skipping rebuild"
            return 0
        fi
    fi

    echo_info "Rebuilding web image..."
    docker-compose -f docker-compose.dev.yml build web
    touch .last_build

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

start_all_services() {
    echo_info "Starting all services..."
    docker-compose -f docker-compose.dev.yml up -d
}

wait_for_services_healthy() {
    echo_info "Waiting for Gitea to be ready..."
    timeout 60 bash -c \
        'until docker-compose -f docker-compose.dev.yml ps | \
        grep docker_gitea_1 | \
        grep -q "Up (healthy)"; do \
        sleep 2; \
        done' \
        && echo_success "Gitea is ready!" \
        || echo_warning \
        "Gitea taking longer, continuing anyway..."
    wait_for_web_healthy
}

verify_and_test_endpoints() {
    echo_info "Deployment status:"
    docker-compose -f docker-compose.dev.yml ps

    echo_info "Testing endpoints..."
    curl -I \
        http://localhost:${SCITEX_CLOUD_HTTP_PORT_DEV:-8000}
    curl -I \
        http://localhost:${SCITEX_CLOUD_HTTP_PORT_DEV:-8000}/admin/
    curl -I \
        http://localhost:${SCITEX_CLOUD_GITEA_HTTP_PORT_DEV:-3000}
}

create_test_user() {
    echo_info "Creating test users..."
    docker-compose -f docker-compose.dev.yml exec -T web \
        python manage.py shell << EOH
import os
from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='test-user').exists():
    user = User.objects.create_user(
        username='test-user',
        email='test@example.com',
        password=os.getenv(
            'SCITEX_TEST_USER_PASSWORD',
            'Test-user!'
        ),
        is_active=True
    )
    print('✓ Created test-user')
else:
    print('✓ test-user already exists')
EOH

    echo_success "Test users ready!"
}

wait_for_web_healthy() {
    echo_info "Waiting for web container to be healthy..."
    local START_TIME=$SECONDS
    local TIMEOUT=1800

    timeout $TIMEOUT bash -c \
        'while ! docker-compose -f docker-compose.dev.yml ps | \
        grep docker_web_1 | \
        grep -q "Up (healthy)"; do
            LAST_LINES=$(
                docker logs docker_web_1 2>&1 | \
                tail -3 | \
                tr "\n" " "
            )
            ELAPSED=$((SECONDS - START_TIME))
            printf "\033[0;37m  [%3d s] Installing: %s\033[0m\n" \
                "$ELAPSED" "$LAST_LINES"
            sleep 10
        done' || {
        echo_warning "Timeout after ${TIMEOUT}s"
        echo_info \
            "Check logs: " \
            "docker-compose -f docker-compose.dev.yml logs web"
        return 1
    }

    if docker-compose -f docker-compose.dev.yml ps | \
        grep docker_web_1 | \
        grep -q "Up (healthy)"; then
        echo_success \
            "Web container is healthy! " \
            "(took $((SECONDS - START_TIME))s)"
        return 0
    fi
    return 1
}

start_dev() {
    cd /home/ywatanabe/proj/scitex-cloud/containers/docker

    detect_wsl_environment
    prepare_environment_files
    check_database_credentials
    stop_conflicting_services
    verify_ports_free
    cleanup_containers
    rebuild_and_nuclear_cleanup
    start_all_services
    wait_for_services_healthy
    verify_and_test_endpoints
    create_test_user
}

restart_dev() {
    cd /home/ywatanabe/proj/scitex-cloud/containers/docker

    echo_info "Restarting web container..."
    docker-compose -f docker-compose.dev.yml restart web
    wait_for_web_healthy

    echo_info "Deployment status:"
    docker-compose -f docker-compose.dev.yml ps

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