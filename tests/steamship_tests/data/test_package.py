import pytest
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import Package, Steamship


@pytest.mark.usefixtures("client")
def test_package_create(client: Steamship):
    client = get_steamship_client()
    _ = Package.create(client)
