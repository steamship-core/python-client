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

        # Test that without specifying an instance handle, the user is delivered into a workspace called
        # packageHandle-default and delivered an instance called workspaceHandle-default
        #
        # These are the same semantics as workspaces: if you don't specify, you get taken to a `default` space,
        # but in this case we need to prefix with the type to avoid namespace collision within the space.
        with steamship_use(package.handle) as static_use_instance1:
            with steamship_use(package.handle, delete_workspace=False) as static_use_instance2:
                assert (
                    static_use_instance1.client.config.workspace_handle
                    == static_use_instance2.client.config.workspace_handle
                )
                assert static_use_instance1.handle == static_use_instance2.handle
                assert static_use_instance1.client.config.workspace_handle == package.handle
                assert static_use_instance1.handle == package.handle

        with steamship_use(package.handle, package_handle_1) as static_use_instance1:
            with steamship_use(package.handle, package_handle_2) as static_use_instance2:
                # Instance 1 and 2 have handles equal to their workspace handles
                assert (
                    static_use_instance1.client.config.workspace_handle
                    == static_use_instance1.handle
                )
                assert (
                    static_use_instance1.client.config.workspace_id
                    == static_use_instance1.workspace_id
                )
                assert (
                    static_use_instance2.client.config.workspace_handle
                    == static_use_instance2.handle
                )
                assert (
                    static_use_instance2.client.config.workspace_id
                    == static_use_instance2.workspace_id
                )

                # Instance 1 and 2 are in different workspaces
                assert static_use_instance1.workspace_id != static_use_instance2.workspace_id
                assert static_use_instance1.workspace_id != static_use_instance2.workspace_id

                # And neither one of these is the default workspace
                assert static_use_instance1.workspace_id != client.config.workspace_id
                assert static_use_instance2.workspace_id != client.config.workspace_id
                assert static_use_instance1.client.config.workspace_handle != "default"
                assert static_use_instance2.client.config.workspace_handle != "default"

                # And they are in the requested workspaces
                assert static_use_instance1.client.config.workspace_handle == package_handle_1
                assert static_use_instance2.client.config.workspace_handle == package_handle_2

            # We can also bring up a second instance of the same invocable
            with steamship_use(
                package.handle, package_handle_1, delete_workspace=False
            ) as static_use_instance1a:
                assert (
                    static_use_instance1a.client.config.workspace_handle
                    == static_use_instance1a.handle
                )
                assert (
                    static_use_instance1a.client.config.workspace_id
                    == static_use_instance1a.workspace_id
                )
                assert static_use_instance1a.workspace_id == static_use_instance1.workspace_id
                # And the handle is the same
                assert (
                    static_use_instance1a.handle == static_use_instance1.handle
                )  # It's the same instance (handle)
                assert (
                    static_use_instance1a.id == static_use_instance1.id
                )  # It's the same instance (id)

            # Or we could have (1) created a client anchored to the Workspace `package_handle_1` and then
            # (2) Loaded that handle from within the client.
            client2 = get_steamship_client(workspace_handle=package_handle_1)
            assert client2.config.workspace_handle == package_handle_1
            assert client2.config.workspace_id == static_use_instance1.workspace_id

            static_use_instance1a = client2.use(package.handle, package_handle_1)
            assert (
                static_use_instance1a.client.config.workspace_handle == static_use_instance1a.handle
            )  # The client is in the same workspace (handle)!
            assert (
                static_use_instance1a.client.config.workspace_id
                == static_use_instance1a.workspace_id
            )  # The client is in the same workspace (id)!
            assert (
                static_use_instance1a.workspace_id == static_use_instance1.workspace_id
            )  # It's in the same workspace!
            # And the handle is the same
            assert (
                static_use_instance1a.handle == static_use_instance1.handle
            )  # It's the same instance! (handle)
            assert (
                static_use_instance1a.id == static_use_instance1.id
            )  # It's the same instance! (id)

            # And here's the potentially hazardous thing that's possible:
            # You can use a client's member function `use` to create a second instance of that package that shares the
            # same workspace as the first, meaning it implicitly shares data.
            #
            # This is potentially useful, so it's not clear we want to forbid it (e.g. package1 could tag data, and
            # package2 could query data). But we want to encourage `Steamship.use` over `client.use` for basic use
            # due to the easier to understand scope semantics.
            package_handle_1b = random_name()
            static_use_instance1b = client2.use(package.handle, package_handle_1b)
            assert (
                static_use_instance1b.client.config.workspace_handle == static_use_instance1.handle
            )
            assert (
                static_use_instance1b.client.config.workspace_id
                == static_use_instance1.workspace_id
            )
            assert static_use_instance1b.workspace_id == static_use_instance1.workspace_id
            # But the handle isn't the same
            assert static_use_instance1b.handle != static_use_instance1.handle
            assert static_use_instance1b.id != static_use_instance1.id


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
