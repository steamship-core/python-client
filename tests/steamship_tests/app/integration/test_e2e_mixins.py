import pytest
from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package

from steamship import Steamship


@pytest.mark.usefixtures("client")
def test_mixin_and_package_invocation(client: Steamship):
    demo_package_path = PACKAGES_PATH / "package_with_mixins.py"

    with deploy_package(client, demo_package_path) as (_, _, instance):
        mixin_response = instance.invoke("test_mixin_route", text="test")
        assert mixin_response == "mixin yo"

        package_response = instance.invoke("test_package_route")
        assert package_response == "package"
