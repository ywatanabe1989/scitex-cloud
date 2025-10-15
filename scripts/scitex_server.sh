#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-23 07:50:00 (ywatanabe)"
# File: ./scripts/scitex_server.sh
# ----------------------------------------
# SciTeX Cloud Server Management Script
# Following AIRight's best practices for server management

# Script directory - resolve symlinks to get actual location
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$SCRIPT_DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
PID_DIR="$PROJECT_ROOT/run"

# Create directories if they don't exist
mkdir -p "$LOG_DIR" "$PID_DIR"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
NC='\033[0m' # No Color

# Helper functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Usage information
show_usage() {
    cat << EOF
SciTeX Cloud Server Management

Usage: $0 [COMMAND] [OPTIONS]

COMMANDS:
    start       Start the server (default: development mode)
    stop        Stop all SciTeX Cloud processes
    restart     Restart the server
    status      Show server status
    logs        View server logs
    clean       Clean temporary files and caches
    test        Run tests
    shell       Open Django shell
    migrate     Run database migrations
    static      Collect static files

OPTIONS:
    -m, --mode MODE         Server mode: dev, prod, windows (default: dev)
    -p, --port PORT         Port number (default: 8000)
    -c, --clean             Clean before starting
    -s, --static            Collect static files
    -d, --daemon            Run in daemon mode (production only)
    -w, --workers NUM       Number of workers (production only, default: 4)
    -h, --help              Show this help message

EXAMPLES:
    $0 start                    # Start development server
    $0 start -m prod -d         # Start production server as daemon
    $0 start -m windows         # Start for Windows access
    $0 stop                     # Stop all servers
    $0 logs                     # View logs
    $0 test                     # Run tests

EOF
}

# Default values
MODE="dev"
PORT="8000"
DO_CLEAN=false
DO_STATIC=false
DAEMON=false
WORKERS=4
COMMAND="start"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        start|stop|restart|status|logs|clean|test|shell|migrate|static)
            COMMAND="$1"
            shift
            ;;
        -m|--mode)
            MODE="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -c|--clean)
            DO_CLEAN=true
            shift
            ;;
        -s|--static)
            DO_STATIC=true
            shift
            ;;
        -d|--daemon)
            DAEMON=true
            shift
            ;;
        -w|--workers)
            WORKERS="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Activate virtual environment
activate_venv() {
    # Check if already in a virtual environment
    if [ -n "$VIRTUAL_ENV" ]; then
        log_info "Using active virtual environment: $VIRTUAL_ENV"
        return 0
    fi

    # Try to find and activate virtual environment
    if [ -d "$PROJECT_ROOT/.env" ]; then
        log_info "Activating virtual environment (.env)..."
        source "$PROJECT_ROOT/.env/bin/activate"
    elif [ -d "$PROJECT_ROOT/env" ]; then
        log_info "Activating virtual environment (env)..."
        source "$PROJECT_ROOT/env/bin/activate"
    elif [ -d "$PROJECT_ROOT/.env-3.11" ]; then
        log_info "Activating Python 3.11 environment..."
        source "$PROJECT_ROOT/.env-3.11/bin/activate"
    else
        log_error "No virtual environment found!"
        log_info "Create one with: python3 -m venv .env"
        exit 1
    fi
}

# Stop server function
stop_server() {
    log_info "Stopping SciTeX Cloud processes..."
    
    # Kill Django development server
    pkill -f "python.*manage.py runserver" || true
    
    # Kill Gunicorn
    if [ -f "$PID_DIR/gunicorn.pid" ]; then
        kill $(cat "$PID_DIR/gunicorn.pid") 2>/dev/null || true
        rm -f "$PID_DIR/gunicorn.pid"
    fi
    pkill -f "gunicorn.*config.wsgi" || true
    
    # Kill uWSGI
    if [ -f "$PID_DIR/uwsgi.pid" ]; then
        uwsgi --stop "$PID_DIR/uwsgi.pid" 2>/dev/null || true
        rm -f "$PID_DIR/uwsgi.pid"
    fi
    pkill -f "uwsgi.*config.wsgi" || true
    
    log_success "All processes stopped"
}

# Clean temporary files
clean_temp() {
    log_info "Cleaning temporary files..."
    find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$PROJECT_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true
    find "$PROJECT_ROOT" -type f -name ".DS_Store" -delete 2>/dev/null || true
    rm -rf "$PROJECT_ROOT/staticfiles/*" 2>/dev/null || true
    log_success "Cleanup complete"
}

# Run migrations
run_migrations() {
    log_info "Running database migrations..."
    cd "$PROJECT_ROOT"
    python manage.py makemigrations
    python manage.py migrate
    log_success "Migrations complete"
}

# Collect static files
collect_static() {
    log_info "Collecting static files..."
    cd "$PROJECT_ROOT"
    python manage.py collectstatic --noinput
    log_success "Static files collected"
}

# Start development server
start_dev() {
    export SCITEX_CLOUD_ENV=development
    export SCITEX_DJANGO_SECRET_KEY="${SCITEX_DJANGO_SECRET_KEY:-dev-secret-key-123}"
    
    cd "$PROJECT_ROOT"
    
    if [[ "$MODE" == "windows" ]]; then
        WSL_IP=$(ip -4 addr show eth0 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}' || echo "127.0.0.1")
        log_success "Starting development server for Windows access..."
        log_info ""
        log_info "===================================================="
        log_success "Access from Windows: http://$WSL_IP:$PORT"
        log_info "===================================================="
        log_info ""
    else
        log_success "Starting development server..."
        log_info "Access at: http://localhost:$PORT"
    fi
    
    log_info "Admin panel: http://localhost:$PORT/admin"
    log_info "Hot reload enabled"
    log_info "Press Ctrl+C to stop"
    
    python manage.py runserver 0.0.0.0:$PORT
}

# Start production server
start_prod() {
    export SCITEX_CLOUD_ENV=production
    
    if [ -z "$SCITEX_DJANGO_SECRET_KEY" ]; then
        log_error "SCITEX_DJANGO_SECRET_KEY not set for production!"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
    
    if $DAEMON; then
        log_info "Starting production server as daemon..."
        gunicorn config.wsgi:application \
            --bind 0.0.0.0:$PORT \
            --workers $WORKERS \
            --pid "$PID_DIR/gunicorn.pid" \
            --log-file "$LOG_DIR/gunicorn.log" \
            --access-logfile "$LOG_DIR/gunicorn_access.log" \
            --daemon
        
        log_success "Production server started as daemon on port $PORT"
        log_info "PID file: $PID_DIR/gunicorn.pid"
        log_info "Logs: $LOG_DIR/gunicorn.log"
    else
        log_info "Starting production server..."
        gunicorn config.wsgi:application \
            --bind 0.0.0.0:$PORT \
            --workers $WORKERS \
            --log-file "$LOG_DIR/gunicorn.log" \
            --access-logfile "$LOG_DIR/gunicorn_access.log"
    fi
}

# Show server status
show_status() {
    log_info "SciTeX Cloud Server Status"
    echo "============================"
    
    # Check Django dev server
    if pgrep -f "python.*manage.py runserver" > /dev/null; then
        log_success "Django development server: RUNNING"
        ps aux | grep "python.*manage.py runserver" | grep -v grep
    else
        log_warning "Django development server: NOT RUNNING"
    fi
    
    echo ""
    
    # Check Gunicorn
    if [ -f "$PID_DIR/gunicorn.pid" ] && kill -0 $(cat "$PID_DIR/gunicorn.pid") 2>/dev/null; then
        log_success "Gunicorn: RUNNING (PID: $(cat $PID_DIR/gunicorn.pid))"
    elif pgrep -f "gunicorn.*config.wsgi" > /dev/null; then
        log_success "Gunicorn: RUNNING"
        ps aux | grep "gunicorn.*config.wsgi" | grep -v grep
    else
        log_warning "Gunicorn: NOT RUNNING"
    fi
    
    echo ""
    
    # Check uWSGI
    if [ -f "$PID_DIR/uwsgi.pid" ] && kill -0 $(cat "$PID_DIR/uwsgi.pid") 2>/dev/null; then
        log_success "uWSGI: RUNNING (PID: $(cat $PID_DIR/uwsgi.pid))"
    elif pgrep -f "uwsgi.*config.wsgi" > /dev/null; then
        log_success "uWSGI: RUNNING"
        ps aux | grep "uwsgi.*config.wsgi" | grep -v grep
    else
        log_warning "uWSGI: NOT RUNNING"
    fi
}

# View logs
view_logs() {
    log_info "Viewing SciTeX Cloud logs..."
    
    # Use multitail if available
    if command -v multitail &> /dev/null; then
        multitail -f "$LOG_DIR/django.log" \
                  -f "$LOG_DIR/app.log" \
                  -f "$LOG_DIR/gunicorn.log" 2>/dev/null || \
        tail -f "$LOG_DIR"/*.log
    else
        # Fall back to regular tail
        tail -f "$LOG_DIR"/*.log
    fi
}

# Main command execution
case $COMMAND in
    start)
        activate_venv
        
        # Clean if requested
        if $DO_CLEAN; then
            clean_temp
        fi
        
        # Run migrations
        run_migrations
        
        # Collect static if requested or in production
        if $DO_STATIC || [[ "$MODE" == "prod" ]]; then
            collect_static
        fi
        
        # Stop any running servers
        stop_server
        
        # Start appropriate server
        case $MODE in
            dev|windows)
                start_dev
                ;;
            prod)
                start_prod
                ;;
            *)
                log_error "Unknown mode: $MODE"
                exit 1
                ;;
        esac
        ;;
        
    stop)
        stop_server
        ;;
        
    restart)
        stop_server
        sleep 2
        $0 start -m "$MODE" -p "$PORT"
        ;;
        
    status)
        show_status
        ;;
        
    logs)
        view_logs
        ;;
        
    clean)
        clean_temp
        ;;
        
    test)
        activate_venv
        cd "$PROJECT_ROOT"
        log_info "Running tests..."
        python manage.py test
        ;;
        
    shell)
        activate_venv
        cd "$PROJECT_ROOT"
        log_info "Opening Django shell..."
        python manage.py shell
        ;;
        
    migrate)
        activate_venv
        run_migrations
        ;;
        
    static)
        activate_venv
        collect_static
        ;;
        
    *)
        log_error "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac

# EOF