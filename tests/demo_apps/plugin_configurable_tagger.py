import json

from steamship import Tag
from steamship.deployable import Deployable, post, create_handler, Response
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.service import PluginRequest
from steamship.plugin.tagger import Tagger


class TestParserPlugin(Tagger, Deployable):
    # For testing; mirrors TestConfigurableTagger in Swift

    def run(self, request: PluginRequest[BlockAndTagPluginInput]) -> Response[BlockAndTagPluginOutput]:
        tagKind = self.config['tagKind']
        tagName = self.config['tagName']
        tagValue = json.dumps({'numberValue': self.config['numberValue'], 'booleanValue': self.config['booleanValue']})

        if request.data is not None:
            file = request.data.file
            tag = Tag.CreateRequest(kind=tagKind, name=tagName, value=tagValue)
            if file.tags:
                file.tags.append(tag)
            else:
                file.tags = [tag]
            return Response(
                data=BlockAndTagPluginOutput(file)
            )

    @post('tag')
    def parse(self, **kwargs) -> dict:
        parseRequest = Tagger.parse_request(request=kwargs)
        return self.run(parseRequest)


handler = create_handler(TestParserPlugin)
