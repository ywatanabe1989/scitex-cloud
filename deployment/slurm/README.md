# SLURM Installation for SciTeX Cloud

Modular, environment-aware SLURM installation system.

## Quick Start

```bash
# Development (WSL)
./install.sh dev

# Production (Generic)
./install.sh prod

# Production (NAS)
./install.sh nas
```

## Structure

```
deployment/slurm/
├── install.sh                 # Orchestration script
├── config/
│   ├── env.dev               # Development environment
│   ├── env.prod              # Production environment
│   └── env.nas               # NAS-specific production
├── scripts/
│   ├── 01_setup_munge.sh     # MUNGE authentication
│   ├── 02_configure_slurm.sh # SLURM configuration
│   ├── 03_start_services.sh  # Start services
│   ├── 04_verify.sh          # Verification & testing
│   └── 05_fix_slurmd.sh      # Fix node state issues
├── lib/
│   └── common.sh             # Shared functions
├── templates/
│   └── slurm.conf.template   # Config template
├── cgroup.conf               # Resource limits
└── .legacy/                  # Old development files
```

## Environment Configuration

**Note**: Node names are auto-detected using `$(hostname -s)` to avoid hardcoding.

### Development (env.dev)
- Cluster: `scitex-dev`
- Node: Auto-detected from hostname (e.g., `ywata-note-win`)
- Hardware: 16 CPUs, 32GB RAM
- No accounting database
- For local WSL development

### Production (env.prod)
- Cluster: `scitex-prod`
- Node: Auto-detected from hostname
- Hardware: 16 CPUs, 64GB RAM
- With accounting database
- Generic production setup

### NAS (env.nas)
- Cluster: `scitex-nas`
- Node: Auto-detected from hostname
- Hardware: 10 CPUs (Intel i5-1235U), 64GB RAM
- With accounting database
- UGREEN NASync DXP480T Plus specific

## Manual Installation

If you need to run steps individually:

```bash
# 1. Load environment
source deployment/slurm/config/env.dev

# 2. Run steps
deployment/slurm/scripts/01_setup_munge.sh
deployment/slurm/scripts/02_configure_slurm.sh
deployment/slurm/scripts/03_start_services.sh
deployment/slurm/scripts/04_verify.sh
```

## Prerequisites

Install SLURM and MUNGE first:

```bash
sudo apt-get update
sudo apt-get install -y slurm-wlm slurm-wlm-basic-plugins munge
```

## Verification

After installation:

```bash
# Check cluster status
sinfo

# View partitions
sinfo -o "%P %a %l %D %T %N"

# Submit test job
sbatch deployment/slurm/scripts/04_verify.sh
```

## Troubleshooting

### Services not starting

```bash
# Check logs
sudo journalctl -u slurmctld -n 50
sudo journalctl -u slurmd -n 50

# Check configuration
sudo slurmctld -Dvvv  # Debug mode
```

### Node in DOWN/INVALID state

```bash
# Use the fix script (auto-detects node name)
deployment/slurm/scripts/05_fix_slurmd.sh

# Or manually set node to IDLE (replace NODE_NAME with your hostname)
sudo scontrol update NodeName=$(hostname -s) State=IDLE

# Reconfigure
sudo scontrol reconfigure
```

### MUNGE authentication fails

```bash
# Test MUNGE
munge -n | unmunge

# Restart MUNGE
sudo systemctl restart munge
```

## Configuration Files

Generated files:
- `/etc/slurm/slurm.conf` - Main configuration
- `/etc/slurm/cgroup.conf` - Resource limits
- `/etc/munge/munge.key` - Authentication key

## Next Steps

1. ✅ SLURM installed
2. → Build Apptainer image: `deployment/apptainer/`
3. → Implement SlurmManager: `apps/code_app/services/`
4. → Django integration

## Related Documentation

- `.legacy/00_INSTALLATION.md` - Legacy installation guide (archived)
- `../apptainer/` - Container setup
- `../../GITIGNORED/INFRASTRUCTURE/` - Architecture docs

---

**Last Updated**: 2025-11-25
**Author**: ywatanabe
