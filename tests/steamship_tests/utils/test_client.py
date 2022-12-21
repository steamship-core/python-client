__copyright__ = "Steamship"
__license__ = "MIT"

from unittest.mock import patch

import pytest
from pydantic import ValidationError
from steamship_tests.utils.client import TESTING_PROFILE
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import Steamship
from steamship.base.client import Client
from steamship.base.configuration import DEFAULT_API_BASE, DEFAULT_APP_BASE, DEFAULT_WEB_BASE
from steamship.data.user import User


def test_get_steamship_client():
    client = get_steamship_client()
    assert client.config is not None
    assert client.config.profile == TESTING_PROFILE
    assert client.config.api_key is not None
    user = User.current(client)
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


def switch_workspace(
    self,
    workspace_handle: str = None,
    workspace_id: str = None,
    fail_if_workspace_exists: bool = False,
    trust_workspace_config: bool = False,
):
    pass


@pytest.mark.parametrize(("web_base", "app_base", "api_base"), empty_base_uris)
def test_base_uris(web_base: str, app_base: str, api_base: str) -> None:
    with patch.object(Client, "switch_workspace", switch_workspace):
        client = Steamship(api_base=api_base, web_base=web_base, app_base=app_base)
        assert str(client.config.web_base) == web_base or DEFAULT_WEB_BASE
        assert str(client.config.app_base) == app_base or DEFAULT_APP_BASE
        assert str(client.config.api_base) == api_base or DEFAULT_API_BASE


def test_incorrectly_formatted_base_uris() -> None:
    with patch.object(Client, "switch_workspace", switch_workspace):
        client = Steamship(
            api_base=TEST_API_BASE[:-1], web_base=TEST_WEB_BASE[:-1], app_base=TEST_APP_BASE[:-1]
        )
        assert str(client.config.web_base) == TEST_WEB_BASE
        assert str(client.config.app_base) == TEST_APP_BASE
        assert str(client.config.api_base) == TEST_API_BASE


@pytest.mark.parametrize("base_uri", ["", "test", "ftp://test.com"])
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
    with pytest.raises(ValidationError):
        Steamship(config=TestObject())


@pytest.mark.parametrize(
    ("app_base", "user", "fixed_base"),
    [
        pytest.param("http://test:8081", "user", "http://test:8081/"),
        pytest.param("http://test:8081/", "user", "http://test:8081/"),
        pytest.param("http://localhost:8081", "user", "http://localhost:8081/"),
        pytest.param("http://localhost:8081/", "user", "http://localhost:8081/"),
        pytest.param("http://127.0.0.1:8081", "user", "http://127.0.0.1:8081/"),
        pytest.param("http://127.0.0.1:8081/", "user", "http://127.0.0.1:8081/"),
        pytest.param(
            "http://host.docker.internal:8081", "user", "http://host.docker.internal:8081/"
        ),
        pytest.param(
            "http://host.docker.internal:8081/", "user", "http://host.docker.internal:8081/"
        ),
        pytest.param("http://0:0:0:0:8081", "user", "http://0:0:0:0:8081/"),
        pytest.param("http://0:0:0:0:8081/", "user", "http://0:0:0:0:8081/"),
        pytest.param("https://apps.steamship.run", "user", "https://user.apps.steamship.run/"),
        pytest.param("https://apps.steamship.run/", "user", "https://user.apps.steamship.run/"),
        pytest.param(
            "https://apps.staging.steamship.com", "user", "https://user.apps.staging.steamship.com/"
        ),
        pytest.param(
            "https://apps.staging.steamship.com/",
            "user",
            "https://user.apps.staging.steamship.com/",
        ),
    ],
)
def test_invocable_call_rewriting(app_base: str, user: str, fixed_base: str):
    client = get_steamship_client()
    client.config.app_base = app_base
    operation = "foo"

    output_url = client._url(is_package_call=True, package_owner=user, operation=operation)
    assert output_url == f"{fixed_base}{operation}"
