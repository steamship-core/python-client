from steamship import Block, MimeTypes
from steamship.invocable import InvocableResponse
from steamship.plugin.generator import Generator
from steamship.plugin.inputs.raw_block_and_tag_plugin_input import RawBlockAndTagPluginInput
from steamship.plugin.outputs.plugin_output import UsageReport
from steamship.plugin.outputs.raw_block_and_tag_plugin_output import RawBlockAndTagPluginOutput
from steamship.plugin.request import PluginRequest


class TestGenerator(Generator):
    def run(
        self, request: PluginRequest[RawBlockAndTagPluginInput]
    ) -> InvocableResponse[RawBlockAndTagPluginOutput]:
        image_blocks = 0
        fetched_raw = 0
        for block in request.data.blocks:
            if block.mime_type == MimeTypes.PNG:
                image_blocks += 1
                _ = block.raw()
                fetched_raw += 1

        output_text = f"Found {image_blocks} image blocks and fetched data from {fetched_raw}"
        return InvocableResponse(
            data=RawBlockAndTagPluginOutput(
                blocks=[Block(text=output_text)], usage=[UsageReport.run_units(1)]
            )
        )
