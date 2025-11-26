# SciTeX Singularity User Workspace

This directory contains Singularity container definitions for secure user code execution in SciTeX Cloud.

## Why Singularity?

Singularity provides superior security compared to Docker for multi-user environments:

- ✅ **No root daemon** - eliminates major security risk
- ✅ **UID preservation** - user runs as themselves, no mapping complexity
- ✅ **HPC integration** - works seamlessly with SLURM/PBS clusters
- ✅ **Resource efficiency** - single .sif image shared by all users (500MB vs 32GB for Docker)
- ✅ **Designed for untrusted users** - built for multi-tenant HPC environments

See `/GITIGNORED/SECURITY_AUDIT_CODE_MODULE.md` Section 11 for detailed comparison.

## Files

- `scitex-user-workspace.def` - Singularity definition file
- `scitex-user-workspace.sif` - Built container image (generated)
- `build.sh` - Build script
- `test.sh` - Test script
- `README.md` - This file

## Quick Start

### 1. Install Singularity

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y singularity-container

# Check version (requires 3.8+)
singularity --version
```

### 2. Build the Container

```bash
cd /home/ywatanabe/proj/scitex-cloud/deployment/singularity

# Build (requires sudo for image creation)
sudo ./build.sh

# Or manually:
sudo singularity build scitex-user-workspace.sif scitex-user-workspace.def
```

Build time: ~5-10 minutes depending on network speed.

### 3. Test the Container

```bash
# Run test script
./test.sh

# Or test manually:
singularity exec scitex-user-workspace.sif python -c "import numpy; print('NumPy version:', numpy.__version__)"
```

### 4. Use in SciTeX

```python
from apps.code_app.services.singularity_manager import singularity_manager

# Execute user code
result = singularity_manager.execute_code(
    user=request.user,
    script_path=Path("/path/to/script.py"),
    timeout=300
)

print(result['stdout'])
```

## Usage Examples

### Basic Execution

```bash
# Execute a Python script
singularity exec scitex-user-workspace.sif python script.py

# With workspace binding
singularity exec --bind /data/workspace:/workspace scitex-user-workspace.sif python /workspace/analysis.py
```

### Secure Execution (Production)

```bash
# With full security options
singularity exec \
    --contain \      # Isolated /tmp, /var/tmp
    --cleanenv \     # Clean environment
    --no-home \      # Don't mount home
    --bind /data/user/workspace:/workspace:rw \
    --pwd /workspace \
    scitex-user-workspace.sif \
    python analysis.py
```

### Resource Limits (cgroups)

```bash
# Create cgroup config (cgroup.toml)
cat > cgroup.toml <<EOF
[cpu]
    shares = 350  # 35% of 1 core

[memory]
    limit = 2147483648  # 2GB

[pids]
    limit = 256
EOF

# Execute with limits
singularity exec --apply-cgroups cgroup.toml scitex-user-workspace.sif python script.py
```

### HPC Submission (SLURM)

```bash
# Submit to SLURM cluster
sbatch <<EOF
#!/bin/bash
#SBATCH --job-name=scitex_analysis
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G

module load singularity/3.8.0

singularity exec \\
    --contain \\
    --bind /data/workspace:/workspace \\
    /data/containers/scitex-user-workspace.sif \\
    python /workspace/analysis.py
EOF
```

## Installed Packages

### System Packages
- build-essential, git, curl, wget
- vim, nano, tmux, htop, tree
- zip, unzip, bzip2

### Python Packages
- **Scientific:** numpy, scipy, pandas
- **Visualization:** matplotlib, seaborn, plotly
- **ML:** scikit-learn
- **Interactive:** jupyter, jupyterlab, ipython, ipdb
- **Utilities:** requests, beautifulsoup4, tqdm
- **Dev:** black, flake8, pytest

See `scitex-user-workspace.def` for exact versions.

## Security Features

### Container Security
- No daemon required
- No privileged mode
- User runs as themselves (UID preserved)
- Isolated filesystems (--contain)
- Clean environment (--cleanenv)
- No home directory by default (--no-home)

### Resource Limits
- CPU: 0.35 cores per user (configurable)
- Memory: 2GB per user (configurable)
- PIDs: 256 processes (prevent fork bombs)
- Storage: 10GB per workspace (configurable)

### Execution Timeout
- Default: 5 minutes (300s)
- Maximum: 30 minutes (1800s)
- Hard kill after timeout

## Migration from Docker

### Before (Docker - Insecure)
```yaml
# docker-compose.yml
services:
  web:
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock  # ❌ Root access!
    privileged: true  # ❌ Dangerous!
```

```python
# Docker execution
import docker
client = docker.from_env()  # Requires daemon
container = client.containers.run(...)  # Complex UID mapping
```

### After (Singularity - Secure)
```python
# Singularity execution
subprocess.run([
    "singularity", "exec",
    "--contain", "--cleanenv",  # ✅ Secure by default
    "scitex-user-workspace.sif",
    "python", "script.py"
])  # No daemon, no root, UID preserved!
```

### Benefits
- ✅ 94% storage reduction (32GB → 500MB)
- ✅ Eliminates 3 of 4 critical security issues
- ✅ HPC-ready (Spartan compatible)
- ✅ Simpler permission model

## Troubleshooting

### Build Fails

```bash
# Check Singularity installation
singularity --version  # Should be 3.8+

# Check disk space
df -h  # Need ~2GB for build

# Check internet connection
curl -I https://hub.docker.com  # Should return 200
```

### Execution Fails

```bash
# Check image exists
ls -lh scitex-user-workspace.sif

# Test basic execution
singularity exec scitex-user-workspace.sif python --version

# Check logs
tail -f /app/logs/singularity.log
```

### Permission Issues

Singularity preserves user UID, so:
- Files created in container have your UID
- No permission issues with mounted volumes
- No need for UID mapping

### Resource Limit Not Working

Requires:
- Singularity 3.8+
- Linux kernel with cgroups v2
- Root privilege to apply cgroups

Check cgroups version:
```bash
mount | grep cgroup
# Should see cgroup2 on /sys/fs/cgroup
```

## Performance

### Build Time
- Initial build: ~5-10 minutes
- Rebuild (cached): ~2-3 minutes

### Execution Overhead
- Startup: ~100-200ms
- Runtime: Near-native performance
- Memory: No overhead (direct execution)

### Storage
- Image size: ~500MB
- Per-user workspace: 10GB (configurable)
- Total for 64 users: 500MB + 640GB = 640.5GB (vs 32GB Docker images + 640GB data)

## Monitoring

### Active Jobs
```python
from apps.code_app.services.singularity_manager import singularity_manager

# Check active jobs
active = singularity_manager.get_active_job_count()
print(f"Active jobs: {active}/10")
```

### User Statistics
```python
# Get user stats
stats = singularity_manager.get_user_stats(user.id)
print(f"Total jobs: {stats['total_jobs']}")
print(f"Success rate: {stats['successful_jobs'] / stats['total_jobs'] * 100:.1f}%")
```

## HPC Integration

### Spartan (University of Melbourne)

```bash
# Login to Spartan
ssh username@spartan.hpc.unimelb.edu.au

# Load Singularity
module load singularity/3.8.0

# Copy container (one-time)
cp /local/path/scitex-user-workspace.sif /data/projects/scitex/containers/

# Submit job
sbatch job.slurm
```

### Other HPC Systems

Singularity works on any HPC system with:
- SLURM, PBS, or other scheduler
- Singularity 3.0+ installed
- Shared filesystem (NFS, Lustre, etc.)

## Development

### Modifying the Container

1. Edit `scitex-user-workspace.def`
2. Rebuild: `sudo ./build.sh`
3. Test: `./test.sh`
4. Deploy: Copy .sif file to production

### Adding Packages

Edit the `%post` section in `.def` file:

```singularity
%post
    # Add new packages
    pip install --no-cache-dir \
        new-package==1.0.0 \
        another-package==2.0.0
```

### Testing Changes

```bash
# Build test image
sudo singularity build test.sif scitex-user-workspace.def

# Test new image
singularity exec test.sif python -c "import new_package"

# If OK, replace production image
sudo mv test.sif scitex-user-workspace.sif
```

## Production Deployment

### NAS (UGREEN NASync)

```bash
# Copy to NAS
scp scitex-user-workspace.sif nas:/app/deployment/singularity/

# Update Django settings
# SINGULARITY_IMAGE_PATH=/app/deployment/singularity/scitex-user-workspace.sif

# Restart Django
docker exec scitex-cloud-web-1 python manage.py check
```

### HPC (Spartan)

```bash
# Copy to shared storage
scp scitex-user-workspace.sif spartan:/data/projects/scitex/containers/

# Submit test job
ssh spartan "sbatch /data/projects/scitex/test_job.slurm"
```

## References

- [Singularity Documentation](https://sylabs.io/docs/)
- [SciTeX Security Audit](/GITIGNORED/SECURITY_AUDIT_CODE_MODULE.md)
- [SciTeX Docker vs Singularity Comparison](/GITIGNORED/DOCKER_AND_SINGULARITY.md)
- [Singularity User Guide](https://sylabs.io/guides/3.8/user-guide/)
- [cgroups v2 Documentation](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)

## Support

For issues or questions:
- Email: support@scitex.ai
- GitHub: https://github.com/ywatanabe/scitex-cloud/issues
- Docs: https://scitex.ai/docs

---

**Last Updated:** 2025-11-25
**Version:** 1.0.0
**Maintainer:** SciTeX Cloud Team
