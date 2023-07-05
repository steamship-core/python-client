import pytest

from steamship import Package, Steamship, SteamshipError


@pytest.mark.usefixtures("client")
def test_package_create(client: Steamship):
    _ = Package.create(client)


@pytest.mark.usefixtures("client")
def test_plugin_delete(client: Steamship):

    package = Package.create(
        client=client,
        is_public=False,
    )

    assert package is not None

    package.delete()

    # Validate plugin is gone
    with pytest.raises(SteamshipError):
        _ = Package.get(client, handle=package.handle)
