from abc import ABC

from steamship.base import Client
from steamship.plugin.inputs.raw_data_plugin_input import RawDataPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.service import PluginService, PluginRequest

# Note!
# =====
#
# This is the PLUGIN IMPLEMENTOR's View of a Converter.
#
# If you are using the Steamship Client, you probably want steamship.client.operations.converter instead
# of this file.
#
class Converter(PluginService[RawDataPluginInput, BlockAndTagPluginOutput], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[RawDataPluginInput]:
        return RawDataPluginInput.from_dict(d, client=client)

