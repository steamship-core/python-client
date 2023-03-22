from time import sleep

from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.client import TESTING_PROFILE
from steamship_tests.utils.deployables import deploy_package

from steamship import Steamship


def test_instance_init_is_called():
    demo_package_path = PACKAGES_PATH / "package_verifying_instance_init.py"

    with Steamship.temporary_workspace(profile=TESTING_PROFILE) as client:
        with deploy_package(client, demo_package_path) as (_, _, instance):
            sleep(5)  # for now, just wait out the init
            invocation_url = instance.invoke("was_init_called")
            assert invocation_url == instance.invocation_url
