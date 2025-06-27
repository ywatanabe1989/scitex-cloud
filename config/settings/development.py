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

from .base import *
# LOGGING is now imported from base.py

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

# Development static files
STATICFILES_DIRS = [
    BASE_DIR / "static",
    BASE_DIR / "public" / "css",
    BASE_DIR / "public" / "js",
]

# Email settings for development
# Use console backend by default, but allow SMTP for testing with TEST_EMAIL_SMTP=true
if os.environ.get('TEST_EMAIL_SMTP', '').lower() == 'true':
    # Use real SMTP for testing
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'mail1030.onamae.ne.jp'
    EMAIL_PORT = 465
    EMAIL_USE_SSL = True
    EMAIL_USE_TLS = False
    EMAIL_HOST_USER = os.environ.get('SCITEX_EMAIL_ADMIN', 'admin@scitex.ai')
    EMAIL_HOST_PASSWORD = os.environ.get('SCITEX_EMAIL_PASSWORD', '')
    DEFAULT_FROM_EMAIL = os.environ.get('SCITEX_EMAIL_ADMIN', 'admin@scitex.ai')
    SERVER_EMAIL = os.environ.get('SCITEX_EMAIL_ADMIN', 'admin@scitex.ai')
else:
    # Use console backend for normal development
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'admin@scitex.ai'
    SERVER_EMAIL = 'admin@scitex.ai'

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
            'level': 'DEBUG',
            'propagate': True,
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
