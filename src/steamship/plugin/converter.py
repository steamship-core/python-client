from abc import ABC

from steamship.base import Client
from steamship.plugin.inputs.raw_data_plugin_input import RawDataPluginInput
from steamship.plugin.service import PluginService, PluginRequest


class Converter(PluginService[RawDataPluginInput, BlockAndTagPluginOutput], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[RawDataPluginInput]:
        return RawDataPluginInput.from_dict(d, client=client)
