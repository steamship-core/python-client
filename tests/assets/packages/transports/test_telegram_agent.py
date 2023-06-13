from typing import Any, Dict, Type

from steamship import Block, File, MimeTypes, Steamship
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.mixins.transports.telegram import TelegramTransport, TelegramTransportConfig
from steamship.agents.schema import Action, Agent, AgentContext, FinishAction
from steamship.agents.service.agent_service import AgentService
from steamship.invocable import Config, InvocationContext


class TestTelegramAgentConfig(TelegramTransportConfig):
    pass


class TestAgent(Agent):
    client: Steamship

    def __init__(self, client: Steamship):
        super(TestAgent, self).__init__(client=client, tools=[])
        self.client = client

    def next_action(self, context: AgentContext) -> Action:
        input_text = context.chat_history.last_user_message.text
        if input_text == "image":
            output_file = File.create(self.client, blocks=[])
            output_block = Block.create(
                self.client,
                content="some image bytes",
                mime_type=MimeTypes.PNG,
                file_id=output_file.id,
            )
        elif input_text == "audio":
            output_file = File.create(self.client, blocks=[])
            output_block = Block.create(
                self.client,
                content="some audio bytes",
                mime_type=MimeTypes.WAV,
                file_id=output_file.id,
            )
        elif input_text == "video":
            output_file = File.create(self.client, blocks=[])
            output_block = Block.create(
                self.client,
                content="some video bytes",
                mime_type=MimeTypes.MP4_VIDEO,
                file_id=output_file.id,
            )
        else:
            output_block = Block(text=f"Response to: {input_text}")
        return FinishAction(output=[output_block], context=context)


class TestTelegramAgent(AgentService):

    config: TestTelegramAgentConfig
    agent: Agent

    USED_MIXIN_CLASSES = [TelegramTransport, SteamshipWidgetTransport]

    def __init__(
        self, client: Steamship, config: Dict[str, Any] = None, context: InvocationContext = None
    ):
        super().__init__(client=client, config=config, context=context)
        self.agent = TestAgent(client)

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
