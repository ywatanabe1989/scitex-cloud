#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-22 02:58:44 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Cloud/config/settings/base.py
# ----------------------------------------
import os
__FILE__ = (
    "./config/settings/base.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Django settings for SciTeX Cloud project.
Base settings shared across all environments.
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SCITEX_DJANGO_SECRET_KEY")

# Application definition
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

LOCAL_APPS = [
    "apps.cloud_app",
    "apps.code_app",
    "apps.core_app",
    "apps.auth_app",  # Dedicated authentication and user management
    "apps.project_app",  # Dedicated project management app
    "apps.document_app",  # Dedicated document management
    "apps.writer_app",
    "apps.engine_app",
    "apps.viz_app",
    "apps.scholar_app",
    # "apps.billing_app",  # Disabled - needs stripe dependency
    "apps.monitoring_app",
    "apps.api",
    "apps.orcid_app",
    "apps.reference_sync_app",
    "apps.mendeley_app",
    "apps.github_app",
    "apps.collaboration_app",
    "apps.ai_assistant_app",  # Priority 3.3: AI Research Assistant - COMPLETED AND OPERATIONAL
    "apps.onboarding_app",  # Priority 1: User Onboarding & Growth - NEW IMPLEMENTATION
    # "apps.integrations",  # Disabled - redundant with orcid_app
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.monitoring_app.middleware.PerformanceMonitoringMiddleware",
]

ROOT_URLCONF = "config.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "scitex_cloud.db",
    }
}

# Cache Configuration
# Cache Configuration - fallback to database if Redis not available
REDIS_URL = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1')
try:
    import redis
    # Test Redis connection
    r = redis.from_url(REDIS_URL)
    r.ping()
    # Redis is available
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'KEY_PREFIX': 'scitex_cloud',
            'TIMEOUT': 3600,  # 1 hour default timeout
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
except (ImportError, redis.exceptions.ConnectionError, redis.exceptions.RedisError):
    # Redis not available, use database cache
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'cache_table',
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'
    
SESSION_COOKIE_AGE = 86400  # 24 hours

# Password validation
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

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Email Configuration
# Use scitex.ai domain email via mail1030.onamae.ne.jp
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail1030.onamae.ne.jp'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('SCITEX_SCHOLAR_FROM_EMAIL_ADDRESS', 'agent@scitex.ai')
EMAIL_HOST_PASSWORD = os.environ.get('SCITEX_SCHOLAR_FROM_EMAIL_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# SciTeX External Components
SCITEX_EXTERNALS_PATH = str(BASE_DIR / 'externals')
SCITEX_WRITER_TEMPLATE_PATH = str(BASE_DIR / 'externals' / 'SciTeX-Writer')
SCITEX_CODE_PATH = str(BASE_DIR / 'externals' / 'SciTeX-Code')
SCITEX_VIZ_PATH = str(BASE_DIR / 'externals' / 'SciTeX-Viz')
SCITEX_SCHOLAR_PATH = str(BASE_DIR / 'externals' / 'SciTeX-Scholar')
SCITEX_ENGINE_PATH = str(BASE_DIR / 'externals' / 'SciTeX-Engine')
SCITEX_EXAMPLE_PROJECT_PATH = str(BASE_DIR / 'externals' / 'SciTeX-Example-Research-Project')

# SciTeX Component Integration Status
SCITEX_COMPONENTS = {
    'writer': {'path': SCITEX_WRITER_TEMPLATE_PATH, 'status': 'active'},
    'code': {'path': SCITEX_CODE_PATH, 'status': 'ready'},
    'viz': {'path': SCITEX_VIZ_PATH, 'status': 'ready'},
    'engine': {'path': SCITEX_ENGINE_PATH, 'status': 'planned'},
    'example': {'path': SCITEX_EXAMPLE_PROJECT_PATH, 'status': 'template'},
}

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ASGI Configuration for Channels
ASGI_APPLICATION = "config.asgi.application"

# Channel Layers Configuration (fallback to in-memory if Redis unavailable)
try:
    import redis
    # Test Redis connection for channels
    redis_url = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/2')
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
except (ImportError, redis.exceptions.ConnectionError, redis.exceptions.RedisError):
    # Fallback to in-memory channel layer
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        },
    }

# Base logging configuration (shared between environments)
# More specific configurations in development.py and production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'standard': {
            'format': '{asctime} [{levelname}] {name}: {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.template': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'scitex': {  # Application-specific logger
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Authentication settings
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/projects/'
LOGOUT_REDIRECT_URL = '/'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# EOF
