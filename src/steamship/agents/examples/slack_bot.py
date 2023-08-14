from typing import Type

from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.mixins.transports.slack import SlackTransport, SlackTransportConfig
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.image_generation.stable_diffusion import StableDiffusionTool
from steamship.invocable import Config
from steamship.utils.repl import AgentREPL

SYSTEM_PROMPT = """You are Assistant - a Slack bot that generates Stable Diffusion images."""

MODEL_NAME = "gpt-4"


class SlackBot(AgentService):
    """Deployable Multimodal Slack Bot that lets you generate Stable Diffusion images.

    For installation instructions, see: https://github.com/steamship-core/python-client/blob/15bd58daf4da882dbbb26b8169a75145f9a920e9/src/steamship/agents/mixins/transports/slack.py#L165
    """

    USED_MIXIN_CLASSES = [SteamshipWidgetTransport, SlackTransport]

    class SlackBotBotConfig(Config):
        pass

    @classmethod
    def config_cls(cls) -> Type[Config]:
        return SlackBot.SlackBotBotConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # The agent's planner is responsible for making decisions about what to do for a given input.
        self._agent = FunctionsBasedAgent(
            tools=[StableDiffusionTool()],
            llm=ChatOpenAI(self.client, model_name=MODEL_NAME),
        )
        self._agent.PROMPT = SYSTEM_PROMPT

        # This Mixin provides HTTP endpoints that connects this agent to a web client
        self.add_mixin(
            SteamshipWidgetTransport(client=self.client, agent_service=self, agent=self._agent)
        )
        # This Mixin provides support for Telegram bots
        self.add_mixin(
            SlackTransport(
                client=self.client,
                config=SlackTransportConfig(),
                agent_service=self,
                agent=self._agent,
            )
        )


if __name__ == "__main__":
    AgentREPL(
        SlackBot,
        agent_package_config={},
    ).run()
