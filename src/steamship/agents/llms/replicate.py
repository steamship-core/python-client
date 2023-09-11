import abc
import logging
from abc import ABC
from typing import List, Optional, Union

from steamship import Block, PluginInstance, Steamship, SteamshipError
from steamship.agents.schema import LLM, Tool
from steamship.utils.dict_utils import remove_none

PLUGIN_HANDLE = "replicate-llm"
DEFAULT_MAX_TOKENS = 256

LLAMA_2_70B = "replicate/llama-2-70b-chat"
DOLLY_2_12B = "replicate/dolly-v2-12b"

VALID_LLAMA_MODELS = [LLAMA_2_70B]

DEFAULT_MODEL = LLAMA_2_70B

ACCEPTED_PARAMETERS = [
    "model_name",
    "model_version",
    "default_system_prompt",
    "max_tokens",
    "temperature",
    "top_p",
    "stop_sequences",
]


def dict_subset(d: dict, keys: List[str]) -> dict:
    """Return the dired not None subset of a dict"""
    return dict((k, d[k]) for k in keys if k in d and d[k] is not None)


def kwargs_to_params(d: dict) -> dict:
    return dict_subset(d, ACCEPTED_PARAMETERS)


class PromptFormatter(ABC):
    """Base class for a Replicate Prompt Formatter.

    Note that this is expected to be replaced by a future PromptFormatter class."""

    @abc.abstractmethod
    def format(self, message: str, tools: List[Tool] = None) -> Union[List[Block], str]:
        pass


class ReplicateBase(LLM):
    """LLM that uses Steamship's Replicate plugin to generate completions.

    See the Replicate plugin source code for more information:
      https://github.com/steamship-plugins/replicate-llms
    """

    generator: PluginInstance
    client: Steamship

    def __init__(self, client, **kwargs):
        replicate_config = kwargs_to_params(kwargs)
        generator = client.use_plugin(PLUGIN_HANDLE, config=replicate_config)
        super().__init__(client=client, generator=generator, **kwargs)

    def generate(
        self,
        prompt: str,
        **kwargs,
    ) -> List[Block]:
        """Completes the prompt."""
        options = kwargs_to_params(kwargs)
        action_task = self.generator.generate(text=prompt, options=options)
        action_task.wait()
        return action_task.output.blocks


class LlamaPromptFormatter(PromptFormatter):
    """Prompt formatter for Llama models.

    Behaviors:
      - Acts as a stateless (message: str) -> (completion: str) pass through.
      - No chat history, chat semantics, etc are applied
      - Forbids tools, which do not work well with Llama.
    """

    block_delimiter: str = "\n\n"

    def format(self, blocks: List[Block], tools: List[Tool] = None) -> Union[List[Block], str]:
        if tools:
            raise SteamshipError(message="This LLM does not support Tool usage.")
        return self.block_delimiter.join([block.text for block in blocks])


class LlamaChatFormatter(PromptFormatter):
    """Chat-style formatter for Llama models.

    Behaviors:
      - Acts as a chat completion formatter for Llama models.
      - No chat history, chat semantics, etc are applied
      - Forbids tools, which do not work well with Llama.
    """

    def format(self, message: List[Block], tools: List[Tool] = None) -> Union[List[Block], str]:
        if tools:
            raise SteamshipError(message="This LLM does not support Tool usage.")

        # TODO: Format a return value that has the LLAMA-style Chat markup based on tags that are on the blocks.

        return ""


class Llama(ReplicateBase):
    """Llama LLM, hosted on Replicate.

    We list the
    """

    def __init__(
        self,
        client,
        model_name: str = LLAMA_2_70B,
        temperature: float = None,
        model_version: Optional[str] = None,
        default_system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        stop_sequences: Optional[str] = None,  # Should be a CSV string,
        **kwargs,
    ):
        if model_name not in VALID_LLAMA_MODELS:
            logging.warning(f"{model_name} is not listed as a valid Llama model.")

        # Collapse the arguments into a single dict to pass up to the parent.
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
        replicate_config.update(kwargs)
        super().__init__(client, **replicate_config)

    def generate(
        self,
        prompt: str,
        model_name: str = None,  # The default in the plugin is LLAMA_2_70B.
        temperature: float = None,
        model_version: Optional[str] = None,
        default_system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        stop_sequences: Optional[str] = None,  # Should be a CSV string
        **kwargs,
    ) -> List[Block]:
        """Completes the prompt."""
        options = remove_none(
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
        action_task = self.generator.generate(text=prompt, options=options)
        action_task.wait()
        return action_task.output.blocks
