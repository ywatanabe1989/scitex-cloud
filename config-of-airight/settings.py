import os
from pathlib import Path

import environ
from django.utils.translation import gettext_lazy


################################################################################
# Functions
################################################################################
def stream_app_name(app):
    return app.replace("app.", "app/")


################################################################################
# PATH
################################################################################
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_URLCONF = "config.urls"

################################################################################
# Security
################################################################################
# Debug mode
env = environ.Env()
environ.Env.read_env()
DEBUG = env.bool("DJANGO_DEBUG")
if DEBUG:
    ALLOWED_HOSTS = ["*"]
    # ALLOWED_HOSTS = ["ai-write.app", "127.0.0.1"]
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = None
else:
    ALLOWED_HOSTS = ["*"]
    # ALLOWED_HOSTS = ["ai-write.app", "127.0.0.1"]
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = (
    "django-insecure-w@=)m1n^mgd+ocl3v(tih&pt+_q5t&o_hsl1wxramq_m3evhb+"
)

# Authentication
LOGIN_URL = "/auth/login/"
AUTH_USER_MODEL = "auth_app.CustomUser"
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


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

################################################################################
# Application definitions
################################################################################
MY_APPS = [
    "editor_app",
    "auth_app",
    "about_app",
    "payment_app",
]
MY_APPS = [f"apps.{app}" for app in MY_APPS]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "channels",
    "widget_tweaks",
    "rest_framework",
    "tempus_dominus",
    "corsheaders",
    "django_browser_reload",
] + MY_APPS


################################################################################
# Middleware
################################################################################
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]


################################################################################
# Templates
################################################################################
MY_APP_TEMPLATE_DIRS = [
    os.path.join(BASE_DIR, stream_app_name(app), "template") for app in MY_APPS
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")] + MY_APP_TEMPLATE_DIRS,
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

################################################################################
# Database
################################################################################
# # sqlite3
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

# # postgresql
pw_ai_write_db = "9J@H_ns}P[6Neq<;@:t3+0eI>L85,gFIKu%;Cgyp6-G&<x3]-Ei?,bXE?@?Om@Td%@9suNr[AlDaR&}N*3SJjmY^}$6eTeS7QTBDQDiMMNWv?`LG*q}ojwk`c1c>IPqg/T3^<Cf9{d<j^P/OWzkE2H.sJA5rt4:8ple[<.Ec*D@j98pnw6!@18tZSoBT-o_2vVh]UgTS4Z!8B]u}nQivDNHQq7/@Oi0vKZ?AsDwtAD0.n;j@21/<5Qk4}vau+gFD"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ai-write",
        "USER": "ywatanabe",
        "PASSWORD": pw_ai_write_db,
        "HOST": "localhost",
        "PORT": "5432",
    }
}

################################################################################
# Language & Timzone
################################################################################
LANGUAGE_CODE = "en-us"
LANGUAGES = [
    ("en", gettext_lazy("English")),
    ("ja", gettext_lazy("Japanese")),
    ("zh", gettext_lazy("Chinese")),
    ("pt", gettext_lazy("Portuguese")),
    ("fr", gettext_lazy("French")),
    ("it", gettext_lazy("Italian")),
    ("ko", gettext_lazy("Korean")),
    ("ru", gettext_lazy("Russian")),
    ("es", gettext_lazy("Spanish")),
]
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

################################################################################
# Static files
################################################################################
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, stream_app_name(app), "static") for app in MY_APPS
]
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "apps", stream_app_name(app), "static")
    for app in MY_APPS
]
STATICFILES_DIRS += [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = BASE_DIR / "staticfiles"

################################################################################
# Media
################################################################################
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


################################################################################
# Logging
################################################################################

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
        },
        "apps.editor_app": {  # Adjust this to match your app's name
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
SILENCED_SYSTEM_CHECKS = [
    "staticfiles.W004",
    "urls.W005",
]


################################################################################
# Resources
################################################################################
# Memory limites
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600

################################################################################
# Email
################################################################################
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "mail1030.onamae.ne.jp"
EMAIL_PORT = 465
EMAIL_HOST_USER = "support@ai-write.app"
EMAIL_HOST_PASSWORD = (
    "G4RK@X9;1rv220$uV1._=45@YJN3.MaMFLB$XCfT:egw>o]4j.9h}Z{l}w/c},_A"
)
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_LOGGING_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_LOGGING_LEVEL = "DEBUG"

################################################################################
# Message
################################################################################
# MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"
MESSAGE_STORAGE = "apps.auth_app.custom_messages.TimedSessionStorage"

# ################################################################################
# # Cache
# ################################################################################
# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
#         "LOCATION": "127.0.0.1:11211",
#     }
# }
