from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package
from steamship_tests.utils.fixtures import get_steamship_client


def test_returns_list():

    client = get_steamship_client()
    demo_package_path = PACKAGES_PATH / "returns_list.py"

    with deploy_package(client, demo_package_path) as (_, _, instance):
        response = instance.invoke("gimme_a_list")
        assert response is not None
        assert len(response) == 3
        assert response == ["here's", "a", "list"]
