from abc import ABC

from steamship.base import Client
from steamship.data.parser import ParseRequest, ParseResponse
from steamship.plugin.service import PluginService, PluginRequest


class Parser(PluginService[ParseRequest, ParseResponse], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[ParseRequest]:
        return ParseRequest.from_dict(d, client=client)
