from typing import List

from steamship import Block, PluginInstance, Steamship
from steamship.agents.base import LLM


class OpenAI(LLM):
    generator: PluginInstance
    client: Steamship

    def __init__(self, client, model_name: str, *args, **kwargs):
        client = client
        generator = client.use_plugin(model_name)
        super().__init__(client=client, generator=generator, *args, **kwargs)

    def complete(self, prompt: str, stop: str) -> List[Block]:
        action_task = self.generator.generate(text=prompt, options={"stop": stop})
        action_task.wait()
        return action_task.output.blocks
