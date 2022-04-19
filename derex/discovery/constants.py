from enum import Enum

from derex.runner.utils import abspath_from_egg

DEREX_DISCOVERY_DJANGO_PATH = abspath_from_egg(
    "derex.discovery", "derex/discovery_django/__init__.py"
).parent
DEREX_DISCOVERY_DJANGO_SETTINGS_PATH = DEREX_DISCOVERY_DJANGO_PATH / "settings"

DDC_PROJECT_TEMPLATE_PATH = abspath_from_egg(
    "derex.discovery", "derex/discovery/docker-compose-discovery.yml.j2"
)

assert all(
    (
        DDC_PROJECT_TEMPLATE_PATH,
        DEREX_DISCOVERY_DJANGO_PATH,
        DEREX_DISCOVERY_DJANGO_SETTINGS_PATH,
    )
), "Some distribution files were not found"


class DiscoveryVersions(Enum):
    # Values will be passed as uppercased named arguments to the docker build
    # e.g. --build-arg DISCOVERY_RELEASE=koa
    ironwood = {
        "discovery_repository": "https://github.com/openedx/course-discovery.git",
        "discovery_version": "open-release/ironwood.master",
        "discovery_release": "ironwood",
        "docker_image_prefix": "ghcr.io/abstract-tech/derex-discovery-ironwood",
        "alpine_version": "alpine3.11",
        "python_version": "2.7.18",
        "whitenoise_version": "<5.0",
        "node_version": "8.9.3",
    }
    juniper = {
        "discovery_repository": "https://github.com/openedx/course-discovery.git",
        "discovery_version": "open-release/juniper.master",
        "discovery_release": "juniper",
        "docker_image_prefix": "ghcr.io/abstract-tech/derex-discovery-juniper",
        "alpine_version": "alpine3.13",
        "python_version": "3.8",
        "node_version": "8.9.3",
    }
    koa = {
        "discovery_repository": "https://github.com/openedx/course-discovery.git",
        "discovery_version": "open-release/koa.master",
        "discovery_release": "koa",
        "docker_image_prefix": "ghcr.io/abstract-tech/derex-discovery-koa",
        "alpine_version": "alpine3.13",
        "python_version": "3.8",
        "node_version": "12.11.1",
    }
