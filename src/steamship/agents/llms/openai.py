from typing import List, Optional

from steamship import Block, File, PluginInstance, Steamship
from steamship.agents.schema import LLM, ConversationalLLM, Tool

PLUGIN_HANDLE = "doug-gpt-four"


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


# TODO(dougreid): should this be a an extension of a BaseOpenAI or similar? Or completely separate?
class ChatOpenAI(ConversationalLLM):
    """LLM that uses Steamship's OpenAI plugin to generate completions.

    NOTE: By default, this LLM uses the `gpt-3.5-turbo` model. Valid model
    choices are `gpt-3.5-turbo` and `gpt-4`.
    """

    generator: PluginInstance
    client: Steamship

    def __init__(
        self, client, model_name: str = "gpt-4-0613", temperature: float = 0.4, *args, **kwargs
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

    def converse(self, messages: List[Block], tools: Optional[List[Tool]]) -> List[Block]:
        # TODO(dougreid): this feels icky. find a better way?
        temp_file = File.create(client=self.client, blocks=messages)
        options = {}
        if len(tools) > 0:
            functions = []
            for tool in tools:
                functions.append(tool.as_openai_function())
            options["functions"] = functions

        action_task = self.generator.generate(input_file_id=temp_file.id, options=options)
        action_task.wait()
        return action_task.output.blocks
