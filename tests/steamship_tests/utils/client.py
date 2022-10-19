from contextlib import contextmanager
from typing import Any, Dict

from steamship import Steamship
from steamship.data.package_instance import PackageInstance
from steamship.data.plugin_instance import PluginInstance


def get_steamship_client(**kwargs) -> Steamship:
    # Always use the `test` profile
    kwargs["profile"] = "test"
    return Steamship(**kwargs)


@contextmanager
def steamship_use(
    package_handle: str,
    instance_handle: str = None,
    config: Dict[str, Any] = None,
    version: str = None,
    reuse: bool = True,
    delete_workspace: bool = True,
    **kwargs
) -> PackageInstance:
    # Always use the `test` profile
    kwargs["profile"] = "test"
    instance = Steamship.use(package_handle, instance_handle, config, version, reuse, **kwargs)
    assert instance.client.config.workspace_id == instance.workspace_id
    yield instance
    # Clean up the workspace
    if delete_workspace:
        instance.client.get_workspace().delete()


@contextmanager
def steamship_use_plugin(
    plugin_handle: str,
    instance_handle: str = None,
    config: Dict[str, Any] = None,
    version: str = None,
    reuse: bool = True,
    delete_workspace: bool = True,
    **kwargs
) -> PluginInstance:
    # Always use the `test` profile
    kwargs["profile"] = "test"
    instance = Steamship.use_plugin(
        plugin_handle, instance_handle, config, version, reuse, **kwargs
    )
    assert instance.client.config.workspace_id == instance.workspace_id
    yield instance
    # Clean up the workspace
    if delete_workspace:
        instance.client.get_workspace().delete()
