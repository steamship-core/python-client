from steamship_tests import APPS_PATH
from steamship_tests.utils.deployables import zip_deployable
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import Package, PackageVersion


def test_version_create():
    client = get_steamship_client()
    demo_app_path = APPS_PATH / "demo_app.py"

    app = Package.create(client)
    zip_bytes = zip_deployable(demo_app_path)

    version = PackageVersion.create(client, package_id=app.id, filebytes=zip_bytes)

    version.wait()
