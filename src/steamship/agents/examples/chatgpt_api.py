"""Minimum viable AgentService implementation.

This will result in an agent that effectively acts like ChatGPT.
"""

from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.service.agent_service import AgentService
from steamship.utils.repl import AgentREPL


class MyAssistant(AgentService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_default_agent(FunctionsBasedAgent(llm=ChatOpenAI(self.client), tools=[]))


if __name__ == "__main__":
    AgentREPL(
        MyAssistant,
        agent_package_config={},
    ).run()
