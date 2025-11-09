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
collect_static_files

# ============================================
# Initialize Visitor Pool
# ============================================
echo_info "Initializing visitor pool..."
python manage.py create_visitor_pool --verbosity 0 2>&1 | grep -v "ERRO\|WARN" || true
echo_success "Visitor pool ready"

# ============================================
# Start Application
# ============================================
echo "🚀 Starting production server..."
exec "$@"

# EOF
