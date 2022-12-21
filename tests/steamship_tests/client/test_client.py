import pytest
from steamship_tests.utils.client import TESTING_PROFILE
from steamship_tests.utils.fixtures import get_steamship_client
from steamship_tests.utils.random import random_name

from steamship import SteamshipError, Workspace
from steamship.data.user import User


def test_connect():
    """Test basic connection"""
    client = get_steamship_client()
    assert client.config is not None
    assert client.config.profile == TESTING_PROFILE
    assert client.config.api_key is not None


def test_user():
    client = get_steamship_client()
    user = User.current(client)
    assert user.id is not None
    assert user.handle is not None


def test_client_has_default_workspace_unless_otherwise_specified():
    client1 = get_steamship_client()
    assert client1.config.workspace_handle == "default"


def test_client_can_create_new_workspace():
    # Create a new workspace anchored in a randomly generated workspace name
    workspace_handle = random_name()
    custom_client = get_steamship_client(workspace_handle=workspace_handle)

    # The custom_client is not in the default workspace
    default_client = get_steamship_client()
    assert custom_client.config.workspace_handle == workspace_handle
    assert custom_client.config.workspace_id != default_client.config.workspace_id

    # Another client specifying the same workspace will be anchored to that workspace.
    custom_client_2 = get_steamship_client(workspace_handle=workspace_handle)
    assert custom_client.config.workspace_handle == custom_client_2.config.workspace_handle
    assert custom_client.config.workspace_id == custom_client_2.config.workspace_id

    # .. But if we specify that workspace with the `fail_if_workspace_exists` option it will fail.
    with pytest.raises(SteamshipError):
        get_steamship_client(
            workspace_handle=custom_client.config.workspace_handle, fail_if_workspace_exists=True
        )

    Workspace(client=custom_client, id=custom_client.config.workspace_id).delete()


def test_switch_workspace():
    """Tests that the client actively loads the default workspace ID and Handle, and that we can revert to it later."""
    default_client = get_steamship_client()
    custom_client = get_steamship_client(workspace_handle=random_name())
    custom_client_2 = get_steamship_client(workspace_handle=custom_client.config.workspace_handle)

    assert custom_client.config.workspace_handle != default_client.config.workspace_handle
    assert custom_client_2.config.workspace_handle == custom_client.config.workspace_handle
    assert default_client.config.workspace_handle == "default"

    # Switch custom_client_2 to the default
    custom_client_2.switch_workspace()
    assert custom_client_2.config.workspace_handle == default_client.config.workspace_handle
    assert custom_client_2.config.workspace_id == default_client.config.workspace_id

    # Switch default_workspace to the custom_client
    default_client.switch_workspace(workspace_handle=custom_client.config.workspace_handle)
    assert custom_client.config.workspace_handle == default_client.config.workspace_handle
    assert custom_client.config.workspace_id == default_client.config.workspace_id

    # client2 has the newly created workspace.
    Workspace(client=custom_client, id=custom_client.config.workspace_id).delete()
