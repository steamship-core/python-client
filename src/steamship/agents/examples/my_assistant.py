import uuid
from typing import List

from steamship import Block
from steamship.agents.llms.openai import OpenAI
from steamship.agents.react import ReACTAgent
from steamship.agents.schema import AgentContext
from steamship.agents.schema.context import Metadata
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.image_generation import DalleTool
from steamship.agents.tools.search import SearchTool
from steamship.invocable import post
from steamship.utils.repl import AgentREPL


class MyAssistant(AgentService):
    """MyAssistant is an example AgentService that exposes a single test endpoint
    for trying out Agent-based invocations. It is configured with two simple Tools
    to provide an overview of the types of tasks it can accomplish (here, search
    and image generation)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._agent = ReACTAgent(
            tools=[
                SearchTool(),
                DalleTool(),
            ],
            llm=OpenAI(self.client),
        )

    @post("prompt")
    def prompt(self, prompt: str) -> str:
        """Run an agent with the provided text as the input."""

        # AgentContexts serve to allow the AgentService to run agents
        # with appropriate information about the desired tasking.
        # Here, we create a new context on each prompt, and append the
        # prompt to the message history stored in the context.
        context_id = uuid.uuid4()
        context = AgentContext.get_or_create(self.client, {"id": f"{context_id}"})
        context.chat_history.append_user_message(prompt)

        # AgentServices provide an emit function hook to access the output of running
        # agents and tools. The emit functions fire at after the supplied agent emits
        # a "FinishAction".
        #
        # Here, we show one way of accessing the output in a synchronous fashion. An
        # alternative way would be to access the final Action in the `context.completed_steps`
        # after the call to `run_agent()`.
        output = ""

        def sync_emit(blocks: List[Block], meta: Metadata):
            nonlocal output
            block_text = "\n".join(
                [b.text if b.is_text() else f"({b.mime_type}: {b.id})" for b in blocks]
            )
            output += block_text

        context.emit_funcs.append(sync_emit)
        self.run_agent(self._agent, context)
        return output


if __name__ == "__main__":
    # AgentREPL provides a mechanism for local execution of an AgentService method.
    # This is used for simplified debugging as agents and tools are developed and
    # added.
    AgentREPL(MyAssistant, "prompt", agent_package_config={}).run()
