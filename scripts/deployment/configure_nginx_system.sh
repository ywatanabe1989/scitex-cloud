#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: 2025-10-18
# File: /home/ywatanabe/proj/scitex-cloud/scripts/configure_nginx_system.sh
# Description: Safely enhance system nginx.conf for Django/uWSGI production

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}SciTeX Cloud - Nginx System Configuration${NC}"
echo "==========================================="
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run with sudo${NC}"
    exit 1
fi

# Backup original nginx.conf if not already backed up
NGINX_CONF="/etc/nginx/nginx.conf"
BACKUP_DIR="/etc/nginx/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

if [ ! -f "$BACKUP_DIR/nginx.conf.original" ]; then
    echo -e "${YELLOW}Creating original backup...${NC}"
    cp "$NGINX_CONF" "$BACKUP_DIR/nginx.conf.original"
    echo -e "${GREEN}✓ Original saved: $BACKUP_DIR/nginx.conf.original${NC}"
fi

# Always create timestamped backup
cp "$NGINX_CONF" "$BACKUP_DIR/nginx.conf.backup_$TIMESTAMP"
echo -e "${GREEN}✓ Backup created: $BACKUP_DIR/nginx.conf.backup_$TIMESTAMP${NC}"
echo ""

# Check if our enhancements are already applied
if grep -q "# SciTeX Cloud Enhancements" "$NGINX_CONF"; then
    echo -e "${YELLOW}SciTeX enhancements already applied to nginx.conf${NC}"
    echo "Skipping modification."
    exit 0
fi

# Add enhancements to http block
echo -e "${YELLOW}Adding Django/uWSGI production enhancements...${NC}"

# Create temporary file with enhancements
cat > /tmp/nginx_enhancements.conf << 'EOF'

    ##
    # SciTeX Cloud Enhancements
    ##

    # Client body size (for file uploads)
    client_max_body_size 100M;
    client_body_buffer_size 128k;

    # Timeouts
    proxy_connect_timeout 600s;
    proxy_send_timeout 600s;
    proxy_read_timeout 600s;
    send_timeout 600s;

    # uWSGI specific
    uwsgi_read_timeout 300s;
    uwsgi_send_timeout 300s;

    # Buffer sizes
    proxy_buffer_size 128k;
    proxy_buffers 4 256k;
    proxy_busy_buffers_size 256k;

    # Rate limiting (adjust as needed)
    limit_req_zone $binary_remote_addr zone=scitex_limit:10m rate=10r/s;
    limit_req_status 429;

    # Security headers (base settings, override in site configs)
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Hide nginx version
    server_tokens off;

EOF

# Insert before the include statements
# Find the line with "include /etc/nginx/conf.d/*.conf;" and insert before it
sed -i '/include \/etc\/nginx\/conf.d\/\*.conf;/i\    ##\n    # SciTeX Cloud Enhancements\n    ##\n\n    # Client body size (for file uploads)\n    client_max_body_size 100M;\n    client_body_buffer_size 128k;\n\n    # Timeouts\n    proxy_connect_timeout 600s;\n    proxy_send_timeout 600s;\n    proxy_read_timeout 600s;\n    send_timeout 600s;\n\n    # uWSGI specific\n    uwsgi_read_timeout 300s;\n    uwsgi_send_timeout 300s;\n\n    # Buffer sizes\n    proxy_buffer_size 128k;\n    proxy_buffers 4 256k;\n    proxy_busy_buffers_size 256k;\n\n    # Rate limiting (adjust as needed)\n    limit_req_zone $binary_remote_addr zone=scitex_limit:10m rate=10r/s;\n    limit_req_status 429;\n\n    # Security headers (base settings, override in site configs)\n    add_header X-Content-Type-Options "nosniff" always;\n    add_header X-Frame-Options "SAMEORIGIN" always;\n    add_header X-XSS-Protection "1; mode=block" always;\n\n    # Hide nginx version\n    server_tokens off;\n' "$NGINX_CONF"

echo -e "${GREEN}✓ Enhancements added${NC}"
echo ""

# Test configuration
echo -e "${YELLOW}Testing nginx configuration...${NC}"
if nginx -t; then
    echo -e "${GREEN}✓ Configuration is valid${NC}"
    echo ""

    # Reload nginx
    echo -e "${YELLOW}Reloading nginx...${NC}"
    systemctl reload nginx
    echo -e "${GREEN}✓ Nginx reloaded successfully${NC}"
    echo ""

    echo -e "${GREEN}System nginx.conf enhanced successfully!${NC}"
    echo ""
    echo "Changes made:"
    echo "  • Client max body size: 100M"
    echo "  • Extended timeouts for long requests"
    echo "  • uWSGI-specific timeouts"
    echo "  • Increased buffer sizes"
    echo "  • Rate limiting configured"
    echo "  • Security headers added"
    echo "  • Server tokens hidden"
    echo ""
    echo "Backup locations:"
    echo "  • Original: $BACKUP_DIR/nginx.conf.original"
    echo "  • This run: $BACKUP_DIR/nginx.conf.backup_$TIMESTAMP"
else
    echo -e "${RED}✗ Configuration test failed!${NC}"
    echo -e "${YELLOW}Rolling back to backup...${NC}"
    cp "$BACKUP_DIR/nginx.conf.backup_$TIMESTAMP" "$NGINX_CONF"
    nginx -t
    echo -e "${RED}Configuration not applied${NC}"
    exit 1
fi

# EOF
