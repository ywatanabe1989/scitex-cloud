# ============================================
# SciTeX Cloud - Docker Development Environment
# ============================================
# Location: /containers/docker_dev/Makefile.dev

.PHONY: help setup build build-ts start restart stop down logs ps clean rebuild test migrate makemigrations shell createsuperuser collectstatic db-shell db-reset verify-env docker-check-health logs-web logs-db logs-gitea logs-redis exec-web exec-db exec-gitea gitea-token verify-gitea recreate-testuser list-env clean-python dev update reset

.DEFAULT_GOAL := help

# ============================================
# Variables
# ============================================
COMPOSE := docker compose -f docker-compose.yml
WEB_CONTAINER := scitex-cloud-dev-web-1
DB_CONTAINER := scitex-cloud-dev-db-1
GITEA_CONTAINER := scitex-cloud-dev-gitea-1
REDIS_CONTAINER := scitex-cloud-dev-redis-1
SCRIPTS_DIR := .

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
	@echo "$(GREEN)║          SciTeX Cloud - Development Mode              ║$(NC)"
	@echo "$(GREEN)╚═══════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(CYAN)🚀 Quick Start:$(NC)"
	@echo "  make start              - Full setup from scratch (recommended)"
	@echo "  make restart            - Quick restart of web container"
	@echo "  make reload             - Super quick reload (for scitex changes)"
	@echo "  make logs               - View all service logs"
	@echo "  make stop               - Stop all services"
	@echo ""
	@echo "$(CYAN)🐳 Docker Services:$(NC)"
	@echo "  make build              - Build Docker images"
	@echo "  make up                 - Start all services (no rebuild)"
	@echo "  make down               - Stop and remove containers"
	@echo "  make ps                 - Show service status"
	@echo "  make rebuild            - Clean rebuild (stops, builds, starts)"
	@echo "  make clean              - Remove containers and volumes (⚠️  DANGEROUS)"
	@echo ""
	@echo "$(CYAN)🐍 Django Management:$(NC)"
	@echo "  make migrate            - Run database migrations"
	@echo "  make makemigrations     - Create new migrations"
	@echo "  make shell              - Open Django shell"
	@echo "  make createsuperuser    - Create superuser account"
	@echo "  make build-ts           - Compile TypeScript to JavaScript"
	@echo "  make collectstatic      - Collect static files (includes compiled JS)"
	@echo "  make test               - Run test suite"
	@echo ""
	@echo "$(CYAN)🗄️  Database:$(NC)"
	@echo "  make db-shell           - PostgreSQL shell"
	@echo "  make db-reset           - Reset database (⚠️  DELETES ALL DATA)"
	@echo ""
	@echo "$(CYAN)📋 Logs & Monitoring:$(NC)"
	@echo "  make logs               - View all service logs"
	@echo "  make logs-web           - View web container logs"
	@echo "  make logs-db            - View database logs"
	@echo "  make logs-gitea         - View Gitea logs"
	@echo "  make logs-redis         - View Redis logs"
	@echo ""
	@echo "$(CYAN)🔧 Shell Access:$(NC)"
	@echo "  make exec-web           - Shell into web container"
	@echo "  make exec-db            - Shell into database container"
	@echo "  make exec-gitea         - Shell into Gitea container"
	@echo ""
	@echo "$(CYAN)🔑 Gitea Management:$(NC)"
	@echo "  make gitea-token        - Generate/verify Gitea API token"
	@echo "  make verify-gitea       - Verify Gitea API access"
	@echo "  make recreate-testuser  - Recreate test user"
	@echo ""
	@echo "$(CYAN)🧪 Development Shortcuts:$(NC)"
	@echo "  make dev                - Full dev cycle (start + migrate + collectstatic)"
	@echo "  make update             - Quick update (restart)"
	@echo "  make reset              - Full reset (down + clean + start)"
	@echo ""
	@echo "$(YELLOW)Access URLs:$(NC)"
	@echo "  📍 Django: http://localhost:8000"
	@echo "  📍 Gitea:  http://localhost:3000"
	@echo ""

# ============================================
# Setup & Build Commands
# ============================================
setup: start migrate build-ts collectstatic
	@echo "$(GREEN)✅ Development setup complete!$(NC)"

start:
	@echo "$(CYAN)🚀 Starting development environment...$(NC)"
	cd $(CURDIR) && bash $(CURDIR)/start.sh -a start

restart:
	@echo "$(CYAN)🔄 Restarting web container...$(NC)"
	cd $(CURDIR) && bash $(CURDIR)/start.sh -a restart

reload:
	@echo "$(CYAN)⚡ Quick reload (for scitex code changes)...$(NC)"
	$(COMPOSE) restart web
	@echo "$(GREEN)✅ Reloaded!$(NC)"

build:
	@echo "$(CYAN)🏗️  Building Docker images...$(NC)"
	DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 $(COMPOSE) build --parallel

up:
	@echo "$(CYAN)⬆️  Starting services...$(NC)"
	$(COMPOSE) up -d
	@echo "$(GREEN)✅ Services started$(NC)"

down:
	@echo "$(YELLOW)⬇️  Stopping services...$(NC)"
	$(COMPOSE) down
	@echo "$(GREEN)✅ Services stopped$(NC)"

stop: down

ps:
	@echo "$(CYAN)📊 Service Status:$(NC)"
	$(COMPOSE) ps

rebuild: down build up migrate build-ts collectstatic
	@echo "$(GREEN)✅ Rebuild complete!$(NC)"

clean:
	@echo "$(RED)⚠️  WARNING: This will remove ALL containers and volumes!$(NC)"
	@read -p "Are you absolutely sure? Type 'yes' to confirm: " confirm && \
	[ "$$confirm" = "yes" ] && \
	(echo "$(RED)🗑️  Removing containers and volumes...$(NC)" && \
	$(COMPOSE) down -v && \
	echo "$(GREEN)✅ Cleanup complete$(NC)") || \
	echo "$(YELLOW)❌ Cleanup cancelled$(NC)"

# ============================================
# Docker Health Check
# ============================================
docker-check-health:
	@if ! docker ps | grep -q $(WEB_CONTAINER); then \
		echo "$(RED)❌ Web container ($(WEB_CONTAINER)) is not running!$(NC)"; \
		echo "$(YELLOW)Run 'make start' first.$(NC)"; \
		exit 1; \
	fi

# ============================================
# Django Management Commands
# ============================================
migrate: docker-check-health
	@echo "$(CYAN)🔄 Running migrations...$(NC)"
	$(COMPOSE) exec -T web python manage.py migrate
	@echo "$(GREEN)✅ Migrations applied$(NC)"

makemigrations: docker-check-health
	@echo "$(CYAN)📝 Creating migrations...$(NC)"
	$(COMPOSE) exec -T web python manage.py makemigrations
	@echo "$(GREEN)✅ Migrations created$(NC)"

shell: docker-check-health
	@echo "$(CYAN)🐍 Opening Django shell...$(NC)"
	$(COMPOSE) exec web python manage.py shell

createsuperuser: docker-check-health
	@echo "$(CYAN)👤 Creating superuser...$(NC)"
	$(COMPOSE) exec web python manage.py createsuperuser

build-ts:
	@echo "$(CYAN)🔨 Building TypeScript...$(NC)"
	@cd ../../.. && cd frontend && npm run build:writer
	@echo "$(GREEN)✅ TypeScript compiled$(NC)"

collectstatic: docker-check-health
	@echo "$(CYAN)📦 Collecting static files...$(NC)"
	$(COMPOSE) exec -T web python manage.py collectstatic --noinput
	@echo "$(GREEN)✅ Static files collected$(NC)"

test: docker-check-health
	@echo "$(CYAN)🧪 Running tests...$(NC)"
	$(COMPOSE) exec -T web python manage.py test
	@echo "$(GREEN)✅ Tests completed$(NC)"

# ============================================
# Database Commands
# ============================================
db-shell: docker-check-health
	@echo "$(CYAN)🗄️  Opening PostgreSQL shell...$(NC)"
	@$(COMPOSE) exec db psql -U $${SCITEX_CLOUD_POSTGRES_USER:-scitex_dev} -d $${SCITEX_CLOUD_POSTGRES_DB:-scitex_cloud_dev}

db-reset: docker-check-health
	@echo "$(RED)⚠️  WARNING: This will DELETE ALL DATA in the database!$(NC)"
	@read -p "Are you absolutely sure? Type 'yes' to confirm: " confirm && \
	[ "$$confirm" = "yes" ] && \
	(echo "$(RED)🔄 Resetting database...$(NC)" && \
	$(COMPOSE) exec -T web python manage.py flush --noinput && \
	$(COMPOSE) exec -T web python manage.py migrate && \
	echo "$(GREEN)✅ Database reset complete$(NC)") || \
	echo "$(YELLOW)❌ Database reset cancelled$(NC)"

# ============================================
# Logs & Monitoring
# ============================================
logs:
	@echo "$(CYAN)📋 Showing all service logs (Ctrl+C to exit)...$(NC)"
	$(COMPOSE) logs -f

logs-web:
	@echo "$(CYAN)📋 Showing web container logs...$(NC)"
	$(COMPOSE) logs -f web

logs-db:
	@echo "$(CYAN)📋 Showing database logs...$(NC)"
	$(COMPOSE) logs -f db

logs-gitea:
	@echo "$(CYAN)📋 Showing Gitea logs...$(NC)"
	$(COMPOSE) logs -f gitea

logs-redis:
	@echo "$(CYAN)📋 Showing Redis logs...$(NC)"
	$(COMPOSE) logs -f redis

# ============================================
# Shell Access
# ============================================
exec-web: docker-check-health
	@echo "$(CYAN)🐳 Opening shell in web container...$(NC)"
	$(COMPOSE) exec web /bin/bash

exec-db: docker-check-health
	@echo "$(CYAN)🐳 Opening shell in database container...$(NC)"
	$(COMPOSE) exec db /bin/sh

exec-gitea: docker-check-health
	@echo "$(CYAN)🐳 Opening shell in Gitea container...$(NC)"
	$(COMPOSE) exec gitea /bin/sh

# ============================================
# Gitea Management
# ============================================
gitea-token: docker-check-health
	@echo "$(CYAN)🔑 Setting up Gitea API token...$(NC)"
	cd $(CURDIR) && bash $(CURDIR)/start.sh -a setup_gitea_token

verify-gitea: docker-check-health
	@echo "$(CYAN)🔍 Verifying Gitea API access...$(NC)"
	cd $(CURDIR) && bash $(CURDIR)/start.sh -a verify_gitea_api

recreate-testuser: docker-check-health
	@echo "$(CYAN)👤 Recreating test user...$(NC)"
	cd $(CURDIR) && bash $(CURDIR)/start.sh -a recreate_test_user

# ============================================
# Environment & Utilities
# ============================================
verify-env:
	@echo "$(CYAN)🔍 Verifying environment setup...$(NC)"
	cd $(CURDIR) && bash $(CURDIR)/start.sh -a verify_env_setup

list-env:
	@echo "$(CYAN)📝 Environment Variables:$(NC)"
	cd $(CURDIR) && bash $(CURDIR)/start.sh -a list_env

clean-python:
	@echo "$(CYAN)🧹 Cleaning Python cache files...$(NC)"
	find ../../ -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find ../../ -type f -name "*.pyc" -delete
	find ../../ -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Python cache cleaned$(NC)"

# ============================================
# Development Workflow Shortcuts
# ============================================
dev: start migrate collectstatic
	@echo "$(GREEN)✅ Development environment ready!$(NC)"
	@echo "$(GREEN)📍 Django: http://localhost:8000$(NC)"
	@echo "$(GREEN)📍 Gitea:  http://localhost:3000$(NC)"

update: restart
	@echo "$(GREEN)✅ Services updated$(NC)"

reset: down clean start migrate collectstatic
	@echo "$(GREEN)✅ Environment reset complete$(NC)"

# EOF
