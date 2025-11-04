# ============================================
# SciTeX Cloud - Environment Orchestrator
# ============================================
# Exclusive environment management for dev/prod/nas
# Location: /Makefile
#
# Key Features:
# - Mutual exclusivity (only one environment runs at a time)
# - Mandatory environment specification (NO defaults!)
# - State file + Docker reality validation
# - Conflict detection and prevention
# - Safety confirmations for production
#
# Usage:
#   make status                    # Show active environment
#   make ENV=dev start             # Start dev (stops others first)
#   make ENV=prod switch           # Switch to prod
#   make ENV=prod rebuild          # Rebuild prod (with confirmation)

.PHONY: help status validate-docker validate switch stop-all start restart reload stop down logs ps migrate shell force-stop-all ssl-setup ssl-verify ssl-check ssl-renew verify-health list-envs exec-web exec-db exec-gitea gitea-token recreate-testuser build-ts collectstatic makemigrations createsuperuser db-shell db-backup db-reset logs-web logs-db logs-gitea build rebuild setup test clean-python info
.DEFAULT_GOAL := help

# ============================================
# Configuration
# ============================================
VALID_ENVS := dev prod nas

# Colors
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
CYAN := \033[0;36m
BLUE := \033[0;34m
NC := \033[0m

# ============================================
# Environment Validation - NO DEFAULTS!
# ============================================
# Accept both env= and ENV= (convert lowercase to uppercase)
ifdef env
  ENV := $(env)
endif

# Check if ENV is specified and valid
ifdef ENV
  ifeq ($(filter $(ENV),$(VALID_ENVS)),)
    $(error Invalid ENV='$(ENV)'. Must be one of: dev, prod, nas)
  endif
  DOCKER_DIR := deployment/docker/docker_$(ENV)
  MAKEFILE := $(DOCKER_DIR)/Makefile
else
  # ENV not specified - only allow non-operational commands
  ifneq ($(MAKECMDGOALS),)
    ifneq ($(filter-out help status validate-docker stop-all force-stop-all,$(MAKECMDGOALS)),)
      $(error ❌ ENV not specified! Use: make ENV=<dev|prod|nas> <command>)
    endif
  endif
endif

# ============================================
# Docker Reality Detection
# ============================================
# Detect which environments are actually running in Docker
get-running-envs = $(shell docker ps --format '{{.Names}}' 2>/dev/null | grep -oE 'scitex-cloud-(dev|prod|nas)-' | sed 's/scitex-cloud-//' | sed 's/-//' | sort -u)

# ============================================
# Validation Functions
# ============================================
validate-docker:
	@echo "$(CYAN)🔍 Checking for container conflicts...$(NC)"
	@RUNNING=$$(docker ps --format '{{.Names}}' 2>/dev/null | grep -oE 'scitex-cloud-(dev|prod|nas)-' | sed 's/scitex-cloud-//' | sed 's/-//' | sort -u); \
	COUNT=$$(echo "$$RUNNING" | wc -w); \
	if [ $$COUNT -gt 1 ]; then \
		echo "$(RED)❌ CONFLICT: Multiple environments running:$(NC)"; \
		for env in $$RUNNING; do \
			echo "  - $$env"; \
		done; \
		echo "$(YELLOW)   Run 'make stop-all' to clean up$(NC)"; \
		exit 1; \
	fi; \
	if [ $$COUNT -eq 0 ]; then \
		echo "$(GREEN)✅ No containers running$(NC)"; \
	else \
		echo "$(GREEN)✅ Only $$RUNNING is running$(NC)"; \
	fi

# Validation alias
validate: validate-docker

# ============================================
# Help
# ============================================
help:
	@echo ""
	@echo "$(GREEN)╔═══════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║      SciTeX Cloud - Environment Orchestrator          ║$(NC)"
	@echo "$(GREEN)╚═══════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@$(MAKE) --no-print-directory status
	@echo ""
	@echo "$(CYAN)📋 Core Commands:$(NC)"
	@echo "  make status                       # Show active environment"
	@echo "  make validate                     # Validate state consistency"
	@echo "  make ENV=<env> start              # Start environment (stops others)"
	@echo "  make ENV=<env> switch             # Switch environment cleanly"
	@echo "  make ENV=<env> stop               # Stop specific environment"
	@echo "  make stop-all                     # Stop all environments"
	@echo ""
	@echo "$(CYAN)🔧 Build & Deploy:$(NC)"
	@echo "  make ENV=<env> build              # Build images"
	@echo "  make ENV=<env> rebuild            # Rebuild (stops, builds, starts)"
	@echo "  make ENV=<env> setup              # Full setup (build + migrate)"
	@echo ""
	@echo "$(CYAN)🐍 Django:$(NC)"
	@echo "  make ENV=<env> migrate            # Run migrations"
	@echo "  make ENV=<env> shell              # Django shell"
	@echo "  make ENV=<env> build-ts           # Compile TypeScript to JavaScript"
	@echo "  make ENV=<env> collectstatic      # Collect static files (auto-builds TS)"
	@echo ""
	@echo "$(CYAN)📊 Monitoring:$(NC)"
	@echo "  make ENV=<env> logs               # View logs"
	@echo "  make ENV=<env> ps                 # Container status"
	@echo ""
	@echo "$(CYAN)💡 Examples:$(NC)"
	@echo "  make status                       # Check what's running"
	@echo "  make ENV=dev start                # Start development"
	@echo "  make ENV=prod switch              # Switch to production"
	@echo "  make ENV=nas rebuild              # Rebuild NAS environment"
	@echo ""
	@echo "$(CYAN)🔧 Utilities:$(NC)"
	@echo "  make ENV=<env> exec-web           # Shell into web container"
	@echo "  make ENV=<env> exec-db            # Shell into database container"
	@echo "  make ENV=<env> list-envs          # List environment variables"
	@echo ""
	@echo "$(CYAN)🔒 SSL/HTTPS (prod only):$(NC)"
	@echo "  make ENV=prod ssl-verify          # Verify HTTPS is working"
	@echo "  make ENV=prod ssl-check           # Check certificate status"
	@echo "  make ENV=prod ssl-renew           # Renew certificates"
	@echo "  make ENV=prod ssl-setup           # Manual SSL setup (interactive)"
	@echo ""
	@echo "$(RED)⚠️  IMPORTANT: ENV parameter is MANDATORY!$(NC)"
	@echo "$(YELLOW)   No defaults - always specify ENV=<dev|prod|nas> (or env=)$(NC)"
	@echo ""

# ============================================
# Status & Information
# ============================================
status:
	@echo "$(CYAN)📊 Environment Status:$(NC)"
	@echo ""
	@RUNNING=$$(docker ps --format '{{.Names}}' 2>/dev/null | grep -oE 'scitex-cloud-(dev|prod|nas)-' | sed 's/scitex-cloud-//' | sed 's/-//' | sort -u | tr '\n' ' ' | xargs); \
	if [ -n "$$RUNNING" ]; then \
		echo "  $(CYAN)Active environment:$(NC) $$RUNNING"; \
	else \
		echo "  $(YELLOW)⚠️  No active environment$(NC)"; \
	fi
	@echo ""
	@echo "$(CYAN)🐳 Running Containers:$(NC)"
	@docker ps --format "table {{.Names}}\t{{.Status}}" 2>/dev/null | grep -E "scitex-cloud-(dev|prod|nas)-" || echo "  $(YELLOW)No scitex-cloud containers running$(NC)"
	@echo ""

# ============================================
# Stop All Environments
# ============================================
stop-all:
	@echo "$(YELLOW)⬇️  Stopping all environments...$(NC)"
	@echo ""
	@for env in $(VALID_ENVS); do \
		echo "$(CYAN)Checking $$env...$(NC)"; \
		cd deployment/docker/docker_$$env && \
		if docker compose ps -q 2>/dev/null | grep -q .; then \
			echo "  $(YELLOW)Stopping $$env containers...$(NC)"; \
			$(MAKE) -f Makefile down 2>/dev/null || docker compose down 2>/dev/null || true; \
		else \
			echo "  $(GREEN)✓ $$env already stopped$(NC)"; \
		fi; \
		cd ../../..; \
	done
	@echo ""
	@echo "$(GREEN)✅ All environments stopped$(NC)"

force-stop-all:
	@echo "$(RED)⚠️  Force stopping all scitex-cloud containers...$(NC)"
	@docker ps -a --format "{{.Names}}" | grep -E "scitex-cloud-(dev|prod|nas)-" | xargs -r docker stop 2>/dev/null || true
	@docker ps -a --format "{{.Names}}" | grep -E "scitex-cloud-(dev|prod|nas)-" | xargs -r docker rm 2>/dev/null || true
	@echo "$(GREEN)✅ All containers force-stopped$(NC)"

# ============================================
# Environment Switching
# ============================================
switch: validate stop-all
	@echo ""
	@echo "$(CYAN)🔄 Switching to $(ENV) environment...$(NC)"
	@$(MAKE) --no-print-directory ENV=$(ENV) start
	@echo ""
	@echo "$(GREEN)✅ Switched to $(ENV) environment$(NC)"

# ============================================
# Service Lifecycle with Validation
# ============================================
start:
	@echo "$(CYAN)🚀 Starting $(ENV) environment (exclusive mode)...$(NC)"
	@echo ""
	@# Stop all other environments to ensure exclusivity
	@for env in $(VALID_ENVS); do \
		if [ "$$env" != "$(ENV)" ]; then \
			echo "$(CYAN)Checking $$env...$(NC)"; \
			cd deployment/docker/docker_$$env && \
			if docker compose ps -q 2>/dev/null | grep -q .; then \
				echo "  $(YELLOW)Stopping $$env containers...$(NC)"; \
				$(MAKE) -f Makefile down 2>/dev/null || docker compose down 2>/dev/null || true; \
			else \
				echo "  $(GREEN)✓ $$env already stopped$(NC)"; \
			fi; \
			cd ../../..; \
		fi; \
	done
	@echo ""
	@# Start the requested environment
	@echo "$(CYAN)Starting $(ENV) services...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile start || (echo "$(RED)❌ Start failed. Run 'make ENV=$(ENV) start' to retry$(NC)"; exit 1)
	@echo ""
	@echo "$(GREEN)✅ $(ENV) environment is now running$(NC)"
	@$(MAKE) --no-print-directory status

restart: validate
	@RUNNING=$$(docker ps --format '{{.Names}}' 2>/dev/null | grep -oE 'scitex-cloud-(dev|prod|nas)-' | sed 's/scitex-cloud-//' | sed 's/-//' | sort -u); \
	if [ "$$RUNNING" != "$(ENV)" ]; then \
		echo "$(RED)❌ $(ENV) is not running (active: $$RUNNING)$(NC)"; \
		echo "$(YELLOW)   Use 'make ENV=$(ENV) start' to start it$(NC)"; \
		exit 1; \
	fi
	@echo "$(CYAN)🔄 Restarting $(ENV) environment...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile restart
	@echo "$(GREEN)✅ $(ENV) restarted$(NC)"

reload: validate
	@RUNNING=$$(docker ps --format '{{.Names}}' 2>/dev/null | grep -oE 'scitex-cloud-(dev|prod|nas)-' | sed 's/scitex-cloud-//' | sed 's/-//' | sort -u); \
	if [ "$$RUNNING" != "$(ENV)" ]; then \
		echo "$(RED)❌ $(ENV) is not running (active: $$RUNNING)$(NC)"; \
		echo "$(YELLOW)   Use 'make ENV=$(ENV) start' to start it$(NC)"; \
		exit 1; \
	fi
	@echo "$(CYAN)⚡ Quick reload (no scitex reinstall)...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile reload
	@echo "$(GREEN)✅ $(ENV) reloaded$(NC)"

stop: validate-docker
	@echo "$(YELLOW)⬇️  Stopping $(ENV) environment...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile down
	@echo "$(GREEN)✅ $(ENV) stopped$(NC)"

down: stop

# ============================================
# Build Commands
# ============================================
build:
	@echo "$(CYAN)🏗️  Building $(ENV) images...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile build
	@echo "$(GREEN)✅ Build complete for $(ENV)$(NC)"

rebuild: validate-docker
	@# Production safety check
	@if [ "$(ENV)" = "prod" ]; then \
		echo ""; \
		echo "$(RED)⚠️  WARNING: Production rebuild!$(NC)"; \
		echo "$(YELLOW)   This will cause downtime.$(NC)"; \
		echo ""; \
		read -p "Type 'yes' to confirm: " confirm; \
		if [ "$$confirm" != "yes" ]; then \
			echo "$(YELLOW)❌ Rebuild cancelled$(NC)"; \
			exit 1; \
		fi; \
	fi
	@echo ""
	@echo "$(CYAN)🔄 Rebuilding $(ENV) environment...$(NC)"
	@echo "  1. Stopping $(ENV)..."
	@$(MAKE) --no-print-directory ENV=$(ENV) stop
	@echo "  2. Building images..."
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile build
	@echo "  3. Starting $(ENV)..."
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile up
	@echo ""
	@echo "$(GREEN)✅ $(ENV) rebuild complete$(NC)"
	@$(MAKE) --no-print-directory validate

setup:
	@echo "$(CYAN)🔧 Setting up $(ENV) environment...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile setup
	@echo "$(GREEN)✅ $(ENV) setup complete$(NC)"

# ============================================
# Django Commands
# ============================================
migrate: validate
	@echo "$(CYAN)🔄 Running migrations ($(ENV))...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile migrate

makemigrations: validate
	@echo "$(CYAN)📝 Creating migrations ($(ENV))...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile makemigrations

shell: validate
	@echo "$(CYAN)🐍 Opening Django shell ($(ENV))...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile shell

createsuperuser: validate
	@echo "$(CYAN)👤 Creating superuser ($(ENV))...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile createsuperuser

build-ts: validate
	@echo "$(CYAN)🔨 Building TypeScript ($(ENV))...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile build-ts

collectstatic: validate
	@echo "$(CYAN)📦 Collecting static files ($(ENV))...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile collectstatic

test: validate
	@echo "$(CYAN)🧪 Running tests ($(ENV))...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile test

# ============================================
# Database Commands
# ============================================
db-shell: validate
	@echo "$(CYAN)🗄️  Opening database shell ($(ENV))...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile db-shell

db-backup: validate
	@echo "$(CYAN)💾 Backing up database ($(ENV))...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile db-backup

db-reset: validate
	@if [ "$(ENV)" != "dev" ]; then \
		echo "$(RED)❌ db-reset only available in dev environment$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)⚠️  Resetting database (dev only)...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile db-reset

# ============================================
# Logs & Monitoring
# ============================================
logs: validate
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile logs

logs-web: validate
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile logs-web

logs-db: validate
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile logs-db

logs-gitea: validate
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile logs-gitea 2>/dev/null || echo "$(YELLOW)Gitea not available in $(ENV)$(NC)"

ps: validate
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile ps

# ============================================
# Shell Access
# ============================================
exec-web: validate
	@echo "$(CYAN)🐳 Opening shell in web container ($(ENV))...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile exec-web

exec-db: validate
	@echo "$(CYAN)🐳 Opening shell in database container ($(ENV))...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile exec-db

exec-gitea: validate
	@echo "$(CYAN)🐳 Opening shell in Gitea container ($(ENV))...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile exec-gitea 2>/dev/null || echo "$(YELLOW)Gitea not available in $(ENV)$(NC)"

list-envs: validate
	@echo "$(CYAN)🔍 Environment variables in $(ENV):$(NC)"
	@docker exec scitex-cloud-$(ENV)-web-1 env | sort

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

# ============================================
# Health Checks
# ============================================
verify-health: validate
	@if [ "$(ENV)" = "dev" ]; then \
		echo "$(YELLOW)❌ verify-health only available in prod/nas$(NC)"; \
		exit 1; \
	fi
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile verify-health

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
# Utilities
# ============================================
clean-python:
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile clean-python

# ============================================
# Info
# ============================================
info:
	@echo "Specified environment: $(ENV)"
	@echo "Running environments: $$(docker ps --format '{{.Names}}' 2>/dev/null | grep -oE 'scitex-cloud-(dev|prod|nas)-' | sed 's/scitex-cloud-//' | sed 's/-//' | sort -u | tr '\n' ' ')"
	@echo "Container directory: $(DOCKER_DIR)"
	@echo "Makefile: $(MAKEFILE)"

# EOF
