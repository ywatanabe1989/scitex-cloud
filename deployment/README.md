<!-- ---
!-- Timestamp: 2025-10-19 00:29:29
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/deployment/README.md
!-- --- -->

# Quick Start - SciTeX Cloud Deployment

**Estimated Time**: 30-60 minutes

> **Note**: For detailed component documentation, see the README.md files in each subdirectory (dotenvs/, postgres/, uwsgi/, nginx/).

---

## 📍 Development Setup

### Prerequisites
- [ ] Ubuntu 20.04+ or Debian 11+ (or WSL2)
- [ ] Python 3.11, Git, PostgreSQL installed
- [ ] Project cloned

### Steps

```bash
# 1. Clone
cd ~/proj/
git clone https://github.com/scitex-ai/scitex-cloud.git
cd scitex-cloud

# 2. Setup virtual environment
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r ./deployment/requirements.txt

# 3. Setup database
bash scripts/deployment/setup_postgres.sh

# 4. Switch to dev environment
source scripts/deployment/switch_env.sh dev

# 5. Run migrations
python manage.py migrate
python manage.py createsuperuser

# 6. Start development server
python manage.py runserver
```

Visit: http://localhost:8000

**Verification:**
- [ ] Homepage loads
- [ ] Admin panel accessible at /admin
- [ ] Login works

---

## 🚀 Production Setup

### Prerequisites
- [ ] Ubuntu server with public IP
- [ ] Domain name pointing to server
- [ ] SSH access with sudo
- [ ] Firewall configured (ports 22, 80, 443)

### Steps

```bash
# 1. Install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv postgresql nginx git ufw

# 2. Configure firewall
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# 3. Clone project
sudo mkdir -p /var/www
cd /var/www
sudo git clone https://github.com/ywatanabe1989/scitex-cloud.git
sudo chown -R $USER:$USER scitex-cloud
cd scitex-cloud

# 4. Setup Python environment
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 5. Setup database
bash scripts/deployment/setup_postgres.sh

# 6. Switch to production environment
source scripts/deployment/switch_env.sh prod

# 7. Run migrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput

# 8. Setup uWSGI systemd service
sudo cp deployment/uwsgi/scitex_cloud_prod.service /etc/systemd/system/scitex_cloud.service
sudo systemctl daemon-reload
sudo systemctl enable scitex_cloud
sudo systemctl start scitex_cloud

# 9. Setup Nginx
sudo cp deployment/nginx/scitex_cloud_prod.conf /etc/nginx/sites-available/scitex_cloud
sudo ln -s /etc/nginx/sites-available/scitex_cloud /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 10. Setup SSL
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

Visit: https://your-domain.com

**Verification:**
- [ ] HTTPS works
- [ ] SSL certificate valid
- [ ] HTTP redirects to HTTPS
- [ ] All static files loading

---

## 🔍 Troubleshooting

### Development

**Database connection error:**
```bash
pg_isready
psql -U scitex_dev -d scitex_cloud_dev
```

**Migration errors:**
```bash
python manage.py showmigrations
python manage.py migrate --fake-initial
```

### Production

**502 Bad Gateway:**
```bash
sudo systemctl status scitex_cloud
sudo journalctl -u scitex_cloud -f
```

**Static files not loading:**
```bash
python manage.py collectstatic --noinput
sudo nginx -t
```

---

## 📖 Component Documentation

For detailed configuration and troubleshooting:

- **[dotenvs/README.md](./dotenvs/README.md)** - Environment variables reference
- **[postgres/README.md](./postgres/README.md)** - PostgreSQL setup and management
- **[uwsgi/README.md](./uwsgi/README.md)** - Application server configuration
- **[nginx/README.md](./nginx/README.md)** - Web server and SSL setup

---

## 📁 Directory Structure

```
deployment/
├── README.md                      # This file (quick start guide)
├── dotenvs/                       # Environment variable files
│   ├── README.md                 # Environment variables documentation
│   ├── dotenv.dev                # Development variables
│   ├── dotenv.prod               # Production variables
│   └── dotenv.example            # Template
├── nginx/                         # Web server configs
│   ├── README.md                 # Nginx setup guide
│   ├── scitex_cloud_dev.conf     # HTTP only
│   └── scitex_cloud_prod.conf    # HTTPS with SSL
├── postgres/                      # Database scripts
│   ├── README.md                 # PostgreSQL documentation
│   └── setup_production.sh       # Production DB setup
├── uwsgi/                         # Application server configs
│   ├── README.md                 # uWSGI documentation
│   ├── scitex_cloud_dev.ini      # 4 processes, 2 threads
│   ├── scitex_cloud_prod.ini     # 8 processes, 4 threads
│   └── scitex_cloud_prod.service # Systemd service
└── ssl/                           # SSL certificates (Let's Encrypt)
```

---

## 🔄 Next Steps

After successful setup:

1. **Configure monitoring** - Setup log rotation, monitoring
2. **Setup backups** - Automated database backups
3. **Security hardening** - fail2ban, security headers
4. **Performance tuning** - Caching, CDN

<!-- EOF -->