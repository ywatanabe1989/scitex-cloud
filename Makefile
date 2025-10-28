# SciTeX Cloud - Development Commands
# DOCKER-AWARE: Automatically runs Django commands inside Docker containers
.PHONY: help setup build restart logs django-migrate django-makemigrations django-shell django-createsuperuser django-collectstatic test clean rebuild docker-exec db-shell db-reset

.DEFAULT_GOAL := help

# Detect if Docker is running and containers are active
DOCKER_RUNNING := $(shell docker ps -q 2>/dev/null | grep -q . && echo 1 || echo 0)
DOCKER_COMPOSE_DIR := containers/docker

help:
	@echo "╔═══════════════════════════════════════════════════════╗"
	@echo "║         SciTeX Cloud - Development Commands           ║"
	@echo "╚═══════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🚀 Setup & Build:"
	@echo "  make setup              - Initial setup (build + django-migrate + django-collectstatic)"
	@echo "  make build              - Start development environment"
	@echo "  make restart            - Restart services"
	@echo "  make rebuild            - Clean rebuild (stops and starts everything)"
	@echo ""
	@echo "🐍 Django Management:"
	@echo "  make django-migrate            - Run database migrations"
	@echo "  make django-makemigrations     - Create new migrations"
	@echo "  make django-shell              - Open Django shell"
	@echo "  make django-createsuperuser    - Create superuser account"
	@echo "  make django-collectstatic      - Collect static files"
	@echo ""
	@echo "🗄️  Database:"
	@echo "  make db-shell           - PostgreSQL shell (inside Docker)"
	@echo "  make db-reset           - Reset database (⚠️  DELETES ALL DATA)"
	@echo ""
	@echo "🧪 Testing & Maintenance:"
	@echo "  make test               - Run test suite"
	@echo "  make clean              - Clean Python cache files"
	@echo "  make logs               - View application logs"
	@echo ""
	@echo "Note: Django commands automatically run inside Docker containers."
	@echo "      Make sure 'make build' or './start_dev.sh -a start' has been run first."
	@echo ""

# ═══════════════════════════════════════════════════════════════
# 🚀 Setup & Build Commands
# ═══════════════════════════════════════════════════════════════

setup: build django-migrate django-collectstatic
	@echo "✅ Setup complete!"

build:
	bash ./containers/docker/start_dev.sh -a start

restart:
	bash ./containers/docker/start_dev.sh -a restart

rebuild: clean build django-migrate django-collectstatic
	@echo "✅ Rebuild complete!"

# ═══════════════════════════════════════════════════════════════
# 🐍 Django Management Commands (run inside Docker)
# ═══════════════════════════════════════════════════════════════

# Helper target to verify Docker containers are running
docker-check-health:
	@if ! docker ps | grep -q docker-web-1; then \
		echo "❌ Web container (docker-web-1) is not running!"; \
		echo "Run 'make build' or './containers/docker/start_dev.sh -a start' first."; \
		exit 1; \
	fi

django-migrate: docker-check-health
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.dev.yml exec -T web python manage.py migrate
	@echo "✅ Migrations applied successfully"

django-makemigrations: docker-check-health
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.dev.yml exec -T web python manage.py makemigrations
	@echo "✅ Migrations created successfully"

django-shell: docker-check-health
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.dev.yml exec web python manage.py shell

django-createsuperuser: docker-check-health
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.dev.yml exec web python manage.py createsuperuser

django-collectstatic: docker-check-health
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.dev.yml exec -T web python manage.py collectstatic --noinput
	@echo "✅ Static files collected"

# ═══════════════════════════════════════════════════════════════
# 🗄️  Database Commands (run inside Docker)
# ═══════════════════════════════════════════════════════════════

db-shell: docker-check-health
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.dev.yml exec db psql -U $$POSTGRES_USER -d $$POSTGRES_DB

db-reset: docker-check-health
	@echo "⚠️  WARNING: This will DELETE ALL DATA in the database!"
	@read -p "Are you absolutely sure? Type 'yes' to confirm: " confirm && \
	[ "$$confirm" = "yes" ] && \
	(echo "Resetting database..." && \
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.dev.yml exec -T web python manage.py migrate zero && \
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.dev.yml exec -T web python manage.py migrate && \
	echo "✅ Database reset complete") || \
	echo "❌ Database reset cancelled"

# ═══════════════════════════════════════════════════════════════
# 🧪 Testing & Maintenance
# ═══════════════════════════════════════════════════════════════

test: docker-check-health
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.dev.yml exec -T web python manage.py test
	@echo "✅ Tests completed"

logs:
	@echo "📋 Docker Compose Logs:"
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.dev.yml logs -f

logs-web:
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.dev.yml logs -f web

logs-db:
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.dev.yml logs -f db

logs-gitea:
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.dev.yml logs -f gitea

clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"
