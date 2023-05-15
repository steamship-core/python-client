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

    def should_preempt_agent(self, prompt: str) -> float:
        """Preempt when an inbound message begins with 'dalle '."""
        if prompt.strip().startswith("dalle "):
            return 1.0
        return 0.0

    def preempt_agent_prompt(self, prompt: str) -> str:
        """Stripe 'dalle ' from the inbound message."""
        prefix = "dalle "
        if prompt.startswith(prefix):
            prompt = prompt[len(prefix) :]

        return prompt.strip()

    def run(self, prompt: str) -> str:
        """Respond to LLM prompt."""
        logging.info(f"[{self.name}] {prompt}")
        if not isinstance(prompt, str):
            prompt = json.dumps(prompt)
        task = self.dalle.generate(text=prompt, append_output_to_file=True)
        task.wait()
        blocks = task.output.blocks
        logging.info(f"[{self.name}] got back {len(blocks)} blocks")
        if len(blocks) > 0:
            logging.info(f"[{self.name}] image size: {len(blocks[0].raw())}")
            return blocks[0].id
        raise SteamshipError(f"[{self.name}] Tool unable to generate image!")
