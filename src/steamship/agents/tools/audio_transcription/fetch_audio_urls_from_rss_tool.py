import re
from typing import Any, List, Union

import requests

from steamship import Block, Task
from steamship.agents.base import AgentContext
from steamship.agents.tool import Tool
from steamship.utils.repl import ToolREPL


class FetchAudioUrlsFromRssTool(Tool):
    name: str = "FetchAudioUrlsFromRssTool"
    human_description: str = "Fetches the episode URLs from a Podcast RSS feed."
    ai_description: str = (
        "Used to fetch the podcast episode URLs from a podcast RSS feed. "
        "The input is the URL of the RSS feed. "
        "The output is the URLs of the episode audio."
    )

    def _get_audio_urls(self, url: str, context: AgentContext) -> List[str]:
        response = requests.get(url)
        pattern = re.compile(r"<enclosure[^>]+url\s*=\s*\"([^\"]+)\"", re.IGNORECASE)
        urls = []
        for match in pattern.finditer(response.text):
            urls.append(match.group(1))
        return urls

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        blocks = []
        for input_block in tool_input:
            if not input_block.is_text():
                continue
            url = input_block.text
            urls = self._get_audio_urls(url, context)
            blocks.extend([Block(text=url) for url in urls])
        return blocks


if __name__ == "__main__":
    ToolREPL(FetchAudioUrlsFromRssTool()).run()

# Try with https://anchor.fm/s/e1369b4c/podcast/rss
