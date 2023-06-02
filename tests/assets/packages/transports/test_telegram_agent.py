from typing import Any, Dict, Type

from steamship import Block, Steamship
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.mixins.transports.telegram import TelegramTransport, TelegramTransportConfig
from steamship.agents.schema import Action, Agent, AgentContext, FinishAction
from steamship.agents.service.agent_service import AgentService
from steamship.invocable import Config, InvocationContext


class TestTelegramAgentConfig(TelegramTransportConfig):
    pass


class TestAgent(Agent):
    def __init__(self):
        super(TestAgent, self).__init__(tools=[])

    def next_action(self, context: AgentContext) -> Action:
        input_text = context.chat_history.last_user_message.text
        return FinishAction(output=[Block(text=f"Response to: {input_text}")], context=context)


class TestTelegramAgent(AgentService):

    config: TestTelegramAgentConfig
    agent: Agent

    def __init__(
        self, client: Steamship, config: Dict[str, Any] = None, context: InvocationContext = None
    ):
        super().__init__(client=client, config=config, context=context)
        self.agent = TestAgent()

        # Including the web widget transport on the telegram test
        # agent to make sure it doesn't interfere
        self.add_mixin(
            SteamshipWidgetTransport(client=client, agent_service=self, agent=self.agent)
        )
        self.add_mixin(
            TelegramTransport(
                client=client, config=self.config, agent_service=self, agent=self.agent
            )
        )

    @classmethod
    def config_cls(cls) -> Type[Config]:
        return TestTelegramAgentConfig
