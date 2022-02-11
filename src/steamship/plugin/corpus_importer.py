from abc import ABC

from steamship.base import Client
from steamship.data.corpus import CorpusImportRequest, CorpusImportResponse
from steamship.plugin.service import PluginService, PluginRequest


class CorpusImporter(PluginService[CorpusImportRequest, CorpusImportResponse], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[CorpusImportRequest]:
        return CorpusImportRequest.from_dict(d, client=client)
