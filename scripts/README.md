<!-- ---
!-- Timestamp: 2025-10-18 21:00:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/scripts/README.md
!-- --- -->

# SciTeX Cloud Scripts

This directory contains executable scripts for managing and maintaining the SciTeX Cloud project.

## Environment Management

### `deployment/switch_env.sh`

**Purpose**: Switch between development and production environments using symlinks.

**Usage**:
```bash
# Switch to development
source scripts/deployment/switch_env.sh dev

# Switch to production
source scripts/deployment/switch_env.sh prod

# Check current environment
source scripts/deployment/switch_env.sh
```

**What it does**:
- Creates/updates `.env` symlink to `.env.dev` or `.env.prod`
- Sources environment variables automatically
- Shows current configuration
- Tests database connection
- **Must be sourced** (not executed) to export variables to current shell

**Environment Files**:
- `deployment/dotenvs/dotenv.dev` - Development variables (committed)
- `deployment/dotenvs/dotenv.prod` - Production variables (committed)
- `deployment/dotenvs/dotenv.example` - Template for reference (committed)
- `.env` - Symlink at project root (NOT committed, gitignored)

**See also**: `../deployment/dotenvs/`, `../deployment/docs/01_ENVIRONMENT_VARIABLES.md`

---

## Database Management

### `deployment/setup_postgres.sh`

**Purpose**: Initial PostgreSQL database setup for development and production environments.

**Usage**:
```bash
bash scripts/deployment/setup_postgres.sh
```

**What it does**:
- Creates `scitex_cloud_dev` and `scitex_cloud_prod` databases
- Creates database users (`scitex_dev` and `scitex_prod`)
- Grants necessary permissions
- Enables PostgreSQL extensions (pg_trgm, unaccent)

**Requirements**:
- PostgreSQL installed and running
- sudo access to postgres user

**See also**: `config/deployment/02_POSTGRESQL_SETUP.md`

---

### `deployment/backup_database.sh`

**Purpose**: Automated backup of both PostgreSQL and SQLite databases.

**Usage**:
```bash
# Manual backup
bash scripts/deployment/backup_database.sh

# Automated backup (add to crontab)
0 2 * * * cd /path/to/scitex-cloud && bash scripts/deployment/backup_database.sh >> logs/backup.log 2>&1
```

**What it does**:
- Backs up PostgreSQL databases (dev and prod)
- Backs up SQLite databases (if they exist)
- Compresses backups with gzip
- Removes backups older than 7 days
- Shows backup summary and disk usage

**Output**: `data/db/backups/scitex_cloud_{env}_{timestamp}.sql.gz`

**See also**: `docs/POSTGRESQL_MIGRATION_GUIDE.md`

---

## Server Management

### `server/scitex_server.sh`

**Purpose**: Start/stop/manage the SciTeX Cloud application server.

**Usage**:
```bash
# Start development server
./scripts/server/scitex_server.sh -m dev

# Start production server
./scripts/server/scitex_server.sh -m prod

# Stop server
./scripts/server/scitex_server.sh stop

# Check status
./scripts/server/scitex_server.sh status

# View logs
./scripts/server/scitex_server.sh logs
```

**What it does**:
- Manages uWSGI/Gunicorn server processes
- Handles environment setup
- Manages log files
- Controls server lifecycle

---

## Documentation Generation

### `docs/build_all_docs.sh`

**Purpose**: Build all project documentation.

**Usage**:
```bash
bash scripts/docs/build_all_docs.sh
```

**What it does**:
- Generates API documentation
- Builds module documentation
- Compiles documentation for all apps

---

### `docs/build_module_docs.sh`

**Purpose**: Build documentation for specific modules.

**Usage**:
```bash
bash scripts/docs/build_module_docs.sh [module_name]
```

---

## Utility Scripts

### `utils/format_django_templates.sh`

**Purpose**: Format Django HTML templates for consistency.

**Usage**:
```bash
bash scripts/utils/format_django_templates.sh
```

**What it does**:
- Formats Django templates
- Ensures consistent indentation
- Fixes common formatting issues

---

## Demo & Visualization

### `demo/create_viz_demo.sh`

**Purpose**: Create visualization demonstrations.

**Usage**:
```bash
bash scripts/demo/create_viz_demo.sh
```

---

### `demo/create_viz_demo_video.sh`

**Purpose**: Create video demonstrations of visualizations.

**Usage**:
```bash
bash scripts/demo/create_viz_demo_video.sh
```

---

## Directory Structure

```
scripts/
├── README.md                       # This file
│
├── deployment/                     # Deployment & infrastructure
│   ├── switch_env.sh              # Environment switcher ⭐
│   ├── setup_postgres.sh          # Database setup
│   ├── setup_postgres.sql         # SQL commands
│   ├── backup_database.sh         # Database backups
│   └── configure_nginx_system.sh  # Nginx system config
│
├── server/                         # Server management
│   ├── scitex_server.sh           # Main server control
│   ├── start                      # Legacy start script
│   └── stop                       # Legacy stop script
│
├── dev/                            # Development environment
│   ├── start_dev.sh
│   ├── start_dev_background.sh
│   ├── start_dev_windows.sh
│   └── monitor.sh
│
├── prod/                           # Production environment
│   ├── start_prod.sh
│   ├── deploy_prod.sh
│   └── monitor_prod.sh
│
├── docs/                           # Documentation generation
│   ├── build_all_docs.sh
│   └── build_module_docs.sh
│
├── demo/                           # Demos & visualizations
│   ├── create_viz_demo.sh
│   ├── create_viz_demo_video.sh
│   └── demo.py
│
└── utils/                          # Utilities
    ├── format_django_templates.sh
    ├── format_templates.py
    ├── create_user.py
    ├── reset_database_with_permissions.py
    └── (other utility scripts)
```

## Script Naming Convention

- **Executable scripts**: Use `.sh` extension, make executable with `chmod +x`
- **Python scripts**: Use `.py` extension
- **SQL scripts**: Use `.sql` extension
- **Purpose-based names**: Scripts should have descriptive names indicating their purpose

## Environment Variables

Environment variables come from two sources:

### 1. Global Secrets (Dotfiles)
Loaded automatically by shell from:
- `~/.dotfiles/.bash.d/secrets/001_ENV_SCITEX.src`

Contains sensitive credentials:
```bash
SCITEX_EMAIL_PASSWORD          # Used as Django secret key
SCITEX_SCHOLAR_FROM_EMAIL_*    # Email SMTP config
SCITEX_SCHOLAR_ZENROWS_API_KEY # API keys
# etc.
```

### 2. Project Environment (Symlink)
Loaded by `scripts/deployment/switch_env.sh`:
- `.env` → `deployment/dotenvs/dotenv.dev` or `dotenv.prod`

Contains environment-specific config:
```bash
# Django
DJANGO_SETTINGS_MODULE
SCITEX_CLOUD_DJANGO_SECRET_KEY

# Database
SCITEX_CLOUD_DB_NAME_{DEV|PROD}
SCITEX_CLOUD_DB_USER_{DEV|PROD}
SCITEX_CLOUD_DB_PASSWORD_{DEV|PROD}

# Logging
SCITEX_LOGGING_LEVEL
```

**Why this split?**
- ✅ Global secrets stay in secure dotfiles (never in project)
- ✅ Project configs can be committed (no passwords)
- ✅ Environment switching is simple (`source scripts/switch_env.sh`)

See `../deployment/docs/01_ENVIRONMENT_VARIABLES.md` for complete documentation.

## Adding New Scripts

When adding new scripts:

1. **Create the script** in this directory
2. **Make it executable**: `chmod +x scripts/your_script.sh`
3. **Add documentation** in this README
4. **Add header** to the script:
   ```bash
   #!/bin/bash
   # -*- coding: utf-8 -*-
   # Timestamp: YYYY-MM-DD
   # File: /home/ywatanabe/proj/scitex-cloud/scripts/your_script.sh
   # Description: What this script does
   ```
5. **Test the script** in both dev and prod environments (if applicable)
6. **Document environment variables** if the script requires them

## Best Practices

1. **Error handling**: Use `set -e` to exit on errors
2. **Path independence**: Use `$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)` to get script directory
3. **Colored output**: Use colors for better readability (see `backup_database.sh` for example)
4. **Logging**: Log important operations to `logs/` directory
5. **Idempotency**: Scripts should be safe to run multiple times
6. **Documentation**: Keep this README updated when adding/modifying scripts

## Quick Workflow Examples

### New Developer Setup
```bash
# 1. Clone and setup
git clone https://github.com/ywatanabe1989/scitex-cloud.git
cd scitex-cloud
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Setup database
bash scripts/deployment/setup_postgres.sh

# 3. Switch to dev environment
source scripts/deployment/switch_env.sh dev

# 4. Run Django
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Daily Development
```bash
# Morning: Switch to dev environment
source scripts/deployment/switch_env.sh dev

# Work on features...
python manage.py runserver

# Evening: Backup database
bash scripts/deployment/backup_database.sh
```

### Production Deployment
```bash
# Switch to production
source scripts/deployment/switch_env.sh prod

# Deploy
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart scitex_cloud
```

## Related Documentation

- **Environment Variables**: `../deployment/docs/01_ENVIRONMENT_VARIABLES.md`
- **Deployment**: `../deployment/README.md`
- **Database**: `../docs/POSTGRESQL_MIGRATION_GUIDE.md`
- **Server Management**: `../deployment/nginx/README.md`

<!-- EOF -->
