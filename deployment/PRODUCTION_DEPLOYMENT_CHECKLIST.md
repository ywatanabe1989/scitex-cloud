<!-- ---
!-- Timestamp: 2025-10-19 15:25:41
!-- Author: ywatanabe
!-- File: /ssh:scitex:/home/ywatanabe/proj/scitex-cloud/deployment/PRODUCTION_DEPLOYMENT_CHECKLIST.md
!-- --- -->

# SciTeX Cloud Production Deployment Checklist

**Server**: 162.43.35.139
**Project Path**: `/home/ywatanabe/proj/scitex-cloud`
**Virtual Environment**: `.venv`
**Date**: 2025-10-19

## ✅ Completed Setup

### 1. PostgreSQL Database
- [x] PostgreSQL installed and running
- [x] Production database created: `scitex_cloud_prod`
- [x] Production user created: `scitex_prod`
- [x] Password configured via environment variable
- [x] Django migrations applied (63 migrations)

### 2. Python Dependencies
- [x] Virtual environment created: `.venv`
- [x] Django and dependencies installed
- [x] scitex-code package installed in editable mode

### 3. Configuration Files Updated
- [x] uWSGI config updated: `deployment/uwsgi/scitex_cloud_prod.ini`
  - Project path: `/home/ywatanabe/proj/scitex-cloud`
  - Virtual env: `.venv`
  - Socket: `/run/scitex_cloud.sock`
  - **Optimized for 6 CPU cores**: 12 processes, 2 threads
- [x] Nginx config updated: `deployment/nginx/scitex_cloud_prod.conf`
  - All paths corrected to `/home/ywatanabe/proj/scitex-cloud`
  - Socket matches uWSGI: `/run/scitex_cloud.sock`
  - Server name: `scitex.ai` (www.scitex.ai removed - no DNS record)
  - SSL certificates configured: `/etc/letsencrypt/live/scitex.ai/`

### 4. Deployment Scripts
- [x] Server management script available: `./server.sh`
- [x] Fixed `server.sh` to set SCITEX_CLOUD_ENV early for migrations/collectstatic
- [x] Updated `scripts/prod/deploy_prod.sh` with correct paths and settings
- [x] Production scripts in `scripts/prod/` directory

## 📋 Pre-Deployment Checklist (2025-10-19 Status)

### Environment Variables
- [x] Production environment configured: `deployment/dotenvs/dotenv.prod` exists
- [x] `SCITEX_CLOUD_DJANGO_SECRET_KEY` is set (verified via `env | grep SCITEX`)
- [x] Database password configured via environment variables
- [x] All required env vars checked: `env | grep SCITEX_`

### Static Files
- [x] Created staticfiles directory: `staticfiles/`
- [x] Created media directory: `media/`
- [x] Fixed missing favicon.ico file
- [x] Collected static files: 193 files copied successfully

### Logs Directory
- [x] Created logs directory: `logs/`
- [x] Permissions set correctly

### Database Final Check
- [x] Database connection verified (production database exists)
- [x] All database migrations applied successfully
- [ ] Create superuser (if needed): `.venv/bin/python manage.py createsuperuser --settings=config.settings.settings_prod`

### File Permissions
- [x] Set logs ownership: `sudo chown -R ywatanabe:www-data logs/`
- [x] Set logs permissions: `sudo chmod -R 775 logs/`
- [x] Set media ownership: `chown -R www-data:www-data media/`
- [x] Set staticfiles ownership: `chown -R www-data:www-data staticfiles/`

## 🚀 Deployment Steps

### Recommended: Using server.sh

The project includes a comprehensive server management script that handles all deployment steps:

```bash
# First-time setup: Install systemd services (requires sudo)
sudo bash scripts/prod/deploy_prod.sh --install

# Start production server
./server.sh start -m prod -d

# Check status
./server.sh status

# View logs
./server.sh logs

# Restart if needed
./server.sh restart -m prod
```

**Available server.sh commands:**
- `start -m prod -d` - Start production server as daemon
- `stop` - Stop all servers
- `restart -m prod` - Restart production server
- `status` - Show server status
- `logs` - View server logs
- `migrate` - Run database migrations
- `static` - Collect static files

---

### Manual Deployment Steps (For Reproducibility)

Follow these steps to understand exactly what happens during deployment:

### Step 1: Create uWSGI Log Directory

```bash
# Create log directory for uWSGI
sudo mkdir -p /var/log/uwsgi

# Set ownership to www-data
sudo chown www-data:www-data /var/log/uwsgi
sudo chown -R ywatanabe:www-data logs/ && sudo chmod -R 775 logs/

# Verify
ls -ld /var/log/uwsgi
```

**What this does**: Creates the directory where uWSGI will write its application logs. The `www-data` user needs write access to this directory.

### Step 2: Install uWSGI Systemd Service

```bash
# Copy the systemd service file
sudo cp \
    deployment/uwsgi/scitex_cloud_prod.service \
    /etc/systemd/system/scitex_cloud_prod.service

# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable scitex_cloud_prod

# Verify the service is recognized
systemctl list-unit-files | grep scitex_cloud_prod
```

**What this does**:
- Installs the systemd service file that defines how uWSGI should run
- The service file specifies:
  - Working directory: `/home/ywatanabe/proj/scitex-cloud`
  - Python environment: `.venv`
  - uWSGI configuration: `deployment/uwsgi/scitex_cloud_prod.ini`
  - User/Group: `www-data`
  - Environment variables from: `deployment/dotenvs/dotenv.prod`

### Step 3: Configure Nginx

```bash
# Copy Nginx site configuration
sudo cp \
    deployment/nginx/scitex_cloud_prod.conf \
    /etc/nginx/sites-available/scitex_cloud

# Enable the site by creating a symbolic link
sudo ln -sf \
    /etc/nginx/sites-available/scitex_cloud \
    /etc/nginx/sites-enabled/scitex_cloud

# Test Nginx configuration for syntax errors
sudo nginx -t

# Enable Nginx to start on boot
sudo systemctl enable nginx
```

**What this does**:
- Installs the Nginx configuration that defines:
  - Upstream uWSGI backend via Unix socket: `/run/scitex_cloud.sock`
  - Server name: `scitex.ai`, `www.scitex.ai`
  - Static files location: `/home/ywatanabe/proj/scitex-cloud/staticfiles`
  - Media files location: `/home/ywatanabe/proj/scitex-cloud/media`
  - Security headers and SSL settings

### Step 4: Set File Permissions

```bash
# Add user to www-data group (allows file access)
sudo usermod -aG www-data ywatanabe
# Fix ownership of the project directories that www-data needs access to
chown -R www-data:www-data /home/ywatanabe/proj/scitex-cloud/logs
chown -R www-data:www-data /home/ywatanabe/proj/scitex-cloud/media
chown -R www-data:www-data /home/ywatanabe/proj/scitex-cloud/staticfiles

# Verify group membership
groups ywatanabe
```

**What this does**: Ensures the `ywatanabe` user can work with files that `www-data` (the uWSGI/Nginx user) needs to access.

**Note**: You may need to log out and back in for group changes to take effect.

### Step 5: Start Services

```bash
# Start uWSGI service
sudo systemctl start scitex_cloud_prod

# Wait a moment for uWSGI to initialize
sleep 3

# Check uWSGI service status
sudo systemctl status scitex_cloud_prod

# Verify socket was created
ls -l /run/scitex_cloud.sock

# Start/Restart Nginx
sudo systemctl restart nginx

# Check Nginx status
sudo systemctl status nginx
```

**What this does**:
- Starts the uWSGI application server
- uWSGI creates a Unix socket at `/run/scitex_cloud.sock`
- uWSGI loads the Django application using production settings
- Nginx connects to the uWSGI socket to serve requests

### Step 6: Verify Deployment

```bash
# Test local connection
curl http://localhost

# Test via IP address
curl http://162.43.35.139

# Check for any errors in logs
sudo journalctl -u scitex_cloud_prod -n 50

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

**Expected results**:
- `curl` should return HTML from your Django application
- No errors in the journalctl output
- Socket exists and has correct permissions

### Step 7: SSL Certificate (Let's Encrypt)
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d scitex.ai

# Test automatic renewal
sudo certbot renew --dry-run
```

### 4. Firewall Configuration
```bash
# Allow HTTP and HTTPS
sudo ufw allow 'Nginx Full'

# Allow SSH (if not already allowed)
sudo ufw allow OpenSSH

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

## ✅ Post-Deployment Verification

### Service Health Checks
- [x] Check uWSGI status: `sudo systemctl status scitex_cloud_prod` - **RUNNING**
- [x] Check Nginx status: `sudo systemctl status nginx` - **RUNNING**
- [x] Check PostgreSQL status: `sudo systemctl status postgresql` - **RUNNING**
- [x] View uWSGI logs: Socket created at `/run/scitex_cloud.sock`
- [x] View Nginx access logs: `tail -f logs/nginx_access.log` - Receiving requests
- [x] View Nginx error logs: `tail -f logs/nginx_error.log` - No critical errors

### Application Tests
- [x] Visit: `http://162.43.35.139/` - Redirects to HTTPS (301)
- [x] Visit: `https://scitex.ai/` - **WORKING** (HTML footer confirmed)
- [ ] Test admin panel: `https://scitex.ai/admin/`
- [x] Test health endpoint: `https://scitex.ai/health/` - Returns "OK"
- [x] Verify static files loading correctly - 240 static files served
- [ ] Test user registration/login
- [x] Production server with Gunicorn: `./server.sh -m prod` - **WORKING**

### Database Checks
- [x] Verify database connectivity - **CONNECTED**
- [ ] Check database size: `sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('scitex_cloud_prod'));"`
- [x] Verify all migrations applied - **63 migrations applied**

## 📊 Monitoring & Maintenance

### Regular Checks
- [ ] Monitor disk usage: `df -h`
- [ ] Monitor database size
- [ ] Review log files for errors
- [ ] Check SSL certificate expiry

### Backup Strategy
- [ ] Set up database backups (pg_dump)
- [ ] Set up media files backup
- [ ] Test restore procedure

### Performance Monitoring
- [ ] Set up application monitoring (optional: Sentry, New Relic)
- [ ] Monitor server resources (CPU, RAM, disk)
- [ ] Set up alerts for critical errors

## 🔧 Troubleshooting

### Common Issues

**uWSGI won't start:**
```bash
# Check logs
sudo journalctl -u scitex_cloud_prod -n 50

# Check socket permissions
ls -l /run/scitex_cloud.sock

# Test uWSGI manually
cd /home/ywatanabe/proj/scitex-cloud
.venv/bin/uwsgi --ini deployment/uwsgi/scitex_cloud_prod.ini
```

**Nginx 502 Bad Gateway:**
- Check if uWSGI is running
- Verify socket path matches in both configs
- Check socket permissions

**Static files not loading:**
```bash
# Re-collect static files
.venv/bin/python manage.py collectstatic --noinput --settings=config.settings.settings_prod

# Check Nginx static file configuration
# Verify file permissions
```

**Database connection errors:**
- Verify PostgreSQL is running
- Check environment variables
- Test connection: `psql -U scitex_prod -d scitex_cloud_prod -h localhost`

## 📝 Configuration Summary

### Key Paths
- **Project**: `/home/ywatanabe/proj/scitex-cloud`
- **Virtual Env**: `/home/ywatanabe/proj/scitex-cloud/.venv`
- **Static Files**: `/home/ywatanabe/proj/scitex-cloud/staticfiles`
- **Media Files**: `/home/ywatanabe/proj/scitex-cloud/media`
- **Logs**: `/home/ywatanabe/proj/scitex-cloud/logs`
- **Socket**: `/run/scitex_cloud.sock`

### Database
- **Name**: `scitex_cloud_prod`
- **User**: `scitex_prod`
- **Host**: `localhost`
- **Port**: `5432`

### Services
- **uWSGI**: 12 processes, 2 threads per process (optimized for 6 CPU cores)
- **Nginx**: Port 80 (HTTP), Port 443 (HTTPS)

### Security
- Django DEBUG: `False`
- ALLOWED_HOSTS: `scitex.ai, 162.43.35.139, localhost`
- SSL/HTTPS: **ENABLED** (Let's Encrypt)
- HSTS: **ENABLED**
- HTTP to HTTPS redirect: **ENABLED**

## 🎯 Current Status & Next Steps

### ✅ Deployment Completed! (2025-10-19)

**Production Status**: 🟢 **LIVE** at https://scitex.ai

#### Successfully Deployed:
1. ✅ Server configuration (6 CPU cores, 162.43.35.139)
2. ✅ uWSGI systemd service running (12 processes × 2 threads)
3. ✅ Nginx reverse proxy configured and running
4. ✅ SSL certificates configured for scitex.ai
5. ✅ Static files collected (240 files)
6. ✅ Database migrations applied (63 migrations)
7. ✅ Missing files fixed (favicon.ico)
8. ✅ All directories created with correct permissions
9. ✅ server.sh fixed to use production settings correctly
10. ✅ File permissions set for www-data user

#### Deployment Methods Available:

**Method 1: Using systemd services (Current)**
```bash
# Check status
sudo systemctl status scitex_cloud_prod
sudo systemctl status nginx

# Restart if needed
sudo systemctl restart scitex_cloud_prod
sudo systemctl restart nginx
```

**Method 2: Using server.sh with Gunicorn**
```bash
# Start production server
./server.sh start -m prod -d

# Check status
./server.sh status

# View logs
./server.sh logs
```

### ⏭️ Remaining Tasks

1. **Create superuser** (if needed):
   ```bash
   source .venv/bin/activate
   python manage.py createsuperuser --settings=config.settings.settings_prod
   # Or use: ./server.sh shell
   ```

2. **Test admin panel**: Visit https://scitex.ai/admin/

3. **Test all application features** via web browser

4. **Setup monitoring** (optional):
   ```bash
   bash scripts/prod/monitor_prod.sh
   ```

5. **Configure backups** for database and media files

### 🐛 Known Issues

1. **RuntimeWarning during startup**: "Accessing the database during app initialization is discouraged"
   - **Impact**: Non-critical - app works fine
   - **Cause**: Some AppConfig.ready() method queries database during startup
   - **Fix**: Review AppConfig.ready() methods to defer database queries

2. **Firewall status**: Currently inactive
   - Consider enabling: `sudo ufw enable` (after allowing OpenSSH and Nginx Full)

### 🛠️ Server Management Commands

```bash
# Using server.sh (recommended)
./server.sh start -m prod -d    # Start production server as daemon
./server.sh stop                # Stop all servers
./server.sh restart -m prod     # Restart production
./server.sh status              # Check status
./server.sh logs                # View logs
./server.sh migrate             # Run migrations
./server.sh static              # Collect static files

# Using deployment scripts
sudo bash scripts/prod/deploy_prod.sh --deploy    # Full deployment
sudo bash scripts/prod/deploy_prod.sh --install   # Install services only
sudo bash scripts/prod/deploy_prod.sh --restart   # Restart services
sudo bash scripts/prod/deploy_prod.sh --check     # Verify deployment
```

---

**Last Updated**: 2025-10-19 13:30
**Maintained By**: ywatanabe
**Server**: 162.43.35.139 (SciTeX)
**Status**: 🟢 **DEPLOYED AND RUNNING** at https://scitex.ai

<!-- EOF -->