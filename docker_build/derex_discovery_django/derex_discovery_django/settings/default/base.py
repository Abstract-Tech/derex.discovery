# type: ignore
# flake8: noqa

import json
import os
import sys

from course_discovery.settings.base import *
from derex_discovery_django.constants import DEREX_DISCOVERY_SUPPORTED_VERSIONS

try:
    DEREX_DISCOVERY_VERSION = os.environ["DEREX_DISCOVERY_VERSION"]
    assert DEREX_DISCOVERY_VERSION in DEREX_DISCOVERY_SUPPORTED_VERSIONS
except KeyError:
    raise RuntimeError(
        "DEREX_DISCOVERY_VERSION environment variable must be defined in order to use derex default settings"
    )
except AssertionError:
    raise RuntimeError(
        "DEREX_DISCOVERY_VERSION must be on of {}".format(
            DEREX_DISCOVERY_SUPPORTED_VERSIONS
        )
    )


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

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

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
HAYSTACK_CONNECTIONS["default"]["URL"] = ELASTICSEARCH_URL

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
SOCIAL_AUTH_EDX_OIDC_ISSUER = "http://{}.localhost/oauth2".format(DEREX_PROJECT)
SOCIAL_AUTH_EDX_OIDC_URL_ROOT = SOCIAL_AUTH_EDX_OIDC_ISSUER
SOCIAL_AUTH_EDX_OIDC_PUBLIC_URL_ROOT = SOCIAL_AUTH_EDX_OIDC_ISSUER
SOCIAL_AUTH_EDX_OIDC_LOGOUT_URL = "http://{}.localhost/logout".format(DEREX_PROJECT)
SOCIAL_AUTH_REDIRECT_IS_HTTPS = False

# Those are the SSO settings needed from juniper onward
SOCIAL_AUTH_EDX_OAUTH2_KEY = os.environ.get(
    "SOCIAL_AUTH_EDX_OAUTH2_KEY", SOCIAL_AUTH_EDX_OIDC_KEY
)
SOCIAL_AUTH_EDX_OAUTH2_SECRET = os.environ.get(
    "SOCIAL_AUTH_EDX_OAUTH2_SECRET", SOCIAL_AUTH_EDX_OIDC_SECRET
)
SOCIAL_AUTH_EDX_OAUTH2_ISSUER = os.environ.get(
    "SOCIAL_AUTH_EDX_OAUTH2_ISSUER", "http://{}.localhost/oauth2".format(DEREX_PROJECT)
)
SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT = os.environ.get(
    "SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT", "http://{}.localhost".format(DEREX_PROJECT)
)
SOCIAL_AUTH_EDX_OAUTH2_LOGOUT_URL = os.environ.get(
    "SOCIAL_AUTH_EDX_OAUTH2_LOGOUT_URL", SOCIAL_AUTH_EDX_OIDC_LOGOUT_URL
)
BACKEND_SERVICE_EDX_OAUTH2_KEY = os.environ.get(
    "BACKEND_SERVICE_EDX_OAUTH2_KEY", "lms-discovery-backend-service-key"
)
BACKEND_SERVICE_EDX_OAUTH2_SECRET = os.environ.get(
    "BACKEND_SERVICE_EDX_OAUTH2_SECRET", "lms-discovery-backend-service-secret"
)
BACKEND_SERVICE_EDX_OAUTH2_PROVIDER_URL = os.environ.get(
    "BACKEND_SERVICE_EDX_OAUTH2_PROVIDER_URL",
    "http://{}.localhost/oauth2".format(DEREX_PROJECT),
)

JWT_AUDIENCE = os.environ.get("JWT_AUDIENCE", "lms-key")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "lms-secret")
JWT_AUTH.update(
    {
        "JWT_AUDIENCE": JWT_AUDIENCE,  # Warning: Without this the LMS will reply with a 401 "Invalid token"
        "JWT_SECRET_KEY": JWT_SECRET_KEY,
        "JWT_ISSUER": [
            {
                "ISSUER": SOCIAL_AUTH_EDX_OIDC_ISSUER,
                "AUDIENCE": JWT_AUDIENCE,
                "SECRET_KEY": JWT_SECRET_KEY,
            },
        ],
        # These settings are NOT part of DRF-JWT's defaults.
        "JWT_ISSUERS": [
            {
                "ISSUER": SOCIAL_AUTH_EDX_OAUTH2_ISSUER,
                "AUDIENCE": JWT_AUDIENCE,
                "SECRET_KEY": JWT_SECRET_KEY,
            },
            {
                "ISSUER": "discovery_worker",
                "AUDIENCE": JWT_AUDIENCE,
                "SECRET_KEY": JWT_SECRET_KEY,
            },
        ],
    }
)

JWT_PUBLIC_SIGNING_JWK_SET = json.dumps(
    {
        "keys": [
            {
                "e": "AQAB",
                "kid": "L9IHZW6G",
                "kty": "RSA",
                "n": "uId8gxb1JqiwS2jYDo6jKAolZzniNr2lviBga-pDyZuBOsVkqL1kreDKKo4C4MFF11XAeFfjEkRlYayrGfHh3GWIyeVA3zr5c1PL0RlxwgmPCRo8XRD5r2hofcRYUzQkjKAVYcs-etLB3_e0Lj0HH0z1RDEKA7dZ6wvJc1UtsUJwLp3IuKRv3I9WXbM3C6RTQgGpfII7tAPsnqnn6TYLvXcvScXpA56IZC6THO5__SuW9JtKMvhX8nuM-U5sBgQi-JFhR1aHoOzmrgMCkw4VvPZC2yPDapqwxl74nUSDN5TokxSheGGtrh6LRUtBWeb4sDE8Xpp_2F7cV-DwYORiKw",
            }
        ]
    }
)
JWT_AUTH["JWT_PUBLIC_SIGNING_JWK_SET"] = JWT_PUBLIC_SIGNING_JWK_SET

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
    if DEREX_DISCOVERY_VERSION == "ironwood":
        MIDDLEWARE_CLASSES += ("debug_toolbar.middleware.DebugToolbarMiddleware",)
    else:
        MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)

    DEBUG_TOOLBAR_PATCH_SETTINGS = False
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": (lambda __: True),
    }
    DEBUG_TOOLBAR_PANELS = [
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.logging.LoggingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
        "elastic_panel.panel.ElasticDebugPanel",
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
    if DEREX_DISCOVERY_VERSION == "ironwood":
        MIDDLEWARE_CLASSES += ("whitenoise.middleware.WhiteNoiseMiddleware",)
    else:
        MIDDLEWARE += ("whitenoise.middleware.WhiteNoiseMiddleware",)

from .container_env import *  # isort:skip
