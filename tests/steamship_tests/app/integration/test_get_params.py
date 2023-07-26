import pytest
from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package

from steamship import Steamship
from steamship.utils.url import Verb


@pytest.mark.usefixtures("client")
def test_get_param_decoding(client: Steamship):
    demo_package_path = PACKAGES_PATH / "demo_package.py"

    with deploy_package(client, demo_package_path) as (package, version, instance):
        result = instance.invoke("greet", verb=Verb.GET, name="A test with spaces")
        assert result == "Hello, A test with spaces!"
