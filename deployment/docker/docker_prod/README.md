# Docker Production Environment

Production deployment with security hardening and performance optimization.

## Quick Start

```bash
# Initial setup
make -f Makefile.prod setup

# Start services
make -f Makefile.prod start

# Stop services
make -f Makefile.prod down
```

## Services

- **Nginx** - Port 80/443 (SSL)
- **Django** - Internal (via Nginx)
- **PostgreSQL** - Internal
- **Redis** - Internal

## Common Commands

```bash
# Deployment
make -f Makefile.prod start           # Start production
make -f Makefile.prod restart         # Restart services
make -f Makefile.prod rebuild         # Full rebuild (⚠️ causes downtime)

# Django
make -f Makefile.prod migrate         # Run migrations
make -f Makefile.prod collectstatic   # Collect static files
make -f Makefile.prod shell           # Django shell (⚠️ production!)

# Database
make -f Makefile.prod db-backup       # Backup database
make -f Makefile.prod db-shell        # PostgreSQL shell (⚠️ production!)

# Monitoring
make -f Makefile.prod verify-health   # Health check
make -f Makefile.prod logs            # View logs
make -f Makefile.prod ps              # Service status

# Help
make -f Makefile.prod help            # Show all commands
```

## Environment Variables

Uses `SECRET/.env.prod`.

Critical variables:
- `DJANGO_SECRET_KEY` - Unique secret key
- `ALLOWED_HOSTS` - Domain names
- `POSTGRES_PASSWORD` - Strong password
- SSL/TLS certificates path

## Security Checklist

- [ ] DEBUG=False
- [ ] Strong SECRET_KEY
- [ ] Strong database password
- [ ] SSL certificates (Let's Encrypt)
- [ ] Configure firewall (allow only 22, 80, 443)
- [ ] Regular database backups
- [ ] Log monitoring

## Backups

Backups saved to `../../backups/` with timestamp:
```bash
make -f Makefile.prod db-backup
# Creates: backups/scitex_prod_YYYYMMDD_HHMMSS.sql.gz
```

## SSL Setup

### Let's Encrypt (Recommended)
```bash
sudo certbot certonly --standalone -d scitex.ai -d www.scitex.ai
sudo cp /etc/letsencrypt/live/scitex.ai/*.pem ../../ssl/
```

### Auto-renewal
```bash
sudo crontab -e
# Add: 0 3 * * 0 certbot renew --quiet && docker compose restart nginx
```
