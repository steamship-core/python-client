import pytest

from steamship.data.plugin import PluginAdapterType
from steamship.data.plugin import PluginType, Plugin
from .helpers import _random_name, _steamship

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
            url="http://foo1",
            transport=PluginAdapterType.steamshipDocker,
            isPublic=True
        )

    # Should require description
    with pytest.raises(Exception):
        index = Plugin.create(
            client=steamship,
            name="Test Plugin",
            type=PluginType.embedder,
            url="http://foo2",
            transport=PluginAdapterType.steamshipDocker,
            isPublic=True
        )

    # Should require model type
    with pytest.raises(Exception):
        index = Plugin.create(
            client=steamship,
            name="Test Plugin",
            description="This is just for test",
            url="http://foo3",
            transport=PluginAdapterType.steamshipDocker,
            isPublic=True
        )

    # Should require url
    with pytest.raises(Exception):
        index = Plugin.create(
            client=steamship,
            name="Test Plugin",
            description="This is just for test",
            type=PluginType.embedder,
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
            url="http://foo5",
            transport=PluginAdapterType.steamshipDocker,
        )

    my_plugins = Plugin.listPrivate(steamship).data
    assert (len(my_plugins.plugins) == orig_count)

    model = Plugin.create(
        client=steamship,
        name=_random_name(),
        description="This is just for test",
        type=PluginType.embedder,
        url="http://foo6",
        transport=PluginAdapterType.steamshipDocker,
        isPublic=False
    ).data
    my_plugins = Plugin.listPrivate(steamship).data
    assert (len(my_plugins.plugins) == orig_count + 1)

    # No upsert doesn't work
    modelX = Plugin.create(
        client=steamship,
        handle=model.handle,
        name=model.name,
        description="This is just for test",
        type=PluginType.embedder,
        url="http://foo7",
        transport=PluginAdapterType.steamshipDocker,
        isPublic=False
    )
    assert (modelX.error is not None)
    assert (modelX.data is None)

    # Upsert does work
    model2 = Plugin.create(
        client=steamship,
        name=model.name,
        description="This is just for test 2",
        type=PluginType.embedder,
        url="http://foo8",
        transport=PluginAdapterType.steamshipDocker,
        isPublic=False,
        upsert=True
    ).data

    assert (model2.id == model.id)

    my_plugins = Plugin.listPrivate(steamship).data
    assert (len(my_plugins.plugins) == orig_count + 1)

    assert (model2.id in [model.id for model in my_plugins.plugins])
    assert (model2.description in [model.description for model in my_plugins.plugins])

    # assert(my_plugins.plugins[0].description != model.description)

    model.delete()

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
