"""Tool for generating images."""
from typing import List

from steamship import Block
from steamship.agents.agent_context import AgentContext, DebugAgentContext
from steamship.agents.agents import Tool
from steamship.agents.debugging import tool_repl


class GenerateSpeechTool(Tool):
    """Tool to generate audio from text."""

    name: str = "GenerateSpokenAudio"
    human_description: str = "Generates spoken audio from text."
    ai_description: str = (
        "Used to generate spoken audio from text prompts. Only use if the user has asked directly for a "
        "an audio version of output. When using this tool, the input should be a plain text string containing the "
        "content to be spoken."
    )

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
            for output_block in blocks:
                if output_block.is_audio():
                    output.append(output_block)

        return output


def main():
    with DebugAgentContext.temporary() as context:
        tool = GenerateSpeechTool()
        tool_repl(tool, context)


if __name__ == "__main__":
    main()
