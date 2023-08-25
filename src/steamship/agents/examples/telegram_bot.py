from typing import Type

from pydantic import Field

from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.mixins.transports.telegram import TelegramTransport, TelegramTransportConfig
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.image_generation.stable_diffusion import StableDiffusionTool
from steamship.invocable import Config
from steamship.utils.repl import AgentREPL

SYSTEM_PROMPT = """You are Captain Jean-Luc Picard of the space ship USS Enterprise.

Who you are:
- You are the captain of the USS Enterprise.
- Your mission is to boldly go where no-one has gone before and explore the stars.
- You always comply with Star Trek's prime directive.

NOTE: Some functions return images, video, and audio files. These multimedia files will be represented in messages as
UUIDs for Steamship Blocks. When responding directly to a user, you SHOULD print the Steamship Blocks for the images,
video, or audio as follows: `Block(UUID for the block)`.

Example response for a request that generated an image:
Here is the image you requested: Block(288A2CA1-4753-4298-9716-53C1E42B726B).

Only use the functions you have been provided with."""


MODEL_NAME = "gpt-4"


class TelegramBot(AgentService):
    """Deployable Multimodal Agent that lets you talk to Google Search & Google Images.

    NOTE: To extend and deploy this agent, copy and paste the code into api.py.

    """

    class TelegramBotConfig(Config):
        telegram_bot_token: str = Field(description="The secret token for your Telegram bot")

    config: TelegramBotConfig

    @classmethod
    def config_cls(cls) -> Type[Config]:
        return TelegramBot.TelegramBotConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # The agent's planner is responsible for making decisions about what to do for a given input.
        self.set_default_agent(
            FunctionsBasedAgent(
                tools=[StableDiffusionTool()],
                llm=ChatOpenAI(self.client, model_name=MODEL_NAME),
            )
        )
        self.get_default_agent().PROMPT = SYSTEM_PROMPT

        # This Mixin provides HTTP endpoints that connects this agent to a web client
        self.add_mixin(SteamshipWidgetTransport(client=self.client, agent_service=self))
        # This Mixin provides support for Telegram bots
        self.add_mixin(
            TelegramTransport(
                client=self.client,
                # IMPORTANT: This is the TelegramTransportConfig, not the AgentService config!
                config=TelegramTransportConfig(bot_token=self.config.telegram_bot_token),
                agent_service=self,
            )
        )


if __name__ == "__main__":
    AgentREPL(
        TelegramBot,
        agent_package_config={"botToken": "not-a-real-token-for-local-testing"},
    ).run()
