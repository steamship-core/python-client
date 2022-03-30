from steamship import Space

from tests.client.helpers import _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


def test_default_space():
    client = _steamship()
    space = Space.get(client=client).data
    assert (space is not None)
    assert (space.handle == 'default')


def test_delete_space():
    client = _steamship()
    default = Space.get(client=client).data
    space1 = Space.create(client=client, name="Test", handle="test").data
    assert (default.id is not None)
    assert (space1.id is not None)
    assert (default.id != space1.id)

    space1.delete()
    space1a = Space.get(client=client, spaceId=space1.id)
    assert (space1a.data is None)
    assert (space1a.error is not None)

    space1 = Space.create(client=client, name="Test", handle="test").data
    assert (default.id is not None)
    assert (space1.id is not None)
    assert (default.id != space1.id)

    space1a = Space.get(client=client, spaceId=space1.id)
    assert (space1a.data is not None)
    assert (space1a.error is None)

    space1.delete()
    space1a = Space.get(client=client, spaceId=space1.id)
    assert (space1a.data is None)
    assert (space1a.error is not None)


def test_get_space():
    client = _steamship()
    default = Space.get(client=client).data
    space1 = Space.create(client=client, name="Test", handle="test").data
    space1a = Space.get(client=client, spaceId=space1.id).data
    assert (space1a.id == space1.id)
    assert (space1a.id != default.id)
    assert (space1a.handle == space1.handle)


def test_create_use_delete_space():
    client = _steamship()
    default = Space.get(client=client).data
    space1 = Space.create(client=client, name="Test", handle="test").data
    space2 = Space.create(client=client, name="Test", handle="test2").data

    assert (space1 is not None)
    assert (space1.handle == 'test')

    assert (space2 is not None)
    assert (space2.handle == 'test2')

    assert (space2.id != space1.id)
    assert (space1.id != default.id)
    assert (space2.id != default.id)

    space1a = Space.get(client=client, spaceId=space1.id).data
    space1b = Space.get(client=client, spaceHandle=space1.handle).data
    space1c = Space.get(client=client, space=space1).data

    assert (space1.id == space1a.id)
    assert (space1.id == space1b.id)
    assert (space1.id == space1c.id)

    space1ad = space1a.delete()
    assert (space1ad.data is not None)
    assert (space1ad.error is None)

    # These two are the same space! You can't delete twice!
    space1bd = space1b.delete()
    assert (space1bd.data is None)
    assert (space1bd.error is not None)
    space1cd = space1c.delete()
    assert (space1cd.data is None)
    assert (space1cd.error is not None)

    space2.delete()

    space1a_deleted = Space.get(client=client, spaceId=space1.id)
    assert (space1a_deleted.data is None)
    assert (space1a_deleted.error is not None)
