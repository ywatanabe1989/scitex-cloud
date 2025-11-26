#!/bin/bash
# SLURM Installation Step 1: Setup MUNGE Authentication
# File: deployment/slurm/scripts/01_setup_munge.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

echo_header "Step 1: Setting up MUNGE authentication"

# Check if MUNGE is installed
if ! command -v munge &> /dev/null; then
    echo_error "MUNGE is not installed. Please install it first:"
    echo_info "sudo apt-get install -y munge"
    exit 1
fi

echo_success "MUNGE is installed"

# Check if MUNGE already works
echo_info "Checking MUNGE status..."
if systemctl is-active --quiet munge && munge -n | unmunge &>/dev/null; then
    echo_success "MUNGE is already configured and working!"
    munge -n | unmunge
else
    echo_info "Configuring MUNGE..."

    # Stop service if running
    sudo systemctl stop munge 2>/dev/null || true

    # Generate key
    echo_info "Generating MUNGE key..."
    if command -v create-munge-key &> /dev/null; then
        sudo create-munge-key -f
    else
        echo_info "Using dd method..."
        sudo dd if=/dev/urandom bs=1 count=1024 of=/tmp/munge.key 2>/dev/null
        sudo mv /tmp/munge.key /etc/munge/munge.key
        sudo chown munge: /etc/munge/munge.key
        sudo chmod 400 /etc/munge/munge.key
    fi

    # Enable and start
    echo_info "Starting MUNGE service..."
    sudo systemctl enable munge
    sudo systemctl restart munge

    # Wait and verify
    sleep 2

    if munge -n | unmunge &> /dev/null; then
        echo_success "MUNGE authentication successful!"
        munge -n | unmunge
    else
        echo_error "MUNGE authentication failed!"
        echo_info "Check logs: sudo journalctl -u munge -n 20"
        exit 1
    fi
fi

echo_success "Step 1 complete: MUNGE authentication configured"

# EOF
