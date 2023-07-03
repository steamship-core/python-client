from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package
from steamship_tests.utils.fixtures import get_steamship_client


def test_adding_configuration():
    """NOTE: Any changes to the package under test need to be reflected in the paired documentation pages!"""

    client = get_steamship_client()
    demo_package_path = PACKAGES_PATH / "adding_configuration.py"
    config_template = {
        "name": {"type": "string"},
        "favoriteColor": {"type": "string"},
        "luckyNumber": {"type": "number"},
        "favoriteTrueFalseValue": {"type": "boolean"},
    }
    instance_config = {
        "name": "Shaggy",
        "favoriteColor": "avocado green",
        "luckyNumber": 42,
        "favoriteTrueFalseValue": True,
    }

    with deploy_package(
        client,
        demo_package_path,
        version_config_template=config_template,
        instance_config=instance_config,
    ) as (_, _, instance):
        response = instance.invoke("my_faves")
        assert response is not None
        assert (
            response
            == """
        Hey Shaggy!
        I can remind you of your favorites.
        Your favorite color is avocado green.
        Your lucky number is 42.0.
        Your favorite true/false value is True.
        Wow, mine too!
        """
        )
