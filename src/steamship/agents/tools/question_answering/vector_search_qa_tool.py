"""Answers questions with the assistance of a VectorSearch plugin."""
from typing import List

from steamship import Block
from steamship.agents.agent_context import AgentContext, DebugAgentContext
from steamship.agents.agents import Tool
from steamship.agents.debugging import tool_repl


class VectorSearchQATool(Tool):
    """Tool to answer questions with the assistance of a vector search plugin."""

    embedding_index_instance_handle: str

    def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
        """Answers questions with the assistance of an Embedding Index plugin.

        Inputs
        ------
        input: List[Block]
            A list of blocks to be rewritten if text-containing.
        context: AgentContext
            The active AgentContext.

        Output
        ------
        output: List[Blocks]
            A lit of blocks containing the answers.
        """

        # Assumed at this point to be an image generator.
        generator = context.client.use_plugin(
            plugin_handle="dall-e", config={"n": 1, "size": "256x256"}
        )

        output = []
        for block in tool_input:
            if not block.is_text():
                continue

            prompt = block.text
            task = generator.generate(text=prompt, append_output_to_file=True)
            task.wait()
            blocks = task.output.blocks

            context.append_log(f"[{self.name}] got back {len(blocks)} blocks")
            if len(blocks) > 0:
                context.append_log(f"[{self.name}] image size: {len(blocks[0].raw())}")
                # TODO: This is how we were doing it.. but it feels like with this new interface
                # perhaps we should return the actual block?
                output.append(Block(text=f"{blocks[0].id}"))

        return output


def main():
    with DebugAgentContext.temporary() as context:
        tool = VectorSearchQATool()
        tool_repl(tool, context)


if __name__ == "__main__":
    main()
