import pytest
from steamship_tests import PLUGINS_PATH
from steamship_tests.utils.deployables import deploy_plugin
from steamship_tests.utils.fixtures import get_steamship_client
from steamship_tests.utils.random import random_name

from steamship import SteamshipError


def test_use_plugin():
    client = get_steamship_client()
    blockifier_path = PLUGINS_PATH / "blockifiers" / "blockifier.py"

    workspace_handle = random_name()
    client.switch_workspace(workspace_handle=workspace_handle)

    with deploy_plugin(client, blockifier_path, "blockifier") as (
        plugin,
        version,
        instance,
    ):
        assert instance.client.config.workspace_handle == workspace_handle


def test_use_plugin_fails_with_same_instance_name_but_different_plugin_name():
    client = get_steamship_client()

    instance_handle = random_name()

    blockifier_path = PLUGINS_PATH / "blockifiers" / "blockifier.py"
    with deploy_plugin(client, blockifier_path, "blockifier") as (
        plugin,
        version,
        instance,
    ):
        with deploy_plugin(client, blockifier_path, "blockifier") as (
            plugin2,
            version2,
            instance2,
        ):
            client.use_plugin(plugin.handle, instance_handle=instance_handle)

            # Should fail because we're using the shortcut `use_plugin` method with the same instance_handle
            with pytest.raises(SteamshipError):
                client.use_plugin(plugin2.handle, instance_handle=instance_handle)

            # setting recreate = True should fix things
            client.use_plugin(plugin2.handle, instance_handle=instance_handle, recreate=True)


def test_use_plugin_recreate():
    client = get_steamship_client()
    blockifier_path = PLUGINS_PATH / "blockifiers" / "blockifier.py"
    with deploy_plugin(client, blockifier_path, "blockifier") as (
        plugin,
        version,
        instance,
    ):
        client.use_plugin(plugin.handle)

        # re-creating the same plugin with fetch_if_exists = True should not fail
        client.use_plugin(plugin.handle)

        # re-creating the same plugin_handle and plugin_version_handle should fail
        with pytest.raises(SteamshipError):
            client.use_plugin(plugin.handle, fetch_if_exists=False)

        # setting recreate = True should fix things
        client.use_plugin(plugin.handle, recreate=True, fetch_if_exists=False)

        instance_handle = random_name()
        client.use_plugin(plugin.handle, instance_handle=instance_handle)

        # re-creating the same plugin_handle and plugin_version_handle with the same instance_handle should fail
        with pytest.raises(SteamshipError):
            client.use_plugin(plugin.handle, instance_handle=instance_handle, fetch_if_exists=False)

        # setting recreate = True should fix things
        client.use_plugin(
            plugin.handle, instance_handle=instance_handle, recreate=True, fetch_if_exists=False
        )

        # using a difference instance_handle fixes things
        new_instance_handle = random_name()
        client.use_plugin(plugin.handle, instance_handle=new_instance_handle)

        # calling recreate on an new instance handle should not fail
        new_instance_handle = random_name()
        client.use_plugin(plugin.handle, instance_handle=new_instance_handle, recreate=True)
