from typing import List, Optional

from steamship import Block, File, PluginInstance, Steamship
from steamship.agents.schema import LLM, ChatLLM, Tool

PLUGIN_HANDLE = "gpt-4"
DEFAULT_MAX_TOKENS = 256


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

        Supported kwargs include:
        - `max_tokens` (controls the size of LLM responses)
        """
        client = client
        max_tokens = DEFAULT_MAX_TOKENS
        if "max_tokens" in kwargs:
            max_tokens = kwargs["max_tokens"]

        generator = client.use_plugin(
            PLUGIN_HANDLE,
            config={"model": model_name, "temperature": temperature, "max_tokens": max_tokens},
        )
        super().__init__(client=client, generator=generator, *args, **kwargs)

    def complete(self, prompt: str, stop: Optional[str] = None, **kwargs) -> List[Block]:
        """Completes the prompt, respecting the supplied stop sequence.

        Supported kwargs include:
        - `max_tokens` (controls the size of LLM responses)
        """
        options = {}
        if stop:
            options["stop"] = stop

        if "max_tokens" in kwargs:
            options["max_tokens"] = kwargs["max_tokens"]

        action_task = self.generator.generate(text=prompt, options=options)
        action_task.wait()
        return action_task.output.blocks


class ChatOpenAI(ChatLLM, OpenAI):
    """ChatLLM that uses Steamship's OpenAI plugin to generate chat completions."""

    def __init__(self, client, model_name: str = "gpt-4-0613", *args, **kwargs):
        """Create a new instance.

        Valid model names are:
         - gpt-4
         - gpt-4-0613

        Supported kwargs include:
        - `max_tokens` (controls the size of LLM responses)
        """
        super().__init__(client=client, model_name=model_name, *args, **kwargs)

    def chat(self, messages: List[Block], tools: Optional[List[Tool]], **kwargs) -> List[Block]:
        """Sends chat messages to the LLM with functions from the supplied tools in a side-channel.

        Supported kwargs include:
        - `max_tokens` (controls the size of LLM responses)
        """

        temp_file = File.create(client=self.client, blocks=messages)

        options = {}
        if len(tools) > 0:
            functions = []
            for tool in tools:
                functions.append(tool.as_openai_function())
            options["functions"] = functions

        if "max_tokens" in kwargs:
            options["max_tokens"] = kwargs["max_tokens"]

        tool_selection_task = self.generator.generate(input_file_id=temp_file.id, options=options)
        tool_selection_task.wait()
        return tool_selection_task.output.blocks
