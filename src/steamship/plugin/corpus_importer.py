import io
from abc import ABC
from dataclasses import dataclass
from typing import Any

import steamship.plugin
from steamship.base import Client
from steamship.base.binary_utils import flexi_create
from steamship.plugin.service import PluginService, PluginRequest
from steamship.data.file import FileImportRequest
from steamship.data.corpus import CorpusImportRequest, CorpusImportResponse


class CorpusImporter(PluginService[CorpusImportRequest, CorpusImportResponse], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[CorpusImportRequest]:
        return CorpusImportRequest.from_dict(d, client=client)
