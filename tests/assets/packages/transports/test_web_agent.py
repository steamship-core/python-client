from typing import Any, Dict

from steamship import Block, Steamship
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.schema import Action, Agent, AgentContext, FinishAction
from steamship.agents.service.agent_service import AgentService
from steamship.invocable import InvocationContext


class TestAgent(Agent):
    def __init__(self):
        super(TestAgent, self).__init__(tools=[])

    def next_action(self, context: AgentContext) -> Action:
        input_text = context.chat_history.last_user_message.text
        return FinishAction(output=[Block(text=f"Response to: {input_text}")], context=context)


class TestTelegramAgent(AgentService):

    agent: Agent

    def __init__(
        self, client: Steamship, config: Dict[str, Any] = None, context: InvocationContext = None
    ):
        super().__init__(client=client, config=config, context=context)
        self.agent = TestAgent()
        self.add_mixin(
            SteamshipWidgetTransport(client=client, agent_service=self, agent=self.agent)
        )
