# 04 - Celery Setup

## What is Celery?

Distributed task queue for async/background job processing.

## When to Use

✅ AI API calls (Claude, OpenAI)
✅ Paper search (PubMed, arXiv)
✅ PDF processing (single files)
✅ LaTeX compilation
✅ Email notifications

## Architecture

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Django  │───▶│  Redis  │───▶│ Celery  │───▶│ Result  │
│  View   │    │ Broker  │    │ Worker  │    │   DB    │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
```

## Configuration

### Celery App

**Location:** `config/celery.py`

```python
from celery import Celery

app = Celery('scitex_cloud')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### Settings

**Location:** `config/settings/settings_shared.py`

```python
CELERY_BROKER_URL = "redis://localhost:6379/1"
CELERY_RESULT_BACKEND = "django-db"

# Task routing
CELERY_TASK_ROUTES = {
    "apps.writer_app.tasks.*": {"queue": "ai_queue"},
    "apps.scholar_app.tasks.*": {"queue": "search_queue"},
}

# Rate limits
CELERY_TASK_ANNOTATIONS = {
    "apps.writer_app.tasks.ai_suggest": {"rate_limit": "10/m"},
    "apps.writer_app.tasks.ai_generate": {"rate_limit": "5/m"},
    "apps.scholar_app.tasks.search_papers": {"rate_limit": "30/m"},
}

# Fairness
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # One task at a time
CELERY_WORKER_CONCURRENCY = 4
```

## Task Queues

| Queue | Tasks | Rate |
|-------|-------|------|
| ai_queue | AI suggestions, generation | 5-10/min |
| search_queue | Paper search, PDF processing | 20-30/min |
| compute_queue | Light compute tasks | No limit |
| vis_queue | Visualization tasks | No limit |

## Task Files

### Writer Tasks

**Location:** `apps/writer_app/tasks.py`

```python
@shared_task(name="apps.writer_app.tasks.ai_suggest", rate_limit="10/m")
def ai_suggest(user_id, content, section_type, target="clarity"):
    from .services.ai_service import WriterAI
    ai = WriterAI()
    return ai.get_suggestion(content, section_type, target)

@shared_task(name="apps.writer_app.tasks.ai_generate", rate_limit="5/m")
def ai_generate(user_id, section_type, target_words, context=None):
    ...

@shared_task(name="apps.writer_app.tasks.compile_latex", rate_limit="20/m")
def compile_latex(user_id, document_id, output_format="pdf"):
    ...
```

### Scholar Tasks

**Location:** `apps/scholar_app/tasks.py`

```python
@shared_task(name="apps.scholar_app.tasks.search_papers", rate_limit="30/m")
def search_papers(user_id, query, sources=None, max_results=20):
    ...

@shared_task(name="apps.scholar_app.tasks.process_pdf", rate_limit="20/m")
def process_pdf(user_id, pdf_path, extract_text=True):
    ...

@shared_task(name="apps.scholar_app.tasks.fetch_paper_metadata", rate_limit="60/m")
def fetch_paper_metadata(user_id, identifier, identifier_type="doi"):
    ...
```

## Usage in Views

```python
from apps.writer_app.tasks import ai_suggest

def suggestion_view(request):
    # Submit async task
    task = ai_suggest.delay(
        user_id=request.user.id,
        content=request.POST['content'],
        section_type="abstract",
    )
    return JsonResponse({"task_id": task.id})

def check_task_view(request, task_id):
    from celery.result import AsyncResult
    result = AsyncResult(task_id)
    if result.ready():
        return JsonResponse(result.get())
    return JsonResponse({"status": "pending"})
```

## Per-User Rate Limiting

**Location:** `apps/core/celery_utils.py`

```python
from apps.core.celery_utils import UserRateLimiter

limiter = UserRateLimiter(
    key_prefix="ai",
    requests_per_minute=10,
    burst_size=5,
)

allowed, info = limiter.is_allowed(user_id=123)
# (True, {'remaining': 4, 'limit': 10, 'reset_in': 30})
# (False, {'remaining': 0, 'retry_after': 15})
```

## Docker Services

```yaml
# docker-compose.yml
celery_worker:
  command: >
    celery -A config worker
    --loglevel=info
    --queues=celery,ai_queue,search_queue,compute_queue,vis_queue
    --concurrency=4

celery_beat:
  command: celery -A config beat --loglevel=info

flower:
  command: celery -A config flower --port=5555
  ports:
    - "5555:5555"
```

## Monitoring

- **Flower Dashboard:** http://localhost:5555
- View queues, workers, task success/failure rates
