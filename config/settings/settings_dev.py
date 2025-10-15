#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-21 10:05:45 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Cloud/config/settings/development.py
# ----------------------------------------
import os
__FILE__ = (
    "./config/settings/development.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""
Development settings for SciTeX Cloud project.
"""

from .settings_shared import *
# LOGGING is now imported from settings_shared.py

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Development SECRET_KEY fallback (override from base.py)
if not SECRET_KEY:
    SECRET_KEY = "django-insecure-dev-key-for-testing-only-do-not-use-in-production"

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "172.19.33.56", "[::1]", "testserver"]

# Development-specific apps
DEVELOPMENT_APPS = [
    "django_browser_reload",
    "django_extensions",
]

INSTALLED_APPS += DEVELOPMENT_APPS

# Development middleware
MIDDLEWARE += [
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

# Hot reload settings
INTERNAL_IPS = [
    "127.0.0.1",
]

# Development database (SQLite)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "scitex_cloud_dev.db",
    }
}

# Development Cache Configuration - fallback to dummy cache if Redis not available
import socket

def test_redis_connection():
    """Test if Redis is available"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 6379))
        sock.close()
        return result == 0
    except:
        return False

# Override cache configuration for development if Redis is not available
if not test_redis_connection():
    print("Redis not available in development, using local memory cache")
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'scitex-cloud-dev',
            'TIMEOUT': 3600,
            'OPTIONS': {
                'MAX_ENTRIES': 1000
            }
        }
    }
    # Use database sessions if Redis is not available
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Development static files - unified with production
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Email settings for development
# Inherit SMTP settings from base.py
# base.py uses Gmail SMTP with SCITEX_SENDER_GMAIL credentials
# No override needed - emails will be sent for real in development too

# Development logging - extends the base logging config
import os

# Create logs directory if it doesn't exist
LOG_DIR = BASE_DIR / 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Update the LOGGING configuration from the base settings with development-specific settings
LOGGING.update({
    'handlers': {
        # Keep existing handlers from base settings
        **LOGGING.get('handlers', {}),
        
        # Add development-specific handlers
        'file_app': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'app.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'file_django': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'django.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'file_requests': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'requests.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'console_debug': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        # Update existing loggers from base settings
        **LOGGING.get('loggers', {}),

        # Add development-specific loggers
        'django': {
            'handlers': ['console', 'file_django'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file_requests'],
            'level': 'ERROR',  # Only log errors, not 404s for __reload__
            'propagate': True,
        },
        'django.server': {
            'handlers': ['file_django'],
            'level': 'ERROR',  # Suppress __reload__ 404 warnings
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console_debug'],
            'level': 'DEBUG' if os.environ.get('SQL_DEBUG') else 'INFO',
            'propagate': False,
        },
        'scitex': {
            'handlers': ['console_debug', 'file_app'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
})

# EOF
