import pytest
from steamship_tests.utils.fixtures import get_steamship_client
from steamship_tests.utils.random import random_name

from steamship import Space, SteamshipError
from steamship.data.user import User


def test_connect():
    """Test basic connection"""
    client = get_steamship_client()
    assert client.config is not None
    assert client.config.profile == "test"
    assert client.config.api_key is not None


def test_user():
    client = get_steamship_client()
    user = User.current(client).data
    assert user.id is not None
    assert user.handle is not None


def test_client_creation_with_new_autogen_space():
    client1 = get_steamship_client(create_space=True)
    client2 = get_steamship_client()
    client3 = get_steamship_client()

    assert client2.config.space_id is None
    assert client2.config.space_handle is None
    assert client3.config.space_id is None
    assert client3.config.space_handle is None

    assert client1.config.space_id is not None
    assert client1.config.space_handle is not None

    Space(client=client1, id=client1.config.space_id).delete()


def test_client_creation_space_failure_modes():
    # Can't create a space by specifying an ID
    with pytest.raises(SteamshipError):
        get_steamship_client(space_id="foo", create_space=True)

    client1 = get_steamship_client(create_space=True)

    # Can't create a space with a handle that already exists
    with pytest.raises(SteamshipError):
        get_steamship_client(space_handle=client1.config.space_handle, create_space=True)

    Space(client=client1, id=client1.config.space_id).delete()


def test_client_creation_new_space_custom_handle():
    name = random_name().lower()
    client1 = get_steamship_client(space_handle=name, create_space=True)

    assert client1.config.space_id is not None
    assert client1.config.space_handle == name

    Space(client=client1, id=client1.config.space_id).delete()


def test_client_creation_recall_existing_space():
    client1 = get_steamship_client(create_space=True)
    client2 = get_steamship_client(space_id=client1.config.space_id)
    client3 = get_steamship_client(space_handle=client1.config.space_handle)

    assert client1.config.space_id == client2.config.space_id
    assert client1.config.space_id == client3.config.space_id
    assert client1.config.space_handle == client2.config.space_handle
    assert client1.config.space_handle == client3.config.space_handle

    Space(client=client1, id=client1.config.space_id).delete()
