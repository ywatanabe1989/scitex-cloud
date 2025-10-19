# Gitea Production Deployment Status

**Date:** 2025-10-20
**Server:** 162.43.35.139
**Domain:** git.scitex.ai

---

## Current Status: Ready to Deploy ✅

All deployment scripts and configurations are prepared and ready.

---

## Deployment Preparation Complete ✅

- [x] Server environment verified (PostgreSQL running, Nginx configured)
- [x] Deployment script created (`deploy-production.sh`)
- [x] Comprehensive documentation created
- [x] Quick start guide created
- [x] Django production settings updated
- [x] Environment variables configured
- [x] Nginx configuration prepared
- [x] All scripts made executable

---

## Execute Deployment Now

### Option 1: Interactive Terminal (Recommended)

**You need to run this manually in your terminal with sudo access:**

```bash
# SSH into production server
ssh ywatanabe@162.43.35.139

# Navigate to project
cd /home/ywatanabe/proj/scitex-cloud

# Run deployment
sudo ./deployment/gitea/deploy-production.sh
```

**Duration:** ~5 minutes

**What it will do:**
1. Create gitea system user
2. Install Gitea binary (v1.21.5)
3. Create PostgreSQL database (`gitea_prod`)
4. Generate secure configuration
5. Create systemd service
6. Configure Nginx reverse proxy
7. Configure firewall
8. Start Gitea service

### Option 2: Alternative Wrapper

```bash
sudo ./deployment/gitea/EXECUTE_DEPLOYMENT.sh
```

---

## After Deployment

### Step 1: Verify Installation

```bash
# Check Gitea is running
sudo systemctl status gitea

# Check logs
sudo journalctl -u gitea -n 50

# Access Gitea (before SSL)
curl -I http://localhost:3000
```

### Step 2: Install SSL Certificate

```bash
# Install SSL with certbot
sudo certbot --nginx -d git.scitex.ai

# Test SSL
curl -I https://git.scitex.ai
```

### Step 3: Create Admin User

1. Open browser: `https://git.scitex.ai`
2. Click "Register"
3. First user becomes admin

### Step 4: Generate API Token

1. Login → Settings → Applications
2. Generate New Token
3. Name: `Django Integration`
4. Scopes: `repo`, `admin:org`, `user`
5. Copy token

### Step 5: Update Django Environment

```bash
# Edit environment file
vim deployment/dotenvs/dotenv.prod

# Update this line with your token:
export SCITEX_CLOUD_GITEA_TOKEN="your-token-here"

# Reload and restart
source deployment/dotenvs/dotenv.prod
./server.sh restart -m prod
```

### Step 6: Test Integration

```bash
cd /home/ywatanabe/proj/scitex-cloud
source .venv/bin/activate

python manage.py shell --settings=config.settings.settings_prod
```

In Python:
```python
from apps.gitea_app.api_client import GiteaClient
client = GiteaClient()
user = client.get_current_user()
print(f"✅ Connected as: {user['username']}")
```

---

## Deployment Checklist

### Pre-Deployment
- [x] Scripts created and tested
- [x] Documentation complete
- [x] Django settings configured
- [x] PostgreSQL running
- [x] Nginx running
- [ ] **DNS A record configured** (verify: `dig git.scitex.ai`)

### Deployment Execution
- [ ] Run deployment script
- [ ] Verify Gitea service running
- [ ] Install SSL certificate
- [ ] Create admin user
- [ ] Generate API token

### Post-Deployment
- [ ] Update Django environment with token
- [ ] Restart Django
- [ ] Test API integration
- [ ] Create test repository
- [ ] Verify git operations (clone/push)

### Final Verification
- [ ] HTTPS accessible: `https://git.scitex.ai`
- [ ] SSL certificate valid
- [ ] Can register/login
- [ ] Can create repository via Django
- [ ] Can clone repository
- [ ] Can push to repository
- [ ] Django API integration working

---

## Troubleshooting

### If deployment fails

Check logs:
```bash
sudo journalctl -u gitea -n 100 --no-pager
```

Common issues:
1. **Port 3000 in use**: Another service using the port
2. **Database connection failed**: Check PostgreSQL running
3. **Permission denied**: Check directory permissions

### If SSL setup fails

```bash
# Check DNS
dig git.scitex.ai

# Check Nginx config
sudo nginx -t

# Check certbot
sudo certbot certificates
```

---

## Documentation

**Guides:**
- Quick Start: `deployment/gitea/DEPLOY_NOW.md`
- Full Guide: `deployment/gitea/PRODUCTION_DEPLOYMENT_GUIDE.md`
- Assessment: `docs/FUNDAMENTAL_INFRASTRUCTURE_ASSESSMENT.md`

**Scripts:**
- Main Deployment: `deployment/gitea/deploy-production.sh`
- Execution Wrapper: `deployment/gitea/EXECUTE_DEPLOYMENT.sh`

**Configuration:**
- Django Settings: `config/settings/settings_prod.py`
- Environment: `deployment/dotenvs/dotenv.prod`

---

## Next Steps After Successful Deployment

1. **Update TODO:**
   - Mark `TODOS/01_USER_DATA_ACCESS_INFRASTRUCTURE.md` → Gitea Production: ✅

2. **Commit Changes:**
   ```bash
   git add deployment/gitea/
   git add config/settings/settings_prod.py
   git add deployment/dotenvs/dotenv.prod
   git commit -m "feat: Complete Gitea production deployment setup"
   ```

3. **Start Using:**
   - Migrate existing projects to Gitea
   - Enable git-backed projects for all users
   - Set up webhooks (optional)

4. **Consider Next:**
   - Direct SSH access for power users (2 weeks)
   - SLURM/HPC integration (optional, 3-4 weeks)

---

**Status:** Deployment scripts ready, waiting for manual execution with sudo access

**Estimated Total Time:** 15-20 minutes (including SSL and testing)

<!-- EOF -->
