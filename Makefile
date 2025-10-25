# SciTeX Cloud - Docker Commands
.PHONY: help build up down restart logs shell migrate collectstatic createsuperuser test clean

DOCKER_DIR = containers/docker
COMPOSE = docker-compose -f $(DOCKER_DIR)/docker-compose.yml
COMPOSE_PROD = docker-compose -f $(DOCKER_DIR)/docker-compose.prod.yml

help:
	@echo "SciTeX Cloud - Docker Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          - Initial setup (build + migrate + collectstatic)"
	@echo ""
	@echo "Development:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View logs (all services)"
	@echo "  make logs-web       - View web logs only"
	@echo ""
	@echo "Django:"
	@echo "  make shell          - Django shell"
	@echo "  make migrate        - Run migrations"
	@echo "  make makemigrations - Create migrations"
	@echo "  make collectstatic  - Collect static files"
	@echo "  make createsuperuser - Create superuser"
	@echo ""
	@echo "Database:"
	@echo "  make dbshell        - PostgreSQL shell"
	@echo "  make dbreset        - Reset database (WARNING: deletes data)"
	@echo ""
	@echo "Maintenance:"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean volumes and containers"
	@echo "  make rebuild        - Clean build and restart"

# Initial setup
setup: build up migrate collectstatic
	@echo "✅ Setup complete! Access at http://localhost:8000"
	@echo "Create superuser: make createsuperuser"

# Build
build:
	$(COMPOSE) build

# Start
up:
	$(COMPOSE) up -d
	@echo "Services started. Logs: make logs"

# Stop
down:
	$(COMPOSE) down

# Restart
restart:
	$(COMPOSE) restart

# Logs
logs:
	$(COMPOSE) logs -f

logs-web:
	$(COMPOSE) logs -f web

# Django shell
shell:
	$(COMPOSE) exec web python manage.py shell

# Migrations
migrate:
	$(COMPOSE) exec web python manage.py migrate

makemigrations:
	$(COMPOSE) exec web python manage.py makemigrations

# Static files
collectstatic:
	$(COMPOSE) exec web python manage.py collectstatic --noinput

# Create superuser
createsuperuser:
	$(COMPOSE) exec web python manage.py createsuperuser

# Database shell
dbshell:
	$(COMPOSE) exec db psql -U scitex -d scitex_cloud

# Reset database (WARNING: destructive)
dbreset:
	@echo "⚠️  WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(COMPOSE) down -v; \
		$(COMPOSE) up -d db; \
		sleep 5; \
		$(COMPOSE) exec web python manage.py migrate; \
		echo "✅ Database reset complete"; \
	fi

# Testing
test:
	$(COMPOSE) exec web python manage.py test

# Clean up
clean:
	$(COMPOSE) down -v
	docker system prune -f

# Rebuild from scratch
rebuild: clean build up migrate collectstatic
	@echo "✅ Rebuild complete!"
