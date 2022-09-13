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


def test_client_has_default_space_unless_otherwise_specified():
    client1 = get_steamship_client()
    assert client1.config.space_handle == "default"


def test_client_can_create_new_workspace():
    # Create a new workspace anchored in a randomly generated workspace name
    space_handle = random_name()
    custom_client = get_steamship_client(workspace=space_handle)

    # The custom_client is not in the default workspace
    default_client = get_steamship_client()
    assert custom_client.config.space_handle == space_handle
    assert custom_client.config.space_id != default_client.config.space_id

    # Another client specifying the same workspace will be anchored to that workspace.
    custom_client_2 = get_steamship_client(workspace=space_handle)
    assert custom_client.config.space_handle == custom_client_2.config.space_handle
    assert custom_client.config.space_id == custom_client_2.config.space_id

    # .. But if we specify that workspace with the `fail_if_workspace_exists` option it will fail.
    with pytest.raises(SteamshipError):
        get_steamship_client(
            workspace=custom_client.config.space_handle, fail_if_workspace_exists=True
        )

    Space(client=custom_client, id=custom_client.config.space_id).delete()


def test_switch_workspace():
    """Tests that the client actively loads the default space ID and Handle, and that we can revert to it later."""
    default_client = get_steamship_client()
    custom_client = get_steamship_client(workspace=random_name())
    custom_client_2 = get_steamship_client(workspace=custom_client.config.space_handle)

    assert custom_client.config.space_handle != default_client.config.space_handle
    assert custom_client_2.config.space_handle == custom_client.config.space_handle
    assert default_client.config.space_handle == "default"

    # Switch custom_client_2 to the default
    custom_client_2.switch_workspace()
    assert custom_client_2.config.space_handle == default_client.config.space_handle
    assert custom_client_2.config.space_id == default_client.config.space_id

    # Switch default_space to the custom_clientt
    default_client.switch_workspace(workspace=custom_client.config.space_handle)
    assert custom_client.config.space_handle == default_client.config.space_handle
    assert custom_client.config.space_id == default_client.config.space_id

    # client2 has the newly created space.
    Space(client=custom_client, id=custom_client.config.space_id).delete()
