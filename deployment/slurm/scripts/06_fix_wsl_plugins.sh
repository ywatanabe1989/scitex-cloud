#!/bin/bash
# Fix SLURM plugins for WSL compatibility
# File: deployment/slurm/scripts/06_fix_wsl_plugins.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

echo_header "Fixing SLURM plugins for WSL"

echo_info "Updating /etc/slurm/slurm.conf..."
sudo sed -i 's/ProctrackType=proctrack\/cgroup/ProctrackType=proctrack\/linuxproc/' /etc/slurm/slurm.conf
sudo sed -i 's/TaskPlugin=task\/cgroup/TaskPlugin=task\/none/' /etc/slurm/slurm.conf

echo_info "Verifying changes..."
grep -E "ProctrackType|TaskPlugin" /etc/slurm/slurm.conf

echo ""
echo_info "Restarting SLURM services..."
sudo systemctl restart slurmctld
sudo systemctl restart slurmd

echo ""
echo_info "Waiting for services..."
sleep 3

echo ""
echo_info "Setting node to IDLE..."
sudo scontrol update NodeName=$(hostname -s) State=IDLE

echo ""
echo_info "Testing SLURM..."
sinfo

echo ""
echo_success "SLURM plugins fixed! Testing job execution..."
srun echo "Hello from SLURM!"

# EOF
