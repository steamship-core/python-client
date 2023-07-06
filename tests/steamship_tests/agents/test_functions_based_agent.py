import pytest

from steamship import Block, Steamship
from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.schema import AgentContext, FinishAction
from steamship.agents.schema.message_selectors import MessageWindowMessageSelector
from steamship.agents.tools.image_generation import DalleTool
from steamship.agents.tools.search import SearchTool


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
    assert action.tool.name == "SearchTool"


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
    assert action.tool.name == "DalleTool"


@pytest.mark.usefixtures("client")
def test_functions_based_agent_no_appropriate_tool_with_no_memory(client: Steamship):
    agent = FunctionsBasedAgent(
        tools=[SearchTool(), DalleTool()], llm=ChatOpenAI(client, temperature=0)
    )

    ctx_keys = {"id": "testing-foo"}
    ctx = AgentContext.get_or_create(client=client, context_keys=ctx_keys, searchable=False)
    ctx.chat_history.append_user_message(
        "make a 10 second movie about a hamburger that learns to talk"
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
    assert action.tool.name == "SearchTool"

    action.output.append(Block(text="George Washington"))
    ctx.completed_steps.append(action)

    second_action = agent.next_action(context=ctx)
    assert not isinstance(second_action, FinishAction)
    assert second_action.tool.name == "DalleTool"


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
    assert action.tool.name == "SearchTool"

    ctx.chat_history.append_assistant_message("Tsai Ing-wen")
    ctx.completed_steps = []

    ctx.chat_history.append_user_message("draw them standing at a podium")

    second_action = agent.next_action(context=ctx)
    assert not isinstance(second_action, FinishAction)
    assert second_action.tool.name == "DalleTool"

    found = False
    for block in second_action.input:
        if "Tsai Ing-wen" in block.text:
            found = True

    assert found
