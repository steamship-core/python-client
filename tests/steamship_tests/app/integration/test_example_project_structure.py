from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package
from steamship_tests.utils.fixtures import get_steamship_client

from steamship.utils.url import Verb


def test_example_project_structure():

    client = get_steamship_client()
    demo_package_path = PACKAGES_PATH / "example_project_structure.py"

    with deploy_package(client, demo_package_path) as (_, _, instance):
        response = instance.invoke("say_hello", verb=Verb.GET)
        assert response is not None
        assert response == "Hello, None"

        response = instance.invoke("say_hello", verb=Verb.GET, name="Testy")
        assert response is not None
        assert response == "Hello, Testy"

        response = instance.invoke("do_something")
        assert response is not None
        assert response == {"number": None}

        response = instance.invoke("do_something", number=3)
        assert response is not None
        assert response == {"number": 3}
