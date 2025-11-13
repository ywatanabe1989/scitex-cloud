#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-05 19:08:34 (ywatanabe)"
# File: ./deployment/docker/docker_dev/entrypoint.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

GIT_ROOT="$(git rev-parse --show-toplevel 2> /dev/null)"

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

set -e

# ============================================
# Development Environment Entry point
# ============================================

# Source common libraries
source /app/deployment/docker/common/lib/logging.src
source /app/deployment/docker/common/lib/database.src
source /app/deployment/docker/common/lib/django.src
source /app/deployment/docker/common/lib/scitex.src

echo "🔧 Development Environment"

# ============================================
# Install SciTeX in Editable Mode (Optional)
# ============================================
try_scitex_installation_in_editable_mode() {
    if [ -d "/scitex-code" ]; then
        # Check if scitex-code is a valid Python project
        if [ -f "/scitex-code/pyproject.toml" ] || [ -f "/scitex-code/setup.py" ]; then
            # Check if scitex is already installed in editable mode from /scitex-code
            if pip show -f scitex 2> /dev/null | grep -q "/scitex-code"; then
                echo -e "${GREEN}✅ Scitex already installed in editable mode${NC}"
            else
                echo_info "Installing scitex (editable mode)..."

                uv pip install -e "/scitex-code[dl,ml,jupyter,neuro,web,scholar,writer,dev]" --link-mode=copy > /dev/null
            fi
            verify_scitex_package
        else
            echo "⚠️  WARNING: /scitex-code exists but is not a valid Python package"
            echo "   (missing pyproject.toml or setup.py at root)"
            echo "   Skipping scitex package installation..."
        fi
    else
        echo "⚠️  WARNING: /scitex-code not mounted!"
        echo "   Skipping scitex package installation..."
    fi
}
try_scitex_installation_in_editable_mode

add_insufficient_python_packages() {
    pip install pygments > /dev/null 2>&1 || true
}
add_insufficient_python_packages

# ============================================
# TypeScript Watch Mode (Hot-Reload)
# ============================================
start_typescript_build_watcher() {
    if [ -d "/app/tsconfig" ] && [ -f "/app/tsconfig/package.json" ]; then
        echo_info "Starting TypeScript watch mode for ALL apps..."
        cd /app/tsconfig || return 0

        # Check if node_modules exists
        if [ ! -d "node_modules" ]; then
            echo_warning "Installing Node dependencies..."
            npm install --silent 2>&1 | grep -v "npm WARN" || true
        fi

        # Start unified TypeScript compiler in watch mode for ALL apps (background)
        nohup npm run build:all:watch \
            > /app/logs/tsc-watch-all.log 2>&1 &
        TSC_ALL_PID=$!
        echo_success "TypeScript watch (ALL apps) started (PID: $TSC_ALL_PID)"
        echo "   Watching: static/ts/**, apps/*/static/*/ts/**"
        echo "   Log: tail -f /app/logs/tsc-watch-all.log"

        cd /app || return 0
    else
        echo_warning "/app/tsconfig not found - skipping TypeScript watch mode"
    fi
}
start_typescript_build_watcher

# ============================================
# Database & Django Setup
# ============================================
wait_for_database
run_migrations
collect_static_files

# ============================================
# Initialize Visitor Pool
# ============================================
initialize_visitor_pool() {
    echo_info "Initializing visitor pool..."
    python manage.py create_visitor_pool --verbosity 0 2>&1 | grep -v "ERRO\|WARN" || true
    echo_success "Visitor pool ready"
}
initialize_visitor_pool

# ============================================
# Start Application
# ============================================
echo "🚀 Starting development server..."
exec "$@"

# EOF
