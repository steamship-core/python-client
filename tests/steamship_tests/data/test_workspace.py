import pytest
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import SteamshipError, Workspace


def test_default_workspace():
    client = get_steamship_client()
    workspace = Workspace.get(client=client)
    assert workspace is not None
    assert workspace.handle == "default"


def test_delete_workspace():
    client = get_steamship_client()
    default = Workspace.get(client=client)
    workspace1 = Workspace.create(client=client, handle="test")
    assert default.id is not None
    assert workspace1.id is not None
    assert default.id != workspace1.id

    workspace1.delete()
    with pytest.raises(SteamshipError):
        _ = Workspace.get(client=client, id_=workspace1.id)

    workspace1 = Workspace.create(client=client, handle="test")
    assert default.id is not None
    assert workspace1.id is not None
    assert default.id != workspace1.id

    workspace1a = Workspace.get(client=client, id_=workspace1.id)
    assert workspace1a is not None

    workspace1.delete()
    with pytest.raises(SteamshipError):
        _ = Workspace.get(client=client, id_=workspace1.id)


def test_get_workspace():
    client = get_steamship_client()
    default = Workspace.get(client=client)
    workspace1 = Workspace.create(client=client, handle="test")
    workspace1a = Workspace.get(client=client, id_=workspace1.id)
    assert workspace1a.id == workspace1.id
    assert workspace1a.id != default.id
    assert workspace1a.handle == workspace1.handle

    workspace1b = Workspace.get(client=client, handle=workspace1.handle)
    assert workspace1b.id == workspace1.id
    assert workspace1b.handle == workspace1.handle

    workspace1c = Workspace.get(client=client, id_=workspace1.id, handle=workspace1.handle)
    assert workspace1c.id == workspace1.id
    assert workspace1c.handle == workspace1.handle

    workspace1.delete()


def test_create_use_delete_workspace():
    client = get_steamship_client()
    default = Workspace.get(client=client)
    workspace1 = Workspace.create(client=client, handle="test")
    workspace2 = Workspace.create(client=client, handle="test2")

    assert workspace1 is not None
    assert workspace1.handle == "test"

    assert workspace2 is not None
    assert workspace2.handle == "test2"

    assert workspace2.id != workspace1.id
    assert workspace1.id != default.id
    assert workspace2.id != default.id

    workspace1a = Workspace.get(client=client, id_=workspace1.id)
    workspace1b = Workspace.get(client=client, handle=workspace1.handle)
    workspace1c = Workspace.get(client=client, id_=workspace1.id)

    assert workspace1.id == workspace1a.id
    assert workspace1.id == workspace1b.id
    assert workspace1.id == workspace1c.id

    workspace1a.delete()

    # These two are the same workspace! You can't delete twice!
    with pytest.raises(SteamshipError):
        workspace1b.delete()

    with pytest.raises(SteamshipError):
        workspace1c.delete()

    workspace2.delete()
    with pytest.raises(SteamshipError):
        _ = Workspace.get(client=client, id_=workspace1.id)


def test_list_workspace():
    client = get_steamship_client()
    default = Workspace.get(client=client)

    initial_workspace_count = len(Workspace.list(client).workspaces)

    workspace1 = Workspace.create(client=client)
    workspace2 = Workspace.create(client=client)
    workspace3 = Workspace.create(client=client)

    workspaces = Workspace.list(client).workspaces
    assert len(workspaces) == initial_workspace_count + 3
    assert default in workspaces
    assert workspace1 in workspaces
    assert workspace2 in workspaces
    assert workspace3 in workspaces

    workspace1.delete()
    workspace2.delete()
    workspace3.delete()
