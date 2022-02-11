import io
from abc import ABC
from dataclasses import dataclass
from typing import Any

from steamship.base import Client
from steamship.base.binary_utils import flexi_create
from steamship.plugin.service import PluginService, PluginRequest
from steamship.data.file import FileImportRequest, FileImportResponse


class FileImporter(PluginService[FileImportRequest, FileImportResponse], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[FileImportRequest]:
        return FileImportRequest.from_dict(d, client=client)
