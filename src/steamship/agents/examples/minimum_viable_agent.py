"""Minimum viable AgentService implementation.

This will result in an agent that effectively acts like ChatGPT.
"""

from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.service.agent_service import AgentService


class MyAssistant(AgentService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._agent = FunctionsBasedAgent(llm=ChatOpenAI(self.client), tools=[])
