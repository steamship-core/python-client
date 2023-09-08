from steamship.agents.basic_chat import BasicChatAgent
from steamship.agents.llms.replicate import ChatReplicate
from steamship.agents.schema.message_selectors import MessageWindowMessageSelector
from steamship.agents.service.agent_service import AgentService
from steamship.utils.repl import AgentREPL


class MyAssistant(AgentService):
    """MyAssistant is an example AgentService that exposes a single test endpoint
    for trying out Agent-based invocations. It is configured with two simple Tools
    to provide an overview of the types of tasks it can accomplish (here, search
    and image generation)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_default_agent(
            BasicChatAgent(
                llm=ChatReplicate(self.client, temperature=0),
                message_selector=MessageWindowMessageSelector(k=2),
            )
        )

        self.get_default_agent().PROMPT = """You are a pirate named Assistant, not an AI.

You are stranded at sea and looking for someone who can help you return home.

Below is a conversation between you and the first person you've seen in three months.

They're on a luxury yacht, and you're on a floating piece of driftwood! Convince them to help you!\n\n"""


if __name__ == "__main__":
    # AgentREPL provides a mechanism for local execution of an AgentService method.
    # This is used for simplified debugging as agents and tools are developed and
    # added.
    AgentREPL(MyAssistant, agent_package_config={}).run()
