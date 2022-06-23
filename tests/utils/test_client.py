__copyright__ = "Steamship"
__license__ = "MIT"

import pytest
from pydantic import ValidationError

from steamship import Steamship, SteamshipError
from steamship.base.configuration import DEFAULT_API_BASE, DEFAULT_APP_BASE, DEFAULT_WEB_BASE
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


TEST_WEB_BASE = "https://app.test.com/"
TEST_APP_BASE = "https://test.run/"
TEST_API_BASE = "https://api.test.com/api/v1/"

empty_base_uris = [
    (TEST_WEB_BASE, TEST_APP_BASE, TEST_API_BASE),
    (None, TEST_APP_BASE, TEST_API_BASE),
    (TEST_WEB_BASE, None, TEST_API_BASE),
    (TEST_WEB_BASE, TEST_APP_BASE, None),
]


@pytest.mark.parametrize("web_base,app_base,api_base", empty_base_uris)
def test_base_uris(web_base: str, app_base: str, api_base: str) -> None:
    client = Steamship(api_base=api_base, web_base=web_base, app_base=app_base)
    assert str(client.config.web_base) == web_base or DEFAULT_WEB_BASE
    assert str(client.config.app_base) == app_base or DEFAULT_APP_BASE
    assert str(client.config.api_base) == api_base or DEFAULT_API_BASE


def test_incorrectly_formatted_base_uris() -> None:
    client = Steamship(
        api_base=TEST_API_BASE[:-1], web_base=TEST_WEB_BASE[:-1], app_base=TEST_APP_BASE[:-1]
    )
    assert str(client.config.web_base) == TEST_WEB_BASE
    assert str(client.config.app_base) == TEST_APP_BASE
    assert str(client.config.api_base) == TEST_API_BASE


@pytest.mark.parametrize("base_uri", ("", "test", "ftp://test.com"))
def test_invalid_base_uris(base_uri: str) -> None:
    with pytest.raises(ValidationError):
        Steamship(api_base=base_uri, web_base=base_uri, app_base=base_uri)


def test_empty_config() -> None:
    client = Steamship()
    assert client.config is not None
    assert client.config.web_base is not None
    assert client.config.app_base is not None
    assert client.config.api_base is not None


def test_none_config() -> None:
    client = Steamship(config=None)
    assert client.config is not None
    assert client.config.web_base is not None
    assert client.config.app_base is not None
    assert client.config.api_base is not None


class TestObject:
    pass


def test_incorrect_config_type() -> None:
    with pytest.raises(SteamshipError):
        client = Steamship(config=TestObject())
