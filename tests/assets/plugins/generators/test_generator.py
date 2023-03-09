from typing import List

from steamship import Block
from steamship.invocable import InvocableResponse
from steamship.plugin.generator import Generator
from steamship.plugin.inputs.raw_block_and_tag_plugin_input import RawBlockAndTagPluginInput
from steamship.plugin.outputs.raw_block_and_tag_plugin_output import RawBlockAndTagPluginOutput
from steamship.plugin.request import PluginRequest


class TestGenerator(Generator):
    def run(
        self, request: PluginRequest[RawBlockAndTagPluginInput]
    ) -> InvocableResponse[RawBlockAndTagPluginOutput]:
        result: List[Block] = []

        for block in request.data.blocks:
            result.append(Block(text=block.text[::-1]))

        return InvocableResponse(data=RawBlockAndTagPluginOutput(blocks=result))
