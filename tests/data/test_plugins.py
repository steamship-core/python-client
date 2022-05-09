import pytest

from steamship.data.plugin import PluginAdapterType
from steamship.data.plugin import PluginType, Plugin
from tests.client.helpers import _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


def test_plugin_create():
    steamship = _steamship()

    my_plugins = Plugin.list(steamship).data
    orig_count = len(my_plugins.plugins)

    # Should require name
    with pytest.raises(Exception):
        index = Plugin.create(
            client=steamship,
            description="This is just for test",
            type=PluginType.embedder,
            transport=PluginAdapterType.steamshipDocker,
            is_public=True,
        )

    # Should require description
    with pytest.raises(Exception):
        index = Plugin.create(
            client=steamship,
            type=PluginType.embedder,
            transport=PluginAdapterType.steamshipDocker,
            is_public=True,
        )

    # Should require plugin type
    with pytest.raises(Exception):
        index = Plugin.create(
            client=steamship,
            description="This is just for test",
            transport=PluginAdapterType.steamshipDocker,
            is_public=True,
        )

    # Should require adapter type
    with pytest.raises(Exception):
        index = steamship.plugins.create(
            client=steamship,
            description="This is just for test",
            type=PluginType.embedder,
            url="http://foo4",
            is_public=True,
        )

    # Should require is public
    with pytest.raises(Exception):
        index = steamship.plugins.create(
            client=steamship,
            description="This is just for test",
            type=PluginType.embedder,
            transport=PluginAdapterType.steamshipDocker,
        )

    my_plugins = Plugin.list(steamship).data
    assert len(my_plugins.plugins) == orig_count

    plugin = Plugin.create(
        client=steamship,
        training_platform=None,
        description="This is just for test",
        type=PluginType.tagger,
        transport=PluginAdapterType.steamshipDocker,
        is_public=False,
    ).data
    my_plugins = Plugin.list(steamship).data
    assert len(my_plugins.plugins) == orig_count + 1

    # No upsert doesn't work
    plugin_x = Plugin.create(
        client=steamship,
        training_platform=None,
        handle=plugin.handle,
        description="This is just for test",
        type=PluginType.tagger,
        transport=PluginAdapterType.steamshipDocker,
        is_public=False,
    )
    assert plugin_x.error is not None
    assert plugin_x.data is None

    # Upsert does work
    plugin2 = Plugin.create(
        client=steamship,
        training_platform=None,
        handle=plugin.handle,
        description="This is just for test 2",
        type=PluginType.tagger,
        transport=PluginAdapterType.steamshipDocker,
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
    steamship = _steamship()

    resp = Plugin.list(steamship).data
    assert resp.plugins is not None
    plugins = resp.plugins

    assert len(plugins) > 0

    # Make sure they can't be deleted.
    res = plugins[0].delete()
    assert res.error is not None
    assert res.data is None
