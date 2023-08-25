from typing import Any, Dict, Optional, Type

from steamship import Block, File, MimeTypes, Steamship
from steamship.agents.mixins.transports.slack import SlackTransport, SlackTransportConfig
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.mixins.transports.telegram import TelegramTransport, TelegramTransportConfig
from steamship.agents.schema import Action, Agent, AgentContext, FinishAction
from steamship.agents.service.agent_service import AgentService
from steamship.invocable import Config, InvocationContext


class TestTransportsAgentConfig(Config):
    telegram_token: Optional[str] = ""
    telegram_api_base: Optional[str] = ""
    slack_api_base: Optional[str] = ""


class TestAgent(Agent):
    client: Steamship

    def __init__(self, client: Steamship):
        super(TestAgent, self).__init__(client=client, tools=[])
        self.client = client

    def next_action(self, context: AgentContext) -> Action:
        """Helps us test the transport by controlling what it will return"""
        input_text = context.chat_history.last_user_message.text
        if input_text == "image":
            output_file = File.create(self.client, blocks=[])
            output_block = Block.create(
                self.client,
                content="some image bytes",
                mime_type=MimeTypes.PNG,
                file_id=output_file.id,
                public_data=True,
            )
        elif input_text == "audio":
            output_file = File.create(self.client, blocks=[])
            output_block = Block.create(
                self.client,
                content="some audio bytes",
                mime_type=MimeTypes.WAV,
                file_id=output_file.id,
                public_data=True,
            )
        elif input_text == "video":
            output_file = File.create(self.client, blocks=[])
            output_block = Block.create(
                self.client,
                content="some video bytes",
                mime_type=MimeTypes.MP4_VIDEO,
                file_id=output_file.id,
                public_data=True,
            )
        else:
            output_block = Block(text=f"Response to: {input_text}")
        return FinishAction(output=[output_block], context=context)


class TestTransportsAgentService(AgentService):

    config: TestTransportsAgentConfig
    agent: Agent

    USED_MIXIN_CLASSES = [
        TelegramTransport,
        SteamshipWidgetTransport,
        SlackTransport,
        # TODO: Future Transport authors: add your transport here.
    ]

    def __init__(
        self, client: Steamship, config: Dict[str, Any] = None, context: InvocationContext = None
    ):
        super().__init__(client=client, config=config, context=context)
        self.set_default_agent(TestAgent(client))

        # Including the web widget transport on the telegram test
        # agent to make sure it doesn't interfere
        self.add_mixin(SteamshipWidgetTransport(client=client, agent_service=self))

        # Only add the mixin if a telegram key was provided.
        self.add_mixin(
            TelegramTransport(
                client=client,
                config=TelegramTransportConfig(
                    bot_token=self.config.telegram_token, api_base=self.config.telegram_api_base
                ),
                agent_service=self,
            )
        )

        self.add_mixin(
            SlackTransport(
                client=client,
                config=SlackTransportConfig(slack_api_base=self.config.slack_api_base),
                agent_service=self,
            )
        )

        # TODO: Future Transport authors: add your transport here.

    @classmethod
    def config_cls(cls) -> Type[Config]:
        return TestTransportsAgentConfig
