#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-02 06:40:00 (ywatanabe)"
# File: ./deployment/docker/docker_prod/nginx/setup_nginx.sh

set -e

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
DOCKER_DIR="$(cd $THIS_DIR/.. && pwd)"
PROJ_ROOT="$(cd $DOCKER_DIR/../../.. && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

GRAY='\033[0;90m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

echo_info() { echo -e "${GRAY}$1${NC}"; }
echo_success() { echo -e "${GREEN}$1${NC}"; }
echo_warning() { echo -e "${YELLOW}$1${NC}"; }
echo_error() { echo -e "${RED}$1${NC}"; }

# ============================================
# Usage
# ============================================
usage() {
    echo "Usage: $0 [--email EMAIL]"
    echo ""
    echo "Options:"
    echo "  --email EMAIL    Email for SSL certificate (default: from .env)"
    echo "  -h, --help       Show this help"
    echo ""
    echo "Example:"
    echo "  $0"
    echo "  $0 --email admin@scitex.ai"
    exit 1
}

# ============================================
# Setup Environment
# ============================================
setup_env() {
    echo_info "Setting up environment..."

    cd "$DOCKER_DIR"

    # Check if .env exists, if not create symlink
    if [ ! -f .env ]; then
        if [ -f "$PROJ_ROOT/SECRET/.env.prod" ]; then
            echo_info "Linking .env.prod..."
            ln -sf "$PROJ_ROOT/SECRET/.env.prod" .env
            echo_success ".env linked"
        else
            echo_error ".env.prod not found at $PROJ_ROOT/SECRET/.env.prod"
            exit 1
        fi
    else
        echo_success ".env already exists"
    fi

    # Load environment
    source .env

    # Set email from env if not provided
    if [ -z "$CERT_EMAIL" ]; then
        CERT_EMAIL="${SCITEX_CLOUD_EMAIL_ADMIN:-admin@scitex.ai}"
    fi

    echo_success "Email for certificate: $CERT_EMAIL"
}

# ============================================
# Check DNS Configuration
# ============================================
check_dns() {
    echo_info "Checking DNS configuration..."

    # Get domains from environment
    local main_domain="${SCITEX_CLOUD_DOMAIN:-scitex.ai}"
    local git_domain="${SCITEX_CLOUD_GIT_DOMAIN:-git.scitex.ai}"
    local domains=("$main_domain" "$git_domain")

    # Get server IP from env or auto-detect
    local server_ip="${SCITEX_CLOUD_SERVER_IP}"
    if [ -z "$server_ip" ]; then
        server_ip=$(curl -s ifconfig.me || curl -s icanhazip.com)
    fi

    if [ -z "$server_ip" ]; then
        echo_warning "Could not detect server public IP"
        read -p "Enter your server public IP: " server_ip
    fi

    echo_success "Server IP: $server_ip"

    local dns_ok=true
    for domain in "${domains[@]}"; do
        echo_info "Checking DNS for $domain..."
        local dns_ip=$(dig +short "$domain" | grep -E '^[0-9.]+$' | head -1)

        if [ -z "$dns_ip" ]; then
            echo_error "DNS not configured for $domain"
            dns_ok=false
        elif [ "$dns_ip" != "$server_ip" ]; then
            echo_warning "$domain points to $dns_ip (expected: $server_ip)"
            dns_ok=false
        else
            echo_success "$domain → $dns_ip ✓"
        fi
    done

    if [ "$dns_ok" = false ]; then
        echo_error "DNS configuration issues detected"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo_warning "SSL setup cancelled"
            exit 1
        fi
    fi
}

# ============================================
# Obtain SSL Certificates
# ============================================
obtain_certificates() {
    echo_info "Obtaining SSL certificates..."

    cd "$DOCKER_DIR"

    # Check if services are running
    if ! docker compose ps | grep -q "Up"; then
        echo_info "Starting services..."
        make up
        sleep 5
    fi

    # Get domains from environment
    local main_domain="${SCITEX_CLOUD_DOMAIN:-scitex.ai}"
    local git_domain="${SCITEX_CLOUD_GIT_DOMAIN:-git.scitex.ai}"

    # Obtain certificates
    echo_info "Running certbot for: $main_domain, $git_domain..."
    docker compose run --rm --entrypoint "certbot" certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email "$CERT_EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$main_domain" \
        -d "$git_domain"

    # Verify certificates
    if [ -d "$DOCKER_DIR/../../ssl/live/$main_domain" ]; then
        echo_success "Certificates obtained successfully"
        ls -la "$DOCKER_DIR/../../ssl/live/$main_domain/"
    else
        echo_error "Certificate generation failed"
        exit 1
    fi
}

# ============================================
# Enable HTTPS in Nginx
# ============================================
enable_https() {
    echo_info "Enabling HTTPS in nginx configuration..."

    SITE_CONF="$THIS_DIR/sites-available/scitex_cloud_prod.conf"
    SITE_CONF_BAK="$THIS_DIR/.old/scitex_cloud_prod.conf.backup_$(date +%Y%m%d_%H%M%S)"

    # Backup current config
    mkdir -p "$THIS_DIR/.old"
    cp "$SITE_CONF" "$SITE_CONF_BAK"
    echo_success "Backed up to $SITE_CONF_BAK"

    echo_warning "Manual step required:"
    echo_warning "Edit $SITE_CONF to enable HTTPS:"
    echo_warning "  1. Comment out HTTP server blocks"
    echo_warning "  2. Uncomment HTTPS server blocks"
    echo_warning "  3. Uncomment HTTP→HTTPS redirect"
}

# ============================================
# Restart Nginx
# ============================================
restart_nginx() {
    echo_info "Testing nginx configuration..."

    cd "$DOCKER_DIR"

    if docker compose exec nginx nginx -t; then
        echo_success "Nginx configuration test passed"

        echo_info "Restarting nginx..."
        make restart
        echo_success "Nginx restarted"
    else
        echo_error "Nginx configuration test failed"
        echo_error "Restoring backup..."
        cp "$NGINX_CONF_BAK" "$NGINX_CONF"
        exit 1
    fi
}

# ============================================
# Verify HTTPS
# ============================================
verify_https() {
    echo_info "Verifying HTTPS..."

    # Get domains from environment
    local main_domain="${SCITEX_CLOUD_DOMAIN:-scitex.ai}"
    local git_domain="${SCITEX_CLOUD_GIT_DOMAIN:-git.scitex.ai}"

    sleep 3

    echo_info "Testing https://$main_domain..."
    if curl -Is https://$main_domain | head -1; then
        echo_success "https://$main_domain is working"
    else
        echo_warning "https://$main_domain test failed (might need DNS propagation)"
    fi

    echo_info "Testing https://$git_domain..."
    if curl -Is https://$git_domain | head -1; then
        echo_success "https://$git_domain is working"
    else
        echo_warning "https://$git_domain test failed (might need DNS propagation)"
    fi
}

# ============================================
# Main
# ============================================
main() {
    CERT_EMAIL=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            --email)
                CERT_EMAIL="$2"
                shift 2
                ;;
            -h | --help)
                usage
                ;;
            *)
                echo_error "Unknown option: $1"
                usage
                ;;
        esac
    done

    echo_info "=== SciTeX Cloud - HTTPS Setup ==="
    echo ""

    setup_env
    check_dns
    obtain_certificates

    echo ""
    echo_warning "Manual step required:"
    echo_warning "Edit sites-available/scitex_cloud_prod.conf to enable HTTPS"
    echo_warning "See README.md for details"
    echo ""

    read -p "Have you enabled HTTPS in scitex_cloud_prod.conf? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        restart_nginx
        verify_https

        # Get domains from environment
        local main_domain="${SCITEX_CLOUD_DOMAIN:-scitex.ai}"
        local git_domain="${SCITEX_CLOUD_GIT_DOMAIN:-git.scitex.ai}"

        echo ""
        echo_success "=== HTTPS Setup Complete ==="
        echo_success "Domains: https://$main_domain, https://$git_domain"
    else
        echo_warning "Skipped nginx restart"
        echo_warning "Run 'make restart' after editing scitex_cloud_prod.conf"
    fi
}

main "$@" 2>&1 | tee -a "$LOG_PATH"

# EOF
