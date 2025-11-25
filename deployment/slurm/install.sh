#!/bin/bash
# SLURM Installation Orchestrator for SciTeX Cloud
# File: deployment/slurm/install.sh
# Usage: ./install.sh [dev|prod|nas]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/common.sh"

# Check not running as root
check_not_root

# Parse environment argument
ENV=${1:-dev}

case "$ENV" in
    dev|development)
        ENV_FILE="${SCRIPT_DIR}/config/env.dev"
        ;;
    prod|production)
        ENV_FILE="${SCRIPT_DIR}/config/env.prod"
        ;;
    nas)
        ENV_FILE="${SCRIPT_DIR}/config/env.nas"
        ;;
    *)
        echo_error "Unknown environment: $ENV"
        echo_info "Usage: $0 [dev|prod|nas]"
        exit 1
        ;;
esac

# Check if environment file exists
if [ ! -f "$ENV_FILE" ]; then
    echo_error "Environment file not found: $ENV_FILE"
    exit 1
fi

# Load environment
echo_info "Loading environment: $ENV"
source "$ENV_FILE"

echo ""
echo_header "SLURM Installation for SciTeX Cloud"
echo_info "Environment: ${SCITEX_ENV}"
echo_info "Cluster: ${SLURM_CLUSTER_NAME}"
echo_info "Node: ${SLURM_NODE_NAME} (${SLURM_NODE_CPUS} CPUs, ${SLURM_NODE_MEMORY}MB RAM)"
echo ""

# Check if SLURM and MUNGE are installed
echo_info "Checking prerequisites..."
if ! check_package "slurm-wlm"; then
    echo_error "SLURM not installed!"
    echo_info "Install with: sudo apt-get install -y slurm-wlm slurm-wlm-basic-plugins"
    exit 1
fi

if ! check_package "munge"; then
    echo_error "MUNGE not installed!"
    echo_info "Install with: sudo apt-get install -y munge"
    exit 1
fi

echo_success "Prerequisites satisfied"
echo ""

# Confirm before proceeding
read -p "Proceed with SLURM installation? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo_info "Installation cancelled"
    exit 0
fi

echo ""
echo_header "Starting SLURM installation"
echo ""

# Step 1: Setup MUNGE
"${SCRIPT_DIR}/scripts/01_setup_munge.sh"
echo ""

# Step 2: Configure SLURM
"${SCRIPT_DIR}/scripts/02_configure_slurm.sh"
echo ""

# Step 3: Start services
"${SCRIPT_DIR}/scripts/03_start_services.sh"
echo ""

# Step 4: Verify installation
"${SCRIPT_DIR}/scripts/04_verify.sh"
echo ""

echo_header "Installation Complete!"
echo ""
echo_success "SLURM is now configured and running"
echo ""
echo_info "Configuration:"
echo_info "  Environment: ${SCITEX_ENV}"
echo_info "  Cluster: ${SLURM_CLUSTER_NAME}"
echo_info "  Node: ${SLURM_NODE_NAME}"
echo_info "  CPUs: ${SLURM_NODE_CPUS}"
echo_info "  Memory: ${SLURM_NODE_MEMORY} MB"
echo ""
echo_info "Useful commands:"
echo_info "  sinfo          - View cluster status"
echo_info "  squeue         - View job queue"
echo_info "  sbatch <file>  - Submit job"
echo_info "  scancel <id>   - Cancel job"
echo_info "  sacct          - View job history"
echo ""
echo_info "Next steps:"
echo_info "  1. Build Apptainer base image"
echo_info "  2. Implement SlurmManager in Django"
echo_info "  3. Test end-to-end job submission"
echo ""

# EOF
