<!-- ---
!-- Timestamp: 2025-10-26 03:26:01
!-- Author: ywatanabe
!-- File: /ssh:scitex:/home/ywatanabe/proj/scitex-cloud/containers/docker/README_PROD.md
!-- --- -->

# SciTeX Cloud - Production Deployment

**Status:** ✅ Successfully Deployed (2025-10-26)
**Server:** scitex.ai (162.43.35.139)
**Docker:** v28.2.2, docker-compose v1.29.2

---

## Quick Deploy (Tested & Working)

```bash
SUDO_PASSWORD="YOUR_PASSWORD"
cd /home/ywatanabe/proj/scitex-cloud/containers/docker

# 1. Prepare environment files
/bin/cp .env.prod .env
rm -f /home/ywatanabe/proj/scitex-cloud/.env
/bin/cp .env /home/ywatanabe/proj/scitex-cloud/.env

# 2. Stop conflicting services
echo "$SUDO_PASSWORD" | sudo -S systemctl stop nginx uwsgi_prod 2>/dev/null || true

# 3. Clean up old containers (important to avoid ContainerConfig error)
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml down
echo "$SUDO_PASSWORD" | sudo -S docker rm -f docker_db_1 docker_web_1 docker_redis_1 docker_nginx_1 2>/dev/null || true

# 4. Build images (~5 min)
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml build

# 5. Start all services with force recreate
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml up -d --force-recreate

# 6. Wait for automatic initialization
# - Scitex package installation
# - Database migrations
# - Static files collection (427 files)
sleep 60

# 7. Verify deployment
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml ps

# 8. Test endpoints
curl -I -k https://localhost
curl -I -k https://localhost/admin/

# 9. Create admin user
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

**✅ Deployment successful!**

**Access site:**
- https://scitex.ai
- https://localhost

**Note:** Browser will show SSL warning (self-signed certificate). Type `thisisunsafe` to bypass or see SSL section below.

---

## What Happens Automatically

The entrypoint script (`/app/containers/docker/scripts/entrypoint.sh`) handles:

1. ✅ **Scitex package installation** - Mounts `/scitex-code` and installs editable mode
2. ✅ **Database connection wait** - Uses netcat to wait for PostgreSQL
3. ✅ **Database migrations** - Runs `python manage.py migrate --noinput`
4. ✅ **Static files** - Collects 427 files to `/app/staticfiles`
5. ✅ **Application startup** - Starts Gunicorn with 6 workers

**No manual migrations or collectstatic needed!**

---

## Deployed Architecture

```
Internet (port 443/80)
    ↓
docker_nginx_1 (nginx:alpine)
  - SSL/TLS termination
  - Static/media serving
  - Reverse proxy
    ↓
docker_web_1 (Python 3.11 + Gunicorn)
  - Django application
  - 6 workers, 2 threads
  - Scitex package (editable from /scitex-code)
    ↓
docker_db_1 (postgres:15-alpine)
  - Database: scitex_cloud_prod
  - User: scitex_prod

docker_redis_1 (redis:7-alpine)
  - Cache layer
  - Session storage
```

---

## Service Status

Check with:
```bash
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml ps
```

**Expected output:**
```
NAME                  STATE            PORTS
docker_web_1          Up (healthy)     8000/tcp
docker_db_1           Up (healthy)     5432/tcp
docker_redis_1        Up (healthy)     6379/tcp
docker_nginx_1        Up               0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

---

## SSL Certificate Setup

### Current: Self-Signed Certificate (Testing)

**Location:** `/home/ywatanabe/proj/scitex-cloud/ssl/`
- `fullchain.pem` - Public certificate
- `privkey.pem` - Private key
- **Valid:** 365 days (until 2026-10-25)

**Browser Warning:** "Your connection is not private" - **This is normal**
- **Bypass:** Type `thisisunsafe` on the warning page
- Or click "Advanced" → "Proceed to scitex.ai (unsafe)"

### Production: Let's Encrypt (Commented for Reference)

<!--
```bash
# 1. Stop Docker nginx temporarily
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml stop nginx

# 2. Install certbot
sudo apt install certbot

# 3. Obtain certificates (standalone mode)
sudo certbot certonly --standalone -d scitex.ai -d www.scitex.ai

# 4. Copy certificates to project
sudo cp /etc/letsencrypt/live/scitex.ai/fullchain.pem /home/ywatanabe/proj/scitex-cloud/ssl/
sudo cp /etc/letsencrypt/live/scitex.ai/privkey.pem /home/ywatanabe/proj/scitex-cloud/ssl/
sudo chmod 644 /home/ywatanabe/proj/scitex-cloud/ssl/*.pem

# 5. Restart nginx
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml up -d nginx

# 6. Setup auto-renewal (optional)
sudo crontab -e
# Add: 0 3 * * 0 certbot renew --quiet && docker-compose -f /home/ywatanabe/proj/scitex-cloud/containers/docker/docker-compose.prod.yml restart nginx
```
-->

---

## Management Commands

### View Status
```bash
cd /home/ywatanabe/proj/scitex-cloud/containers/docker

echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml ps
```

### View Logs
```bash
# All services
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml logs -f

# Web only (most useful)
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml logs -f web

# Last 100 lines
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml logs --tail=100 web
```

### Restart Services
```bash
# Restart all
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml restart

# Restart specific service
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml restart web
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml restart nginx
```

### Stop Services
```bash
# Stop (keeps data)
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml down

# Stop and remove all data (DANGEROUS!)
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml down -v
```

### Database Backup
```bash
cd /home/ywatanabe/proj/scitex-cloud/containers/docker

# Create backup
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml exec -T db \
  pg_dump -U scitex_prod -d scitex_cloud_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Compress backup
gzip backup_*.sql

# Restore from backup
gunzip -c backup_20251026_120000.sql.gz | \
  echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml exec -T db \
  psql -U scitex_prod -d scitex_cloud_prod
```

---

## Update Application

```bash
cd /home/ywatanabe/proj/scitex-cloud

# 1. Pull latest code
git pull

# 2. Rebuild and restart
cd containers/docker
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml build web
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml down
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml up -d

# Migrations and static files are handled automatically by entrypoint!
```

---

## Create Admin User

```bash
cd /home/ywatanabe/proj/scitex-cloud/containers/docker

echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Prompts:
# Username: admin
# Email: admin@scitex.ai
# Password: <secure-password>
```

**Login:** https://scitex.ai/admin/

---

## Troubleshooting

### POSTGRES_DB Variable Warnings

**Symptom:** `WARNING: The POSTGRES_DB variable is not set`

**Fix:**
```bash
# Ensure .env exists (docker-compose v1.29 only reads .env, not .env.prod)
/bin/cp .env.prod .env

# Restart
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml down
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml up -d
```

### ContainerConfig Error

**Symptom:** `KeyError: 'ContainerConfig'`

**Fix:** Remove old containers completely
```bash
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml down
echo "$SUDO_PASSWORD" | sudo -S docker rm -f docker_db_1 docker_web_1 docker_redis_1 docker_nginx_1
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml up -d --force-recreate
```

### ModuleNotFoundError: scitex

**Symptom:** Web container fails with "No module named 'scitex'"

**Fix:** Already handled by entrypoint script. Check logs:
```bash
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml logs web | grep "Scitex package installed"
```

Should show: "Successfully installed scitex-2.1.0"

### SECRET_KEY Empty Error

**Symptom:** `The SECRET_KEY setting must not be empty`

**Fix:** Environment files must be in correct locations
```bash
# Copy to both locations
/bin/cp .env.prod .env
rm -f /home/ywatanabe/proj/scitex-cloud/.env
/bin/cp .env /home/ywatanabe/proj/scitex-cloud/.env

# Restart
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml down
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml up -d --force-recreate
```

### Port 80/443 Already in Use

**Symptom:** `failed to bind host port 0.0.0.0:80`

**Fix:**
```bash
# Check what's using ports
sudo lsof -i :80
sudo lsof -i :443

# Stop system nginx/uwsgi
echo "$SUDO_PASSWORD" | sudo -S systemctl stop nginx uwsgi_prod uwsgi_dev

# Restart Docker services
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml up -d
```

### Web Container Not Healthy

**Check logs:**
```bash
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml logs web | tail -100
```

**Look for:**
- "Scitex package installed!" - ✅
- "Database is ready!" - ✅
- "Running migrations..." - ✅
- "Collecting static files..." - ✅
- "Starting application..." - ✅

---

## Key Configuration Details

### Environment Variables (.env)

**Critical settings:**
```bash
# Django
DEBUG=False
SECRET_KEY=CHANGE_THIS_SECRET_KEY
SCITEX_DJANGO_SECRET_KEY=CHANGE_THIS_SECRET_KEY
DJANGO_SETTINGS_MODULE=config.settings.settings_prod

# Database (must use 'db' not 'localhost')
POSTGRES_DB=scitex_cloud_prod
POSTGRES_USER=scitex_prod
POSTGRES_PASSWORD=CHANGE_THIS_PASSWORD
SCITEX_CLOUD_DB_HOST_PROD=db
SCITEX_CLOUD_DB_PORT_PROD=5432

# Environment
SCITEX_CLOUD_ENV=production
```

### Docker Volumes

| Volume | Purpose | Data |
|--------|---------|------|
| postgres_data | PostgreSQL database | Persistent |
| redis_data | Redis cache | Persistent |
| static_volume | CSS/JS files | Auto-generated |
| media_volume | User uploads | Persistent |
| /scitex-code | Scitex package (editable) | Host mount |

### Ports

| Service | Internal | External | Access |
|---------|----------|----------|--------|
| nginx | - | 80, 443 | Public |
| web | 8000 | - | Internal only |
| db | 5432 | - | Internal only |
| redis | 6379 | - | Internal only |

---

## Files Reference

```
/home/ywatanabe/proj/scitex-cloud/
├── .env                                    # ✅ Django environment (copied from containers/docker/.env)
├── requirements.txt                        # ✅ Python dependencies (copied from deployment/)
├── ssl/
│   ├── fullchain.pem                       # ✅ SSL certificate (self-signed, valid 365 days)
│   └── privkey.pem                         # ✅ SSL private key
├── containers/docker/
│   ├── .env                                # ✅ Docker Compose environment
│   ├── .env.prod                           # ✅ Production template
│   ├── docker-compose.prod.yml             # ✅ Production services config
│   ├── Dockerfile                          # ✅ Web container image
│   ├── scripts/
│   │   └── entrypoint.sh                   # ✅ Auto-setup script
│   ├── nginx/
│   │   └── nginx_prod.conf                 # ✅ Nginx configuration
│   ├── README_PROD.md                      # ✅ This file
│   └── DOCKER_SETUP.md                     # Docker installation guide
```

---

## Production Checklist

**Completed:**
- [x] Docker installed and configured
- [x] Environment variables configured
- [x] SSL certificates created (self-signed)
- [x] Database setup (PostgreSQL)
- [x] Redis cache configured
- [x] Nginx reverse proxy
- [x] Scitex package integration
- [x] Auto-migrations enabled
- [x] Auto-static collection enabled
- [x] All services healthy

**For production use:**
- [ ] Replace self-signed SSL with Let's Encrypt (see commented section above)
- [ ] Create admin user account
- [ ] Change database password from default
- [ ] Setup automated database backups
- [ ] Configure monitoring/alerting
- [ ] Review and update `.env.prod` security settings
- [ ] Configure firewall (allow only 22, 80, 443)
- [ ] Setup log rotation
- [ ] Test all functionality

---

## Quick Reference Commands

```bash
# Navigate to docker directory
cd /home/ywatanabe/proj/scitex-cloud/containers/docker

# Status
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml ps

# Logs
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml logs -f web

# Restart
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml restart

# Django shell
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml exec web python manage.py shell

# Database shell
echo "$SUDO_PASSWORD" | sudo -S docker-compose -f docker-compose.prod.yml exec db psql -U scitex_prod -d scitex_cloud_prod
```

---

**Deployment successful! Site is live at https://scitex.ai** 🚀

**Docker setup guide:** `DOCKER_SETUP.md`
**Development setup:** `README.md`

<!-- EOF -->