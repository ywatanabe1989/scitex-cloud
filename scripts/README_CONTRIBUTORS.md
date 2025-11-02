# Contributors Sync

This directory contains scripts for syncing GitHub contributors to the database.

## Quick Start

### Sync from Organization (Recommended)

This syncs all contributors across all SciTeX repositories:

```bash
# Sync all contributors from SciTeX organization
./scripts/sync_contributors_org.sh

# Sync from a different organization
./scripts/sync_contributors_org.sh other-org-name
```

### Sync from Single Repository

```bash
# Sync contributors from one repository
./scripts/sync_contributors.sh

# Sync from a different repository
./scripts/sync_contributors.sh owner/repo-name
```

## What it does

### Organization Sync (`sync_contributors_org.sh`)

1. Fetches all repositories from the SciTeX organization using `gh` CLI
2. Collects contributors from each repository
3. Aggregates total contributions per user across all repositories
4. Automatically assigns roles based on total contribution count:
   - **Creator**: ywatanabe1989 (hardcoded)
   - **Core Team**: 100+ contributions across all repos
   - **Maintainer**: 50-99 contributions
   - **Contributor**: Less than 50 contributions
5. Updates the database with aggregated contributor information
6. Shows which repositories each contributor has worked on
7. Displays contributors on the website at `/contributors/`

### Single Repository Sync (`sync_contributors.sh`)

1. Fetches contributors from one specific GitHub repository
2. Updates contribution counts for that repository only
3. Same role assignment logic as organization sync

## Requirements

- GitHub CLI (`gh`) installed and authenticated
- Docker Compose (for running Django commands)
- Access to the GitHub repository

## Using Django Management Command

You can also use the Django management command directly:

```bash
# Dry run (preview changes without saving)
make ENV=dev shell
python manage.py sync_github_contributors --dry-run

# Actual sync
python manage.py sync_github_contributors

# Sync a different repository
python manage.py sync_github_contributors --repo owner/repo-name
```

Note: The management command requires `gh` CLI to be available inside the Docker container.

## Manual Management

Contributors can also be managed through Django Admin:

1. Go to http://127.0.0.1:8000/admin/
2. Navigate to Public App → Contributors
3. Add, edit, or remove contributors manually

## Automation

To automatically sync contributors on a schedule:

### Option 1: Cron Job (Recommended)

Add to your crontab:

```bash
# Sync all organization contributors daily at 2 AM
0 2 * * * cd /home/ywatanabe/proj/scitex-cloud && ./scripts/sync_contributors_org.sh >> /home/ywatanabe/proj/scitex-cloud/logs/contributors_sync.log 2>&1
```

### Option 2: GitHub Actions

Create `.github/workflows/sync-contributors.yml`:

```yaml
name: Sync Contributors

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:  # Allow manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Sync Contributors
        run: ./scripts/sync_contributors.sh
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Troubleshooting

### "gh: command not found"

Install GitHub CLI:

```bash
# Ubuntu/Debian
sudo apt install gh

# macOS
brew install gh

# Authenticate
gh auth login
```

### Docker issues

Make sure Docker containers are running:

```bash
make ENV=dev status
make ENV=dev start
```

### Permission denied

Make sure the script is executable:

```bash
chmod +x ./scripts/sync_contributors.sh
```
