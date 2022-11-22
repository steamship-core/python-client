from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package
from steamship_tests.utils.fixtures import get_steamship_client


def test_safe_loaded_hello_world():

    client = get_steamship_client()
    demo_package_path = PACKAGES_PATH / "safe_loaded_hello_world.py"

    with deploy_package(client, demo_package_path) as (_, _, instance):
        response = instance.invoke("greet")
        assert response is not None
        assert response == "Hello, Person"
