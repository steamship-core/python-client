import time

from steamship import MimeTypes
from steamship.invocable import InvocableResponse
from steamship.plugin.inputs.raw_block_and_tag_plugin_input import RawBlockAndTagPluginInput
from steamship.plugin.inputs.raw_block_and_tag_plugin_input_with_preallocated_blocks import (
    RawBlockAndTagPluginInputWithPreallocatedBlocks,
)
from steamship.plugin.outputs.block_type_plugin_output import BlockTypePluginOutput
from steamship.plugin.outputs.stream_complete_plugin_output import StreamCompletePluginOutput
from steamship.plugin.request import PluginRequest
from steamship.plugin.streaming_generator import StreamingGenerator


class TestStreamingGenerator(StreamingGenerator):
    def run(
        self, request: PluginRequest[RawBlockAndTagPluginInputWithPreallocatedBlocks]
    ) -> InvocableResponse[StreamCompletePluginOutput]:

        chunk_delay = int((request.data.options or {}).get("chunk_delay", "100"))
        for i, block in enumerate(request.data.blocks):
            output_block = request.data.output_blocks[i]
            output_text = block.text[::-1]
            for chunk in TestStreamingGenerator.split_string_into_chunks(output_text, 2):
                output_block.append_stream(bytes=bytes(chunk, "utf-8"))
                time.sleep(chunk_delay / 1000)
            output_block.finish_stream()

        return InvocableResponse(data=StreamCompletePluginOutput())

    def determine_output_block_types(
        self, request: PluginRequest[RawBlockAndTagPluginInput]
    ) -> InvocableResponse[BlockTypePluginOutput]:
        # Output block types are one text block per input block
        result = [MimeTypes.TXT.value] * len(request.data.blocks)
        return InvocableResponse(data=BlockTypePluginOutput(block_types_to_create=result))

    @staticmethod
    def split_string_into_chunks(s: str, chunk_size: int):
        length = len(s)
        result = []
        for pos in range(0, length, chunk_size):
            result.append(s[pos : pos + chunk_size])
        return result
