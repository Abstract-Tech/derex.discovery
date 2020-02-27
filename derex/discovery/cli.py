import logging
import os

import click
from derex.runner.cli import ensure_project
from derex.runner.compose_utils import run_compose
from derex.runner.project import ProjectRunMode
from derex.runner.utils import abspath_from_egg

logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def discovery(ctx):
    """Derex edX Discovery plugin: commands to manage the Open edX Discovery service
    """
    pass


@discovery.command(name="reset-mysql")
@click.pass_obj
@ensure_project
def reset_mysql_cmd(project):
    """Reset the discovery mysql database"""
    from derex.runner.docker import check_services
    from derex.runner.docker import wait_for_mysql

    if project.runmode is not ProjectRunMode.debug:
        click.get_current_context().fail(
            "This command can only be run in `debug` runmode"
        )
    if not check_services(["mysql"]):
        click.echo(
            "Mysql service not found.\nMaybe you forgot to run\nddc-services up -d"
        )
        return

    wait_for_mysql()
    restore_dump_path = abspath_from_egg(
        "derex.discovery", "derex/discovery/restore_dump.py"
    )
    run_compose(
        [
            "run",
            "--rm",
            "-v",
            f"{restore_dump_path}:/openedx/discovery/restore_dump.py",
            "discovery",
            "python",
            "/openedx/discovery/restore_dump.py",
        ],
        project=project,
    )
    return 0


@discovery.command(name="refresh-course-metadata")
@click.pass_obj
@ensure_project
def refresh_course_metadata(project):
    """Reset the discovery mysql database"""
    from derex.runner.docker import check_services

    if not check_services(["elasticsearch"]):
        click.echo(
            "Elasticsearch service not found.\nMaybe you forgot to run\nddc-services up -d"
        )
        return

    run_compose(
        [
            "run",
            "--rm",
            "discovery",
            "python",
            "manage.py",
            "refresh_course_metadata"
        ],
        project=project,
    )
    return 0


@discovery.command(name="refresh-course-metadata")
@click.pass_obj
@ensure_project
def refresh_course_metadata(project):
    """Run discovery refresh_course_metadata Django command"""
    from derex.runner.docker import check_services

    if not check_services(["elasticsearch"]):
        click.echo(
            "Elasticsearch service not found.\nMaybe you forgot to run\nddc-services up -d"
        )
        return

    run_compose(
        [
            "run",
            "--rm",
            "discovery",
            "python",
            "manage.py",
            "refresh_course_metadata"
        ],
        project=project,
    )
    return 0


@discovery.command(name="create-index")
@click.pass_obj
@ensure_project
def create_index(project):
    """Run discovery install_es_indexes Django command"""
    from derex.runner.docker import check_services

    if not check_services(["elasticsearch"]):
        click.echo(
            "Elasticsearch service not found.\nMaybe you forgot to run\nddc-services up -d"
        )
        return

    run_compose(
        [
            "run",
            "--rm",
            "discovery",
            "python",
            "manage.py",
            "install_es_indexes"
        ],
        project=project,
    )
    return 0


@discovery.command(name="update-index")
@click.pass_obj
@ensure_project
def update_index(project):
    """Run discovery update_index Django command"""
    from derex.runner.docker import check_services

    if not check_services(["elasticsearch"]):
        click.echo(
            "Elasticsearch service not found.\nMaybe you forgot to run\nddc-services up -d"
        )
        return

    run_compose(
        [
            "run",
            "--rm",
            "discovery",
            "python",
            "manage.py",
            "update_index",
            "--disable-change-limit"
        ],
        project=project,
    )
    return 0
