from abc import ABC

from steamship.base import Client
from steamship.data.file import FileCreateRequest, FileImportResponse
from steamship.plugin.service import PluginService, PluginRequest


class FileImporter(PluginService[FileCreateRequest, FileImportResponse], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[FileCreateRequest]:
        return FileCreateRequest.from_dict(d, client=client)
