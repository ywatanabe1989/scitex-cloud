#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-22 09:24:39 (ywatanabe)"
# File: ./deployment/server/start.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

BLACK='\033[0;30m'
LIGHT_GRAY='\033[0;37m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${LIGHT_GRAY}$1${NC}"; }
echo_success() { echo -e "${GREEN}$1${NC}"; }
echo_warning() { echo -e "${YELLOW}$1${NC}"; }
echo_error() { echo -e "${RED}$1${NC}"; }
# ---------------------------------------

echo_header() { echo_info "==== $1 ==="; }

# SciTeX-Cloud Start Script
# Based on best practices from airight project

APP_HOME="/home/ywatanabe/proj/scitex-cloud"
PYTHON_ENV="$APP_HOME/.venv"
PYTHON_BIN="$APP_HOME/.venv/bin/python"
MANAGE_PY="$PYTHON_BIN manage.py"
LOG_DIR="$APP_HOME/logs"
PID_FILE="$APP_HOME/run/scitex.pid"

# Create necessary directories
mkdir -p "$LOG_DIR" "$APP_HOME/run"

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -m, --migrate          Run database migrations"
    echo "  -c, --collect-static   Collect static files"
    echo "  -p, --production       Start in production mode"
    echo "  -d, --daemon           Run in background (daemon mode)"
    echo "  -h, --help             Show this help message"
    echo
    echo "Description:"
    echo "  This script manages Django project tasks and server startup."
    echo "  Without options, it starts the development server."
    echo
    echo "Examples:"
    echo "  $0                     # Start development server"
    echo "  $0 -m -c               # Migrate, collect static, start dev server"
    echo "  $0 -p                  # Start production server with uwsgi"
    echo "  $0 -d                  # Start dev server in background"
    exit 1
}

# Ensure proper file permissions
ensure_permissions() {
    echo_header "Ensure permissions..."
    chmod 755 "$APP_HOME/scripts"/*.sh 2>/dev/null || true
    chmod 755 "$APP_HOME/manage.py" 2>/dev/null || true
    echo "Done"
}

# Run database migrations
migrate() {
    echo_header "Running database migrations..."
    $MANAGE_PY makemigrations
    $MANAGE_PY migrate
    echo "Done"
}

# Collect static files
collect_static() {
    echo_header "Collecting static files..."
    $MANAGE_PY collectstatic --noinput
    echo "Done"
}

# Stop any existing servers
stop_existing() {
    echo_header "Stopped existing processes..."

    # Kill all Django runserver processes (with and without sudo)
    pkill -9 -f "runserver" 2>/dev/null || true
    sudo pkill -9 -f "runserver" 2>/dev/null || true

    # Kill all Python processes running manage.py
    pkill -9 -f "python.*manage.py" 2>/dev/null || true
    sudo pkill -9 -f "python.*manage.py" 2>/dev/null || true

    # Kill processes using port 8000
    sudo fuser -k -9 8000/tcp 2>/dev/null || true
    fuser -k -9 8000/tcp 2>/dev/null || true

    # Kill any processes listening on port 8000 using lsof
    if command -v lsof &> /dev/null; then
        lsof -ti:8000 | xargs -r kill -9 2>/dev/null || true
        sudo lsof -ti:8000 | xargs -r sudo kill -9 2>/dev/null || true
    fi

    # Kill existing uwsgi processes
    pkill -9 -f "uwsgi.*scitex" 2>/dev/null || true
    sudo pkill -9 -f "uwsgi.*scitex" 2>/dev/null || true

    # Remove PID file
    rm -f "$PID_FILE"

    # Remove uwsgi socket
    rm -f "$APP_HOME/run/uwsgi.sock"

    # Wait a moment for processes to fully terminate
    sleep 1

    echo "Done"
}

# Start development server
start_dev() {
    echo_header "Starting SciTeX-Cloud development server..."

    if [[ "$1" == "daemon" ]]; then
        nohup $MANAGE_PY runserver 127.0.0.1:8000 > "$LOG_DIR/django.log" 2>&1 &
        echo $! > "$PID_FILE"
        echo_info "    Development server started in background (PID: $(cat $PID_FILE))"
        echo_info "    Logs: tail -f $LOG_DIR/django.log"
    else
        echo_info "    Starting at http://localhost:8000"
        echo_info "    Press Ctrl+C to stop"
        $MANAGE_PY runserver 0.0.0.0:8000
    fi

    echo "Done"
}

# Start production server with uwsgi
start_prod() {
    echo_header "Starting SciTeX-Cloud production server..."

    # Ensure nginx is configured
    if ! nginx -t 2>/dev/null; then
        echo_warn "    Nginx configuration not found or invalid"
        echo_warn "    Please configure nginx before running in production"
    fi

    # Start uwsgi
    "$APP_HOME/env/bin/uwsgi" --ini "$APP_HOME/config/uwsgi.ini" \
        --daemonize "$LOG_DIR/uwsgi.log" \
        --pidfile "$PID_FILE"

    echo_info "    Production server started with uwsgi"
    echo_info "    Logs: tail -f $LOG_DIR/uwsgi.log"
}

# Main function
main() {
    local do_migrate=false
    local do_collect_static=false
    local is_prod=false
    local is_daemon=false

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -m|--migrate) do_migrate=true ;;
            -c|--collect-static) do_collect_static=true ;;
            -p|--production) is_prod=true ;;
            -d|--daemon) is_daemon=true ;;
            -h|--help) usage ;;
            *) echo "Unknown option: $1"; usage ;;
        esac
        shift
    done

    rm $LOG_DIR/*.log -f

    # In production, always migrate and collect static
    if $is_prod; then
        do_migrate=true
        do_collect_static=true
    fi

    # Activate virtual environment
    source "$PYTHON_ENV/bin/activate"

    # Ensure permissions
    ensure_permissions

    # Stop existing processes
    stop_existing

    # Run migrations if requested
    if $do_migrate; then
        migrate
    fi

    # Collect static files if requested
    if $do_collect_static; then
        collect_static
    fi

    # Start appropriate server
    if $is_prod; then
        start_prod
    else
        if $is_daemon; then
            start_dev "daemon"
        else
            start_dev
        fi
    fi
}

# Run main function with all arguments
main "$@"

tail -f $LOG_DIR/*.log

# EOF