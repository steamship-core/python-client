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

from steamship import Package, PackageInstance, PackageVersion, Steamship
from steamship.data.plugin import HostingType, Plugin
from steamship.data.plugin.plugin_instance import PluginInstance
from steamship.data.plugin.plugin_version import PluginVersion
from steamship.data.user import User


def install_dependencies(folder: str, requirements_path: Path):
    subprocess.run(  # noqa: S607,S603
        ["pip", "install", "--target", folder, "-r", str(requirements_path.resolve())],
        stdout=subprocess.PIPE,
    )
    # Write an empty requirements.txt to the test deployment.
    # Note that this is INTENTIONALLY different than the behavior of a deployable
    # deployed with the CLI, so that you can use the steamship version that you're currently editing
    with open(Path(folder) / "requirements.txt", "w") as requirements_file:
        requirements_file.write("")


def zip_deployable(file_path: Path) -> bytes:
    """Prepare and zip a Steamship plugin."""

    package_paths = [
        SRC_PATH / "steamship",
    ]

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

    # To generate zip files for engine tests, use the create_engine_test_assets script in Scripts

    return zip_buffer.getvalue()


@contextlib.contextmanager
def deploy_plugin(
    client: Steamship,
    py_path: Path,
    plugin_type: str,
    training_platform: Optional[HostingType] = None,
    version_config_template: Dict[str, Any] = None,
    instance_config: Dict[str, Any] = None,
    safe_load_handler: bool = False,
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
    hosting_handler = "steamship.invocable.entrypoint.safe_handler" if safe_load_handler else None
    plugin_version = PluginVersion.create(
        client,
        "test-version",
        plugin_id=plugin.id,
        filebytes=zip_bytes,
        config_template=version_config_template,
        hosting_handler=hosting_handler,
    )
    # TODO: This is due to having to wait for the lambda to finish deploying.
    # TODO: We should update the task system to allow its .wait() to depend on this.
    _wait_for_version(plugin_version)

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
def deploy_package(
    client: Steamship,
    py_path: Path,
    version_config_template: Dict[str, Any] = None,
    instance_config: Dict[str, Any] = None,
    safe_load_handler: bool = False,
):
    package = Package.create(client)

    zip_bytes = zip_deployable(py_path)
    hosting_handler = "steamship.invocable.entrypoint.safe_handler" if safe_load_handler else None
    version = PackageVersion.create(
        client,
        package_id=package.id,
        filebytes=zip_bytes,
        config_template=version_config_template,
        hosting_handler=hosting_handler,
    )

    _wait_for_version(version)
    package_instance = PackageInstance.create(
        client,
        package_id=package.id,
        package_version_id=version.id,
        config=instance_config,
    )

    assert package_instance.package_id == package.id
    assert package_instance.package_version_id == version.id

    _check_user(client, package_instance)

    yield package, version, package_instance

    _delete_deployable(package_instance, version, package)


def _check_user(client, instance):
    user = User.current(client)
    assert instance.user_id == user.id


def _delete_deployable(instance, version, deployable):
    instance.delete()


def _wait_for_version(version: [PackageVersion, PluginVersion]):
    time.sleep(15)
    assert version is not None
