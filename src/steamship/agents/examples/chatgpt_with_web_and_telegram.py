from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.service.agent_service import AgentService
from steamship.utils.repl import AgentREPL


class ChatGpt(AgentService):
    """Minimal implementation of an Agent that just chats with you via the web."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # The agent's planner is responsible for making decisions about what to do for a given input.
        self.set_default_agent(
            FunctionsBasedAgent(
                tools=[],
                llm=ChatOpenAI(self.client, model_name="gpt-4"),
            )
        )

        # This Mixin provides HTTP endpoints that connects this agent to a web client
        self.add_mixin(SteamshipWidgetTransport(client=self.client, agent_service=self))


if __name__ == "__main__":
    AgentREPL(
        ChatGpt,
        agent_package_config={"botToken": "not-a-real-token-for-local-testing"},
    ).run()
