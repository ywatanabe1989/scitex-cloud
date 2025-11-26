# SciTeX Cloud - Architecture Documentation Index

> Quick navigation to all architecture documents

## Overview

| Document | Description |
|----------|-------------|
| [OVERVIEW.md](./OVERVIEW.md) | Architecture diagram and tech stack |
| [MONITORING.md](./MONITORING.md) | Monitoring services and dashboards |

## Core Architecture

| Document | Description | Key Topics |
|----------|-------------|------------|
| [FAIR_RESOURCE_SYSTEM.md](./FAIR_RESOURCE_SYSTEM.md) | **Main Reference** - Complete fair resource allocation | SLURM, Celery, Django, rate limits |
| [RESOURCE_ALLOCATION_STRATEGY.md](./RESOURCE_ALLOCATION_STRATEGY.md) | Strategy and rationale | Task classification, fairness principles |

## Infrastructure Components

| Document | Description | Status |
|----------|-------------|--------|
| [SLURM_INSTALLATION.md](./SLURM_INSTALLATION.md) | SLURM setup and configuration | ✅ Implemented |
| [APPTAINER_SETUP.md](./APPTAINER_SETUP.md) | Container environment | ✅ Implemented |
| [HYBRID_ARCHITECTURE.md](./HYBRID_ARCHITECTURE.md) | Docker + SLURM hybrid | ✅ Implemented |

## Project Management

| Document | Description | Status |
|----------|-------------|--------|
| [REMOTE_PROJECT_INTEGRATION.md](./REMOTE_PROJECT_INTEGRATION.md) | Remote filesystem access (TRAMP-like) | 📋 Planning |

## Quick Reference

### Which System Handles What?

```
/code/   → SLURM (user scripts, ML training)
/scholar/ → Celery (search) + SLURM (batch PDFs)
/writer/ → Celery (AI) + Django (editing)
/vis/    → Django (editing) + SLURM (batch export)
```

### Rate Limits at a Glance

| Service | Limit | System |
|---------|-------|--------|
| AI suggestions | 10/min | Celery |
| AI generation | 5/min | Celery |
| Paper search | 30/min | Celery |
| SLURM jobs | 10 concurrent | SLURM |
| API requests | 1000/day | Django |

### Key Files

```
config/celery.py              # Celery configuration
apps/*/tasks.py               # Async task definitions
apps/code_app/services/       # SlurmManager
deployment/slurm/             # SLURM installation
deployment/singularity/       # Apptainer containers
```

### Monitoring URLs

- **Celery (Flower):** http://localhost:5555
- **Django Admin:** http://localhost:8000/admin/

---

*Start with [FAIR_RESOURCE_SYSTEM.md](./FAIR_RESOURCE_SYSTEM.md) for complete documentation.*
