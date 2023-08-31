from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.schema.message_selectors import MessageWindowMessageSelector
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.image_generation import DalleTool
from steamship.agents.tools.search import SearchTool
from steamship.data import TagValueKey
from steamship.invocable import post
from steamship.utils.kv_store import KeyValueStore
from steamship.utils.repl import AgentREPL


class MyCachingAssistant(AgentService):
    """MyCachingAssistant is an example AgentService that exposes a single test endpoint
    for trying out Agent-based invocations. It is configured with two simple Tools
    to provide an overview of the types of tasks it can accomplish (here, search
    and image generation)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs, use_llm_cache=True, use_action_cache=True)

        # Load the max_actions_per_run from the saved store for use in testing.
        self.kv = KeyValueStore(self.client)
        self.max_actions_per_run = self.get_max_actions_per_run()

        self.set_default_agent(
            FunctionsBasedAgent(
                tools=[
                    SearchTool(),
                    DalleTool(),
                ],
                llm=ChatOpenAI(self.client, temperature=0),
                message_selector=MessageWindowMessageSelector(k=2),
            )
        )

    @post("set_max_actions_per_run")
    def set_max_actions_per_run(self, value: int):
        """Save the max_actions_per_run value so that it will be reloaded upon next request."""
        self.max_actions_per_run = self.kv.set(
            "max_actions_per_run", {TagValueKey.NUMBER_VALUE: value}
        )
        return value

    @post("get_max_actions_per_run")
    def get_max_actions_per_run(self) -> int:
        """Save the max_actions_per_run value so that it will be reloaded upon next request."""
        return (self.kv.get("max_actions_per_run") or {}).get(TagValueKey.NUMBER_VALUE, 5)


if __name__ == "__main__":
    # AgentREPL provides a mechanism for local execution of an AgentService method.
    # This is used for simplified debugging as agents and tools are developed and
    # added.
    AgentREPL(MyCachingAssistant, agent_package_config={}).run()
