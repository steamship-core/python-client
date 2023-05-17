"""Tool for generating images."""
from typing import List

import requests

from steamship import Block, File, MimeTypes
from steamship.agents.agent_context import AgentContext
from steamship.tools.tool import Tool, ToolOutput
from steamship.utils.repl import ToolREPL


class ScrapeAudioTool(Tool):
    """Scrapes audio from a URL."""

    name: str = "ScrapeAudioTool"
    human_description: str = "Scrapes audio from a URL."
    ai_description: str = (
        "Used to download audio from a URL. "
        "The input is a URL to download audio from. "
        "The output is the audio file that was downloaded."
    )

    def run(self, tool_input: List[Block], context: AgentContext) -> ToolOutput:
        output_blocks = []
        for input_block in tool_input:
            if input_block.is_text():
                url = input_block.text
                response = requests.get(url)
                # TODO: We shouldn't assume it's MP3, but checking the mime-type is rather intensive and involves
                # importing other libraries. This would feel a lot better as some Engine-supported operation.

                # This isn't a good solution, but just to get to something somewhat workable..
                file = File.create(context.client)
                block = Block.create(
                    context.client,
                    file_id=file.id,
                    content=response.content,
                    mime_type=MimeTypes.MP3,
                )
                output_blocks.append(block)

        return output_blocks


if __name__ == "__main__":
    ToolREPL(ScrapeAudioTool()).run()
