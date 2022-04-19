"""
Bare minimum settings for dumping database migrations.
"""

from course_discovery.settings.base import *

LOGGING["handlers"]["local"] = {
    "level": "DEBUG",
    "class": "logging.StreamHandler",
    "formatter": "standard",
}

# Use a custom mysql port to increase the probability of finding it free on a build machine.
# buildkit seems to always use host networking mode, so it might clash
# Attempts to add `--network=none` to the Dockerfile RUN directives proved fruitless
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "discovery",
        "HOST": "127.0.0.1",
        "PORT": "3399",
    }
}
