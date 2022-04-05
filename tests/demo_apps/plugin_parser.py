from steamship import Block, DocTag, Tag
from steamship.app import App, post, create_handler
from steamship.plugin.tagger import Tagger
from steamship.plugin.service import PluginResponse, PluginRequest
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
import re



def tagSentences(block: Block):
    """Splits the document into sentences by assuming a period is a sentence divider."""
    # Add the period back
    tags = []
    for m in re.finditer(r'[^\.]+', block.text):
        tags.append(Tag(kind=DocTag.doc, name=DocTag.sentence, startIdx=m.start(), endIdx=m.end()+1))
    if block.tags:
        block.tags.extend(tags)
    else:
        block.tags = tags



def _makeTestResponse(request: BlockAndTagPluginInput) -> BlockAndTagPluginOutput:
    for block in request.file.blocks:
        tagSentences(block)
    response = BlockAndTagPluginOutput(request.file)
    return response


class TestParserPlugin(Tagger, App):
    # TODO: WARNING! We will need to implement some logic that prevents 
    # a distributed endless loop. E.g., a parser plugin returning the results
    # of using the Steamship client to call parse.. via itself!

    def run(self, request: PluginRequest[BlockAndTagPluginInput]) -> PluginResponse[BlockAndTagPluginOutput]:
        if request.data is not None:
            return PluginResponse(
                data=_makeTestResponse(request.data)
            )

    @post('tag')
    def parse(self, **kwargs) -> dict:
        parseRequest = Tagger.parse_request(request=kwargs)
        parseResponse = self.run(parseRequest)
        return Tagger.response_to_dict(parseResponse)


handler = create_handler(TestParserPlugin)
