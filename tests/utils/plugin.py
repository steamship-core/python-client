import contextlib
import io
import os
import time
import zipfile
from pathlib import Path
from typing import Dict

from steamship import Steamship
from steamship.data.plugin import Plugin
from steamship.data.plugin_instance import PluginInstance
from steamship.data.plugin_version import PluginVersion
from steamship.data.user import User
from tests import VENV_PATH, SRC_PATH


def zip_plugin(file_path: Path) -> bytes:
    """Prepare and zip a Steamship plugin."""

    # TODO: This is very dependent on the setup of the local machine.
    # Might be good to find a more machine-invariant solution here.
    # The goal is to copy in all the dependencies of the lambda package.
    # Which are: steamship (current repo), setuptools_scm, requests
    dependencies_path = VENV_PATH / "lib" / "python3.9" / "site-packages"

    package_paths = [
        SRC_PATH / "steamship",
        SRC_PATH / ".." / "tests", # This is included to test plugin development using inheritance
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
                    zip_file.write(pypi_file, pypi_file.relative_to(package_path.parent))

    return zip_buffer.getvalue()


@contextlib.contextmanager
def deploy_plugin(
    client: Steamship,
    py_path: Path,
    plugin_type: str,
    version_config_template: Dict[str, any] = None,
    instance_config: Dict[str, any] = None,
    training_platform: str = None,
):
    plugin = Plugin.create(
        client,
        trainingPlatform=training_platform,
        description="test",
        type=plugin_type,
        transport="jsonOverHttp",
        isPublic=False,
    )
    assert plugin.error is None
    assert plugin.data is not None
    plugin = plugin.data

    zip_bytes = zip_plugin(py_path)
    version = PluginVersion.create(
        client,
        "test-version",
        pluginId=plugin.id,
        filebytes=zip_bytes,
        configTemplate=version_config_template, # TODO: What is this?
    )
    # TODO: This is due to having to wait for the lambda to finish deploying.
    # TODO: We should update the task system to allow its .wait() to depend on this.
    time.sleep(15)
    version.wait()
    assert version.error is None
    assert version.data is not None
    version = version.data

    instance = PluginInstance.create(
        client, pluginId=plugin.id, pluginVersionId=version.id, config=instance_config
    )
    instance.wait()
    assert instance.error is None
    assert instance.data is not None
    instance = instance.data

    assert instance.pluginId == plugin.id
    assert instance.pluginVersionId == version.id

    user = User.current(client).data

    assert instance.userId == user.id
    yield plugin, version, instance

    res = instance.delete()
    assert res.error is None

    res = version.delete()
    assert res.error is None

    res = plugin.delete()
    assert res.error is None
