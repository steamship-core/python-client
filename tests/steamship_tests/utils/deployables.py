import contextlib
import io
import logging
import os
import subprocess  # noqa: S404
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any, Dict, Optional

from steamship_tests import ROOT_PATH, SRC_PATH, TEST_ASSETS_PATH

from steamship import App, AppInstance, AppVersion, Steamship
from steamship.base import Task
from steamship.data.plugin import HostingType, Plugin
from steamship.data.plugin_instance import PluginInstance
from steamship.data.plugin_version import PluginVersion
from steamship.data.user import User


def install_dependencies(folder: str, requirements_path: Path):
    subprocess.run(  # noqa: S607,S603
        ["pip", "install", "--target", folder, "-r", str(requirements_path.resolve())],
        stdout=subprocess.PIPE,
    )


def zip_deployable(file_path: Path) -> bytes:
    """Prepare and zip a Steamship plugin."""

    package_paths = [SRC_PATH / "steamship"]

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(
        file=zip_buffer, mode="a", compression=zipfile.ZIP_DEFLATED, allowZip64=False
    ) as zip_file:
        zip_file.write(file_path, "api.py")

        # Copy in the package paths from source
        for package_path in package_paths:
            for root, _, files in os.walk(package_path):
                for file in files:
                    pypi_file = Path(root) / file
                    zip_file.write(pypi_file, pypi_file.relative_to(package_path.parent))

        # Copy in package paths from pip
        with tempfile.TemporaryDirectory() as package_dir:
            logging.info(f"Created tempdir for pip installs: {package_dir}")
            install_dependencies(
                folder=package_dir, requirements_path=ROOT_PATH / "requirements.txt"
            )
            # Now write that whole folder
            for root, _, files in os.walk(package_dir):
                for file in files:
                    pypi_file = Path(root) / file
                    zip_file.write(pypi_file, pypi_file.relative_to(package_dir))

        # Now we'll copy in the whole assets directory so that our test files can access things there..
        for root, _, files in os.walk(TEST_ASSETS_PATH):
            for file in files:
                the_file = Path(root) / file
                relative_path = the_file.relative_to(TEST_ASSETS_PATH.parent)
                zip_file.write(the_file, relative_path)

    # Leaving this in as a reminder: this is an easy way to generate the app zip for use in
    # updating engine unit steamship_tests.
    #
    # with open("demo_app.zip", 'wb') as f:
    #     f.write(zip_buffer.getvalue())
    #

    return zip_buffer.getvalue()


@contextlib.contextmanager
def deploy_plugin(
    client: Steamship,
    py_path: Path,
    plugin_type: str,
    training_platform: Optional[HostingType] = None,
    version_config_template: Dict[str, Any] = None,
    instance_config: Dict[str, Any] = None,
):
    plugin = Plugin.create(
        client,
        training_platform=training_platform,
        type_=plugin_type,
        transport="jsonOverHttp",
        description="A Plugin (python client steamship_tests)",
        is_public=False,
    )

    zip_bytes = zip_deployable(py_path)
    create_plugin_version_task = PluginVersion.create(
        client,
        "test-version",
        plugin_id=plugin.id,
        filebytes=zip_bytes,
        config_template=version_config_template,
    )
    # TODO: This is due to having to wait for the lambda to finish deploying.
    # TODO: We should update the task system to allow its .wait() to depend on this.
    plugin_version = _wait_for_version(create_plugin_version_task)

    plugin_instance = PluginInstance.create(
        client,
        plugin_id=plugin.id,
        plugin_version_id=plugin_version.id,
        config=instance_config,
    )

    assert plugin_instance.plugin_id == plugin.id
    assert plugin_instance.plugin_version_id == plugin_version.id

    _check_user(client, plugin_instance)

    yield plugin, plugin_version, plugin_instance

    _delete_deployable(plugin_instance, plugin_version, plugin)


@contextlib.contextmanager
def deploy_app(
    client: Steamship,
    py_path: Path,
    version_config_template: Dict[str, Any] = None,
    instance_config: Dict[str, Any] = None,
):
    app = App.create(client)

    zip_bytes = zip_deployable(py_path)
    version = AppVersion.create(
        client,
        app_id=app.id,
        filebytes=zip_bytes,
        config_template=version_config_template,
    )

    version = _wait_for_version(version)
    app_instance = AppInstance.create(
        client,
        app_id=app.id,
        app_version_id=version.id,
        config=instance_config,
    )

    assert app_instance.app_id == app.id
    assert app_instance.app_version_id == version.id

    _check_user(client, app_instance)

    yield app, version, app_instance

    _delete_deployable(app_instance, version, app)


def _check_user(client, instance):
    user = User.current(client)
    assert instance.user_id == user.id


def _delete_deployable(instance, version, deployable):
    instance.delete()
    version.delete()
    deployable.delete()


def _wait_for_version(version: Task):
    time.sleep(15)
    version.wait()
    assert version.output is not None
    return version.output
