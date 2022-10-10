import pytest
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import Space, SteamshipError


def test_default_space():
    client = get_steamship_client()
    space = Space.get(client=client)
    assert space is not None
    assert space.handle == "default"


def test_delete_space():
    client = get_steamship_client()
    default = Space.get(client=client)
    space1 = Space.create(client=client, handle="test")
    assert default.id is not None
    assert space1.id is not None
    assert default.id != space1.id

    space1.delete()
    with pytest.raises(SteamshipError):
        _ = Space.get(client=client, id_=space1.id)

    space1 = Space.create(client=client, handle="test")
    assert default.id is not None
    assert space1.id is not None
    assert default.id != space1.id

    space1a = Space.get(client=client, id_=space1.id)
    assert space1a is not None

    space1.delete()
    with pytest.raises(SteamshipError):
        _ = Space.get(client=client, id_=space1.id)


def test_get_space():
    client = get_steamship_client()
    default = Space.get(client=client)
    space1 = Space.create(client=client, handle="test")
    space1a = Space.get(client=client, id_=space1.id)
    assert space1a.id == space1.id
    assert space1a.id != default.id
    assert space1a.handle == space1.handle

    space1b = Space.get(client=client, handle=space1.handle)
    assert space1b.id == space1.id
    assert space1b.handle == space1.handle

    space1c = Space.get(client=client, id_=space1.id, handle=space1.handle)
    assert space1c.id == space1.id
    assert space1c.handle == space1.handle

    space1.delete()


def test_create_use_delete_space():
    client = get_steamship_client()
    default = Space.get(client=client)
    space1 = Space.create(client=client, handle="test")
    space2 = Space.create(client=client, handle="test2")

    assert space1 is not None
    assert space1.handle == "test"

    assert space2 is not None
    assert space2.handle == "test2"

    assert space2.id != space1.id
    assert space1.id != default.id
    assert space2.id != default.id

    space1a = Space.get(client=client, id_=space1.id)
    space1b = Space.get(client=client, handle=space1.handle)
    space1c = Space.get(client=client, id_=space1.id)

    assert space1.id == space1a.id
    assert space1.id == space1b.id
    assert space1.id == space1c.id

    space1a.delete()

    # These two are the same space! You can't delete twice!
    with pytest.raises(SteamshipError):
        space1b.delete()

    with pytest.raises(SteamshipError):
        space1c.delete()

    space2.delete()
    with pytest.raises(SteamshipError):
        _ = Space.get(client=client, id_=space1.id)
