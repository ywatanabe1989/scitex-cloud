#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-22 08:22:46 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/config/settings/settings_prod.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./config/settings/settings_prod.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Production settings for SciTeX Cloud project.
"""

from .settings_shared import *
from dotenv import load_dotenv
from scitex import logging
logger = logging.getLogger(__name__)

# ---------------------------------------
# Env
# ---------------------------------------
try:
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except Exception as e:
    logger.error(e)

# ---------------------------------------
# Security
# ---------------------------------------
DEBUG = False

SECRET_KEY = os.environ.get("SCITEX_DJANGO_SECRET_KEY")

ALLOWED_HOSTS = [
    "scitex.ai",
    "www.scitex.ai",
    "sciwriter.app",
    "www.sciwriter.app",
    "162.43.35.139",
    "localhost",
    "scitex",
    "airight.app",
]

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_PRELOAD = True
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = (
    os.environ.get("ENABLE_SSL_REDIRECT", "false").lower() == "true"
)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# ---------------------------------------
# Cookie
# ---------------------------------------
SESSION_COOKIE_SECURE = (
    os.environ.get("FORCE_HTTPS_COOKIES", "false").lower() == "true"
)
CSRF_COOKIE_SECURE = (
    os.environ.get("FORCE_HTTPS_COOKIES", "false").lower() == "true"
)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# ---------------------------------------
# Database
# ---------------------------------------
if os.environ.get("SCITEX_CLOUD_USE_SQLITE_PROD"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR
            / "data"
            / "db"
            / "sqlite"
            / "scitex_cloud_prod.db",
        }
    }
else:
    # PostgreSQL (default for production)
    DB_PASSWORD = os.environ.get("SCITEX_CLOUD_DB_PASSWORD_PROD")

    if DB_PASSWORD and DB_PASSWORD != "your_database_password_here":
        # Remote PostgreSQL (for production deployment)
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": os.environ.get(
                    "SCITEX_CLOUD_DB_NAME_PROD", "scitex_cloud_prod"
                ),
                "USER": os.environ.get(
                    "SCITEX_CLOUD_DB_USER_PROD", "scitex_prod"
                ),
                "PASSWORD": DB_PASSWORD,
                "HOST": os.environ.get(
                    "SCITEX_CLOUD_DB_HOST_PROD", "localhost"
                ),
                "PORT": os.environ.get("SCITEX_CLOUD_DB_PORT_PROD", "5432"),
                "ATOMIC_REQUESTS": True,
                "CONN_MAX_AGE": 600,
                "OPTIONS": {
                    "connect_timeout": 10,
                    "options": "-c statement_timeout=30000",
                },
            }
        }
    else:
        # Local PostgreSQL for production testing (default credentials)
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": "scitex_cloud_prod",
                "USER": "scitex_prod",
                "PASSWORD": "CHANGE_THIS_IN_PRODUCTION",
                "HOST": "localhost",
                "PORT": "5432",
                "ATOMIC_REQUESTS": True,
                "CONN_MAX_AGE": 600,
            }
        }

# ---------------------------------------
# Email
# ---------------------------------------
ADMINS = [
    ("Admin", "admin@scitex.ai"),
    ("Yusuke Watanabe", "ywatanabe@scitex.ai"),
]

# ---------------------------------------
# Integration
# ---------------------------------------
# Gitea - Always enabled (core feature)
GITEA_URL = os.environ.get("SCITEX_CLOUD_GITEA_URL", "https://git.scitex.ai")
GITEA_API_URL = os.environ.get(
    "SCITEX_CLOUD_GITEA_API_URL", "https://git.scitex.ai/api/v1"
)
GITEA_TOKEN = os.environ.get("SCITEX_CLOUD_GITEA_TOKEN", "")
GITEA_INTEGRATION_ENABLED = True  # Core feature, always enabled

# ---------------------------------------
# Logging
# ---------------------------------------
LOGGING.update(
    {
        "handlers": {
            # Keep existing handlers from base settings
            **LOGGING.get("handlers", {}),
            # Add production-specific handlers
            "file_app": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_DIR, "app.log"),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 10,
                "formatter": "verbose",
            },
            "file_django": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_DIR, "django.log"),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 10,
                "formatter": "verbose",
            },
            "file_error": {
                "level": "ERROR",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_DIR, "error.log"),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 10,
                "formatter": "verbose",
            },
            "file_security": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_DIR, "security.log"),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 10,
                "formatter": "verbose",
            },
        },
        "loggers": {
            # Update existing loggers
            "django": {
                "handlers": ["file_django", "mail_admins"],
                "level": "INFO",
                "propagate": False,
            },
            "django.request": {
                "handlers": ["file_error", "mail_admins"],
                "level": "ERROR",
                "propagate": False,
            },
            "django.security": {
                "handlers": ["file_security", "mail_admins"],
                "level": "INFO",
                "propagate": False,
            },
            "scitex": {
                "handlers": ["file_app", "file_error"],
                "level": "INFO",
                "propagate": False,
            },
        },
        # Root logger catches everything else
        "root": {
            "handlers": ["file_error"],
            "level": "ERROR",
        },
    }
)

# EOF
