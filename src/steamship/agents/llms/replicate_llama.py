"""LLM classes for  connecting to Llama via Steamship's `replicate-llm` Plugin."""
import logging
from typing import List, Optional, Union

from steamship import Block, PluginInstance, Steamship, SteamshipError
from steamship.agents.schema import LLM, ChatLLM
from steamship.agents.schema.tool import Tool
from steamship.data.tags.tag_constants import RoleTag
from steamship.utils.dict_utils import remove_none

PLUGIN_HANDLE = "replicate-llm"

LLAMA_2_70B = "replicate/llama-2-70b-chat"

# We list the supported Llama models here so we can log a warning if the provided model is not in one of them.
# This is important because things such as prompt formatting may fail if misaligned with the specific LLM.
VALID_LLAMA_MODELS = [LLAMA_2_70B]


class Llama(LLM):
    """LLama LLM without chat semantics.

    - Use this class if you are seeking raw prompt completion.
    - If you are building a chatbot, you want LlamaChat, which implements Llama's chat semantics.

    Uses Steamship's Replicate plugin for inference: https://github.com/steamship-plugins/replicate-llms
    """

    generator: PluginInstance
    client: Steamship
    block_delimiter: str = "\n\n"

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
        print(replicate_config)
        replicate_config.update(kwargs)
        generator = client.use_plugin(PLUGIN_HANDLE, config=remove_none(kwargs))
        super().__init__(client=client, generator=generator, **kwargs)

    def format_prompt(self, blocks: List[Block]) -> str:
        """The basic Llama usage is not trained for chat.

        - It simply accepts blocks as raw text and performs a completion.
        - No tools are supported (note their absense in the type signature)

        Here, we collapse all the provided blocks together using a delimeter."""
        return self.block_delimiter.join([block.text for block in blocks])

    def complete(
        self,
        prompt: Union[str, List[Block]],
        model_name: str = None,  # The default in the plugin is LLAMA_2_70B.
        temperature: float = None,
        model_version: Optional[str] = None,
        default_system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        stop_sequences: Optional[str] = None,  # Should be a CSV string
        **kwargs,
    ) -> List[Block]:
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

        if isinstance(prompt, str):
            input_text = prompt
        else:
            input_text = self.format_prompt(prompt)

        action_task = self.generator.generate(text=input_text, options=remove_none(options))
        action_task.wait()
        return action_task.output.blocks


class LlamaChat(ChatLLM, Llama):
    """Llama Chat LLM: A Chat-tuned LLM hoted on Replicate.

    This variant of Llama uses knowledge of the chat history to format a Llama prompt with special tags that it has
    been trained to recognize as chat markers.
    """

    def format_prompt(self, blocks: List[Block]) -> str:
        """A Llama2 Prompt is properly formatted as:

            <s>[INST] <<SYS>>
            system prompt
            <</SYS>>

            use message [/INST]

        As the conversation progresses, the prompt should evolve as follows:

            <s>[INST] <<SYS>>
            system prompt
            <</SYS>>

            use message [/INST] {{ model_answer_1 }} </s><s>[INST] {{ user_msg_2 }} [/INST]

        - No tools are supported (note their absense in the type signature)"""

        output = ""

        # The system prompt is EMBEDDED inside the user message that follows it, so we keep a running memory
        # of the last system prompt we saw to append to the next use message we see
        last_system_prompt = ""

        for block in blocks:
            if block.chat_role == RoleTag.SYSTEM:
                last_system_prompt = f"<<SYS>>\n{block.text}\n<</SYS>>\n\n"
            elif block.chat_role == RoleTag.USER:
                output += f"<s>[INST] {last_system_prompt}{block.text} [/INST]"
                last_system_prompt = ""
            elif block.chat_role == RoleTag.ASSISTANT:
                output += f"{block.text} </s>"
        return output

    def chat(
        self,
        messages: List[Block],
        tools: Optional[List[Tool]] = None,
        model_name: str = None,  # The default in the plugin is LLAMA_2_70B.
        temperature: float = None,
        model_version: Optional[str] = None,
        default_system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        stop_sequences: Optional[str] = None,  # Should be a CSV string
        **kwargs,
    ) -> List[Block]:
        # Note: The only reason that `tools` is in the function signature is to conform to the interfaces currently established.
        # As per the internal discussion, these interfaces will likely be refactored.
        if tools and len(tools) > 0:
            raise SteamshipError(
                message="The Replicate Llama LLM does not support tools. Please use OpenAI if you need tools, or remove your tools to use Replicate."
            )

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

        if isinstance(messages, str):
            raise SteamshipError(
                message="The LlamaChat class can only generate completions with a list of blocks as input."
            )
        input_text = self.format_prompt(messages)
        return super().complete(prompt=input_text, **options)
