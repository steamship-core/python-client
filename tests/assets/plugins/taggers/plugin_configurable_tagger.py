from typing import Optional, Type, Union

from steamship import Tag
from steamship.app import Response, create_handler
from steamship.plugin.config import Config
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.service import PluginRequest
from steamship.plugin.tagger import Tagger


class TestParserPlugin(Tagger):
    # For testing; mirrors TestConfigurableTagger in Swift

    class TestParserConfig(Config):
        tagKind: str
        tagName: str
        numberValue: Union[int, float]
        # TODO: Check to see if python and/or swift removes False from obj.
        # If this is non-optional, the typecheck fails despite the fact that the test passes
        # in a value of false....
        booleanValue: Optional[bool] = False

    def config_cls(self) -> Type[Config]:
        return self.TestParserConfig

    def run(
        self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> Response[BlockAndTagPluginOutput]:
        tag_kind = self.config.tagKind
        tag_name = self.config.tagName
        tag_value = {
            "numberValue": self.config.numberValue,
            "booleanValue": self.config.booleanValue,
        }

        if request.data is not None:
            file = request.data.file
            tag = Tag.CreateRequest(kind=tag_kind, name=tag_name, value=tag_value)
            if file.tags:
                file.tags.append(tag)
            else:
                file.tags = [tag]
            return Response(data=BlockAndTagPluginOutput(file=file))


handler = create_handler(TestParserPlugin)
