from steamship_tests.utils.fixtures import get_steamship_client

from steamship import Package


def test_app_create():
    client = get_steamship_client()
    _ = Package.create(client)
