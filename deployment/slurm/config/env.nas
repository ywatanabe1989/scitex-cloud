# SLURM Environment Configuration - NAS Production
# Source: deployment/slurm/config/env.nas
# Hardware: UGREEN NASync DXP480T Plus

# Cluster identification
export SLURM_CLUSTER_NAME="scitex-nas"
export SLURM_NODE_NAME="$(hostname -s)"  # Auto-detect hostname

# Hardware specs (UGREEN NASync DXP480T Plus)
export SLURM_NODE_CPUS="10"       # Intel i5-1235U (10 cores)
export SLURM_NODE_MEMORY="64000"  # 64GB RAM

# Resource limits per user
export SLURM_DEFAULT_MEM_PER_CPU="2000"  # MB
export SLURM_MAX_MEM_PER_CPU="4000"      # MB

# Logging
export SLURM_LOG_LEVEL="info"

# Accounting
export SLURM_ACCOUNTING_STORAGE="accounting_storage/slurmdbd"

# Environment
export SCITEX_ENV="production"

# EOF
