import pytest

from steamship.data.plugin import PluginAdapterType
from steamship.data.plugin import PluginType, Plugin
from tests.client.helpers import _random_name, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


def test_plugin_create():
    steamship = _steamship()
    name = _random_name()

    my_plugins = Plugin.listPrivate(steamship).data
    orig_count = len(my_plugins.plugins)

    # Should require name
    with pytest.raises(Exception):
        index = Plugin.create(
            client=steamship,
            description="This is just for test",
            type=PluginType.embedder,
            transport=PluginAdapterType.steamshipDocker,
            isPublic=True
        )

    # Should require description
    with pytest.raises(Exception):
        index = Plugin.create(
            client=steamship,
            name="Test Plugin",
            type=PluginType.embedder,
            transport=PluginAdapterType.steamshipDocker,
            isPublic=True
        )

    # Should require plugin type
    with pytest.raises(Exception):
        index = Plugin.create(
            client=steamship,
            name="Test Plugin",
            description="This is just for test",
            transport=PluginAdapterType.steamshipDocker,
            isPublic=True
        )

    # Should require adapter type
    with pytest.raises(Exception):
        index = steamship.plugins.create(
            client=steamship,
            name="Test Plugin",
            description="This is just for test",
            type=PluginType.embedder,
            url="http://foo4",
            isPublic=True
        )

    # Should require is public
    with pytest.raises(Exception):
        index = steamship.plugins.create(
            client=steamship,
            name="Test Plugin",
            description="This is just for test",
            type=PluginType.embedder,
            transport=PluginAdapterType.steamshipDocker,
        )

    my_plugins = Plugin.listPrivate(steamship).data
    assert (len(my_plugins.plugins) == orig_count)

    plugin = Plugin.create(
        client=steamship,
        isTrainable=False,
        name=_random_name(),
        description="This is just for test",
        type=PluginType.tagger,
        transport=PluginAdapterType.steamshipDocker,
        isPublic=False
    ).data
    my_plugins = Plugin.listPrivate(steamship).data
    assert (len(my_plugins.plugins) == orig_count + 1)

    # No upsert doesn't work
    pluginX = Plugin.create(
        client=steamship,
        isTrainable=False,
        handle=plugin.handle,
        name=plugin.name,
        description="This is just for test",
        type=PluginType.tagger,
        transport=PluginAdapterType.steamshipDocker,
        isPublic=False
    )
    assert (pluginX.error is not None)
    assert (pluginX.data is None)

    # Upsert does work
    plugin2 = Plugin.create(
        client=steamship,
        isTrainable=False,
        name=plugin.name,
        description="This is just for test 2",
        type=PluginType.tagger,
        transport=PluginAdapterType.steamshipDocker,
        isPublic=False,
        upsert=True
    ).data

    assert (plugin2.id == plugin.id)

    my_plugins = Plugin.listPrivate(steamship).data
    assert (len(my_plugins.plugins) == orig_count + 1)

    assert (plugin2.id in [plugin.id for plugin in my_plugins.plugins])
    assert (plugin2.description in [plugin.description for plugin in my_plugins.plugins])

    # assert(my_plugins.plugins[0].description != plugin.description)

    plugin.delete()

    my_plugins = Plugin.listPrivate(steamship).data
    assert (len(my_plugins.plugins) == orig_count)


def test_plugin_public():
    steamship = _steamship()
    name = _random_name()

    resp = Plugin.listPublic(steamship).data
    assert (resp.plugins is not None)
    plugins = resp.plugins

    assert (len(plugins) > 0)

    # Make sure they can't be deleted.
    res = plugins[0].delete()
    assert (res.error is not None)
    assert (res.data is None)
