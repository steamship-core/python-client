import logging

from steamship.invocable import InvocableResponse, create_handler
from steamship.invocable.plugin_service import PluginRequest
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.tagger import Tagger


class TestLoggingTaggerPlugin(Tagger):
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
