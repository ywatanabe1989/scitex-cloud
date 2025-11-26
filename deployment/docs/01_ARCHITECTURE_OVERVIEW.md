# 01 - Architecture Overview

## System Design

SciTeX Cloud uses a **hybrid architecture** combining:
- **Docker**: Platform services (Django, PostgreSQL, Redis, Gitea)
- **SLURM + Apptainer**: User compute workloads (isolated, fair-scheduled)
- **Celery**: Async I/O tasks (API calls, background processing)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SciTeX Cloud Platform                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │  /scholar/  │    │   /code/    │    │   /writer/  │    │    /vis/    │  │
│  │  Literature │    │  Compute    │    │  Documents  │    │   Figures   │  │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘  │
│         │                  │                  │                  │         │
│         ▼                  ▼                  ▼                  ▼         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Django Web Layer                             │   │
│  │    Request handling │ Authentication │ Template rendering            │   │
│  └───────────────────────────────┬─────────────────────────────────────┘   │
│                                  │                                         │
│         ┌────────────────────────┼────────────────────────┐               │
│         │                        │                        │               │
│         ▼                        ▼                        ▼               │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐         │
│  │   SLURM     │         │   Celery    │         │   Django    │         │
│  │  Scheduler  │         │   Workers   │         │   Sync      │         │
│  ├─────────────┤         ├─────────────┤         ├─────────────┤         │
│  │ Heavy tasks │         │ I/O tasks   │         │ Quick tasks │         │
│  │ > 30 sec    │         │ API calls   │         │ < 1 sec     │         │
│  └──────┬──────┘         └──────┬──────┘         └─────────────┘         │
│         │                       │                                         │
│         ▼                       ▼                                         │
│  ┌─────────────┐         ┌─────────────┐                                 │
│  │  Apptainer  │         │    Redis    │                                 │
│  │ Containers  │         │   Broker    │                                 │
│  └─────────────┘         └─────────────┘                                 │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

## Component Summary

| Component | Technology | Purpose |
|-----------|------------|---------|
| Web Layer | Django 5.2 | HTTP handling, auth, templates |
| Database | PostgreSQL 15 | Persistent data storage |
| Cache/Broker | Redis 7 | Caching, Celery message broker |
| Job Scheduler | SLURM | Heavy compute job management |
| Containers | Apptainer | Isolated user code execution |
| Task Queue | Celery | Async background tasks |
| Git Server | Gitea | Version control for projects |
| Monitoring | Flower | Celery task monitoring |

## Data Flow

### User Script Execution (/code/)
```
Browser → Django → SLURM → Apptainer → Results → Django → Browser
```

### AI Suggestion (/writer/)
```
Browser → Django → Celery → Claude API → Celery → Django → Browser
```

### Paper Search (/scholar/)
```
Browser → Django → Celery → PubMed/arXiv API → Celery → Django → Browser
```

### Figure Editing (/vis/)
```
Browser (Canvas) → Django (Save) → PostgreSQL
```

## Network Topology

```
┌─────────────────────────────────────────┐
│           Docker Network                │
│           (172.20.0.0/16)               │
│                                         │
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐   │
│  │ web │  │ db  │  │redis│  │gitea│   │
│  │:8000│  │:5432│  │:6379│  │:3001│   │
│  └──┬──┘  └─────┘  └──┬──┘  └─────┘   │
│     │                 │                │
│  ┌──┴──┐  ┌─────┐  ┌──┴──┐            │
│  │celery│ │beat │  │flower│            │
│  │worker│ │     │  │:5555│            │
│  └─────┘  └─────┘  └─────┘            │
│                                         │
└─────────────────────────────────────────┘
         │
         │ (Host network for SLURM)
         ▼
┌─────────────────────────────────────────┐
│           SLURM Cluster                 │
│                                         │
│  ┌──────────┐  ┌──────────────────┐    │
│  │ slurmctld│  │     slurmd       │    │
│  │ (control)│  │ (compute node)   │    │
│  └──────────┘  └──────────────────┘    │
│                        │               │
│                        ▼               │
│               ┌──────────────┐         │
│               │  Apptainer   │         │
│               │  Containers  │         │
│               └──────────────┘         │
│                                         │
└─────────────────────────────────────────┘
```

## Why This Architecture?

| Requirement | Solution |
|-------------|----------|
| Fair resource sharing | SLURM fair-share + Celery rate limits |
| Isolated user code | Apptainer containers |
| Quick web responses | Django sync handlers |
| Background processing | Celery async tasks |
| Scalability | SLURM multi-node, Celery distributed |
| Reproducibility | Container-based execution |
