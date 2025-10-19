#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: 2025-10-20
# Author: ywatanabe
# File: deployment/gitea/deploy-production.sh
# ----------------------------------------
# Gitea Production Deployment Script for SciTeX Cloud
# This script sets up Gitea on production server for git.scitex.ai
# ----------------------------------------

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GITEA_VERSION="1.21.5"
GITEA_USER="gitea"
GITEA_HOME="/var/lib/gitea"
GITEA_BIN="/usr/local/bin/gitea"
GITEA_CONFIG_DIR="/etc/gitea"
GITEA_DB_NAME="gitea_prod"
GITEA_DB_USER="gitea_prod"
DOMAIN="git.scitex.ai"
HTTP_PORT="3000"
SSH_PORT="2222"

# Function to print colored messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if script is run as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Function to check if PostgreSQL is running
check_postgres() {
    print_status "Checking PostgreSQL status..."
    if ! systemctl is-active --quiet postgresql; then
        print_error "PostgreSQL is not running. Please start it first."
        exit 1
    fi
    print_success "PostgreSQL is running"
}

# Function to create gitea system user
create_gitea_user() {
    print_status "Creating gitea system user..."
    if id "$GITEA_USER" &>/dev/null; then
        print_warning "User $GITEA_USER already exists, skipping..."
    else
        useradd --system --shell /bin/bash --home "$GITEA_HOME" "$GITEA_USER"
        print_success "Created user $GITEA_USER"
    fi
}

# Function to create directories
create_directories() {
    print_status "Creating Gitea directories..."

    mkdir -p "$GITEA_HOME"/{custom,data,log}
    mkdir -p "$GITEA_CONFIG_DIR"
    mkdir -p "$GITEA_HOME/data/gitea-repositories"
    mkdir -p "$GITEA_HOME/data/lfs"

    chown -R "$GITEA_USER:$GITEA_USER" "$GITEA_HOME"
    chmod -R 750 "$GITEA_HOME"
    chown root:$GITEA_USER "$GITEA_CONFIG_DIR"
    chmod 770 "$GITEA_CONFIG_DIR"

    print_success "Directories created"
}

# Function to download and install Gitea binary
install_gitea_binary() {
    print_status "Downloading Gitea ${GITEA_VERSION}..."

    ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then
        ARCH="amd64"
    elif [ "$ARCH" = "aarch64" ]; then
        ARCH="arm64"
    fi

    DOWNLOAD_URL="https://dl.gitea.io/gitea/${GITEA_VERSION}/gitea-${GITEA_VERSION}-linux-${ARCH}"

    wget -O "$GITEA_BIN" "$DOWNLOAD_URL"
    chmod +x "$GITEA_BIN"

    print_success "Gitea binary installed at $GITEA_BIN"

    # Verify installation
    "$GITEA_BIN" --version
}

# Function to create PostgreSQL database and user
create_database() {
    print_status "Creating PostgreSQL database for Gitea..."

    # Generate random password
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)

    # Create database and user
    sudo -u postgres psql <<EOF
-- Create user if doesn't exist
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '${GITEA_DB_USER}') THEN
        CREATE USER ${GITEA_DB_USER} WITH PASSWORD '${DB_PASSWORD}';
    END IF;
END
\$\$;

-- Create database if doesn't exist
SELECT 'CREATE DATABASE ${GITEA_DB_NAME} OWNER ${GITEA_DB_USER}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${GITEA_DB_NAME}')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ${GITEA_DB_NAME} TO ${GITEA_DB_USER};
EOF

    # Save password to secure file
    echo "$DB_PASSWORD" > /root/.gitea_db_password
    chmod 600 /root/.gitea_db_password

    print_success "Database created: $GITEA_DB_NAME"
    print_success "Database password saved to /root/.gitea_db_password"
}

# Function to create Gitea configuration
create_config() {
    print_status "Creating Gitea configuration..."

    # Read database password
    DB_PASSWORD=$(cat /root/.gitea_db_password)

    # Generate secret keys
    SECRET_KEY=$(gitea generate secret SECRET_KEY)
    INTERNAL_TOKEN=$(gitea generate secret INTERNAL_TOKEN)
    JWT_SECRET=$(gitea generate secret JWT_SECRET)

    cat > "${GITEA_CONFIG_DIR}/app.ini" <<EOF
; Gitea Configuration for SciTeX Cloud
; Generated: $(date)

[server]
APP_NAME = SciTeX Git Hosting
DOMAIN = ${DOMAIN}
SSH_DOMAIN = ${DOMAIN}
HTTP_PORT = ${HTTP_PORT}
ROOT_URL = https://${DOMAIN}/
DISABLE_SSH = false
SSH_PORT = ${SSH_PORT}
SSH_LISTEN_PORT = ${SSH_PORT}
START_SSH_SERVER = true
LFS_START_SERVER = true
LFS_JWT_SECRET = ${JWT_SECRET}
OFFLINE_MODE = false

[database]
DB_TYPE = postgres
HOST = localhost:5432
NAME = ${GITEA_DB_NAME}
USER = ${GITEA_DB_USER}
PASSWD = ${DB_PASSWORD}
SSL_MODE = disable
CHARSET = utf8
PATH = ${GITEA_HOME}/data/gitea.db
LOG_SQL = false

[repository]
ROOT = ${GITEA_HOME}/data/gitea-repositories
SCRIPT_TYPE = bash
DEFAULT_BRANCH = main
DEFAULT_PRIVATE = last
ENABLE_PUSH_CREATE_USER = true
ENABLE_PUSH_CREATE_ORG = true

[security]
INSTALL_LOCK = true
SECRET_KEY = ${SECRET_KEY}
INTERNAL_TOKEN = ${INTERNAL_TOKEN}
PASSWORD_HASH_ALGO = pbkdf2

[service]
DISABLE_REGISTRATION = false
REQUIRE_SIGNIN_VIEW = false
REGISTER_EMAIL_CONFIRM = false
ENABLE_NOTIFY_MAIL = false
ALLOW_ONLY_EXTERNAL_REGISTRATION = false
ENABLE_CAPTCHA = false
DEFAULT_KEEP_EMAIL_PRIVATE = false
DEFAULT_ALLOW_CREATE_ORGANIZATION = true
DEFAULT_ENABLE_TIMETRACKING = true
NO_REPLY_ADDRESS = noreply.${DOMAIN}

[mailer]
ENABLED = false

[session]
PROVIDER = file
PROVIDER_CONFIG = ${GITEA_HOME}/data/sessions

[log]
MODE = console, file
LEVEL = Info
ROOT_PATH = ${GITEA_HOME}/log

[git]
MAX_GIT_DIFF_LINES = 1000
MAX_GIT_DIFF_LINE_CHARACTERS = 5000
MAX_GIT_DIFF_FILES = 100

[api]
ENABLE_SWAGGER = true

[oauth2]
JWT_SECRET = ${JWT_SECRET}

[lfs]
PATH = ${GITEA_HOME}/data/lfs

[actions]
ENABLED = true
EOF

    chown root:$GITEA_USER "${GITEA_CONFIG_DIR}/app.ini"
    chmod 640 "${GITEA_CONFIG_DIR}/app.ini"

    print_success "Gitea configuration created"
}

# Function to create systemd service
create_systemd_service() {
    print_status "Creating systemd service..."

    cat > /etc/systemd/system/gitea.service <<EOF
[Unit]
Description=Gitea (Git with a cup of tea)
After=syslog.target
After=network.target
After=postgresql.service

[Service]
Type=simple
User=${GITEA_USER}
Group=${GITEA_USER}
WorkingDirectory=${GITEA_HOME}
ExecStart=${GITEA_BIN} web --config ${GITEA_CONFIG_DIR}/app.ini
Restart=always
Environment=USER=${GITEA_USER}
Environment=HOME=${GITEA_HOME}
Environment=GITEA_WORK_DIR=${GITEA_HOME}

# Security settings
ProtectSystem=full
PrivateDevices=yes
PrivateTmp=yes
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    print_success "Systemd service created"
}

# Function to create Nginx configuration
create_nginx_config() {
    print_status "Creating Nginx configuration..."

    cat > /etc/nginx/sites-available/gitea <<EOF
# Gitea Nginx Configuration for SciTeX Cloud
# Domain: ${DOMAIN}

upstream gitea {
    server 127.0.0.1:${HTTP_PORT};
}

server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN};

    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ${DOMAIN};

    # SSL Configuration (will be updated by certbot)
    # ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;

    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Logging
    access_log /var/log/nginx/gitea_access.log;
    error_log /var/log/nginx/gitea_error.log;

    # Client body size (for git push)
    client_max_body_size 512M;

    # Proxy settings
    location / {
        proxy_pass http://gitea;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_buffering off;
    }
}
EOF

    # Enable site
    ln -sf /etc/nginx/sites-available/gitea /etc/nginx/sites-enabled/gitea

    # Test nginx configuration
    nginx -t

    print_success "Nginx configuration created"
}

# Function to configure firewall
configure_firewall() {
    print_status "Configuring firewall..."

    if command -v ufw &> /dev/null; then
        ufw allow ${HTTP_PORT}/tcp comment "Gitea HTTP"
        ufw allow ${SSH_PORT}/tcp comment "Gitea SSH"
        print_success "UFW rules added"
    elif command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-port=${HTTP_PORT}/tcp
        firewall-cmd --permanent --add-port=${SSH_PORT}/tcp
        firewall-cmd --reload
        print_success "Firewalld rules added"
    else
        print_warning "No firewall detected (ufw or firewalld), skipping..."
    fi
}

# Function to start Gitea service
start_gitea() {
    print_status "Starting Gitea service..."

    systemctl enable gitea
    systemctl start gitea

    sleep 3

    if systemctl is-active --quiet gitea; then
        print_success "Gitea is running!"
    else
        print_error "Gitea failed to start. Check logs: journalctl -u gitea -n 50"
        exit 1
    fi
}

# Function to display post-installation instructions
display_instructions() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}Gitea Installation Complete!${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📍 Next Steps:"
    echo ""
    echo "1. Set up DNS:"
    echo "   Add A record: ${DOMAIN} → $(hostname -I | awk '{print $1}')"
    echo ""
    echo "2. Install SSL certificate:"
    echo "   sudo certbot --nginx -d ${DOMAIN}"
    echo ""
    echo "3. Access Gitea:"
    echo "   http://localhost:${HTTP_PORT}  (temporary, until SSL)"
    echo "   https://${DOMAIN}  (after SSL setup)"
    echo ""
    echo "4. Create admin user:"
    echo "   First user to register will be admin"
    echo ""
    echo "5. Generate API token:"
    echo "   Settings → Applications → Generate New Token"
    echo ""
    echo "6. Update Django environment:"
    echo "   SCITEX_CLOUD_GITEA_URL=https://${DOMAIN}"
    echo "   SCITEX_CLOUD_GITEA_TOKEN=<your-api-token>"
    echo ""
    echo "📝 Important Files:"
    echo "   Config: ${GITEA_CONFIG_DIR}/app.ini"
    echo "   Data: ${GITEA_HOME}/data/"
    echo "   Logs: ${GITEA_HOME}/log/"
    echo "   DB Password: /root/.gitea_db_password"
    echo ""
    echo "🔧 Service Management:"
    echo "   systemctl status gitea"
    echo "   systemctl restart gitea"
    echo "   journalctl -u gitea -f"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Main installation function
main() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Gitea Production Deployment for SciTeX Cloud"
    echo "  Domain: ${DOMAIN}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    check_root
    check_postgres
    create_gitea_user
    create_directories
    install_gitea_binary
    create_database
    create_config
    create_systemd_service
    create_nginx_config
    configure_firewall
    start_gitea
    display_instructions
}

# Run main function
main

# EOF
