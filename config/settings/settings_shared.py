#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-22 08:23:01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/config/settings/settings_shared.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./config/settings/settings_shared.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Django settings for SciTeX Cloud project.
Base settings shared across all environments.
"""

from pathlib import Path
from datetime import timedelta
from scitex import logging
logger = logging.getLogger(__name__)

# ---------------------------------------
# Functions
# ---------------------------------------
def discover_local_apps():
    """Discover all Django apps in the apps directory."""
    apps_path = BASE_DIR / "apps"
    local_apps = []

    if apps_path.exists():
        for item in sorted(apps_path.iterdir()):
            if item.is_dir() and not item.name.startswith("_"):
                # Check if it's a Django app (has apps.py or __init__.py)
                if (item / "apps.py").exists() or (
                    item / "__init__.py"
                ).exists():
                    app_name = f"apps.{item.name}"
                    local_apps.append(app_name)

    return local_apps


# ---------------------------------------
# Meatadata
# ---------------------------------------
SCITEX_VERSION = "0.1.0-alpha"

# ---------------------------------------
# Paths
# ---------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_URLCONF = "config.urls"
LOG_DIR = BASE_DIR / "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------
# URL
# ---------------------------------------
# Authentication settings
LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/core/"  # Redirects to dashboard
LOGOUT_REDIRECT_URL = "/"


# ---------------------------------------
# Security
# ---------------------------------------
SECRET_KEY = os.getenv("SCITEX_DJANGO_SECRET_KEY")

# ---------------------------------------
# Applications
# ---------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "channels",
]

LOCAL_APPS = discover_local_apps()

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.project_app.middleware.GuestSessionMiddleware",
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------
# Templates
# ---------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.project_app.context_processors.version_context",
                "apps.project_app.context_processors.project_context",
            ],
        },
    },
]


# ---------------------------------------
# Database - Fallback
# ---------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "data" / "db" / "sqlite" / "scitex_cloud.db",
    }
}

# Cache Configuration - fallback to database if Redis not available
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1")
try:
    import redis

    # Test Redis connection
    r = redis.from_url(REDIS_URL)
    r.ping()
    # Redis is available
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
            "KEY_PREFIX": "scitex_cloud",
            "TIMEOUT": 3600,  # 1 hour default timeout
        }
    }
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"
except (ImportError, Exception):
    # Redis not available, use database cache
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "cache_table",
        }
    }
    SESSION_ENGINE = "django.contrib.sessions.backends.db"

SESSION_COOKIE_AGE = 86400  # 24 hours

# ---------------------------------------
# Password validation
# ---------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ---------------------------------------
# Internationalization
# ---------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------
# Email
# ---------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "mail1030.onamae.ne.jp"
EMAIL_PORT = 587  # 587 is modern; use 465 only if 587 is blocked
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get(
    "SCITEX_SCHOLAR_FROM_EMAIL_ADDRESS", "agent@scitex.ai"
)
EMAIL_HOST_PASSWORD = os.environ.get("SCITEX_SCHOLAR_FROM_EMAIL_PASSWORD", "")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ASGI Configuration for Channels
ASGI_APPLICATION = "config.asgi.application"

# Channel Layers Configuration (fallback to in-memory if Redis unavailable)
try:
    import redis

    # Test Redis connection for channels
    redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/2")
    r = redis.from_url(redis_url)
    r.ping()
    # Redis is available for channels
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [redis_url],
            },
        },
    }
except (ImportError, Exception):
    # Fallback to in-memory channel layer
    CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
    }

# ---------------------------------------
# Logging
# ---------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "standard": {
            "format": "{asctime} [{levelname}] {name}: {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
            "formatter": "verbose",
        },
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.template": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "scitex": {  # Application-specific logger
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

# ---------------------------------------
# Integration
# ---------------------------------------
# ORCID OAuth
ORCID_CLIENT_ID = os.getenv("ORCID_CLIENT_ID", "")
ORCID_CLIENT_SECRET = os.getenv("ORCID_CLIENT_SECRET", "")
ORCID_REDIRECT_URI = os.getenv(
    "ORCID_REDIRECT_URI", "http://localhost:8000/integrations/orcid/callback/"
)

# ---------------------------------------
# SciTeX Scholar Search Settings
# ---------------------------------------
# Enable/disable search pipeline caching
SCITEX_USE_CACHE = os.getenv("SCITEX_USE_CACHE", "True").lower() in ["true", "1", "yes"]

# Maximum parallel workers for parallel search pipeline
SCITEX_MAX_WORKERS = int(os.getenv("SCITEX_MAX_WORKERS", "5"))

# Timeout per engine in seconds
SCITEX_TIMEOUT_PER_ENGINE = int(os.getenv("SCITEX_TIMEOUT_PER_ENGINE", "30"))

# Preferred engines (comma-separated, e.g., "PubMed,CrossRef,arXiv")
SCITEX_ENGINES = os.getenv("SCITEX_ENGINES", "CrossRef,PubMed,Semantic_Scholar,arXiv,OpenAlex").split(",")

# Default search mode: "parallel" or "single"
SCITEX_DEFAULT_MODE = os.getenv("SCITEX_DEFAULT_MODE", "parallel")

# ---------------------------------------
# REST Framework
# ---------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

# ---------------------------------------
# JWT Settings
# ---------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# EOF
