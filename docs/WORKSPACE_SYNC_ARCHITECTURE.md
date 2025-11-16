# SciTeX Cloud Workspace Sync Architecture

**Last Updated:** 2025-11-15
**Status:** Active

## Overview

This document describes the clean, user-centric architecture for workspace synchronization in SciTeX Cloud.

## Architecture Diagram

```
┌─────────────────┐
│  User's Local   │  ← User works here
│    Machine      │
└────────┬────────┘
         │
         │ scitex cloud push/pull/clone
         │ (Manual, user-controlled)
         ↓
┌─────────────────┐
│   Workspace     │  ← User edits files here (web/SSH)
│ (Cloud Storage) │
└────────┬────────┘
         │
         │ Internal sync (invisible to user)
         ↓
┌─────────────────┐
│     Gitea       │  ← Implementation detail
│ (Git Repository)│     Users don't see this
└─────────────────┘

+ Rsync Snapshots (every 5 min, disaster recovery)
```

## Key Principles

### 1. User Mental Model

**What users understand:**
- Local machine (their laptop)
- Workspace (cloud files they can edit)
- `scitex cloud` commands to sync between them

**What users DON'T need to know:**
- Gitea exists
- Git operations happening internally
- Backup mechanisms

### 2. Clear Separation

| Location | Purpose | Commands |
|----------|---------|----------|
| **Local Machine** | User's laptop | `scitex cloud push/pull/clone` |
| **Workspace** | Cloud dev environment | Regular `git` commands or just edit files |
| **Gitea** | Internal version control | Hidden from users |

## Synchronization Systems

### System 1: Manual Git Sync (User-Controlled)

**Purpose:** Clean version control history

**Workflow:**

```bash
# From LOCAL machine
laptop$ scitex cloud push    # Push local → workspace
laptop$ scitex cloud pull    # Pull workspace → local

# Inside WORKSPACE
workspace$ vim analysis.py    # Edit files
workspace$ git add .          # Optional: manual git
workspace$ git commit -m "msg"
workspace$ git push origin main
# OR just edit files - backups handle safety
```

**Benefits:**
- ✅ Users control when to sync
- ✅ Clean Git history (meaningful commits only)
- ✅ No dirty commits during editing
- ✅ No background merge conflicts

### System 2: Automatic Backups (Transparent)

**Purpose:** Disaster recovery

**Implementation:**
- Simple `rsync` file copies (NOT Git)
- Runs every 5 minutes via cron
- Keeps last 24 hours (288 snapshots)
- Admin-only access

**Benefits:**
- ✅ No Git conflicts
- ✅ Works while user is editing
- ✅ Invisible to users
- ✅ Simple and reliable

**Script:** `scripts/backup_workspaces.sh`

## Command Behavior

### `scitex cloud` Commands

**MUST run from LOCAL machine only:**

```bash
# ✅ Correct: Run from laptop
laptop$ scitex cloud push
📤 Pushing to workspace...
✓ Pushed to workspace (origin/main)

# ❌ Error: Run from workspace
workspace$ scitex cloud push
❌ Error: You are inside a SciTeX workspace!

The 'scitex cloud' commands are for your LOCAL machine
to interact with your cloud workspace.

Inside the workspace, use regular git commands:
  git status
  git add .
  git commit -m 'msg'
  git push origin main

💡 Or just edit and save files - automatic backups
   run every 5 minutes for disaster recovery!
```

### Inside Workspace

Users can:
1. **Just edit files** - Automatic backups every 5 min
2. **Use regular Git** - Full control over commits
3. **Use web IDE** - Edit directly in browser

Users should NOT:
- ❌ Run `scitex cloud` commands (throws error)

## Why This Architecture?

### Problems with Auto-Git-Sync (Old Approach)

**Issue 1: Dirty Commits**
```
09:00:00 - User editing file.py...
09:05:00 - Auto-sync commits incomplete file!
09:05:10 - User saves complete version (too late)
```

**Issue 2: Polluted History**
```
commit abc123 - "Auto-sync 09:00" ← debugging
commit def456 - "Auto-sync 09:05" ← still broken
commit ghi789 - "Auto-sync 09:10" ← trial and error
```

**Issue 3: Background Conflicts**
```
User A: Auto-sync at 09:05
User B: Auto-sync at 09:07 → ❌ Conflict!
         (No user available to resolve)
```

### Solution: Separate Concerns

| Need | Solution | Method |
|------|----------|--------|
| Version control | Manual Git sync | `scitex cloud push/pull` |
| Disaster recovery | Auto backups | `rsync` snapshots |

## File Structure

```
/app/data/users/
├── alice/
│   ├── project-001/        ← Workspace files
│   └── project-002/
└── bob/
    └── default-project/

/app/backups/snapshots/
├── alice_project-001_20251115_090000/
├── alice_project-001_20251115_090500/  ← Every 5 min
├── alice_project-001_20251115_091000/
...
└── (keeps last 24 hours)
```

## Configuration

### Environment Variables

```bash
# Workspace root
SCITEX_WORKSPACE_ROOT=/app/data/users

# Backup configuration
SCITEX_BACKUP_ROOT=/app/backups/snapshots
SCITEX_MAX_SNAPSHOTS=288  # 24 hours at 5-min intervals
```

### Cron Setup

```bash
# Install cron job
sudo cp deployment/docker/common/cron/workspace-backups /etc/cron.d/
sudo systemctl restart cron

# Verify
sudo crontab -l
```

## User Workflows

### Workflow 1: Work on Laptop

```bash
# Clone workspace to laptop
laptop$ scitex cloud clone myproject

# Edit files locally
laptop$ vim analysis.py
laptop$ git add analysis.py
laptop$ git commit -m "Add new analysis"

# Push to workspace
laptop$ scitex cloud push
```

### Workflow 2: Work in Workspace

```bash
# SSH into workspace
laptop$ ssh workspace.scitex.cloud

# Edit files in workspace
workspace$ vim analysis.py

# Option A: Manual git (clean commits)
workspace$ git add .
workspace$ git commit -m "Analysis complete"
workspace$ git push origin main

# Option B: Do nothing (auto-backup handles it)
workspace$ # Just save and close
```

### Workflow 3: Sync Between Locations

```bash
# Work in workspace
workspace$ vim analysis.py
workspace$ git commit -am "Work in progress"
workspace$ git push origin main

# Later, on laptop
laptop$ scitex cloud pull
📥 Pulling from workspace...
✓ Pulled from workspace (origin/main)
```

## Disaster Recovery

### Restore from Snapshot

```bash
# List available snapshots
ls /app/backups/snapshots/alice_project-001_*

# Restore to specific timestamp
rsync -a /app/backups/snapshots/alice_project-001_20251115_090000/ \
         /app/data/users/alice/project-001/
```

### Backup Rotation

- Snapshots older than 24 hours are automatically deleted
- Adjust `SCITEX_MAX_SNAPSHOTS` to keep more/less history
- For long-term backups, copy snapshots elsewhere

## Migration from Old Architecture

### Before (Auto-Git-Sync)
```bash
# Background daemon running
python manage.py auto_sync_workspaces --daemon

# Polluted Git history
commit 123 - "Auto-sync 09:00"
commit 456 - "Auto-sync 09:05"
commit 789 - "Auto-sync 09:10"
```

### After (Manual Sync + Rsync Backups)
```bash
# No background daemon
# Clean Git history
commit abc - "Implement analysis"
commit def - "Fix bug in preprocessing"
commit ghi - "Add visualization"

# Backups are separate
/app/backups/snapshots/*
```

## Monitoring

### Check Backup Status

```bash
# View backup logs
tail -f /app/logs/workspace-backups.log

# Count recent snapshots
ls -1 /app/backups/snapshots/ | grep $(date +%Y%m%d) | wc -l

# Check disk usage
du -sh /app/backups/snapshots/
```

### Alerts

Monitor:
- Backup script failures
- Disk space usage
- Missing snapshots (indicates backup not running)

## FAQ

**Q: What if I forget to push from workspace?**
A: Rsync snapshots run every 5 minutes. Your work is safe even if you forget to commit.

**Q: Can I use `scitex cloud` inside workspace?**
A: No, it will show a clear error message guiding you to use regular `git` commands.

**Q: How do I recover deleted files?**
A: Use rsync snapshots from `/app/backups/snapshots/` (admin access required).

**Q: Do snapshots include .git directories?**
A: No, snapshots exclude `.git/`, `__pycache__/`, `node_modules/`, etc.

**Q: What about Gitea?**
A: Gitea is an internal implementation detail. Users interact with "workspace" - Gitea is transparent.

## References

- Auto-sync removal: `apps/workspace_app/management/commands/auto_sync_workspaces.py`
- Backup script: `scripts/backup_workspaces.sh`
- Cloud commands: `/home/ywatanabe/proj/scitex-code/src/scitex/cli/cloud.py`

---

**Architecture approved:** 2025-11-15
**Implementation:** Complete
**Status:** Production-ready
