from steamship.data.user import User

from .helpers import _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


def test_connect():
    """Test basic connection"""
    client = _steamship()
    assert (client.config is not None)
    assert (client.config.profile == "test")
    assert (client.config.apiKey is not None)


def test_user():
    client = _steamship()
    user = User.current(client).data
    assert (user.id is not None)
    assert (user.handle is not None)
