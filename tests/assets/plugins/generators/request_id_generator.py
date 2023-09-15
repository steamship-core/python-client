from steamship import Block
from steamship.invocable import InvocableResponse
from steamship.plugin.generator import Generator
from steamship.plugin.inputs.raw_block_and_tag_plugin_input import RawBlockAndTagPluginInput
from steamship.plugin.outputs.plugin_output import UsageReport
from steamship.plugin.outputs.raw_block_and_tag_plugin_output import RawBlockAndTagPluginOutput
from steamship.plugin.request import PluginRequest


class RequestIDGenerator(Generator):
    # Just generate a block with the request ID as the text.
    def run(
        self, request: PluginRequest[RawBlockAndTagPluginInput]
    ) -> InvocableResponse[RawBlockAndTagPluginOutput]:
        return InvocableResponse(
            data=RawBlockAndTagPluginOutput(
                blocks=[Block(text=self.client.config.request_id)],
                usage=[UsageReport.run_tokens(5)],
            )
        )
