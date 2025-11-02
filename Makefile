# ============================================
# SciTeX Cloud - Root Makefile
# ============================================
# Automatic environment switching for Docker deployments
# Location: /Makefile

.PHONY: help dev prod nas start restart stop down logs ps migrate shell db-shell db-backup clean ssl-setup ssl-verify ssl-check ssl-renew verify-health list-envs

.DEFAULT_GOAL := help

# ============================================
# Environment Detection
# ============================================
# Default to dev if ENV not specified
ENV ?= dev

# Validate environment
ifeq ($(filter $(ENV),dev prod nas),)
$(error Invalid ENV='$(ENV)'. Use: dev, prod, or nas)
endif

# Set paths based on environment
DOCKER_DIR := deployment/docker/docker_$(ENV)
COMPOSE_FILE := $(DOCKER_DIR)/docker-compose.yml
MAKEFILE := $(DOCKER_DIR)/Makefile

# Colors
GREEN := \033[0;32m
YELLOW := \033[0;33m
CYAN := \033[0;36m
NC := \033[0m

# ============================================
# Help
# ============================================
help:
	@echo ""
	@echo "$(GREEN)╔═══════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║           SciTeX Cloud - Root Makefile                ║$(NC)"
	@echo "$(GREEN)╚═══════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(CYAN)📍 Current Environment: $(ENV)$(NC)"
	@echo ""
	@echo "$(CYAN)🔀 Switch Environment:$(NC)"
	@echo "  make ENV=dev <command>      # Development"
	@echo "  make ENV=prod <command>     # Production"
	@echo "  make ENV=nas <command>      # NAS/Home server"
	@echo ""
	@echo "$(CYAN)🚀 Quick Start:$(NC)"
	@echo "  make start                  # Start services (current: $(ENV))"
	@echo "  make restart                # Restart services"
	@echo "  make stop                   # Stop services"
	@echo "  make logs                   # View logs"
	@echo ""
	@echo "$(CYAN)🐍 Django:$(NC)"
	@echo "  make migrate                # Run migrations"
	@echo "  make makemigrations         # Create migrations"
	@echo "  make shell                  # Django shell"
	@echo "  make collectstatic          # Collect static files"
	@echo ""
	@echo "$(CYAN)🗄️  Database:$(NC)"
	@echo "  make db-shell               # PostgreSQL shell"
	@echo "  make db-backup              # Backup database"
	@echo "  make db-reset               # Reset database (⚠️  dev only)"
	@echo ""
	@echo "$(CYAN)📋 Monitoring:$(NC)"
	@echo "  make ps                     # Service status"
	@echo "  make logs                   # All logs"
	@echo "  make logs-web               # Web logs only"
	@echo ""
	@echo "$(CYAN)🔧 Utilities:$(NC)"
	@echo "  make clean                  # Clean Python cache"
	@echo "  make exec-web               # Shell into web container"
	@echo "  make list-envs              # List environment variables in container"
	@echo ""
	@echo "$(CYAN)🔒 SSL/HTTPS (prod only):$(NC)"
	@echo "  make ENV=prod ssl-verify    # Verify HTTPS is working"
	@echo "  make ENV=prod ssl-check     # Check certificate status"
	@echo "  make ENV=prod ssl-renew     # Renew certificates"
	@echo "  make ENV=prod ssl-setup     # Manual SSL setup (interactive)"
	@echo ""
	@echo "$(CYAN)💡 Examples:$(NC)"
	@echo "  make start                  # Start dev (default)"
	@echo "  make ENV=prod start         # Start production"
	@echo "  make ENV=prod ssl-setup     # Setup HTTPS for production"
	@echo "  make ENV=nas logs           # View NAS logs"
	@echo ""
	@echo "$(YELLOW)For all commands: cd $(DOCKER_DIR) && make help$(NC)"
	@echo ""

# ============================================
# Environment Shortcuts
# ============================================
dev:
	@$(MAKE) ENV=dev help

prod:
	@$(MAKE) ENV=prod help

nas:
	@$(MAKE) ENV=nas help

# ============================================
# Service Lifecycle
# ============================================
start:
	@echo "$(CYAN)🚀 Starting $(ENV) environment...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) start

restart:
	@echo "$(CYAN)🔄 Restarting $(ENV) environment...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) restart

reload:
	@echo "$(CYAN)⚡ Quick reload ($(ENV))...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) reload

stop:
	@echo "$(YELLOW)⬇️  Stopping $(ENV) environment...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile down

down: stop

build:
	@echo "$(CYAN)🏗️  Building $(ENV) images...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile build

up:
	@echo "$(CYAN)⬆️  Starting $(ENV) services...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile up

rebuild:
	@echo "$(CYAN)🔄 Rebuilding $(ENV) environment...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile rebuild

clean:
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile clean

# ============================================
# Django Commands
# ============================================
migrate:
	@echo "$(CYAN)🔄 Running migrations ($(ENV))...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile migrate

makemigrations:
	@echo "$(CYAN)📝 Creating migrations ($(ENV))...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile makemigrations

shell:
	@echo "$(CYAN)🐍 Opening Django shell ($(ENV))...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile shell

createsuperuser:
	@echo "$(CYAN)👤 Creating superuser ($(ENV))...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile createsuperuser

collectstatic:
	@echo "$(CYAN)📦 Collecting static files ($(ENV))...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile collectstatic

test:
	@echo "$(CYAN)🧪 Running tests ($(ENV))...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile test

# ============================================
# Database Commands
# ============================================
db-shell:
	@echo "$(CYAN)🗄️  Opening database shell ($(ENV))...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile db-shell

db-backup:
	@echo "$(CYAN)💾 Backing up database ($(ENV))...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile db-backup

db-reset:
ifeq ($(ENV),dev)
	@echo "$(YELLOW)⚠️  Resetting database (dev only)...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile db-reset
else
	@echo "$(YELLOW)❌ db-reset only available in dev environment$(NC)"
	@exit 1
endif

# ============================================
# Logs & Monitoring
# ============================================
logs:
	@echo "$(CYAN)📋 Showing logs ($(ENV))...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile logs

logs-web:
	@echo "$(CYAN)📋 Showing web logs ($(ENV))...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile logs-web

logs-db:
	@echo "$(CYAN)📋 Showing database logs ($(ENV))...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile logs-db

logs-gitea:
	@echo "$(CYAN)📋 Showing Gitea logs ($(ENV))...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile logs-gitea 2>/dev/null || echo "$(YELLOW)Gitea not available in $(ENV)$(NC)"

ps:
	@echo "$(CYAN)📊 Service status ($(ENV)):$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile ps

status: ps

# ============================================
# Shell Access
# ============================================
exec-web:
	@echo "$(CYAN)🐳 Opening shell in web container ($(ENV))...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile exec-web

exec-db:
	@echo "$(CYAN)🐳 Opening shell in database container ($(ENV))...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile exec-db

exec-gitea:
	@echo "$(CYAN)🐳 Opening shell in Gitea container ($(ENV))...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile exec-gitea 2>/dev/null || echo "$(YELLOW)Gitea not available in $(ENV)$(NC)"

list-envs:
	@echo "$(CYAN)🔍 Listing environment variables ($(ENV))...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile list-envs

# ============================================
# Dev-Only Commands
# ============================================
gitea-token:
ifeq ($(ENV),dev)
	@echo "$(CYAN)🔑 Setting up Gitea token (dev)...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile gitea-token
else
	@echo "$(YELLOW)❌ gitea-token only available in dev environment$(NC)"
	@exit 1
endif

recreate-testuser:
ifeq ($(ENV),dev)
	@echo "$(CYAN)👤 Recreating test user (dev)...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile recreate-testuser
else
	@echo "$(YELLOW)❌ recreate-testuser only available in dev environment$(NC)"
	@exit 1
endif

verify-gitea:
ifeq ($(ENV),dev)
	@echo "$(CYAN)🔍 Verifying Gitea (dev)...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile verify-gitea
else
	@echo "$(YELLOW)❌ verify-gitea only available in dev environment$(NC)"
	@exit 1
endif

# ============================================
# Prod/NAS-Only Commands
# ============================================
verify-health:
ifneq ($(ENV),dev)
	@echo "$(CYAN)🔍 Checking health ($(ENV))...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile verify-health
else
	@echo "$(YELLOW)❌ verify-health only available in prod/nas$(NC)"
	@exit 1
endif

ssl-setup:
ifeq ($(ENV),prod)
	@echo "$(CYAN)🔒 Setting up SSL/HTTPS for production...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) ssl-setup
else
	@echo "$(YELLOW)❌ ssl-setup only available in prod environment$(NC)"
	@exit 1
endif

ssl-verify:
ifeq ($(ENV),prod)
	cd $(DOCKER_DIR) && $(MAKE) ssl-verify
else
	@echo "$(YELLOW)❌ ssl-verify only available in prod environment$(NC)"
	@exit 1
endif

ssl-check:
ifeq ($(ENV),prod)
	cd $(DOCKER_DIR) && $(MAKE) ssl-check
else
	@echo "$(YELLOW)❌ ssl-check only available in prod environment$(NC)"
	@exit 1
endif

ssl-renew:
ifeq ($(ENV),prod)
	cd $(DOCKER_DIR) && $(MAKE) ssl-renew
else
	@echo "$(YELLOW)❌ ssl-renew only available in prod environment$(NC)"
	@exit 1
endif

# ============================================
# Development Workflow Shortcuts
# ============================================
setup:
	@echo "$(CYAN)🔧 Setting up $(ENV) environment...$(NC)"
	cd $(DOCKER_DIR) && $(MAKE) -f Makefile setup

dev-cycle: ENV=dev
dev-cycle:
	@$(MAKE) ENV=dev start migrate collectstatic
	@echo "$(GREEN)✅ Development environment ready at http://localhost:8000$(NC)"

prod-deploy: ENV=prod
prod-deploy:
	@$(MAKE) ENV=prod setup
	@echo "$(GREEN)✅ Production deployed$(NC)"

# ============================================
# Info
# ============================================
info:
	@echo "Current environment: $(ENV)"
	@echo "Container directory: $(DOCKER_DIR)"
	@echo "Compose file: $(COMPOSE_FILE)"
	@echo "Makefile: $(MAKEFILE)"

# EOF
