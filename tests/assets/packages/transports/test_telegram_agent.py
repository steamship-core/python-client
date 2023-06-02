from typing import Any, Dict, Type

from steamship import Steamship
from steamship.agents.llms import OpenAI
from steamship.agents.mixins.transports.telegram import TelegramTransport, TelegramTransportConfig
from steamship.agents.react import ReACTAgent
from steamship.agents.schema import Agent
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.image_generation import DalleTool
from steamship.agents.tools.search import SearchTool
from steamship.invocable import Config, InvocationContext


class TestTelegramAgentConfig(TelegramTransportConfig):
    pass


class TestTelegramAgent(AgentService):

    config: TestTelegramAgentConfig
    agent: Agent

    def __init__(
        self, client: Steamship, config: Dict[str, Any] = None, context: InvocationContext = None
    ):
        super().__init__(client=client, config=config, context=context)
        self.agent = ReACTAgent(
            tools=[SearchTool(), DalleTool()],
            llm=OpenAI(self.client),
        )
        self.add_mixin(
            TelegramTransport(
                client=client, config=self.config, agent_service=self, agent=self.agent
            )
        )

    @classmethod
    def config_cls(cls) -> Type[Config]:
        return TestTelegramAgentConfig
