# Nginx Production - HTTPS Setup

Production nginx for https://scitex.ai and https://git.scitex.ai

---

## Quick Setup

From project root:
```bash
cd /home/ywatanabe/proj/scitex-cloud

# 1. Start production
make ENV=prod start

# 2. Setup HTTPS
make ENV=prod ssl-setup
```

Or from docker directory:
```bash
cd deployment/docker/docker_prod

# 1. Link environment
ln -sf ../../SECRET/.env.prod .env

# 2. Start services
make up

# 3. Setup HTTPS
cd nginx && ./setup_nginx.sh
```

---

## Manual Setup

### 1. Obtain Certificates

```bash
cd /home/ywatanabe/proj/scitex-cloud/deployment/docker/docker_prod
source .env

docker compose run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  --email ${SCITEX_EMAIL_ADMIN} \
  --agree-tos --no-eff-email \
  -d scitex.ai -d git.scitex.ai
```

### 2. Enable HTTPS

Edit `sites-available/scitex_cloud_prod.conf`:
- Comment out HTTP server blocks
- Uncomment HTTPS server blocks
- Uncomment HTTP→HTTPS redirect

```bash
docker compose exec nginx nginx -t
make restart
```

### 3. Verify

```bash
curl -I https://scitex.ai
curl -I https://git.scitex.ai
```

---

## Structure

```
nginx/
├── nginx.conf                          # System config (global settings)
├── sites-available/
│   └── scitex_cloud_prod.conf         # Site config (server blocks)
└── sites-enabled/
    └── scitex_cloud_prod.conf         # Symlink to sites-available
```

## Configuration

### Environment Variables (.env.prod)
```bash
SCITEX_CLOUD_DOMAIN=scitex.ai              # Main domain
SCITEX_CLOUD_GIT_DOMAIN=git.scitex.ai      # Git server domain
SCITEX_CLOUD_SERVER_IP=162.43.35.139       # Server IP (for DNS check)
SCITEX_CLOUD_EMAIL_ADMIN=admin@scitex.ai   # Email for SSL certificates
```

### Settings
- **Timeouts**: 600s (for LaTeX processing)
- **Rate limits**: 10 req/s general, 5 req/min auth
- **Auto-renewal**: Every 12 hours (certbot container)
- **SSL certs**: `/etc/nginx/ssl/live/${SCITEX_CLOUD_DOMAIN}/`

---

## Troubleshooting

**Certificate fails**
```bash
dig scitex.ai
curl -I http://scitex.ai
```

**Nginx won't start**
```bash
docker compose exec nginx nginx -t
docker compose logs nginx
```

**502 error**
```bash
docker compose ps web
make logs-web
```

---

**Domains**: https://scitex.ai, https://git.scitex.ai

<!-- EOF -->
