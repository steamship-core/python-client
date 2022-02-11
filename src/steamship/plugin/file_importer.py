from abc import ABC

from steamship.base import Client
from steamship.data.file import FileImportRequest, FileImportResponse
from steamship.plugin.service import PluginService, PluginRequest


class FileImporter(PluginService[FileImportRequest, FileImportResponse], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[FileImportRequest]:
        return FileImportRequest.from_dict(d, client=client)
