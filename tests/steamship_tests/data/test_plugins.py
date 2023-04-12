# noinspection PyPackageRequirements
import uuid

import pytest
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import PluginInstance, SteamshipError, Workspace
from steamship.data.plugin import Plugin, PluginAdapterType, PluginType
from steamship.data.user import User


def test_plugin_create():
    steamship = get_steamship_client()

    resp = Plugin.list(steamship)
    prior_plugin_ids = [plugin.id for plugin in resp.plugins]

    plugin_args = {
        "client": steamship,
        "description": "This is just for test",
        "type_": PluginType.tagger,
        "transport": PluginAdapterType.steamship_docker,
        "is_public": True,
    }

    required_fields = {"description", "type_"}
    for required_field in required_fields:
        del plugin_args[required_field]
        with pytest.raises(TypeError):
            Plugin.create(**plugin_args)

    plugin = Plugin.create(
        client=steamship,
        description="This is just for test",
        type_=PluginType.tagger,
        transport=PluginAdapterType.steamship_docker,
        is_public=False,
    )

    assert plugin.id not in prior_plugin_ids

    resp = Plugin.list(steamship)
    assert plugin.id in [
        plugin.id for plugin in resp.plugins
    ]  # newly-created plugin should be top of list
    assert plugin.description in [plugin.description for plugin in resp.plugins]

    user_id = User.current(steamship).id
    assert plugin.user_id == user_id

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


def test_plugin_update():
    steamship = get_steamship_client()

    plugin = Plugin.create(
        client=steamship,
        description="This is just for test",
        type_=PluginType.tagger,
        transport=PluginAdapterType.steamship_docker,
        is_public=False,
    )

    new_description = "f"
    plugin.description = new_description

    plugin = plugin.update(steamship)
    assert plugin.description == new_description

    got_plugin = Plugin.get(steamship, handle=plugin.handle)
    assert got_plugin.description == new_description


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


def test_plugin_instance_handle_refs():
    steamship = get_steamship_client()
    handle = f"test_tagger_test_handle{uuid.uuid4()}"
    instance = PluginInstance.create(
        steamship, plugin_handle="test-tagger", plugin_version_handle="1.0", handle=handle
    )

    assert instance.plugin_handle == "test-tagger"
    assert instance.plugin_version_handle == "1.0"

    got_instance = PluginInstance.get(steamship, handle=handle)
    assert got_instance.plugin_handle == "test-tagger"
    assert got_instance.plugin_version_handle == "1.0"

    use_instance = steamship.use_plugin("test-tagger", handle)
    assert use_instance.plugin_handle == "test-tagger"
    assert use_instance.plugin_version_handle == "1.0"
