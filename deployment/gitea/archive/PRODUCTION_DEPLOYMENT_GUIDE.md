# Gitea Production Deployment Guide

**Date:** 2025-10-20
**Domain:** git.scitex.ai
**Server IP:** 162.43.35.139

---

## Prerequisites

Before running the deployment script, ensure:

- [x] You have root/sudo access to the production server
- [x] PostgreSQL is installed and running
- [x] Nginx is installed
- [x] Domain `git.scitex.ai` DNS A record points to 162.43.35.139
- [ ] Certbot is installed (for SSL certificates)

## Quick Deployment (Automated)

```bash
# On production server (162.43.35.139)
cd /home/ywatanabe/proj/scitex-cloud

# Run the deployment script
sudo ./deployment/gitea/deploy-production.sh
```

The script will:
1. ✅ Create gitea system user
2. ✅ Create required directories
3. ✅ Download and install Gitea binary
4. ✅ Create PostgreSQL database (`gitea_prod`)
5. ✅ Generate secure Gitea configuration
6. ✅ Create systemd service
7. ✅ Configure Nginx reverse proxy
8. ✅ Configure firewall rules
9. ✅ Start Gitea service

**Duration:** ~5 minutes

---

## Step-by-Step Manual Deployment

If you prefer manual control, follow these steps:

### Step 1: DNS Configuration

Verify DNS is correctly configured:

```bash
# Check DNS resolution
dig git.scitex.ai

# Should return: 162.43.35.139
```

If not configured, add A record at your DNS provider:
```
Type: A
Name: git
Value: 162.43.35.139
TTL: 3600
```

### Step 2: Install Dependencies

```bash
# Ensure PostgreSQL is running
sudo systemctl status postgresql
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Ensure Nginx is running
sudo systemctl status nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# Install certbot for SSL (if not already installed)
sudo dnf install certbot python3-certbot-nginx  # RHEL/Rocky
# OR
sudo apt install certbot python3-certbot-nginx  # Ubuntu/Debian
```

### Step 3: Run Automated Deployment

```bash
cd /home/ywatanabe/proj/scitex-cloud
sudo ./deployment/gitea/deploy-production.sh
```

### Step 4: Set Up SSL Certificate

```bash
# After Gitea is running, install SSL certificate
sudo certbot --nginx -d git.scitex.ai

# Certbot will:
# - Obtain SSL certificate from Let's Encrypt
# - Update Nginx configuration automatically
# - Set up automatic renewal
```

Test SSL renewal:
```bash
sudo certbot renew --dry-run
```

### Step 5: Create Admin User

1. Open browser: `https://git.scitex.ai`
2. Click "Register"
3. First user to register becomes admin
4. Recommended username: `scitex` or your username

### Step 6: Generate API Token

1. Login to Gitea
2. Navigate: User Settings → Applications → Manage Access Tokens
3. Click "Generate New Token"
4. Name: `SciTeX Cloud Django Integration`
5. Select scopes:
   - `repo` (read/write repositories)
   - `admin:org` (manage organizations)
   - `user` (read user profile)
6. Click "Generate Token"
7. **Copy the token** (you won't see it again!)

### Step 7: Update Django Environment

Add to `deployment/dotenvs/dotenv.prod`:

```bash
# ----------------------------------------
# Gitea Configuration
# ----------------------------------------
export SCITEX_CLOUD_GITEA_URL=https://git.scitex.ai
export SCITEX_CLOUD_GITEA_API_URL=https://git.scitex.ai/api/v1
export SCITEX_CLOUD_GITEA_TOKEN=<your-api-token-from-step-6>
```

Update `config/settings/settings_prod.py`:

```python
# Gitea Configuration
GITEA_URL = os.environ.get('SCITEX_CLOUD_GITEA_URL', 'https://git.scitex.ai')
GITEA_API_URL = os.environ.get('SCITEX_CLOUD_GITEA_API_URL', 'https://git.scitex.ai/api/v1')
GITEA_TOKEN = os.environ.get('SCITEX_CLOUD_GITEA_TOKEN', '')
```

### Step 8: Reload Environment and Restart Django

```bash
# Source updated environment
source deployment/dotenvs/dotenv.prod

# Restart Django (if using systemd/uwsgi)
./server.sh restart -m prod
```

### Step 9: Test Integration

```bash
# Test Gitea API from Django
cd /home/ywatanabe/proj/scitex-cloud
source .venv/bin/activate

python manage.py shell --settings=config.settings.settings_prod

# In Python shell:
from apps.gitea_app.api_client import GiteaClient

client = GiteaClient()
user = client.get_current_user()
print(f"Connected as: {user['username']}")

repos = client.list_repositories()
print(f"Repositories: {len(repos)}")
```

Expected output:
```
Connected as: scitex
Repositories: 0
```

### Step 10: Create Test Repository

Via Django web UI:
1. Navigate to `https://scitex.ai/new`
2. Enter project name: "test-gitea-prod"
3. Select: "Git-backed repository (Recommended)"
4. Click "Create Repository"

Verify in Gitea:
1. Navigate to `https://git.scitex.ai`
2. Should see new repository: `username/test-gitea-prod`

Clone and test:
```bash
git clone https://git.scitex.ai/username/test-gitea-prod.git
cd test-gitea-prod
echo "# Test" >> README.md
git add .
git commit -m "Test commit"
git push origin main
```

---

## Verification Checklist

After deployment, verify:

- [ ] Gitea accessible at `https://git.scitex.ai`
- [ ] SSL certificate installed and valid
- [ ] Can register/login to Gitea
- [ ] Can create repository via Gitea UI
- [ ] Can create repository via Django UI
- [ ] Can clone repository (HTTPS)
- [ ] Can push to repository (HTTPS)
- [ ] Django API integration working
- [ ] systemd service enabled (auto-start on reboot)
- [ ] Firewall rules configured
- [ ] Logs accessible: `journalctl -u gitea -f`

---

## Service Management

```bash
# Check status
sudo systemctl status gitea

# Start
sudo systemctl start gitea

# Stop
sudo systemctl stop gitea

# Restart
sudo systemctl restart gitea

# Enable auto-start
sudo systemctl enable gitea

# Disable auto-start
sudo systemctl disable gitea

# View logs
sudo journalctl -u gitea -f           # Follow logs
sudo journalctl -u gitea -n 100       # Last 100 lines
sudo journalctl -u gitea --since today # Today's logs
```

---

## Configuration Files

### Gitea Configuration
**File:** `/etc/gitea/app.ini`
```bash
# View config
sudo cat /etc/gitea/app.ini

# Edit config (requires restart)
sudo vim /etc/gitea/app.ini
sudo systemctl restart gitea
```

### Nginx Configuration
**File:** `/etc/nginx/sites-available/gitea`
```bash
# View config
cat /etc/nginx/sites-available/gitea

# Edit config
sudo vim /etc/nginx/sites-available/gitea

# Test config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### Database
**Database Name:** `gitea_prod`
**Database User:** `gitea_prod`
**Database Password:** `/root/.gitea_db_password`

```bash
# Connect to database
sudo -u postgres psql gitea_prod

# Backup database
sudo -u postgres pg_dump gitea_prod > gitea_backup_$(date +%Y%m%d).sql

# Restore database
sudo -u postgres psql gitea_prod < gitea_backup_20251020.sql
```

---

## Troubleshooting

### Gitea won't start

```bash
# Check logs
sudo journalctl -u gitea -n 100 --no-pager

# Common issues:
# 1. Port already in use
sudo netstat -tlnp | grep 3000

# 2. Database connection failed
sudo -u postgres psql -l | grep gitea

# 3. Permission issues
sudo chown -R gitea:gitea /var/lib/gitea
```

### Can't access via HTTPS

```bash
# Check Nginx status
sudo systemctl status nginx

# Check Nginx configuration
sudo nginx -t

# Check SSL certificate
sudo certbot certificates

# Renew certificate manually
sudo certbot renew

# Check firewall
sudo ufw status | grep 443
sudo firewall-cmd --list-ports
```

### API integration not working

```bash
# Test API directly
curl -H "Authorization: token YOUR_TOKEN" \
  https://git.scitex.ai/api/v1/user/repos

# Check Django environment
source deployment/dotenvs/dotenv.prod
echo $SCITEX_CLOUD_GITEA_URL
echo $SCITEX_CLOUD_GITEA_TOKEN

# Check Django logs
tail -f logs/app.log
```

### SSH clone not working

```bash
# Check SSH port
sudo ss -tlnp | grep 2222

# Test SSH connection
ssh -T -p 2222 git@git.scitex.ai

# Check firewall
sudo ufw allow 2222/tcp
sudo firewall-cmd --add-port=2222/tcp --permanent
sudo firewall-cmd --reload
```

---

## Backup Strategy

### Automated Backup Script

Create `/root/backup-gitea.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/backup/gitea"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump gitea_prod | gzip > $BACKUP_DIR/gitea_db_$DATE.sql.gz

# Backup repositories
tar -czf $BACKUP_DIR/gitea_repos_$DATE.tar.gz -C /var/lib/gitea/data gitea-repositories

# Backup configuration
cp /etc/gitea/app.ini $BACKUP_DIR/app.ini_$DATE

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

Make executable:
```bash
chmod +x /root/backup-gitea.sh
```

Add to cron (daily at 2 AM):
```bash
sudo crontab -e
# Add line:
0 2 * * * /root/backup-gitea.sh >> /var/log/gitea-backup.log 2>&1
```

---

## Performance Tuning

### PostgreSQL Optimization

Edit `/var/lib/pgsql/data/postgresql.conf`:
```ini
# Increase shared buffers
shared_buffers = 256MB

# Increase work memory
work_mem = 16MB

# Increase maintenance work memory
maintenance_work_mem = 128MB

# Increase effective cache size
effective_cache_size = 1GB
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### Gitea Configuration

Edit `/etc/gitea/app.ini`:
```ini
[server]
# Increase connection limits
HTTP_ADDR = 0.0.0.0
HTTP_PORT = 3000

[database]
# Connection pool
MAX_OPEN_CONNS = 50
MAX_IDLE_CONNS = 25

[repository]
# Enable caching
ENABLE_PUSH_CREATE_USER = true
ENABLE_PUSH_CREATE_ORG = true
```

---

## Security Hardening

### 1. Enable 2FA for Admin

1. Login to Gitea
2. Settings → Security → Two-Factor Authentication
3. Scan QR code with authenticator app
4. Save recovery codes

### 2. Restrict Registration (Optional)

Edit `/etc/gitea/app.ini`:
```ini
[service]
DISABLE_REGISTRATION = true  # Disable public registration
```

### 3. Enable Rate Limiting

Edit `/etc/gitea/app.ini`:
```ini
[service.rate_limit]
ENABLED = true
REQUEST_LIMIT = 10
REQUEST_TIME = 60
```

### 4. Configure Fail2Ban

Create `/etc/fail2ban/filter.d/gitea.conf`:
```ini
[Definition]
failregex = .*Failed authentication attempt.*<HOST>
ignoreregex =
```

Create `/etc/fail2ban/jail.d/gitea.conf`:
```ini
[gitea]
enabled = true
filter = gitea
logpath = /var/lib/gitea/log/gitea.log
maxretry = 5
bantime = 3600
```

Restart fail2ban:
```bash
sudo systemctl restart fail2ban
```

---

## Migration from Development

If you have existing repositories in development Gitea:

```bash
# 1. Export from development (on dev machine)
docker exec scitex-gitea-dev gitea dump -c /data/gitea/conf/app.ini

# 2. Copy to production
scp gitea-dump-*.zip root@162.43.35.139:/tmp/

# 3. Import on production
cd /tmp
unzip gitea-dump-*.zip
sudo -u gitea gitea restore --config /etc/gitea/app.ini --from gitea-dump-*.zip
sudo systemctl restart gitea
```

---

## Next Steps

After successful deployment:

1. **Update Documentation**
   - Update project README with Gitea URL
   - Document git workflows for team

2. **Migrate Existing Projects**
   - See `TODOS/01_USER_DATA_ACCESS_INFRASTRUCTURE.md`
   - Use Django management command (create if needed)

3. **Set Up Webhooks** (Optional)
   - Gitea → Django notifications
   - Automated testing on push

4. **Monitor Performance**
   - Set up Prometheus/Grafana
   - Track repository growth
   - Monitor API usage

---

## Support

**Documentation:**
- Gitea Docs: https://docs.gitea.io/
- SciTeX Assessment: `docs/FUNDAMENTAL_INFRASTRUCTURE_ASSESSMENT.md`
- Implementation Status: `deployment/gitea/IMPLEMENTATION_COMPLETE.md`

**Logs:**
```bash
# Gitea service logs
sudo journalctl -u gitea -f

# Nginx logs
sudo tail -f /var/log/nginx/gitea_access.log
sudo tail -f /var/log/nginx/gitea_error.log

# Django logs
tail -f logs/app.log
```

---

**Deployment Complete! 🎉**

Your Gitea instance should now be running at: `https://git.scitex.ai`

<!-- EOF -->
