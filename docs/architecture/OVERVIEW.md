# Architecture Overview

## Three-Layer Resource Management

```
┌─────────────────────────────────────────────────────────┐
│                     User Request                        │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   ┌────────┐  ┌─────────┐  ┌─────────┐
   │ Django │  │  Celery │  │  SLURM  │
   │  Web   │  │  Async  │  │ Compute │
   └────────┘  └─────────┘  └─────────┘
        │            │            │
        │            │            │
   Interactive  I/O Bound    CPU Heavy
   < 1 second   Async        Minutes

   Quick UI     AI calls     User code
   CRUD ops     Searches     ML training
   Editing      PDF proc     Analysis
```

## Technology Stack

**Frontend:**
- HTML/CSS/JavaScript
- Bootstrap 5
- htmx for dynamic updates

**Backend:**
- Django 5.1
- Django REST Framework
- PostgreSQL 16
- Redis 7

**Compute:**
- SLURM 24.05
- Apptainer/Singularity 1.3
- Celery 5.4

**Infrastructure:**
- Docker & Docker Compose
- Nginx (reverse proxy)
- Gitea (Git server)

## Service Routing

| Request Type | Handler | Example |
|-------------|---------|---------|
| Page loads | Django | `/scholar/`, `/writer/` |
| AI suggestions | Celery | Claude API calls |
| Paper search | Celery | PubMed, arXiv queries |
| User scripts | SLURM | Python analysis, ML training |

## Detailed Documentation

- [Fair Resource Allocation](./FAIR_RESOURCE_SYSTEM.md)
- [Resource Strategy](./RESOURCE_ALLOCATION_STRATEGY.md)
- [Deployment Docs](../../deployment/docs/00_INDEX.md)
