import logging
import re

from steamship import Block, DocTag, Tag
from steamship.data import TagKind
from steamship.invocable import InvocableResponse
from steamship.invocable.plugin_service import PluginRequest
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.tagger import Tagger

# If this isn't present, Localstack won't show logs
logging.getLogger().setLevel(logging.INFO)


def tag_sentences(block: Block):
    """Splits the document into sentences by assuming a period is a sentence divider."""
    # Add the period back
    tags = []
    for m in re.finditer(r"[^.]+", block.text):
        tags.append(
            Tag(
                kind=TagKind.DOCUMENT,
                name=DocTag.SENTENCE,
                start_idx=m.start(),
                end_idx=m.end() + 1,
            )
        )
    if block.tags:
        block.tags.extend(tags)
    else:
        block.tags = tags


class TestParserPlugin(Tagger):
    # TODO: WARNING! We will need to implement some logic that prevents
    # a distributed endless loop. E.g., a parser plugin returning the results
    # of using the Steamship client to call parse.. via itself!

    def run(
        self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> InvocableResponse[BlockAndTagPluginOutput]:
        logging.info(f"Inside parser: {type(request)}")
        file = request.data.file
        for block in file.blocks:
            tag_sentences(block)
        if request.data is not None:
            ret = InvocableResponse(data=BlockAndTagPluginOutput(file=file))
            logging.info(f"Ret: {ret}")
            return ret
