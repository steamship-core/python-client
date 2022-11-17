import pytest
from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import SteamshipError


def test_safe_loaded_package_with_bad_import():
    client = get_steamship_client()
    demo_package_path = PACKAGES_PATH / "safe_loaded_bad_import.pyignore"

    with deploy_package(client, demo_package_path, safe_load_handler=True) as (_, _, instance):
        with pytest.raises(SteamshipError) as error:
            _ = instance.invoke("greet")
        assert error is not None
        assert "No module named 'somethingthatclearlydoesnotexist'" in error.value.message
