from steamship import Block, MimeTypes
from steamship.data.block import BlockUploadType
from steamship.invocable import InvocableResponse
from steamship.plugin.generator import Generator
from steamship.plugin.inputs.raw_block_and_tag_plugin_input import RawBlockAndTagPluginInput
from steamship.plugin.outputs.plugin_output import UsageReport
from steamship.plugin.outputs.raw_block_and_tag_plugin_output import RawBlockAndTagPluginOutput
from steamship.plugin.request import PluginRequest

TEST_BYTES_STRING = "Test MP3 bytes"


class TestGeneratorReturnsBytes(Generator):
    def run(
        self, request: PluginRequest[RawBlockAndTagPluginInput]
    ) -> InvocableResponse[RawBlockAndTagPluginOutput]:

        _bytes = TEST_BYTES_STRING.encode("utf-8")
        result = [
            Block(upload_bytes=_bytes, mime_type=MimeTypes.MP3, upload_type=BlockUploadType.FILE)
        ]

        return InvocableResponse(
            data=RawBlockAndTagPluginOutput(blocks=result, usage=[UsageReport.run_tokens(5)])
        )
