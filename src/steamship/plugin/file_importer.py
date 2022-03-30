from abc import ABC

from steamship.base import Client
from steamship.data.file import File
from steamship.plugin.service import PluginService, PluginRequest


class FileImporter(PluginService[File.CreateRequest, File.CreateResponse], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[File.CreateRequest]:
        return File.CreateRequest.from_dict(d, client=client)
