from assets.packages.proto_agent_service import ToolBinding
from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package
from steamship_tests.utils.fixtures import get_steamship_client


def test_tool_binding_serialization():
    binding = ToolBinding(
        tool_name="ToolThatAlwaysResponseSynchronouslyAndStatically",
    )
    binding_dict = binding.dict()
    assert isinstance(binding_dict, dict)


def test_safe_loaded_hello_world():
    client = get_steamship_client()
    demo_package_path = PACKAGES_PATH / "proto_agent_service.py"

    with deploy_package(client, demo_package_path) as (_, _, instance):

        # TEST BATCH 1: SYNCHRONOUS CALLS
        # ===============================
        # This tests the idea that we can make a call to a tool that performs synrhonous work

        # Static Responses
        # ----------------
        # The output is invariant input

        binding = ToolBinding(
            tool_name="ToolThatAlwaysResponseSynchronouslyAndStatically",
        )
        response = instance.invoke("run_tool", binding=binding)
        assert response is not None
