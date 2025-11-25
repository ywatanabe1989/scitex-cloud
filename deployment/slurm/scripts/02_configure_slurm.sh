#!/bin/bash
# SLURM Installation Step 2: Configure SLURM
# File: deployment/slurm/scripts/02_configure_slurm.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

echo_header "Step 2: Configuring SLURM"

# Check if SLURM is installed
if [ ! -f /usr/sbin/slurmctld ] && ! command -v sbatch &> /dev/null; then
    echo_error "SLURM is not installed. Please install it first:"
    echo_info "sudo apt-get install -y slurm-wlm slurm-wlm-basic-plugins"
    exit 1
fi

echo_success "SLURM is installed"

# Load environment variables
if [ -z "$SLURM_CLUSTER_NAME" ]; then
    echo_error "SLURM environment variables not loaded!"
    echo_info "Source the appropriate config first:"
    echo_info "  source deployment/slurm/config/env.dev"
    echo_info "  source deployment/slurm/config/env.nas"
    exit 1
fi

echo_info "Cluster: ${SLURM_CLUSTER_NAME}"
echo_info "Node: ${SLURM_NODE_NAME} (${SLURM_NODE_CPUS} CPUs, ${SLURM_NODE_MEMORY}MB RAM)"

# Create directories
echo_info "Creating SLURM directories..."
sudo mkdir -p /etc/slurm
sudo mkdir -p /var/log/slurm
sudo mkdir -p /var/spool/slurm

# Set permissions
echo_info "Setting directory permissions..."
if id slurm &>/dev/null; then
    sudo chown slurm: /var/log/slurm
    sudo chown slurm: /var/spool/slurm
else
    echo_warning "User 'slurm' does not exist. Skipping chown."
fi

# Generate slurm.conf from template
echo_info "Generating slurm.conf..."
TEMPLATE_FILE="${SCRIPT_DIR}/../templates/slurm.conf.template"

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo_error "Template file not found: $TEMPLATE_FILE"
    exit 1
fi

# Replace variables in template
sudo sed -e "s/{{CLUSTER_NAME}}/${SLURM_CLUSTER_NAME}/g" \
         -e "s/{{NODE_NAME}}/${SLURM_NODE_NAME}/g" \
         -e "s/{{NODE_CPUS}}/${SLURM_NODE_CPUS}/g" \
         -e "s/{{NODE_MEMORY}}/${SLURM_NODE_MEMORY}/g" \
         -e "s/{{DEFAULT_MEM_PER_CPU}}/${SLURM_DEFAULT_MEM_PER_CPU}/g" \
         -e "s/{{MAX_MEM_PER_CPU}}/${SLURM_MAX_MEM_PER_CPU}/g" \
         -e "s/{{LOG_LEVEL}}/${SLURM_LOG_LEVEL}/g" \
         -e "s|{{ACCOUNTING_STORAGE}}|${SLURM_ACCOUNTING_STORAGE}|g" \
         "$TEMPLATE_FILE" | sudo tee /etc/slurm/slurm.conf > /dev/null

# Copy cgroup.conf
echo_info "Copying cgroup.conf..."
sudo cp "${SCRIPT_DIR}/../cgroup.conf" /etc/slurm/cgroup.conf

# Set permissions
echo_info "Setting configuration file permissions..."
sudo chmod 644 /etc/slurm/slurm.conf
sudo chmod 644 /etc/slurm/cgroup.conf

echo_success "Step 2 complete: SLURM configured"
echo_info "Configuration files:"
echo_info "  - /etc/slurm/slurm.conf"
echo_info "  - /etc/slurm/cgroup.conf"

# EOF
