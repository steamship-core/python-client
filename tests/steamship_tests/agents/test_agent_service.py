import json
import time
from typing import Any, List, Union

import pytest
import requests
from pydantic.fields import PrivateAttr
from steamship_tests import SRC_PATH
from steamship_tests.utils.deployables import deploy_package

from steamship import Block, File, Steamship, SteamshipError, Task, TaskState
from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.logging import AgentLogging
from steamship.agents.schema import Action, AgentContext, Tool
from steamship.agents.service.agent_service import AgentService
from steamship.data.tags.tag_constants import ChatTag, RoleTag, TagKind, TagValueKey


def _blocks_from_invoke(client: Steamship, potential_blocks) -> List[Block]:
    try:
        if isinstance(potential_blocks, list):
            return [Block(client=client, **raw) for raw in potential_blocks]
        else:
            return [Block(client=client, **potential_blocks)]
    except Exception as e:
        raise SteamshipError(f"Could not convert to blocks: {e}")


@pytest.mark.usefixtures("client")
def test_example_with_caching_service(client: Steamship):
    # TODO(dougreid): replace the example agent with fake/free/fast tools to minimize test time / costs?

    example_caching_agent_path = (
        SRC_PATH / "steamship" / "agents" / "examples" / "example_assistant_with_caching.py"
    )
    with deploy_package(client, example_caching_agent_path, wait_for_init=True) as (
        _,
        _,
        caching_agent,
    ):
        context_id = "foo-test-caching"
        context_keys = {"id": context_id}

        # attempt without caching
        blocks_json = caching_agent.invoke("prompt", prompt="draw a cat", context_id=context_id)
        assert blocks_json
        blocks = _blocks_from_invoke(client, blocks_json)
        assert len(blocks) == 2
        assert "image" in blocks[0].text
        assert blocks[1].is_image()

        # attempt with a max_actions_per_run budget of 0 (should fail!)
        assert caching_agent.invoke("get_max_actions_per_run") == 5
        caching_agent.invoke("set_max_actions_per_run", value=0)
        assert caching_agent.invoke("get_max_actions_per_run") == 0

        with pytest.raises(SteamshipError, match="budget"):
            blocks_json = caching_agent.invoke("prompt", prompt="draw a cat", context_id=context_id)

        caching_agent.invoke("set_max_actions_per_run", value=5)
        assert caching_agent.invoke("get_max_actions_per_run") == 5

        agent_context = AgentContext.get_or_create(
            client=client, context_keys=context_keys, use_llm_cache=True, use_action_cache=True
        )
        # just clear the cache to start fresh
        agent_context.llm_cache.clear()
        agent_context.action_cache.clear()

        fake_action = Action(tool="fake_tool", input=[Block(text="a cat")])
        agent_context.llm_cache.update(key=[Block(text="draw a cat")], value=fake_action)

        fake_output = [Block(text="psyche")]
        agent_context.action_cache.update(key=fake_action, value=fake_output)

        fake_finish_action = Action(
            tool="Agent-FinishAction", input=[], output=[Block(text="insert cat image here")]
        )
        agent_context.llm_cache.update(key=fake_output, value=fake_finish_action)

        # now attempt with the caching
        blocks_json = caching_agent.invoke("prompt", prompt="draw a cat", context_id=context_id)
        assert blocks_json
        blocks = _blocks_from_invoke(client, blocks_json)
        assert len(blocks) == 1
        assert "insert cat image here" == blocks[0].text


class FakeUncachableTool(Tool):
    name = "FakeUncacheableTool"
    human_description = "Fake tool"
    agent_description = "Ignored"

    _runs: int = PrivateAttr(default=0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs, cacheable=False)

    @property
    def runs(self):
        return self._runs

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        self._runs += 1
        return [Block(text="sunny and mild")]


class FakeCachingService(AgentService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, use_llm_cache=True, use_action_cache=True)
        self.set_default_agent(
            FunctionsBasedAgent(
                tools=[FakeUncachableTool()], llm=ChatOpenAI(self.client, temperature=0)
            )
        )

    @property
    def uncachable_tool(self):
        return self.get_default_agent().tools[0]


@pytest.mark.usefixtures("client")
def test_non_cacheable_tool_actions(client: Steamship):
    context_id = "foo-test-non-cacheable"
    context_keys = {"id": context_id}

    agent_context = AgentContext.get_or_create(
        client=client, context_keys=context_keys, use_llm_cache=True, use_action_cache=True
    )

    service_under_test = FakeCachingService(client=client, config={})

    # clear the cache to start fresh
    agent_context.llm_cache.clear()
    agent_context.action_cache.clear()

    # build up cache to ensure Fake Weather Tool is called
    fake_action = Action(
        tool=service_under_test.uncachable_tool.name, input=[Block(text="weather in SF today")]
    )
    agent_context.llm_cache.update(
        key=[Block(text="what is the weather in SF today?")], value=fake_action
    )

    fake_finish_action = Action(
        tool="Agent-FinishAction", input=[], output=[Block(text="sunny and mild")]
    )
    agent_context.llm_cache.update(key=[Block(text="sunny and mild")], value=fake_finish_action)

    # run once to "fill" caches
    service_under_test.prompt(prompt="what is the weather in SF today?", context_id=context_id)
    assert service_under_test.uncachable_tool.runs == 1

    # now attempt again, and verify the Tool executed again
    service_under_test.prompt(prompt="what is the weather in SF today?", context_id=context_id)
    assert service_under_test.uncachable_tool.runs == 2, "The tool action was unexpectedly cached."


def has_status_message(blocks: List[Block], role: RoleTag) -> bool:
    for b in blocks:
        for t in b.tags:
            if (
                t.kind == TagKind.CHAT
                and t.name == ChatTag.ROLE
                and t.value.get(TagValueKey.STRING_VALUE) == role
            ):
                return True


@pytest.mark.usefixtures("client")
def test_context_logging_to_chat_history_everything(client: Steamship):
    example_agent_service_path = (
        SRC_PATH / "steamship" / "agents" / "examples" / "example_assistant.py"
    )
    with deploy_package(client, example_agent_service_path, wait_for_init=True) as (
        _,
        _,
        agent_service,
    ):
        # test for everything (should include actions, llm, and tool)
        context_id = "foo-test-logging-everything"
        context_keys = {"id": context_id}
        agent_context = AgentContext.get_or_create(client=client, context_keys=context_keys)
        chat_history = agent_context.chat_history

        agent_service.invoke(
            "prompt", prompt="who is the current president of Taiwan?", context_id=context_id
        )
        chat_history.refresh()
        assert len(chat_history.messages) != 0
        assert has_status_message(chat_history.messages, RoleTag.AGENT)
        assert has_status_message(chat_history.messages, RoleTag.LLM)
        assert has_status_message(chat_history.messages, RoleTag.TOOL)

        # test for individual bits (only include actions, llm, or tool)
        context_id = "foo-test-logging-agent-only"
        context_keys = {"id": context_id}
        agent_context = AgentContext.get_or_create(client=client, context_keys=context_keys)
        chat_history = agent_context.chat_history

        agent_service.invoke(
            "prompt",
            prompt="who is the current prime minister of Canada?",
            context_id=context_id,
            include_llm_messages=False,
            include_tool_messages=False,
        )
        chat_history.refresh()

        assert len(chat_history.messages) != 0
        assert has_status_message(chat_history.messages, RoleTag.AGENT)
        assert not has_status_message(chat_history.messages, RoleTag.LLM)
        assert not has_status_message(chat_history.messages, RoleTag.TOOL)

        context_id = "foo-test-logging-llm-only"
        context_keys = {"id": context_id}
        agent_context = AgentContext.get_or_create(client=client, context_keys=context_keys)
        chat_history = agent_context.chat_history

        agent_service.invoke(
            "prompt",
            prompt="who is the current prime minister of England?",
            context_id=context_id,
            include_agent_messages=False,
            include_tool_messages=False,
        )
        chat_history.refresh()

        assert len(chat_history.messages) != 0
        assert not has_status_message(chat_history.messages, RoleTag.AGENT)
        assert has_status_message(chat_history.messages, RoleTag.LLM)
        assert not has_status_message(chat_history.messages, RoleTag.TOOL)

        context_id = "foo-test-logging-tool-only"
        context_keys = {"id": context_id}
        agent_context = AgentContext.get_or_create(client=client, context_keys=context_keys)
        chat_history = agent_context.chat_history

        agent_service.invoke(
            "prompt",
            prompt="who is the current president of France?",
            context_id=context_id,
            include_agent_messages=False,
            include_llm_messages=False,
        )
        chat_history.refresh()

        assert len(chat_history.messages) != 0
        assert not has_status_message(chat_history.messages, RoleTag.AGENT)
        assert not has_status_message(chat_history.messages, RoleTag.LLM)
        assert has_status_message(chat_history.messages, RoleTag.TOOL)


@pytest.fixture()
def close_clients():
    to_close = []
    yield to_close
    for item in to_close:
        item.close()


@pytest.mark.usefixtures("client", "close_clients")
def test_async_prompt(client: Steamship, close_clients):  # noqa: C901
    example_agent_service_path = (
        SRC_PATH / "steamship" / "agents" / "examples" / "example_assistant.py"
    )
    with deploy_package(client, example_agent_service_path, wait_for_init=True) as (
        _,
        _,
        agent_service,
    ):
        context_id = "some_async_fun"
        try:
            streaming_resp = agent_service.invoke(
                "async_prompt",
                prompt="who is the current president of the United States?",
                context_id=context_id,
            )
        except SteamshipError as error:
            pytest.fail(f"failed request: {error}")

        assert streaming_resp is not None
        assert streaming_resp["file"] is not None
        assert streaming_resp["task"] is not None

        file = File(client=client, **(streaming_resp["file"]))
        streaming_task = Task(client=client, **(streaming_resp["task"]))

        original_len = len(file.blocks)

        while streaming_task.state in [TaskState.waiting]:
            # tight loop to check on waiting status of Task
            # we only want to try to stream once a Task **starts**
            time.sleep(0.1)
            streaming_task.refresh()

        assert streaming_task.state in [TaskState.running]

        block_ids_seen = []
        llm_prompt_event_count = 0
        function_selection_event = False
        tool_execution_event = False
        function_complete_event = False
        assistant_chat_response_event = False

        # TODO: it is concerning that putting this block after a Task completes is the only way it seems to work
        num_events = 0
        # sse event format: {'blockCreated': {'blockId': '<uuid>', 'createdAt': '2023-09-25T16:12:54Z'}}
        for event in events_while_running(client, streaming_task, file):
            # TODO: it seems like event ids aren't consistent
            block_creation_event = json.loads(event.data)
            block_created = block_creation_event["blockCreated"]
            block_id = block_created["blockId"]
            if block_id in block_ids_seen:
                continue
            block_ids_seen.append(block_id)
            num_events += 1
            block = Block.get(client=client, _id=block_id)
            for t in block.tags:
                match t.kind:
                    case TagKind.LLM_STATUS_MESSAGE:
                        if t.name == AgentLogging.PROMPT:
                            llm_prompt_event_count += 1
                    case TagKind.FUNCTION_SELECTION:
                        if t.name == "SearchTool":
                            function_selection_event = True
                    case TagKind.TOOL_STATUS_MESSAGE:
                        tool_execution_event = True
                    case TagKind.ROLE:
                        if t.name == RoleTag.FUNCTION:
                            function_complete_event = True
                    case TagKind.CHAT:
                        if (
                            t.name == ChatTag.ROLE
                            and t.value.get(TagValueKey.STRING_VALUE, "") == RoleTag.ASSISTANT
                        ):
                            assistant_chat_response_event = True

        file.refresh()
        assert (
            len(file.blocks) > original_len
        ), "File should have increased in size during AgentService execution"

        print(f"num events: {num_events}")
        assert num_events > 0, "Events should have been streamed during execution"
        assert llm_prompt_event_count == 2, (
            "At least 2 llm prompts should have happened (first for tool selection, "
            "second for generating final answer)"
        )
        assert function_selection_event is True, "SearchTool should have been selected"
        assert tool_execution_event is True, "SearchTool should log a status message"
        assert function_complete_event is True, "SearchTool should return a response"
        assert (
            assistant_chat_response_event is True
        ), "Agent should have sent the assistant chat response"
        # assert False


def events_while_running(client: Steamship, task: Task, file: File):
    req_id = task.request_id
    while task.state in [TaskState.running]:
        yields = 0
        # NOTE: I'm convinced that this generator of generators approach is not correct, but...
        event_gen = events_for_file(client, file.id, req_id)
        try:
            for event in event_gen:
                yields += 1
                yield event
        except StopIteration:
            # not ready to stream, or done streaming.
            print("stop iteration")
            pass
        print(f"total yields: {yields}")
        # This is not ideal, but it at least should make sure we get **all** events
        task.refresh()
    print(f"task is complete: {task.state}")


def events_for_file(client: Steamship, file_id: str, req_id: str):
    print("getting events for file.")
    import sseclient

    sse_source = f"{client.config.api_base}file/{file_id}/stream?tagKindFilter=request-id&tagNameFilter={req_id}&timeoutSeconds=30"
    headers = {
        "Accept": "text/event-stream",
        "X-Workspace-Id": client.get_workspace().id,
        "Authorization": f"Bearer {client.config.api_key.get_secret_value()}",
    }

    sse_response = requests.get(sse_source, stream=True, headers=headers, timeout=45)
    sse_client = sseclient.SSEClient(sse_response)
    yields = 0
    try:
        for event in sse_client.events():
            yields += 1
            print(f"--> yield: {yields}")
            yield event
    except requests.exceptions.ConnectionError as err:
        if "Read timed out." in str(err):
            print("-- timeout")
            pass
        else:
            sse_client.close()
            sse_response.close()
            raise err
    except StopIteration:
        print("-- stop iteration")
        sse_client.close()
        sse_response.close()
    except Exception as err:
        sse_client.close()
        sse_response.close()
        raise err
    else:
        print("-- successful close of stream.")
        sse_client.close()
        sse_response.close()
