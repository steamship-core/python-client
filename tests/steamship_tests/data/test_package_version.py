from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import zip_deployable
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import Package, PackageVersion


def test_version_create():
    client = get_steamship_client()
    demo_package_path = PACKAGES_PATH / "demo_package.py"

    package = Package.create(client)
    zip_bytes = zip_deployable(demo_package_path)

    version = PackageVersion.create(client, package_id=package.id, filebytes=zip_bytes)

    assert version is not None
