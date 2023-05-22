from typing import List

from steamship import Block, PluginInstance, Steamship
from steamship.agents.base import LLM


class OpenAI(LLM):
    generator: PluginInstance
    client: Steamship

    def __init__(self, client, *args, **kwargs):
        client = client
        generator = client.use_plugin("gpt-4")
        super().__init__(client=client, generator=generator, *args, **kwargs)

    def complete(self, prompt: str, stop: str) -> List[Block]:
        action_task = self.generator.generate(text=prompt, options={"stop": stop})
        action_task.wait()
        return action_task.output.blocks
