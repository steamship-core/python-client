from abc import ABC, abstractmethod
from typing import List

from steamship.data.block import Block, StreamState
from steamship.invocable import InvocableResponse, post
from steamship.invocable.plugin_service import PluginRequest, PluginService
from steamship.plugin.inputs.raw_block_and_tag_plugin_input import RawBlockAndTagPluginInput
from steamship.plugin.inputs.raw_block_and_tag_plugin_input_with_preallocated_blocks import (
    RawBlockAndTagPluginInputWithPreallocatedBlocks,
)
from steamship.plugin.outputs.block_type_plugin_output import BlockTypePluginOutput
from steamship.plugin.outputs.stream_complete_plugin_output import StreamCompletePluginOutput

# Note!
# =====
#
# This is the PLUGIN IMPLEMENTOR's View of a Streaming Generator.
#
# If you are using the Steamship Client, you probably want steamship.client.operations.generator instead
# of this file.
#


class StreamingGenerator(
    PluginService[RawBlockAndTagPluginInputWithPreallocatedBlocks, StreamCompletePluginOutput], ABC
):
    @abstractmethod
    def run(
        self, request: PluginRequest[RawBlockAndTagPluginInputWithPreallocatedBlocks]
    ) -> InvocableResponse[StreamCompletePluginOutput]:
        raise NotImplementedError()

    @post("streamResultToBlocks")
    def run_endpoint(self, **kwargs) -> InvocableResponse[StreamCompletePluginOutput]:
        input = PluginRequest[RawBlockAndTagPluginInputWithPreallocatedBlocks].parse_obj(kwargs)
        for block in input.data.blocks:
            block.client = self.client
        for block in input.data.output_blocks:
            block.client = self.client
        return self.run(input)

    @post("determineOutputBlockTypes")
    def determine_output_block_types_endpoint(
        self, **kwargs
    ) -> InvocableResponse[BlockTypePluginOutput]:
        input = PluginRequest[RawBlockAndTagPluginInput].parse_obj(kwargs)
        for block in input.data.blocks:
            block.client = self.client
        try:
            return self.determine_output_block_types(input)
        except BaseException as e:
            # If anything goes wrong, make sure
            # we automatically abort any open streams
            # so the client can know
            self.abort_open_block_streams(input.data.blocks)
            raise e

    @abstractmethod
    def determine_output_block_types(
        self, request: PluginRequest[RawBlockAndTagPluginInput]
    ) -> InvocableResponse[BlockTypePluginOutput]:
        raise NotImplementedError()

    def abort_open_block_streams(self, blocks: List[Block]):
        for block in blocks:
            refreshed_block = Block.get(block.client, block.id)
            if refreshed_block.stream_state == StreamState.STARTED:
                refreshed_block.abort_stream()
