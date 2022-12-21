import pytest
from pydantic import ValidationError

from steamship import Configuration, SteamshipError
from steamship.base.configuration import DEFAULT_API_BASE, DEFAULT_APP_BASE, DEFAULT_WEB_BASE

TEST_WEB_BASE = "https://app.test.com/"
TEST_APP_BASE = "https://test.run/"
TEST_API_BASE = "https://api.test.com/api/v1/"

empty_base_uris = [
    (TEST_WEB_BASE, TEST_APP_BASE, TEST_API_BASE),
    (None, TEST_APP_BASE, TEST_API_BASE),
    (TEST_WEB_BASE, None, TEST_API_BASE),
    (TEST_WEB_BASE, TEST_APP_BASE, None),
]


@pytest.mark.parametrize(("web_base", "app_base", "api_base"), empty_base_uris)
def test_base_uris(web_base: str, app_base: str, api_base: str) -> None:
    configuration = Configuration(api_base=api_base, web_base=web_base, app_base=app_base)
    assert str(configuration.web_base) == web_base or DEFAULT_WEB_BASE
    assert str(configuration.app_base) == app_base or DEFAULT_APP_BASE
    assert str(configuration.api_base) == api_base or DEFAULT_API_BASE


def test_incorrectly_formatted_base_uris() -> None:
    configuration = Configuration(
        api_base=TEST_API_BASE[:-1], web_base=TEST_WEB_BASE[:-1], app_base=TEST_APP_BASE[:-1]
    )
    assert str(configuration.web_base) == TEST_WEB_BASE
    assert str(configuration.app_base) == TEST_APP_BASE
    assert str(configuration.api_base) == TEST_API_BASE


@pytest.mark.parametrize("base_uri", ["", "test", "ftp://test.com"])
def test_invalid_base_uris(base_uri: str) -> None:
    with pytest.raises(ValidationError):
        Configuration(api_base=base_uri, web_base=base_uri, app_base=base_uri)


def test_empty_base_uris() -> None:
    configuration = Configuration()
    assert configuration.web_base is not None
    assert configuration.app_base is not None
    assert configuration.api_base is not None


@pytest.mark.xfail()
def test_empty_api_key() -> None:
    with pytest.raises(SteamshipError):
        # Note: We're referencing a non existing profile to make sure the api key is not loaded from the default profile in steamship.json
        Configuration(api_key=None, profile="non-existing-profile")
