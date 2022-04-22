import json

from steamship import Block, DocTag, Tag
from steamship.app import App, post, create_handler, Response
from steamship.plugin.tagger import Tagger
from steamship.plugin.service import PluginResponse, PluginRequest
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship import SteamshipError
import re
import logging

class TestTrainableTaggerPlugin(Tagger, App):
    # For testing; mirrors TestConfigurableTagger in Swift

    def run(self, request: PluginRequest[BlockAndTagPluginInput]) -> PluginResponse[BlockAndTagPluginOutput]:
        raise SteamshipError(message="Inference on this tagger is performed by the Steamship Inference Cloud.")

    @post('getTrainingParameters')
    def getTrainingParameters(self, **kwargs) -> Response:
        return Response(json=dict(
            epochs=3,
            model="pytorch_text_classification",
            trainTestSplit=dict(
                trainPercent=0.7
            )
        ))

handler = create_handler(TestTrainableTaggerPlugin)
