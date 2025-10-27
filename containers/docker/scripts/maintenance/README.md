<!-- ---
!-- Timestamp: 2025-10-27 06:59:01
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/containers/docker/scripts/maintenance/README.md
!-- --- -->

# Docker Maintenance Scripts

Docker Compose-specific maintenance scripts for SciTeX Cloud development.

## Scripts

### Status Checks

```bash
./containers/docker/scripts/maintenance/gitea_check_status.sh      # Gitea: container, API, auth, resources
./containers/docker/scripts/maintenance/postgres_check_status.sh   # PostgreSQL: container, DB, connections
./containers/docker/scripts/maintenance/django_check_status.sh     # Django: container, web, migrations
```

### Resource Listing

```bash
# Users
./containers/docker/scripts/maintenance/gitea_list_users.sh                  # List all
./containers/docker/scripts/maintenance/gitea_list_users.sh --search query   # Search
./containers/docker/scripts/maintenance/gitea_list_users.sh --detail user    # Details
./containers/docker/scripts/maintenance/gitea_list_users.sh --admins         # Admins only

# Repositories
./containers/docker/scripts/maintenance/gitea_list_repositories.sh              # List all
./containers/docker/scripts/maintenance/gitea_list_repositories.sh --user name  # By user
./containers/docker/scripts/maintenance/gitea_list_repositories.sh --detail owner/repo
./containers/docker/scripts/maintenance/gitea_list_repositories.sh --private    # Private only
```

## Environment

Scripts load from `.env`:
```bash
SCITEX_CLOUD_GITEA_URL_DEV=http://127.0.0.1:3000
SCITEX_CLOUD_GITEA_TOKEN_DEV=<token>
SCITEX_CLOUD_HTTP_PORT_DEV=8000
POSTGRES_USER=scitex_dev
POSTGRES_DB=scitex_cloud_dev
```

## Troubleshooting

**Container not found:**
```bash
./containers/docker/start_dev.sh -a start
```

**Invalid token:**
1. Generate at http://localhost:3000 → Settings → Applications
2. Update `SCITEX_CLOUD_GITEA_TOKEN_DEV` in `.env`
3. `./containers/docker/start_dev.sh -a restart`

**Logs:**
```bash
cat .gitea_check_status.sh.log
tail -f .django_check_status.sh.log
```

## See Also

- `./containers/docker/start_dev.sh` - Startup (auto-runs verification)
- `./scripts/README_GITEA_SETUP.md` - Gitea setup guide

<!-- EOF -->