"""Tool for generating images."""
import json
import logging
from typing import Optional

from steamship import Steamship
from steamship.base.error import SteamshipError
from steamship.experimental.tools.tool import Tool


class GenerateImageTool(Tool):
    """Tool used to generate images from a text-prompt."""

    name: str = "GenerateImages"
    description: str = (
        "Used to generate images from text prompts. Only use if the user has asked directly for an "
        "image. When using this tool, the input should be a plain text string that describes, "
        "in detail, the desired image."
    )

    client: Steamship

    def __init__(self, client: Steamship, plugin_handle: Optional[str] = "dall-e"):
        self.plugin_handle = plugin_handle
        self.client = client
        self.dalle = client.use_plugin(
            plugin_handle=self.plugin_handle, config={"n": 1, "size": "256x256"}
        )

    def run(self, prompt: str) -> str:
        """Respond to LLM prompt."""
        logging.info(f"[dall-e] {prompt}")
        if not isinstance(prompt, str):
            prompt = json.dumps(prompt)
        task = self.dalle.generate(text=prompt, append_output_to_file=True)
        task.wait()
        blocks = task.output.blocks
        logging.info(f"[dall-e] got back {len(blocks)} blocks")
        if len(blocks) > 0:
            logging.info(f"[dall-e] image size: {len(blocks[0].raw())}")
            return blocks[0].id
        raise SteamshipError("could not generate image!")
