<!-- ---
!-- Timestamp: 2025-10-18 21:40:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/deployment/nginx/README.md
!-- --- -->

# Nginx Configuration for SciTeX Cloud

## Overview

This directory contains Nginx configurations for SciTeX Cloud in both development and production environments.

## Active Configurations

### Development: `scitex_cloud_dev.conf`
- HTTP only (no SSL)
- Uses uWSGI backend via Unix socket
- Serves at: http://localhost or http://scitex.local

### Production: `scitex_cloud_prod.conf`
- HTTPS with Let's Encrypt SSL certificates
- HTTP → HTTPS redirect
- Uses uWSGI backend via Unix socket
- Serves at: https://scitex.ai

## Architecture

```
Browser → Nginx (80/443) → uWSGI (Unix socket) → Django
```

## Development Setup

### 1. Link Development Config

```bash
SCITEX_NGINX_DIR=/home/ywatanabe/proj/scitex-cloud/deployment/nginx

# Link site-specific config
sudo ln -sf \
    "$SCITEX_NGINX_DIR"/scitex_cloud_dev.conf \
    /etc/nginx/sites-available/scitex_cloud_dev.conf

sudo ln -sf \
    /etc/nginx/sites-available/scitex_cloud_dev.conf \
    /etc/nginx/sites-enabled/scitex_cloud_dev.conf

# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### 2. Start Development Server

```bash
# Using uWSGI
uwsgi --ini deployment/uwsgi/scitex_cloud_dev.ini

# Or using Django dev server (simpler)
python manage.py runserver
```

## Production Setup

### Initial Setup

```bash
SCITEX_NGINX_DIR=/home/ywatanabe/proj/scitex-cloud/deployment/nginx

# 1. Link production config
sudo ln -sf \
    "$SCITEX_NGINX_DIR"/scitex_cloud_prod.conf \
    /etc/nginx/sites-available/scitex_cloud

sudo ln -sf \
    /etc/nginx/sites-available/scitex_cloud \
    /etc/nginx/sites-enabled/scitex_cloud

# 2. Test nginx configuration
sudo nginx -t

# 3. Setup SSL with Let's Encrypt
sudo certbot --nginx -d scitex.ai -d www.scitex.ai

# 4. Reload nginx
sudo systemctl reload nginx

# 5. Start uWSGI service
sudo systemctl enable scitex_cloud
sudo systemctl start scitex_cloud

# 6. Check logs
sudo journalctl -u scitex_cloud -f
```

### Update Configuration

```bash
# After editing nginx config
sudo nginx -t
sudo systemctl reload nginx
```

## Server Management

### Control uWSGI Service

```bash
# Start
sudo systemctl start scitex_cloud

# Stop
sudo systemctl stop scitex_cloud

# Restart
sudo systemctl restart scitex_cloud

# Status
sudo systemctl status scitex_cloud
```

### View Logs

```bash
# uWSGI logs
sudo journalctl -u scitex_cloud -f
sudo tail -f /var/log/uwsgi/scitex_cloud.log

# Nginx logs
sudo tail -f /var/log/nginx/scitex_cloud_access.log
sudo tail -f /var/log/nginx/scitex_cloud_error.log
```

## File Structure

```
nginx/
├── README.md                   # This file
├── scitex_cloud_dev.conf       # Development config (HTTP)
├── scitex_cloud_prod.conf      # Production config (HTTPS)
└── README_FROM_ANOTHER_BRANCH.md  # Legacy reference
```

## Configuration Details

### Development (`scitex_cloud_dev.conf`)
- **Protocol**: HTTP only
- **Backend**: uWSGI via Unix socket
- **Socket**: `/run/scitex_cloud.sock`
- **Static files**: Served directly by Nginx
- **Location**: Works in `~/proj/scitex-cloud`

### Production (`scitex_cloud_prod.conf`)
- **Protocol**: HTTPS with SSL
- **Backend**: uWSGI via Unix socket
- **Socket**: `/run/scitex_cloud.sock`
- **SSL**: Let's Encrypt certificates
- **Static files**: Served directly by Nginx with caching
- **Security headers**: Enabled
- **Location**: Works in `/var/www/scitex-cloud` (or current location)

## Troubleshooting

### Bad Gateway (502)

```bash
# Check if uWSGI is running
ps aux | grep uwsgi
sudo systemctl status scitex_cloud

# Check uWSGI logs
sudo journalctl -u scitex_cloud -f
sudo tail -f /var/log/uwsgi/scitex_cloud.log

# Check nginx error logs
sudo tail -f /var/log/nginx/scitex_cloud_error.log

# Restart uWSGI
sudo systemctl restart scitex_cloud
```

### Socket Permission Issues

```bash
# Check socket exists
ls -la /run/scitex_cloud.sock

# Check nginx can access it
sudo -u www-data test -r /run/scitex_cloud.sock && echo "OK" || echo "FAIL"

# Fix permissions (if needed)
sudo chmod 666 /run/scitex_cloud.sock
```

### SSL Certificate Issues

```bash
# Check expiry
sudo certbot certificates

# Renew certificates
sudo certbot renew

# Reload nginx after renewal
sudo systemctl reload nginx
```

### Static Files Not Loading

```bash
# Collect static files
python manage.py collectstatic --noinput

# Check permissions
ls -la ./staticfiles/

# Check nginx config paths match
grep static deployment/nginx/scitex_cloud_prod.conf
```

### PostgreSQL Connection Issues

```bash
# Check PostgreSQL is running
pg_isready
sudo service postgresql status

# Check database connection
psql -U scitex_dev -d scitex_cloud_dev -c "SELECT version();"

# Check Django can connect
python manage.py dbshell
```

## Important Notes

### Development
- Use HTTP for local development
- No SSL certificates needed
- Can use Django dev server instead of uWSGI
- PostgreSQL recommended but SQLite available as fallback

### Production
- Always use HTTPS with valid SSL certificates
- uWSGI service runs as systemd service
- PostgreSQL required (no SQLite in production)
- Environment variables required:
  - `SCITEX_CLOUD_DJANGO_SECRET_KEY`
  - `SCITEX_CLOUD_DB_PASSWORD_PROD`
- Always test nginx config before reloading: `sudo nginx -t`
- Static files must be collected: `python manage.py collectstatic`

## Migration from SQLite to PostgreSQL

If you're migrating from SQLite to PostgreSQL:

```bash
# 1. Backup current SQLite database
cp data/scitex_cloud_dev.db data/backups/scitex_cloud_dev.db.backup_$(date +%Y%m%d_%H%M%S)

# 2. Setup PostgreSQL
bash scripts/setup_postgres.sh

# 3. Export data from SQLite
python manage.py dumpdata --natural-foreign --natural-primary > data/backups/sqlite_data.json

# 4. Switch to PostgreSQL in settings
# (Already configured in settings_dev.py and settings_prod.py)

# 5. Run migrations
python manage.py migrate

# 6. Load data into PostgreSQL
python manage.py loaddata data/backups/sqlite_data.json

# 7. Create superuser (if needed)
python manage.py createsuperuser
```

See `../docs/02_POSTGRESQL_SETUP.md` for detailed PostgreSQL documentation.

## Next Steps

1. ✅ Nginx configuration files created
2. ✅ PostgreSQL setup documented
3. ⏳ Configure for your environment (dev or prod)
4. ⏳ Setup SSL certificates (production only)
5. ⏳ Test the complete stack

## See Also

- `../README.md` - Main deployment guide
- `../docs/00_QUICK_START.md` - Quick start guide
- `../docs/02_POSTGRESQL_SETUP.md` - PostgreSQL setup
- `../docs/03_UWSGI_SETUP.md` - uWSGI configuration
- `../docs/99_FILE_ORGANIZATION.md` - File organization reference
- `../../config/` - Django application configuration

<!-- EOF -->