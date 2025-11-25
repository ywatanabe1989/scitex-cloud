# Docker NAS Environment

NAS/Home server deployment with Cloudflare Tunnel for secure public access.

## Quick Start

```bash
# Start services
make -f Makefile.nas start

# Stop services
make -f Makefile.nas down
```

## Services

- **Django** - Internal:8000
- **Nginx** - Internal:80
- **Cloudflare Tunnel** - Public HTTPS access
- **Gitea** - localhost:3000
- **PostgreSQL** - Internal
- **Redis** - Internal

## Access

- **Public:** https://scitex.ai (via Cloudflare Tunnel)
- **Local:** http://nas-ip:8000 (LAN only)
- **Gitea:** http://nas-ip:3000 (LAN only)

## Common Commands

```bash
# Deployment
make -f Makefile.nas start            # Start services
make -f Makefile.nas restart          # Restart services
make -f Makefile.nas rebuild          # Full rebuild

# Django
make -f Makefile.nas migrate          # Run migrations
make -f Makefile.nas collectstatic    # Collect static files
make -f Makefile.nas shell            # Django shell

# Database
make -f Makefile.nas db-backup        # Backup database
make -f Makefile.nas db-shell         # PostgreSQL shell

# Monitoring
make -f Makefile.nas status           # Service status
make -f Makefile.nas logs             # View logs
make -f Makefile.nas logs-web         # Web logs only

# Help
make -f Makefile.nas help             # Show all commands
```

## Cloudflare Tunnel Setup

### Quick Start (Random URL)
The tunnel is already configured with a token! Just start the services:
```bash
make start
```

After services start, check the cloudflared logs to get your random URL:
```bash
make logs cloudflared
# Look for: "Your quick tunnel is available at: https://random-name.trycloudflare.com"
```

Then update your `.env` file with this URL:
```bash
# In SECRET/.env.nas
ALLOWED_HOSTS=random-name.trycloudflare.com,web,nginx,localhost
CSRF_TRUSTED_ORIGINS=https://random-name.trycloudflare.com
```

Restart services:
```bash
make restart
```

### Custom Domain Setup (Optional)
To use your own domain (scitex.ai):

1. Go to: https://dash.cloudflare.com
2. **Zero Trust** > **Networks** > **Tunnels**
3. Find your tunnel and configure routes:
   - `scitex.ai` → `http://nginx:80`
   - `www.scitex.ai` → `http://nginx:80`

4. Update `.env` file:
```bash
# In SECRET/.env.nas
ALLOWED_HOSTS=scitex.ai,www.scitex.ai,web,nginx,localhost
CSRF_TRUSTED_ORIGINS=https://scitex.ai,https://www.scitex.ai
```

5. Restart services:
```bash
make restart
```

## Environment Variables

Uses `SECRET/.env.nas`.

## NAS-Specific Features

- No port forwarding needed (Cloudflare Tunnel handles it)
- Lower resource usage than production
- Persistent data on NAS storage
- Suitable for home/lab environments
- Free SSL via Cloudflare

## Backups

Backups saved to `../../backups/`:
```bash
make -f Makefile.nas db-backup
# Creates: backups/scitex_nas_YYYYMMDD_HHMMSS.sql.gz
```

## Troubleshooting

**Cloudflare Tunnel unhealthy:**
```bash
make -f Makefile.nas logs cloudflared
# Check token in .env
```

**Site shows 502:**
```bash
make -f Makefile.nas logs-web
make -f Makefile.nas restart
```
