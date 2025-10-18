<!-- ---
!-- Timestamp: 2025-10-18 21:56:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/deployment/dotenvs/README.md
!-- --- -->

# Environment Variable Files

This directory contains environment-specific configuration files for SciTeX Cloud.

## Files

- **`dotenv.dev`** - Development environment variables (committed)
- **`dotenv.prod`** - Production environment variables (committed)
- **`dotenv.example`** - Template showing all available variables (committed)

## How It Works

### Symlink Strategy

The project root has a `.env` symlink that points to one of these files:

```
scitex-cloud/
├── .env  → deployment/dotenvs/dotenv.dev   (or dotenv.prod)
└── deployment/
    └── dotenvs/
        ├── dotenv.dev      ✅ committed
        ├── dotenv.prod     ✅ committed
        └── dotenv.example  ✅ committed
```

### Switching Environments

```bash
# Switch to development
source scripts/deployment/switch_env.sh dev

# Switch to production
source scripts/deployment/switch_env.sh prod
```

The script:
1. Updates the `.env` symlink
2. Sources the environment file
3. Shows current configuration
4. Tests database connection

## Why This Organization?

### ✅ Advantages

1. **Clean separation**: Deployment configs grouped together
2. **Clear naming**: `dotenv.*` clearly indicates purpose
3. **Safe to commit**: No secrets in these files
4. **Team-friendly**: Everyone uses same config files
5. **Easy to find**: All dotenvs in one place

### Security Model

**Secrets come from dotfiles:**
```bash
# ~/.dotfiles/.bash.d/secrets/001_ENV_SCITEX.src
SCITEX_EMAIL_PASSWORD="actual_secret"
SCITEX_SCHOLAR_ZENROWS_API_KEY="actual_api_key"
```

**Config comes from project:**
```bash
# deployment/dotenvs/dotenv.dev
SCITEX_CLOUD_DJANGO_SECRET_KEY="${SCITEX_EMAIL_PASSWORD}"  # Reference
SCITEX_CLOUD_DB_NAME_DEV=scitex_cloud_dev  # Safe to commit
```

## Environment Variables Hierarchy

1. **Global secrets** (from `~/.dotfiles/`) - Always loaded by shell
   - API keys
   - Email passwords
   - Service credentials

2. **Environment-specific** (from this directory) - Loaded by switch script
   - Database configuration
   - Django settings module
   - Logging levels
   - Feature flags

## File Format

All files are bash scripts that export environment variables:

```bash
#!/bin/bash
# Comments explaining the variable
export VARIABLE_NAME=value
export ANOTHER_VAR="${REFERENCE_FROM_DOTFILES}"
```

## Adding New Variables

1. Add to `dotenv.example` with documentation
2. Add to `dotenv.dev` with dev value
3. Add to `dotenv.prod` with prod value
4. Document in `../docs/01_ENVIRONMENT_VARIABLES.md`

## Important Notes

### ⚠️ Security

- **DO commit** `dotenv.{dev,prod,example}` - they contain no secrets
- **DO NOT commit** `.env` symlink at project root - it's gitignored
- **DO use** `${VARIABLE}` syntax to reference dotfile secrets
- **DO NOT** hardcode passwords in these files

### 📝 Best Practices

1. Use descriptive variable names with `SCITEX_CLOUD_` prefix
2. Group related variables with comments
3. Reference dotfile secrets, don't duplicate them
4. Keep examples in `dotenv.example` up to date

### 🔍 Verification

Check current environment:
```bash
# Show current symlink
ls -la .env

# Show loaded variables
source scripts/deployment/switch_env.sh
```

## Environment Variables Reference

For complete documentation on all available environment variables, including naming conventions and security best practices, see the deployment documentation.

### Quick Reference

**Database Configuration:**
- `SCITEX_CLOUD_DB_NAME_{DEV|PROD}`
- `SCITEX_CLOUD_DB_USER_{DEV|PROD}`
- `SCITEX_CLOUD_DB_PASSWORD_{DEV|PROD}`
- `SCITEX_CLOUD_DB_HOST_{DEV|PROD}`
- `SCITEX_CLOUD_DB_PORT_{DEV|PROD}`
- `SCITEX_CLOUD_USE_SQLITE_{DEV|PROD}`

**Django Configuration:**
- `DJANGO_SETTINGS_MODULE`
- `SCITEX_CLOUD_DJANGO_SECRET_KEY`

**Logging:**
- `SCITEX_LOGGING_LEVEL` (debug, info, warning, error)

**Global SciTeX Variables (from dotfiles):**
- `SCITEX_EMAIL_PASSWORD`
- `SCITEX_EMAIL_ADMIN`
- `SCITEX_SCHOLAR_FROM_EMAIL_ADDRESS`

## See Also

- `../../scripts/deployment/switch_env.sh` - Environment switcher script
- `~/.dotfiles/.bash.d/secrets/001_ENV_SCITEX.src` - Global secrets

<!-- EOF -->
