# 06 - Docker Services

## Service Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │   web   │  │   db    │  │  redis  │  │  gitea  │       │
│  │ :8000   │  │ :5432   │  │ :6379   │  │ :3001   │       │
│  │ Django  │  │Postgres │  │  Cache  │  │   Git   │       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                     │
│  │ celery  │  │  beat   │  │ flower  │                     │
│  │ worker  │  │scheduler│  │ :5555   │                     │
│  │  Tasks  │  │Periodic │  │ Monitor │                     │
│  └─────────┘  └─────────┘  └─────────┘                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Services

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| web | scitex-cloud-dev-web | 8000 | Django application |
| db | postgres:15-alpine | 5432 | Database |
| redis | redis:7-alpine | 6379 | Cache & Celery broker |
| gitea | gitea/gitea | 3001 | Git server |
| celery_worker | scitex-cloud-dev-web | - | Task processing |
| celery_beat | scitex-cloud-dev-web | - | Periodic tasks |
| flower | scitex-cloud-dev-web | 5555 | Celery monitoring |

## Docker Compose File

**Location:** `deployment/docker/docker_dev/docker-compose.yml`

### Web Service

```yaml
web:
  build:
    context: ../../..
    dockerfile: deployment/docker/docker_dev/Dockerfile
  ports:
    - "8000:8000"
  volumes:
    - ../../..:/app:cached
    - ../../../../scitex-code:/scitex-code:cached
    - ../../../logs:/app/logs
  depends_on:
    db:
      condition: service_healthy
    redis:
      condition: service_started
  command: ["python", "manage.py", "runserver", "0.0.0.0:8000", "from_docker"]
```

### Database

```yaml
db:
  image: postgres:15-alpine
  volumes:
    - postgres_data:/var/lib/postgresql/data
  ports:
    - "5433:5432"
  environment:
    - POSTGRES_DB=scitex_cloud_dev
    - POSTGRES_USER=scitex_dev
    - POSTGRES_PASSWORD=scitex_dev_2025
```

### Redis

```yaml
redis:
  image: redis:7-alpine
  volumes:
    - redis_data:/data
  ports:
    - "6379:6379"
  command: redis-server --appendonly yes
```

### Celery Worker

```yaml
celery_worker:
  image: scitex-cloud-dev-web:latest
  volumes:
    - ../../..:/app:cached
  depends_on:
    - db
    - redis
  command: >
    celery -A config worker
    --loglevel=info
    --queues=celery,ai_queue,search_queue,compute_queue,vis_queue
    --concurrency=4
    --prefetch-multiplier=1
```

### Celery Beat

```yaml
celery_beat:
  image: scitex-cloud-dev-web:latest
  depends_on:
    - db
    - redis
  command: celery -A config beat --loglevel=info
```

### Flower

```yaml
flower:
  image: scitex-cloud-dev-web:latest
  ports:
    - "5555:5555"
  depends_on:
    - redis
    - celery_worker
  command: celery -A config flower --port=5555 --broker=redis://redis:6379/1
```

### Gitea

```yaml
gitea:
  image: gitea/gitea:latest
  volumes:
    - gitea_data:/data
  ports:
    - "3001:3000"
    - "2222:22"
  environment:
    - GITEA__database__DB_TYPE=postgres
    - GITEA__database__HOST=db:5432
```

## Volumes

```yaml
volumes:
  postgres_data:    # Database persistence
  redis_data:       # Cache persistence
  gitea_data:       # Git repositories
  static_volume:    # Static files
  media_volume:     # Uploaded files
  uv_cache:         # Build cache
```

## Network

```yaml
networks:
  scitex-dev:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## Commands

```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d web db redis

# Rebuild after code changes
docker-compose build web
docker-compose up -d web

# View logs
docker-compose logs -f web
docker-compose logs -f celery_worker

# Restart service
docker-compose restart web

# Stop all
docker-compose down

# Stop and remove volumes (careful!)
docker-compose down -v
```

## Environment Variables

**Location:** `deployment/docker/docker_dev/.env`

```bash
# Django
SCITEX_CLOUD_DJANGO_SECRET_KEY=your-secret-key
SCITEX_CLOUD_DJANGO_DEBUG=True

# Database
SCITEX_CLOUD_POSTGRES_DB=scitex_cloud_dev
SCITEX_CLOUD_POSTGRES_USER=scitex_dev
SCITEX_CLOUD_POSTGRES_PASSWORD=scitex_dev_2025

# Redis
SCITEX_CLOUD_REDIS_URL=redis://redis:6379/1

# API Keys
ANTHROPIC_API_KEY=your-key
OPENAI_API_KEY=your-key
```

## URLs

| Service | URL |
|---------|-----|
| Django | http://localhost:8000 |
| Django Admin | http://localhost:8000/admin/ |
| Flower | http://localhost:5555 |
| Gitea | http://localhost:3001 |
