# SciTeX Resource Allocation Strategy

## Principle: Right Tool for the Right Job

Not all tasks should use SLURM. Different task types require different resource management approaches to ensure fair user access.

## Task Classification

### 1. SLURM-Managed Tasks (Heavy Compute)

**Use SLURM when:**
- CPU/GPU intensive (> 30 seconds expected)
- Memory intensive (> 1GB)
- Long-running (> 1 minute)
- Parallelizable across nodes
- Needs resource isolation

**Tasks:**
| App | Task | Resource Profile |
|-----|------|------------------|
| `/code/` | User Python scripts | CPU: 1-16, Mem: 1-32GB |
| `/code/` | ML model training | CPU: 4-16, GPU: 0-4 |
| `/code/` | Data analysis pipelines | CPU: 2-8, Mem: 4-16GB |
| `/scholar/` | Batch PDF processing (100+ PDFs) | CPU: 2-4, Mem: 4GB |
| `/vis/` | Batch figure export (100+ figures) | CPU: 2-4, Mem: 2GB |

**Fairness via SLURM:**
```bash
# User quotas in slurm.conf
MaxJobsPerUser=10
MaxSubmitJobsPerUser=20
GrpTRESMins=cpu=10000  # 10,000 CPU-minutes per month
```

### 2. Celery-Managed Tasks (Async I/O)

**Use Celery when:**
- I/O bound (API calls, file operations)
- Background processing
- Needs retry logic
- Quick but non-blocking

**Tasks:**
| App | Task | Queue |
|-----|------|-------|
| `/writer/` | AI suggestions (Claude/OpenAI) | `ai_queue` |
| `/scholar/` | Literature search (PubMed, arXiv) | `search_queue` |
| `/writer/` | LaTeX compilation | `compile_queue` |
| All | Email notifications | `default` |

**Fairness via Celery:**
```python
# Rate limiting per user
CELERY_TASK_RATE_LIMITS = {
    'writer.ai_suggest': '10/m',      # 10 AI calls per minute
    'scholar.search': '30/m',         # 30 searches per minute
}
```

### 3. Django-Managed Tasks (Interactive)

**Handle in Django when:**
- Quick (< 1 second)
- Synchronous response needed
- Database CRUD
- User interaction required

**Tasks:**
| App | Task | Protection |
|-----|------|------------|
| All | Page rendering | Connection pooling |
| All | Database queries | Query optimization |
| `/vis/` | Single figure save | Request throttling |
| `/writer/` | Document autosave | Debouncing |

**Fairness via Django:**
```python
# Request throttling in settings
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'user': '1000/day',
        'anon': '100/day',
    }
}
```

## Implementation Roadmap

### Phase 1: Current (Implemented) ✅
- [x] SLURM for `/code/` user scripts
- [x] Django for all web interactions
- [x] Basic request handling

### Phase 2: Enhanced Fairness ✅
- [x] Add Celery for AI and search tasks
- [x] Implement per-user rate limiting
- [x] Celery workers in Docker
- [x] Flower monitoring dashboard

### Phase 3: Scaling (Future)
- [ ] Multi-node SLURM cluster
- [ ] GPU partition for ML tasks
- [ ] Distributed Celery workers
- [ ] SLURM job quotas per user

## Per-App Resource Strategy

### /code/ - Computational Workbench
```
User submits script
        │
        ▼
┌───────────────────┐
│  Quick validation │  ← Django (< 1s)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  SLURM job queue  │  ← SLURM (minutes to hours)
│  - Apptainer      │
│  - Resource limits│
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Results stored   │  ← Django (retrieve output)
└───────────────────┘
```

### /scholar/ - Literature Research
```
User searches papers
        │
        ▼
┌───────────────────┐
│  Parse query      │  ← Django (< 1s)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Search APIs      │  ← Celery (async, I/O bound)
│  - PubMed         │
│  - arXiv          │
│  - Google Scholar │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Process PDFs     │  ← SLURM (if batch) or Celery (if few)
└───────────────────┘
```

### /writer/ - Document Authoring
```
User requests AI help
        │
        ▼
┌───────────────────┐
│  Validate request │  ← Django (< 1s)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  AI API call      │  ← Celery (rate-limited)
│  - Claude         │
│  - Rate limited   │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Return suggestion│  ← Django (WebSocket or SSE)
└───────────────────┘
```

### /vis/ - Visualization
```
User edits figure
        │
        ▼
┌───────────────────┐
│  Client-side edit │  ← Browser (JS/Canvas)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Save to server   │  ← Django (quick)
└───────────────────┘

User exports batch
        │
        ▼
┌───────────────────┐
│  Queue batch job  │  ← SLURM (if large)
└───────────────────┘
```

## Fair Opportunity Guarantees

### 1. Compute Fairness (SLURM)
- Equal job slots per user (default: 5 concurrent)
- Fair-share scheduling (priority based on recent usage)
- CPU-minute budgets per month
- Express queue for quick jobs (< 5 min limit)

### 2. API Fairness (Celery/Django)
- Rate limiting per user per endpoint
- Priority queues for premium users (if monetized)
- Retry budgets for failed requests
- Graceful degradation under load

### 3. Storage Fairness
- Workspace quotas per user
- Automatic cleanup of old job outputs
- Shared project storage pools

## Monitoring & Alerts

```bash
# SLURM usage per user
sacct -u $USER --format=JobID,Elapsed,MaxRSS,ExitCode

# Celery queue depth
celery -A config inspect stats

# Django request metrics
# (via prometheus/grafana)
```

## Conclusion

Fair resource allocation requires a **multi-layer approach**:

1. **SLURM** for heavy compute (fair scheduling, quotas)
2. **Celery** for async I/O (rate limiting, queues)
3. **Django** for interactive (throttling, pooling)

This ensures users get fair access regardless of task type while optimizing for the specific characteristics of each workload.
