#!/bin/bash
set -e

# ============================================
# Production/NAS Environment Entrypoint
# ============================================

# Source common libraries
source /app/deployment/docker/common/lib/logging.src
source /app/deployment/docker/common/lib/database.src
source /app/deployment/docker/common/lib/django.src
source /app/deployment/docker/common/lib/scitex.src

echo "🏭 Production Environment"

# ============================================
# Verify SciTeX from PyPI
# ============================================
verify_scitex_package

# Ensure we're NOT using editable install
if [ -d "/scitex-code" ]; then
    echo "⚠️  WARNING: /scitex-code detected in production!"
    echo "   This should not be mounted in prod/nas environments."
    echo "   Using PyPI version anyway..."
fi

# ============================================
# Database & Django Setup
# ============================================
wait_for_database
run_migrations

# ============================================
# TypeScript Build
# ============================================
build_typescript() {
    if [ -d "/app/tsconfig" ] && [ -f "/app/tsconfig/package.json" ]; then
        echo_info "Building TypeScript for production..."
        cd /app/tsconfig || return 0

        # Install dependencies if needed
        if [ ! -d "node_modules" ]; then
            echo_info "Installing Node dependencies..."
            if ! npm install --silent 2>&1 | grep -v "npm WARN"; then
                echo_warning "npm install failed - TypeScript build skipped"
                cd /app || return 0
                return 0
            fi
        fi

        # Build all TypeScript files
        if npm run build:all > /dev/null 2>&1; then
            echo_success "TypeScript compiled successfully"
        else
            echo_warning "TypeScript build failed - continuing anyway"
        fi

        cd /app || return 0
    else
        echo_warning "/app/tsconfig not found - skipping TypeScript build"
    fi
}
build_typescript || echo_warning "TypeScript build skipped due to errors"

collect_static_files

# ============================================
# Initialize Visitor Pool
# ============================================
echo_info "Initializing visitor pool..."
python manage.py create_visitor_pool --verbosity 0 2>&1 | grep -v "ERRO\|WARN" || true
echo_success "Visitor pool ready (1-hour sessions with auto-expiration)"

# ============================================
# Start Application
# ============================================
echo "🚀 Starting production server..."
exec "$@"

# EOF
