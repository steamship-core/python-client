"""Tool for generating images."""
import json
import logging
from typing import Optional

from steamship import Steamship
from steamship.base.error import SteamshipError
from steamship.experimental.tools.tool import Tool


class GenerateSpeechTool(Tool):
    """Tool used to generate images from a text-prompt."""

    name: str = "GenerateSpokenAudio"
    description: str = (
        "Used to generate spoken audio from text prompts. Only use if the user has asked directly for a "
        "an audio version of output. When using this tool, the input should be a plain text string containing the "
        "content to be spoken."
    )

    client: Steamship

    def __init__(self, client: Steamship, plugin_handle: Optional[str] = "elevenlabs"):
        self.plugin_handle = plugin_handle
        self.client = client
        self.elevenlabs = client.use_plugin(plugin_handle=self.plugin_handle, config={})

    def should_preempt_agent(self, prompt: str) -> float:
        """Preempt when an inbound message begins with 'speak '."""
        if prompt.strip().startswith("speak "):
            return 1.0
        return 0.0

    def preempt_agent_prompt(self, prompt: str) -> str:
        """Stripe 'speak ' from the inbound message."""
        prefix = "speak "
        if prompt.startswith(prefix):
            prompt = prompt[len(prefix) :]

        return prompt.strip()

    def run(self, prompt: str) -> str:
        """Respond to LLM prompt."""
        logging.info(f"[{self.name}] {prompt}")
        if not isinstance(prompt, str):
            prompt = json.dumps(prompt)
        task = self.elevenlabs.generate(text=prompt, append_output_to_file=True)
        task.wait()
        blocks = task.output.blocks
        logging.info(f"[{self.name}] got back {len(blocks)} blocks")
        if len(blocks) > 0:
            logging.info(f"[{self.name}] audio size: {len(blocks[0].raw())}")
            return blocks[0].id
        raise SteamshipError(f"[{self.name}] Tool unable to generate audio!")
