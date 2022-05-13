from abc import ABC
from typing import Any

from steamship.app import Response, post
from steamship.base import Client
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.service import PluginRequest, PluginService


# Note!
# =====
#
# This is the PLUGIN IMPLEMENTOR's View of a Tagger.
#
# If you are using the Steamship Client, you probably want steamship.client.operations.tagger instead
# of this file.
#
class Tagger(PluginService[BlockAndTagPluginInput, BlockAndTagPluginOutput], ABC):
    @classmethod
    def subclass_request_from_dict(
        cls, d: Any, client: Client = None
    ) -> PluginRequest[BlockAndTagPluginInput]:
        return BlockAndTagPluginInput.from_dict(d, client=client)


    @post("getTrainingParameters")
    def _get_training_parameters_endpoint(self, **kwargs) -> dict:
        parse_request = Tagger.parse_request(request=kwargs)
        return self.run(parse_request)