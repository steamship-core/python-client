from steamship.data.user import User
from tests.utils.fixtures import get_steamship_client


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
