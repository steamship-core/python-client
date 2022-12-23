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

    package_path = PACKAGES_PATH / "demo_package.py"

    with deploy_package(client, package_path) as (app, version, instance):
        with deploy_package(client, package_path) as (app2, version2, instance2):
            client.use(app.handle, instance_handle)

            # Should fail because we're using the shortcut `import_plugin` method with the same instance
            with pytest.raises(SteamshipError):
                client.use(app2.handle, instance_handle)

            # setting recreate = True should fix things
            client.use_plugin(app2.handle, instance_handle=instance_handle, recreate=True)


def test_use_plugin_recreate():
    client = get_steamship_client()
    package_path = PACKAGES_PATH / "demo_package.py"
    with deploy_package(client, package_path) as (
        app,
        version,
        instance,
    ):
        client.use(app.handle)

        # re-creating the same plugin with fetch_if_exists = True should not fail
        client.use(app.handle)

        # re-creating the same plugin_handle and plugin_version_handle should fail
        with pytest.raises(SteamshipError):
            client.use(app.handle, fetch_if_exists=False)

        # setting recreate = True should fix things
        client.use(app.handle, recreate=True, fetch_if_exists=False)

        instance_handle = random_name()
        client.use(app.handle, instance_handle=instance_handle)

        # re-creating the same app_handle and app_version_handle with the same instance_handle should fail
        with pytest.raises(SteamshipError):
            client.use(app.handle, instance_handle=instance_handle, fetch_if_exists=False)

        # setting recreate = True should fix things
        client.use(
            app.handle, instance_handle=instance_handle, recreate=True, fetch_if_exists=False
        )

        # using a difference instance_handle fixes things
        new_instance_handle = random_name()
        client.use(app.handle, instance_handle=new_instance_handle)

        # calling recreate on an new instance handle should not fail
        new_instance_handle = random_name()
        client.use(app.handle, instance_handle=new_instance_handle, recreate=True)
