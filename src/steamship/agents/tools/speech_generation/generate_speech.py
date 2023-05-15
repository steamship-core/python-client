"""Tool for generating images."""
from typing import List

from steamship import Block
from steamship.agents.agent_context import AgentContext, DebugAgentContext
from steamship.agents.agents import Tool
from steamship.agents.debugging import tool_repl


class GenerateSpeechTool(Tool):
    """Tool to generate audio from text."""

    def __init__(self, **kwargs):
        """Generates audio from text."""
        kwargs["name"] = kwargs.get("name", "GenerateSpokenAudio")
        kwargs["human_description"] = kwargs.get(
            "human_description", "Generates spoken audio from text."
        )
        kwargs["ai_description"] = kwargs.get(
            "ai_description",
            (
                "Used to generate spoken audio from text prompts. Only use if the user has asked directly for a "
                "an audio version of output. When using this tool, the input should be a plain text string containing the "
                "content to be spoken."
            ),
        )
        super().__init__(**kwargs)

    def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
        """Generates audio for each text block provided.

        Waits, synchronously, for completion.
        TODO: We should probably make this async.

        Inputs
        ------
        input: List[Block]
            A list of blocks to be rewritten if text-containing.
        context: AgentContext
            The active AgentContext.

        Output
        ------
        output: List[Blocks]
            A list of blocks containing audio content.
        """

        # TODO: Make this an option in the tool
        plugin_handle = "elevenlabs"

        # Assumed at this point to be an audio generator.
        generator = context.client.use_plugin(plugin_handle=plugin_handle, config={})

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
                context.append_log(f"[{self.name}] audio size: {len(blocks[0].raw())}")
                # TODO: This is how we were doing it.. but it feels like with this new interface
                # perhaps we should return the actual block?
                output.append(Block(text=f"{blocks[0].id}"))

        return output


def main():
    with DebugAgentContext.temporary() as context:
        tool = GenerateSpeechTool()
        tool_repl(tool, context)


if __name__ == "__main__":
    main()
