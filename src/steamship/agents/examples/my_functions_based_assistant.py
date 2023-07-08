import uuid

from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.schema.message_selectors import MessageWindowMessageSelector
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.image_generation import DalleTool
from steamship.agents.tools.search import SearchTool
from steamship.utils.repl import AgentREPL


class MyFunctionsBasedAssistant(AgentService):
    """MyFunctionsBasedAssistant is an example AgentService that exposes a single test endpoint
    for trying out Agent-based invocations. It is configured with two simple Tools
    to provide an overview of the types of tasks it can accomplish (here, search
    and image generation)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._agent = FunctionsBasedAgent(
            tools=[
                SearchTool(),
                DalleTool(),
            ],
            llm=ChatOpenAI(self.client, temperature=0),
            conversation_memory=MessageWindowMessageSelector(k=2),
        )


if __name__ == "__main__":
    # AgentREPL provides a mechanism for local execution of an AgentService method.
    # This is used for simplified debugging as agents and tools are developed and
    # added.
    AgentREPL(MyFunctionsBasedAssistant, agent_package_config={}).run(context_id=uuid.uuid4())
