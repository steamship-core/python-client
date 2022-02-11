from abc import ABC

from steamship.base import Client
from steamship.data.converter import ConvertRequest, ConvertResponse
from steamship.plugin.service import PluginService, PluginRequest


class Converter(PluginService[ConvertRequest, ConvertResponse], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[ConvertRequest]:
        return ConvertRequest.from_dict(d, client=client)
