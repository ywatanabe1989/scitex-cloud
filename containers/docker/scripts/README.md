# Docker Scripts

This directory contains scripts specifically designed for Docker Compose-based development.

## Directory Structure

```
scripts/
├── maintenance/          # Docker-specific maintenance scripts
│   ├── README.md        # Detailed documentation
│   ├── gitea_check_status.sh
│   ├── gitea_list_users.sh
│   ├── gitea_list_repositories.sh
│   ├── postgres_check_status.sh
│   └── django_check_status.sh
└── README.md           # This file
```

## Quick Start

### Check All Services

```bash
cd scripts/maintenance

# Check each service
./gitea_check_status.sh
./postgres_check_status.sh
./django_check_status.sh
```

### List Gitea Resources

```bash
cd scripts/maintenance

# List users
./gitea_list_users.sh

# List repositories
./gitea_list_repositories.sh

# Get user details
./gitea_list_users.sh --detail username

# Get repository details
./gitea_list_repositories.sh --detail owner/repo
```

## Maintenance Scripts

See [`maintenance/README.md`](maintenance/README.md) for comprehensive documentation of all maintenance scripts.

### Available Scripts

1. **`gitea_check_status.sh`** - Check Gitea container, API, and authentication
2. **`gitea_list_users.sh`** - List and search Gitea users
3. **`gitea_list_repositories.sh`** - List and search repositories
4. **`postgres_check_status.sh`** - Check PostgreSQL database status
5. **`django_check_status.sh`** - Check Django application status

## Design Principles

### Docker-Native

All scripts use `docker-compose` commands and Docker API:
```bash
docker-compose -f docker-compose.dev.yml ps
docker logs container_name
docker stats container_name
```

### Environment-Aware

Scripts automatically load configuration from project `.env`:
```bash
# Load environment
if [ -f "$GIT_ROOT/.env" ]; then
    set -a
    source "$GIT_ROOT/.env"
    set +a
fi
```

### Self-Contained

No external dependencies beyond:
- Docker and Docker Compose
- Standard Unix tools (curl, grep, sed, awk)
- Python 3 (for JSON parsing)

### Informative Output

Color-coded status indicators:
- 🟢 Green: Success
- 🟡 Yellow: Warning
- 🔴 Red: Error
- ⚪ Gray: Info

### Logged

All outputs saved to `.log` files for troubleshooting:
```bash
.gitea_check_status.sh.log
.gitea_list_users.sh.log
# etc.
```

## Comparison: Docker vs Deployment Scripts

| Aspect | Docker Scripts | Deployment Scripts |
|--------|---------------|-------------------|
| **Location** | `containers/docker/scripts/` | `deployment/*/scripts/` |
| **Environment** | Docker Compose | systemd/uwsgi |
| **Execution** | Direct (`./script.sh`) | Via Docker exec or system |
| **Complexity** | Simple, single-service | Complex, multi-service |
| **Safety** | High (containers) | Lower (system-wide) |
| **Portability** | Any Docker host | Specific Linux distro |
| **Use Case** | Development | Production |

## Integration

### With `start_dev.sh`

The startup script automatically runs verifications:

```bash
cd containers/docker
./start_dev.sh -a start
```

This internally calls:
- `verify_gitea_api()` - Validates Gitea API
- `create_gitea_users()` - Creates test users

### With Project Root Scripts

These complement the scripts in `$PROJECT_ROOT/scripts/`:

| Project Root | Docker Scripts |
|-------------|---------------|
| `check_gitea_api.py` | `gitea_check_status.sh` |
| `test_repo_creation.py` | `gitea_list_repositories.sh` |
| `sync_django_gitea_users.py` | `gitea_list_users.sh` |

## Common Workflows

### Daily Development Checks

```bash
cd containers/docker/scripts/maintenance

# Morning health check
./django_check_status.sh
./gitea_check_status.sh
./postgres_check_status.sh
```

### User Management

```bash
cd containers/docker/scripts/maintenance

# List all users
./gitea_list_users.sh

# Check specific user
./gitea_list_users.sh --detail username

# Sync Django → Gitea
cd ../../..
docker-compose -f containers/docker/docker-compose.dev.yml exec -T web \
    python /app/scripts/sync_django_gitea_users.py
```

### Repository Operations

```bash
cd containers/docker/scripts/maintenance

# List repositories
./gitea_list_repositories.sh

# Check repository details
./gitea_list_repositories.sh --detail owner/repo

# List user's repositories
./gitea_list_repositories.sh --user username
```

### Database Maintenance

```bash
cd containers/docker/scripts/maintenance

# Check database
./postgres_check_status.sh

# Access psql
cd ../..
docker-compose -f docker-compose.dev.yml exec db \
    psql -U scitex_dev -d scitex_cloud_dev

# Backup
docker-compose -f docker-compose.dev.yml exec db \
    pg_dump -U scitex_dev scitex_cloud_dev > backup.sql
```

## Troubleshooting

### Common Issues

1. **"Container not found"**
   ```bash
   cd containers/docker
   ./start_dev.sh -a start
   ```

2. **"Connection refused"**
   ```bash
   docker ps | grep gitea
   docker logs docker_gitea_1
   ```

3. **"Invalid token"**
   - Generate new token at http://localhost:3000
   - Update `SCITEX_CLOUD_GITEA_TOKEN_DEV` in `.env`

4. **"Database connection failed"**
   ```bash
   cd containers/docker
   docker-compose -f docker-compose.dev.yml down -v
   ./start_dev.sh -a start
   ```

### Debug Mode

View detailed logs:
```bash
cd scripts/maintenance
cat .gitea_check_status.sh.log
tail -f .django_check_status.sh.log
```

## Best Practices

1. **Always run from script directory**
   ```bash
   cd containers/docker/scripts/maintenance
   ./script.sh
   ```

2. **Check logs after failures**
   ```bash
   cat .script_name.sh.log
   ```

3. **Use help flags**
   ```bash
   ./gitea_list_users.sh --help
   ```

4. **Combine with Docker commands**
   ```bash
   ./gitea_check_status.sh && docker logs docker_gitea_1
   ```

5. **Run periodic health checks**
   ```bash
   # Add to cron or run periodically
   */30 * * * * cd /path/to/containers/docker/scripts/maintenance && ./django_check_status.sh > /tmp/status.txt
   ```

## See Also

- [`maintenance/README.md`](maintenance/README.md) - Detailed maintenance scripts documentation
- [`../start_dev.sh`](../start_dev.sh) - Docker Compose startup script
- [`../README_DEV.md`](../README_DEV.md) - Docker development guide
- [`../../scripts/README_GITEA_SETUP.md`](../../scripts/README_GITEA_SETUP.md) - Gitea setup guide
- [`../../deployment/`](../../deployment/) - Production deployment scripts
