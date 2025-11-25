# SciTeX Cloud - Deployment Documentation

> **Version:** 1.0.0 | **Updated:** 2025-11-25

## Document Index

| # | Document | Description |
|---|----------|-------------|
| 01 | [Architecture Overview](./01_ARCHITECTURE_OVERVIEW.md) | System design, components, data flow |
| 02 | [Fair Resource Allocation](./02_FAIR_RESOURCE_ALLOCATION.md) | Three-tier system, rate limits, quotas |
| 03 | [SLURM Setup](./03_SLURM_SETUP.md) | Job scheduler for heavy compute |
| 04 | [Celery Setup](./04_CELERY_SETUP.md) | Async task queue for I/O tasks |
| 05 | [Apptainer Containers](./05_APPTAINER_CONTAINERS.md) | User workspace containers |
| 06 | [Docker Services](./06_DOCKER_SERVICES.md) | Development/production services |
| 07 | [Operations Guide](./07_OPERATIONS_GUIDE.md) | Commands, monitoring, troubleshooting |

## Quick Start

```bash
# Start all services
cd deployment/docker/docker_dev
docker-compose up -d

# Check status
docker-compose ps
squeue
```

## System at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│  /scholar/  →  Celery (search) + SLURM (batch PDFs)        │
│  /code/     →  SLURM (user scripts, ML training)           │
│  /writer/   →  Celery (AI) + Django (editing)              │
│  /vis/      →  Django (editing) + SLURM (batch export)     │
└─────────────────────────────────────────────────────────────┘
```

## Key Directories

```
deployment/
├── docs/           # This documentation
├── slurm/          # SLURM installation scripts
├── singularity/    # Apptainer container definitions
└── docker/         # Docker compose files
    ├── docker_dev/     # Development environment
    └── docker_prod/    # Production environment
```
