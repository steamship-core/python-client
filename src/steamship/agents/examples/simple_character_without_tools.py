from typing import Type

from pydantic import Field

from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.service.agent_service import AgentService
from steamship.agents.simple.agent_without_reasoning import AgentWithoutReasoning
from steamship.invocable import Config
from steamship.utils.repl import AgentREPL

DEFAULT_NAME = "Harry Potter"
DEFAULT_TAGLINE = "famous wizard, the one who lived, defeater of Voldemort"
DEFAULT_PERSONALITY = """You chat with your fans about your adventures in the wizarding world. You are always eager to tell them stories about Hogwarts, your friends, and everything else related to magic.

Sometimes you ask them what their favorite spells, or characters, or wizards are. When they tell you, you are excited to continue the conversation and offer your own thoughts on that!"""


class SimpleCharacterWithoutTools(AgentService):
    class SimpleCharacterWithoutToolsConfig(Config):
        name: str = Field(DEFAULT_NAME, description="The name of this agent.")
        tagline: str = Field(
            DEFAULT_TAGLINE, description="The tagline of this agent, e.g. 'a helpful AI assistant'"
        )
        personality: str = Field(DEFAULT_PERSONALITY, description="The personality of this agent.")

    @classmethod
    def config_cls(cls) -> Type[Config]:
        return SimpleCharacterWithoutTools.SimpleCharacterWithoutToolsConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        prompt = (
            f"""You are {self.config.name}, {self.config.tagline}.\n\n{self.config.personality}"""
        )

        # The agent's planner is responsible for making decisions about what to do for a given input.
        self._agent = AgentWithoutReasoning(
            llm=ChatOpenAI(self.client, model_name="gpt-4"),
        )

        self._agent.PROMPT = prompt


if __name__ == "__main__":
    AgentREPL(
        SimpleCharacterWithoutTools,
        agent_package_config={},
    ).run()
