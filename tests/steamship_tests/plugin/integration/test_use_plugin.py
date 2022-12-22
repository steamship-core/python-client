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
            client.use_plugin(plugin.handle, instance_handle)

            # Should fail because we're using the shortcut `use_plugin` method with the same instance_handle
            with pytest.raises(SteamshipError):
                client.use_plugin(plugin2.handle, instance_handle)
