__copyright__ = "Steamship"
__license__ = "MIT"

from steamship.data.user import User
from tests.utils.fixtures import get_steamship_client


def test_get_steamship_client():
    client = get_steamship_client()
    assert client.config is not None
    assert client.config.profile == "test"
    assert client.config.api_key is not None
    user = User.current(client).data
    assert user.id is not None
    assert user.handle is not None
