# noinspection PyPackageRequirements
import uuid

import pytest
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import PluginInstance, Space
from steamship.data.plugin import Plugin, PluginAdapterType, PluginType


def test_plugin_create():
    steamship = get_steamship_client()

    my_plugins = Plugin.list(steamship).data
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

    my_plugins = Plugin.list(steamship).data
    assert len(my_plugins.plugins) == orig_count

    plugin = Plugin.create(
        client=steamship,
        description="This is just for test",
        type_=PluginType.tagger,
        transport=PluginAdapterType.steamship_docker,
        is_public=False,
    ).data
    my_plugins = Plugin.list(steamship).data
    assert len(my_plugins.plugins) == orig_count + 1

    # No upsert doesn't work
    plugin_x = Plugin.create(
        client=steamship,
        handle=plugin.handle,
        description="This is just for test",
        type_=PluginType.tagger,
        transport=PluginAdapterType.steamship_docker,
        is_public=False,
        upsert=False,
    )
    assert plugin_x.error is not None

    # Upsert does work
    plugin2 = Plugin.create(
        client=steamship,
        handle=plugin.handle,
        description="This is just for test 2",
        type_=PluginType.tagger,
        transport=PluginAdapterType.steamship_docker,
        is_public=False,
        upsert=True,
    ).data

    assert plugin2.id == plugin.id

    my_plugins = Plugin.list(steamship).data
    assert len(my_plugins.plugins) == orig_count + 1

    assert plugin2.id in [plugin.id for plugin in my_plugins.plugins]
    assert plugin2.description in [plugin.description for plugin in my_plugins.plugins]

    # assert(my_plugins.plugins[0].description != plugin.description)

    plugin.delete()

    my_plugins = Plugin.list(steamship).data
    assert len(my_plugins.plugins) == orig_count


def test_plugin_public():
    steamship = get_steamship_client()

    resp = Plugin.list(steamship).data
    assert resp.plugins is not None
    plugins = resp.plugins

    assert len(plugins) > 0

    # Make sure they can't be deleted.
    res = plugins[0].delete()
    assert res.error is not None


def test_deploy_in_space():
    client = get_steamship_client()
    space = Space.create(client, handle="test-non-default-space").data
    instance = PluginInstance.create(client, plugin_handle="test-tagger", space_id=space.id).data
    assert instance.space_id == space.id


def test_plugin_instance_get():
    steamship = get_steamship_client()
    handle = f"test_tagger_test_handle{uuid.uuid4()}"
    instance = PluginInstance.create(steamship, plugin_handle="test-tagger", handle=handle).data
    assert instance.id is not None

    other_instance = PluginInstance.get(steamship, handle=handle).data

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
