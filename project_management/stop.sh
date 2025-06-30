#!/bin/bash
# SciTeX Cloud Server Stopper - Clean & Simple

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo_info() { echo -e "${CYAN}$1${NC}"; }
echo_success() { echo -e "${GREEN}$1${NC}"; }
echo_error() { echo -e "${RED}$1${NC}"; }

echo_info "🛑 Stopping SciTeX Cloud servers..."

# Stop nginx gracefully first
echo_info "🔸 Reloading nginx (to drop connections)..."
sudo systemctl reload nginx 2>/dev/null || echo_info "  (nginx reload skipped)"

# Kill all uWSGI processes (more comprehensive)
if pgrep -f "uwsgi" > /dev/null; then
    echo_info "🔸 Stopping all uWSGI processes..."
    pkill -f "uwsgi"
    sleep 2
    # Force kill if still running
    pkill -9 -f "uwsgi" 2>/dev/null || true
fi

# Kill Django development servers
if pgrep -f "manage.py runserver" > /dev/null; then
    echo_info "🔸 Stopping Django development servers..."
    pkill -f "manage.py runserver"
    pkill -9 -f "manage.py runserver" 2>/dev/null || true
    sleep 1
fi

# Clean up socket files
echo_info "🔸 Cleaning up socket files..."
rm -f /home/ywatanabe/proj/SciTeX-Cloud/uwsgi.sock
rm -f /home/ywatanabe/proj/SciTeX-Cloud/*.sock
rm -f /tmp/uwsgi*.sock 2>/dev/null || true

# Show remaining processes (for verification)
REMAINING=$(pgrep -f "uwsgi\|manage.py runserver" | wc -l)
if [ "$REMAINING" -eq 0 ]; then
    echo_success "✅ All SciTeX Cloud servers stopped"
else
    echo_error "⚠️  Some processes may still be running: $REMAINING"
    pgrep -f "uwsgi\|manage.py runserver" || true
fi