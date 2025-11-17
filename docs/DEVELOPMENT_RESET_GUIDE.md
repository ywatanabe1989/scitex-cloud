# Development Reset Guide

Quick reference for resetting your development environment.

## 🚀 Quick Start - Full Reset

**Recommended for most cases:**

```bash
make ENV=dev fresh-start
```

**Before deletion, shows you:**
- Current number of users, projects, manuscripts
- Database size (e.g., 82.6M)
- Number of Gitea repositories
- Gitea volume size
- User files total size (e.g., 5.8G)
- Number of user directories

**Then it will:**
- ✅ Stop all containers
- ✅ Delete database volumes (PostgreSQL)
- ✅ Delete Gitea volumes
- ✅ Clean `./data/users/*` directory
- ✅ Clean log files
- ✅ Restart with fresh database
- ✅ Run migrations
- ✅ Initialize visitor pool (4 accounts)

**Safety**:
- Shows exact current state before deletion
- Requires typing `DELETE EVERYTHING` to confirm
- Will ask for sudo password (needed to delete Docker-created files)

---

## 🔍 What Gets Deleted vs Preserved

### ❌ DELETED (Data Only)
- Database tables and all records
- User-generated files in `./data/users/`
- Gitea repositories (Git data)
- Docker volumes (postgres_data, gitea_data)
- Log files

### ✅ PRESERVED (Code & Config)
- Source code (all Python, TypeScript, HTML)
- Docker images (won't need to rebuild)
- Configuration files (.env, settings.py)
- Static assets (CSS, JS, templates)
- Python packages (.venv)
- Your Git repository (scitex-cloud itself)
- Makefile and scripts

**In short:** Only runtime data is deleted. Your development environment setup stays intact.

---

## 📋 Reset Options

### 1. Complete Fresh Start (Recommended)

```bash
make ENV=dev fresh-start
```

**Use when:**
- You want a completely clean development environment
- Gitea data is corrupted or needs reset
- Database migrations are causing issues
- You want to test the setup from scratch

**Resets:**
- Database (all tables)
- Gitea (repos + volume data)
- User files (`./data/users/*`)
- Logs

---

### 2. Quick Fresh Start (For Scripts/Automation)

```bash
make ENV=dev fresh-start-confirm
```

**Use when:**
- Running in automated scripts
- You're absolutely sure (no confirmation prompt)

**⚠️ Warning:** No confirmation - use with caution!

---

### 3. Partial Reset (Django Data Only)

```bash
./scripts/utils/reset_all_data.sh --confirm --delete-directories
```

**Use when:**
- You only need to reset Django data
- Want to keep Gitea database intact
- Need more granular control

**Options:**
- `--dry-run` - Preview what will be deleted
- `--confirm` - Actually delete
- `--keep-users` - Only delete projects
- `--delete-directories` - Also delete project directories

**Resets:**
- Django projects
- Django users (except superusers)
- Gitea repositories (via API)
- Optionally: project directories

**Does NOT reset:**
- Gitea database tables
- Gitea volume data

---

### 4. Database Only Reset

```bash
make ENV=dev db-reset
```

**Use when:**
- You only need to reset the database
- Want to keep files intact

---

## 🔄 Comparison Table

| Command | Database | Gitea Volume | User Files | Gitea Repos | Time |
|---------|----------|--------------|------------|-------------|------|
| `make ENV=dev fresh-start` | ✅ Full | ✅ Yes | ✅ Yes | ✅ Yes | ~30s |
| `./scripts/utils/reset_all_data.sh --confirm` | ✅ Django only | ❌ No | ⚠️ Optional | ✅ Yes | ~15s |
| `make ENV=dev db-reset` | ✅ Full | ❌ No | ❌ No | ❌ No | ~10s |

## 📝 After Reset

After any fresh start, you'll typically want to:

1. **Create a superuser:**
   ```bash
   make ENV=dev createsuperuser
   ```

2. **Access the services:**
   - Django dev server: http://localhost:8000
   - Gitea: http://localhost:3001

3. **Verify visitor pool:**
   - Check that 4 visitor accounts are ready (rotated automatically)
   - Test anonymous user flow

## 🔍 Troubleshooting

### "Container not found" error
The container might not be running. Try:
```bash
make ENV=dev start
```

### "Volume is in use" error
Stop all containers first:
```bash
make stop-all
```

### Docker build permission errors
If you see errors like:
```
open /home/.../data/ssh_keys/user_301: permission denied
```

**Cause**: Docker is trying to copy `./data/` directory which contains root-owned files.

**Solution**: Already fixed in `.dockerignore`. If you still see this:
1. Check `.dockerignore` includes `data/` and `logs/`
2. Make sure you're building from project root
3. Try: `make env=dev rebuild`

### Permission denied on `./data/users/`
Files in `./data/users/` are created by Docker containers running as root.

**Solution**: The `fresh-start` command now automatically uses sudo.
- You'll be prompted for your password during the cleanup step
- This is normal and expected

If you need to clean manually:
```bash
sudo rm -rf ./data/users/*
```

## 💡 Best Practices

1. **Before major changes:** Run `fresh-start` to ensure clean state
2. **Testing migrations:** Use `fresh-start` to test from clean DB
3. **Daily development:** Usually just `restart` is enough
4. **After git pull:** If migrations changed, consider `fresh-start`

## ⚠️ Important Notes

- ❌ `fresh-start` is **DEV ONLY** - not available in production
- ✅ Always commit your work before resetting
- ✅ Visitor pool is automatically recreated
- ✅ Superuser accounts are preserved in partial resets
- ❌ All data is lost - make sure you don't need anything!

## 🔗 Related Commands

```bash
make status                    # Check what's running
make ENV=dev stop              # Stop dev environment
make ENV=dev restart           # Restart without reset
make ENV=dev logs              # View logs
```

---

**Last Updated:** 2025-11-17
**For Issues:** See project README or open an issue on GitHub
