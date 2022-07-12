__copyright__ = "Steamship"
__license__ = "MIT"

import pytest

from steamship import Configuration
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


@pytest.mark.parametrize(
    "app_base,user,fixed_base",
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
def test_app_call_rewriting(app_base: str, user: str, fixed_base: str):
    client = get_steamship_client()

    OPERATION = "foo"

    config = Configuration(app_base=app_base)
    output_url = client._url(app_call=True, app_owner=user, operation=OPERATION, config=config)
    assert output_url == f"{fixed_base}{OPERATION}"
