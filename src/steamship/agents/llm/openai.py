from typing import List

from steamship import Block, PluginInstance, Steamship
from steamship.agents.base import LLM

PLUGIN_HANDLE = "gpt-4"


class OpenAI(LLM):
    generator: PluginInstance
    client: Steamship

    def __init__(self, client, model_name: str = "gpt-3.5-turbo", *args, **kwargs):
        """Create a new instance.

        Valid model names are:
         - gpt-4
         - gpt-3.5-turbo
        """
        client = client
        generator = client.use_plugin(PLUGIN_HANDLE, config={"model": model_name})
        super().__init__(client=client, generator=generator, *args, **kwargs)

    def complete(self, prompt: str, stop: str) -> List[Block]:
        action_task = self.generator.generate(text=prompt, options={"stop": stop})
        action_task.wait()
        return action_task.output.blocks
