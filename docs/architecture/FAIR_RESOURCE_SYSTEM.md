# SciTeX Cloud - Fair Resource Allocation System

> **Document Version:** 1.0.0
> **Last Updated:** 2025-11-25
> **Author:** ywatanabe

## Table of Contents

1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Three-Tier Resource System](#three-tier-resource-system)
4. [SLURM: Heavy Compute](#slurm-heavy-compute)
5. [Celery: Async I/O Tasks](#celery-async-io-tasks)
6. [Django: Interactive Requests](#django-interactive-requests)
7. [Fair Scheduling Rules](#fair-scheduling-rules)
8. [Per-App Task Routing](#per-app-task-routing)
9. [File Locations](#file-locations)
10. [Operations Guide](#operations-guide)

---

## Overview

SciTeX Cloud uses a **three-tier resource allocation system** to ensure fair access for all users:

| Tier | Technology | Use Case | Fairness Mechanism |
|------|------------|----------|-------------------|
| **Heavy Compute** | SLURM + Apptainer | ML training, data analysis, batch jobs | Job quotas, fair-share scheduling |
| **Async I/O** | Celery + Redis | AI API calls, paper search, PDF processing | Rate limiting, queue prioritization |
| **Interactive** | Django | Page loads, CRUD, quick queries | Request throttling, connection pooling |

**Key Principle:** Different task types need different resource management approaches. Not everything should use SLURM.

---

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
│  │                      Django Web Layer                                │   │
│  │  • Request handling  • Authentication  • Template rendering         │   │
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
│  │ CPU/GPU     │         │ Background  │         │ Interactive │         │
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

---

## Three-Tier Resource System

### When to Use Each Tier

```
User Request
     │
     ▼
┌─────────────────────────────────────────┐
│  Is it CPU/GPU intensive (> 30 sec)?    │
└────────────────┬────────────────────────┘
                 │
        ┌────────┴────────┐
        │ YES             │ NO
        ▼                 ▼
   ┌─────────┐    ┌─────────────────────────────┐
   │  SLURM  │    │  Is it I/O bound or async?  │
   └─────────┘    └──────────────┬──────────────┘
                                 │
                        ┌────────┴────────┐
                        │ YES             │ NO
                        ▼                 ▼
                   ┌─────────┐       ┌─────────┐
                   │ Celery  │       │ Django  │
                   └─────────┘       └─────────┘
```

---

## SLURM: Heavy Compute

### What Goes to SLURM

| App | Task | Why SLURM |
|-----|------|-----------|
| `/code/` | User Python scripts | CPU intensive, long-running |
| `/code/` | ML model training | GPU required, hours to run |
| `/code/` | Data analysis pipelines | Memory intensive |
| `/scholar/` | Batch PDF processing (100+) | CPU intensive, parallel |
| `/vis/` | Batch figure export (100+) | Memory intensive |

### SLURM Configuration

**Location:** `/home/ywatanabe/proj/scitex-cloud/deployment/slurm/`

```bash
# Partitions (queues)
normal    # Default, up to 24 hours
express   # Quick jobs, up to 1 hour, higher priority
long      # Extended jobs, up to 7 days

# Resource Limits per Job
CPUs:     1-16
Memory:   1-24 GB
Time:     1 min - 7 days
```

### Fair Scheduling Rules (SLURM)

```bash
# In slurm.conf
MaxJobsPerUser=10          # Max concurrent jobs per user
MaxSubmitJobsPerUser=20    # Max jobs in queue per user

# Fair-share scheduling
# Users who recently used more resources get lower priority
PriorityType=priority/multifactor
PriorityWeightFairshare=10000
```

### Job Submission Example

```python
# apps/code_app/services/slurm_manager.py
from apps.code_app.services import SlurmManager

manager = SlurmManager()
result = manager.submit_job(
    user_id="123",
    script_path=Path("/workspace/analysis.py"),  # Path INSIDE container
    container_path=Path("/path/to/scitex-user-workspace.sif"),
    workspace=Path("/tmp/user_123_workspace"),   # Host path, mounted to /workspace
    job_name="my_analysis",
    partition="normal",
    cpus=4,
    memory_gb=8,
    time_limit="02:00:00",
)
# Returns: {'success': True, 'job_id': 42, ...}
```

### SLURM API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/code/api/jobs/submit/` | POST | Submit new job |
| `/code/api/jobs/<id>/status/` | GET | Get job status |
| `/code/api/jobs/<id>/cancel/` | POST | Cancel job |
| `/code/api/jobs/<id>/output/` | GET | Get job output |
| `/code/api/jobs/queue/` | GET | Get queue status |
| `/code/api/jobs/` | GET | List user's jobs |

---

## Celery: Async I/O Tasks

### What Goes to Celery

| App | Task | Why Celery |
|-----|------|------------|
| `/writer/` | AI suggestions (Claude/OpenAI) | External API, I/O bound |
| `/writer/` | AI content generation | External API, I/O bound |
| `/writer/` | LaTeX compilation | Background, seconds |
| `/scholar/` | Paper search (PubMed, arXiv) | External API, I/O bound |
| `/scholar/` | PDF processing (single) | Background, < 2 min |
| `/scholar/` | Metadata fetching | External API |

### Celery Configuration

**Location:** `/home/ywatanabe/proj/scitex-cloud/config/celery.py`

```python
# Broker (message queue)
CELERY_BROKER_URL = "redis://localhost:6379/1"

# Result storage
CELERY_RESULT_BACKEND = "django-db"

# Task routing to dedicated queues
CELERY_TASK_ROUTES = {
    "apps.writer_app.tasks.*": {"queue": "ai_queue"},
    "apps.scholar_app.tasks.*": {"queue": "search_queue"},
    "apps.code_app.tasks.*": {"queue": "compute_queue"},
    "apps.vis_app.tasks.*": {"queue": "vis_queue"},
}
```

### Fair Scheduling Rules (Celery)

```python
# Rate limits per task type (requests per minute)
CELERY_TASK_ANNOTATIONS = {
    "apps.writer_app.tasks.ai_suggest":      {"rate_limit": "10/m"},
    "apps.writer_app.tasks.ai_generate":     {"rate_limit": "5/m"},
    "apps.scholar_app.tasks.search_papers":  {"rate_limit": "30/m"},
    "apps.scholar_app.tasks.process_pdf":    {"rate_limit": "20/m"},
}

# Worker fairness
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # One task at a time
CELERY_WORKER_CONCURRENCY = 4          # 4 parallel workers
```

### Per-User Rate Limiting

**Location:** `/home/ywatanabe/proj/scitex-cloud/apps/core/celery_utils.py`

```python
from apps.core.celery_utils import UserRateLimiter

# Create limiter
limiter = UserRateLimiter(
    key_prefix="ai",
    requests_per_minute=10,
    burst_size=5,
)

# Check if allowed
allowed, info = limiter.is_allowed(user_id=123)
# Returns: (True, {'remaining': 4, 'limit': 10, 'reset_in': 30})
# or:      (False, {'remaining': 0, 'retry_after': 15})
```

### Task Example

```python
# apps/writer_app/tasks.py
from celery import shared_task

@shared_task(
    bind=True,
    name="apps.writer_app.tasks.ai_suggest",
    max_retries=3,
    soft_time_limit=60,
    rate_limit="10/m",
)
def ai_suggest(self, user_id, content, section_type, target="clarity"):
    """Get AI suggestions - rate limited to 10/min per worker."""
    from .services.ai_service import WriterAI

    ai = WriterAI()
    result = ai.get_suggestion(content, section_type, target)
    return {"success": True, "result": result}
```

### Calling Tasks from Views

```python
# In Django view
from apps.writer_app.tasks import ai_suggest

def get_suggestion_view(request):
    # Submit task asynchronously
    task = ai_suggest.delay(
        user_id=request.user.id,
        content=request.POST['content'],
        section_type="abstract",
    )

    # Return task ID for polling
    return JsonResponse({"task_id": task.id})

def check_task_view(request, task_id):
    from celery.result import AsyncResult

    result = AsyncResult(task_id)
    if result.ready():
        return JsonResponse(result.get())
    return JsonResponse({"status": "pending"})
```

---

## Django: Interactive Requests

### What Stays in Django

| App | Task | Why Django |
|-----|------|------------|
| All | Page rendering | Synchronous, fast |
| All | Database CRUD | Quick queries |
| `/vis/` | Figure save | Single operation |
| `/writer/` | Document autosave | Quick write |

### Fair Scheduling Rules (Django)

```python
# config/settings/settings_shared.py

# Request throttling (via DRF)
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '1000/day',
        'anon': '100/day',
    }
}

# Database connection pooling
DATABASES = {
    'default': {
        'CONN_MAX_AGE': 60,  # Reuse connections
    }
}
```

---

## Fair Scheduling Rules

### Summary Table

| Resource | Mechanism | Limit | Scope |
|----------|-----------|-------|-------|
| SLURM Jobs | Job quota | 10 concurrent | Per user |
| SLURM CPU | Fair-share | Lower priority after heavy use | Per user |
| AI Calls | Rate limit | 10/minute | Per worker |
| AI Generation | Rate limit | 5/minute | Per worker |
| Paper Search | Rate limit | 30/minute | Per worker |
| PDF Processing | Rate limit | 20/minute | Per worker |
| API Requests | Throttle | 1000/day | Per user |
| Anonymous | Throttle | 100/day | Per IP |

### User Quotas

```python
# Get current quota status for a user
from apps.core.celery_utils import get_user_quota_status

status = get_user_quota_status(user_id=123)
# Returns:
# {
#     'ai': {'remaining': 8, 'limit': 10, 'reset_in': 45},
#     'search': {'remaining': 25, 'limit': 30, 'reset_in': 30},
#     'pdf': {'remaining': 18, 'limit': 20, 'reset_in': 20},
# }
```

### What Happens When Limit Exceeded

1. **SLURM**: Job queued, runs when resources available
2. **Celery**: Task rejected with `retry_after` seconds
3. **Django**: HTTP 429 Too Many Requests

---

## Per-App Task Routing

### /code/ - Computational Workbench

```
User submits script
        │
        ▼
┌───────────────────┐
│  Django: Validate │  (< 1s)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  SLURM: Execute   │  (minutes to hours)
│  in Apptainer     │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Django: Results  │  (< 1s)
└───────────────────┘
```

### /scholar/ - Literature Research

```
User searches papers
        │
        ▼
┌───────────────────┐
│  Django: Parse    │  (< 1s)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Celery: Search   │  (seconds, rate limited)
│  External APIs    │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Django: Display  │  (< 1s)
└───────────────────┘

User processes 100+ PDFs
        │
        ▼
┌───────────────────┐
│  SLURM: Batch     │  (minutes, parallel)
│  Processing       │
└───────────────────┘
```

### /writer/ - Document Authoring

```
User requests AI help
        │
        ▼
┌───────────────────┐
│  Django: Validate │  (< 1s)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Celery: AI API   │  (seconds, rate limited)
│  Claude/OpenAI    │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Django: Return   │  (WebSocket or polling)
└───────────────────┘
```

### /vis/ - Visualization

```
User edits figure (single)
        │
        ▼
┌───────────────────┐
│  Browser: Canvas  │  (client-side)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Django: Save     │  (< 1s)
└───────────────────┘

User exports 100+ figures
        │
        ▼
┌───────────────────┐
│  SLURM: Batch     │  (minutes)
│  Export           │
└───────────────────┘
```

---

## File Locations

### Core Configuration

```
config/
├── celery.py                    # Celery app definition
├── settings/
│   └── settings_shared.py       # CELERY_* settings, rate limits
└── __init__.py                  # Imports celery_app

deployment/
├── slurm/
│   ├── install.sh               # SLURM installation script
│   ├── config/
│   │   ├── env.dev              # Dev environment (hostname, memory)
│   │   ├── env.prod             # Prod environment
│   │   └── env.nas              # NAS environment
│   ├── templates/
│   │   └── slurm.conf.template  # SLURM config template
│   └── scripts/
│       ├── 01_setup_munge.sh    # MUNGE authentication
│       ├── 02_configure_slurm.sh # SLURM configuration
│       └── ...
└── docker/docker_dev/
    └── docker-compose.yml       # Celery worker, beat, flower services
```

### Task Definitions

```
apps/
├── writer_app/
│   └── tasks.py                 # ai_suggest, ai_generate, compile_latex
├── scholar_app/
│   └── tasks.py                 # search_papers, process_pdf, fetch_metadata
├── code_app/
│   ├── services/
│   │   └── slurm_manager.py     # SlurmManager class
│   └── job_api_views.py         # SLURM REST API endpoints
└── core/
    └── celery_utils.py          # UserRateLimiter, rate limit decorators
```

### Container Definition

```
deployment/singularity/
└── scitex-user-workspace.def    # Apptainer container (SciTeX 2.3.0)
```

---

## Operations Guide

### Starting Services

```bash
# Start all services (including Celery)
cd deployment/docker/docker_dev
docker-compose up -d

# Start only Celery services
docker-compose up -d celery_worker celery_beat flower

# Check service status
docker-compose ps
```

### Monitoring

```bash
# Flower dashboard (Celery monitoring)
open http://localhost:5555

# SLURM queue status
squeue

# SLURM job details
sacct -j <job_id> --format=JobID,JobName,State,ExitCode,Elapsed

# Redis queue depth
docker-compose exec redis redis-cli LLEN celery
```

### Common Operations

```bash
# Restart Celery worker (pick up new code)
docker-compose restart celery_worker

# Check Celery worker logs
docker-compose logs -f celery_worker

# Purge all pending tasks (careful!)
docker-compose exec celery_worker celery -A config purge

# SLURM: Cancel all user's jobs
scancel -u <username>

# SLURM: Check node status
sinfo
```

### Troubleshooting

| Problem | Check | Solution |
|---------|-------|----------|
| Tasks not running | `docker-compose ps` | Restart celery_worker |
| Rate limit errors | Flower dashboard | Wait for reset_in seconds |
| SLURM job pending | `squeue -j <id>` | Check resources, priority |
| Container not found | `ls *.sif` | Rebuild with `apptainer build` |

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│                   SciTeX Resource Cheat Sheet                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  WHEN TO USE WHAT:                                              │
│  ─────────────────                                              │
│  SLURM   → Heavy compute, > 30 sec, CPU/GPU intensive          │
│  Celery  → API calls, background tasks, I/O bound              │
│  Django  → Quick operations, < 1 sec, interactive              │
│                                                                 │
│  RATE LIMITS:                                                   │
│  ────────────                                                   │
│  AI suggestions    10/min                                       │
│  AI generation      5/min                                       │
│  Paper search      30/min                                       │
│  PDF processing    20/min                                       │
│  API requests    1000/day                                       │
│                                                                 │
│  MONITORING:                                                    │
│  ───────────                                                    │
│  Celery → http://localhost:5555 (Flower)                       │
│  SLURM  → squeue, sinfo, sacct                                 │
│                                                                 │
│  KEY FILES:                                                     │
│  ──────────                                                     │
│  config/celery.py           - Celery app                       │
│  apps/*/tasks.py            - Task definitions                 │
│  apps/core/celery_utils.py  - Rate limiting                    │
│  deployment/slurm/          - SLURM installation               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Related Documents

- [RESOURCE_ALLOCATION_STRATEGY.md](./RESOURCE_ALLOCATION_STRATEGY.md) - Detailed strategy
- [SLURM_INSTALLATION.md](./SLURM_INSTALLATION.md) - SLURM setup guide
- [APPTAINER_SETUP.md](./APPTAINER_SETUP.md) - Container configuration

---

*This document is the authoritative reference for SciTeX Cloud's fair resource allocation system.*
