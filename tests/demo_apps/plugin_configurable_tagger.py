import json

from steamship import Block, DocTag, Tag
from steamship.app import App, post, create_handler
from steamship.plugin.tagger import Tagger
from steamship.plugin.service import PluginResponse, PluginRequest
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
import re



class TestParserPlugin(Tagger, App):
    # For testing; mirrors TestConfigurableTagger in Swift

    def run(self, request: PluginRequest[BlockAndTagPluginInput]) -> PluginResponse[BlockAndTagPluginOutput]:
        tagKind = self.config['tagKind']
        tagName = self.config['tagName']
        tagValue = json.dumps({'numberValue':self.config['numberValue'], 'booleanValue':self.config['booleanValue']})

        if request.data is not None:
            file = request.data.file
            tag = Tag.CreateRequest(kind=tagKind, name= tagName, value=tagValue)
            if file.tags:
                file.tags.append(tag)
            else:
                file.tags = [tag]
            return PluginResponse(
                data=BlockAndTagPluginOutput(file)
            )

    @post('tag')
    def parse(self, **kwargs) -> dict:
        parseRequest = Tagger.parse_request(request=kwargs)
        parseResponse = self.run(parseRequest)
        return Tagger.response_to_dict(parseResponse)


handler = create_handler(TestParserPlugin)
