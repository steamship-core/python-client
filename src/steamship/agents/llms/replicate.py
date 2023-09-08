from typing import List, Optional

from steamship import Block, PluginInstance, Steamship
from steamship.agents.schema import LLM
from steamship.utils.dict_utils import remove_none

PLUGIN_HANDLE = "replicate-llm"
DEFAULT_MAX_TOKENS = 256

LLAMA_2_70B = "replicate/llama-2-70b-chat"
DOLLY_2_12B = "replicate/dolly-v2-12b"

DEFAULT_MODEL = LLAMA_2_70B


class Replicate(LLM):
    """LLM that uses Steamship's Replicate plugin to generate completions.

    The default model is Llama 2 70B.

    See the Replicate plugin source code for more information:
      https://github.com/steamship-plugins/replicate-llms
    """

    generator: PluginInstance
    client: Steamship

    def __init__(
        self,
        client,
        model_name: str = None,  # The default in the plugin is LLAMA_2_70B.
        temperature: float = None,
        model_version: Optional[str] = None,
        default_system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        stop_sequences: Optional[str] = None,  # Should be a CSV string
        *args,
        **kwargs
    ):
        """Create a new instance.

        Valid model names are presently:
         - replicate/llama-2-70b-chat
         - replicate/dolly-v2-12b
        """

        # TODO: We've got whatever the opposite of an encapsulation leak here, in that this is all strongly typed
        # and defined in the Replicate plugin, yet we can't refer to it here.
        #
        # One side-step approach might be to strongly type LLM configuration in the python-client repository, since
        # it tends to be mostly stable across LLM providers, and then we can refer to it from plugins, inverting the
        # location of definition.
        replicate_config = remove_none(
            {
                "model_name": model_name,
                "model_version": model_version,
                "default_system_prompt": default_system_prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stop_sequences": stop_sequences,
            }
        )

        generator = client.use_plugin(PLUGIN_HANDLE, replicate_config)
        super().__init__(client=client, generator=generator, **kwargs)

    def complete(self, prompt: str, **kwargs) -> List[Block]:
        """Completes the prompt."""
        options = remove_none(
            {
                "model_name": kwargs.get("model_name", None),
                "model_version": kwargs.get("model_version", None),
                "default_system_prompt": kwargs.get("default_system_prompt", None),
                "max_tokens": kwargs.get("max_tokens", None),
                "temperature": kwargs.get("temperature", None),
                "top_p": kwargs.get("top_p", None),
                "stop_sequences": kwargs.get("stop_sequences", None),
            }
        )
        action_task = self.generator.generate(text=prompt, options=options)
        action_task.wait()
        return action_task.output.blocks
