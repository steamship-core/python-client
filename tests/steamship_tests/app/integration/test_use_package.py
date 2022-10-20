import pytest
from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.client import steamship_use
from steamship_tests.utils.deployables import deploy_package
from steamship_tests.utils.fixtures import get_steamship_client
from steamship_tests.utils.random import random_name

from steamship import SteamshipError


def test_use_package():
    client = get_steamship_client()
    demo_package_path = PACKAGES_PATH / "demo_package.py"

    with deploy_package(client, demo_package_path) as (package, version, instance):
        # Test for infinite recursion bug
        assert package.__repr__()

        # Now let's invoke it!
        # Note: we're invoking the data at demo_package.py in the tests/assets/packages folder
        package_handle_1 = random_name()
        package_handle_2 = random_name()

        with steamship_use(package.handle, package_handle_1) as static_use_instance1:
            with steamship_use(package.handle, package_handle_2) as static_use_instance2:
                # Instance 1 and 2 have handles equal to their space handles
                assert (
                    static_use_instance1.client.config.space_handle == static_use_instance1.handle
                )
                assert static_use_instance1.client.config.space_id == static_use_instance1.space_id
                assert (
                    static_use_instance2.client.config.space_handle == static_use_instance2.handle
                )
                assert static_use_instance2.client.config.space_id == static_use_instance2.space_id

                # Instance 1 and 2 are in different spaces
                assert static_use_instance1.space_id != static_use_instance2.space_id
                assert static_use_instance1.space_id != static_use_instance2.space_id

                # And neither one of these is the default space
                assert static_use_instance1.space_id != client.config.space_id
                assert static_use_instance2.space_id != client.config.space_id
                assert static_use_instance1.client.config.space_handle != "default"
                assert static_use_instance2.client.config.space_handle != "default"

                # And they are in the requested spaces
                assert static_use_instance1.client.config.space_handle == package_handle_1
                assert static_use_instance2.client.config.space_handle == package_handle_2

            # We can also bring up a second instance of the same invocable
            with steamship_use(
                package.handle, package_handle_1, delete_space=False
            ) as static_use_instance1a:
                assert (
                    static_use_instance1a.client.config.space_handle == static_use_instance1a.handle
                )
                assert (
                    static_use_instance1a.client.config.space_id == static_use_instance1a.space_id
                )
                assert static_use_instance1a.space_id == static_use_instance1.space_id
                # And the handle is the same
                assert (
                    static_use_instance1a.handle == static_use_instance1.handle
                )  # It's the same instance (handle)
                assert (
                    static_use_instance1a.id == static_use_instance1.id
                )  # It's the same instance (id)

            # Or we could have (1) created a client anchored to the Workspace `package_handle_1` and then
            # (2) Loaded that handle from within the client.
            client2 = get_steamship_client(workspace=package_handle_1)
            assert client2.config.space_handle == package_handle_1
            assert client2.config.space_id == static_use_instance1.space_id

            static_use_instance1a = client2.use(package.handle, package_handle_1)
            assert (
                static_use_instance1a.client.config.space_handle == static_use_instance1a.handle
            )  # The client is in the same space (handle)!
            assert (
                static_use_instance1a.client.config.space_id == static_use_instance1a.space_id
            )  # The client is in the same space (id)!
            assert (
                static_use_instance1a.space_id == static_use_instance1.space_id
            )  # It's in the same space!
            # And the handle is the same
            assert (
                static_use_instance1a.handle == static_use_instance1.handle
            )  # It's the same instance! (handle)
            assert (
                static_use_instance1a.id == static_use_instance1.id
            )  # It's the same instance! (id)

            # And here's the potentially hazardous thing that's possible:
            # You can use a client's member function `use` to create a second instance of that package that shares the
            # same space as the first, meaning it implicitly shares data.
            #
            # This is potentially useful, so it's not clear we want to forbid it (e.g. package1 could tag data, and
            # package2 could query data). But we want to encourage `Steamship.use` over `client.use` for basic use
            # due to the easier to understand scope semantics.
            package_handle_1b = random_name()
            static_use_instance1b = client2.use(package.handle, package_handle_1b)
            assert static_use_instance1b.client.config.space_handle == static_use_instance1.handle
            assert static_use_instance1b.client.config.space_id == static_use_instance1.space_id
            assert static_use_instance1b.space_id == static_use_instance1.space_id
            # But the handle isn't the same
            assert static_use_instance1b.handle != static_use_instance1.handle
            assert static_use_instance1b.id != static_use_instance1.id


def test_use_plugin_fails_with_same_instance_name_but_different_plugin_name():
    client = get_steamship_client()

    instance_handle = random_name()

    demo_app_path = PACKAGES_PATH / "demo_app.py"

    with deploy_package(client, demo_app_path) as (app, version, instance):
        with deploy_package(client, demo_app_path) as (app2, version2, instance2):
            client.use_plugin(app.handle, instance_handle)

            # Should fail because we're using the shortcut `import_plugin` method with the same instance
            with pytest.raises(SteamshipError):
                client.use_plugin(app2.handle, instance_handle)
