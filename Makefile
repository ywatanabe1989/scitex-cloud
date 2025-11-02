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

.PHONY: help status validate-state validate-docker validate switch stop-all start restart stop down logs ps migrate shell clean-state force-stop-all set-active-env clear-active-env ssl-setup ssl-verify ssl-check ssl-renew verify-health list-envs exec-web exec-db exec-gitea gitea-token recreate-testuser build-ts collectstatic
.DEFAULT_GOAL := help

# ============================================
# Configuration
# ============================================
STATE_FILE := deployment/.active-env
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
    ifneq ($(filter-out help status validate-state validate-docker clean-state stop-all force-stop-all set-active-env clear-active-env,$(MAKECMDGOALS)),)
      $(error ❌ ENV not specified! Use: make ENV=<dev|prod|nas> <command>)
    endif
  endif
endif

# ============================================
# Docker Reality Detection
# ============================================
# Detect which environments are actually running in Docker
get-running-envs = $(shell docker ps --format '{{.Names}}' 2>/dev/null | grep -oE 'scitex-cloud-(dev|prod|nas)-' | sed 's/scitex-cloud-//' | sed 's/-//' | sort -u)

# Get active environment from state file
get-active-env = $(shell [ -f $(STATE_FILE) ] && cat $(STATE_FILE) || echo "none")

# ============================================
# State Management
# ============================================
# Set active environment
set-active-env:
	@mkdir -p deployment
	@echo "$(ENV)" > $(STATE_FILE)
	@echo "$(GREEN)✅ State file updated: $(ENV)$(NC)"

# Clear active environment
clear-active-env:
	@rm -f $(STATE_FILE)
	@echo "$(YELLOW)⚠️  State file cleared$(NC)"

# ============================================
# Validation Functions
# ============================================
validate-state:
	@echo "$(CYAN)🔍 Validating environment state...$(NC)"
	@ACTIVE=$$(cat $(STATE_FILE) 2>/dev/null || echo "none"); \
	RUNNING=$$(docker ps --format '{{.Names}}' 2>/dev/null | grep -oE 'scitex-cloud-(dev|prod|nas)-' | sed 's/scitex-cloud-//' | sed 's/-//' | sort -u | tr '\n' ' '); \
	echo "  State file: $$ACTIVE"; \
	echo "  Running containers: $$RUNNING"; \
	if [ "$$ACTIVE" = "none" ] && [ -n "$$RUNNING" ]; then \
		echo "$(RED)❌ CONFLICT: State says 'none' but containers are running: $$RUNNING$(NC)"; \
		echo "$(YELLOW)   Run 'make stop-all' to clean up$(NC)"; \
		exit 1; \
	fi; \
	for env in $$RUNNING; do \
		if [ "$$env" != "$$ACTIVE" ]; then \
			echo "$(RED)❌ CONFLICT: State says '$$ACTIVE' but '$$env' containers are running$(NC)"; \
			echo "$(YELLOW)   Run 'make stop-all' to clean up$(NC)"; \
			exit 1; \
		fi; \
	done; \
	echo "$(GREEN)✅ State is consistent$(NC)"

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

# Full validation (state + docker)
validate: validate-docker validate-state

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
	@echo "  make exec-web                     # Shell into web container"
	@echo "  make list-envs                    # List environment variables in container"
	@echo ""
	@echo "$(CYAN)🔒 SSL/HTTPS (prod only):$(NC)"
	@echo "  make ENV=prod ssl-verify          # Verify HTTPS is working"
	@echo "  make ENV=prod ssl-check           # Check certificate status"
	@echo "  make ENV=prod ssl-renew           # Renew certificates"
	@echo "  make ENV=prod ssl-setup           # Manual SSL setup (interactive)"
	@echo ""
	@echo "$(RED)⚠️  IMPORTANT: ENV parameter is MANDATORY!$(NC)"
	@echo "$(YELLOW)   No defaults - always specify ENV=<dev|prod|nas>$(NC)"
	@echo ""

# ============================================
# Status & Information
# ============================================
status:
	@echo "$(CYAN)📊 Environment Status:$(NC)"
	@echo ""
	@ACTIVE=$$(cat $(STATE_FILE) 2>/dev/null || echo "none"); \
	RUNNING=$$(docker ps --format '{{.Names}}' 2>/dev/null | grep -oE 'scitex-cloud-(dev|prod|nas)-' | sed 's/scitex-cloud-//' | sed 's/-//' | sort -u | tr '\n' ' ' | xargs); \
	echo "  $(CYAN)State file:$(NC) $$ACTIVE"; \
	if [ -n "$$RUNNING" ]; then \
		echo "  $(CYAN)Docker running:$(NC) $$RUNNING"; \
	else \
		echo "  $(CYAN)Docker running:$(NC) none"; \
	fi; \
	echo ""; \
	if [ "$$ACTIVE" != "none" ] && [ "$$ACTIVE" != "$$RUNNING" ]; then \
		echo "  $(RED)⚠️  MISMATCH DETECTED!$(NC)"; \
		echo "  $(YELLOW)Run 'make validate' for details$(NC)"; \
	elif [ "$$ACTIVE" = "none" ] && [ -z "$$RUNNING" ]; then \
		echo "  $(YELLOW)⚠️  No active environment$(NC)"; \
	else \
		echo "  $(GREEN)✅ State is consistent$(NC)"; \
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
	@$(MAKE) --no-print-directory clear-active-env
	@echo ""
	@echo "$(GREEN)✅ All environments stopped$(NC)"

force-stop-all:
	@echo "$(RED)⚠️  Force stopping all scitex-cloud containers...$(NC)"
	@docker ps -a --format "{{.Names}}" | grep -E "scitex-cloud-(dev|prod|nas)-" | xargs -r docker stop 2>/dev/null || true
	@docker ps -a --format "{{.Names}}" | grep -E "scitex-cloud-(dev|prod|nas)-" | xargs -r docker rm 2>/dev/null || true
	@$(MAKE) --no-print-directory clear-active-env
	@echo "$(GREEN)✅ All containers force-stopped$(NC)"

# ============================================
# Environment Switching
# ============================================
switch: validate stop-all
	@echo ""
	@echo "$(CYAN)🔄 Switching to $(ENV) environment...$(NC)"
	@$(MAKE) --no-print-directory ENV=$(ENV) set-active-env
	@$(MAKE) --no-print-directory ENV=$(ENV) start
	@echo ""
	@echo "$(GREEN)✅ Switched to $(ENV) environment$(NC)"

# ============================================
# Service Lifecycle with Validation
# ============================================
start: validate-docker
	@echo "$(CYAN)🚀 Starting $(ENV) environment...$(NC)"
	@echo ""
	@# Check state file
	@ACTIVE=$$(cat $(STATE_FILE) 2>/dev/null || echo "none"); \
	if [ "$$ACTIVE" != "none" ] && [ "$$ACTIVE" != "$(ENV)" ]; then \
		echo "$(YELLOW)⚠️  $$ACTIVE is marked as active in state file$(NC)"; \
		echo "$(YELLOW)   Stopping all environments first...$(NC)"; \
		$(MAKE) --no-print-directory stop-all; \
		echo ""; \
	fi
	@# Check running containers
	@RUNNING=$$(docker ps --format '{{.Names}}' 2>/dev/null | grep -oE 'scitex-cloud-(dev|prod|nas)-' | sed 's/scitex-cloud-//' | sed 's/-//' | sort -u); \
	if [ -n "$$RUNNING" ] && [ "$$RUNNING" != "$(ENV)" ]; then \
		echo "$(YELLOW)⚠️  $$RUNNING containers are running$(NC)"; \
		echo "$(YELLOW)   Stopping all environments first...$(NC)"; \
		$(MAKE) --no-print-directory stop-all; \
		echo ""; \
	fi
	@# Start the requested environment
	@echo "$(CYAN)Starting $(ENV) services...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile start
	@$(MAKE) --no-print-directory ENV=$(ENV) set-active-env
	@echo ""
	@echo "$(GREEN)✅ $(ENV) environment is now running$(NC)"
	@$(MAKE) --no-print-directory status

restart: validate
	@ACTIVE=$$(cat $(STATE_FILE) 2>/dev/null || echo "none"); \
	if [ "$$ACTIVE" != "$(ENV)" ]; then \
		echo "$(RED)❌ $(ENV) is not the active environment (active: $$ACTIVE)$(NC)"; \
		echo "$(YELLOW)   Use 'make ENV=$(ENV) switch' to switch environments$(NC)"; \
		exit 1; \
	fi
	@echo "$(CYAN)🔄 Restarting $(ENV) environment...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile restart
	@echo "$(GREEN)✅ $(ENV) restarted$(NC)"

stop: validate-docker
	@echo "$(YELLOW)⬇️  Stopping $(ENV) environment...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile down
	@ACTIVE=$$(cat $(STATE_FILE) 2>/dev/null || echo "none"); \
	if [ "$$ACTIVE" = "$(ENV)" ]; then \
		$(MAKE) --no-print-directory clear-active-env; \
	fi
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
	@$(MAKE) --no-print-directory ENV=$(ENV) set-active-env
	@echo ""
	@echo "$(GREEN)✅ $(ENV) rebuild complete$(NC)"
	@$(MAKE) --no-print-directory validate

setup:
	@echo "$(CYAN)🔧 Setting up $(ENV) environment...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile setup
	@$(MAKE) --no-print-directory ENV=$(ENV) set-active-env
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
	@echo "$(CYAN)🔍 Listing environment variables ($(ENV))...$(NC)"
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile list-envs

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
clean-state:
	@echo "$(YELLOW)🧹 Cleaning state file...$(NC)"
	@rm -f $(STATE_FILE)
	@echo "$(GREEN)✅ State cleaned$(NC)"

clean-python:
	@cd $(DOCKER_DIR) && $(MAKE) -f Makefile clean-python

# ============================================
# Info
# ============================================
info:
	@echo "Specified environment: $(ENV)"
	@echo "Active environment: $$(cat $(STATE_FILE) 2>/dev/null || echo 'none')"
	@echo "Running environments: $$(docker ps --format '{{.Names}}' 2>/dev/null | grep -oE 'scitex-cloud-(dev|prod|nas)-' | sed 's/scitex-cloud-//' | sed 's/-//' | sort -u | tr '\n' ' ')"
	@echo "Container directory: $(DOCKER_DIR)"
	@echo "Makefile: $(MAKEFILE)"
	@echo "State file: $(STATE_FILE)"

# EOF
