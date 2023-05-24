import uuid
from typing import List

from steamship import Block
from steamship.agents.llms.openai import OpenAI
from steamship.agents.react import ReACTAgent
from steamship.agents.schema import AgentContext
from steamship.agents.schema.context import Metadata
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.image_generation.dalle import DalleTool
from steamship.agents.tools.search.search import SearchTool
from steamship.invocable import post
from steamship.utils.repl import AgentREPL


class MyAssistant(AgentService):
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
        context_id = uuid.uuid4()
        context = AgentContext.get_or_create(self.client, {"id": f"{context_id}"})
        context.chat_history.append_user_message(prompt)

        # TODO: is this preferred over taking the last step in completed step?
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
    AgentREPL(MyAssistant, "prompt", agent_package_config={}).run()
