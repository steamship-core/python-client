from typing import List, Optional

from steamship import Block, PluginInstance, Steamship
from steamship.agents.schema import LLM

PLUGIN_HANDLE = "gpt-4"


class OpenAI(LLM):
    """LLM that uses Steamship's OpenAI plugin to generate completions.

    NOTE: By default, this LLM uses the `gpt-3.5-turbo` model. Valid model
    choices are `gpt-3.5-turbo` and `gpt-4`.
    """

    generator: PluginInstance
    client: Steamship

    def __init__(
        self, client, model_name: str = "gpt-3.5-turbo", temperature: float = 0.4, *args, **kwargs
    ):
        """Create a new instance.

        Valid model names are:
         - gpt-4
         - gpt-3.5-turbo
        """
        client = client
        generator = client.use_plugin(
            PLUGIN_HANDLE, config={"model": model_name, "temperature": temperature}
        )
        super().__init__(client=client, generator=generator, *args, **kwargs)

    def complete(self, prompt: str, stop: Optional[str] = None) -> List[Block]:
        options = {}
        if stop:
            options["stop"] = stop
        action_task = self.generator.generate(text=prompt, options=options)
        action_task.wait()
        return action_task.output.blocks
