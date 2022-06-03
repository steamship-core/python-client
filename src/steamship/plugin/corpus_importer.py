from abc import ABC, abstractmethod

from steamship.app import Response, post
from steamship.data.operations.corpus_importer import CorpusImportRequest, CorpusImportResponse
from steamship.plugin.service import PluginRequest, PluginService


# Note!
# =====
#
# This is the PLUGIN IMPLEMENTOR's View of a Corpus Importer.
#
# If you are using the Steamship Client, you probably want steamship.client.operations.corpus_importer instead
# of this file.
#
class CorpusImporter(PluginService[CorpusImportRequest, CorpusImportResponse], ABC):
    @abstractmethod
    def run(self, request: PluginRequest[CorpusImportRequest]) -> Response[CorpusImportResponse]:
        raise NotImplementedError()

    @post("import")
    def run_endpoint(self, **kwargs) -> Response[CorpusImportResponse]:
        """Exposes the Corpus Importer's `run` operation to the Steamship Engine via the expected HTTP path POST /import"""
        return self.run(PluginRequest[CorpusImportRequest].parse_obj(kwargs))
