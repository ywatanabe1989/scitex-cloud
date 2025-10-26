<!-- ---
!-- Timestamp: 2025-10-26 12:29:55
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/containers/docker/README_NAS.md
!-- --- -->

# SciTeX Cloud - NAS Deployment with Cloudflare Tunnel

**Environment:** Synology DXP480T Plus (Home NAS)
**Method:** Cloudflare Tunnel (Zero Trust)
**Benefits:** No router access or port forwarding needed!

---

## NAS Specifications

- **Device:** Synology DXP480T Plus
- **CPU:** Intel i5-1235U (10 cores, 12 threads)
- **RAM:** 64 GB
- **IP:** 168.254.11.30 (local)
- **Domain:** scitex.ai (via Cloudflare Tunnel)

---

## Quick Deploy (Copy-Paste Ready)

```bash
BLACK='\033[0;30m'
LIGHT_GRAY='\033[0;37m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${LIGHT_GRAY}INFO: $1${NC}"; }
echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; }

# Helper: Wait for web container to be healthy
wait_for_web_healthy_nas() {
    echo_info "Waiting for web container to be healthy..."
    local START_TIME=$SECONDS
    local TIMEOUT=300

    timeout $TIMEOUT bash -c '
        while ! sudo docker-compose -f docker-compose.nas.yml ps | grep docker_web_1 | grep -q "Up (healthy)"; do
            # Show last 3 lines of logs
            LAST_LINES=$(sudo docker logs docker_web_1 2>&1 | tail -3 | tr "\n" " ")
            ELAPSED=$((SECONDS - START_TIME))
            printf "\033[0;37m  [%3d s] Status: %s\033[0m\n" "$ELAPSED" "$LAST_LINES"
            sleep 10
        done
    ' || {
        echo_warning "Timeout after ${TIMEOUT}s"
        echo_info "Check logs: sudo docker-compose -f docker-compose.nas.yml logs web"
        return 1
    }

    if sudo docker-compose -f docker-compose.nas.yml ps | grep docker_web_1 | grep -q "Up (healthy)"; then
        echo_success "Web container is healthy! (took $((SECONDS - START_TIME))s)"
        return 0
    fi
    return 1
}

start_nas() {
    # Run on NAS (Synology)
    cd /volume1/docker/scitex-cloud/containers/docker

    # 1. Prepare environment files (from gitignored SECRET directory)
    /bin/cp ~/proj/scitex-cloud/SECRET/.env.nas .env
    rm -f /volume1/docker/scitex-cloud/.env
    cp .env /volume1/docker/scitex-cloud/.env

    # 2. Stop any conflicting services (NAS might have services running)
    sudo systemctl stop nginx 2>/dev/null || true
    sudo systemctl stop gitea 2>/dev/null || true

    # 2.1. Verify ports are free (Gitea only - nginx is internal)
    lsof -i :${SCITEX_CLOUD_GITEA_HTTP_PORT_NAS:-3000} || echo_success "Port ${SCITEX_CLOUD_GITEA_HTTP_PORT_NAS:-3000} is free (Gitea)"

    # 3. Clean up old containers (preserves database volumes)
    echo_info "Cleaning up old containers..."
    sudo docker-compose -f docker-compose.nas.yml down
    sudo docker rm -f docker_db_1 docker_web_1 docker_redis_1 docker_nginx_1 docker_gitea_1 docker_cloudflared_1 \
        2>/dev/null || true

    # 4. Check database credentials compatibility
    if docker volume inspect docker_postgres_data >/dev/null 2>&1; then
        echo_info "Database volume exists, checking credentials..."
        sudo docker-compose -f docker-compose.nas.yml up -d db
        sleep 3
        if ! sudo docker-compose -f docker-compose.nas.yml exec -T db \
            psql -U "${POSTGRES_USER}" \
                 -d "${POSTGRES_DB}" \
                 -c "SELECT 1" >/dev/null 2>&1; then
            echo_warning "Credentials mismatch detected!"
            echo_warning "Manually recreate with: sudo docker-compose -f docker-compose.nas.yml down -v"
            sudo docker-compose -f docker-compose.nas.yml down
            return 1
        else
            echo_success "Credentials valid, reusing existing database"
            sudo docker-compose -f docker-compose.nas.yml down
        fi
    fi

    # 5. Build images (~5 min on NAS)
    echo_info "Building images..."
    sudo docker-compose -f docker-compose.nas.yml build

    # 6. Start all services
    echo_info "Starting all services..."
    sudo docker-compose -f docker-compose.nas.yml up -d

    # 6.1. Wait for Gitea to be healthy
    echo_info "Waiting for Gitea to be ready..."
    timeout 60 bash -c 'until sudo docker-compose -f docker-compose.nas.yml ps | grep docker_gitea_1 | grep -q "Up (healthy)"; do sleep 2; done' \
        && echo_success "Gitea is ready!" \
        || echo_warning "Gitea taking longer than expected, continuing anyway..."

    # 6.2. Wait for Cloudflare Tunnel to be healthy
    echo_info "Waiting for Cloudflare Tunnel to connect..."
    timeout 30 bash -c 'until sudo docker-compose -f docker-compose.nas.yml ps | grep docker_cloudflared_1 | grep -q "Up (healthy)"; do sleep 2; done' \
        && echo_success "Cloudflare Tunnel connected!" \
        || echo_warning "Cloudflare Tunnel taking longer, check token configuration"

    # 7. Wait for web container to be healthy
    wait_for_web_healthy_nas

    # 8. Verify deployment
    echo_info "Deployment status:"
    sudo docker-compose -f docker-compose.nas.yml ps

    # 9. Test endpoints
    echo_info "Testing endpoints..."
    echo_info "Local nginx: http://localhost (internal only)"
    curl -I http://localhost
    echo_info ""
    echo_info "Public site (via Cloudflare Tunnel): https://scitex.ai"
    echo_success "If Cloudflare Tunnel is healthy, site should be live at https://scitex.ai"

    # # 10. Create admin user (optional)
    # sudo docker-compose -f docker-compose.nas.yml exec web python manage.py createsuperuser
}

restart_nas() {
    cd /volume1/docker/scitex-cloud/containers/docker

    echo_info "Restarting web container..."
    sudo docker-compose -f docker-compose.nas.yml restart web

    # Wait for web container to be healthy
    wait_for_web_healthy_nas

    # Show status
    echo_info "Deployment status:"
    sudo docker-compose -f docker-compose.nas.yml ps

    # Test endpoints
    echo_info "Testing endpoints..."
    curl -I http://localhost
    echo_success "Public site: https://scitex.ai"
}

start_nas
```

**✅ NAS deployment ready!**

**Access site:**
- https://scitex.ai (via Cloudflare Tunnel)
- http://168.254.11.30 (NAS local network only)

---

## What Happens Automatically

The entrypoint script handles:

1. ✅ **Scitex package installation** - Mounts `/scitex-code` and installs editable mode
2. ✅ **Database connection wait** - Waits for PostgreSQL to be ready
3. ✅ **Database migrations** - Runs `python manage.py migrate --noinput`
4. ✅ **Static files** - Collects static files to `/app/staticfiles`
5. ✅ **Application startup** - Starts Gunicorn with 6 workers
6. ✅ **Cloudflare Tunnel** - Connects to Cloudflare for public HTTPS access

**No manual migrations or collectstatic needed!**

---

## NAS Deployment Architecture

```
Internet (HTTPS)
    ↓
Cloudflare (SSL/DDoS protection)
    ↓ (Cloudflare Tunnel - encrypted)
docker_cloudflared_1
    ↓
docker_nginx_1 (internal HTTP:80)
  - Static/media serving
  - Reverse proxy
    ↓
docker_web_1 (Gunicorn:8000)
  - Django application
  - 6 workers, 2 threads
  - Scitex package (editable)
    ↓
docker_db_1 (postgres:15-alpine)
  - Database: scitex_cloud_nas

docker_redis_1 (redis:7-alpine)
  - Cache layer

docker_gitea_1 (gitea:latest)
  - Git server
  - Port 3000 (can be accessed via tunnel or local network)
```

---

## Service Status

Check with:
```bash
cd /volume1/docker/scitex-cloud/containers/docker
sudo docker-compose -f docker-compose.nas.yml ps
```

**Expected output:**
```
NAME                  STATE            PORTS
docker_web_1          Up (healthy)     8000/tcp
docker_db_1           Up (healthy)     5432/tcp
docker_redis_1        Up (healthy)     6379/tcp
docker_nginx_1        Up               80/tcp
docker_gitea_1        Up (healthy)     0.0.0.0:3000->3000/tcp, 0.0.0.0:222->22/tcp
docker_cloudflared_1  Up (healthy)     -
```

---

## Management Commands

### View Status
```bash
cd /volume1/docker/scitex-cloud/containers/docker
sudo docker-compose -f docker-compose.nas.yml ps
```

### View Logs
```bash
# All services
sudo docker-compose -f docker-compose.nas.yml logs -f

# Web only
sudo docker-compose -f docker-compose.nas.yml logs -f web

# Cloudflare Tunnel
sudo docker-compose -f docker-compose.nas.yml logs -f cloudflared

# Last 100 lines
sudo docker-compose -f docker-compose.nas.yml logs --tail=100 web
```

### Restart Services
```bash
# Restart all
sudo docker-compose -f docker-compose.nas.yml restart

# Restart specific service
sudo docker-compose -f docker-compose.nas.yml restart web
sudo docker-compose -f docker-compose.nas.yml restart cloudflared
```

### Stop Services
```bash
# Stop (keeps data)
sudo docker-compose -f docker-compose.nas.yml down

# Stop and remove all data (DANGEROUS!)
sudo docker-compose -f docker-compose.nas.yml down -v
```

### Update Application
```bash
cd /volume1/docker/scitex-cloud

# 1. Pull latest code (from your dev machine, use rsync)
# rsync -avz ~/proj/scitex-cloud/ ywatanabe@168.254.11.30:/volume1/docker/scitex-cloud/

# 2. Rebuild and restart
cd containers/docker
sudo docker-compose -f docker-compose.nas.yml build web
sudo docker-compose -f docker-compose.nas.yml down
sudo docker-compose -f docker-compose.nas.yml up -d

# Migrations and static files handled automatically by entrypoint!
```

---

## Cloudflare Tunnel Setup

### Prerequisites
1. Cloudflare account (free)
2. Domain `scitex.ai` added to Cloudflare
3. Tunnel created in Cloudflare Dashboard

### Create Tunnel (Cloudflare Dashboard)

1. Go to: https://dash.cloudflare.com
2. Select domain: `scitex.ai`
3. **Zero Trust** > **Networks** > **Tunnels**
4. **Create a tunnel**
5. Name: `scitex-nas`
6. Copy the token
7. Configure routes:
   - `scitex.ai` → `http://nginx:80`
   - `www.scitex.ai` → `http://nginx:80`
   - `git.scitex.ai` → `http://gitea:3000` (optional)

### Add Token to .env

```bash
# In /volume1/docker/scitex-cloud/containers/docker/.env
SCITEX_CLOUD_CLOUDFLARE_TUNNEL_TOKEN_NAS=your-actual-token-here
```

---

## Troubleshooting

### Cloudflare Tunnel Unhealthy

**Check logs:**
```bash
sudo docker-compose -f docker-compose.nas.yml logs cloudflared
```

**Common issues:**
- Invalid token → Check .env file
- Network issue → Check NAS internet connection
- Service not found → Check nginx container is running

### Site Shows 502 Bad Gateway

**Fix:**
```bash
# Check if web service is healthy
sudo docker-compose -f docker-compose.nas.yml ps web

# Check nginx logs
sudo docker-compose -f docker-compose.nas.yml logs nginx

# Restart nginx
sudo docker-compose -f docker-compose.nas.yml restart nginx
```

### Database Connection Failed

```bash
# Check database is healthy
sudo docker-compose -f docker-compose.nas.yml ps db

# Verify credentials in .env
grep POSTGRES .env

# Recreate with new credentials
sudo docker-compose -f docker-compose.nas.yml down -v
sudo docker-compose -f docker-compose.nas.yml up -d
```

---

## Files Reference

```
/volume1/docker/scitex-cloud/
├── .env                                # Django environment (copied from containers/docker/.env)
├── requirements.txt                    # Python dependencies
├── containers/docker/
│   ├── .env                            # Docker Compose environment
│   ├── .env.nas.example                # NAS template
│   ├── docker-compose.nas.yml          # NAS services config
│   ├── Dockerfile                      # Web container image
│   ├── scripts/
│   │   └── entrypoint.sh               # Auto-setup script
│   ├── nginx/
│   │   └── nginx_nas.conf              # Nginx for Cloudflare Tunnel
│   └── README_NAS.md                   # This file
```

---

## Migration from Rental Server

### Phase 1: Parallel Testing
```bash
# Deploy to NAS with test subdomain
# In Cloudflare: test.scitex.ai → nginx:80
start_nas
```

### Phase 2: Full Migration
```bash
# 1. Backup from rental server
# 2. Restore to NAS
# 3. Update Cloudflare route: scitex.ai → nginx:80
# 4. Test!
```

---

## Quick Reference Commands

```bash
# Navigate to docker directory on NAS
cd /volume1/docker/scitex-cloud/containers/docker

# Start services
sudo docker-compose -f docker-compose.nas.yml up -d

# Check status
sudo docker-compose -f docker-compose.nas.yml ps

# View logs
sudo docker-compose -f docker-compose.nas.yml logs -f web

# Restart
sudo docker-compose -f docker-compose.nas.yml restart

# Django shell
sudo docker-compose -f docker-compose.nas.yml exec web python manage.py shell

# Database shell
sudo docker-compose -f docker-compose.nas.yml exec db psql -U scitex_nas -d scitex_cloud_nas
```

---

**Deployment ready! Site accessible at https://scitex.ai via Cloudflare Tunnel** 🚀

**Development setup:** `README_DEV.md`
**Production setup:** `README_PROD.md`
**NAS path:** `/volume1/docker/scitex-cloud/`

<!-- EOF -->