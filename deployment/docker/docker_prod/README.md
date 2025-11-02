# Docker Production Environment

Production deployment for https://scitex.ai and https://git.scitex.ai

---

## Quick Start

### 1. Setup Environment
```bash
cd /home/ywatanabe/proj/scitex-cloud/deployment/docker/docker_prod

# Link production environment file
ln -sf ../../SECRET/.env.prod .env
```

### 2. Start Services
```bash
make up
```

### 3. Setup HTTPS
```bash
cd nginx
./setup_nginx.sh
```

See `nginx/README.md` for complete SSL setup guide.

---

## Services

| Service | Port | Purpose |
|---------|------|---------|
| **nginx** | 80, 443 | Reverse proxy with HTTPS |
| **web** | 8000 (internal) | Django application |
| **db** | 5432 (internal) | PostgreSQL database |
| **redis** | 6379 (internal) | Cache |
| **gitea** | 3000, 222 | Git server |
| **certbot** | - | SSL auto-renewal |

---

## Common Commands

### Deployment
```bash
make up              # Start services
make restart         # Restart services
make down            # Stop services
make rebuild         # Full rebuild (⚠️ causes downtime)
```

### Django
```bash
make migrate         # Run migrations
make collectstatic   # Collect static files
make shell           # Django shell (⚠️ production!)
```

### Database
```bash
make db-backup       # Backup database
make db-shell        # PostgreSQL shell (⚠️ production!)
```

### Monitoring
```bash
make status          # Service status
make logs            # View all logs
make logs-web        # View web logs
make logs-nginx      # View nginx logs
make verify-health   # Health check
```

### Help
```bash
make help            # Show all commands
```

---

## Environment Variables

Configuration file: `../../SECRET/.env.prod`

Key variables:
```bash
# Server & Domains (customize for your site)
SCITEX_CLOUD_SERVER_IP=162.43.35.139           # Server public IP
SCITEX_CLOUD_DOMAIN=scitex.ai                  # Main domain
SCITEX_CLOUD_GIT_DOMAIN=git.scitex.ai          # Git subdomain

# Django
DEBUG=False
SCITEX_CLOUD_DJANGO_SECRET_KEY=<generated>
SCITEX_CLOUD_ALLOWED_HOSTS=${SCITEX_CLOUD_DOMAIN},www.${SCITEX_CLOUD_DOMAIN},web

# Database
SCITEX_CLOUD_POSTGRES_DB=scitex_cloud_prod
SCITEX_CLOUD_POSTGRES_USER=scitex_prod
SCITEX_CLOUD_POSTGRES_PASSWORD=<strong_password>

# SSL/HTTPS
SCITEX_CLOUD_ENABLE_SSL_REDIRECT=true  # After SSL setup
SCITEX_CLOUD_FORCE_HTTPS_COOKIES=true  # After SSL setup

# Email (for SSL certificates)
SCITEX_CLOUD_EMAIL_ADMIN=admin@${SCITEX_CLOUD_DOMAIN}  # SSL renewal notifications
```

---

## SSL/HTTPS Setup

### Automated Setup
```bash
cd nginx
./setup_nginx.sh
```

### Manual Setup
See `nginx/README.md` for detailed instructions.

### Auto-Renewal
Certbot container automatically renews certificates every 12 hours.

---

## Security Checklist

Production deployment checklist:

- [ ] DEBUG=False in .env
- [ ] Strong SCITEX_CLOUD_DJANGO_SECRET_KEY generated
- [ ] Strong database password
- [ ] .env symlinked from SECRET/.env.prod
- [ ] SSL certificates obtained (./nginx/setup_nginx.sh)
- [ ] HTTPS enabled in nginx config
- [ ] Firewall configured (ports 22, 80, 443 only)
- [ ] Database backups configured
- [ ] Log monitoring enabled

---

## Backups

### Database Backup
```bash
make db-backup
```

Backups saved to: `../../backups/scitex_prod_YYYYMMDD_HHMMSS.sql.gz`

### Restore Database
```bash
gunzip < backups/scitex_prod_YYYYMMDD_HHMMSS.sql.gz | \
  docker compose exec -T db psql -U scitex_prod scitex_cloud_prod
```

---

## Troubleshooting

### Services won't start
```bash
# Check logs
make logs

# Check status
docker compose ps
```

### Database connection issues
```bash
# Check database
make db-shell

# Check environment
cat .env | grep POSTGRES
```

### SSL/HTTPS issues
See `nginx/README.md` troubleshooting section.

---

**Domains**: https://scitex.ai, https://git.scitex.ai

<!-- EOF -->
