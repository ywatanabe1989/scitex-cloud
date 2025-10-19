# 02 - Gitea Production Deployment

**Deploy Gitea to production server at git.scitex.ai**

---

## Prerequisites

- [x] PostgreSQL installed and running
- [x] Nginx installed
- [x] Root/sudo access
- [ ] DNS A record: `git.scitex.ai` → `162.43.35.139`
- [ ] Certbot installed (for SSL)

---

## Quick Deployment (15 minutes)

```bash
# SSH to production server
ssh ywatanabe@162.43.35.139

# Navigate to project
cd /home/ywatanabe/proj/scitex-cloud

# Run deployment script
sudo ./deployment/gitea/scripts/deploy-production.sh

# Install SSL certificate
sudo certbot --nginx -d git.scitex.ai

# Access Gitea
open https://git.scitex.ai
```

---

## Deployment Steps

### Step 1: Verify Prerequisites

```bash
# Check PostgreSQL
systemctl is-active postgresql
# Should show: active

# Check Nginx
systemctl is-active nginx
# Should show: active

# Check DNS
dig git.scitex.ai
# Should return: 162.43.35.139
```

### Step 2: Run Deployment Script

```bash
cd /home/ywatanabe/proj/scitex-cloud
sudo ./deployment/gitea/scripts/deploy-production.sh
```

**Script will:**
1. ✅ Create gitea system user
2. ✅ Download Gitea binary (v1.21.5)
3. ✅ Create PostgreSQL database (`gitea_prod`)
4. ✅ Generate secure configuration
5. ✅ Create systemd service
6. ✅ Configure Nginx reverse proxy
7. ✅ Configure firewall rules
8. ✅ Start Gitea service

**Duration:** ~5 minutes

### Step 3: Install SSL Certificate

```bash
sudo certbot --nginx -d git.scitex.ai

# Follow prompts:
# - Email: your-email@example.com
# - Agree to terms: Y
# - Redirect HTTP to HTTPS: 2 (recommended)
```

**Test SSL:**
```bash
curl -I https://git.scitex.ai
# Should show: HTTP/2 200
```

### Step 4: Create Admin User

1. Open: https://git.scitex.ai
2. Click "Register"
3. Fill in:
   - Username: `scitex` (or preferred)
   - Email: `admin@scitex.ai`
   - Password: (strong password)
4. Click "Register Account"

**First user becomes admin automatically**

### Step 5: Generate API Token

1. Login to Gitea
2. Avatar → Settings → Applications
3. **Manage Access Tokens** → **Generate New Token**
4. Name: `Django Integration`
5. Scopes:
   - ✅ `repo` (repositories)
   - ✅ `admin:org` (organizations)
   - ✅ `user` (user profile)
6. **Generate Token**
7. **COPY TOKEN** (shown only once!)

### Step 6: Update Django Environment

```bash
# Edit production environment
vim /home/ywatanabe/proj/scitex-cloud/deployment/dotenvs/dotenv.prod

# Update this line (paste your token):
export SCITEX_CLOUD_GITEA_TOKEN="your-token-from-step-5"

# Save and exit (:wq)

# Reload environment
source deployment/dotenvs/dotenv.prod

# Restart Django
cd /home/ywatanabe/proj/scitex-cloud
./server.sh restart -m prod
```

### Step 7: Test Integration

```bash
cd /home/ywatanabe/proj/scitex-cloud
source .venv/bin/activate

python manage.py shell --settings=config.settings.settings_prod
```

```python
from apps.gitea_app.api_client import GiteaClient

client = GiteaClient()
user = client.get_current_user()
print(f"✅ Connected as: {user['username']}")

repos = client.list_repositories()
print(f"✅ Repositories: {len(repos)}")
```

Expected output:
```
✅ Connected as: scitex
✅ Repositories: 0
```

### Step 8: Create Test Repository

**Via Django UI:**
1. Navigate: https://scitex.ai/new
2. Name: `test-production`
3. Select: **"Git-backed repository"**
4. Click "Create Repository"

**Verify in Gitea:**
1. Navigate: https://git.scitex.ai
2. Should see: `username/test-production`

**Test git operations:**
```bash
git clone https://git.scitex.ai/username/test-production.git
cd test-production
echo "# Production Test" >> README.md
git add .
git commit -m "Test from production"
git push origin main
```

---

## Service Management

### Check Status
```bash
sudo systemctl status gitea
```

### Start/Stop/Restart
```bash
sudo systemctl start gitea
sudo systemctl stop gitea
sudo systemctl restart gitea
```

### Enable Auto-Start
```bash
sudo systemctl enable gitea
```

### View Logs
```bash
# Follow logs
sudo journalctl -u gitea -f

# Last 100 lines
sudo journalctl -u gitea -n 100

# Today's logs
sudo journalctl -u gitea --since today
```

---

## Configuration Files

### Gitea Configuration
**File:** `/etc/gitea/app.ini`

```bash
# View config
sudo cat /etc/gitea/app.ini

# Edit config
sudo vim /etc/gitea/app.ini

# Restart after changes
sudo systemctl restart gitea
```

### Nginx Configuration
**File:** `/etc/nginx/sites-available/gitea`

```bash
# Edit
sudo vim /etc/nginx/sites-available/gitea

# Test config
sudo nginx -t

# Reload
sudo systemctl reload nginx
```

### Database
- **Name:** gitea_prod
- **User:** gitea_prod
- **Password:** `/root/.gitea_db_password`

```bash
# Connect to database
sudo -u postgres psql gitea_prod

# Backup
sudo -u postgres pg_dump gitea_prod > gitea_backup_$(date +%Y%m%d).sql

# Restore
sudo -u postgres psql gitea_prod < gitea_backup.sql
```

---

## Verification Checklist

- [ ] Gitea accessible: https://git.scitex.ai
- [ ] SSL certificate valid (green lock)
- [ ] Can register/login
- [ ] Can create repository via Gitea UI
- [ ] Can create repository via Django UI
- [ ] Can clone repository (HTTPS)
- [ ] Can push to repository (HTTPS)
- [ ] Django API integration working
- [ ] Service enabled (auto-start)
- [ ] Firewall rules configured
- [ ] Logs accessible

---

## Backup Strategy

### Manual Backup

```bash
#!/bin/bash
BACKUP_DIR="/backup/gitea"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump gitea_prod | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup repositories
sudo tar -czf $BACKUP_DIR/repos_$DATE.tar.gz -C /var/lib/gitea/data gitea-repositories

# Backup configuration
sudo cp /etc/gitea/app.ini $BACKUP_DIR/app.ini_$DATE

echo "Backup complete: $DATE"
```

### Automated Backups

Save to `/root/backup-gitea.sh`:
```bash
chmod +x /root/backup-gitea.sh

# Add to cron (daily at 2 AM)
sudo crontab -e
# Add:
0 2 * * * /root/backup-gitea.sh >> /var/log/gitea-backup.log 2>&1
```

---

## Troubleshooting

### Gitea won't start

```bash
# Check logs
sudo journalctl -u gitea -n 100 --no-pager

# Common issues:
# 1. Port in use
sudo netstat -tlnp | grep 3000

# 2. Database connection
sudo -u postgres psql -l | grep gitea

# 3. Permissions
sudo chown -R gitea:gitea /var/lib/gitea
```

### Can't access HTTPS

```bash
# Check Nginx
sudo systemctl status nginx
sudo nginx -t

# Check SSL
sudo certbot certificates

# Renew
sudo certbot renew

# Check firewall
sudo ufw status | grep 443
```

### API not working

```bash
# Test directly
curl -H "Authorization: token YOUR_TOKEN" \
  https://git.scitex.ai/api/v1/user/repos

# Check Django env
source deployment/dotenvs/dotenv.prod
echo $SCITEX_CLOUD_GITEA_URL
echo $SCITEX_CLOUD_GITEA_TOKEN

# Check logs
tail -f logs/app.log
```

### SSH clone not working

```bash
# Check SSH port
sudo ss -tlnp | grep 2222

# Test connection
ssh -T -p 2222 git@git.scitex.ai

# Open firewall
sudo ufw allow 2222/tcp
```

---

## Security Hardening

### 1. Enable 2FA for Admin
1. Login → Settings → Security
2. Two-Factor Authentication
3. Scan QR code
4. Save recovery codes

### 2. Restrict Registration (Optional)
Edit `/etc/gitea/app.ini`:
```ini
[service]
DISABLE_REGISTRATION = true
```

### 3. Configure Fail2Ban
```bash
# Install
sudo apt install fail2ban

# Create filter
sudo vim /etc/fail2ban/filter.d/gitea.conf
```

```ini
[Definition]
failregex = .*Failed authentication.*<HOST>
```

```bash
# Create jail
sudo vim /etc/fail2ban/jail.d/gitea.conf
```

```ini
[gitea]
enabled = true
filter = gitea
logpath = /var/lib/gitea/log/gitea.log
maxretry = 5
bantime = 3600
```

```bash
# Restart
sudo systemctl restart fail2ban
```

---

## Performance Tuning

### PostgreSQL
Edit `/var/lib/pgsql/data/postgresql.conf`:
```ini
shared_buffers = 256MB
work_mem = 16MB
maintenance_work_mem = 128MB
effective_cache_size = 1GB
```

Restart:
```bash
sudo systemctl restart postgresql
```

### Gitea
Edit `/etc/gitea/app.ini`:
```ini
[database]
MAX_OPEN_CONNS = 50
MAX_IDLE_CONNS = 25

[repository]
ENABLE_PUSH_CREATE_USER = true
ENABLE_PUSH_CREATE_ORG = true
```

---

## Important Files

| File | Purpose |
|------|---------|
| `/etc/gitea/app.ini` | Gitea configuration |
| `/var/lib/gitea/` | Data directory |
| `/var/lib/gitea/data/gitea-repositories/` | Git repositories |
| `/etc/nginx/sites-available/gitea` | Nginx config |
| `/etc/systemd/system/gitea.service` | Systemd service |
| `/root/.gitea_db_password` | Database password |

---

## Quick Reference

| Item | Value |
|------|-------|
| **Web UI** | https://git.scitex.ai |
| **SSH Port** | 2222 |
| **HTTP Clone** | `https://git.scitex.ai/user/repo.git` |
| **SSH Clone** | `git@git.scitex.ai:2222/user/repo.git` |
| **Service** | gitea.service |
| **Database** | gitea_prod |

---

## Next Steps

After successful deployment:

1. **Migrate Projects**
   - Move existing projects to Gitea
   - Update Django project records

2. **Enable for Users**
   - Announce git.scitex.ai availability
   - Update documentation for users

3. **Set Up Webhooks** (Optional)
   - Gitea → Django notifications
   - Automated testing on push

4. **Monitor**
   - Set up monitoring/alerts
   - Track repository growth
   - Monitor API usage

---

**Production deployment complete!** 🎉

**Gitea running at:** https://git.scitex.ai

<!-- EOF -->
