# Environment Variables

Environment-specific configuration for SciTeX Cloud

---

## Files

| File | Purpose |
|------|---------|
| `.env.example` | Template file with all available variables (✅ safe to commit) |
| `setup_env.sh` | Environment setup script (✅ safe to commit) |
| `README.md` | This documentation (✅ safe to commit) |

**All configuration files here are safe to commit** (no secrets - templates only)

---

## Quick Start

**First time setup:**
```bash
# 1. Copy example to SECRET/ directory (gitignored)
cp .env.example ../../SECRET/.env.dev

# 2. Edit with your actual credentials
vim ../../SECRET/.env.dev

# 3. Docker Compose will automatically use SECRET/ files via symlinks
cd ../docker/docker_dev
docker compose up -d
```

---

## Architecture

**Single Source of Truth: `SECRET/` directory**

```
SECRET/                          # ❌ Gitignored (entire directory)
  ├── .env.dev                   # Real secrets for development
  ├── .env.prod                  # Real secrets for production
  └── .env.nas                   # Real secrets for NAS deployment

deployment/envs/
  └── .env.example               # ✅ Template (committed to git)

deployment/docker/
  ├── docker_dev/.env    → ../../../SECRET/.env.dev   (symlink)
  ├── docker_prod/.env   → ../../../SECRET/.env.prod  (symlink)
  └── docker_nas/.env    → ../../../SECRET/.env.nas   (symlink)
```

**Benefits:**
- ✅ Single source of truth for all secrets
- ✅ No risk of committing secrets (entire SECRET/ is gitignored)
- ✅ Docker automatically uses correct environment via symlinks
- ✅ Easy to update: edit files in SECRET/, restart containers

---

## Common Variables

**Database:**
- `SCITEX_CLOUD_DB_NAME`
- `SCITEX_CLOUD_DB_USER`
- `SCITEX_CLOUD_DB_PASSWORD`
- `SCITEX_CLOUD_DB_HOST`
- `SCITEX_CLOUD_DB_PORT`

**Django:**
- `SCITEX_CLOUD_DJANGO_SETTINGS_MODULE`
- `SCITEX_CLOUD_DJANGO_SECRET_KEY`

**Services:**
- `SCITEX_CLOUD_GITEA_URL`
- `SCITEX_CLOUD_GITEA_TOKEN`

---

## Security

- ✅ **DO** keep all secrets in `SECRET/` directory
- ✅ **DO** commit `.env.example` template
- ✅ **DO** use symlinks from docker directories to `SECRET/`
- ❌ **DON'T** commit anything in `SECRET/` (entire directory is gitignored)
- ❌ **DON'T** hardcode passwords in committed files

---

## Updating Configuration

To update environment variables in production:

```bash
# 1. Edit the SECRET file
vim SECRET/.env.prod

# 2. Restart containers to reload
cd deployment/docker/docker_prod
docker compose restart web
```

---

**Location:** `/home/ywatanabe/proj/scitex-cloud/deployment/envs/`

<!-- EOF -->
