import logging
import os
import stat
from pathlib import Path
from typing import Dict, List, Optional, Union

from derex import runner  # type: ignore
from derex.runner.project import Project
from derex.runner.utils import abspath_from_egg
from jinja2 import Template

logger = logging.getLogger(__name__)


def generate_local_docker_compose(project: Project) -> Path:
    """TODO: Interim function waiting to be refactored into derex.runner
    """
    local_compose_path = project.private_filepath("docker-compose-discovery.yml")
    template_compose_path = abspath_from_egg(
        "derex.discovery", "derex/discovery/docker-compose-discovery.yml.j2"
    )
    plugin_directories = project.get_plugin_directories(__package__)
    our_settings_dir = abspath_from_egg(
        "derex.discovery", "derex/discovery/settings/README.rst"
    ).parent

    settings_dir = our_settings_dir / "derex"
    active_settings = "base"

    if plugin_directories.get("settings"):
        settings_dir = plugin_directories.get("settings")

        if (
            plugin_directories.get("settings") / "{}.py".format(project.settings.name)
        ).exists():
            active_settings = project.settings.name
        else:
            logger.warning(
                f"{project.settings.name} settings module not found for {__package__} plugin. "
                "Running with default settings."
            )

        # Write out default read-only settings file
        # if they are not present
        base_settings = settings_dir / "base.py"
        if not base_settings.is_file():
            base_settings.write_text("from .derex import *\n")

        init = settings_dir / "__init__.py"
        if not init.is_file():
            init.write_text('"""Settings for edX Discovery Service"""')

        for source_code in our_settings_dir.glob("**/*.py"):
            destination = settings_dir / source_code.relative_to(our_settings_dir)
            if (
                destination.is_file()
                and destination.read_text() != source_code.read_text()
            ):
                # TODO: Replace this warning with a call to a derex.runner
                # function which should take care of updating default settings
                logger.warning(
                    f"WARNING: Default settings modified at {destination}. Replacing "
                )
            if not destination.parent.is_dir():
                destination.parent.mkdir(parents=True)
            try:
                destination.write_text(source_code.read_text())
            except PermissionError:
                current_mode = stat.S_IMODE(os.lstat(destination).st_mode)
                # XXX Remove me: older versions of derex set a non-writable permission
                # for their files. This except branch is needed now (Easter 2020), but
                # when the pandemic is over we can probably remove it
                destination.chmod(current_mode | 0o700)
                destination.write_text(source_code.read_text())

    tmpl = Template(template_compose_path.read_text())
    text = tmpl.render(
        project=project,
        plugins_dirs=plugin_directories,
        settings_dir=settings_dir,
        active_settings=active_settings,
    )
    local_compose_path.write_text(text)
    return local_compose_path


class DiscoveryService:
    @staticmethod
    @runner.hookimpl
    def ddc_project_options(
        project: Project,
    ) -> Optional[Dict[str, Union[str, List[str]]]]:
        if "derex.discovery" in project.config.get("plugins", {}):
            local_compose_path = generate_local_docker_compose(project)
            options = ["-f", str(local_compose_path)]
            return {
                "options": options,
                "name": "discovery",
                "priority": "<local-project",
            }
        return None
