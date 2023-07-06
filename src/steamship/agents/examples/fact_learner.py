from steamship.agents.llms.openai import OpenAI
from steamship.agents.react import ReACTAgent
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.question_answering import VectorSearchQATool
from steamship.agents.tools.question_answering.vector_search_learner_tool import (
    VectorSearchLearnerTool,
)
from steamship.utils.repl import AgentREPL

# Use either "gpt-3.5-turbo-0613" or "gpt-4-0613" here.
# Other versions of GPT tend not to work well with the ReAct prompt.
MODEL_NAME = "gpt-4-0613"


class FactLearner(AgentService):
    """FactLearner is an example AgentService contains an Agent which:

    1) Learns facts to a vector store
    2) Can answer questions based on those facts"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._agent = ReACTAgent(
            tools=[
                VectorSearchLearnerTool(),
                VectorSearchQATool(),
            ],
            llm=OpenAI(self.client, model_name=MODEL_NAME),
        )


if __name__ == "__main__":
    # AgentREPL provides a mechanism for local execution of an AgentService method.
    # This is used for simplified debugging as agents and tools are developed and
    # added.
    AgentREPL(FactLearner, agent_package_config={}).run()
