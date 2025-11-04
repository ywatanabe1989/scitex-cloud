#!/bin/bash
set -e

# ============================================
# Development Environment Entrypoint
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
if [ -d "/scitex-code" ]; then
    # Check if scitex-code is a valid Python project
    if [ -f "/scitex-code/pyproject.toml" ] || [ -f "/scitex-code/setup.py" ]; then
        run_timed "Installing scitex (editable mode)" pip install --user -e /scitex-code
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

# ============================================
# Database & Django Setup
# ============================================
wait_for_database
run_migrations
collect_static_files

# ============================================
# Start Application
# ============================================
echo "🚀 Starting development server..."
exec "$@"

# EOF
