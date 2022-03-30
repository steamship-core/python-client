from abc import ABC
from dataclasses import dataclass

from steamship.base import Client
from steamship.plugin.inputs.raw_data_plugin_input import RawDataPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.service import PluginService, PluginRequest


class Converter(PluginService[RawDataPluginInput, BlockAndTagPluginOutput], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[RawDataPluginInput]:
        return RawDataPluginInput.from_dict(d, client=client)


@dataclass
class ConvertRequest:
    type: str = None
    pluginInstance: str = None
    id: str = None
    handle: str = None
    name: str = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "ClientsideConvertRequest":
        return ClientsideConvertRequest(
            type=d.get('type', None),
            pluginInstance=d.get('pluginInstance', None),
            id=d.get('id', None),
            handle=d.get('handle', None),
            name=d.get('name', None)
        )
