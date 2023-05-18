import base64
import json
from typing import Any, List

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


def run_action_with_async_response(
    client: Steamship, agent_service: PackageInstance, action: ToolAction
) -> List[Block]:
    output_action = run_action(client, agent_service, action)
    assert output_action is not None
    assert output_action.output is not None
    output = output_action.output.value(client)

    # This is some special casing that we should fix the need for, but that structurally doesn't impose a problem.
    # The way the engine guarantees that package methods can be async-ified is to base64 encode their output. This is
    # the only way to ensure that we blanket-support things like binary responses (images, audio, etc) in both sync
    # and async mode. But that means in this prototype, we have to deal with anything that's been routed async through
    # a package as having been base64'd
    obj = b64_decode_str(output)

    # There's another annoying case of this object SOMETIMES being another task that was stuffed in here.
    # Basically we need to homogenize the carrier signal back. There are a few different wrappers that get added
    # around things in different circumstances and we need to iron it out so there are no bizarre special case de-wrappings.
    # This particular wrapper which starts with <START> and ends with <END> is for the case the tools which depend upon
    # sequences of other tools dynamically.
    if obj.get("taskId"):  # <START>
        t2 = Task.get(client, _id=obj.get("taskId"))
        t2.wait()

    # <END>

    # The next quick is the off-by-one error of the "postprocess" step for a final too requiring special handling.
    # Since that special handling isn't yet created, we're handling it in the test.
    #
    # CLAIM: This is fine to illustrate capability. For example: since the ToolAction encodes the Tool name, as a worst
    # case we could always just ahve a "fetch-final-value" method that took ToolAction as input and ran the postprocessing
    # before returning an output. Or even the "singleton tool run" could be a chain of: [Tool, Finalize] in which finalize
    # is the opportunity to postprocess
    assert (
        "obj" in obj
    )  # This is the wrapping we added & the off-by-one error of not having postprocessed upon final pipeline egress

    # Return the actual contents of "obj" (basically copy-pasting the final post-processing step here for convenience)
    blocks = obj.get("obj")

    # Finally, at this point we're working with python, so we need to parse the blocks
    return [Block.parse_obj(block) for block in blocks]


def test_that_async_and_dynamically_planned_tool_chains_work():
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
        blocks_out_4 = run_action_with_async_response(client, agent_service, action_in_4)
        assert len(blocks_out_4) == 1
        assert blocks_out_4[0].text == "This was Asynchronous and Static"

        # Dynamic Responses
        # -----------------
        # The output is conditioned on input

        # Empty output

        action_in_5 = ToolAction(
            tool_name="ToolThatAlwaysResponseAsynchronouslyAndDynamically", input=ToolData()
        )
        blocks_out_5 = run_action_with_async_response(client, agent_service, action_in_5)
        assert len(blocks_out_5) == 0

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
        blocks_out_6 = run_action_with_async_response(client, agent_service, action_in_6)
        assert len(blocks_out_6) == 2
        assert blocks_out_6[0].text == "This was asynchronous and Dynamic. Input block was: 1."
        assert blocks_out_6[1].text == "This was asynchronous and Dynamic. Input block was: 2."

        # TEST BATCH 3: DYNAMIC WORK PLANS UNKNOWN AT TIME OF EXECUTION REQUEST OR EVEN EXECUTION START
        # =============================================================================================
        # This test demonstrates that it is possible for a tool to dynamically schedule work whose workflow was
        # unknown at (1) the time ToolAction was requested and (2)  the time the ToolAction began executing.
        #
        # This isn't a suggestion for what the Reasoning Agent Loop should look like. This is one level below: just
        # a demonstration that a "single tooL" need not be a simple, atomic action, but can easily be a very complex
        # and pre-planned workflow that takes places over many tasks, files, and time.. ultimately delivering a reponse
        # to the reasoning agent in the same way that a simple, atomic-scale Tool would.

        action_in_7 = ToolAction(
            tool_name="ToolThatDynamicallyPlansMoreAsyncWork", input=ToolData()
        )
        blocks_out_7 = run_action_with_async_response(client, agent_service, action_in_7)
        assert len(blocks_out_7) == 1

        # Here we see that the output is the result of Tool 2 having consumed and re-used the output of Tool 1
        assert (
            blocks_out_7[0].text
            == "This was asynchronous and Dynamic. Input block was: This was Asynchronous and Static"
        )
