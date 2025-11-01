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
- Password: `Test-user!`

## Environment Variables

Uses `SECRET/.env.dev` (symlinked to `.env`).

## Features

- Live code reloading (no rebuild needed for Python changes)
- Django DEBUG mode enabled
- Volume mounts for development
- Auto-created test user
- Gitea integration
