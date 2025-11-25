# 03 - SLURM Setup

## What is SLURM?

**S**imple **L**inux **U**tility for **R**esource **M**anagement - Job scheduler for compute clusters.

## When to Use

✅ User Python scripts
✅ ML model training
✅ Data analysis pipelines
✅ Batch PDF processing (100+ files)
✅ Batch figure export (100+ figures)

## Installation

```bash
cd deployment/slurm
./install.sh dev    # For development (WSL)
./install.sh prod   # For production
./install.sh nas    # For NAS server
```

## Directory Structure

```
deployment/slurm/
├── install.sh              # Main installer
├── config/
│   ├── env.dev             # Dev config (hostname, memory)
│   ├── env.prod            # Prod config
│   └── env.nas             # NAS config
├── templates/
│   └── slurm.conf.template # SLURM config template
└── scripts/
    ├── 01_setup_munge.sh   # Authentication setup
    ├── 02_configure_slurm.sh
    ├── 03_start_services.sh
    └── 04_verify.sh
```

## Environment Config (env.dev)

```bash
export SLURM_CLUSTER_NAME="scitex-dev"
export SLURM_NODE_NAME="$(hostname -s)"  # Dynamic
export SLURM_NODE_CPUS="16"
export SLURM_NODE_MEMORY="24000"  # MB
export SLURM_PARTITION_NORMAL_TIME="24:00:00"
export SLURM_PARTITION_EXPRESS_TIME="01:00:00"
export SLURM_PARTITION_LONG_TIME="168:00:00"
```

## Partitions (Queues)

| Partition | Max Time | Priority | Use Case |
|-----------|----------|----------|----------|
| normal | 24 hours | 50 | Default |
| express | 1 hour | 100 | Quick jobs |
| long | 7 days | 25 | Extended jobs |

## SlurmManager API

**Location:** `apps/code_app/services/slurm_manager.py`

```python
from apps.code_app.services import SlurmManager

manager = SlurmManager()

# Submit job
result = manager.submit_job(
    user_id="123",
    script_path=Path("/workspace/script.py"),  # Inside container
    container_path=Path("/path/to/container.sif"),
    workspace=Path("/tmp/user_workspace"),      # Host path
    job_name="my_job",
    partition="normal",
    cpus=4,
    memory_gb=8,
    time_limit="02:00:00",
)
# Returns: {'success': True, 'job_id': 42, ...}

# Check status
status = manager.get_job_status(42)
# Returns: {'job_id': 42, 'state': 'RUNNING', ...}

# Cancel job
manager.cancel_job(42)

# Get output
output = manager.get_job_output(42, workspace)
# Returns: {'stdout': '...', 'stderr': '...'}
```

## REST API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/code/api/jobs/submit/` | POST | Submit job |
| `/code/api/jobs/<id>/status/` | GET | Job status |
| `/code/api/jobs/<id>/cancel/` | POST | Cancel job |
| `/code/api/jobs/<id>/output/` | GET | Job output |
| `/code/api/jobs/queue/` | GET | Queue status |

## Job Submission (POST body)

```json
{
    "script_path": "/workspace/analysis.py",
    "job_name": "my_analysis",
    "cpus": 2,
    "memory_gb": 4,
    "time_limit": "01:00:00",
    "partition": "normal",
    "env_vars": {"DEBUG": "1"}
}
```

## Important Notes

1. **script_path** is path INSIDE container (`/workspace/...`)
2. **workspace** on host is mounted to `/workspace` in container
3. Output files: `{workspace}/slurm_outputs/slurm-{job_id}.out`

## Common Commands

```bash
# Check queue
squeue

# Job details
scontrol show job <job_id>

# Cancel job
scancel <job_id>

# Node status
sinfo

# Job history
sacct -j <job_id> --format=JobID,JobName,State,ExitCode,Elapsed
```

## WSL-Specific Config

For WSL, use these plugins (cgroup doesn't work):

```bash
ProctrackType=proctrack/linuxproc
TaskPlugin=task/none
```
