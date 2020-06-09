# type: ignore
# flake8: noqa

import os
import sys

from course_discovery.settings.base import *
from course_discovery.settings.base import (INSTALLED_APPS, COMPRESS_CSS_FILTERS,
                                     JWT_AUTH, LOGGING, MIDDLEWARE_CLASSES, HAYSTACK_CONNECTIONS)


# System
ALLOWED_HOSTS = ["*"]
TIME_ZONE = os.environ.get("TIME_ZONE", "UTC")
LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "en")
DEREX_PROJECT = os.environ["DEREX_PROJECT"]

SECRET_KEY = os.environ.get("SECRET_KEY", "replace-me")
EDX_API_KEY = os.environ.get("EDX_API_KEY", "replace-me")

LOGGING["handlers"]["local"] = {
    "level": "DEBUG",
    "class": "logging.StreamHandler",
    "formatter": "standard",
}

CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache",}}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("MYSQL_DB_NAME", "derex_discovery"),
        "USER": os.environ.get("MYSQL_DB_USER", "root"),
        "PASSWORD": os.environ.get("MYSQL_DB_PASSWORD", "secret"),
        "HOST": os.environ.get("MYSQL_DB_HOST", "mysql"),
        "PORT": os.environ.get("MYSQL_DB_PORT", 3306),
        "ATOMIC_REQUESTS": True,
        "CONN_MAX_AGE": 60,
    }
}

ELASTICSEARCH_URL = "http://elasticsearch:9200/"
HAYSTACK_CONNECTIONS['default']['URL'] = ELASTICSEARCH_URL

# Static files
STATIC_ROOT = "/openedx/staticfiles"
STATIC_URL = "/static/"

# Media
MEDIA_ROOT = "/openedx/media"
MEDIA_URL = "/media/"
LOCAL_DISCOVERY_MEDIA_URL = MEDIA_URL

# Authentication
SOCIAL_AUTH_EDX_OIDC_KEY = os.environ.get("SOCIAL_AUTH_EDX_OIDC_KEY", "discovery-key")
SOCIAL_AUTH_EDX_OIDC_SECRET = os.environ.get(
    "SOCIAL_AUTH_EDX_OIDC_SECRET", "discovery-secret"
)
SOCIAL_AUTH_EDX_OIDC_ID_TOKEN_DECRYPTION_KEY = SOCIAL_AUTH_EDX_OIDC_SECRET
SOCIAL_AUTH_EDX_OIDC_ISSUER = "http://{}.localhost.derex/oauth2".format(DEREX_PROJECT)
SOCIAL_AUTH_EDX_OIDC_URL_ROOT = SOCIAL_AUTH_EDX_OIDC_ISSUER
SOCIAL_AUTH_EDX_OIDC_PUBLIC_URL_ROOT = SOCIAL_AUTH_EDX_OIDC_ISSUER
SOCIAL_AUTH_EDX_OIDC_LOGOUT_URL = "http://{}.localhost.derex/logout".format(DEREX_PROJECT)
SOCIAL_AUTH_REDIRECT_IS_HTTPS = False

BACKEND_SERVICE_EDX_OAUTH2_KEY = SOCIAL_AUTH_EDX_OIDC_KEY
BACKEND_SERVICE_EDX_OAUTH2_SECRET = SOCIAL_AUTH_EDX_OIDC_SECRET
BACKEND_SERVICE_EDX_OAUTH2_PROVIDER_URL = SOCIAL_AUTH_EDX_OIDC_PUBLIC_URL_ROOT

JWT_AUDIENCE = os.environ.get("JWT_AUDIENCE", "lms-key")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "lms-secret")
JWT_AUTH["JWT_ISSUER"] = [
    {
        "ISSUER": SOCIAL_AUTH_EDX_OIDC_ISSUER,
        "AUDIENCE": JWT_AUDIENCE,
        "SECRET_KEY": JWT_SECRET_KEY,
    },
]
# TODO: use urljoin
EDX_DRF_EXTENSIONS = {
    "OAUTH2_USER_INFO_URL": SOCIAL_AUTH_EDX_OIDC_ISSUER + "/user_info"
}

# Email
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp")
EMAIL_PORT = os.environ.get("EMAIL_PORT", "25")
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

if "runserver" in sys.argv:
    DEBUG = True
    COMPRESS_ENABLED = False
    COMPRESS_OFFLINE = False

    INSTALLED_APPS.extend(["debug_toolbar", "elastic_panel"])
    MIDDLEWARE_CLASSES += ("debug_toolbar.middleware.DebugToolbarMiddleware",)
    DEBUG_TOOLBAR_PATCH_SETTINGS = False
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': (lambda __: True),
    }
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'elastic_panel.panel.ElasticDebugPanel'
    ]
    # Without this debug toolbar urls are not registered...
    os.environ["ENABLE_DJANGO_TOOLBAR"] = "1"
    USE_API_CACHING = False
else:
    COMPRESS_CSS_FILTERS += [
        "compressor.filters.cssmin.CSSMinFilter",
    ]
    COMPRESS_ENABLED = True
    COMPRESS_OFFLINE = True
    MIDDLEWARE_CLASSES += ("whitenoise.middleware.WhiteNoiseMiddleware",)

from .container_env import *  # isort:skip
