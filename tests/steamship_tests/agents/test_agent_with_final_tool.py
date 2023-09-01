from typing import Any, Callable, List, Optional, Union

import pytest

from steamship import Block, Task
from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.schema import AgentContext, Tool
from steamship.agents.schema.message_selectors import MessageWindowMessageSelector
from steamship.agents.service.agent_service import AgentService


class NonFinalTool(Tool):
    name = "SuggestFood"
    agent_description = "Tool that suggests a food. Use whenever someone wants a food suggestion. Input: the food suggestion request. Output: the food suggested."
    human_description = "SuggestFood"
    is_final: bool = False

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        return [Block(text="apples")]


class FinalTool(Tool):
    name = "SuggestPlace"
    agent_description = "Tool that suggests a place. Use whenever someone wants a place suggestion. Input: the place suggestion request. Output: the place suggested."
    human_description = "SuggestPlace"
    is_final: bool = True

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        return [Block(text="Peru")]


class MyFinalToolAssistant(AgentService):
    """MyFinalToolAssistant is an example AgentService that exposes a single test endpoint
    for testing the `is_final` marker on Tools. It is configured with two simple Tool: one
    is final and one is not. It is instructed to have a strong personality which should it cause it
    to rewrite the tool output if the tool is not final, but not to rewrite the tool output if it
    is final."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs, use_llm_cache=True, use_action_cache=True)
        self.set_default_agent(
            FunctionsBasedAgent(
                tools=[
                    NonFinalTool(),
                    FinalTool(),
                ],
                llm=ChatOpenAI(self.client, temperature=0),
                conversation_memory=MessageWindowMessageSelector(k=2),
            )
        )


@pytest.mark.parametrize("invocable_handler", [MyFinalToolAssistant], indirect=True)
def test_final_tool_assistant(invocable_handler: Callable[[str, str, Optional[dict]], dict]):
    food_suggestion = invocable_handler("POST", "/prompt", {"prompt": "Suggest a food"}).get("data")
    assert food_suggestion
    assert food_suggestion[0].get("text")

    # The agent responded with a FULL sentence. Something like: "I suggest you try some apples!"
    assert food_suggestion[0].get("text") != "apples"
    assert "apples" in food_suggestion[0].get("text")

    # Now we'll ask for a place, which uses the is_final=True tool.
    # The response should be exactly and only the tool output.

    food_suggestion = invocable_handler("POST", "/prompt", {"prompt": "Suggest a place"}).get(
        "data"
    )
    assert food_suggestion
    assert food_suggestion[0].get("text")

    # The agent responded with a FULL sentence. Something like: "I suggest you try some apples!"
    assert food_suggestion[0].get("text") == "Peru"
