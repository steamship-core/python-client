import uuid
from typing import Any, Dict, List, Union

import pytest

from steamship import Block, Steamship, SteamshipError, Task
from steamship.agents.schema import Action, Agent, AgentContext, Tool
from steamship.agents.service.agent_service import AgentService


class MyEverythingTool(Tool):
    name = "everything"
    agent_description = ""
    human_description = ""

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        return [Block(text="Yes")]


class MyPredictableAgent(Agent):
    def next_action(self, context: AgentContext) -> Action:
        return Action(tool="everything", input=[])


class MyToolLimitedAgentService(AgentService):
    def __init__(self, max_actions_per_tool: Dict[str, int], **kwargs):
        super().__init__(max_actions_per_tool=max_actions_per_tool, **kwargs)
        self.set_default_agent(
            MyPredictableAgent(
                tools=[
                    MyEverythingTool(),
                ],
            )
        )


@pytest.mark.usefixtures("client")
def test_tool_limits(client: Steamship):
    agent_service = MyToolLimitedAgentService(client=client, max_actions_per_tool={"everything": 3})
    agent_context = AgentContext.get_or_create(client, context_keys={"id": str(uuid.uuid4())})
    with pytest.raises(SteamshipError) as e:
        agent_service.run_agent(agent_service.get_default_agent(), context=agent_context)
    assert "budget of 3 for tool everything" in str(e)
