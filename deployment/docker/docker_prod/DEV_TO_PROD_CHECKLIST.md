<!-- ---
!-- Timestamp: 2025-11-22 12:28:55
!-- Author: ywatanabe
!-- File: /ssh:scitex:/home/ywatanabe/proj/scitex-cloud/deployment/docker/docker_prod/DEV_TO_PROD_CHECKLIST.md
!-- --- -->

# Development to Production Deployment Checklist

## Pre-Deployment Verification

### 1. Code & Dependencies
- [ ] **scitex-code package updated**
  - [ ] Specify correct version in ./deployment/docker/docker_prod/Dockerfile
- [ ] TypeScript compiled successfully (`cd tsconfig && npm run build:all`)

### 2. Environment Configuration
- [ ] **SECRETS/.env.dev** has latest working configuration
- [ ] **SECRETS/.env.prod** synchronized with dev (check below)
  - [ ] Email settings (use `no-reply@scitex.ai`)
  - [ ] SciTeX Scholar configuration (all API keys, credentials)
  - [ ] SciTeX Writer settings (template branch/tag)
  - [ ] Gitea URLs (both host and container URLs)
  - [ ] Test user password matches dev (`Password1234!`)
  - [ ] `DEBUG=False` in production
  - [ ] SSL/HTTPS settings enabled
- [ ] Symlinks created: `deployment/docker/docker_prod/.env -> ../../../SECRETS/.env.prod`

### 3. Version & Documentation
- [ ] **Version updated to v0.X.0** in:
  - [ ] `deployment/docker/docker_prod/Dockerfile` (LABEL version)
  - [ ] `package.json` or version file
  - [ ] Any other version references
- [ ] **Release notes updated**:
  - [ ] `apps/public_app/templates/public_app/release_note.html`
  - [ ] Document new features (WebSocket, collaborative editing, PTY terminal)
  - [ ] Document breaking changes (database reset required)

### 4. Docker Configuration Verified
- [ ] **Daphne (ASGI) server** configured (not Gunicorn)
  - [ ] `deployment/docker/docker_prod/Dockerfile` CMD uses Daphne
  - [ ] `deployment/docker/docker_prod/docker-compose.yml` command uses Daphne
- [ ] **TypeScript build** in production entrypoint
  - [ ] `deployment/docker/docker_prod/entrypoint.sh` has `build_typescript()` function
- [ ] **Nginx WebSocket support** configured
  - [ ] `deployment/docker/docker_prod/nginx/sites-available/scitex_cloud_prod.conf` has WebSocket map and headers

### 5. Database & Data
- [ ] **Database backup** created (if preserving data)
  - [ ] `cd deployment/docker/docker_prod && make db-backup`
- [ ] **Database reset** planned (if needed for schema changes)
  - [ ] Data migration plan documented
  - [ ] User notification sent (if applicable)

## Deployment Process

### 6. Build & Start
```bash
cd deployment/docker/docker_prod

# Option A: Full rebuild (recommended for major changes)
make rebuild

# Option B: Quick restart (for config changes only)
make restart
```

### 7. Post-Deployment Verification
- [ ] **Container health checks** passing
  - [ ] `make verify-health`
  - [ ] `make ps` - all containers "Up" and "healthy"
- [ ] **Service accessibility**
  - [ ] Main site: https://scitex.ai (200 OK)
  - [ ] Gitea: https://git.scitex.ai (200 OK)
  - [ ] Admin panel: https://scitex.ai/admin/
- [ ] **WebSocket features working**
  - [ ] PTY terminal connects
  - [ ] Collaborative editing works
  - [ ] No WebSocket connection errors in browser console
- [ ] **SSL/HTTPS working**
  - [ ] `make ssl-verify`
  - [ ] HTTP redirects to HTTPS
  - [ ] Certificate valid and not expired
- [ ] **Static files served correctly**
  - [ ] JavaScript bundles loaded (check browser network tab)
  - [ ] CSS styles applied
  - [ ] Images displayed

### 8. Functionality Testing
- [ ] User registration/login working
- [ ] Project creation working
- [ ] Code workspace features:
  - [ ] Terminal launches
  - [ ] File editing works
- [ ] Writer features:
  - [ ] Document creation
  - [ ] LaTeX compilation
  - [ ] Collaborative editing (if applicable)
- [ ] Scholar features:
  - [ ] Paper search working
  - [ ] PDF download working

### 9. Monitoring & Logs
- [ ] Check application logs: `make logs-web`
- [ ] Check database logs: `make logs-db`
- [ ] Check Nginx logs: `make logs-nginx`
- [ ] No critical errors in logs
- [ ] Set up log rotation (if not already configured)

## Post-Deployment

### 10. User Communication
- [ ] Announce new version to users
- [ ] Document new features on website
- [ ] Update user documentation (if applicable)
- [ ] Notify about any breaking changes or required actions

### 11. Backup & Rollback Plan
- [ ] Database backup verified and stored securely
- [ ] Previous Docker image tagged for rollback
- [ ] Rollback procedure documented

## Quick Reference Commands

```bash
# Navigate to production directory
cd deployment/docker/docker_prod

# Environment check
make list-envs

# Health verification
make verify-health
make ssl-verify

# Logs
make logs           # All services
make logs-web       # Application
make logs-db        # Database
make logs-nginx     # Web server

# Database operations
make db-backup      # Backup before changes
make db-shell       # PostgreSQL shell access
make migrate        # Run migrations

# Rebuild & restart
make rebuild        # Full rebuild (stops, builds, starts)
make restart        # Quick restart

# SSL management
make ssl-check      # Check certificate status
make ssl-renew      # Renew certificates
```

## Troubleshooting

### Common Issues

**WebSocket not connecting:**
- Check Nginx WebSocket configuration
- Verify Daphne is running (not Gunicorn)
- Check browser console for errors

**Static files not loading:**
- Run `make collectstatic`
- Verify TypeScript compiled: `make build-ts`
- Check Nginx volume mounts

**Database connection errors:**
- Verify `.env.prod` database credentials
- Check database container: `make logs-db`
- Ensure migrations ran: `make migrate`

**SSL certificate issues:**
- Check certificate expiry: `make ssl-check`
- Renew if needed: `make ssl-renew`
- Verify domain DNS points to server IP

<!-- EOF -->