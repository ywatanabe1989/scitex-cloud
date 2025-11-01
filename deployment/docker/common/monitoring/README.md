# Maintenance Scripts

Health check and status scripts for SciTeX Cloud services.

## Scripts

- `django_check_status.sh` - Django application health
- `postgres_check_status.sh` - PostgreSQL database health
- `gitea_check_status.sh` - Gitea service health
- `gitea_list_users.sh` - List all Gitea users
- `gitea_list_repositories.sh` - List all Gitea repositories

## Usage

```bash
# From inside container
./django_check_status.sh
./postgres_check_status.sh
./gitea_check_status.sh

# From host
docker exec docker-web-1 /app/common/scripts/maintenance/django_check_status.sh
docker exec docker-db-1 /app/common/scripts/maintenance/postgres_check_status.sh
docker exec docker-gitea-1 /app/common/scripts/maintenance/gitea_check_status.sh
```

## Environment Variables

Scripts load from `.env`:
- `SCITEX_CLOUD_GITEA_URL_DEV`
- `SCITEX_CLOUD_GITEA_TOKEN_DEV`
- `POSTGRES_USER`, `POSTGRES_DB`
