import json
from typing import List

import pytest
from steamship_tests import TEST_ASSETS_PATH
from steamship_tests.utils.deployables import zip_deployable

from steamship import Package, PackageInstance, PackageVersion, Steamship, SteamshipError
from steamship.data.package.package_version import CreatePackageVersionRequest
from steamship.utils.url import Verb


@pytest.mark.usefixtures("client")
def test_install_two_packages_at_once(client: Steamship):

    pillow_version_task = create_version(client, additional_requirements=["pillow"])
    pandas_version_task = create_version(client, additional_requirements=["pandas"])

    pillow_version = pillow_version_task.wait()
    pandas_version = pandas_version_task.wait()

    pillow_instance = PackageInstance.create(
        client, package_id=pillow_version.package_id, package_version_id=pillow_version.id
    )
    pandas_instance = PackageInstance.create(
        client, package_id=pandas_version.package_id, package_version_id=pandas_version.id
    )

    # Pillow version should be able to run the method that imports pillow locally
    assert pillow_instance.invoke("try_pillow", verb=Verb.GET) == "PIL"

    # Pillow version should NOT be able to run the method that imports pandas locally
    with pytest.raises(SteamshipError):
        _ = pillow_instance.invoke("try_pandas", verb=Verb.GET)

    # Pandas version should be able to run the method that imports pandas locally
    assert pandas_instance.invoke("try_pandas", verb=Verb.GET) == "pandas"

    # Pandas version should NOT be able to run the method that imports pillow locally
    with pytest.raises(SteamshipError):
        _ = pandas_instance.invoke("try_pillow", verb=Verb.GET)

    pillow_version.delete()
    pandas_version.delete()


def create_version(client: Steamship, additional_requirements: List[str]):
    """Separate implementation of create version so that we can not wait on the task, and run multiple at once."""
    package = Package.create(client)

    zip_bytes = zip_deployable(
        TEST_ASSETS_PATH / "packages" / "requirement_isolation_package.py",
        additional_requirements=additional_requirements,
    )
    hosting_handler = "steamship.invocable.entrypoint.safe_handler"

    req = CreatePackageVersionRequest(
        handle="handle",
        package_id=package.id,
        config_template=json.dumps({}),
        hosting_handler=hosting_handler,
    )

    task = client.post(
        "package/version/create",
        payload=req,
        file=("package.zip", zip_bytes, "multipart/form-data"),
        expect=PackageVersion,
    )
    return task
