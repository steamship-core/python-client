from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.question_answering import VectorSearchQATool
from steamship.agents.tools.question_answering.vector_search_learner_tool import (
    VectorSearchLearnerTool,
)
from steamship.utils.repl import AgentREPL


class FactLearner(AgentService):
    """FactLearner is an example AgentService contains an Agent which:

    1) Learns facts to a vector store
    2) Can answer questions based on those facts"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._agent = FunctionsBasedAgent(
            tools=[
                VectorSearchLearnerTool(),
                VectorSearchQATool(),
            ],
            llm=ChatOpenAI(self.client),
        )


if __name__ == "__main__":
    # AgentREPL provides a mechanism for local execution of an AgentService method.
    # This is used for simplified debugging as agents and tools are developed and
    # added.
    AgentREPL(FactLearner, agent_package_config={}).run()
