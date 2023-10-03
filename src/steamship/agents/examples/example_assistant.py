from typing import Type

from pydantic.fields import Field

from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.schema.message_selectors import MessageWindowMessageSelector
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.image_generation import DalleTool
from steamship.agents.tools.search import SearchTool
from steamship.invocable import Config
from steamship.utils.repl import AgentREPL


class MyFunctionsBasedAssistant(AgentService):
    """MyFunctionsBasedAssistant is an example AgentService that exposes a single test endpoint
    for trying out Agent-based invocations. It is configured with two simple Tools
    to provide an overview of the types of tasks it can accomplish (here, search
    and image generation)."""

    class AgentConfig(Config):
        model_name: str = Field(default="gpt-4")

    @classmethod
    def config_cls(cls) -> Type[Config]:
        return MyFunctionsBasedAssistant.AgentConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_default_agent(
            FunctionsBasedAgent(
                tools=[
                    SearchTool(),
                    DalleTool(),
                ],
                llm=ChatOpenAI(self.client, temperature=0, model_name=self.config.model_name),
                message_selector=MessageWindowMessageSelector(k=2),
            )
        )


if __name__ == "__main__":
    # AgentREPL provides a mechanism for local execution of an AgentService method.
    # This is used for simplified debugging as agents and tools are developed and
    # added.
    AgentREPL(MyFunctionsBasedAssistant, agent_package_config={"model_name": "gpt-3.5-turbo"}).run(
        dump_history_on_exit=True
    )
