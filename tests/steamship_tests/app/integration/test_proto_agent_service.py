import base64
import json
from typing import Any

from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import Block, PackageInstance, Steamship, Task, TaskState
from steamship.agents.action import ToolAction
from steamship.agents.tool_data import ToolData


def b64_decode_str(b64_output: str) -> Any:
    binary_output = base64.b64decode(b64_output)
    string_output = binary_output.decode("utf-8")
    json_output = json.loads(string_output)
    return json_output


def test_tool_binding_serialization():
    action = ToolAction(
        tool_name="ToolThatAlwaysResponseSynchronouslyAndStatically", input=ToolData()
    )
    binding_dict = action.dict()
    assert isinstance(binding_dict, dict)

    action2 = ToolAction(
        tool_name="ToolThatAlwaysResponseSynchronouslyAndStatically",
        input=ToolData(inline_value=[Block(text="fo")]),
    )
    binding_dict2 = action2.dict()
    assert isinstance(binding_dict2, dict)


def run_action(client: Steamship, agent_service: PackageInstance, action: ToolAction) -> ToolAction:
    response = agent_service.invoke("enqueue_tool_action", action=action.dict())
    assert response is not None

    # Response is a task
    task = Task.parse_obj(response)
    task.client = client  # Necessary since it's not on the response
    assert task.task_id is not None

    # Assert task is waiting -- it's truly async
    assert task.state == TaskState.waiting
    task.wait()

    b64_output = task.output
    binary_output = base64.b64decode(b64_output)
    string_output = binary_output.decode("utf-8")
    json_output = json.loads(string_output)
    tool_action_out = ToolAction.parse_obj(json_output)
    return tool_action_out


def test_safe_loaded_hello_world():
    client = get_steamship_client()
    demo_package_path = PACKAGES_PATH / "agent_service_prototype.py"

    with deploy_package(client, demo_package_path) as (_, _, agent_service):

        # TEST BATCH 1: SYNCHRONOUS CALLS
        # ===============================
        # This tests the idea that we can make a call to a tool that performs synrhonous work

        # Static Responses
        # ----------------
        # The output is invariant input

        action_in_1 = ToolAction(
            tool_name="ToolThatAlwaysResponseSynchronouslyAndStatically", input=ToolData()
        )
        action_out_1 = run_action(client, agent_service, action_in_1)
        assert action_out_1.output is not None
        assert action_out_1.output.inline_value is not None
        assert len(action_out_1.output.inline_value) == 1
        assert action_out_1.output.inline_value[0].text == "This was Synchronous and Static"

        # Dynamic Responses
        # -----------------
        # The output is conditioned on input

        # Empty output

        action_in_2 = ToolAction(
            tool_name="ToolThatAlwaysResponseSynchronouslyAndDynamically", input=ToolData()
        )
        action_out_2 = run_action(client, agent_service, action_in_2)
        assert action_out_2.output is not None
        assert action_out_2.output.inline_value is not None
        assert len(action_out_2.output.inline_value) == 0

        # Two outputs

        action_in_3 = ToolAction(
            tool_name="ToolThatAlwaysResponseSynchronouslyAndDynamically",
            input=ToolData(
                inline_value=[
                    Block(text="1."),
                    Block(text="2."),
                ]
            ),
        )
        action_out_3 = run_action(client, agent_service, action_in_3)
        assert action_out_3.output is not None
        assert action_out_3.output.inline_value is not None
        assert len(action_out_3.output.inline_value) == 2
        assert (
            action_out_3.output.inline_value[0].text
            == "This was synchronous and Dynamic. Input block was: 1."
        )
        assert (
            action_out_3.output.inline_value[1].text
            == "This was synchronous and Dynamic. Input block was: 2."
        )

        # TEST BATCH 2: ASYNC CALLS
        # ===============================
        # This tests the idea that we can make a call to a tool that performs async work

        # Static Responses
        # ----------------
        # The output is invariant input

        action_in_4 = ToolAction(
            tool_name="ToolThatAlwaysResponseAsynchronouslyAndStatically", input=ToolData()
        )
        action_out_4 = run_action(client, agent_service, action_in_4)
        action_out_4_output = action_out_4.output.value(client)
        assert action_out_4_output is not None
        obj4 = b64_decode_str(action_out_4_output)  # Side effect of the way we async package calls
        assert (
            "obj" in obj4
        )  # This is the wrapping we added & the off-by-one error of not having postprocessed upon final pipeline egress
        obj4a = obj4.get("obj")
        assert len(obj4a) == 1
        assert obj4a[0].get("text") == "This was Asynchronous and Static"

        # Dynamic Responses
        # -----------------
        # The output is conditioned on input

        # Empty output

        action_in_5 = ToolAction(
            tool_name="ToolThatAlwaysResponseAsynchronouslyAndDynamically", input=ToolData()
        )
        action_out_5 = run_action(client, agent_service, action_in_5)
        action_out_5_output = action_out_5.output.value(client)
        obj5 = b64_decode_str(action_out_5_output)  # Side effect of the way we async package calls
        assert (
            "obj" in obj5
        )  # This is the wrapping we added & the off-by-one error of not having postprocessed upon final pipeline egress
        obj5a = obj5.get("obj")
        assert len(obj5a) == 0

        # Two outputs
        action_in_6 = ToolAction(
            tool_name="ToolThatAlwaysResponseAsynchronouslyAndDynamically",
            input=ToolData(
                inline_value=[
                    Block(text="1."),
                    Block(text="2."),
                ]
            ),
        )
        action_out_6 = run_action(client, agent_service, action_in_6)
        action_out_6_output = action_out_6.output.value(client)
        assert action_out_6_output is not None
        obj6 = b64_decode_str(action_out_6_output)  # Side effect of the way we async package calls
        assert (
            "obj" in obj6
        )  # This is the wrapping we added & the off-by-one error of not having postprocessed upon final pipeline egress
        obj6a = obj6.get("obj")
        assert len(obj6a) == 2
        assert obj6a[0].get("text") == "This was asynchronous and Dynamic. Input block was: 1."
        assert obj6a[1].get("text") == "This was asynchronous and Dynamic. Input block was: 2."
