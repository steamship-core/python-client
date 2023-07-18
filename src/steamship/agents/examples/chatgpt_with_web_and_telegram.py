"""Minimum viable AgentService implementation with Web Widget & Telegram support.

This will result in an agent that acts like ChatGPT and can be communicated with on the Steamship website
as well as over Telegram.
"""
from typing import Type

from pydantic import Field

from steamship.agents.examples.telegram_bot import TelegramBot
from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.mixins.transports.telegram import TelegramTransport, TelegramTransportConfig
from steamship.agents.service.agent_service import AgentService
from steamship.invocable import Config
from steamship.utils.repl import AgentREPL


class MyAssistant(AgentService):
    class MyAssistantConfig(Config):
        bot_token: str = Field(description="The secret token for your Telegram bot")

    config: MyAssistantConfig

    @classmethod
    def config_cls(cls) -> Type[Config]:
        return TelegramBot.TelegramBotConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._agent = FunctionsBasedAgent(llm=ChatOpenAI(self.client), tools=[])

        # This Mixin provides HTTP endpoints that connects this agent to a web client
        self.add_mixin(
            SteamshipWidgetTransport(client=self.client, agent_service=self, agent=self._agent)
        )
        # This Mixin provides support for Telegram bots
        self.add_mixin(
            TelegramTransport(
                client=self.client,
                config=TelegramTransportConfig(bot_token=self.config.bot_token),
                agent_service=self,
                agent=self._agent,
            )
        )


if __name__ == "__main__":
    AgentREPL(
        MyAssistant,
        agent_package_config={"botToken": "not-a-real-token-for-local-testing"},
    ).run()
