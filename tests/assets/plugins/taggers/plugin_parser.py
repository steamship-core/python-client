import logging
import re
from typing import Type

from steamship import Block, DocTag, Tag
from steamship.app import Response, create_handler
from steamship.plugin.config import Config
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.service import PluginRequest
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
                kind=DocTag.doc,
                name=DocTag.sentence,
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
    class EmptyConfig(Config):
        pass

    def config_cls(self) -> Type[Config]:
        return self.EmptyConfig

    def run(
        self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> Response[BlockAndTagPluginOutput]:
        logging.info(f"Inside parser: {type(request)}")
        file = request.data.file
        for block in file.blocks:
            tag_sentences(block)
        if request.data is not None:
            ret = Response(data=BlockAndTagPluginOutput(file=file))
            logging.info(f"Ret: {ret}")
            return ret


handler = create_handler(TestParserPlugin)
