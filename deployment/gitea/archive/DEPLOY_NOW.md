# Deploy Gitea to Production NOW

**Quick Start Guide** - Get Gitea running in 10 minutes

---

## Prerequisites Check

```bash
# On production server (162.43.35.139)
# Verify you're on the right server
hostname -I
# Should show: 162.43.35.139

# Check PostgreSQL is running
systemctl is-active postgresql
# Should show: active

# Check Nginx is running
systemctl is-active nginx
# Should show: active
```

All checks passed? Continue below.

---

## Step 1: Run Deployment Script (5 minutes)

```bash
cd /home/ywatanabe/proj/scitex-cloud

# Run the automated deployment
sudo ./deployment/gitea/deploy-production.sh
```

The script will:
- Install Gitea binary
- Create PostgreSQL database
- Configure Gitea
- Set up Nginx
- Start Gitea service

**Wait for:** "Gitea Installation Complete!" message

---

## Step 2: Set Up DNS (if not already done)

Add DNS A record at your DNS provider:
```
Type: A
Name: git
Host: scitex.ai
Value: 162.43.35.139
TTL: 3600
```

Verify:
```bash
dig git.scitex.ai
# Should return: 162.43.35.139
```

---

## Step 3: Install SSL Certificate (2 minutes)

```bash
# Install SSL certificate with certbot
sudo certbot --nginx -d git.scitex.ai

# Follow prompts:
# - Enter email: your-email@example.com
# - Agree to terms: Y
# - Share email: N (optional)
# - Redirect HTTP to HTTPS: 2 (recommended)
```

**Result:** Gitea now accessible at `https://git.scitex.ai`

---

## Step 4: Create Admin User (1 minute)

1. Open browser: `https://git.scitex.ai`
2. Click "Register"
3. Fill in:
   - Username: `scitex` (or your preferred username)
   - Email: `admin@scitex.ai`
   - Password: (strong password)
4. Click "Register Account"

**First user becomes admin automatically**

---

## Step 5: Generate API Token (1 minute)

1. Login to Gitea
2. Click your avatar → Settings
3. Applications → Manage Access Tokens
4. Click "Generate New Token"
5. Name: `Django Integration`
6. Select scopes:
   - ✅ `repo`
   - ✅ `admin:org`
   - ✅ `user`
7. Click "Generate Token"
8. **COPY THE TOKEN** (shown only once!)

---

## Step 6: Update Django Environment (1 minute)

```bash
# Edit production environment file
vim /home/ywatanabe/proj/scitex-cloud/deployment/dotenvs/dotenv.prod

# Update this line (paste your token from Step 5):
export SCITEX_CLOUD_GITEA_TOKEN="your-token-here"

# Save and exit (:wq)

# Reload environment
source /home/ywatanabe/proj/scitex-cloud/deployment/dotenvs/dotenv.prod

# Restart Django
cd /home/ywatanabe/proj/scitex-cloud
./server.sh restart -m prod
```

---

## Step 7: Test Integration (2 minutes)

```bash
cd /home/ywatanabe/proj/scitex-cloud
source .venv/bin/activate

# Test Gitea API connection
python manage.py shell --settings=config.settings.settings_prod
```

In Python shell:
```python
from apps.gitea_app.api_client import GiteaClient

client = GiteaClient()
user = client.get_current_user()
print(f"✅ Connected as: {user['username']}")

repos = client.list_repositories()
print(f"✅ API working! Repositories: {len(repos)}")

# Exit shell
exit()
```

Expected output:
```
✅ Connected as: scitex
✅ API working! Repositories: 0
```

---

## Step 8: Create Test Repository (1 minute)

### Via Django Web UI:
1. Navigate to `https://scitex.ai/new`
2. Project name: `test-production-gitea`
3. Description: `Testing Gitea production deployment`
4. Select: **"Git-backed repository (Recommended)"**
5. Click "Create Repository"

### Verify in Gitea:
1. Navigate to `https://git.scitex.ai`
2. Should see: `username/test-production-gitea`

### Test Git Operations:
```bash
cd /tmp
git clone https://git.scitex.ai/username/test-production-gitea.git
cd test-production-gitea
echo "# Production Test" >> README.md
git add .
git commit -m "Test commit from production"
git push origin main
```

---

## ✅ Deployment Complete!

Gitea is now running at: **https://git.scitex.ai**

### Verification Checklist:
- [x] Gitea accessible via HTTPS
- [x] SSL certificate installed
- [x] Admin user created
- [x] API token generated
- [x] Django integration working
- [x] Can create repositories via Django
- [x] Can clone/push via git

---

## What's Next?

1. **Commit Changes:**
   ```bash
   cd /home/ywatanabe/proj/scitex-cloud
   git add deployment/dotenvs/dotenv.prod
   git add config/settings/settings_prod.py
   git commit -m "feat: Add Gitea production configuration"
   ```

2. **Update TODO:**
   - Mark `01_USER_DATA_ACCESS_INFRASTRUCTURE.md` → Production Gitea: ✅ Complete

3. **Start Using:**
   - Migrate existing projects to Gitea
   - Enable git-backed projects for all users
   - Set up webhooks (optional)

---

## Troubleshooting

### Gitea not accessible?
```bash
sudo systemctl status gitea
sudo journalctl -u gitea -n 50
```

### SSL issues?
```bash
sudo certbot certificates
sudo nginx -t
sudo systemctl restart nginx
```

### Django integration not working?
```bash
# Check environment variables
source deployment/dotenvs/dotenv.prod
echo $SCITEX_CLOUD_GITEA_URL
echo $SCITEX_CLOUD_GITEA_TOKEN

# Check Django logs
tail -f logs/app.log
```

---

## Support

**Full Guide:** `deployment/gitea/PRODUCTION_DEPLOYMENT_GUIDE.md`

**Quick Commands:**
```bash
# Service status
sudo systemctl status gitea

# View logs
sudo journalctl -u gitea -f

# Restart service
sudo systemctl restart gitea

# Check config
sudo cat /etc/gitea/app.ini
```

---

**Total Time:** ~10-15 minutes
**Difficulty:** Easy (mostly automated)

🎉 **Congratulations! Your Gitea instance is production-ready!**

<!-- EOF -->
