from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import File


def test_importer_mixin_and_package_invocation():

    client = get_steamship_client()
    demo_package_path = PACKAGES_PATH / "package_with_mixin_importer.py"

    with deploy_package(client, demo_package_path) as (_, _, instance):
        mixin_response = instance.invoke("import_url", url="https://www.google.com/")
        assert mixin_response
        file_id = mixin_response.get("id")
        assert file_id
        file = File.get(client, _id=file_id)
        content = file.raw()
        assert content
