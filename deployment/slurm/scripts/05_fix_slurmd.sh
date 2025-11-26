#!/bin/bash
# Fix slurmd startup issues
# File: deployment/slurm/scripts/05_fix_slurmd.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

echo_header "Fixing slurmd startup"

# Get node name from environment or hostname
NODE_NAME="${SLURM_NODE_NAME:-$(hostname -s)}"

# Check logs
echo_info "Recent slurmd logs:"
sudo journalctl -u slurmd -n 20 --no-pager | tail -20

echo ""
echo_info "Checking node registration..."
sudo scontrol show node "${NODE_NAME}" 2>&1 || echo "Node not registered"

echo ""
echo_info "Setting node to IDLE state..."
sudo scontrol update NodeName="${NODE_NAME}" State=IDLE 2>&1 || echo "Failed to update node"

echo ""
echo_info "Restarting slurmd..."
sudo systemctl restart slurmd
sleep 2

echo ""
echo_info "Checking status..."
if sudo systemctl is-active --quiet slurmd; then
    echo_success "slurmd is now running!"
    sinfo
else
    echo_error "slurmd still not running"
    echo_info "Check detailed logs: sudo journalctl -u slurmd -f"
fi

# EOF
