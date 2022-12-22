import pytest
from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package
from steamship_tests.utils.fixtures import get_steamship_client
from steamship_tests.utils.random import random_name

from steamship import SteamshipError


def test_use_package():
    client = get_steamship_client()
    demo_package_path = PACKAGES_PATH / "demo_package.py"

    workspace_handle = random_name()
    client.switch_workspace(workspace_handle=workspace_handle)
    with deploy_package(client, demo_package_path) as (package, version, instance):
        # Test for infinite recursion bug
        assert package.__repr__()

        assert instance.client.config.workspace_handle == workspace_handle


def test_use_package_fails_with_same_instance_name_but_different_package_name():
    client = get_steamship_client()

    instance_handle = random_name()

    demo_package_path = PACKAGES_PATH / "demo_package.py"

    with deploy_package(client, demo_package_path) as (app, version, instance):
        with deploy_package(client, demo_package_path) as (app2, version2, instance2):
            client.use(app.handle, instance_handle)

            # Should fail because we're using the shortcut `import_plugin` method with the same instance
            with pytest.raises(SteamshipError):
                client.use(app2.handle, instance_handle)
