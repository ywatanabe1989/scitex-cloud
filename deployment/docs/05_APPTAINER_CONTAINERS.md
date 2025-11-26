# 05 - Apptainer Containers

## What is Apptainer?

Container platform for HPC (formerly Singularity). Runs as user, no daemon, ideal for compute clusters.

## Why Apptainer (not Docker)?

| Feature | Docker | Apptainer |
|---------|--------|-----------|
| Root required | Yes (daemon) | No |
| HPC compatible | Limited | Native |
| SLURM integration | Manual | Native |
| User isolation | Container root | Host UID |

## Container Definition

**Location:** `deployment/singularity/scitex-user-workspace.def`

```singularity
Bootstrap: docker
From: python:3.11-slim

%labels
    Version 2.0.0
    SciTeX Latest from PyPI

%post
    # System packages
    apt-get update && apt-get install -y \
        build-essential git wget curl vim nano \
        tmux htop tree less zip unzip

    # Python packages
    pip install --no-cache-dir \
        numpy scipy pandas matplotlib seaborn \
        scikit-learn jupyter jupyterlab

    # SciTeX with all extras
    pip install 'scitex[dl,ml,jupyter,neuro,web,scholar,writer]'

%environment
    export LC_ALL=C
    export PATH=/usr/local/bin:$PATH

%runscript
    exec python "$@"
```

## Building Container

```bash
cd deployment/singularity

# Build container (requires sudo for bootstrap)
sudo apptainer build scitex-user-workspace.sif scitex-user-workspace.def

# Build time: ~15 minutes
# Size: ~4.9 GB
```

## Container Contents

| Component | Version |
|-----------|---------|
| Python | 3.11.14 |
| NumPy | 1.26.4 |
| SciPy | 1.12.0 |
| Pandas | 2.2.0 |
| Matplotlib | 3.8.2 |
| scikit-learn | 1.4.0 |
| PyTorch | Latest |
| TensorFlow | Latest |
| SciTeX | 2.3.0 |

## Running Container

### Direct Execution

```bash
# Run Python script
apptainer exec scitex-user-workspace.sif python script.py

# Interactive shell
apptainer shell scitex-user-workspace.sif

# With workspace binding
apptainer exec \
    --bind /tmp/workspace:/workspace \
    --pwd /workspace \
    scitex-user-workspace.sif \
    python analysis.py
```

### Via SLURM

```bash
#!/bin/bash
#SBATCH --job-name=my_job
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G

apptainer exec \
    --contain \
    --cleanenv \
    --bind /user/workspace:/workspace \
    --pwd /workspace \
    /path/to/scitex-user-workspace.sif \
    python /workspace/script.py
```

## Binding Options

| Flag | Purpose |
|------|---------|
| `--bind host:container` | Mount directory |
| `--pwd /path` | Set working directory |
| `--contain` | Isolate from host |
| `--cleanenv` | Clean environment |
| `--nv` | Enable NVIDIA GPU |

## Common Bindings

```bash
# User workspace
--bind /tmp/user_123:/workspace

# Data directory (read-only)
--bind /data/shared:/data:ro

# Output directory
--bind /results:/output
```

## Verifying Container

```bash
# Check Python
apptainer exec container.sif python --version

# Check SciTeX
apptainer exec container.sif python -c "import scitex; print(scitex.__version__)"

# Check packages
apptainer exec container.sif pip list
```

## Container Location

| Environment | Path |
|-------------|------|
| Development | `deployment/singularity/scitex-user-workspace.sif` |
| Production | `/opt/scitex/containers/scitex-user-workspace.sif` |
| NAS | `/shared/containers/scitex-user-workspace.sif` |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Permission denied | Check bind mount permissions |
| Package not found | Rebuild container |
| GPU not available | Add `--nv` flag |
| Memory error | Increase SLURM `--mem` |
