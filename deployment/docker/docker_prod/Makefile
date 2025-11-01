# ============================================
# SciTeX Cloud - Docker Production Environment
# ============================================
# Location: /containers/docker_prod/Makefile.prod

.PHONY: help setup build start restart stop down logs ps status rebuild migrate makemigrations shell collectstatic db-shell db-backup verify-health logs-web logs-db logs-redis logs-nginx exec-web exec-db clean-python

.DEFAULT_GOAL := help

# ============================================
# Variables
# ============================================
COMPOSE := docker compose -f docker-compose.yml
WEB_CONTAINER := scitex-cloud-prod-web-1
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
	@echo "  make logs-web           - View web container logs"
	@echo "  make logs-db            - View database logs"
	@echo "  make logs-redis         - View Redis logs"
	@echo "  make logs-nginx         - View Nginx logs"
	@echo ""
	@echo "$(CYAN)🔧 Shell Access:$(NC)"
	@echo "  make exec-web           - Shell into web container"
	@echo "  make exec-db            - Shell into database container"
	@echo ""
	@echo "$(CYAN)🔍 Health & Monitoring:$(NC)"
	@echo "  make verify-health      - Check all services health"
	@echo ""

# ============================================
# Health Check
# ============================================
docker-check-health:
	@if ! docker ps | grep -q "$(WEB_CONTAINER)"; then \
		echo "$(RED)❌ Web container not running!$(NC)"; \
		echo "$(YELLOW)Run 'make start' first.$(NC)"; \
		exit 1; \
	fi

# ============================================
# Deployment Commands
# ============================================
setup: build up migrate collectstatic
	@echo "$(GREEN)✅ Production setup complete!$(NC)"
	@echo "$(YELLOW)⚠️  Remember to configure SSL and domain settings$(NC)"

start: up
	@echo "$(GREEN)✅ Production services started$(NC)"

restart:
	@echo "$(CYAN)🔄 Restarting production services...$(NC)"
	$(COMPOSE) restart
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
	$(COMPOSE) exec -T web python manage.py migrate
	@echo "$(GREEN)✅ Migrations applied$(NC)"

makemigrations: docker-check-health
	@echo "$(RED)⚠️  WARNING: This should be done in development!$(NC)"
	@read -p "Continue anyway? Type 'yes' to confirm: " confirm && \
	[ "$$confirm" = "yes" ] && \
	$(COMPOSE) exec -T web python manage.py makemigrations || \
	echo "$(YELLOW)❌ Cancelled$(NC)"

shell: docker-check-health
	@echo "$(CYAN)🐍 Opening Django shell (production)...$(NC)"
	@echo "$(YELLOW)⚠️  BE CAREFUL - This is production!$(NC)"
	$(COMPOSE) exec web python manage.py shell

collectstatic: docker-check-health
	@echo "$(CYAN)📦 Collecting static files...$(NC)"
	$(COMPOSE) exec -T web python manage.py collectstatic --noinput
	@echo "$(GREEN)✅ Static files collected$(NC)"

# ============================================
# Database Commands
# ============================================
db-shell: docker-check-health
	@echo "$(CYAN)🗄️  Opening PostgreSQL shell (production)...$(NC)"
	@echo "$(YELLOW)⚠️  BE CAREFUL - This is production!$(NC)"
	@$(COMPOSE) exec db psql -U $${POSTGRES_USER} -d $${POSTGRES_DB}

db-backup: docker-check-health
	@echo "$(CYAN)💾 Backing up production database...$(NC)"
	@mkdir -p ../../backups
	@BACKUP_FILE="../../backups/scitex_prod_$$(date +%Y%m%d_%H%M%S).sql" && \
	$(COMPOSE) exec -T db pg_dump -U $${POSTGRES_USER} $${POSTGRES_DB} > $$BACKUP_FILE && \
	gzip $$BACKUP_FILE && \
	echo "$(GREEN)✅ Backup saved to: $$BACKUP_FILE.gz$(NC)"

# ============================================
# Logs & Monitoring
# ============================================
logs:
	@echo "$(CYAN)📋 Showing production logs (Ctrl+C to exit)...$(NC)"
	$(COMPOSE) logs -f --tail=100

logs-web:
	@echo "$(CYAN)📋 Showing web logs...$(NC)"
	$(COMPOSE) logs -f --tail=100 web

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
exec-web: docker-check-health
	@echo "$(CYAN)🐳 Opening shell in web container...$(NC)"
	$(COMPOSE) exec web /bin/bash

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

# EOF
