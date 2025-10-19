# Gitea Deployment for SciTeX Cloud

**Complete setup guide for Git hosting at git.scitex.ai**

---

## 📁 Directory Structure

```
deployment/gitea/
├── 00_README.md                      # ← You are here
├── 01_DEVELOPMENT.md                 # Local development setup
├── 02_PRODUCTION.md                  # Production deployment
├── docker-compose.gitea-dev.yml      # Docker config (development)
├── scripts/
│   ├── start-dev.sh                  # Start development Gitea
│   ├── stop-dev.sh                   # Stop development Gitea
│   ├── deploy-production.sh          # Production deployment script
│   └── EXECUTE_DEPLOYMENT.sh         # Wrapper for deployment
└── archive/
    └── (old documentation files)
```

---

## 🚀 Quick Start

### Development (Local)

```bash
# Start Gitea
./deployment/gitea/scripts/start-dev.sh

# Access: http://localhost:3000
```

**See:** `01_DEVELOPMENT.md`

### Production (git.scitex.ai)

```bash
# Deploy to production
sudo ./deployment/gitea/scripts/deploy-production.sh

# Install SSL
sudo certbot --nginx -d git.scitex.ai

# Access: https://git.scitex.ai
```

**See:** `02_PRODUCTION.md`

---

## 📚 Documentation Guide

| File | Purpose | When to Read |
|------|---------|--------------|
| **00_README.md** | Overview (this file) | Start here |
| **01_DEVELOPMENT.md** | Local development setup | Setting up dev environment |
| **02_PRODUCTION.md** | Production deployment | Deploying to git.scitex.ai |

---

## ✅ Current Status

**Development:** ✅ Complete and working
- Gitea running locally via Docker
- Django API client implemented
- Project creation working
- GitHub import supported

**Production:** 🚀 Ready to deploy
- Deployment script created
- SSL configuration prepared
- Django settings updated
- Awaiting manual deployment

---

## Development Commands

```bash
# Start development Gitea
./deployment/gitea/scripts/start-dev.sh

# Stop development Gitea
./deployment/gitea/scripts/stop-dev.sh

# View logs
docker logs scitex-gitea-dev -f

# Check status
docker ps | grep gitea
```

---

## Production Commands

```bash
# Check Gitea status
sudo systemctl status gitea

# View logs
sudo journalctl -u gitea -f

# Restart service
sudo systemctl restart gitea
```

---

## Access Points

### Development
- **Web UI:** http://localhost:3000
- **SSH:** localhost:2222
- **API:** http://localhost:3000/api/v1

### Production
- **Web UI:** https://git.scitex.ai
- **SSH:** git.scitex.ai:2222
- **API:** https://git.scitex.ai/api/v1

---

## Integration with Django

### Development
```python
# config/settings/settings_dev.py
GITEA_URL = 'http://localhost:3000'
GITEA_API_URL = 'http://localhost:3000/api/v1'
GITEA_TOKEN = os.environ.get('SCITEX_CLOUD_GITEA_TOKEN', '')
```

### Production
```python
# config/settings/settings_prod.py
GITEA_URL = 'https://git.scitex.ai'
GITEA_API_URL = 'https://git.scitex.ai/api/v1'
GITEA_TOKEN = os.environ.get('SCITEX_CLOUD_GITEA_TOKEN', '')
```

---

## Quick Reference

| Component | Development | Production |
|-----------|-------------|------------|
| **Domain** | localhost:3000 | git.scitex.ai |
| **Protocol** | HTTP | HTTPS |
| **SSH Port** | 2222 | 2222 |
| **Database** | SQLite3 | PostgreSQL |
| **Container** | Docker | Binary + Systemd |
| **Data** | Docker volume | /var/lib/gitea |

---

## Related Documentation

### Project Documentation
- **Infrastructure Assessment:** `docs/FUNDAMENTAL_INFRASTRUCTURE_ASSESSMENT.md`
- **Architecture:** `docs/INSTITUTIONAL_DEPLOYMENT_ARCHITECTURE.md`
- **Integration Roadmap:** `docs/GITEA_INTEGRATION_ROADMAP.md`

### TODO Lists
- **User Data Access:** `TODOS/01_USER_DATA_ACCESS_INFRASTRUCTURE.md`

### Archive
- Old documentation: `deployment/gitea/archive/`

---

## Support

### Troubleshooting

**Development issues:**
- See `01_DEVELOPMENT.md` → Troubleshooting section

**Production issues:**
- See `02_PRODUCTION.md` → Troubleshooting section

### Logs

**Development:**
```bash
docker logs scitex-gitea-dev -f
```

**Production:**
```bash
sudo journalctl -u gitea -f
```

---

## Next Steps

### If setting up development:
1. Read `01_DEVELOPMENT.md`
2. Run `./deployment/gitea/scripts/start-dev.sh`
3. Complete initial setup
4. Generate API token
5. Test Django integration

### If deploying to production:
1. Read `02_PRODUCTION.md`
2. Verify prerequisites
3. Run `sudo ./deployment/gitea/scripts/deploy-production.sh`
4. Install SSL certificate
5. Create admin user
6. Generate API token
7. Update Django environment
8. Test integration

---

**Clean, organized, and ready to use!** 🎉

<!-- EOF -->
