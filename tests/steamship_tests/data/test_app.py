from steamship_tests.utils.fixtures import get_steamship_client

from steamship import App


def test_app_create():
    client = get_steamship_client()
    _ = App.create(client)
