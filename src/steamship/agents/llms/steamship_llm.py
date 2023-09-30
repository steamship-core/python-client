import logging
from pprint import pformat
from typing import List, Optional

from steamship import Block, File, MimeTypes, PluginInstance, Steamship, SteamshipError, Tag
from steamship.agents.schema import Tool
from steamship.data import GenerationTag, TagKind
from steamship.plugin.capabilities import (
    CapabilityPluginRequest,
    CapabilityPluginResponse,
    ConversationSupport,
    FunctionCallingSupport,
    SystemPromptSupport,
)


class SteamshipLLM:
    """A class wrapping LLM plugins."""

    def __init__(self, plugin_instance: PluginInstance):
        # TODO (PR callout): In the spirit of getting folks to pin to specific instances more often, take the route of
        #  using specific PluginInstances rather than client.use_plugin all the time with the params that we determine?
        self.client = plugin_instance.client
        self.plugin_instance = plugin_instance

    @staticmethod
    def with_gpt4(client: Steamship, temperature: float = 0.4, max_tokens: int = 256):
        # TODO (PR callout): This is an example of helpers that can initialize plugins that we know are solid / are
        #  steamship-published.  These don't need to live in this class either, to keep the interface more pure.
        gpt4 = client.use_plugin(
            "gpt-4", config={"model": "gpt-4", "temperature": temperature, "max_tokens": max_tokens}
        )
        return SteamshipLLM(gpt4)

    def generate(
        self,
        messages: List[Block],
        system_prompt: List[Block] = None,
        history: Optional[List[Block]] = None,
        tools: Optional[List[Tool]] = None,
        assert_capabilities: bool = True,
        **kwargs,
    ) -> List[Block]:
        """
        Call the LLM plugin's generate method.  Generate requests for plugin capabilities based on input parameters.

        :param messages: Messages to be passed to the LLM to construct the prompt.
        :param system_prompt: A system prompt to include with the prompt. Providing this requests the
          SystemPromptSupport capability.
        :param history: A list of blocks which are previous interactions with the tool. Providing this requests the
          ConversationSupport capability.
        :param tools: A list of Tools, representing functions which can be called with this LLM. Providing this requests
          the FunctionCallingSupport capability, and provides the function definitions for it.
        :param assert_capabilities: If True (default), raise a SteamshipError if the LLM plugin did not respond with a
          block that asserts what level capabilities were fulfilled at.
        :param kwargs: Options that can be passed to the LLM model as other parameters.
        :return: a List of Blocks that are returned from the plugin.
        """

        # TODO (PR callout): I'm not certain this class needs to be abstract?  This seems pretty soup-to-nuts.
        capabilities = []
        blocks = messages[:]
        if system_prompt:
            blocks += system_prompt
            capabilities.append(SystemPromptSupport())

        if history:
            blocks += history
            capabilities.append(ConversationSupport())

        if tools:
            capabilities.append(
                FunctionCallingSupport(functions=[tool.as_openai_function() for tool in tools])
            )

        blocks.append(CapabilityPluginRequest(requested_capabilities=capabilities).to_block())
        # TODO (PR callout): I have maybe ideas for not needing temp files here in all cases? GH comment
        temp_file = File.create(
            client=self.client,
            blocks=blocks,
            tags=[Tag(kind=TagKind.GENERATION, name=GenerationTag.PROMPT_COMPLETION)],
        )

        try:
            generation_task = self.plugin_instance.generate(
                input_file_id=temp_file.id, options=kwargs
            )
            generation_task.wait()

            for block in generation_task.output.blocks:
                if block.mime_type == MimeTypes.STEAMSHIP_PLUGIN_CAPABILITIES:
                    if logging.DEBUG >= logging.root.getEffectiveLevel():
                        response = CapabilityPluginResponse.from_block(block)
                        logging.debug(
                            f"Plugin capability fulfillment:\n\n{pformat(response.json())}"
                        )
                    break
            else:
                if assert_capabilities:
                    version_string = f"{self.plugin_instance.plugin_handle}, v.{self.plugin_instance.plugin_version_handle}"
                    raise SteamshipError(
                        f"Asserting capabilities are used, but capability response was not returned by plugin ({version_string})"
                    )
        finally:
            # TODO (PR callout): It looks like current OpenAI impl might not do this?
            temp_file.delete()

        # TODO (PR callout): Use special output parser in the meantime to extract the tool to call from output block
        #  tagged with new tags, _easy_ slot in with existing FunctionsBasedLLMAgent.
        return generation_task.output.blocks
