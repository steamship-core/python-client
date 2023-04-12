import pytest
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import SteamshipError, Workspace
from steamship.base.request import SortOrder


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

    initial_workspace_ids = [
        w.id for w in Workspace.list(client, sort_order=SortOrder.ASC).workspaces
    ]

    workspace1 = Workspace.create(client=client)
    workspace2 = Workspace.create(client=client)
    workspace3 = Workspace.create(client=client)

    latest_workspace_ids = [w.id for w in Workspace.list(client).workspaces]
    assert workspace1.id not in initial_workspace_ids
    assert workspace2.id not in initial_workspace_ids
    assert workspace3.id not in initial_workspace_ids
    assert workspace1.id in latest_workspace_ids
    assert workspace2.id in latest_workspace_ids
    assert workspace3.id in latest_workspace_ids

    workspace1.delete()
    workspace2.delete()
    workspace3.delete()


def test_list_workspace_paging():
    client = get_steamship_client()

    orig_first_page_of_workspace_ids = [w.id for w in Workspace.list(client).workspaces]

    workspace1 = Workspace.create(client=client)
    workspace2 = Workspace.create(client=client)
    workspace3 = Workspace.create(client=client)

    assert workspace1.id not in orig_first_page_of_workspace_ids
    assert workspace2.id not in orig_first_page_of_workspace_ids
    assert workspace3.id not in orig_first_page_of_workspace_ids

    resp = Workspace.list(client, page_size=2)
    assert resp.next_page_token is not None

    updated_page_of_workspace_ids = [w.id for w in resp.workspaces]
    assert len(updated_page_of_workspace_ids) == 2
    assert workspace1.id not in updated_page_of_workspace_ids
    assert workspace2.id in updated_page_of_workspace_ids
    assert workspace3.id in updated_page_of_workspace_ids

    resp = Workspace.list(client, page_size=1, page_token=resp.next_page_token)
    final_page_of_workspace_ids = [w.id for w in resp.workspaces]
    assert len(final_page_of_workspace_ids) == 1
    assert workspace1.id in final_page_of_workspace_ids

    with pytest.raises(SteamshipError):
        Workspace.list(client, page_size=-1)

    workspace1.delete()
    workspace2.delete()
    workspace3.delete()
