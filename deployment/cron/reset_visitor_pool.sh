#!/bin/bash
#
# ⚠️ DEPRECATED - DO NOT USE
#
# This script is DEPRECATED as of 2025-11.
# The visitor pool system now uses 60-minute sessions with automatic expiration.
# No cron job is needed - sessions are handled by middleware.
#
# For manual cleanup during testing, use:
#   python manage.py shell
#   >>> from apps.public_app.visitor_pool import VisitorPool
#   >>> VisitorPool.free_expired_allocations()
#
# See deployment/cron/README.md for details.
#

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Load environment
if [ -f "$PROJECT_ROOT/SECRETS/.env.prod" ]; then
    source "$PROJECT_ROOT/SECRETS/.env.prod"
elif [ -f "$PROJECT_ROOT/SECRETS/.env.dev" ]; then
    source "$PROJECT_ROOT/SECRETS/.env.dev"
fi

# Log file
LOG_FILE="$PROJECT_ROOT/logs/visitor_pool_reset.log"
mkdir -p "$(dirname "$LOG_FILE")"

# Timestamp
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting visitor pool reset..." >> "$LOG_FILE"

# Run management command
cd "$PROJECT_ROOT"

# Use docker if running in containers
if [ -f "$PROJECT_ROOT/deployment/docker/docker_dev/docker-compose.yml" ]; then
    docker exec scitex-web python manage.py reset_visitor_pool --free-expired >> "$LOG_FILE" 2>&1
    docker exec scitex-web python manage.py cleanup_demo_projects --hours 24 >> "$LOG_FILE" 2>&1
else
    # Direct python execution
    python manage.py reset_visitor_pool --free-expired >> "$LOG_FILE" 2>&1
    python manage.py cleanup_demo_projects --hours 24 >> "$LOG_FILE" 2>&1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Visitor pool reset complete" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
