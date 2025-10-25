<!-- ---
!-- Timestamp: 2025-10-26 00:08:33
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/containers/docker/README.md
!-- --- -->

# SciTeX Cloud - Docker Configuration

## Quick Start

```bash
cd /home/ywatanabe/proj/scitex-cloud/containers/docker

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web
```

## Current Configuration

### Services
- **web**: Django + Gunicorn on **http://localhost:8000**
- **db**: PostgreSQL on **localhost:5433** (container uses 5432)
- **redis**: Redis on localhost:6379

### Important Details
- PostgreSQL uses port **5433** on host (5432 was taken)
- Database connection from containers: `db:5432`
- SciTeX package mounted from `/home/ywatanabe/proj/scitex-code`
- Logs stored in Docker volume (not host directory)
- **Auto-collectstatic runs every 10 seconds** (development only)

## Environment Variables (.env)

Required variables for database connection:
```bash
SCITEX_CLOUD_DB_HOST_DEV=db          # Use 'db', NOT 'localhost'!
SCITEX_CLOUD_DB_PORT_DEV=5432
SCITEX_CLOUD_DB_NAME_DEV=scitex_cloud
SCITEX_CLOUD_DB_USER_DEV=scitex
SCITEX_CLOUD_DB_PASSWORD_DEV=scitex_dev_password
```

## Common Commands

```bash
# Start/stop
docker-compose up -d
docker-compose down

# Rebuild after code changes
docker-compose build web
docker-compose up -d

# Migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# View logs
docker-compose logs -f web
docker-compose logs -f db
```

## Important Notes

1. **After changing `.env`**: Must recreate containers (`down` then `up`), restart won't load new env vars
2. **PostgreSQL from host**: Use port **5433**, not 5432
3. **SciTeX package**: Auto-installed at startup with `pip install --user -e /scitex-code`
4. **Logs**: Stored in Docker volume `/app/logs` (use `docker-compose exec web cat /app/logs/app.log`)
5. **Static files**: Auto-collected every 10 seconds (no manual collectstatic needed in dev)

## Troubleshooting

### Web container keeps restarting
```bash
# Check logs for errors
docker-compose logs --tail=50 web

# Common fixes:
# 1. Check DATABASE_HOST is 'db' not 'localhost' in .env
# 2. Recreate containers: docker-compose down && docker-compose up -d
```

### Port conflicts
```bash
# PostgreSQL: Already configured to use 5433
# Redis/Web: Check with: lsof -i :6379 or lsof -i :8000
```

## Detailed Documentation

- Development details: [README_DEV.md](./README_DEV.md)
- Production deployment: [README_PROD.md](./README_PROD.md)
- Quick reference: [../../DOCKER_QUICKSTART.md](../../DOCKER_QUICKSTART.md)

<!-- EOF -->