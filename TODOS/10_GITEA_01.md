<!-- ---
!-- Timestamp: 2025-10-20 10:08:42
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/10_GITEA_GIT_HOSTING.md
!-- --- -->

# Git Hosting Setup for SciTeX

## Goal
Enable forking functionality for SciTeX projects at git.scitex.ai

## Solution: Gitea Self-Hosted Git Service

Since forking is required, a simple bare-repo approach isn't sufficient. We need a self-hosted Git service with user accounts, permissions, and fork support.

### Why Gitea?
- Lightweight and fast (single binary)
- GitHub-style forking, PRs, issues, webhooks
- Clean integration with Django on the same host
- Production-ready with PostgreSQL
- Works alongside existing Nginx setup

## Implementation Plan

### 1. DNS Configuration
Add A record:
```
git.scitex.ai → <server IP>
```

### 2. Setup PostgreSQL Database
```bash
# Install PostgreSQL
sudo dnf install postgresql-server postgresql-contrib

# Initialize database
sudo postgresql-setup --initdb

# Start and enable service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create Gitea database and user
sudo -u postgres psql << EOF
CREATE DATABASE gitea;
CREATE USER gitea WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE gitea TO gitea;
\q
EOF

# Configure PostgreSQL to allow local connections
# Edit /var/lib/pgsql/data/pg_hba.conf
# Add line: host gitea gitea 127.0.0.1/32 md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### 3. Install Gitea
```bash
# Install dependencies
sudo dnf install git

# Create gitea user
sudo adduser --system --shell /bin/bash --home /var/lib/gitea gitea

# Create directories
sudo mkdir -p /var/lib/gitea/{custom,data,log}
sudo chown -R gitea:gitea /var/lib/gitea
sudo chmod -R 750 /var/lib/gitea

# Download Gitea
wget -O /usr/local/bin/gitea https://dl.gitea.io/gitea/latest/gitea-linux-amd64
chmod +x /usr/local/bin/gitea
```

### 4. Create Systemd Service
Create `/etc/systemd/system/gitea.service`:
```ini
[Unit]
Description=Gitea (Git with a cup of tea)
After=syslog.target
After=network.target
After=postgresql.service

[Service]
RestartSec=2s
Type=simple
User=gitea
Group=gitea
WorkingDirectory=/var/lib/gitea/
ExecStart=/usr/local/bin/gitea web --config /etc/gitea/app.ini
Restart=always
Environment=USER=gitea HOME=/var/lib/gitea GITEA_WORK_DIR=/var/lib/gitea

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable gitea
sudo systemctl start gitea
```

### 5. Configure Gitea
Visit `http://git.scitex.ai:3000` for initial setup.

Configuration in `/etc/gitea/app.ini`:
```ini
[database]
DB_TYPE  = postgres
HOST     = 127.0.0.1:5432
NAME     = gitea
USER     = gitea
PASSWD   = secure_password_here
SCHEMA   =
SSL_MODE = disable

[server]
DOMAIN           = git.scitex.ai
SSH_DOMAIN       = git.scitex.ai
HTTP_PORT        = 3000
ROOT_URL         = https://git.scitex.ai/
START_SSH_SERVER = true
SSH_PORT         = 22

[repository]
ROOT = /var/lib/gitea/data/gitea-repositories
```

**Important:** If using port 22 for Gitea SSH, you must move your server's SSH to a different port.

### 6. SSH Port Configuration

**Option A: Gitea on port 22, Server SSH on custom port (Recommended)**

This provides a cleaner Git experience (`git@git.scitex.ai:user/repo.git`).

```bash
# Move server SSH to port 2222
sudo vi /etc/ssh/sshd_config
# Change: Port 22 → Port 2222

# Restart SSH service
sudo systemctl restart sshd

# Update firewall
sudo firewall-cmd --permanent --add-port=2222/tcp
sudo firewall-cmd --permanent --remove-service=ssh
sudo firewall-cmd --reload

# Test before closing current session!
# In new terminal: ssh -p 2222 user@scitex.ai
```

**Option B: Server SSH on port 22, Gitea on custom port**

Keep standard SSH login, but Git URLs require port specification.

```bash
# In /etc/gitea/app.ini, change:
SSH_PORT = 2222

# Update firewall
sudo firewall-cmd --permanent --add-port=2222/tcp
sudo firewall-cmd --reload
```

Clone URLs become: `git clone ssh://git@git.scitex.ai:2222/user/repo.git`

### 7. Firewall Configuration
```bash
# For Option A (Gitea on 22, Server SSH on 2222)
sudo firewall-cmd --permanent --add-port=2222/tcp  # Server SSH
sudo firewall-cmd --permanent --add-service=ssh    # Gitea SSH

# For Option B (Server SSH on 22, Gitea on 2222)
sudo firewall-cmd --permanent --add-port=2222/tcp  # Gitea SSH
sudo firewall-cmd --permanent --add-service=ssh    # Server SSH

sudo firewall-cmd --reload
```

### 8. Nginx Reverse Proxy
- Point git.scitex.ai to Gitea's HTTP port (3000)
- Enable SSL with Let's Encrypt

### 9. Django Integration
- Use Gitea's REST API or OAuth for user account linking
- Display repositories on Django site
- Implement "Fork on Git" workflow

## Clone URLs Format
**Production (Option A - Gitea on port 22):**
- SSH: `git@git.scitex.ai:username/repo.git`
- HTTPS: `https://git.scitex.ai/username/repo.git`
- Server SSH: `ssh -p 2222 user@scitex.ai`

**Production (Option B - Server SSH on port 22):**
- SSH: `ssh://git@git.scitex.ai:2222/username/repo.git`
- HTTPS: `https://git.scitex.ai/username/repo.git`
- Server SSH: `ssh user@scitex.ai` (standard port 22)

**Local Development:**
- HTTPS: `http://localhost:3000/username/repo.git`

## Local Development Setup

You can develop and test Gitea locally without Nginx. Gitea includes a built-in web server.

### Quick Start (Local)

**Option 1: Direct Binary**
```bash
# Download Gitea
wget -O gitea https://dl.gitea.io/gitea/latest/gitea-linux-amd64
chmod +x gitea

# Run with SQLite for development (simpler)
./gitea web

# Access at http://localhost:3000
```

**Option 2: Docker (Recommended for Development)**
```bash
# Run Gitea with SQLite
docker run -d --name=gitea \
  -p 3000:3000 \
  -p 2222:22 \
  -v gitea-data:/data \
  gitea/gitea:latest

# Access at http://localhost:3000
```

### Local Development Workflow

```bash
# Terminal 1: Django dev server
python manage.py runserver
# Runs on http://localhost:8000

# Terminal 2: Gitea
./gitea web
# Runs on http://localhost:3000
```

### Local Configuration

For local development, use simpler settings in `app.ini`:

```ini
[database]
DB_TYPE  = sqlite3
PATH     = /data/gitea/gitea.db

[server]
DOMAIN           = localhost
HTTP_PORT        = 3000
ROOT_URL         = http://localhost:3000/
START_SSH_SERVER = false

[repository]
ROOT = /data/gitea/gitea-repositories
```

### Django OAuth Integration (Local)

Configure OAuth application in Gitea with local URLs:
- **Authorization callback URL:** `http://localhost:8000/auth/gitea/callback`
- **Application URL:** `http://localhost:8000`

Your Django app can call Gitea API at `http://localhost:3000/api/v1/...`

### Local Development Benefits
- No SSL certificates required
- Direct access to both services
- Easier debugging with direct log access
- Fast iteration without deployment
- Use SQLite instead of PostgreSQL for simplicity

### Testing Before Production
1. Develop OAuth integration locally
2. Test forking, PRs, user management
3. Verify API integration with Django
4. Once stable, deploy to production with PostgreSQL + Nginx

## Complexity Assessment

### Easy (✅)
- Gitea binary installation
- Basic app.ini configuration
- DNS A record setup
- Systemd service creation

### Moderate (⚠️)
- Nginx reverse proxy with SSL
- SSH on custom port 2222
- User/permission management
- OAuth integration with Django

### Challenging (🔴)
- PostgreSQL backup strategy (pg_dump automation)
- Repository backup strategy
- Security hardening (SSH keys, rate limiting)
- Ongoing maintenance and updates

## Time Estimate
- PostgreSQL setup: 30-45 minutes
- Initial Gitea setup: 1-2 hours
- SSL + Nginx configuration: 30-60 minutes
- Testing & debugging: 1-2 hours
- OAuth integration: 2-4 hours
- **Total: 0.5-1 day for production-ready setup**

## Next Steps
1. Confirm server specifications
2. Set secure PostgreSQL password
3. Generate Nginx configuration with SSL
4. Plan OAuth integration with Django user model
5. Define backup procedures (PostgreSQL + repositories)

<!-- EOF -->