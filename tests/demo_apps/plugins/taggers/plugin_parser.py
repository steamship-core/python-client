import re

from steamship import Block, DocTag, Tag
from steamship.app import Response, create_handler
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.service import PluginRequest
from steamship.plugin.tagger import Tagger


def tag_sentences(block: Block):
    """Splits the document into sentences by assuming a period is a sentence divider."""
    # Add the period back
    tags = []
    for m in re.finditer(r"[^.]+", block.text):
        tags.append(
            Tag(
                kind=DocTag.doc,
                name=DocTag.sentence,
                startIdx=m.start(),
                endIdx=m.end() + 1,
            )
        )
    if block.tags:
        block.tags.extend(tags)
    else:
        block.tags = tags


def _make_test_response(request: BlockAndTagPluginInput) -> BlockAndTagPluginOutput:
    for block in request.file.blocks:
        tag_sentences(block)
    response = BlockAndTagPluginOutput(request.file)
    return response


class TestParserPlugin(Tagger):
    # TODO: WARNING! We will need to implement some logic that prevents
    # a distributed endless loop. E.g., a parser plugin returning the results
    # of using the Steamship client to call parse.. via itself!

    def run(
        self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> Response[BlockAndTagPluginOutput]:
        if request.data is not None:
            return Response(data=_make_test_response(request.data))


handler = create_handler(TestParserPlugin)
