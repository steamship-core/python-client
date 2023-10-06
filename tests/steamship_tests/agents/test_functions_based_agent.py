import json

import pytest

from steamship import Block, Steamship, Tag
from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.schema import Action, AgentContext, FinishAction
from steamship.agents.schema.message_selectors import MessageWindowMessageSelector
from steamship.agents.tools.image_generation import DalleTool
from steamship.agents.tools.search import SearchTool
from steamship.data import TagKind, TagValueKey
from steamship.data.tags.tag_constants import ChatTag, RoleTag
from steamship.data.tags.tag_utils import get_tag, get_tag_value_key


@pytest.mark.usefixtures("client")
def test_functions_based_agent_build_chat_history(client: Steamship):
    agent = FunctionsBasedAgent(tools=[], llm=ChatOpenAI(client, temperature=0))

    ctx_keys = {"id": "testing-foo"}
    ctx = AgentContext.get_or_create(client=client, context_keys=ctx_keys, searchable=False)

    msg_text = "what should I eat for dinner?"
    appended_msg = ctx.chat_history.append_user_message(msg_text)
    assert appended_msg
    assert appended_msg.text == msg_text

    last_user_message = ctx.chat_history.last_user_message
    assert last_user_message
    assert last_user_message.text == msg_text

    messages = agent.build_chat_history_for_tool(context=ctx)

    assert messages
    assert len(messages) == 2

    assert messages[1].text == msg_text


@pytest.mark.usefixtures("client")
def test_functions_based_agent_with_no_tools_and_no_memory(client: Steamship):
    agent = FunctionsBasedAgent(tools=[], llm=ChatOpenAI(client, temperature=0))

    ctx_keys = {"id": "testing-foo"}
    ctx = AgentContext.get_or_create(client=client, context_keys=ctx_keys, searchable=False)
    ctx.chat_history.append_user_message("what should I eat for dinner?")

    action = agent.next_action(context=ctx)
    assert isinstance(action, FinishAction)


@pytest.mark.usefixtures("client")
def test_functions_based_agent_single_tool_selection_with_no_memory(client: Steamship):
    agent = FunctionsBasedAgent(
        tools=[SearchTool(), DalleTool()], llm=ChatOpenAI(client, temperature=0)
    )

    ctx_keys = {"id": "testing-foo"}
    ctx = AgentContext.get_or_create(client=client, context_keys=ctx_keys, searchable=False)
    ctx.chat_history.append_user_message("who won the men's french open in 2023?")

    action = agent.next_action(context=ctx)
    assert not isinstance(action, FinishAction)
    assert action.tool == "SearchTool"


@pytest.mark.usefixtures("client")
def test_functions_based_agent_multimodal_tool_selection_with_no_memory(client: Steamship):
    agent = FunctionsBasedAgent(
        tools=[SearchTool(), DalleTool()], llm=ChatOpenAI(client, temperature=0)
    )

    ctx_keys = {"id": "testing-foo"}
    ctx = AgentContext.get_or_create(client=client, context_keys=ctx_keys, searchable=False)
    ctx.chat_history.append_user_message("paint a picture of a cat in a silly hat")

    action = agent.next_action(context=ctx)
    assert not isinstance(action, FinishAction)
    assert action.tool == "DalleTool"


@pytest.mark.usefixtures("client")
def test_functions_based_agent_no_appropriate_tool_with_no_memory(client: Steamship):
    agent = FunctionsBasedAgent(
        tools=[SearchTool(), DalleTool()], llm=ChatOpenAI(client, temperature=0)
    )

    ctx_keys = {"id": "testing-foo"}
    ctx = AgentContext.get_or_create(client=client, context_keys=ctx_keys, searchable=False)
    ctx.chat_history.append_user_message(
        "record an original 30 minute song about a hamburger that learns to talk. do not find an existing one."
    )

    action = agent.next_action(context=ctx)
    assert isinstance(action, FinishAction)


@pytest.mark.usefixtures("client")
def test_functions_based_agent_tool_chaining_without_memory(client: Steamship):
    agent = FunctionsBasedAgent(
        tools=[SearchTool(), DalleTool()],
        llm=ChatOpenAI(client, temperature=0),
    )

    ctx_keys = {"id": "testing-foo"}
    ctx = AgentContext.get_or_create(client=client, context_keys=ctx_keys, searchable=False)
    ctx.chat_history.append_user_message(
        "search to find the first president of the United States and then paint a picture of them"
    )

    action = agent.next_action(context=ctx)
    assert not isinstance(action, FinishAction)
    assert action.tool == "SearchTool"

    if not action.output:
        action.output = []

    action.output.append(Block(text="George Washington"))
    agent.record_action_run(action, ctx)

    second_action = agent.next_action(context=ctx)
    assert not isinstance(second_action, FinishAction)
    assert second_action.tool == "DalleTool"


@pytest.mark.usefixtures("client")
def test_functions_based_agent_tools_with_memory(client: Steamship):
    agent = FunctionsBasedAgent(
        tools=[SearchTool(), DalleTool()],
        llm=ChatOpenAI(client, temperature=0),
        message_selector=MessageWindowMessageSelector(k=2),
    )

    ctx_keys = {"id": "testing-foo"}
    ctx = AgentContext.get_or_create(client=client, context_keys=ctx_keys)
    ctx.chat_history.append_user_message("who is the president of Taiwan?")

    action = agent.next_action(context=ctx)
    assert not isinstance(action, FinishAction)
    assert action.tool == "SearchTool"

    ctx.chat_history.append_assistant_message("Tsai Ing-wen")
    ctx.completed_steps = []

    ctx.chat_history.append_user_message("draw them standing at a podium")

    second_action = agent.next_action(context=ctx)
    assert not isinstance(second_action, FinishAction)
    assert second_action.tool == "DalleTool"

    found = False
    for block in second_action.input:
        if "Tsai Ing-wen" in block.text:
            found = True

    assert found


@pytest.mark.usefixtures("client")
def test_proper_message_selection(client: Steamship):
    context_id = "test-for-message-selection"
    context_keys = {"id": context_id}
    agent_context = AgentContext.get_or_create(client=client, context_keys=context_keys)

    test_agent = FunctionsBasedAgent(
        tools=[
            SearchTool(),
            DalleTool(),
        ],
        llm=ChatOpenAI(client, temperature=0),
        message_selector=MessageWindowMessageSelector(k=2),
    )

    # simulate prompting and tool selection
    agent_context.chat_history.append_system_message(text=test_agent.PROMPT)
    agent_context.chat_history.append_user_message(text="Who is the current president of Taiwan?")
    agent_context.chat_history.append_agent_message(text="Ignore me.")
    agent_context.chat_history.append_llm_message(text="OpenAI ChatComplete...")

    # simulate running the Tool
    arg_block = Block(
        text="current president of Taiwan", tags=[Tag(kind=TagKind.FUNCTION_ARG, name="text")]
    )
    action = Action(tool="SearchTool", input=[arg_block], output=[Block(text="Tsai Ing-wen")])
    test_agent._record_action_selection(action=action, context=agent_context)
    agent_context.chat_history.append_tool_message(text="Some tool message.")
    test_agent.record_action_run(action=action, context=agent_context)

    # simulate completing
    agent_context.chat_history.append_agent_message(text="something about Tsai Ing-wen")
    agent_context.chat_history.append_llm_message(text="OpenAI ChatComplete...")
    agent_context.chat_history.append_agent_message(text="Finish Action...")
    agent_context.chat_history.append_assistant_message(
        text="The current president of Taiwan is Tsai Ing-wen."
    )

    # simulate next prompt
    agent_context.chat_history.append_user_message(text="totally. thanks.")

    selected_messages = test_agent.build_chat_history_for_tool(agent_context)

    expected_messages = [
        Block(
            text=test_agent.PROMPT,
            tags=[
                Tag(
                    kind=TagKind.CHAT, name=ChatTag.ROLE, value={TagValueKey.STRING_VALUE: "system"}
                )
            ],
        ),
        Block(
            text="Who is the current president of Taiwan?",
            tags=[
                Tag(kind=TagKind.CHAT, name=ChatTag.ROLE, value={TagValueKey.STRING_VALUE: "user"})
            ],
        ),
        Block(
            text=json.dumps(
                {"name": "SearchTool", "arguments": '{"text": "current president of Taiwan"}'}
            ),
            tags=[
                Tag(
                    kind=TagKind.CHAT,
                    name=ChatTag.ROLE,
                    value={TagValueKey.STRING_VALUE: "assistant"},
                ),
                Tag(kind="function-selection", name="SearchTool"),
            ],
        ),
        Block(
            text="Tsai Ing-wen",
            tags=[
                Tag(
                    kind=ChatTag.ROLE,
                    name=RoleTag.FUNCTION,
                    value={TagValueKey.STRING_VALUE: "SearchTool"},
                )
            ],
        ),
        Block(
            text="The current president of Taiwan is Tsai Ing-wen.",
            tags=[
                Tag(
                    kind=TagKind.CHAT,
                    name=ChatTag.ROLE,
                    value={TagValueKey.STRING_VALUE: "assistant"},
                )
            ],
        ),
        Block(
            text="totally. thanks.",
            tags=[
                Tag(kind=TagKind.CHAT, name=ChatTag.ROLE, value={TagValueKey.STRING_VALUE: "user"})
            ],
        ),
    ]

    assert len(selected_messages) == len(
        expected_messages
    ), "Missing selected messages from prepared messages"
    for idx, selected_msg in enumerate(selected_messages):
        expected_msg = expected_messages[idx]
        assert (
            selected_msg.text == expected_msg.text
        ), f"Got: {selected_msg.text}, want: {expected_msg.text}"
        for t in expected_msg.tags:
            if t.value:
                assert get_tag_value_key(
                    tags=selected_msg.tags, key=TagValueKey.STRING_VALUE, kind=t.kind, name=t.name
                ), "Expected tag not found in selected message"
            else:
                assert get_tag(
                    tags=selected_msg.tags, kind=t.kind, name=t.name
                ), "Expected tag not found in selected message"
