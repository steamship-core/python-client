import contextlib
import io
import os
import time
import zipfile
from pathlib import Path
from typing import Any, Dict

from steamship import App, AppInstance, AppVersion, Steamship
from steamship.data.plugin import Plugin
from steamship.data.plugin_instance import PluginInstance
from steamship.data.plugin_version import PluginVersion
from steamship.data.user import User
from tests import SRC_PATH, VENV_PATH


def zip_deployable(file_path: Path) -> bytes:
    """Prepare and zip a Steamship plugin."""

    # TODO: This is very dependent on the setup of the local machine.
    # Might be good to find a more machine-invariant solution here.
    # The goal is to copy in all the dependencies of the lambda package.
    # Which are: steamship (current repo), setuptools_scm, requests
    dependencies_path = VENV_PATH / "lib" / "python3.9" / "site-packages"

    package_paths = [
        SRC_PATH / "steamship",
        SRC_PATH
        / ".."
        / "tests",  # This is included to test plugin development using inheritance
        dependencies_path / "setuptools_scm",
        dependencies_path / "requests",
        dependencies_path / "charset_normalizer",
        dependencies_path / "certifi",
        dependencies_path / "urllib3",
        dependencies_path / "idna",
        dependencies_path / "pydantic",
    ]

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(
        file=zip_buffer, mode="a", compression=zipfile.ZIP_DEFLATED, allowZip64=False
    ) as zip_file:
        zip_file.write(file_path, "api.py")

        for package_path in package_paths:
            for root, _, files in os.walk(package_path):
                for file in files:
                    pypi_file = Path(root) / file
                    zip_file.write(
                        pypi_file, pypi_file.relative_to(package_path.parent)
                    )

    return zip_buffer.getvalue()


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
        client, app_id=app.id, app_version_id=version.id, config=instance_config, space_id=space_id
    )
    instance = _wait_for_instance(instance)

    assert instance.app_id == app.id
    assert instance.app_version_id == version.id

    _check_user(client, instance)

    yield app, version, instance

    _delete_deployable(instance, version, app)


@contextlib.contextmanager
def deploy_plugin(
    client: Steamship,
    py_path: Path,
    plugin_type: str,
    version_config_template: Dict[str, Any] = None,
    instance_config: Dict[str, Any] = None,
    training_platform: str = None,
):
    plugin = Plugin.create(
        client,
        training_platform=training_platform,
        description="test",
        type_=plugin_type,
        transport="jsonOverHttp",
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
        config_template=version_config_template,  # TODO: What is this?
    )
    # TODO: This is due to having to wait for the lambda to finish deploying.
    # TODO: We should update the task system to allow its .wait() to depend on this.
    version = _wait_for_version(version)

    instance = PluginInstance.create(
        client,
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
    instance = instance.data
    return instance


def _wait_for_version(version):
    time.sleep(15)
    version.wait()
    assert version.error is None
    assert version.data is not None
    version = version.data
    return version
