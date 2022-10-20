from abc import ABC, abstractmethod

from steamship.invocable import InvocableResponse, post
from steamship.invocable.plugin_service import PluginRequest, PluginService
from steamship.plugin.inputs.raw_data_plugin_input import RawDataPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput

# Note!
# =====
#
# This is the PLUGIN IMPLEMENTOR's View of a Blockifier.
#
# If you are using the Steamship Client, you probably want steamship.client.operations.converter instead
# of this file.
#


class Blockifier(PluginService[RawDataPluginInput, BlockAndTagPluginOutput], ABC):
    @abstractmethod
    def run(
        self, request: PluginRequest[RawDataPluginInput]
    ) -> InvocableResponse[BlockAndTagPluginOutput]:
        raise NotImplementedError()

    @post("blockify")
    def run_endpoint(self, **kwargs) -> InvocableResponse[BlockAndTagPluginOutput]:
        """Exposes the Corpus Importer's `run` operation to the Steamship Engine via the expected HTTP path POST /import"""
        return self.run(PluginRequest[RawDataPluginInput].parse_obj(kwargs))
