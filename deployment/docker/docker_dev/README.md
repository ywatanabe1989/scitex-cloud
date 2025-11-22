# Docker Development Environment

Development environment with hot-reload and debugging tools.

## Quick Start

```bash
# Full setup (first time)
make -f Makefile.dev start

# Quick restart (after code changes)
make -f Makefile.dev restart

# Stop all
make -f Makefile.dev down
```

## Services

- **Django** - http://localhost:8000
- **Gitea** - http://localhost:3000
- **PostgreSQL** - localhost:5433
- **Redis** - localhost:6379

## Common Commands

```bash
# Django
make -f Makefile.dev migrate          # Run migrations
make -f Makefile.dev shell            # Django shell
make -f Makefile.dev collectstatic    # Collect static files

# Database
make -f Makefile.dev db-shell         # PostgreSQL shell
make -f Makefile.dev db-reset         # Reset database (⚠️ deletes all data)

# Logs
make -f Makefile.dev logs             # All services
make -f Makefile.dev logs-web         # Web only
make -f Makefile.dev logs-gitea       # Gitea only

# Gitea
make -f Makefile.dev gitea-token      # Setup API token
make -f Makefile.dev recreate-testuser # Recreate test user

# Help
make -f Makefile.dev help             # Show all commands
```

## Test User

- Username: `test-user`
- Password: `Password123!`

### Quick Setup (Django Only)

For quick test user setup without Gitea integration:

```bash
# Via root Makefile
make ENV=dev shell
python manage.py init_test_user

# Or directly via Docker
docker exec scitex-cloud-dev-web-1 python manage.py init_test_user

# Custom credentials
docker exec scitex-cloud-dev-web-1 python manage.py init_test_user \
    --username="my-user" \
    --password="MyPassword123!" \
    --email="my@example.com"
```

### Full Setup (Django + Gitea Integration)

For testing the complete Django-to-Gitea synchronization pipeline:

```bash
# Via root Makefile
make ENV=dev recreate-testuser

# Or via docker Makefile
cd deployment/docker/docker_dev
make recreate-testuser
```

This will:
1. Delete test user from Django (triggers Gitea deletion via signal)
2. Verify deletion from Gitea API
3. Create test user in Django (triggers Gitea creation via signal)
4. Verify creation in both Django and Gitea
5. Set up SSH keys for the user

## Environment Variables

Uses `SECRET/.env.dev` (symlinked to `.env`).

## Features

- Live code reloading (no rebuild needed for Python changes)
- Django DEBUG mode enabled
- Volume mounts for development
- Auto-created test user
- Gitea integration
