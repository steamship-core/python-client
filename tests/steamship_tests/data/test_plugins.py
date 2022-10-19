# noinspection PyPackageRequirements
import uuid

import pytest
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import PluginInstance, SteamshipError, Workspace
from steamship.data.plugin import Plugin, PluginAdapterType, PluginType


def test_plugin_create():
    steamship = get_steamship_client()

    my_plugins = Plugin.list(steamship)
    orig_count = len(my_plugins.plugins)

    plugin_args = {
        "client": steamship,
        "description": "This is just for test",
        "type_": PluginType.embedder,
        "transport": PluginAdapterType.steamship_docker,
        "is_public": True,
    }

    required_fields = {"description", "type_"}
    for required_field in required_fields:
        del plugin_args[required_field]
        with pytest.raises(TypeError):
            Plugin.create(**plugin_args)

    my_plugins = Plugin.list(steamship)
    assert len(my_plugins.plugins) == orig_count

    plugin = Plugin.create(
        client=steamship,
        description="This is just for test",
        type_=PluginType.tagger,
        transport=PluginAdapterType.steamship_docker,
        is_public=False,
    )
    my_plugins = Plugin.list(steamship)
    assert len(my_plugins.plugins) == orig_count + 1

    # No fetch_if_exists doesn't work
    with pytest.raises(SteamshipError):
        _ = Plugin.create(
            client=steamship,
            handle=plugin.handle,
            description="This is just for test",
            type_=PluginType.tagger,
            transport=PluginAdapterType.steamship_docker,
            is_public=False,
        )

    my_plugins = Plugin.list(steamship)
    assert len(my_plugins.plugins) == orig_count + 1

    assert plugin.id in [plugin.id for plugin in my_plugins.plugins]
    assert plugin.description in [plugin.description for plugin in my_plugins.plugins]

    # assert(my_plugins.plugins[0].description != plugin.description)


def test_plugin_public():
    steamship = get_steamship_client()

    resp = Plugin.list(steamship)
    assert resp.plugins is not None
    plugins = resp.plugins

    assert len(plugins) > 0


def test_deploy_in_workspace():
    client = get_steamship_client()
    workspace = Workspace.create(client, handle="test-non-default-workspace")
    client.switch_workspace(workspace_id=workspace.id)
    instance = PluginInstance.create(client, plugin_handle="test-tagger")
    assert instance.workspace_id == workspace.id


def test_plugin_instance_get():
    steamship = get_steamship_client()
    handle = f"test_tagger_test_handle{uuid.uuid4()}"
    instance = PluginInstance.create(steamship, plugin_handle="test-tagger", handle=handle)
    assert instance.id is not None

    other_instance = PluginInstance.get(steamship, handle=handle)
    assert instance.id == other_instance.id


def test_plugin_instance_quick_create():
    steamship = get_steamship_client()

    handle = f"test_tagger_test_handle{uuid.uuid4()}"
    handle2 = f"test_tagger_test_handle{uuid.uuid4()}"

    p1 = steamship.use_plugin("test-tagger", handle)
    p2 = steamship.use_plugin("test-tagger", handle2)
    p3 = steamship.use_plugin("test-tagger", handle)
    p4 = steamship.use_plugin("test-tagger")

    assert p1.id == p3.id
    assert p1.id != p2.id
    assert p1.id != p4.id
