#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-22 04:47:00 (ywatanabe)"
# File: ./scripts/deploy_prod.sh

# SciTeX Cloud Production Deployment Script
# Based on best practices from airight project

set -e  # Exit on any error

APP_HOME="/home/ywatanabe/proj/SciTeX-Cloud"
LOG_DIR="/var/log/scitex-cloud"
RUN_DIR="/var/run/scitex-cloud"
PYTHON_BIN="$APP_HOME/env/bin/python"
MANAGE_PY="$PYTHON_BIN $APP_HOME/manage.py"

# ANSI colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
echo_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
echo_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $1"; }

usage() {
    echo "SciTeX Cloud Production Deployment"
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -d, --deploy       Full deployment (migrate, static, start)"
    echo "  -m, --migrate      Run database migrations only"
    echo "  -s, --static       Collect static files only"
    echo "  -r, --restart      Restart services only"
    echo "  -c, --check        Check system configuration"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -d              # Full deployment"
    echo "  $0 -m -s           # Migrate and collect static"
    echo "  $0 -r              # Restart services"
    exit 1
}

check_dependencies() {
    echo_info "Checking dependencies..."
    
    # Check if virtual environment exists
    if [ ! -d "$APP_HOME/env" ]; then
        echo_error "Virtual environment not found at $APP_HOME/env"
        exit 1
    fi
    
    # Check if Python executable exists
    if [ ! -f "$PYTHON_BIN" ]; then
        echo_error "Python executable not found at $PYTHON_BIN"
        exit 1
    fi
    
    # Check if manage.py exists
    if [ ! -f "$APP_HOME/manage.py" ]; then
        echo_error "Django manage.py not found at $APP_HOME/manage.py"
        exit 1
    fi
    
    echo_success "Dependencies check passed"
}

create_directories() {
    echo_info "Creating required directories..."
    
    # Create log directory
    sudo mkdir -p "$LOG_DIR" || echo_warning "Could not create $LOG_DIR"
    sudo chown -R www-data:www-data "$LOG_DIR" 2>/dev/null || echo_warning "Could not set ownership for $LOG_DIR"
    
    # Create run directory for PID files and sockets
    sudo mkdir -p "$RUN_DIR" || echo_warning "Could not create $RUN_DIR"
    sudo chown -R www-data:www-data "$RUN_DIR" 2>/dev/null || echo_warning "Could not set ownership for $RUN_DIR"
    
    echo_success "Directories created"
}

run_migrations() {
    echo_info "Running database migrations..."
    
    cd "$APP_HOME"
    source env/bin/activate
    
    # Set production environment
    export DJANGO_SETTINGS_MODULE=config.settings.production
    
    echo_info "Making migrations..."
    $MANAGE_PY makemigrations
    
    echo_info "Applying migrations..."
    $MANAGE_PY migrate
    
    echo_success "Database migrations completed"
}

collect_static() {
    echo_info "Collecting static files..."
    
    cd "$APP_HOME"
    source env/bin/activate
    
    # Set production environment
    export DJANGO_SETTINGS_MODULE=config.settings.production
    
    # Remove old static files
    if [ -d "$APP_HOME/staticfiles" ]; then
        echo_info "Backing up old static files..."
        mv "$APP_HOME/staticfiles" "$APP_HOME/staticfiles_backup_$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
    fi
    
    # Collect new static files
    $MANAGE_PY collectstatic --noinput --clear
    
    echo_success "Static files collected"
}

stop_services() {
    echo_info "Stopping services..."
    
    # Stop uWSGI processes
    sudo pkill -f uwsgi 2>/dev/null || echo_warning "No uWSGI processes to stop"
    
    # Stop Gunicorn processes
    sudo pkill -f gunicorn 2>/dev/null || echo_warning "No Gunicorn processes to stop"
    
    # Remove socket files
    sudo rm -f "$RUN_DIR/uwsgi.sock" 2>/dev/null || true
    sudo rm -f "$RUN_DIR/gunicorn.sock" 2>/dev/null || true
    
    echo_success "Services stopped"
}

start_services() {
    echo_info "Starting services..."
    
    cd "$APP_HOME"
    source env/bin/activate
    
    # Set production environment
    export DJANGO_SETTINGS_MODULE=config.settings.production
    
    # Start uWSGI
    echo_info "Starting uWSGI..."
    "$APP_HOME/env/bin/uwsgi" --ini "$APP_HOME/config/uwsgi.ini" --daemonize "$LOG_DIR/uwsgi.log"
    
    # Wait a moment for uWSGI to start
    sleep 2
    
    # Check if uWSGI is running
    if pgrep -f uwsgi > /dev/null; then
        echo_success "uWSGI started successfully"
    else
        echo_error "Failed to start uWSGI"
        exit 1
    fi
    
    # Restart Nginx
    echo_info "Restarting Nginx..."
    sudo systemctl restart nginx 2>/dev/null || echo_warning "Could not restart Nginx"
    
    echo_success "Services started"
}

run_checks() {
    echo_info "Running system checks..."
    
    cd "$APP_HOME"
    source env/bin/activate
    
    # Set production environment
    export DJANGO_SETTINGS_MODULE=config.settings.production
    
    # Run Django system checks
    echo_info "Running Django system checks..."
    $MANAGE_PY check --deploy
    
    # Test database connection
    echo_info "Testing database connection..."
    $MANAGE_PY shell -c "from django.db import connection; connection.ensure_connection(); print('Database connection: OK')"
    
    echo_success "System checks passed"
}

# Parse command line arguments
DO_MIGRATE=false
DO_STATIC=false
DO_RESTART=false
DO_DEPLOY=false
DO_CHECK=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--deploy)
            DO_DEPLOY=true
            DO_MIGRATE=true
            DO_STATIC=true
            DO_RESTART=true
            shift
            ;;
        -m|--migrate)
            DO_MIGRATE=true
            shift
            ;;
        -s|--static)
            DO_STATIC=true
            shift
            ;;
        -r|--restart)
            DO_RESTART=true
            shift
            ;;
        -c|--check)
            DO_CHECK=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo_error "Unknown option: $1"
            usage
            ;;
    esac
done

# If no options provided, show usage
if [ "$DO_MIGRATE" = false ] && [ "$DO_STATIC" = false ] && [ "$DO_RESTART" = false ] && [ "$DO_DEPLOY" = false ] && [ "$DO_CHECK" = false ]; then
    usage
fi

# Main execution
echo_info "Starting SciTeX Cloud production deployment..."

check_dependencies
create_directories

if [ "$DO_CHECK" = true ]; then
    run_checks
fi

if [ "$DO_MIGRATE" = true ]; then
    run_migrations
fi

if [ "$DO_STATIC" = true ]; then
    collect_static
fi

if [ "$DO_RESTART" = true ]; then
    stop_services
    start_services
fi

echo_success "Deployment completed successfully!"

if [ "$DO_DEPLOY" = true ]; then
    echo_info "=== Deployment Summary ==="
    echo_info "- Database migrations: Applied"
    echo_info "- Static files: Collected"
    echo_info "- Services: Restarted"
    echo_info "- Logs: $LOG_DIR"
    echo_info "=========================="
fi

# EOF