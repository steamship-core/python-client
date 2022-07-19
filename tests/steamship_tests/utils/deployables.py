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

from steamship_tests import SRC_PATH, TEST_ASSETS_PATH

from steamship import App, AppInstance, AppVersion, Steamship
from steamship.data.plugin import HostingType, Plugin
from steamship.data.plugin_instance import PluginInstance
from steamship.data.plugin_version import PluginVersion
from steamship.data.user import User


def install_package(package: str, into_folder: str):
    logging.info(f"Installing {package} into: {into_folder}")
    subprocess.run(  # noqa: S607,S603
        ["pip", "install", "--target", into_folder, package], stdout=subprocess.PIPE
    )


def zip_deployable(file_path: Path) -> bytes:
    """Prepare and zip a Steamship plugin."""

    package_paths = [
        SRC_PATH / "steamship",
        SRC_PATH
        / ".."
        / "steamship_tests",  # This is included to test plugin development using inheritance
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
            for package in [
                "setuptools_scm",
                "requests",
                "charset_normalizer",
                "certifi",
                "urllib3",
                "idna",
                "pydantic==1.9.0",
                "typing_extensions",
                "inflection==0.5.1",
                "fluent-logger==0.10.0",
            ]:
                install_package(package, into_folder=package_dir)
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
    space_id: Optional[str] = None,
):
    plugin = Plugin.create(
        client,
        training_platform=training_platform,
        type_=plugin_type,
        transport="jsonOverHttp",
        description="A Plugin (python client steamship_tests)",
        is_public=False,
    )
    assert plugin.error is None
    assert plugin.data is not None
    plugin = plugin.data

    zip_bytes = zip_deployable(py_path)
    version = PluginVersion.create(
        client,
        "test-version",
        plugin_id=plugin.id,
        filebytes=zip_bytes,
        config_template=version_config_template,
    )
    # TODO: This is due to having to wait for the lambda to finish deploying.
    # TODO: We should update the task system to allow its .wait() to depend on this.
    version = _wait_for_version(version)

    instance = PluginInstance.create(
        client,
        space_id=space_id,
        plugin_id=plugin.id,
        plugin_version_id=version.id,
        config=instance_config,
    )
    instance = _wait_for_instance(instance)

    assert instance.plugin_id == plugin.id
    assert instance.plugin_version_id == version.id

    _check_user(client, instance)

    yield plugin, version, instance

    _delete_deployable(instance, version, plugin)


@contextlib.contextmanager
def deploy_app(
    client: Steamship,
    py_path: Path,
    version_config_template: Dict[str, Any] = None,
    instance_config: Dict[str, Any] = None,
    space_id: str = None,
):
    app = App.create(client)
    assert app.error is None
    assert app.data is not None
    app = app.data

    zip_bytes = zip_deployable(py_path)
    version = AppVersion.create(
        client,
        app_id=app.id,
        filebytes=zip_bytes,
        config_template=version_config_template,
    )

    version = _wait_for_version(version)
    instance = AppInstance.create(
        client,
        app_id=app.id,
        app_version_id=version.id,
        config=instance_config,
        space_id=space_id,
    )
    instance = _wait_for_instance(instance)

    assert instance.app_id == app.id
    assert instance.app_version_id == version.id

    _check_user(client, instance)

    yield app, version, instance

    _delete_deployable(instance, version, app)


def _check_user(client, instance):
    user = User.current(client).data
    assert instance.user_id == user.id


def _delete_deployable(instance, version, deployable):
    res = instance.delete()
    assert res.error is None
    res = version.delete()
    assert res.error is None
    res = deployable.delete()
    assert res.error is None


def _wait_for_instance(instance):
    instance.wait()
    assert instance.error is None
    assert instance.data is not None
    return instance.data


def _wait_for_version(version):
    time.sleep(15)
    version.wait()
    assert version.error is None
    assert version.data is not None
    return version.data
