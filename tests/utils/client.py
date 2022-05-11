from steamship import Steamship
from steamship.data.user import User


def get_steamship_client() -> Steamship:
    # TODO: The asserts do not have to be run every time
    # This should automatically pick up variables from the environment.
    client = Steamship(profile="test")
    assert client.config is not None
    assert client.config.profile == "test"
    assert client.config.api_key is not None
    user = User.current(client).data
    assert user.id is not None
    assert user.handle is not None
    return client
