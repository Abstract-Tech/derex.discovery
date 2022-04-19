import logging

import click
from derex.runner.cli import ensure_project
from derex.runner.cli.build import build as derex_build_cli
from derex.runner.docker_utils import buildx_image
from derex.runner.utils import abspath_from_egg

from derex.discovery import __version__
from derex.discovery.constants import DiscoveryVersions

logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def discovery(ctx):
    """Derex edX Discovery plugin: commands to manage the Open edX Discovery service"""
    pass


@discovery.command(name="reset-mysql")
@click.pass_obj
@ensure_project
def reset_mysql(project):
    """Reset the discovery mysql database"""
    from derex.runner.ddc import run_ddc_project
    from derex.runner.docker_utils import wait_for_service
    from derex.runner.project import ProjectRunMode
    from derex.runner.utils import abspath_from_egg

    if project.runmode is not ProjectRunMode.debug:
        click.get_current_context().fail(
            "This command can only be run in `debug` runmode"
        )

    wait_for_service("mysql")
    restore_dump_path = abspath_from_egg(
        "derex.discovery", "derex/discovery/restore_dump.py"
    )
    run_ddc_project(
        [
            "run",
            "--rm",
            "-v",
            f"{restore_dump_path}:/openedx/discovery/restore_dump.py",
            "discovery",
            "python",
            "/openedx/discovery/restore_dump.py",
        ],
        project,
    )
    return 0


# TODO: Be able to load fixtures selectively
@discovery.command(name="load-fixtures")
@click.pass_obj
@ensure_project
def load_fixtures(project):
    """Load fixtures from the plugin fixtures directory"""
    from derex.runner.ddc import run_ddc_project
    from derex.runner.utils import abspath_from_egg

    fixtures_dir = project.get_plugin_directories(__package__).get("fixtures")
    if fixtures_dir is None:
        click.echo("No fixtures directory present for this plugin")
        return

    load_fixtures_path = abspath_from_egg(
        "derex.discovery", "derex/discovery/load_fixtures.py"
    )
    compose_args = [
        "run",
        "--rm",
        "-v",
        f"{load_fixtures_path}:/openedx/discovery/load_fixtures.py",
        "discovery",
        "python",
        "/openedx/discovery/load_fixtures.py",
    ]
    run_ddc_project(compose_args, project)
    return


@discovery.command(name="refresh-course-metadata")
@click.pass_obj
@ensure_project
def refresh_course_metadata(project):
    """Run discovery `refresh_course_metadata` Django command"""
    from derex.runner.ddc import run_ddc_project
    from derex.runner.docker_utils import check_services

    if not check_services(["elasticsearch"]):
        click.echo(
            "Elasticsearch service not found.\nMaybe you forgot to run\nddc-services up -d"
        )
        return

    run_ddc_project(
        ["run", "--rm", "discovery", "python", "manage.py", "refresh_course_metadata"],
        project,
    )
    return 0


@discovery.command(name="create-index")
@click.pass_obj
@ensure_project
def create_index(project):
    """Run discovery `install_es_indexes` Django command"""
    from derex.runner.ddc import run_ddc_project
    from derex.runner.docker_utils import check_services

    if not check_services(["elasticsearch"]):
        click.echo(
            "Elasticsearch service not found.\nMaybe you forgot to run\nddc-services up -d"
        )
        return

    run_ddc_project(
        ["run", "--rm", "discovery", "python", "manage.py", "install_es_indexes"],
        project,
    )
    return 0


@discovery.command(name="update-index")
@click.pass_obj
@ensure_project
def update_index(project):
    """Run discovery `update_index` Django command"""
    from derex.runner.ddc import run_ddc_project
    from derex.runner.docker_utils import check_services

    if not check_services(["elasticsearch"]):
        click.echo(
            "Elasticsearch service not found.\nMaybe you forgot to run\nddc-services up -d"
        )
        return

    run_ddc_project(
        [
            "run",
            "--rm",
            "discovery",
            "python",
            "manage.py",
            "update_index",
            "--disable-change-limit",
        ],
        project,
    )
    return 0


@derex_build_cli.command("discovery")
@click.argument(
    "version",
    type=click.Choice(DiscoveryVersions.__members__),
    required=True,
    callback=lambda _, __, value: value and DiscoveryVersions[value],
)
@click.option(
    "--only-print-image-tag",
    is_flag=True,
    default=False,
    help="Only print the tag which will be assigned to the image",
)
def discovery_build(version, only_print_image_tag):
    """Build discovery image using docker BuildKit."""
    dockerfile_dir = abspath_from_egg(
        "derex.discovery", "docker_build/Dockerfile"
    ).parent
    dockerfile_text = (dockerfile_dir / "Dockerfile").read_text()
    build_args = {}
    for spec in version.value.items():
        build_args[spec[0].upper()] = spec[1]
    docker_image_prefix = version.value["docker_image_prefix"]
    image_tag = f"{docker_image_prefix}:{__version__}"
    cache_tag = f"{docker_image_prefix}:cache"
    if only_print_image_tag:
        click.echo(image_tag)
        return
    buildx_image(
        dockerfile_text=dockerfile_text,
        paths=[dockerfile_dir],
        target="base",
        output="docker",
        tags=[image_tag],
        pull=False,
        cache=True,
        cache_to=False,
        cache_from=False,
        cache_tag=cache_tag,
        build_args=build_args,
    )
