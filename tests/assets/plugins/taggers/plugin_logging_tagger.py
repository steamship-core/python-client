import logging
from typing import Type

from steamship.app import InvocableResponse, create_handler
from steamship.app.config import Config
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.service import PluginRequest
from steamship.plugin.tagger import Tagger


class TestLoggingTaggerPlugin(Tagger):
    class EmptyConfig(Config):
        pass

    def config_cls(self) -> Type[Config]:
        return self.EmptyConfig

    def run(
        self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> InvocableResponse[BlockAndTagPluginOutput]:
        logging.info("A remote logging log")
        file = request.data.file
        if request.data is not None:
            ret = InvocableResponse(data=BlockAndTagPluginOutput(file=file))
            logging.info(f"Ret: {ret}")
            return ret


handler = create_handler(TestLoggingTaggerPlugin)
