from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.schema import MessageWindowMessageSelector
from steamship.agents.service import AgentService
from steamship.agents.tools.search import SearchTool


class AgentWithSearchTool(AgentService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._agent = FunctionsBasedAgent(
            tools=[
                # Adding this tool will make Internet searching via the SERP API part of
                # your agent's capabilities. The `SearchTool` uses Steamship's SERP API
                # key for executing searches. There is no need to set up a separate account.
                #
                # If you have other tools you wish to use with your agent, you may add
                # them here in a similar fashion.
                SearchTool(),
            ],
            llm=ChatOpenAI(self.client, temperature=0),
            conversation_memory=MessageWindowMessageSelector(k=2),
        )
