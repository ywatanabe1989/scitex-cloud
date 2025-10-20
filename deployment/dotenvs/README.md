# Environment Variables

Environment-specific configuration for SciTeX Cloud

---

## Files

| File | Purpose |
|------|---------|
| `dotenv.dev` | Development environment |
| `dotenv.prod` | Production environment |
| `setup_env.sh` | Environment setup script |

**All files are safe to commit** (no secrets - references only)

---

## Quick Start

```bash
# Setup environment (creates symlink and loads vars)
source ./setup_env.sh

# Manual sourcing
source dotenv.dev    # or dotenv.prod
```

---

## Architecture

**Two-layer approach:**

1. **Global secrets** (from `~/.dotfiles/.bash.d/secrets/`)
   - API keys, passwords, credentials
   - Loaded automatically by shell

2. **Project config** (this directory)
   - References secrets via `${VARIABLE}`
   - Database settings, Django config
   - Safe to commit

```bash
# Example: dotenv.dev
export SCITEX_CLOUD_DJANGO_SECRET_KEY="${SCITEX_EMAIL_PASSWORD}"  # Reference
export SCITEX_CLOUD_DB_NAME=scitex_cloud_dev                       # Safe config
```

---

## Common Variables

**Database:**
- `SCITEX_CLOUD_DB_NAME`
- `SCITEX_CLOUD_DB_USER`
- `SCITEX_CLOUD_DB_PASSWORD`
- `SCITEX_CLOUD_DB_HOST`
- `SCITEX_CLOUD_DB_PORT`

**Django:**
- `DJANGO_SETTINGS_MODULE`
- `SCITEX_CLOUD_DJANGO_SECRET_KEY`

**Services:**
- `SCITEX_CLOUD_GITEA_URL`
- `SCITEX_CLOUD_GITEA_TOKEN`

---

## Security

- ✅ **DO** commit these dotenv files (no secrets)
- ✅ **DO** use `${VAR}` to reference secrets
- ❌ **DON'T** hardcode passwords
- ❌ **DON'T** commit `.env` symlink at project root

---

**Location:** `/home/ywatanabe/proj/scitex-cloud/deployment/dotenvs/`

<!-- EOF -->
