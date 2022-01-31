from .helpers import _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


def test_connect():
    """Test basic connection"""
    client = _steamship()
    assert (client.config is not None)
    assert (client.config.profile == "test")
    assert (client.config.apiKey is not None)
