import pytest
from steamship_tests import PACKAGES_PATH, PLUGINS_PATH
from steamship_tests.utils.deployables import deploy_package, deploy_plugin

from steamship import Steamship


@pytest.mark.usefixtures("client")
def test_get_param_decoding(client: Steamship):
    request_id_package_path = PACKAGES_PATH / "request_id_plumbing_test_package.py"
    request_id_plugin_path = PLUGINS_PATH / "generators" / "request_id_generator.py"

    with deploy_package(client, request_id_package_path) as (package, version, instance):
        with deploy_plugin(client, request_id_plugin_path, plugin_type="generator") as (
            plugin,
            _,
            _,
        ):
            result = instance.invoke("requestids", plugin_handle=plugin.handle)
            package_request_id = result.get("packageRequestId")
            plugin_request_id = result.get("pluginRequestId")
            invoke_later_request_id = result.get("invokeLaterRequestId")
            assert package_request_id is not None
            assert package_request_id == plugin_request_id
            assert package_request_id == invoke_later_request_id
