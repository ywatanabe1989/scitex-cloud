<!-- ---
!-- Timestamp: 2025-10-18 20:29:16
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/config/deployment/nginx/README_FROM_ANOTHER_BRANCH.md
!-- --- -->

# Nginx Configuration for SciTeX Cloud

## Active Configuration

**Current:** `scitex-https.conf`
- Production setup with **uWSGI** backend
- HTTPS with Let's Encrypt SSL certificates
- Serves at: https://scitex.ai

## Architecture

```
Browser → Nginx (443) → uWSGI (Unix socket) → Django
```

## Setup Instructions

### Initial Setup

```bash
# # 1. [BE CAREFUL] Link system nginx.conf (for reference, optional)
# # This overrides system nginx.conf
# sudo cp \
#     /home/ywatanabe/proj/scitex-cloud/config/deployment/nginx/nginx.conf
#     /home/ywatanabe/proj/scitex-cloud/config/deployment/nginx/nginx.conf.back
# sudo ln -sfr \
#     /home/ywatanabe/proj/scitex-cloud/config/deployment/nginx/nginx.conf \
#     /etc/nginx/nginx.conf

# 2. Link site-specific config
sudo ln -sfr \
    /home/ywatanabe/proj/scitex-cloud/config/deployment/nginx/scitex-https.conf \
    /etc/nginx/sites-available/scitex-https.conf

sudo ln -sfr \
    /etc/nginx/sites-available/scitex-https.conf \
    /etc/nginx/sites-enabled/scitex-https.conf

# 3. Test nginx configuration
sudo nginx -t

# 4. Reload nginx
sudo systemctl reload nginx

# 5. Start uWSGI
source /home/ywatanabe/.dotfiles/.bash.d/secrets/001_ENV_SCITEX.src
./server.sh -m prod

# 6. Check log
tail -f /home/ywatanabe/proj/scitex-cloud/logs/uwsgi.log
```

### Update Configuration

```bash
# After editing scitex-https.conf
sudo nginx -t
sudo systemctl reload nginx
```

## Server Management

### Start Production Server
```bash
./server.sh -m prod
```

### Stop Server
```bash
./server.sh stop
```

### Check Status
```bash
./server.sh status
```

### View Logs
```bash
./server.sh logs
```

## File Structure

```
nginx/
├── README.md              # This file
├── scitex-https.conf      # Active production config (uWSGI)
└── archived/              # Old configs (reference only)
```

## Configuration Details

### scitex-https.conf
- **Backend**: uWSGI via Unix socket
- **Socket**: `/home/ywatanabe/proj/scitex-cloud/uwsgi.sock`
- **Protocol**: uwsgi_pass
- **SSL**: Let's Encrypt certificates
- **Static files**: Served directly by Nginx
- **Logs**: `/home/ywatanabe/proj/scitex-cloud/logs/nginx_*.log`

## Troubleshooting

### Bad Gateway (502)
```bash
# Check if uWSGI is running
ps aux | grep uwsgi

# Check uWSGI logs
tail -f /home/ywatanabe/proj/scitex-cloud/logs/uwsgi.log

# Check nginx error logs
tail -f /home/ywatanabe/proj/scitex-cloud/logs/nginx_error.log

# Restart uWSGI
./server.sh stop
./server.sh -m prod
```

### Socket Permission Issues
```bash
# Check socket exists
ls -la /home/ywatanabe/proj/scitex-cloud/uwsgi.sock

# Check nginx can access it
sudo -u www-data test -r /home/ywatanabe/proj/scitex-cloud/uwsgi.sock && echo "OK" || echo "FAIL"
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
./server.sh static

# Check permissions
ls -la /home/ywatanabe/proj/scitex-cloud/staticfiles/

# Check nginx config paths match
grep static /home/ywatanabe/proj/scitex-cloud/config/deployment/nginx/scitex-https.conf
```

## Important Notes

- **Production uses uWSGI only** (no Gunicorn)
- Socket location: `/home/ywatanabe/proj/scitex-cloud/uwsgi.sock`
- uWSGI config: `/home/ywatanabe/proj/scitex-cloud/config/deployment/uwsgi/uwsgi_production.ini`
- Always test nginx config before reloading: `sudo nginx -t`
- Environment variable required: `SCITEX_CLOUD_DJANGO_SECRET_KEY`

<!-- EOF -->