# 01 - Gitea Development Setup

**Quick guide for running Gitea locally for development**

---

## Quick Start

```bash
# Start Gitea
./deployment/gitea/scripts/start-dev.sh

# Access: http://localhost:3000
```

---

## Initial Setup (First Time)

### 1. Start Gitea

```bash
cd /home/ywatanabe/proj/scitex-cloud
./deployment/gitea/scripts/start-dev.sh
```

**Access:** http://localhost:3000

### 2. Complete Installation Wizard

#### Database Settings
- **Type:** SQLite3 ✅ (already selected)
- **Path:** /data/gitea/gitea.db (default)

#### General Settings
- **Site Title:** SciTeX Git
- **Repository Root:** /data/git/repositories
- **Git LFS Root:** /data/git/lfs
- **Run As:** git

#### Server Settings
- **SSH Domain:** localhost
- **SSH Port:** 22 (mapped to 2222 on host)
- **HTTP Port:** 3000
- **Base URL:** http://localhost:3000/

#### Admin Account
- **Username:** scitex (recommended)
- **Password:** (choose secure password)
- **Email:** your@email.com

**Click "Install Gitea"**

### 3. Test Setup

Create test repository:
1. Click "+" → "New Repository"
2. Name: `test-repo`
3. Initialize with README ✅
4. Click "Create Repository"

Test git operations:
```bash
git clone http://localhost:3000/scitex/test-repo.git
cd test-repo
echo "# Test" >> README.md
git add .
git commit -m "Test commit"
git push origin main
```

---

## Using with Django

### Create API Token

1. Login to Gitea: http://localhost:3000
2. Avatar → Settings → Applications
3. **Generate New Token**
4. Name: `Django Integration`
5. Scopes: (select all for development)
6. **Generate Token**
7. **Copy token** (shown only once!)

### Set Environment Variable

```bash
# Edit development environment
vim deployment/dotenvs/dotenv.dev

# Add:
export SCITEX_CLOUD_GITEA_TOKEN="your-token-here"

# Reload
source deployment/dotenvs/dotenv.dev
```

### Test Django Integration

```bash
source .venv/bin/activate
python manage.py shell --settings=config.settings.settings_dev
```

```python
from apps.gitea_app.api_client import GiteaClient

client = GiteaClient()
user = client.get_current_user()
print(f"✅ Connected as: {user['username']}")
```

---

## Creating Projects via Django

### Option 1: New Git-Backed Project

1. Navigate: http://localhost:8000/new
2. **Name:** "My Research Project"
3. **Description:** Optional
4. Select: **"Git-backed repository"** ✅
5. Click "Create Repository"

**Result:**
- Repository in Gitea: http://localhost:3000/username/my-research-project
- Local clone: `./data/username/my-research-project/`
- Ready for git commands

### Option 2: Import from GitHub

1. Navigate: http://localhost:8000/new
2. **Name:** "Imported Project"
3. Select: **"Import from GitHub"**
4. **GitHub URL:** `https://github.com/user/repo`
5. **GitHub Token:** (optional, for private repos)
6. Click "Create Repository"

**Get GitHub Token:**
1. https://github.com/settings/tokens
2. Generate new token (classic)
3. Scope: `repo` ✅
4. Copy token

---

## Working with Local Files

```bash
# Navigate to project
cd ./data/username/my-project/

# Edit with any tool
vim script.py
code .
jupyter notebook

# Commit and push
git add .
git commit -m "Update analysis"
git push origin main
```

**View in Gitea:** http://localhost:3000/username/my-project

---

## Container Management

### Stop Gitea
```bash
./deployment/gitea/scripts/stop-dev.sh
# OR
docker stop scitex-gitea-dev
```

### Start Gitea
```bash
./deployment/gitea/scripts/start-dev.sh
# OR
docker start scitex-gitea-dev
```

### View Logs
```bash
docker logs scitex-gitea-dev -f
```

### Check Status
```bash
docker ps | grep gitea
```

### Remove Container (keeps data)
```bash
docker stop scitex-gitea-dev
docker rm scitex-gitea-dev
```

### Remove Everything (including data)
```bash
docker stop scitex-gitea-dev
docker rm scitex-gitea-dev
docker volume rm gitea-data
```

---

## Quick Reference

| Item | Value |
|------|-------|
| **Web UI** | http://localhost:3000 |
| **SSH Port** | 2222 |
| **HTTP Clone** | `http://localhost:3000/username/repo.git` |
| **SSH Clone** | `git@localhost:2222:username/repo.git` |
| **Container** | scitex-gitea-dev |
| **Data Volume** | gitea-data |
| **Config** | `docker-compose.gitea-dev.yml` |

---

## Troubleshooting

### Can't access localhost:3000

```bash
# Check if running
docker ps | grep gitea

# If not running
docker start scitex-gitea-dev

# Check logs
docker logs scitex-gitea-dev
```

### Port 3000 already in use

```bash
# Find what's using it
lsof -i :3000

# OR use different port
docker rm scitex-gitea-dev
docker run -d --name scitex-gitea-dev \
  -p 3001:3000 -p 2222:22 \
  -v gitea-data:/data \
  gitea/gitea:1.21
```

### API token not working

```bash
# Test token
curl -H "Authorization: token $SCITEX_CLOUD_GITEA_TOKEN" \
  http://localhost:3000/api/v1/user

# Should return user info

# If fails, regenerate token in Gitea UI
```

### GitHub import rate limited

**Problem:** "Remote visit addressed rate limitation"

**Solution:** Provide GitHub token (even for public repos)

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Repository exists | Use different name or delete old repo |
| GitHub URL required | Enter URL when selecting "Import" |
| Rate limited | Add GitHub token |
| Clone failed | Check network, verify repo exists |

---

## Next Steps

- ✅ Gitea running locally
- ✅ API token configured
- ✅ Django integration tested
- ⏭️ Create test project via Django
- ⏭️ Test GitHub import
- ⏭️ Ready for production deployment

**See:** `02_PRODUCTION.md` for production deployment

---

**Development environment ready!** 🚀

<!-- EOF -->
