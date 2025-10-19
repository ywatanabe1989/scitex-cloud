#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-16 00:35:58 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/config/settings/settings_prod.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./config/settings/settings_prod.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from .settings_shared import *  # Import shared settings

# Load environment variables from .env.production if it exists
try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(BASE_DIR, ".env.production"))
except ImportError:
    pass  # python-dotenv not installed, rely on system environment

"""
Production settings for SciTeX Cloud project.
"""

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Security - Use environment variable for production
SECRET_KEY = os.environ.get("SCITEX_DJANGO_SECRET_KEY")
if not SECRET_KEY:
    # Fallback secret key for development/testing purposes
    SECRET_KEY = "WlLHhph63BKuRP7W?Z3TszWTltaObIzC-fallback-production-key-change-in-real-deployment"

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

# Security settings for production - only enable SSL redirects if HTTPS is properly configured
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_PRELOAD = True  # Enable HSTS preload for enhanced security
SECURE_REDIRECT_EXEMPT = []
# Only enable SSL redirect if explicitly configured
SECURE_SSL_REDIRECT = (
    os.environ.get("ENABLE_SSL_REDIRECT", "false").lower() == "true"
)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# Additional security headers
X_FRAME_OPTIONS = "DENY"  # Prevent clickjacking
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Cookie security settings
# Temporarily allow HTTP for testing - should be True in production with HTTPS
SESSION_COOKIE_SECURE = (
    os.environ.get("FORCE_HTTPS_COOKIES", "false").lower() == "true"
)
CSRF_COOKIE_SECURE = (
    os.environ.get("FORCE_HTTPS_COOKIES", "false").lower() == "true"
)
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookies
CSRF_COOKIE_HTTPONLY = True  # Prevent JavaScript access to CSRF cookies

# Production database - PostgreSQL (recommended) with SQLite fallback
# Use SQLite: export SCITEX_CLOUD_USE_SQLITE_PROD=1
if os.environ.get('SCITEX_CLOUD_USE_SQLITE_PROD'):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "data" / "db" / "sqlite" / "scitex_cloud_prod.db",
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
                "NAME": os.environ.get("SCITEX_CLOUD_DB_NAME_PROD", "scitex_cloud_prod"),
                "USER": os.environ.get("SCITEX_CLOUD_DB_USER_PROD", "scitex_prod"),
                "PASSWORD": DB_PASSWORD,
                "HOST": os.environ.get("SCITEX_CLOUD_DB_HOST_PROD", "localhost"),
                "PORT": os.environ.get("SCITEX_CLOUD_DB_PORT_PROD", "5432"),
                "ATOMIC_REQUESTS": True,
                "CONN_MAX_AGE": 600,
                "OPTIONS": {
                    "connect_timeout": 10,
                    "options": "-c statement_timeout=30000",  # 30 second query timeout
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

# Production static files
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Email configuration for production
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "mail1030.onamae.ne.jp"
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_HOST_USER = os.environ.get("SCITEX_EMAIL_ADMIN", "admin@scitex.ai")
EMAIL_HOST_PASSWORD = os.environ.get(
    "SCITEX_EMAIL_PASSWORD", "WlLHhph63BKuRP7W?Z3TszWTltaObIzC"
)
DEFAULT_FROM_EMAIL = os.environ.get("SCITEX_EMAIL_ADMIN", "admin@scitex.ai")
SERVER_EMAIL = os.environ.get("SCITEX_EMAIL_ADMIN", "admin@scitex.ai")

# Admin emails for error notifications
ADMINS = [
    ("Admin", "admin@scitex.ai"),
    ("Yusuke Watanabe", "ywatanabe@scitex.ai"),
]

# ----------------------------------------
# Gitea Configuration (Production)
# ----------------------------------------
GITEA_URL = os.environ.get('SCITEX_CLOUD_GITEA_URL', 'https://git.scitex.ai')
GITEA_API_URL = os.environ.get('SCITEX_CLOUD_GITEA_API_URL', 'https://git.scitex.ai/api/v1')
GITEA_TOKEN = os.environ.get('SCITEX_CLOUD_GITEA_TOKEN', '')

# Production logging - extends the base logging config

# Define log directory for production
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Ensure log directory exists - in production this should be handled by deployment
# but we'll add this safety check that will try to create it with proper permissions
try:
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, mode=0o755)
except:
    # In production we might not have permissions to create this
    # so we'll let it fail silently and rely on deployment scripts
    pass

# Update the LOGGING configuration from the base settings with production-specific settings
# Production logs are more robust with larger file sizes and more backups
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
                "maxBytes": 1024 * 1024 * 10,  # 10 MB
                "backupCount": 10,
                "formatter": "verbose",
            },
            "file_django": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_DIR, "django.log"),
                "maxBytes": 1024 * 1024 * 10,  # 10 MB
                "backupCount": 10,
                "formatter": "verbose",
            },
            "file_error": {
                "level": "ERROR",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_DIR, "error.log"),
                "maxBytes": 1024 * 1024 * 10,  # 10 MB
                "backupCount": 10,
                "formatter": "verbose",
            },
            "file_security": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_DIR, "security.log"),
                "maxBytes": 1024 * 1024 * 10,  # 10 MB
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
