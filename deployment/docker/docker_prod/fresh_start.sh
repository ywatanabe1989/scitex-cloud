#!/bin/bash
# -*- coding: utf-8 -*-
# Production Fresh Start Script
# Safely stops old containers, removes them, and starts fresh with new configuration

set -e

SCRIPT_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo_info() { echo -e "${CYAN}INFO: $1${NC}"; }
echo_success() { echo -e "${GREEN}SUCCESS: $1${NC}"; }
echo_warning() { echo -e "${YELLOW}WARNING: $1${NC}"; }
echo_error() { echo -e "${RED}ERROR: $1${NC}"; }
echo_header() { echo -e "\n${CYAN}========================================${NC}"; echo -e "${CYAN}$1${NC}"; echo -e "${CYAN}========================================${NC}"; }

# Confirmation
echo_header "Production Fresh Start (Alpha - No Backup)"
echo_warning "This will:"
echo "  1. Stop all running containers"
echo "  2. Remove old containers (keeping volumes)"
echo "  3. Remove old images"
echo "  4. Build fresh images with all updates"
echo "  5. Start new containers"
echo ""
echo_warning "ALPHA DEPLOYMENT: No database backup will be created"
echo_info "Data volumes preserved: Database, Redis, Gitea repos, SSL certs"
echo ""
read -p "Continue with fresh start? (type 'yes' to confirm): " confirm

if [ "$confirm" != "yes" ]; then
    echo_warning "Aborted by user"
    exit 0
fi

# Step 1: Stop Old Containers
echo_header "Step 1: Stopping old containers"

# Stop docker_prod containers
OLD_CONTAINERS="docker_prod-web-1 docker_prod-db-1 docker_prod-redis-1 docker_prod-gitea-1"
for container in $OLD_CONTAINERS; do
    if docker ps -q -f name=$container 2>/dev/null | grep -q .; then
        echo_info "Stopping $container..."
        docker stop $container
    else
        echo_info "$container not running, skipping"
    fi
done

# Stop old nginx/certbot
if docker ps -q -f name=scitex-cloud-nginx 2>/dev/null | grep -q .; then
    echo_info "Stopping scitex-cloud-nginx..."
    docker stop scitex-cloud-nginx
fi

if docker ps -q -f name=scitex-cloud-certbot 2>/dev/null | grep -q .; then
    echo_info "Stopping scitex-cloud-certbot (old naming)..."
    docker stop scitex-cloud-certbot 2>/dev/null || true
fi

# Stop any docker_prod certbot containers
docker ps -a | grep "docker_prod-certbot" | awk '{print $1}' | xargs -r docker stop 2>/dev/null || true

echo_success "All old containers stopped"

# Step 2: Remove Old Containers
echo_header "Step 2: Removing old containers (keeping volumes)"

# Remove via docker compose (removes scitex-cloud-prod-* containers that were created)
docker compose down --remove-orphans 2>/dev/null || true

# Remove old docker_prod containers
for container in $OLD_CONTAINERS; do
    if docker ps -a -q -f name=$container 2>/dev/null | grep -q .; then
        echo_info "Removing $container..."
        docker rm -f $container 2>/dev/null || true
    fi
done

# Remove old nginx/certbot
docker rm -f scitex-cloud-nginx 2>/dev/null || true
docker ps -a | grep "docker_prod-certbot\|scitex-cloud-certbot" | awk '{print $1}' | xargs -r docker rm -f 2>/dev/null || true

echo_success "Old containers removed"

# Step 3: Remove Old Images
echo_header "Step 3: Removing old images"

docker rmi scitex-cloud-django:latest 2>/dev/null || echo_info "scitex-cloud-django:latest not found"
docker rmi scitex-cloud-prod-django:latest 2>/dev/null || echo_info "scitex-cloud-prod-django:latest not found"

echo_info "Cleaning up dangling images..."
docker image prune -f

echo_success "Old images removed"

# Step 4: Fresh Build
echo_header "Step 4: Building fresh images (this will take several minutes)"

if ! docker compose build --no-cache; then
    echo_error "Build failed! Check the logs above."
    exit 1
fi

echo_success "Fresh images built successfully"

# Step 5: Start New Containers
echo_header "Step 5: Starting new containers"

if ! docker compose up -d; then
    echo_error "Failed to start containers! Check logs with: make logs"
    exit 1
fi

echo_success "New containers started"

# Wait a moment for containers to initialize
echo_info "Waiting for containers to initialize (10 seconds)..."
sleep 10

# Step 6: Verify Deployment
echo_header "Step 6: Verifying deployment"

echo_info "Container status:"
docker compose ps

echo ""
echo_info "Checking container health..."
sleep 5

# Check if Django container is healthy
if docker ps --filter "name=scitex-cloud-prod-django-1" --filter "health=healthy" | grep -q scitex-cloud-prod-django-1; then
    echo_success "Django container is healthy"
else
    echo_warning "Django container not yet healthy (may still be starting)"
    echo_info "Check logs with: make logs-django"
fi

# Check if db container is healthy
if docker ps --filter "name=scitex-cloud-prod-db-1" --filter "health=healthy" | grep -q scitex-cloud-prod-db-1; then
    echo_success "Database container is healthy"
else
    echo_warning "Database container not yet healthy (may still be starting)"
fi

echo_header "Fresh Start Complete!"
echo_success "All steps completed successfully"
echo ""
echo_info "Next steps:"
echo "  1. Check logs: make logs-web"
echo "  2. Verify health: make verify-health"
echo "  3. Test site: curl -I https://scitex.ai"
echo "  4. Test Gitea: curl -I https://git.scitex.ai"
echo "  5. Check users: ./scripts/maintenance/list_users.sh prod"
echo ""
echo_info "Container names (new):"
docker ps --filter "name=scitex-cloud-prod" --format "  - {{.Names}}"
echo ""
echo_success "Fresh start completed! 🚀"
