# ============================================
# SciTeX Cloud - Docker Production Environment
# ============================================
# Location: /containers/docker_prod/Makefile.prod

.PHONY: help setup build build-ts start restart stop down logs ps status rebuild migrate makemigrations shell collectstatic db-shell db-backup verify-health logs-django logs-db logs-redis logs-nginx exec-django exec-db clean-python ssl-setup ssl-check ssl-create ssl-renew ssl-verify ssl-auto list-envs

.DEFAULT_GOAL := help

# ============================================
# Variables
# ============================================
COMPOSE := docker compose -f docker-compose.yml
DJANGO_CONTAINER := scitex-cloud-prod-django-1
DB_CONTAINER := scitex-cloud-prod-db-1
REDIS_CONTAINER := scitex-cloud-prod-redis-1
NGINX_CONTAINER := scitex-cloud-prod-nginx-1

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
CYAN := \033[0;36m
NC := \033[0m

# ============================================
# Help (default target)
# ============================================
help:
	@echo ""
	@echo "$(GREEN)╔═══════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║          SciTeX Cloud - Production Mode               ║$(NC)"
	@echo "$(GREEN)╚═══════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(RED)⚠️  PRODUCTION ENVIRONMENT - USE WITH CAUTION ⚠️$(NC)"
	@echo ""
	@echo "$(CYAN)🚀 Deployment:$(NC)"
	@echo "  make start              - Start production services"
	@echo "  make restart            - Restart services"
	@echo "  make stop               - Stop all services"
	@echo "  make status             - Show service status"
	@echo ""
	@echo "$(CYAN)🐳 Docker Management:$(NC)"
	@echo "  make build              - Build Docker images"
	@echo "  make up                 - Start services (no rebuild)"
	@echo "  make down               - Stop and remove containers"
	@echo "  make ps                 - Show container status"
	@echo "  make rebuild            - Clean rebuild (⚠️  CAUSES DOWNTIME)"
	@echo ""
	@echo "$(CYAN)🐍 Django Management:$(NC)"
	@echo "  make migrate            - Run database migrations"
	@echo "  make makemigrations     - Create new migrations (dev only)"
	@echo "  make shell              - Open Django shell"
	@echo "  make collectstatic      - Collect static files"
	@echo ""
	@echo "$(CYAN)🗄️  Database:$(NC)"
	@echo "  make db-shell           - PostgreSQL shell"
	@echo "  make db-backup          - Backup database"
	@echo ""
	@echo "$(CYAN)📋 Logs & Monitoring:$(NC)"
	@echo "  make logs               - View all service logs"
	@echo "  make logs-django        - View Django container logs"
	@echo "  make logs-db            - View database logs"
	@echo "  make logs-redis         - View Redis logs"
	@echo "  make logs-nginx         - View Nginx logs"
	@echo ""
	@echo "$(CYAN)🔧 Shell Access & Debug:$(NC)"
	@echo "  make exec-django        - Shell into Django container"
	@echo "  make exec-db            - Shell into database container"
	@echo "  make list-envs          - List environment variables"
	@echo ""
	@echo "$(CYAN)🔍 Health & Monitoring:$(NC)"
	@echo "  make verify-health      - Check all services health"
	@echo ""
	@echo "$(CYAN)🔒 SSL/HTTPS Management:$(NC)"
	@echo "  make ssl-auto           - Automatic SSL management (runs in start/restart)"
	@echo "  make ssl-verify         - Verify HTTPS is working"
	@echo "  make ssl-check          - Check certificate status"
	@echo "  make ssl-renew          - Renew certificates"
	@echo ""

# ============================================
# Health Check
# ============================================
docker-check-health:
	@if ! docker ps | grep -q "$(DJANGO_CONTAINER)"; then \
		echo "$(RED)❌ Django container not running!$(NC)"; \
		echo "$(YELLOW)Run 'make start' first.$(NC)"; \
		exit 1; \
	fi

# ============================================
# Deployment Commands
# ============================================
setup: build up migrate collectstatic ssl-auto
	@echo "$(GREEN)✅ Production setup complete!$(NC)"

start: up ssl-auto
	@echo "$(GREEN)✅ Production services started$(NC)"

restart:
	@echo "$(CYAN)🔄 Restarting production services...$(NC)"
	$(COMPOSE) restart
	@$(MAKE) ssl-verify || true
	@echo "$(GREEN)✅ Services restarted$(NC)"

stop: down

build:
	@echo "$(CYAN)🏗️  Building production images...$(NC)"
	$(COMPOSE) build --no-cache
	@echo "$(GREEN)✅ Build complete$(NC)"

up:
	@echo "$(CYAN)⬆️  Starting production services...$(NC)"
	$(COMPOSE) up -d
	@echo "$(GREEN)✅ Services started$(NC)"

down:
	@echo "$(YELLOW)⬇️  Stopping production services...$(NC)"
	$(COMPOSE) down
	@echo "$(GREEN)✅ Services stopped$(NC)"

ps:
	@echo "$(CYAN)📊 Container Status:$(NC)"
	$(COMPOSE) ps

status: ps verify-health

rebuild:
	@echo "$(RED)⚠️  WARNING: This will cause production downtime!$(NC)"
	@read -p "Are you absolutely sure? Type 'yes' to confirm: " confirm && \
	[ "$$confirm" = "yes" ] && \
	(echo "$(CYAN)🔄 Rebuilding production environment...$(NC)" && \
	$(COMPOSE) down && \
	$(COMPOSE) build --no-cache && \
	$(COMPOSE) up -d && \
	make migrate && \
	make collectstatic && \
	echo "$(GREEN)✅ Rebuild complete$(NC)") || \
	echo "$(YELLOW)❌ Rebuild cancelled$(NC)"

# ============================================
# Django Management
# ============================================
migrate: docker-check-health
	@echo "$(CYAN)🔄 Running migrations (production)...$(NC)"
	$(COMPOSE) exec -T django python manage.py migrate
	@echo "$(GREEN)✅ Migrations applied$(NC)"

makemigrations: docker-check-health
	@echo "$(RED)⚠️  WARNING: This should be done in development!$(NC)"
	@read -p "Continue anyway? Type 'yes' to confirm: " confirm && \
	[ "$$confirm" = "yes" ] && \
	$(COMPOSE) exec -T django python manage.py makemigrations || \
	echo "$(YELLOW)❌ Cancelled$(NC)"

shell: docker-check-health
	@echo "$(CYAN)🐍 Opening Django shell (production)...$(NC)"
	@echo "$(YELLOW)⚠️  BE CAREFUL - This is production!$(NC)"
	$(COMPOSE) exec django python manage.py shell

build-ts:
	@echo "$(CYAN)🔨 Building TypeScript...$(NC)"
	@cd ../../.. && cd tsconfig && npm install --silent && npm run build:all
	@echo "$(GREEN)✅ TypeScript compiled$(NC)"

collectstatic: docker-check-health build-ts
	@echo "$(CYAN)📦 Collecting static files...$(NC)"
	$(COMPOSE) exec -T django python manage.py collectstatic --noinput
	@echo "$(GREEN)✅ Static files collected$(NC)"

# ============================================
# Database Commands
# ============================================
db-shell: docker-check-health
	@echo "$(CYAN)🗄️  Opening PostgreSQL shell (production)...$(NC)"
	@echo "$(YELLOW)⚠️  BE CAREFUL - This is production!$(NC)"
	@$(COMPOSE) exec db psql -U $${SCITEX_CLOUD_POSTGRES_USER} -d $${SCITEX_CLOUD_POSTGRES_DB}

db-backup: docker-check-health
	@echo "$(CYAN)💾 Backing up production database...$(NC)"
	@mkdir -p ../../backups
	@BACKUP_FILE="../../backups/scitex_prod_$$(date +%Y%m%d_%H%M%S).sql" && \
	$(COMPOSE) exec -T db pg_dump -U $${SCITEX_CLOUD_POSTGRES_USER} $${SCITEX_CLOUD_POSTGRES_DB} > $$BACKUP_FILE && \
	gzip $$BACKUP_FILE && \
	echo "$(GREEN)✅ Backup saved to: $$BACKUP_FILE.gz$(NC)"

# ============================================
# Logs & Monitoring
# ============================================
logs:
	@echo "$(CYAN)📋 Showing production logs (Ctrl+C to exit)...$(NC)"
	$(COMPOSE) logs -f --tail=100

logs-django:
	@echo "$(CYAN)📋 Showing Django logs...$(NC)"
	$(COMPOSE) logs -f --tail=100 django

logs-db:
	@echo "$(CYAN)📋 Showing database logs...$(NC)"
	$(COMPOSE) logs -f --tail=100 db

logs-redis:
	@echo "$(CYAN)📋 Showing Redis logs...$(NC)"
	$(COMPOSE) logs -f --tail=100 redis

logs-nginx:
	@echo "$(CYAN)📋 Showing Nginx logs...$(NC)"
	$(COMPOSE) logs -f --tail=100 nginx 2>/dev/null || echo "$(YELLOW)Nginx not configured$(NC)"

# ============================================
# Shell Access
# ============================================
exec-django: docker-check-health
	@echo "$(CYAN)🐳 Opening shell in Django container...$(NC)"
	$(COMPOSE) exec django /bin/bash

exec-db: docker-check-health
	@echo "$(CYAN)🐳 Opening shell in database container...$(NC)"
	$(COMPOSE) exec db /bin/sh

# ============================================
# Health & Monitoring
# ============================================
verify-health:
	@echo "$(CYAN)🔍 Checking service health...$(NC)"
	@$(COMPOSE) ps | grep -E "(healthy|Up)" && \
		echo "$(GREEN)✅ All services healthy$(NC)" || \
		echo "$(RED)❌ Some services unhealthy$(NC)"

# ============================================
# Utilities
# ============================================
clean-python:
	@echo "$(CYAN)🧹 Cleaning Python cache files...$(NC)"
	find ../../ -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find ../../ -type f -name "*.pyc" -delete
	@echo "$(GREEN)✅ Python cache cleaned$(NC)"

# ============================================
# SSL/HTTPS Management (Automatic)
# ============================================

# Check if SSL certificates exist and are valid
ssl-check:
	@echo "$(CYAN)🔍 Checking SSL certificates...$(NC)"
	@bash -c 'if [ -f ".env" ]; then source .env; fi; \
	DOMAIN=$${SCITEX_CLOUD_DOMAIN:-scitex.ai}; \
	if docker exec scitex-cloud-prod-nginx test -f /etc/nginx/ssl/live/$$DOMAIN/fullchain.pem 2>/dev/null; then \
		echo "✅ Certificates exist for $$DOMAIN"; \
		$(COMPOSE) run --rm --entrypoint "certbot" certbot certificates 2>/dev/null | grep -E "Certificate Name|Expiry Date" || true; \
	else \
		echo "⚠️  No certificates found for $$DOMAIN"; \
		exit 1; \
	fi'

# Create new SSL certificates (non-interactive)
ssl-create:
	@echo "$(CYAN)🔒 Creating SSL certificates...$(NC)"
	@bash -c 'if [ -f ".env" ]; then source .env; fi && \
	$(COMPOSE) run --rm --entrypoint "certbot" certbot certonly \
		--webroot -w /var/www/certbot \
		--email $${SCITEX_CLOUD_EMAIL_ADMIN:-admin@$${SCITEX_CLOUD_DOMAIN:-scitex.ai}} \
		--agree-tos --no-eff-email --non-interactive \
		-d $${SCITEX_CLOUD_DOMAIN:-scitex.ai} \
		-d $${SCITEX_CLOUD_GIT_DOMAIN:-git.scitex.ai} && \
	echo "$(GREEN)✅ Certificates created$(NC)" || \
	echo "$(RED)❌ Certificate creation failed$(NC)"'

# Enable HTTPS in nginx configuration
ssl-enable:
	@echo "$(CYAN)🔧 Enabling HTTPS in nginx configuration...$(NC)"
	@bash nginx/enable_https.sh
	@echo "$(CYAN)⏳ Waiting for nginx to be ready...$(NC)"
	@for i in 1 2 3 4 5; do \
		if docker ps --filter "name=scitex-cloud-prod-nginx" --filter "status=running" | grep -q scitex-cloud-prod-nginx; then \
			break; \
		fi; \
		echo "  Waiting... ($$i/5)"; \
		sleep 2; \
	done
	@if docker ps --filter "name=scitex-cloud-prod-nginx" --filter "status=running" | grep -q scitex-cloud-prod-nginx; then \
		$(COMPOSE) exec nginx nginx -t && \
		$(COMPOSE) exec nginx nginx -s reload && \
		echo "$(GREEN)✅ HTTPS enabled$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Nginx not ready yet - config updated but not reloaded$(NC)"; \
		echo "$(YELLOW)Run 'make restart' to apply changes$(NC)"; \
	fi

# Renew SSL certificates
ssl-renew:
	@echo "$(CYAN)🔄 Renewing SSL certificates...$(NC)"
	@$(COMPOSE) run --rm --entrypoint "certbot" certbot renew && \
	$(COMPOSE) exec nginx nginx -s reload && \
	echo "$(GREEN)✅ Certificates renewed$(NC)"

# Verify HTTPS is working
ssl-verify:
	@echo "$(CYAN)🔍 Verifying HTTPS...$(NC)"
	@bash -c 'set -e; \
	if [ -f ".env" ]; then source .env; fi; \
	MAIN_DOMAIN=$${SCITEX_CLOUD_DOMAIN:-scitex.ai}; \
	GIT_DOMAIN=$${SCITEX_CLOUD_GIT_DOMAIN:-git.scitex.ai}; \
	echo "  Testing https://$$MAIN_DOMAIN..."; \
	STATUS=$$(curl -sI https://$$MAIN_DOMAIN 2>/dev/null | head -1 | grep -o "[0-9]\{3\}"); \
	if [ "$$STATUS" = "200" ]; then \
		echo "  ✅ https://$$MAIN_DOMAIN → $$STATUS"; \
	else \
		echo "  ❌ https://$$MAIN_DOMAIN → $$STATUS"; \
	fi; \
	echo "  Testing https://$$GIT_DOMAIN..."; \
	STATUS=$$(curl -sI https://$$GIT_DOMAIN 2>/dev/null | head -1 | grep -o "[0-9]\{3\}"); \
	if [ "$$STATUS" = "200" ]; then \
		echo "  ✅ https://$$GIT_DOMAIN → $$STATUS"; \
	else \
		echo "  ❌ https://$$GIT_DOMAIN → $$STATUS"; \
	fi; \
	echo "  Testing HTTP→HTTPS redirect..."; \
	REDIRECT=$$(curl -sI http://$$MAIN_DOMAIN 2>/dev/null | grep -o "301\|302"); \
	if [ -n "$$REDIRECT" ]; then \
		echo "  ✅ HTTP redirects to HTTPS ($$REDIRECT)"; \
	else \
		echo "  ⚠️  No HTTP redirect"; \
	fi'

# Automatic SSL management (integrated into start/restart)
ssl-auto:
	@echo "$(CYAN)🤖 Automatic SSL management...$(NC)"
	@bash -c 'if [ -f ".env" ]; then source .env; fi; \
	MAIN_DOMAIN=$${SCITEX_CLOUD_DOMAIN:-scitex.ai}; \
	if ! docker exec scitex-cloud-prod-nginx test -f /etc/nginx/ssl/live/$$MAIN_DOMAIN/fullchain.pem 2>/dev/null; then \
		echo "⚠️  No certificates found - creating..."; \
		$(MAKE) ssl-create && $(MAKE) ssl-enable; \
	else \
		echo "✅ Certificates already exist"; \
		$(MAKE) ssl-verify || true; \
	fi'

# Manual SSL setup (interactive - for initial setup)
ssl-setup:
	@echo "$(CYAN)🔒 Setting up SSL/HTTPS (interactive)...$(NC)"
	@bash $(CURDIR)/nginx/setup_nginx.sh

# ============================================
# Utilities
# ============================================

# List environment variables in Django container
list-envs:
	@echo "$(CYAN)🔍 Environment variables in Django container:$(NC)"
	@echo ""
	@echo "$(CYAN)━━━ SCITEX_CLOUD_* variables ━━━$(NC)"
	@$(COMPOSE) exec -T django env | grep "^SCITEX_CLOUD_" | sort || true
	@echo ""
	@echo "$(CYAN)━━━ SCITEX_* variables (non-CLOUD) ━━━$(NC)"
	@$(COMPOSE) exec -T django env | grep "^SCITEX_" | grep -v "^SCITEX_CLOUD_" | sort || true
	@echo ""
	@echo "$(CYAN)━━━ SCITEX_CLOUD_EMAIL_* variables ━━━$(NC)"
	@$(COMPOSE) exec -T django env | grep "^SCITEX_CLOUD_EMAIL_" | sort || true
	@echo ""
	@echo "$(CYAN)━━━ Django variables ━━━$(NC)"
	@$(COMPOSE) exec -T django env | grep -E "^(DEBUG|DJANGO_|SCITEX_CLOUD_DJANGO_SECRET_KEY|SCITEX_CLOUD_ALLOWED_HOSTS|SCITEX_CLOUD_POSTGRES_URL|SCITEX_CLOUD_REDIS_URL)" | sort || true
	@echo ""
	@echo "$(CYAN)━━━ Database variables ━━━$(NC)"
	@$(COMPOSE) exec -T django env | grep -E "^(POSTGRES_|DB_)" | sort || true

# EOF

