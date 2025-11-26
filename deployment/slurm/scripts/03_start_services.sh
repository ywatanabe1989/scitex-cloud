#!/bin/bash
# SLURM Installation Step 3: Start SLURM Services
# File: deployment/slurm/scripts/03_start_services.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

echo_header "Step 3: Starting SLURM services"

# Check if configuration exists
if [ ! -f /etc/slurm/slurm.conf ]; then
    echo_error "SLURM configuration not found!"
    echo_info "Run: deployment/slurm/scripts/02_configure_slurm.sh"
    exit 1
fi

# Enable services
echo_info "Enabling SLURM services..."
sudo systemctl enable slurmctld
sudo systemctl enable slurmd

# Restart services (use restart to handle already-running case)
echo_info "Starting slurmctld (controller)..."
sudo systemctl restart slurmctld

echo_info "Starting slurmd (compute daemon)..."
sudo systemctl restart slurmd

# Wait for services to start
echo_info "Waiting for services to initialize..."
sleep 3

# Check service status
echo_info "Checking service status..."
if sudo systemctl is-active --quiet slurmctld; then
    echo_success "slurmctld is running"
else
    echo_error "slurmctld failed to start"
    echo_info "Check logs: sudo journalctl -u slurmctld -n 20"
    exit 1
fi

if sudo systemctl is-active --quiet slurmd; then
    echo_success "slurmd is running"
else
    echo_error "slurmd failed to start"
    echo_info "Check logs: sudo journalctl -u slurmd -n 20"
    exit 1
fi

echo_success "Step 3 complete: SLURM services started"

# EOF
