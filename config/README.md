# SciTeX Cloud Configuration

This directory contains all Django configuration files organized for easy environment management.

## Directory Structure

```
config/
├── settings/              # Django settings (organized by environment)
│   ├── __init__.py       # Auto-detects environment
│   ├── base.py           # Shared settings for all environments
│   ├── development.py    # Development-specific settings
│   └── production.py     # Production-specific settings
├── deployment/            # Deployment configurations
│   ├── uwsgi/            # uWSGI configs
│   │   ├── uwsgi.ini
│   │   ├── uwsgi_prod.ini
│   │   └── uwsgi_simple.ini
│   └── nginx/            # Nginx configs
│       └── *.conf
├── asgi.py               # ASGI application
├── wsgi.py               # WSGI application
├── urls.py               # URL configuration
├── routing.py            # WebSocket routing
└── logger.py             # Logging configuration
```

## Environment Switching

### Method 1: Environment Variable (Recommended)

```bash
# Development (default)
export SCITEX_CLOUD_ENV=development
python manage.py runserver

# Production
export SCITEX_CLOUD_ENV=production
gunicorn config.wsgi:application
```

### Method 2: Django Settings Module

```bash
# Development
export DJANGO_SETTINGS_MODULE=config.settings.development

# Production
export DJANGO_SETTINGS_MODULE=config.settings.production
```

## Quick Start

### Development

```bash
# Default - automatically uses development settings
./scripts/scitex_server.sh start

# Or explicitly
./scripts/scitex_server.sh start -m dev
```

### Production

```bash
# Set environment
export SCITEX_CLOUD_ENV=production

# Start production server
./scripts/scitex_server.sh start -m prod -d
```

## Settings Files

### `base.py`
- Shared settings for all environments
- Database configuration
- Installed apps
- Middleware
- Static/media files base configuration

### `development.py`
- Inherits from `base.py`
- DEBUG=True
- Development database (SQLite)
- Django debug toolbar
- Hot reload enabled
- Console email backend

### `production.py`
- Inherits from `base.py`
- DEBUG=False
- Production database
- Security settings
- SMTP email backend
- Logging configuration

## Auto-Detection Logic

The `settings/__init__.py` automatically loads the appropriate settings based on:

1. `SCITEX_CLOUD_ENV` environment variable (recommended)
2. Falls back to development if not set

## Migration from Old Structure

Previously used files (now archived):
- `config/settings.py` → Archived
- `config/django_settings.py` → Archived

These have been replaced by the organized `config/settings/` directory structure.

## See Also

- `/scripts/` - Server management scripts organized by environment
- `/scripts/dev/` - Development scripts
- `/scripts/prod/` - Production deployment scripts
