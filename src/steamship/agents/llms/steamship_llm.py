import logging
from pprint import pformat
from typing import List, Optional

from steamship import Block, File, MimeTypes, PluginInstance, Steamship, SteamshipError, Tag
from steamship.data import GenerationTag, TagKind
from steamship.plugin.capabilities import (
    Capability,
    CapabilityPluginRequest,
    CapabilityPluginResponse,
)


class SteamshipLLM:
    """A class wrapping LLM plugins."""

    def __init__(self, plugin_instance: PluginInstance):
        self.client = plugin_instance.client
        self.plugin_instance = plugin_instance

    class Impls:
        @staticmethod
        def gpt(
            client: Steamship,
            plugin_version: Optional[str] = None,
            model: str = "gpt-4",
            temperature: float = 0.4,
            max_tokens: int = 256,
            **kwargs,
        ):
            gpt = client.use_plugin(
                "gpt-4",
                version=plugin_version,
                config={
                    "model": model,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    **kwargs,
                },
            )
            return SteamshipLLM(gpt)

    def generate(
        self,
        messages: List[Block],
        capabilities: List[Capability] = None,
        assert_capabilities: bool = True,
        **kwargs,
    ) -> List[Block]:
        """
        Call the LLM plugin's generate method.  Generate requests for plugin capabilities based on input parameters.

        :param messages: Messages to be passed to the LLM to construct the prompt.
        :param capabilities: Capabilities that will be asked of the LLM.  See the docstring for
          steamship.plugins.capabilities.

          If default_capabilities was provided at construction, those capabilities will be requested unless overridden
          by this parameter.
        :param assert_capabilities: If True (default), raise a SteamshipError if the LLM plugin did not respond with a
          block that asserts what level capabilities were fulfilled at.
        :param kwargs: Options that can be passed to the LLM model as other parameters.
        :return: a List of Blocks that are returned from the plugin.
        """
        file_ids = {b.file_id for b in messages}
        block_ids = None
        temp_file = None
        if len(file_ids) != 1 and next(iter(file_ids)) is not None:
            file_id = next(iter(file_ids))
            block_ids = [b.id for b in messages]
        else:
            temp_file = File.create(
                client=self.client,
                blocks=messages,
                tags=[Tag(kind=TagKind.GENERATION, name=GenerationTag.PROMPT_COMPLETION)],
            )
            file_id = temp_file.id

        request_block = CapabilityPluginRequest(requested_capabilities=capabilities).create_block(
            client=self.client, file_id=file_id
        )
        if block_ids:
            block_ids.append(request_block.id)

        try:
            generation_task = self.plugin_instance.generate(
                input_file_id=file_id, input_file_block_index_list=block_ids, options=kwargs
            )
            generation_task.wait()

            for block in generation_task.output.blocks:
                if block.mime_type == MimeTypes.STEAMSHIP_PLUGIN_CAPABILITIES_RESPONSE:
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
            if temp_file:
                temp_file.delete()

        return generation_task.output.blocks
