# 02 - Fair Resource Allocation

## Three-Tier System

Different tasks need different resource management:

| Tier | System | Use Case | Fairness |
|------|--------|----------|----------|
| **Heavy Compute** | SLURM | ML training, data analysis | Job quotas, fair-share |
| **Async I/O** | Celery | AI calls, search APIs | Rate limiting |
| **Interactive** | Django | Page loads, CRUD | Request throttling |

## Decision Tree

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

## Per-App Routing

| App | Light Tasks | Heavy Tasks |
|-----|-------------|-------------|
| `/scholar/` | Celery: paper search, metadata | SLURM: batch PDF (100+) |
| `/code/` | Django: validation | SLURM: all scripts |
| `/writer/` | Celery: AI, LaTeX | - |
| `/vis/` | Django: figure save | SLURM: batch export |

## Rate Limits

### SLURM (Heavy Compute)

```bash
# Per-user limits
MaxJobsPerUser=10          # Max concurrent jobs
MaxSubmitJobsPerUser=20    # Max queued jobs

# Partitions
normal    # Default, 24h max
express   # Quick jobs, 1h max, higher priority
long      # Extended, 7 days max
```

### Celery (Async I/O)

| Task | Rate Limit | Queue |
|------|------------|-------|
| `ai_suggest` | 10/min | ai_queue |
| `ai_generate` | 5/min | ai_queue |
| `search_papers` | 30/min | search_queue |
| `process_pdf` | 20/min | search_queue |
| `compile_latex` | 20/min | ai_queue |

### Django (Interactive)

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'user': '1000/day',
        'anon': '100/day',
    }
}
```

## Summary Table

| Resource | Limit | Scope |
|----------|-------|-------|
| SLURM concurrent jobs | 10 | Per user |
| AI suggestions | 10/min | Per worker |
| AI generation | 5/min | Per worker |
| Paper search | 30/min | Per worker |
| API requests | 1000/day | Per user |
| Anonymous requests | 100/day | Per IP |

## What Happens When Limit Exceeded

| System | Behavior |
|--------|----------|
| SLURM | Job queued, waits for resources |
| Celery | Returns `retry_after` seconds |
| Django | HTTP 429 Too Many Requests |

## Configuration Files

```
config/settings/settings_shared.py   # CELERY_* settings
config/celery.py                     # Celery app
apps/core/celery_utils.py            # Per-user rate limiting
deployment/slurm/config/env.*        # SLURM environment configs
```
