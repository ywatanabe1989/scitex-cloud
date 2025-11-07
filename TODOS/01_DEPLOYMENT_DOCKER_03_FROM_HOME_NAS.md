<!-- ---
!-- Timestamp: 2025-10-26 00:47:42
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/01_DEPLOYMENT_FROM_HOME_NAS.md
!-- --- -->

# Hosting scitex.ai from Home NAS (Shared House Setup)

## Overview
This guide shows how to host https://scitex.ai from your Synology NAS **without** router access or ISP coordination, using Cloudflare Tunnel.

## NAS Specifications

```
## Device Information

**Device Name:** DXP480TPLUS-994  
**Model:** DXP480T Plus  
**System Version:** 1.7.0-3125  
**Serial Number:** TCT18HM95245NAD

## Owner Information

**UserID/Data ID:** ywatanabe1989  
**Device Owner:** ywata1989@gmail.com

## Hardware Specifications

### CPU
- **Model:** 12th Gen Intel(R) Core(TM) i5-1235U
- **Cores:** 10 Cores
- **Threads:** 12 Threads

### Memory
- **Memory 1 (Channel):** CM536450X30A4800C40
  - **Capacity:** 32 GB
  - **Speed:** 4800 MHz
- **Memory 2 (Channel):** CM536450X30A4800C40
  - **Capacity:** 32 GB
  - **Speed:** 4800 MHz
- **Total RAM:** 64 GB

### Network
- **LAN1:** 168.254.11.30
- **Speed:** 1Gbps
- **Mode:** Full duplex
- **MTU:** 1500
- **MAC Address (Subnet mask):** fec:1f:f7:40:26:11 / 255.255.0.0
```



**Your situation:**
- ✅ Synology DXP480T Plus NAS (i5-1235U, 64GB RAM)
- ✅ Django app with Docker/Gunicorn ready
- ❌ Cannot modify router (shared house)
- ❌ Cannot contact ISP
- ✅ Domain: scitex.ai

**Solution:** Cloudflare Tunnel (Zero Trust)

---

## Part 1: Cloudflare Setup

### 1.1 Prerequisites
- Cloudflare account (free tier is sufficient)
- scitex.ai domain added to Cloudflare
- SSH access to your NAS

### 1.2 Create Cloudflare Tunnel

**Method A: Via Cloudflare Dashboard (Easiest)**

1. Log into Cloudflare Dashboard
2. Select your domain: `scitex.ai`
3. Go to **Zero Trust** > **Networks** > **Tunnels**
4. Click **Create a tunnel**
5. Name it: `scitex-nas-tunnel`
6. Choose **Cloudflared** connector
7. Copy the installation token (you'll need this!)

**Method B: Via CLI (Advanced)**
```bash
# Install cloudflared on your computer first
cloudflared tunnel login
cloudflared tunnel create scitex-nas-tunnel
cloudflared tunnel route dns scitex-nas-tunnel scitex.ai
```

---

## Part 2: NAS Deployment Options

You have two deployment options for your NAS:

### Option A: Docker Compose Integration (Recommended)
Add Cloudflare Tunnel as a service to your existing docker-compose setup.

### Option B: Synology Container Manager
Run Cloudflare Tunnel as a separate container in Container Manager.

---

## Part 3: Docker Compose Integration (Option A)

### 3.1 Modified docker-compose.prod.yml

Create this file: `docker-compose.cloudflare.yml`

```yaml
version: '3.8'

services:
  web:
    build:
      context: ../..
      dockerfile: containers/docker/Dockerfile
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 2 --timeout 120 --access-logfile - --error-logfile - --log-level info
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    env_file:
      - .env
    environment:
      - SCITEX_CLOUD_DJANGO_SETTINGS_MODULE=config.settings.settings_prod
      - PYTHONUNBUFFERED=1
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    restart: always
    networks:
      - scitex-network

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - SCITEX_CLOUD_POSTGRES_DB=${SCITEX_CLOUD_POSTGRES_DB}
      - SCITEX_CLOUD_POSTGRES_USER=${SCITEX_CLOUD_POSTGRES_USER}
      - SCITEX_CLOUD_POSTGRES_PASSWORD=${SCITEX_CLOUD_POSTGRES_PASSWORD}
    restart: always
    networks:
      - scitex-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${SCITEX_CLOUD_POSTGRES_USER}"]
      interval: 10s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: always
    networks:
      - scitex-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # Internal Nginx (not exposed to internet)
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx/nginx_tunnel.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
    depends_on:
      - web
    restart: always
    networks:
      - scitex-network

  # Cloudflare Tunnel (replaces port forwarding!)
  cloudflared:
    image: cloudflare/cloudflared:latest
    command: tunnel --no-autoupdate run --token ${CLOUDFLARE_TUNNEL_TOKEN}
    restart: always
    networks:
      - scitex-network
    depends_on:
      - nginx

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:

networks:
  scitex-network:
    driver: bridge
```

### 3.2 Nginx Configuration for Tunnel

Create: `containers/docker/nginx/nginx_tunnel.conf`

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 2048;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Cloudflare provides SSL, so we listen on HTTP internally
    # Cloudflare Tunnel handles HTTPS termination
    
    gzip on;
    gzip_vary on;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    upstream web {
        server web:8000;
    }

    server {
        listen 80;
        server_name _;

        # Trust Cloudflare proxy headers
        set_real_ip_from 0.0.0.0/0;
        real_ip_header CF-Connecting-IP;

        location /static/ {
            alias /app/staticfiles/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        location /media/ {
            alias /app/media/;
            expires 7d;
        }

        location / {
            proxy_pass http://web;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;  # Force HTTPS scheme
            proxy_redirect off;
            proxy_buffering off;

            # Timeouts
            proxy_connect_timeout 120s;
            proxy_send_timeout 120s;
            proxy_read_timeout 120s;
        }
    }
}
```

### 3.3 Environment Variables

Add to your `.env` file:
```bash
# Cloudflare Tunnel Token (from Cloudflare Dashboard)
CLOUDFLARE_TUNNEL_TOKEN=your-token-here

# Django settings for Cloudflare
CSRF_TRUSTED_ORIGINS=https://scitex.ai
SCITEX_CLOUD_ALLOWED_HOSTS=scitex.ai,localhost,nginx
```

---

## Part 4: Cloudflare Tunnel Configuration

### 4.1 Route Configuration (in Cloudflare Dashboard)

After creating the tunnel, configure the route:

1. **Public Hostname:** `scitex.ai`
2. **Service:** 
   - Type: `HTTP`
   - URL: `nginx:80` (or `http://nginx:80`)
3. **Additional settings:**
   - Enable **No TLS Verify** (for internal Docker network)

### 4.2 Multiple Routes (Optional)

If you want subdomains:
```
scitex.ai → nginx:80
www.scitex.ai → nginx:80
api.scitex.ai → web:8000
```

---

## Part 5: Deployment on Synology NAS

### 5.1 Prepare Your NAS

SSH into your NAS:
```bash
ssh ywatanabe@168.254.11.30
```

Create project directory:
```bash
sudo mkdir -p /volume1/docker/scitex-cloud
cd /volume1/docker/scitex-cloud
```

### 5.2 Copy Your Project

From your local machine:
```bash
# Copy entire project to NAS
rsync -avz --exclude 'node_modules' --exclude '.git' \
  ~/proj/scitex-cloud/ \
  ywatanabe@168.254.11.30:/volume1/docker/scitex-cloud/
```

### 5.3 Deploy with Docker Compose

On your NAS:
```bash
cd /volume1/docker/scitex-cloud/containers/docker

# Create .env file with your secrets
nano .env

# Build and start services
docker-compose -f docker-compose.cloudflare.yml up -d

# Check logs
docker-compose -f docker-compose.cloudflare.yml logs -f

# Run migrations
docker-compose -f docker-compose.cloudflare.yml exec web python manage.py migrate

# Collect static files
docker-compose -f docker-compose.cloudflare.yml exec web python manage.py collectstatic --noinput

# Create superuser
docker-compose -f docker-compose.cloudflare.yml exec web python manage.py createsuperuser
```

---

## Part 6: Verify Deployment

### 6.1 Check Tunnel Status

In Cloudflare Dashboard:
- Go to **Zero Trust** > **Networks** > **Tunnels**
- Your tunnel should show as **HEALTHY** (green)

### 6.2 Check Container Status

```bash
docker-compose -f docker-compose.cloudflare.yml ps
```

All services should show as "Up" or "healthy"

### 6.3 Test Access

1. Visit: https://scitex.ai
2. Should see your Django app!
3. Check SSL: Should show Cloudflare certificate (valid)

### 6.4 Troubleshooting

**Tunnel shows unhealthy:**
```bash
# Check cloudflared logs
docker-compose logs cloudflared

# Check if token is correct
grep CLOUDFLARE_TUNNEL_TOKEN .env
```

**502 Bad Gateway:**
```bash
# Check nginx logs
docker-compose logs nginx

# Check web service
docker-compose logs web

# Ensure web service is running
docker-compose ps web
```

**Static files not loading:**
```bash
# Re-collect static files
docker-compose exec web python manage.py collectstatic --noinput --clear
```

---

## Part 7: Alternative - Synology Container Manager

If you prefer using Synology's GUI:

### 7.1 Install Container Manager
1. Open **Package Center**
2. Search for **Container Manager**
3. Install

### 7.2 Create Cloudflared Container
1. Open **Container Manager**
2. Go to **Container** tab
3. Click **Create**
4. Search for: `cloudflare/cloudflared`
5. Configure:
   - Container name: `cloudflared-scitex`
   - Command: `tunnel --no-autoupdate run --token YOUR_TOKEN_HERE`
   - Network: Bridge to your web app containers
   - Auto-restart: Yes

---

## Part 8: Production Considerations

### 8.1 Monitoring

**Setup health monitoring:**
```bash
# Add to docker-compose
  healthcheck-monitor:
    image: louislam/uptime-kuma:latest
    volumes:
      - uptime_data:/app/data
    ports:
      - "3001:3001"  # Access via http://NAS_IP:3001
    restart: always
```

### 8.2 Backups

```bash
# Backup database
docker-compose exec db pg_dump -U scitex scitex_cloud > backup_$(date +%Y%m%d).sql

# Backup media files
rsync -avz /volume1/docker/scitex-cloud/media/ /volume1/backups/scitex-media/
```

### 8.3 Updates

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose -f docker-compose.cloudflare.yml up -d --build

# Run migrations
docker-compose exec web python manage.py migrate
```

### 8.4 Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f web
docker-compose logs -f cloudflared

# Last 100 lines
docker-compose logs --tail=100
```

---

## Part 9: Migration from Rental Server

### Step-by-step migration:

**Phase 1: Parallel Testing (Week 1)**
- ✅ Deploy to NAS with subdomain (test.scitex.ai)
- Test all functionality
- Monitor performance

**Phase 2: DNS Preparation (Week 2)**
- Lower TTL on scitex.ai DNS records (to 300 seconds)
- Prepare rollback plan

**Phase 3: Cutover (Day 0)**
- Take final backup from rental server
- Restore to NAS
- Update DNS: scitex.ai → Cloudflare Tunnel
- Wait 5-10 minutes for DNS propagation
- Test from multiple locations

**Phase 4: Monitoring (Week 3-4)**
- Keep rental server running as backup
- Monitor NAS performance
- After 2 weeks of stability, decommission rental server

---

## Benefits of This Setup

✅ **No router configuration needed**
✅ **No ISP coordination required**
✅ **Works in shared house**
✅ **Free SSL from Cloudflare**
✅ **DDoS protection included**
✅ **Zero-downtime updates possible**
✅ **Better than rental server (your own hardware)**

---

## Costs

- Cloudflare Tunnel: **FREE** (Zero Trust free tier)
- Cloudflare DNS/Proxy: **FREE**
- Your NAS: Already owned ✅
- Internet: Existing connection ✅

**Total additional cost: $0/month**

Compare to:
- Rental server: $X/month (you can cancel this!)

---

## Quick Start Commands

```bash
# 1. SSH to NAS
ssh ywatanabe@168.254.11.30

# 2. Navigate to project
cd /volume1/docker/scitex-cloud/containers/docker

# 3. Start everything
docker-compose -f docker-compose.cloudflare.yml up -d

# 4. Watch logs
docker-compose logs -f cloudflared

# 5. Check status
docker-compose ps
```

---

## Support Resources

- Cloudflare Tunnel Docs: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/
- Cloudflare Dashboard: https://dash.cloudflare.com
- Your NAS: http://168.254.11.30:5000

---

## Next Steps

1. Create Cloudflare account (if you haven't)
2. Add scitex.ai to Cloudflare
3. Create tunnel and get token
4. Deploy using this guide
5. Test thoroughly before migrating DNS

**Questions?** Let me know and I'll help you through each step!

