<!-- ---
!-- Timestamp: 2025-10-20 17:57:44
!-- Author: ywatanabe
!-- File: /ssh:scitex:/home/ywatanabe/proj/scitex-cloud/deployment/README.md
!-- --- -->

# SciTeX Cloud Deployment

Production and development deployment configurations

---

## Quick Start

### Development
```bash
# 1. Setup PostgreSQL
sudo ./deployment/postgres/setup_postgres.sh -e dev

# 2. Setup environment
source ./deployment/dotenvs/setup_env.sh -e dev

# 3. Run Django
python manage.py runserver
```

### Development using uwsgi, nginx, and gitea
```bash
# 1. Setup all services
sudo ./deployment/postgres/setup_postgres.sh -e dev
sudo ./deployment/uwsgi/setup_uwsgi.sh -e dev
sudo ./deployment/nginx/setup_nginx.sh -e dev
sudo ./deployment/gitea/setup_gitea.sh -e dev

# 2. Get SSL certificates
sudo certbot --nginx -d scitex.ai
sudo certbot --nginx -d git.scitex.ai

# 3. Start services
sudo systemctl start uwsgi_dev gitea_dev nginx
```

### Production
```bash
# 1. Setup all services
sudo ./deployment/postgres/setup_postgres.sh -e prod
sudo ./deployment/uwsgi/setup_uwsgi.sh -e prod
sudo ./deployment/nginx/setup_nginx.sh -e prod
sudo ./deployment/gitea/setup_gitea.sh -e prod

# 2. Get SSL certificates
sudo certbot --nginx -d scitex.ai
sudo certbot --nginx -d git.scitex.ai

# 3. Start services
sudo systemctl start uwsgi_prod gitea_prod nginx
```

---

## Architecture

```
Browser
   ↓
Nginx (80/443) ← SSL (Let's Encrypt)
   ├→ Static/Media (direct)
   ├→ uWSGI (socket) → Django → PostgreSQL
   └→ Gitea (proxy) → Gitea Service → PostgreSQL
```

---

## Components

| Component | Purpose | Config |
|-----------|---------|--------|
| **PostgreSQL** | Database | `./postgres/` |
| **uWSGI** | App server | `./uwsgi/` |
| **Nginx** | Reverse proxy | `./nginx/` |
| **Gitea** | Git hosting | `./gitea/` |
| **Environment** | Variables | `./dotenvs/` |

---

## DNS Requirements

| Domain | Points To | Purpose |
|--------|-----------|---------|
| `scitex.ai` | `162.43.35.139` | Main site |
| `git.scitex.ai` | `162.43.35.139` | Git hosting |

---

## Service Names

**Development:**
```bash
uwsgi_dev
gitea_dev
nginx (system)
postgresql (system)
```

**Production:**
```bash
uwsgi_prod
gitea_prod
nginx (system)
postgresql (system)
```

---

## Service Management

```bash
# Check all services
sudo systemctl status uwsgi_prod gitea_prod nginx postgresql

# Restart all
sudo systemctl restart uwsgi_prod gitea_prod nginx

# View logs
sudo journalctl -u uwsgi_prod -f
sudo journalctl -u gitea_prod -f
tail -f logs/nginx_*.log
```

---

## Maintenance Scripts

```bash
# Check DNS and SSL
./nginx/maintenance/nginx_check_dns.sh
./gitea/maintenance/gitea_check_dns.sh

# Backup database
./scripts/deployment/backup_database.sh

# Server management
./server.sh {start|stop|restart|status} -m {dev|prod}
```

---

## File Structure

```
deployment/
├── README.md          # This file
├── dotenvs/           # Environment variables
├── postgres/          # Database setup
├── uwsgi/             # Application server
├── nginx/             # Reverse proxy
├── gitea/             # Git hosting
└── server/            # Server management scripts
```

---

## Ports

| Service | Port | Access |
|---------|------|--------|
| Django (dev) | 8000 | Direct |
| uWSGI | socket | Via nginx |
| Nginx HTTP | 80 | Public |
| Nginx HTTPS | 443 | Public |
| Gitea HTTP | 3000 | Via nginx |
| Gitea SSH | 2222 | Public |
| PostgreSQL | 5432 | Local only |

---

## URLs

| Environment | Main Site | Git Hosting |
|-------------|-----------|-------------|
| **Development** | http://localhost:8000 | http://localhost:3001 |
| **Production** | https://scitex.ai | https://git.scitex.ai |

---

**Status:** Production Ready  
**Version:** 2025-10-20  
**Naming:** Consistent underscore convention (service_env)

<!-- EOF -->