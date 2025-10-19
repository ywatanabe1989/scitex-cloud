<!-- ---
!-- Timestamp: 2025-10-18 14:25:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/deployment/uwsgi/README.md
!-- --- -->

# uWSGI Setup Guide

uWSGI is the application server that runs Django in production.

## Overview

- **Purpose**: Run Django application as a service
- **Protocol**: HTTP and Unix socket
- **Process Management**: Master + worker processes
- **Integration**: Works with Nginx for production

## Installation

```bash
# Activate virtual environment
source .venv/bin/activate

# Install uWSGI
pip install uwsgi

# Verify installation
uwsgi --version
```

## Configuration Files

### 1. uWSGI Configuration (scitex_cloud_prod.ini)

Location: `deployment/uwsgi/scitex_cloud_prod.ini`

**Production configuration updated for:**
- Project location: `/home/ywatanabe/proj/scitex-cloud`
- Virtual environment: `.venv`
- Socket: `/run/scitex_cloud.sock`

```ini
[uwsgi]
# Django project settings - PRODUCTION
chdir = /home/ywatanabe/proj/scitex-cloud
module = config.wsgi:application
home = /home/ywatanabe/proj/scitex-cloud/.venv
env = DJANGO_SETTINGS_MODULE=config.settings.settings_prod

# Process management (Production - more workers)
master = true
processes = 8
threads = 4
max-requests = 5000
harakiri = 60
max-worker-lifetime = 3600

# Socket configuration
socket = /run/scitex_cloud.sock
chmod-socket = 666
vacuum = true

# Logging
logto = /var/log/uwsgi/scitex_cloud.log
log-maxsize = 50000000
log-backupname = /var/log/uwsgi/scitex_cloud.log.old

# Performance
enable-threads = true
lazy-apps = true
single-interpreter = true
buffer-size = 32768

# Static files (handled by Nginx in production)
static-map = /static=/home/ywatanabe/proj/scitex-cloud/staticfiles
static-map = /media=/home/ywatanabe/proj/scitex-cloud/media

# User/Group
uid = www-data
gid = www-data

# Production optimizations
cheaper = 2
cheaper-initial = 4
cheaper-step = 1
cheaper-algo = spare

# Misc
die-on-term = true
need-app = true
```

### 2. Systemd Service File (scitex_cloud_prod.service)

Location: `/etc/systemd/system/scitex_cloud_prod.service`

```ini
[Unit]
Description=uWSGI instance to serve SciTeX Cloud (Production)
After=network.target postgresql.service
Wants=postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/ywatanabe/proj/scitex-cloud
Environment="PATH=/home/ywatanabe/proj/scitex-cloud/.venv/bin"
EnvironmentFile=/home/ywatanabe/proj/scitex-cloud/deployment/dotenvs/dotenv.prod
ExecStart=/home/ywatanabe/proj/scitex-cloud/.venv/bin/uwsgi --ini /home/ywatanabe/proj/scitex-cloud/deployment/uwsgi/scitex_cloud_prod.ini

# Restart policy
Restart=always
RestartSec=10s

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

## Setup Steps

### 1. Create Log Directory

```bash
sudo mkdir -p /var/log/uwsgi
sudo chown www-data:www-data /var/log/uwsgi
```

### 2. Create uWSGI Directory

```bash
sudo mkdir -p /etc/uwsgi
```

### 3. Setup Systemd Service

```bash
# Copy systemd service
sudo cp deployment/uwsgi/scitex_cloud_prod.service /etc/systemd/system/scitex_cloud_prod.service

# Note: uWSGI config is read directly from:
# /home/ywatanabe/proj/scitex-cloud/deployment/uwsgi/scitex_cloud_prod.ini
```

### 4. Set File Permissions

```bash
# Set ownership (or add your user to www-data group)
sudo chown -R www-data:www-data /home/ywatanabe/proj/scitex-cloud
# OR add your user to www-data group
sudo usermod -aG www-data ywatanabe

# Set permissions
sudo chmod 755 /home/ywatanabe/proj/scitex-cloud
sudo chmod 600 /home/ywatanabe/proj/scitex-cloud/deployment/dotenvs/dotenv.prod
```

### 5. Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable scitex_cloud_prod

# Start service
sudo systemctl start scitex_cloud_prod

# Check status
sudo systemctl status scitex_cloud_prod
```

## Management Commands

### Service Control

```bash
# Start service
sudo systemctl start scitex_cloud_prod

# Stop service
sudo systemctl stop scitex_cloud_prod

# Restart service
sudo systemctl restart scitex_cloud_prod

# Reload configuration (no downtime)
sudo systemctl reload scitex_cloud_prod

# Check status
sudo systemctl status scitex_cloud_prod

# View logs
sudo journalctl -u scitex_cloud_prod -f
```

### Check Socket

```bash
# Verify socket exists
ls -l /run/scitex_cloud.sock

# Check socket permissions
stat /run/scitex_cloud.sock
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u scitex_cloud_prod --no-pager

# Check uWSGI logs
sudo tail -f /var/log/uwsgi/scitex_cloud.log

# Test uWSGI configuration manually
cd /home/ywatanabe/proj/scitex-cloud
.venv/bin/uwsgi --ini deployment/uwsgi/scitex_cloud_prod.ini
```

### Permission Errors

```bash
# Fix ownership
sudo chown -R www-data:www-data /home/ywatanabe/proj/scitex-cloud

# Fix socket permissions
sudo chmod 666 /run/scitex_cloud.sock
```

### Process Issues

```bash
# Check running processes
ps aux | grep uwsgi

# Kill all uWSGI processes
sudo killall -9 uwsgi

# Restart service
sudo systemctl restart scitex_cloud_prod
```

## Performance Tuning

### Worker Processes

```ini
# Formula: (2 * CPU_cores) + 1
processes = 4  # For 2 CPU cores
threads = 2    # 2 threads per process
```

### Memory Configuration

```ini
# Reload worker after X requests (prevent memory leaks)
max-requests = 5000

# Kill requests taking longer than 60 seconds
harakiri = 60

# Buffer size for requests
buffer-size = 32768
```

### Connection Limits

```ini
# Maximum queue size
listen = 128

# Maximum concurrent requests
max-worker-lifetime = 3600
```

## Monitoring

### Check Worker Status

```bash
# Via uwsgitop (install first: pip install uwsgitop)
uwsgitop /run/scitex_cloud.sock

# Via systemd
sudo systemctl status scitex_cloud_prod
```

### Memory Usage

```bash
# Check memory per process
ps aux | grep uwsgi | awk '{print $6}'

# Total memory usage
ps aux | grep uwsgi | awk '{sum+=$6} END {print sum/1024 " MB"}'
```

## Security Considerations

### Process Isolation

```ini
# Run as dedicated user
uid = www-data
gid = www-data

# Drop privileges
no-orphans = true
die-on-term = true
```

### Environment Variables

```bash
# Load from secure file
EnvironmentFile=/home/ywatanabe/proj/scitex-cloud/deployment/dotenvs/dotenv.prod

# Ensure file is secure
chmod 600 /home/ywatanabe/proj/scitex-cloud/deployment/dotenvs/dotenv.prod
```

## Configuration Files in This Directory

- **`scitex_cloud_dev.ini`** - Development config (4 processes, 2 threads)
- **`scitex_cloud_prod.ini`** - Production config (8 processes, 4 threads)
- **`scitex_cloud_prod.service`** - Systemd service file for production

## Next Steps

- **[../nginx/README.md](../nginx/README.md)** - Configure web server
- **[../README.md](../README.md)** - Back to deployment overview

<!-- EOF -->
