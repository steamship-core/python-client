from steamship import Block, File, Tag
from steamship.data import GenerationTag, TagKind, TagValueKey
from steamship.invocable import InvocableResponse, create_handler
from steamship.invocable.plugin_service import PluginRequest
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.tagger import Tagger


class TestPromptGeneratorPlugin(Tagger):
    def run(
        self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> InvocableResponse[BlockAndTagPluginOutput]:
        """Merely returns the prompt."""
        request_file = request.data.file
        output = BlockAndTagPluginOutput(file=File(id=request_file.id), tags=[])
        for block in request.data.file.blocks:
            text = block.text
            tags = [
                Tag(
                    kind=TagKind.GENERATION,
                    name=GenerationTag.PROMPT_COMPLETION,
                    value={TagValueKey.STRING_VALUE: text},
                )
            ]
            output_block = Block(id=block.id, tags=tags)
            output.file.blocks.append(output_block)

        return InvocableResponse(data=output)


handler = create_handler(TestPromptGeneratorPlugin)
