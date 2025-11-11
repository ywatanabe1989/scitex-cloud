#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-10 15:46:56 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/config/settings/settings_dev.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./config/settings/settings_dev.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Development settings for SciTeX Cloud project.
"""

from scitex.context import quiet
from .settings_shared import *
from dotenv import load_dotenv
import socket


# ---------------------------------------
# Functions
# ---------------------------------------
def test_redis_connection():
    """Test if Redis is available"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("127.0.0.1", 6379))
        sock.close()
        return result == 0
    except:
        return False


# ---------------------------------------
# Env
# ---------------------------------------
try:
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except Exception as e:
    print(e)

# ---------------------------------------
# Security (Development)
# ---------------------------------------
# Allow same-site iframes (needed for PDF viewer in writer app)
X_FRAME_OPTIONS = "SAMEORIGIN"

# ---------------------------------------
# Security
# ---------------------------------------
DEBUG = os.getenv("SCITEX_CLOUD_DJANGO_DEBUG", "True").lower() in [
    "true",
    "1",
    "yes",
]

# ---------------------------------------
# SciTeX Settings
# ---------------------------------------
# Use develp for writer template in development
SCITEX_WRITER_TEMPLATE_BRANCH = os.getenv(
    "SCITEX_WRITER_TEMPLATE_BRANCH", "develop"
)
SCITEX_WRITER_TEMPLATE_TAG = os.getenv("SCITEX_WRITER_TEMPLATE_TAG", None)
SECRET_KEY = os.getenv("SCITEX_CLOUD_DJANGO_SECRET_KEY")
ALLOWED_HOSTS = os.getenv(
    "SCITEX_CLOUD_ALLOWED_HOSTS",
    "localhost,127.0.0.1,0.0.0.0,172.19.33.56,[::1],testserver",
).split(",")


# Hot reload settings
INTERNAL_IPS = [
    "127.0.0.1",
]

# ---------------------------------------
# Applications
# ---------------------------------------
DEVELOPMENT_APPS = [
    "django_browser_reload",
    "django_extensions",
]

INSTALLED_APPS += DEVELOPMENT_APPS
MIDDLEWARE += [
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]


# ---------------------------------------
# Database - Fallback
# ---------------------------------------
# Use SQLite: export SCITEX_CLOUD_USE_SQLITE_DEV=1
if os.environ.get("SCITEX_CLOUD_USE_SQLITE_DEV"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR
            / "data"
            / "db"
            / "sqlite"
            / "scitex_cloud_dev.db",
        }
    }
else:
    # PostgreSQL (default for development)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get(
                "SCITEX_CLOUD_DB_NAME_DEV", "scitex_cloud_dev"
            ),
            "USER": os.environ.get("SCITEX_CLOUD_DB_USER_DEV", "scitex_dev"),
            "PASSWORD": os.environ.get(
                "SCITEX_CLOUD_DB_PASSWORD_DEV", "scitex_dev_2025"
            ),
            "HOST": os.environ.get("SCITEX_CLOUD_DB_HOST_DEV", "localhost"),
            "PORT": os.environ.get("SCITEX_CLOUD_DB_PORT_DEV", "5432"),
            "ATOMIC_REQUESTS": True,  # Wrap each request in a transaction
            "CONN_MAX_AGE": 600,  # Connection pooling (10 minutes)
            "OPTIONS": {
                "connect_timeout": 10,
            },
        }
    }

# ---------------------------------------
# Integration
# ---------------------------------------
# Gitea
# Use container URL for Django (http://gitea:3000) for inter-container communication
GITEA_URL = os.environ.get(
    "SCITEX_CLOUD_GITEA_URL_IN_CONTAINER_DEV", "http://gitea:3000"
)
GITEA_API_URL = f"{GITEA_URL}/api/v1"
GITEA_TOKEN = os.environ.get("SCITEX_CLOUD_GITEA_TOKEN_DEV", "")
GITEA_INTEGRATION_ENABLED = True  # Core feature, always enabled

# Development Cache Configuration - fallback to dummy cache if Redis not available
# Override cache configuration for development if Redis is not available
if not test_redis_connection():
    print("⚠️  Redis not available in development, using local memory cache")
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "scitex-cloud-dev",
            "TIMEOUT": 3600,
            "OPTIONS": {"MAX_ENTRIES": 1000},
        }
    }
    # Use database sessions if Redis is not available
    SESSION_ENGINE = "django.contrib.sessions.backends.db"

# ---------------------------------------
# Logging
# ---------------------------------------
LOGGING.update(
    {
        "handlers": {
            # Keep existing handlers from base settings
            **LOGGING.get("handlers", {}),
            # Add development-specific handlers
            "file_app": {
                "level": "DEBUG",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": LOG_DIR / "app.log",
                "maxBytes": 1024 * 1024 * 5,  # 5 MB
                "backupCount": 5,
                "formatter": "standard",
            },
            "file_django": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": LOG_DIR / "django.log",
                "maxBytes": 1024 * 1024 * 5,  # 5 MB
                "backupCount": 5,
                "formatter": "standard",
            },
            "file_requests": {
                "level": "DEBUG",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": LOG_DIR / "requests.log",
                "maxBytes": 1024 * 1024 * 5,  # 5 MB
                "backupCount": 5,
                "formatter": "standard",
            },
            "console_debug": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "standard",
            },
        },
        "loggers": {
            # Update existing loggers from base settings
            **LOGGING.get("loggers", {}),
            # Add development-specific loggers
            "django": {
                "handlers": ["console", "file_django"],
                "level": "INFO",
                "propagate": True,
            },
            "django.request": {
                "handlers": ["file_requests"],
                "level": "ERROR",  # Only log errors, not 404s for __reload__
                "propagate": True,
            },
            "django.server": {
                "handlers": ["file_django"],
                "level": "ERROR",  # Suppress __reload__ 404 warnings
                "propagate": False,
            },
            "django.db.backends": {
                "handlers": ["console_debug"],
                "level": "DEBUG" if os.environ.get("SQL_DEBUG") else "INFO",
                "propagate": False,
            },
            "scitex": {
                "handlers": ["console_debug", "file_app"],
                "level": "DEBUG",
                "propagate": True,
            },
        },
    }
)

# EOF
